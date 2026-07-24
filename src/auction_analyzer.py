"""
Yahoo Auction 商品分析工作流 Lambda (极简重构版)
主要变更：
1. active/closed 各搜索一次，不再按型号分别搜索
2. AI 仅返回极简型号信息（brand/model/variant/storage/listingType/condition/missing/confidence）
3. 所有辅助字段由程序生成（hasAllCriticalParameters/isAnalysisEligible/isComparable/exclusionReason）
4. 价格统计、风险等级、购买建议完全由程序生成
5. 仅在本次搜索到的 closed 中匹配
6. 删除 evidence/criticalParameters 等冗余字段
"""

import os
import re
import json
import time
import random
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Any, Set, Tuple

import boto3

from yahoo_auction_scraper import scrape_auctions

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ==================== 环境变量辅助函数 ====================

def _env_int(key: str, default: int) -> int:
    """读取环境变量并转为 int，空值或不存在时用默认值"""
    value = os.getenv(key, "")
    if not value:
        return default
    return int(value)


def _env_float(key: str, default: float) -> float:
    """读取环境变量并转为 float，空值或不存在时用默认值"""
    value = os.getenv(key, "")
    if not value:
        return default
    return float(value)


def _env_decimal(key: str, default: str) -> Decimal:
    """读取环境变量并转为 Decimal，空值或不存在时用默认值"""
    value = os.getenv(key, "")
    if not value:
        return Decimal(default)
    return Decimal(value)


def _env_bool(key: str, default: bool) -> bool:
    """读取环境变量并转为 bool，空值或不存在时用默认值"""
    value = os.getenv(key, "")
    if not value:
        return default
    return value.lower() == "true"


# ============ 环境变量 ============
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
AI_API_URL = os.getenv("AI_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "doubao-seed-2-0-mini-260428")
AI_API_KEY = os.getenv("AI_API_KEY", "")
SECRET_NAME = os.getenv("SECRET_NAME", "yahoo-auction-ai-api-key")

# active 和 closed 默认各抓取 100 条，并且每种类型只搜索一次
DEFAULT_ACTIVE_COUNT = _env_int("DEFAULT_ACTIVE_COUNT", 100)
DEFAULT_CLOSED_COUNT = _env_int("DEFAULT_CLOSED_COUNT", 100)
MAX_ACTIVE_ITEMS = _env_int("MAX_ACTIVE_ITEMS", 100)
MAX_CLOSED_ITEMS = _env_int("MAX_CLOSED_ITEMS", 100)

# AI 仅用于型号和关键参数解析
MODEL_PARSE_BATCH_SIZE = _env_int("MODEL_PARSE_BATCH_SIZE", 15)
CLOSED_PARSE_BATCH_SIZE = _env_int("CLOSED_PARSE_BATCH_SIZE", 15)
AI_MAX_OUTPUT_TOKENS = _env_int("AI_MAX_OUTPUT_TOKENS", 6000)

# 程序生成购买建议时的阈值
BUY_MARGIN_THRESHOLD = _env_decimal("BUY_MARGIN_THRESHOLD", "0.20")
REVIEW_MARGIN_THRESHOLD = _env_decimal("REVIEW_MARGIN_THRESHOLD", "0.10")
HIGH_CONFIDENCE_COMPARABLE_COUNT = _env_int("HIGH_CONFIDENCE_COMPARABLE_COUNT", 10)
MEDIUM_CONFIDENCE_COMPARABLE_COUNT = _env_int("MEDIUM_CONFIDENCE_COMPARABLE_COUNT", 5)

AI_REQUEST_TIMEOUT = _env_int("AI_REQUEST_TIMEOUT", 90)
AI_MAX_RETRIES = _env_int("AI_MAX_RETRIES", 3)
REQUEST_INTERVAL = _env_float("REQUEST_INTERVAL", 1.0)
INCLUDE_PAYPAY = _env_bool("INCLUDE_PAYPAY", False)

MAX_TOTAL_TOKENS = _env_int("MAX_TOTAL_TOKENS", 50000)
LAMBDA_TIMEOUT_SECONDS = _env_int("LAMBDA_TIMEOUT_SECONDS", 840)
LAMBDA_TIMEOUT_BUFFER = _env_int("LAMBDA_TIMEOUT_BUFFER", 30)

# 定价参数
EXPECTED_SELLING_FEE_RATE = _env_decimal("EXPECTED_SELLING_FEE_RATE", "0.10")
DEFAULT_SHIPPING_COST = _env_decimal("DEFAULT_SHIPPING_COST", "1500")
DEFAULT_REPAIR_RESERVE_RATE = _env_decimal("DEFAULT_REPAIR_RESERVE_RATE", "0.05")
MIN_COMPARABLE_COUNT = _env_int("MIN_COMPARABLE_COUNT", 3)
MAX_PRICE_DEVIATION = _env_decimal("MAX_PRICE_DEVIATION", "1.5")
RISK_RESERVE_RATE = _env_decimal("RISK_RESERVE_RATE", "0.03")

RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

dynamodb = boto3.resource("dynamodb")
active_table = dynamodb.Table(TABLE_NAME_ACTIVE)
closed_table = dynamodb.Table(TABLE_NAME_CLOSED)
secretsmanager = boto3.client("secretsmanager")

_api_key_cache = None
_total_tokens_used = 0
_lambda_start_time = None


# ==================== 密钥管理 ====================

def get_api_key():
    """APIキーの取得"""
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache
    if AI_API_KEY:
        _api_key_cache = AI_API_KEY
        return _api_key_cache
    try:
        response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response.get("SecretString")
        if not secret_string:
            raise RuntimeError("SecretにSecretStringがありません")
        try:
            secret_dict = json.loads(secret_string)
            api_key = (
                secret_dict.get("apiKey") or 
                secret_dict.get("api_key") or 
                secret_dict.get("key") or
                secret_dict.get("API_KEY")
            )
            if not api_key:
                raise RuntimeError("Secret JSONにapiKey/api_key/key/API_KEYが見つかりません")
            _api_key_cache = api_key
        except json.JSONDecodeError:
            _api_key_cache = secret_string
        return _api_key_cache
    except Exception as e:
        logger.error(f"Secrets Managerからのキー取得失敗: {e}")
        raise RuntimeError(f"APIキー取得不可: {e}")


# ==================== Token 和超时控制 ====================

def get_elapsed_seconds():
    """Lambda実行経過秒数を取得"""
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    """Lambdaの残り利用可能秒数を取得"""
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    """Lambdaがタイムアウトに近いかチェック"""
    remaining = get_remaining_seconds()
    if remaining <= 0:
        raise RuntimeError(
            f"Lambdaタイムアウトカウントダウン: 実行時間{get_elapsed_seconds():.1f}秒, "
            f"タイムアウト制限{LAMBDA_TIMEOUT_SECONDS}秒, バッファ{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_token_limit():
    """Token使用量が制限を超えたかチェック"""
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token使用量が上限に達しました: {_total_tokens_used}/{MAX_TOTAL_TOKENS}、実行中断"
        )


def check_limits():
    """Tokenとタイムアウトを同時にチェック"""
    check_token_limit()
    check_timeout()


def update_token_usage(usage):
    """Token使用統計を更新"""
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        logger.info(
            f"Token使用量更新: +{total}, 合計={_total_tokens_used}/{MAX_TOTAL_TOKENS}, "
            f"残り={MAX_TOTAL_TOKENS - _total_tokens_used}"
        )


# ==================== 工具函数 ====================

def to_dynamodb_value(value: Any) -> Any:
    """
    Python値をDynamoDBが受け入れ可能な構造に変換。
    重要なルール：文字列は常に文字列のまま、商品IDが誤って数値に変換されない
    """
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, Decimal):
        return value
    if isinstance(value, dict):
        return {str(key): to_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_dynamodb_value(item) for item in value]
    if isinstance(value, tuple):
        return [to_dynamodb_value(item) for item in value]
    if isinstance(value, set):
        return {str(item) for item in value if str(item)}
    if isinstance(value, str):
        return value
    return value


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """安全にDecimalに変換、失敗時はデフォルト値を返す"""
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """安全に整数に変換、失敗時はデフォルト値を返す"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def normalize(value: str) -> str:
    """全角を半角に変換し、余分な空白を削除"""
    if not value:
        return ""
    value = str(value).strip()
    value = value.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
    ))
    return re.sub(r"\s+", " ", value)


def normalize_storage(value: Any) -> str:
    """
    ストレージ容量を正規化。
    例：256G -> 256GB, 1 tb -> 1TB
    """
    if value is None:
        return ""
    text = normalize(str(value)).upper()
    text = re.sub(r"\s+", "", text)
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(GB|G|TB|T)", text)
    if not match:
        return text
    amount = match.group(1)
    unit = match.group(2)
    if unit == "G":
        unit = "GB"
    elif unit == "T":
        unit = "TB"
    return f"{amount}{unit}"


def parse_bool(value: Any) -> bool:
    """安全にブール値に変換"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def determine_shipping_status(shipping_text: str) -> Dict:
    """送料状態を判定"""
    if not shipping_text or not shipping_text.strip():
        return {
            "isFreeShipping": False,
            "shippingStatus": "UNKNOWN",
            "shippingText": ""
        }
    text = shipping_text.strip().lower()
    free_shipping_keywords = [
        "送料無料", "送料込み", "送料込", "送料無", "送料0", "送料ゼロ",
        "free shipping", "shipping free", "shipping included",
        "free", "0円", "0円送料", "出品者負担"
    ]
    for keyword in free_shipping_keywords:
        if keyword.lower() in text.lower():
            return {
                "isFreeShipping": True,
                "shippingStatus": "FREE",
                "shippingText": shipping_text.strip()
            }
    return {
        "isFreeShipping": False,
        "shippingStatus": "CHARGED",
        "shippingText": shipping_text.strip()
    }


def generate_pricing_model_key(
    brand: str,
    model_name: str,
    storage: str = "",
    variant: str = ""
) -> str:
    """
    価格マッチングキーを生成。
    例：APPLE IPHONE 15 PRO 256GB
    """
    normalized_brand = normalize(brand).upper()
    normalized_model = normalize(model_name).upper()
    normalized_variant = normalize(variant).upper()
    normalized_storage = normalize_storage(storage).upper()
    
    parts = []
    if normalized_brand:
        parts.append(normalized_brand)
    if normalized_model:
        parts.append(normalized_model)
    if normalized_variant and not model_contains_variant(normalized_model, normalized_variant):
        parts.append(normalized_variant)
    if normalized_storage:
        parts.append(normalized_storage)
    
    combined = " ".join(parts)
    combined = re.sub(r"[^A-Z0-9\s+\-/]", " ", combined)
    combined = re.sub(r"\s+", " ", combined).strip()
    return combined


def model_contains_variant(model_name: str, variant: str) -> bool:
    """model名にvariantが既に含まれているかチェック"""
    if not model_name or not variant:
        return False
    model_tokens = model_name.upper().split()
    variant_tokens = variant.upper().split()
    if len(variant_tokens) > len(model_tokens):
        return False
    for start in range(0, len(model_tokens) - len(variant_tokens) + 1):
        if model_tokens[start:start + len(variant_tokens)] == variant_tokens:
            return True
    return False


def response(status_code: int, body: Dict) -> Dict:
    """Lambdaレスポンスを構築"""
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    """Lambda エントリーポイント"""
    global _total_tokens_used, _lambda_start_time
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    
    try:
        keyword = normalize(event.get("keyword", ""))
        if not keyword:
            return response(400, {"error": "keywordは必須です"})
        
        try:
            active_count = int(event.get("active_count", event.get("count", DEFAULT_ACTIVE_COUNT)))
            closed_count = int(event.get("closed_count", DEFAULT_CLOSED_COUNT))
        except (ValueError, TypeError):
            return response(400, {"error": "active_count、closed_countは有効な整数である必要があります"})
        
        force_reprocess = parse_bool(event.get("force_reprocess", False))
        
        active_count = max(1, min(active_count, MAX_ACTIVE_ITEMS))
        closed_count = max(1, min(closed_count, MAX_CLOSED_ITEMS))
        
        logger.info(
            f"商品分析ワークフロー開始: keyword='{keyword}', "
            f"active_count={active_count}, closed_count={closed_count}, "
            f"force_reprocess={force_reprocess}"
        )
        
        result = execute_workflow(
            keyword=keyword,
            active_count=active_count,
            closed_count=closed_count,
            force_reprocess=force_reprocess
        )
        
        result["execution_stats"] = {
            "total_tokens_used": _total_tokens_used,
            "token_limit": MAX_TOTAL_TOKENS,
            "elapsed_seconds": get_elapsed_seconds(),
            "remaining_seconds": get_remaining_seconds()
        }
        
        return response(200, result)
        
    except Exception as e:
        logger.error(f"ワークフロー実行失敗: {e}", exc_info=True)
        return response(500, {
            "error": "内部エラー",
            "details": str(e),
            "total_tokens_used": _total_tokens_used,
            "elapsed_seconds": get_elapsed_seconds()
        })


def execute_workflow(
    keyword: str,
    active_count: int,
    closed_count: int,
    force_reprocess: bool
) -> Dict:
    """
    新ワークフロー：
    1. active を元のキーワードで1回検索、最大 active_count 件
    2. active をバッチでAIに送信してモデル解析
    3. closed を元のキーワードで1回検索、最大 closed_count 件
    4. closed をバッチでAIに送信してモデル解析
    5. 各 active を pricingModelKey で closed とマッチング
    6. 価格統計と購入提案は全てプログラムで生成
    """
    start_time = time.time()
    stage_times = {}
    
    workflow_result = {
        "keyword": keyword,
        "active_search_count": 0,
        "closed_search_count": 0,
        "active_parsed": 0,
        "active_excluded": 0,
        "active_review_required": 0,
        "active_parse_failed": 0,
        "closed_parsed": 0,
        "closed_excluded": 0,
        "closed_review_required": 0,
        "closed_parse_failed": 0,
        "pricing_attempted": 0,
        "pricing_completed": 0,
        "pricing_insufficient_data": 0,
        "pricing_failed": 0,
        "errors": []
    }
    
    try:
        check_limits()
        
        # ==================================================
        # 第一步：active を1回検索
        # ==================================================
        stage_start = time.time()
        logger.info(f"ステップ1：active検索 1回実行、keyword='{keyword}', count={active_count}")
        
        active_item_ids = scrape_and_save_active(
            keyword=keyword,
            count=active_count,
            force_reprocess=force_reprocess
        )
        
        workflow_result["active_search_count"] = len(active_item_ids)
        stage_times["active_search"] = round(time.time() - stage_start, 1)
        
        if not active_item_ids:
            workflow_result["status"] = "NO_ACTIVE_RESULTS"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = stage_times
            return workflow_result
        
        # ==================================================
        # 第二步：active をバッチAIモデル解析
        # ==================================================
        stage_start = time.time()
        try:
            api_key = get_api_key()
        except Exception as exc:
            logger.warning(f"AI APIキー取得不可、スクレイピング結果のみ保存: {exc}")
            workflow_result["status"] = "SCRAPED_ONLY"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = stage_times
            return workflow_result
        
        active_items = get_active_items_by_ids(
            active_item_ids,
            only_pending=not force_reprocess
        )
        
        if active_items:
            logger.info(f"ステップ2：active商品バッチ解析、合計 {len(active_items)} 件")
            
            active_parse_result = batch_parse_models(active_items)
            
            workflow_result["active_parsed"] = active_parse_result["parsed"]
            workflow_result["active_excluded"] = active_parse_result["excluded"]
            workflow_result["active_review_required"] = active_parse_result["review_required"]
            workflow_result["active_parse_failed"] = active_parse_result["failed"]
            workflow_result["errors"].extend(active_parse_result.get("errors", []))
        
        stage_times["active_parse"] = round(time.time() - stage_start, 1)
        
        # ==================================================
        # 第三步：closed を1回検索
        # ==================================================
        stage_start = time.time()
        check_limits()
        
        logger.info(f"ステップ3：closed検索 1回実行、keyword='{keyword}', count={closed_count}")
        
        closed_item_ids = scrape_and_save_closed_once(
            keyword=keyword,
            count=closed_count,
            force_reprocess=force_reprocess
        )
        
        workflow_result["closed_search_count"] = len(closed_item_ids)
        stage_times["closed_search"] = round(time.time() - stage_start, 1)
        
        # ==================================================
        # 第四步：今回の closed 検索結果のみ解析
        # ==================================================
        stage_start = time.time()
        if closed_item_ids:
            closed_items = get_closed_items_by_ids(
                closed_item_ids,
                only_pending=not force_reprocess
            )
            
            if closed_items:
                logger.info(f"ステップ4：closed商品バッチ解析、合計 {len(closed_items)} 件")
                
                closed_parse_result = batch_parse_closed_models(closed_items)
                
                workflow_result["closed_parsed"] = closed_parse_result["parsed"]
                workflow_result["closed_excluded"] = closed_parse_result["excluded"]
                workflow_result["closed_review_required"] = closed_parse_result["review_required"]
                workflow_result["closed_parse_failed"] = closed_parse_result["failed"]
                workflow_result["errors"].extend(closed_parse_result.get("errors", []))
        
        stage_times["closed_parse"] = round(time.time() - stage_start, 1)
        
        # ==================================================
        # 第五步：プログラムによる価格評価と購入提案
        # ==================================================
        stage_start = time.time()
        active_items_for_pricing = get_unpriced_items_for_ids(
            active_item_ids,
            require_model_completed=True,
            include_completed=force_reprocess,
            limit=active_count
        )
        
        if active_items_for_pricing:
            logger.info(f"ステップ5：プログラムによる購入提案生成、合計 {len(active_items_for_pricing)} 件")
            
            pricing_result = batch_price_analysis(
                active_items_for_pricing,
                allowed_closed_item_ids=set(closed_item_ids)
            )
            
            workflow_result["pricing_attempted"] = pricing_result["attempted"]
            workflow_result["pricing_completed"] = pricing_result["completed"]
            workflow_result["pricing_insufficient_data"] = pricing_result["insufficient_data"]
            workflow_result["pricing_failed"] = pricing_result["failed"]
        
        stage_times["pricing"] = round(time.time() - stage_start, 1)
        
        # ==================================================
        # 最終ステータス
        # ==================================================
        if workflow_result["pricing_completed"] > 0:
            final_status = "COMPLETED"
        elif (
            workflow_result["pricing_insufficient_data"] > 0
            or workflow_result["active_excluded"] > 0
            or workflow_result["active_review_required"] > 0
        ):
            final_status = "PARTIAL_COMPLETED"
        elif workflow_result["active_parse_failed"] > 0:
            final_status = "PARTIAL_FAILED"
        else:
            final_status = "COMPLETED"
        
        workflow_result["status"] = final_status
        workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
        workflow_result["stage_times"] = stage_times
        
        logger.info("ワークフロー完了: %s", json.dumps(workflow_result, ensure_ascii=False, default=str))
        return workflow_result
        
    except RuntimeError as exc:
        error_message = str(exc)
        if "Token使用量が上限" in error_message or "Lambdaタイムアウト" in error_message or "残り時間不足" in error_message:
            workflow_result["status"] = "INTERRUPTED"
            workflow_result["interrupt_reason"] = error_message
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = stage_times
            return workflow_result
        raise
    except Exception as exc:
        logger.error(f"ワークフロー実行失敗: {exc}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(exc))
        workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
        workflow_result["stage_times"] = stage_times
        return workflow_result


# ==================== ステップ1：active商品検索 ====================

def scrape_and_save_active(
    keyword: str,
    count: int = 100,
    force_reprocess: bool = False
) -> List[str]:
    """active は scrape_auctions を1回だけ呼び出す"""
    logger.info(f"active 単回検索: keyword='{keyword}', count={count}")
    
    try:
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        logger.info(f"スクレイパーが {len(items)} 件の生結果を返しました")
        
        items = items[:count]
        logger.info(f"切り詰め後 {len(items)} 件を保持")
        
        saved_ids = []
        
        for item in items:
            try:
                upsert_active_item(
                    item=item,
                    keyword=keyword,
                    force_reprocess=force_reprocess
                )
                saved_ids.append(str(item["itemId"]))
            except Exception as exc:
                logger.error(f"active商品保存失敗 {item.get('itemId')}: {exc}")
        
        logger.info(f"active 単回検索完了、{len(saved_ids)} 件保存")
        return saved_ids
        
    except Exception as exc:
        logger.error(f"active 検索失敗: {exc}", exc_info=True)
        return []


def upsert_active_item(
    item: Dict,
    keyword: str,
    force_reprocess: bool = False
):
    """アクティブ商品を保存または更新"""
    now = datetime.now(timezone.utc)
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    
    set_parts = [
        "itemType = :item_type",
        "title = :title",
        "price = :price",
        "bidCount = :bid_count",
        "endTime = :end_time",
        "sellerId = :seller_id",
        "sellerRating = :seller_rating",
        "sellerType = :seller_type",
        "prefecture = :prefecture",
        "#url = :url",
        "thumbnailUrl = :thumbnail",
        "searchKeyword = :keyword",
        "lastScrapedAt = :now",
        "isFreeShipping = :is_free_shipping",
        "shippingStatus = :shipping_status",
        "workflowStatus = :workflow",
        "#ttl = :ttl"
    ]
    
    values = {
        ":item_type": item.get("itemType", "auction"),
        ":title": item.get("title", ""),
        ":price": safe_int(item.get("price", 0)),
        ":bid_count": safe_int(item.get("bidCount", 0)),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": str(item.get("sellerId") or "unknown"),
        ":seller_rating": str(item.get("sellerRating") or "unknown"),
        ":seller_type": item.get("sellerType", "personal"),
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""),
        ":thumbnail": item.get("thumbnailUrl", ""),
        ":keyword": keyword,
        ":now": now.isoformat(),
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":workflow": "ACTIVE_SCRAPED",
        ":ttl": int((now + timedelta(days=30)).timestamp()),
        ":pending": "PENDING"
    }
    
    if force_reprocess:
        set_parts.extend([
            "modelStatus = :pending",
            "pricingStatus = :pending"
        ])
    else:
        set_parts.extend([
            "modelStatus = if_not_exists(modelStatus, :pending)",
            "pricingStatus = if_not_exists(pricingStatus, :pending)"
        ])
    
    if item.get("buynowPrice") is not None:
        set_parts.append("buynowPrice = :buynow_price")
        values[":buynow_price"] = safe_int(item.get("buynowPrice"))
    
    if shipping_text:
        set_parts.append("shippingText = :shipping_text")
        values[":shipping_text"] = shipping_text
    
    if item.get("itemCondition") is not None:
        set_parts.append("itemCondition = :item_condition")
        values[":item_condition"] = item["itemCondition"]
    
    active_table.update_item(
        Key={"itemID": str(item["itemId"])},
        UpdateExpression="SET " + ", ".join(set_parts),
        ExpressionAttributeNames={"#url": "url", "#ttl": "ttl"},
        ExpressionAttributeValues=values
    )


# ==================== ステップ2：active AIモデル解析 ====================

def get_active_items_by_ids(
    item_ids: List[str],
    only_pending: bool = True
) -> List[Dict]:
    """IDリストでアクティブ商品を取得"""
    items = []
    for item_id in item_ids:
        try:
            result = active_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if item:
                if not only_pending or item.get("modelStatus") == "PENDING":
                    items.append(item)
        except Exception as e:
            logger.error(f"active商品取得失敗 {item_id}: {e}")
    return items


def batch_parse_models(items: List[Dict]) -> Dict:
    """アクティブ商品モデルをバッチ解析"""
    if not items:
        return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    batch_size = MODEL_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        
        logger.info(f"active モデル解析バッチ {batch_number}: {len(batch)} 商品")
        
        items_data = [
            {
                "itemId": str(item["itemID"]),
                "title": item.get("title", "")
            }
            for item in batch
        ]
        
        prompt = build_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        
        if not result:
            logger.error(f"active バッチ {batch_number} AIが空結果を返しました")
            for item in batch:
                mark_active_model_failed(str(item["itemID"]), "AI_RESPONSE_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"active バッチ{batch_number}（{len(batch)}商品）AIが空結果を返しました")
            continue
        
        parsed_items = result.get("items", [])
        if not isinstance(parsed_items, list):
            parsed_items = []
        
        returned_ids = set()
        for parsed in parsed_items:
            if not isinstance(parsed, dict):
                continue
            item_id = str(parsed.get("itemId", "")).strip()
            if not item_id:
                continue
            returned_ids.add(item_id)
            
            saved_status = save_active_models_minimal(item_id=item_id, parsed=parsed)
            if saved_status == "COMPLETED":
                totals["parsed"] += 1
            elif saved_status == "EXCLUDED":
                totals["excluded"] += 1
            elif saved_status == "REVIEW_REQUIRED":
                totals["review_required"] += 1
            else:
                totals["failed"] += 1
        
        input_ids = {str(item["itemID"]) for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_active_model_failed(missing_id, "AI_NOT_RETURNED")
            totals["failed"] += 1
        if missing_ids:
            totals["errors"].append(f"active バッチ{batch_number}: AIが{len(missing_ids)}商品を返しませんでした")
        
        if start + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    logger.info(
        f"active モデル解析完了: 成功={totals['parsed']}, "
        f"除外={totals['excluded']}, 要確認={totals['review_required']}, "
        f"失敗={totals['failed']}"
    )
    return totals


def build_model_parsing_prompt(items: List[Dict]) -> str:
    """active商品モデル解析プロンプトを構築（極簡版）"""
    items_text = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    
    return f"""あなたは中古電子製品の識別専門家です。
以下の商品タイトルを解析し、モデルと主要スペックを返してください。

入力：
{items_text}

以下のJSON形式のみを返してください。全ての入力IDを含めてください：
{{"items":[{{"itemId":"ID","brand":"ブランド","model":"完全なモデル名","variant":"バリエーションまたは空","storage":"容量または空","listingType":"MAIN_PRODUCT","condition":"USED","missing":[],"confidence":0.95}}]}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

ルール：
1. スマホはPro/Pro Maxを区別し、容量はstorageに
2. PCはシリーズ/世代を区別し、メモリと容量はstorageに
3. 価格に影響するスペックが不足する場合、missingに不足項目名を列挙
4. タイトルに明記されていない情報は推測しない
5. アクセサリ、部品、故障品、空箱、セットは対応するlistingTypeで
6. modelはPro/Pro Maxを区別し、iPhone 15だけにしない
7. JSONのみを出力し、説明文は一切不要"""


def parse_ai_result_minimal(parsed: Dict) -> Tuple[List[Dict], str, str, bool, List[str], str]:
    """
    極簡AI結果を解析し、補助フィールドをプログラムで生成。
    
    戻り値：(models, listing_type, condition, has_all_critical, missing, exclusion_reason)
    """
    brand = normalize(parsed.get("brand", ""))
    model_name = normalize(parsed.get("model", ""))
    variant = normalize(parsed.get("variant", ""))
    storage = normalize_storage(parsed.get("storage", ""))
    confidence = safe_decimal(parsed.get("confidence", 0))
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    condition = normalize(parsed.get("condition", "UNKNOWN")).upper()
    missing = parsed.get("missing", [])
    
    if not isinstance(missing, list):
        missing = []
    
    has_all_critical = len(missing) == 0
    
    models = []
    if brand and model_name:
        pricing_model_key = generate_pricing_model_key(
            brand=brand,
            model_name=model_name,
            storage=storage,
            variant=variant
        )
        
        models.append({
            "brand": brand,
            "model": model_name,
            "variant": variant,
            "storage": storage,
            "pricingModelKey": pricing_model_key,
            "confidence": str(confidence)
        })
    
    excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
    exclusion_reasons = []
    
    if listing_type in excluded_types:
        exclusion_reasons.append(f"商品タイプ不適: {listing_type}")
    if condition == "BROKEN":
        exclusion_reasons.append("商品状態が故障品")
    if not has_all_critical:
        exclusion_reasons.append(f"キーパラメータ不足: {', '.join(missing)}")
    
    exclusion_reason = "; ".join(exclusion_reasons)
    
    return models, listing_type, condition, has_all_critical, missing, exclusion_reason


def save_active_models_minimal(item_id: str, parsed: Dict) -> str:
    """アクティブ商品モデルを保存（極簡AI結果使用）"""
    models, listing_type, condition, has_all_critical, missing, exclusion_reason = parse_ai_result_minimal(parsed)
    
    is_analysis_eligible = (
        listing_type == "MAIN_PRODUCT"
        and condition != "BROKEN"
        and has_all_critical
        and len(models) > 0
    )
    
    if not models:
        status = "REVIEW_REQUIRED"
    elif not is_analysis_eligible:
        status = "EXCLUDED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in models):
        status = "REVIEW_REQUIRED"
    else:
        status = "COMPLETED"
    
    now = datetime.now(timezone.utc).isoformat()
    
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                listingType = :listing_type,
                hasAllCriticalParameters = :has_all_critical,
                missingCriticalParameters = :missing,
                isAnalysisEligible = :is_analysis_eligible,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now,
                workflowStatus = :workflow,
                pricingStatus = :pricing_status
        """,
        ExpressionAttributeValues={
            ":models": models,
            ":status": status,
            ":listing_type": listing_type,
            ":has_all_critical": has_all_critical,
            ":missing": missing,
            ":is_analysis_eligible": is_analysis_eligible,
            ":exclusion_reason": exclusion_reason,
            ":now": now,
            ":workflow": (
                "MODEL_PARSED" if status == "COMPLETED"
                else "MODEL_EXCLUDED" if status == "EXCLUDED"
                else "MODEL_REVIEW_REQUIRED"
            ),
            ":pricing_status": ("PENDING" if status == "COMPLETED" else "NOT_APPLICABLE")
        }
    )
    
    return status


def mark_active_model_failed(item_id: str, error: str):
    """アクティブ商品モデル解析失敗をマーク"""
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET modelStatus = :status,
                modelError = :error,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error[:500],
            ":now": now
        }
    )


# ==================== ステップ3：closed 1回検索 ====================

def scrape_and_save_closed_once(
    keyword: str,
    count: int = 100,
    force_reprocess: bool = False
) -> List[str]:
    """closed はユーザー元キーワードで1回検索"""
    logger.info(f"closed 単回検索: keyword='{keyword}', count={count}")
    
    try:
        items = scrape_auctions(keyword, "closed", False)
        logger.info(f"スクレイパーが {len(items)} 件の生結果を返しました")
        
        items = items[:count]
        logger.info(f"切り詰め後 {len(items)} 件を保持")
        
        saved_ids = []
        
        for item in items:
            try:
                upsert_closed_item_once(
                    item=item,
                    search_keyword=keyword,
                    force_reprocess=force_reprocess
                )
                saved_ids.append(str(item["itemId"]))
            except Exception as exc:
                logger.error(f"closed商品保存失敗 {item.get('itemId')}: {exc}")
        
        logger.info(f"closed 単回検索完了、{len(saved_ids)} 件保存")
        return saved_ids
        
    except Exception as exc:
        logger.error(f"closed 検索失敗: {exc}", exc_info=True)
        return []


def upsert_closed_item_once(
    item: Dict,
    search_keyword: str,
    force_reprocess: bool = False
):
    """単回検索の落札商品を保存"""
    now = datetime.now(timezone.utc)
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    
    set_parts = [
        "itemType = :item_type",
        "title = :title",
        "price = :price",
        "bidCount = :bid_count",
        "endTime = :end_time",
        "sellerId = :seller_id",
        "sellerRating = :seller_rating",
        "sellerType = :seller_type",
        "prefecture = :prefecture",
        "#url = :url",
        "thumbnailUrl = :thumbnail",
        "searchKeyword = :search_keyword",
        "lastScrapedAt = :now",
        "isFreeShipping = :is_free_shipping",
        "shippingStatus = :shipping_status",
        "#ttl = :ttl"
    ]
    
    values = {
        ":item_type": item.get("itemType", "auction"),
        ":title": item.get("title", ""),
        ":price": safe_int(item.get("price", 0)),
        ":bid_count": safe_int(item.get("bidCount", 0)),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": str(item.get("sellerId") or "unknown"),
        ":seller_rating": str(item.get("sellerRating") or "unknown"),
        ":seller_type": item.get("sellerType", "personal"),
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""),
        ":thumbnail": item.get("thumbnailUrl", ""),
        ":search_keyword": search_keyword,
        ":now": now.isoformat(),
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":ttl": int((now + timedelta(days=180)).timestamp()),
        ":pending": "PENDING"
    }
    
    if force_reprocess:
        set_parts.append("modelStatus = :pending")
    else:
        set_parts.append("modelStatus = if_not_exists(modelStatus, :pending)")
    
    if item.get("buynowPrice") is not None:
        set_parts.append("buynowPrice = :buynow_price")
        values[":buynow_price"] = safe_int(item.get("buynowPrice"))
    
    if shipping_text:
        set_parts.append("shippingText = :shipping_text")
        values[":shipping_text"] = shipping_text
    
    if item.get("itemCondition") is not None:
        set_parts.append("itemCondition = :item_condition")
        values[":item_condition"] = item["itemCondition"]
    
    closed_table.update_item(
        Key={"itemID": str(item["itemId"])},
        UpdateExpression="SET " + ", ".join(set_parts),
        ExpressionAttributeNames={"#url": "url", "#ttl": "ttl"},
        ExpressionAttributeValues=values
    )


# ==================== ステップ4：closed AIモデル解析 ====================

def get_closed_items_by_ids(
    item_ids: List[str],
    only_pending: bool = True
) -> List[Dict]:
    """IDリストで今回検索したclosed商品を取得"""
    items = []
    for item_id in item_ids:
        try:
            result = closed_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item:
                continue
            if only_pending and item.get("modelStatus") != "PENDING":
                continue
            items.append(item)
        except Exception as e:
            logger.error(f"closed商品取得失敗 {item_id}: {e}")
    return items


def batch_parse_closed_models(items: List[Dict]) -> Dict:
    """今回検索したclosed商品をバッチ解析"""
    if not items:
        return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    batch_size = CLOSED_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        
        logger.info(f"closed モデル解析バッチ {batch_number}: {len(batch)} 商品")
        
        items_data = [
            {
                "itemId": str(item["itemID"]),
                "title": item.get("title", "")
            }
            for item in batch
        ]
        
        prompt = build_closed_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        
        if not result:
            logger.error(f"closed バッチ {batch_number} AIが空結果を返しました")
            for item in batch:
                mark_closed_parse_failed(str(item["itemID"]), "AI_RESPONSE_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"closed バッチ{batch_number}（{len(batch)}商品）AIが空結果を返しました")
            continue
        
        parsed_items = result.get("items", [])
        if not isinstance(parsed_items, list):
            parsed_items = []
        
        returned_ids = set()
        for parsed in parsed_items:
            if not isinstance(parsed, dict):
                continue
            item_id = str(parsed.get("itemId", "")).strip()
            if not item_id:
                continue
            returned_ids.add(item_id)
            
            saved_status = save_closed_models_minimal(item_id=item_id, parsed=parsed)
            if saved_status == "COMPLETED":
                totals["parsed"] += 1
            elif saved_status == "EXCLUDED":
                totals["excluded"] += 1
            elif saved_status == "REVIEW_REQUIRED":
                totals["review_required"] += 1
            else:
                totals["failed"] += 1
        
        input_ids = {str(item["itemID"]) for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_closed_parse_failed(missing_id, "AI_NOT_RETURNED")
            totals["failed"] += 1
        if missing_ids:
            totals["errors"].append(f"closed バッチ{batch_number}: AIが{len(missing_ids)}商品を返しませんでした")
        
        if start + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    logger.info(
        f"closed モデル解析完了: 成功={totals['parsed']}, "
        f"除外={totals['excluded']}, 要確認={totals['review_required']}, "
        f"失敗={totals['failed']}"
    )
    return totals


def build_closed_model_parsing_prompt(items: List[Dict]) -> str:
    """closed商品モデル解析プロンプトを構築（極簡版）"""
    items_text = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    
    return f"""あなたは中古電子製品の識別専門家です。
以下の落札済み商品タイトルを解析し、モデルと主要スペックを返してください。

入力：
{items_text}

以下のJSON形式のみを返してください。全ての入力IDを含めてください：
{{"items":[{{"itemId":"ID","brand":"ブランド","model":"完全なモデル名","variant":"バリエーションまたは空","storage":"容量または空","listingType":"MAIN_PRODUCT","condition":"USED","missing":[],"confidence":0.95}}]}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

ルール：
1. スマホはPro/Pro Maxを区別し、容量はstorageに
2. PCはシリーズ/世代を区別し、メモリと容量はstorageに
3. 価格に影響するスペックが不足する場合、missingに不足項目名を列挙
4. タイトルに明記されていない情報は推測しない
5. アクセサリ、部品、故障品、空箱、セットは対応するlistingTypeで
6. modelはPro/Pro Maxを区別し、iPhone 15だけにしない
7. JSONのみを出力し、説明文は一切不要"""


def save_closed_models_minimal(item_id: str, parsed: Dict) -> str:
    """落札商品モデルを保存（極簡AI結果使用）"""
    models, listing_type, condition, has_all_critical, missing, exclusion_reason = parse_ai_result_minimal(parsed)
    
    is_comparable = (
        listing_type == "MAIN_PRODUCT"
        and condition != "BROKEN"
        and has_all_critical
        and len(models) > 0
    )
    
    if not models:
        status = "REVIEW_REQUIRED"
    elif not is_comparable:
        status = "EXCLUDED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in models):
        status = "REVIEW_REQUIRED"
    else:
        status = "COMPLETED"
    
    now = datetime.now(timezone.utc).isoformat()
    
    closed_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                listingType = :listing_type,
                isComparable = :is_comparable,
                parsedCondition = :condition,
                hasAllCriticalParameters = :has_all_critical,
                missingCriticalParameters = :missing,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":models": models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_comparable": is_comparable,
            ":condition": condition,
            ":has_all_critical": has_all_critical,
            ":missing": missing,
            ":exclusion_reason": exclusion_reason,
            ":now": now
        }
    )
    
    return status


def mark_closed_parse_failed(item_id: str, error: str):
    """落札商品モデル解析失敗をマーク"""
    now = datetime.now(timezone.utc).isoformat()
    closed_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET modelStatus = :status,
                modelError = :error,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error[:500],
            ":now": now
        }
    )


# ==================== ステップ5：プログラムによる価格評価と購入提案 ====================

def get_unpriced_items_for_ids(
    item_ids: List[str],
    require_model_completed: bool = True,
    include_completed: bool = False,
    limit: int = 100
) -> List[Dict]:
    """価格評価待ちのアクティブ商品を取得"""
    items = []
    for item_id in item_ids:
        try:
            result = active_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item:
                continue
            
            pricing_status = item.get("pricingStatus", "PENDING")
            
            if include_completed:
                if pricing_status not in {"PENDING", "COMPLETED", "INSUFFICIENT_DATA", "FAILED"}:
                    continue
            elif pricing_status != "PENDING":
                continue
            
            if require_model_completed:
                if item.get("modelStatus") != "COMPLETED":
                    continue
                if item.get("isAnalysisEligible") is not True:
                    continue
                if item.get("hasAllCriticalParameters") is not True:
                    continue
                if item.get("exclusionReason"):
                    continue
            
            models = item.get("models", [])
            if isinstance(models, str):
                try:
                    models = json.loads(models)
                except json.JSONDecodeError:
                    models = []
            if not isinstance(models, list):
                continue
            
            valid_models = [model for model in models if isinstance(model, dict) and model.get("pricingModelKey")]
            if not valid_models:
                continue
            
            items.append(item)
            if len(items) >= limit:
                break
        except Exception as e:
            logger.error(f"価格評価待ち商品取得失敗 {item_id}: {e}")
    return items


def build_closed_comparable_index(closed_item_ids: Set[str]) -> Dict[str, List[Dict]]:
    """今回のclosed検索結果を読み取り、pricingModelKeyでインデックス構築"""
    comparable_index: Dict[str, List[Dict]] = {}
    
    for item_id in closed_item_ids:
        try:
            result = closed_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item:
                continue
            if item.get("modelStatus") != "COMPLETED":
                continue
            if item.get("isComparable") is not True:
                continue
            if item.get("hasAllCriticalParameters") is not True:
                continue
            if item.get("listingType") != "MAIN_PRODUCT":
                continue
            if item.get("parsedCondition") == "BROKEN":
                continue
            
            price = safe_decimal(item.get("price", 0))
            if price <= 0:
                continue
            
            models = item.get("models", [])
            if isinstance(models, str):
                try:
                    models = json.loads(models)
                except json.JSONDecodeError:
                    continue
            if not isinstance(models, list):
                continue
            
            item_keys = set()
            for model in models:
                if not isinstance(model, dict):
                    continue
                pricing_model_key = normalize(model.get("pricingModelKey", "")).upper()
                if not pricing_model_key:
                    continue
                if pricing_model_key in item_keys:
                    continue
                item_keys.add(pricing_model_key)
                comparable_index.setdefault(pricing_model_key, []).append(item)
        except Exception as e:
            logger.error(f"closed商品読み取り失敗 {item_id}: {e}")
    
    for model_key, items in comparable_index.items():
        items.sort(key=lambda value: value.get("endTime", ""), reverse=True)
        logger.info(f"closed インデックス: {model_key} 合計 {len(items)} 件の比較可能商品")
    
    return comparable_index


def get_comparable_closed_items(
    active_item: Dict,
    comparable_index: Dict[str, List[Dict]]
) -> List[Dict]:
    """active商品のpricingModelKeyで今回のclosedインデックスから同スペック商品を取得"""
    models = active_item.get("models", [])
    if isinstance(models, str):
        try:
            models = json.loads(models)
        except json.JSONDecodeError:
            return []
    if not isinstance(models, list):
        return []
    
    comparable_items = []
    seen_ids = set()
    
    for model in models:
        if not isinstance(model, dict):
            continue
        pricing_model_key = normalize(model.get("pricingModelKey", "")).upper()
        if not pricing_model_key:
            continue
        
        matched_items = comparable_index.get(pricing_model_key, [])
        for closed_item in matched_items:
            item_id = str(closed_item.get("itemID", ""))
            if not item_id:
                continue
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            comparable_items.append(closed_item)
    
    comparable_items.sort(key=lambda value: value.get("endTime", ""), reverse=True)
    return comparable_items


def calculate_price_statistics(comparable_items: List[Dict]) -> Dict:
    """closed成約価格統計を計算、IQR法で極端な外れ値を除外"""
    price_records = []
    for item in comparable_items:
        try:
            price = safe_decimal(item.get("price", 0))
            if price <= 0:
                continue
            price_records.append({
                "itemId": str(item.get("itemID", "")),
                "price": price,
                "endTime": item.get("endTime", "")
            })
        except Exception:
            continue
    
    price_records.sort(key=lambda record: record["price"])
    prices = [record["price"] for record in price_records]
    count = len(prices)
    
    if count < MIN_COMPARABLE_COUNT:
        return {
            "count": count,
            "filtered_count": count,
            "is_sufficient": False,
            "insufficientReason": f"比較データ不足、最低{MIN_COMPARABLE_COUNT}件必要、現在{count}件",
            "prices": [int(price) for price in prices],
            "filtered_prices": [int(price) for price in prices],
            "comparableItemIds": [record["itemId"] for record in price_records if record["itemId"]]
        }
    
    def percentile(data: List[Decimal], probability: Decimal) -> Decimal:
        if not data:
            return Decimal("0")
        if len(data) == 1:
            return data[0]
        position = Decimal(len(data) - 1) * probability
        lower_index = int(position)
        fraction = position - Decimal(lower_index)
        if lower_index + 1 < len(data):
            return data[lower_index] + (data[lower_index + 1] - data[lower_index]) * fraction
        return data[lower_index]
    
    q1 = percentile(prices, Decimal("0.25"))
    median = percentile(prices, Decimal("0.50"))
    q3 = percentile(prices, Decimal("0.75"))
    iqr = q3 - q1
    
    lower_bound = q1 - MAX_PRICE_DEVIATION * iqr
    upper_bound = q3 + MAX_PRICE_DEVIATION * iqr
    
    filtered_records = [record for record in price_records if lower_bound <= record["price"] <= upper_bound]
    filtered_prices = [record["price"] for record in filtered_records]
    filtered_count = len(filtered_prices)
    
    if filtered_count < MIN_COMPARABLE_COUNT:
        return {
            "count": count,
            "filtered_count": filtered_count,
            "is_sufficient": False,
            "insufficientReason": f"異常価格除外後、比較データ不足：最低{MIN_COMPARABLE_COUNT}件必要、現在{filtered_count}件",
            "min": int(min(prices)),
            "max": int(max(prices)),
            "q1": int(q1),
            "median": int(median),
            "q3": int(q3),
            "iqr": int(iqr),
            "lowerBound": int(lower_bound),
            "upperBound": int(upper_bound),
            "prices": [int(price) for price in prices],
            "filtered_prices": [int(price) for price in filtered_prices],
            "comparableItemIds": [record["itemId"] for record in filtered_records if record["itemId"]]
        }
    
    filtered_prices.sort()
    filtered_median = percentile(filtered_prices, Decimal("0.50"))
    filtered_average = sum(filtered_prices, Decimal("0")) / Decimal(filtered_count)
    filtered_min = min(filtered_prices)
    filtered_max = max(filtered_prices)
    
    price_spread_ratio = Decimal("0")
    if filtered_median > 0:
        price_spread_ratio = ((filtered_max - filtered_min) / filtered_median).quantize(Decimal("0.001"), ROUND_HALF_UP)
    
    return {
        "count": count,
        "filtered_count": filtered_count,
        "excluded_outlier_count": count - filtered_count,
        "is_sufficient": True,
        "min": int(min(prices)),
        "max": int(max(prices)),
        "q1": int(q1),
        "median": int(median),
        "q3": int(q3),
        "iqr": int(iqr),
        "lowerBound": int(lower_bound),
        "upperBound": int(upper_bound),
        "filtered_min": int(filtered_min),
        "filtered_max": int(filtered_max),
        "filtered_median": int(filtered_median),
        "filtered_average": int(filtered_average.quantize(Decimal("1"), ROUND_HALF_UP)),
        "price_spread_ratio": price_spread_ratio,
        "prices": [int(price) for price in prices],
        "filtered_prices": [int(price) for price in filtered_prices],
        "comparableItemIds": [str(record["itemId"]) for record in filtered_records if record["itemId"]]
    }


def calculate_pricing_confidence(stats: Dict) -> Decimal:
    """比較サンプル数、価格分散度、異常値比率に基づき、プログラムで価格信頼度を生成"""
    if not stats.get("is_sufficient"):
        return Decimal("0.20")
    
    comparable_count = safe_int(stats.get("filtered_count", 0))
    spread_ratio = safe_decimal(stats.get("price_spread_ratio", 0))
    total_count = safe_int(stats.get("count", 0))
    excluded_count = safe_int(stats.get("excluded_outlier_count", 0))
    
    if comparable_count >= HIGH_CONFIDENCE_COMPARABLE_COUNT:
        confidence = Decimal("0.90")
    elif comparable_count >= MEDIUM_CONFIDENCE_COMPARABLE_COUNT:
        confidence = Decimal("0.80")
    else:
        confidence = Decimal("0.70")
    
    if spread_ratio >= Decimal("0.50"):
        confidence -= Decimal("0.20")
    elif spread_ratio >= Decimal("0.30"):
        confidence -= Decimal("0.10")
    
    if total_count > 0:
        outlier_ratio = Decimal(excluded_count) / Decimal(total_count)
        if outlier_ratio >= Decimal("0.30"):
            confidence -= Decimal("0.10")
    
    if confidence < Decimal("0.20"):
        confidence = Decimal("0.20")
    if confidence > Decimal("0.95"):
        confidence = Decimal("0.95")
    
    return confidence.quantize(Decimal("0.01"), ROUND_HALF_UP)


def parse_seller_rating(value: Any) -> Optional[Decimal]:
    """出品者評価を百分率に変換"""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "unknown":
        return None
    try:
        if text.endswith("%"):
            return Decimal(text[:-1].strip())
        rating = Decimal(text)
        if Decimal("0") <= rating <= Decimal("1"):
            return rating * Decimal("100")
        return rating
    except Exception:
        return None


def determine_programmatic_risk(
    active_item: Dict,
    stats: Dict,
    pricing_confidence: Decimal,
    profit_margin: Decimal,
    has_buynow_price: bool
) -> Dict:
    """完全にプログラムでリスクレベルとリスク要因を判断"""
    risk_score = 0
    risk_factors = []
    reasons = []
    
    comparable_count = safe_int(stats.get("filtered_count", 0))
    spread_ratio = safe_decimal(stats.get("price_spread_ratio", 0))
    
    if comparable_count < 5:
        risk_score += 2
        risk_factors.append(f"有効比較サンプルが少ない、{comparable_count}件のみ")
    elif comparable_count < 10:
        risk_score += 1
        risk_factors.append(f"有効比較サンプル数が普通、合計{comparable_count}件")
    else:
        reasons.append(f"有効比較サンプル数が十分、合計{comparable_count}件")
    
    if pricing_confidence < Decimal("0.50"):
        risk_score += 3
        risk_factors.append("価格統計信頼度が低い")
    elif pricing_confidence < Decimal("0.75"):
        risk_score += 1
        risk_factors.append("価格統計信頼度が普通")
    else:
        reasons.append(f"価格統計信頼度は{pricing_confidence}")
    
    if spread_ratio >= Decimal("0.50"):
        risk_score += 2
        risk_factors.append("同型落札価格の分布が非常に分散")
    elif spread_ratio >= Decimal("0.30"):
        risk_score += 1
        risk_factors.append("同型落札価格にある程度の変動あり")
    
    seller_rating = parse_seller_rating(active_item.get("sellerRating"))
    if seller_rating is None:
        risk_score += 1
        risk_factors.append("出品者評価が確認不可")
    elif seller_rating < Decimal("95"):
        risk_score += 2
        risk_factors.append(f"出品者評価が低い：{seller_rating}%")
    elif seller_rating < Decimal("98"):
        risk_score += 1
        risk_factors.append(f"出品者評価が普通：{seller_rating}%")
    else:
        reasons.append(f"出品者評価が高い：{seller_rating}%")
    
    seller_type = str(active_item.get("sellerType", "personal")).lower()
    if seller_type == "personal":
        risk_score += 1
        risk_factors.append("個人出品者による商品")
    elif seller_type == "store":
        reasons.append("ストア出品者による商品")
    
    shipping_status = active_item.get("shippingStatus", "UNKNOWN")
    if shipping_status == "UNKNOWN":
        risk_score += 1
        risk_factors.append("送料確認不可、実際のコストが増加する可能性")
    elif shipping_status == "FREE":
        reasons.append("送料込み商品")
    
    active_condition = normalize(active_item.get("itemCondition", ""))
    if not active_condition:
        risk_score += 1
        risk_factors.append("商品状態欄が不明確")
    
    if profit_margin < Decimal("0"):
        risk_score += 3
        risk_factors.append("現在価格で購入すると損失見込み")
    elif profit_margin < REVIEW_MARGIN_THRESHOLD:
        risk_score += 2
        risk_factors.append("予想利益率が審査閾値未満")
    elif profit_margin < BUY_MARGIN_THRESHOLD:
        risk_score += 1
        risk_factors.append("予想利益率が推奨購入閾値に達していない")
    else:
        reasons.append("予想利益率が推奨購入閾値に到達")
    
    if has_buynow_price:
        reasons.append("即決価格での収益も同時計算済み")
    
    if risk_score >= 6:
        risk_level = "HIGH"
    elif risk_score >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "riskLevel": risk_level,
        "riskScore": risk_score,
        "riskFactors": risk_factors,
        "reasons": reasons
    }


def determine_purchase_decision(
    net_profit: Decimal,
    profit_margin: Decimal,
    risk_level: str,
    pricing_confidence: Decimal,
    comparable_count: int
) -> str:
    """プログラムで購入提案を生成"""
    if comparable_count < MIN_COMPARABLE_COUNT:
        return "INSUFFICIENT_DATA"
    if net_profit <= 0:
        return "AVOID"
    if profit_margin >= BUY_MARGIN_THRESHOLD and risk_level in {"LOW", "MEDIUM"} and pricing_confidence >= Decimal("0.70"):
        return "BUY_CANDIDATE"
    if profit_margin >= REVIEW_MARGIN_THRESHOLD and pricing_confidence >= Decimal("0.50"):
        return "REVIEW"
    if risk_level == "HIGH" and profit_margin < BUY_MARGIN_THRESHOLD:
        return "AVOID"
    return "REVIEW"


def build_programmatic_reasons(
    estimated_price: Decimal,
    purchase_price: Decimal,
    net_profit: Decimal,
    profit_margin: Decimal,
    decision_signal: str,
    stats: Dict
) -> List[str]:
    """AIに依存しない購入提案理由を生成"""
    reasons = []
    comparable_count = safe_int(stats.get("filtered_count", 0))
    
    reasons.append(f"価格判断は{comparable_count}件の同スペック有効成約サンプルに基づく")
    reasons.append(f"同スペック成約価格中央値は約{int(estimated_price)}円")
    
    if purchase_price > estimated_price:
        reasons.append(f"現在価格は市場中央値より{int(purchase_price - estimated_price)}円高い")
    elif purchase_price < estimated_price:
        reasons.append(f"現在価格は市場中央値より{int(estimated_price - purchase_price)}円低い")
    else:
        reasons.append("現在価格は市場中央値と同じ")
    
    if net_profit > 0:
        reasons.append(f"手数料・送料・リスク準備金控除後、予想純利益は{int(net_profit)}円")
    else:
        reasons.append(f"手数料・送料・リスク準備金控除後、予想損失{abs(int(net_profit))}円")
    
    margin_percent = (profit_margin * Decimal("100")).quantize(Decimal("0.1"), ROUND_HALF_UP)
    reasons.append(f"予想販売利益率は{margin_percent}%")
    
    decision_text = {
        "BUY_CANDIDATE": "プログラム判断：利益余地が購入候補基準に到達",
        "REVIEW": "プログラム判断：商品状態と最終落札価格の人手確認が必要",
        "AVOID": "プログラム判断：現在価格では合理的な利益余地なし",
        "INSUFFICIENT_DATA": "比較データ不足、信頼できる購入提案を生成不可"
    }
    
    reasons.append(decision_text.get(decision_signal, "プログラムが明確な提案を生成できません"))
    return reasons


def get_effective_shipping_cost(item: Dict) -> Decimal:
    """仕入れ送料を決定"""
    is_free_shipping = parse_bool(item.get("isFreeShipping", False))
    shipping_status = str(item.get("shippingStatus", "UNKNOWN")).upper()
    
    if is_free_shipping and shipping_status == "FREE":
        return Decimal("0")
    
    shipping_fee = item.get("shippingFee")
    if shipping_fee is not None:
        parsed_fee = safe_decimal(shipping_fee, DEFAULT_SHIPPING_COST)
        if parsed_fee >= 0:
            return parsed_fee
    
    return DEFAULT_SHIPPING_COST


def generate_programmatic_pricing_result(
    active_item: Dict,
    stats: Dict,
    purchase_price: Decimal,
    actual_shipping: Decimal = Decimal("0"),
    buynow_price: Optional[Decimal] = None
) -> Dict:
    """完全にプログラムで価格・リスク・購入提案を生成"""
    if not stats.get("is_sufficient"):
        comparable_ids = [str(item_id) for item_id in stats.get("comparableItemIds", [])]
        return to_dynamodb_value({
            "pricingStatus": "INSUFFICIENT_DATA",
            "pricingConfidence": Decimal("0.20"),
            "riskLevel": "HIGH",
            "riskScore": 10,
            "decisionSignal": "INSUFFICIENT_DATA",
            "reasons": [stats.get("insufficientReason", "比較データ不足")],
            "riskFactors": ["有効成約サンプル不足、信頼できる価格評価不可"],
            "comparableCount": safe_int(stats.get("filtered_count", stats.get("count", 0))),
            "comparableItemIds": comparable_ids
        })
    
    estimated_price = safe_decimal(stats.get("filtered_median", 0))
    estimated_low = safe_decimal(stats.get("filtered_min", 0))
    estimated_high = safe_decimal(stats.get("filtered_max", 0))
    
    platform_fee = (estimated_price * EXPECTED_SELLING_FEE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    repair_reserve = (estimated_price * DEFAULT_REPAIR_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    risk_reserve = (estimated_price * RISK_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    
    total_non_purchase_costs = platform_fee + actual_shipping + repair_reserve + risk_reserve
    net_profit_at_bid = estimated_price - purchase_price - total_non_purchase_costs
    
    profit_margin_at_bid = Decimal("0")
    if estimated_price > 0:
        profit_margin_at_bid = (net_profit_at_bid / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP)
    
    total_bid_investment = purchase_price + actual_shipping + repair_reserve + risk_reserve
    roi_at_bid = Decimal("0")
    if total_bid_investment > 0:
        roi_at_bid = (net_profit_at_bid / total_bid_investment).quantize(Decimal("0.001"), ROUND_HALF_UP)
    
    pricing_confidence = calculate_pricing_confidence(stats)
    comparable_count = safe_int(stats.get("filtered_count", 0))
    
    preliminary_risk = determine_programmatic_risk(
        active_item=active_item,
        stats=stats,
        pricing_confidence=pricing_confidence,
        profit_margin=profit_margin_at_bid,
        has_buynow_price=(buynow_price is not None and buynow_price > 0)
    )
    
    decision_signal = determine_purchase_decision(
        net_profit=net_profit_at_bid,
        profit_margin=profit_margin_at_bid,
        risk_level=preliminary_risk["riskLevel"],
        pricing_confidence=pricing_confidence,
        comparable_count=comparable_count
    )
    
    programmatic_reasons = build_programmatic_reasons(
        estimated_price=estimated_price,
        purchase_price=purchase_price,
        net_profit=net_profit_at_bid,
        profit_margin=profit_margin_at_bid,
        decision_signal=decision_signal,
        stats=stats
    )
    
    break_even_price = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE)
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_10 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - Decimal("0.10"))
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_20 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - Decimal("0.20"))
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    comparable_item_ids = [str(item_id) for item_id in stats.get("comparableItemIds", []) if str(item_id)]
    
    result = {
        "pricingStatus": "COMPLETED",
        "analysisMethod": "PROGRAMMATIC",
        "estimatedMarketPrice": int(estimated_price),
        "estimatedLow": int(estimated_low),
        "estimatedHigh": int(estimated_high),
        "currentBidPrice": int(purchase_price),
        "breakEvenPurchasePrice": max(0, int(break_even_price)),
        "targetPurchasePrice10Margin": max(0, int(target_price_10)),
        "targetPurchasePrice20Margin": max(0, int(target_price_20)),
        "netProfitAtCurrentBid": int(net_profit_at_bid),
        "profitMarginAtCurrentBid": profit_margin_at_bid,
        "roiAtCurrentBid": roi_at_bid,
        "pricingConfidence": pricing_confidence,
        "riskLevel": preliminary_risk["riskLevel"],
        "riskScore": preliminary_risk["riskScore"],
        "decisionSignal": decision_signal,
        "reasons": programmatic_reasons + preliminary_risk["reasons"],
        "riskFactors": preliminary_risk["riskFactors"],
        "conditionAdjustment": "NONE",
        "comparableItemIds": comparable_item_ids,
        "comparableCount": comparable_count,
        "rawComparableCount": safe_int(stats.get("count", 0)),
        "excludedOutlierCount": safe_int(stats.get("excluded_outlier_count", 0)),
        "priceSpreadRatio": safe_decimal(stats.get("price_spread_ratio", 0)),
        "priceBreakdown": {
            "estimatedSellingPrice": int(estimated_price),
            "currentBidPrice": int(purchase_price),
            "platformFee": int(platform_fee),
            "shippingCost": int(actual_shipping),
            "repairReserve": int(repair_reserve),
            "riskReserve": int(risk_reserve),
            "netProfit": int(net_profit_at_bid)
        }
    }
    
    if buynow_price is not None and buynow_price > 0:
        net_profit_at_buynow = estimated_price - buynow_price - total_non_purchase_costs
        profit_margin_at_buynow = Decimal("0")
        if estimated_price > 0:
            profit_margin_at_buynow = (net_profit_at_buynow / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP)
        
        total_buynow_investment = buynow_price + actual_shipping + repair_reserve + risk_reserve
        roi_at_buynow = Decimal("0")
        if total_buynow_investment > 0:
            roi_at_buynow = (net_profit_at_buynow / total_buynow_investment).quantize(Decimal("0.001"), ROUND_HALF_UP)
        
        buynow_risk = determine_programmatic_risk(
            active_item=active_item,
            stats=stats,
            pricing_confidence=pricing_confidence,
            profit_margin=profit_margin_at_buynow,
            has_buynow_price=True
        )
        
        buynow_decision = determine_purchase_decision(
            net_profit=net_profit_at_buynow,
            profit_margin=profit_margin_at_buynow,
            risk_level=buynow_risk["riskLevel"],
            pricing_confidence=pricing_confidence,
            comparable_count=comparable_count
        )
        
        result.update({
            "buynowPrice": int(buynow_price),
            "netProfitAtBuynow": int(net_profit_at_buynow),
            "profitMarginAtBuynow": profit_margin_at_buynow,
            "roiAtBuynow": roi_at_buynow,
            "buynowDecisionSignal": buynow_decision,
            "buynowRiskLevel": buynow_risk["riskLevel"]
        })
    
    return to_dynamodb_value(result)


def batch_price_analysis(
    items: List[Dict],
    allowed_closed_item_ids: Set[str]
) -> Dict:
    """全てのactive商品にプログラム価格分析を実行"""
    totals = {"attempted": 0, "completed": 0, "insufficient_data": 0, "failed": 0}
    
    if not items:
        return totals
    
    comparable_index = build_closed_comparable_index({
        str(item_id) for item_id in allowed_closed_item_ids
    })
    
    logger.info(f"closed 比較可能インデックスに {len(comparable_index)} のpricingModelKey")
    
    for item in items:
        item_id = str(item.get("itemID", ""))
        try:
            check_timeout()
            totals["attempted"] += 1
            
            comparable_items = get_comparable_closed_items(
                active_item=item,
                comparable_index=comparable_index
            )
            
            stats = calculate_price_statistics(comparable_items)
            purchase_price = safe_decimal(item.get("price", 0))
            actual_shipping = get_effective_shipping_cost(item)
            
            raw_buynow_price = item.get("buynowPrice")
            buynow_price = None
            if raw_buynow_price is not None:
                buynow_price = safe_decimal(raw_buynow_price)
                if buynow_price <= 0:
                    buynow_price = None
            
            pricing_result = generate_programmatic_pricing_result(
                active_item=item,
                stats=stats,
                purchase_price=purchase_price,
                actual_shipping=actual_shipping,
                buynow_price=buynow_price
            )
            
            save_pricing_result(item_id=item_id, pricing_result=pricing_result)
            
            pricing_status = pricing_result.get("pricingStatus")
            if pricing_status == "COMPLETED":
                totals["completed"] += 1
            elif pricing_status == "INSUFFICIENT_DATA":
                totals["insufficient_data"] += 1
            else:
                totals["failed"] += 1
                
        except RuntimeError:
            raise
        except Exception as exc:
            logger.error(f"プログラム価格評価失敗 {item_id}: {exc}", exc_info=True)
            mark_pricing_failed(item_id, str(exc))
            totals["failed"] += 1
    
    return totals


def save_pricing_result(item_id: str, pricing_result: Dict):
    """プログラム分析結果を保存"""
    now = datetime.now(timezone.utc).isoformat()
    pricing_status = pricing_result.get("pricingStatus", "FAILED")
    
    workflow_status_map = {
        "COMPLETED": "PRICING_COMPLETED",
        "INSUFFICIENT_DATA": "PRICING_INSUFFICIENT_DATA",
        "FAILED": "PRICING_FAILED"
    }
    workflow_status = workflow_status_map.get(pricing_status, "PRICING_FAILED")
    
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET pricingResult = :result,
                pricingStatus = :status,
                pricedAt = :now,
                workflowStatus = :workflow,
                pricingMethod = :method
        """,
        ExpressionAttributeValues={
            ":result": to_dynamodb_value(pricing_result),
            ":status": pricing_status,
            ":now": now,
            ":workflow": workflow_status,
            ":method": "PROGRAMMATIC"
        }
    )


def mark_pricing_failed(item_id: str, error: str):
    """価格評価失敗をマーク"""
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET pricingStatus = :status,
                pricingError = :error,
                pricedAt = :now,
                workflowStatus = :workflow,
                pricingMethod = :method
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": str(error)[:500],
            ":now": now,
            ":workflow": "PRICING_FAILED",
            ":method": "PROGRAMMATIC"
        }
    )


# ==================== AI 呼び出し ====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
    """リトライ付きAI呼び出し"""
    for attempt in range(AI_MAX_RETRIES):
        try:
            check_limits()
            remaining = get_remaining_seconds()
            if remaining < AI_REQUEST_TIMEOUT + 10:
                raise RuntimeError(f"残り時間不足: 残り{remaining:.1f}秒")
            
            result, finish_reason = call_ai(prompt)
            
            if result is not None:
                return result
            
            if finish_reason == "length":
                logger.error("AI出力がmax_tokens制限に達しました。バッチが大きすぎます。リトライしません")
                return None
            
            logger.warning(f"AIが空結果を返しました (finish_reason={finish_reason})、リトライ {attempt + 1}/{AI_MAX_RETRIES}")
            
        except RuntimeError as e:
            error_msg = str(e)
            if "Token使用量が上限" in error_msg or "Lambdaタイムアウト" in error_msg or "残り時間不足" in error_msg:
                raise
            logger.error(f"AI呼び出し例外 (試行 {attempt + 1}): {e}")
        except Exception as e:
            logger.error(f"AI呼び出し例外 (試行 {attempt + 1}): {e}")
        
        if attempt < AI_MAX_RETRIES - 1:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    logger.error(f"AI呼び出し失敗、{AI_MAX_RETRIES}回リトライ済み")
    return None


def call_ai(prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    """AI APIを呼び出す"""
    try:
        api_key = get_api_key()
    except Exception as e:
        raise
    
    body = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "あなたは電子製品の専門家です。必ず有効なJSON形式のみを返してください。説明文は一切不要です。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0,
        "max_tokens": AI_MAX_OUTPUT_TOKENS,
        "response_format": {"type": "json_object"}
    }
    
    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    
    request = urllib.request.Request(
        AI_API_URL,
        data=encoded_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(request, timeout=AI_REQUEST_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            usage = result.get("usage", {})
            if usage:
                update_token_usage(usage)
            
            finish_reason = None
            content = ""
            
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason", "unknown")
            else:
                content = result.get("content", "")
                finish_reason = result.get("finish_reason", "unknown")
            
            parsed = parse_ai_json(content)
            return parsed, finish_reason
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"AI API HTTP {e.code}: {error_body[:500]}")
        if e.code in RETRYABLE_CODES:
            raise
        return None, f"http_{e.code}"
    except Exception as e:
        raise


def parse_ai_json(content: str) -> Optional[Dict]:
    """AIが返したJSONを解析"""
    if not content:
        return None
    content = content.strip()
    parse_attempts = [
        lambda c: json.loads(c),
        lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", c)),
        lambda c: json.loads(re.search(r"\{[\s\S]*\}", c).group(0)),
    ]
    for attempt in parse_attempts:
        try:
            return attempt(content)
        except (json.JSONDecodeError, AttributeError):
            continue
    logger.error(f"AI応答を解析できません: {content[:500]}")
    return None
