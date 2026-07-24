"""
Yahoo Auction 商品分析工作流 Lambda (重构版 - 程序化估价)
主要变更：
1. active/closed 各搜索一次，不再按型号分别搜索
2. AI 仅用于型号和关键参数解析
3. 价格统计、风险等级、购买建议完全由程序生成
4. 仅在本次搜索到的 closed 中匹配
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

# ============ 环境变量 ============
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
AI_API_URL = os.getenv("AI_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "doubao-seed-2-0-mini-260428")
AI_API_KEY = os.getenv("AI_API_KEY", "")
SECRET_NAME = os.getenv("SECRET_NAME", "yahoo-auction-ai-api-key")

# active 和 closed 默认各抓取 100 条，并且每种类型只搜索一次
DEFAULT_ACTIVE_COUNT = int(os.getenv("DEFAULT_ACTIVE_COUNT", "100"))
DEFAULT_CLOSED_COUNT = int(os.getenv("DEFAULT_CLOSED_COUNT", "100"))
MAX_ACTIVE_ITEMS = int(os.getenv("MAX_ACTIVE_ITEMS", "100"))
MAX_CLOSED_ITEMS = int(os.getenv("MAX_CLOSED_ITEMS", "100"))

# AI 仅用于型号和关键参数解析
MODEL_PARSE_BATCH_SIZE = int(os.getenv("MODEL_PARSE_BATCH_SIZE", "20"))
CLOSED_PARSE_BATCH_SIZE = int(os.getenv("CLOSED_PARSE_BATCH_SIZE", "20"))
AI_MAX_OUTPUT_TOKENS = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "6000"))

# 程序生成购买建议时的阈值
BUY_MARGIN_THRESHOLD = Decimal(os.getenv("BUY_MARGIN_THRESHOLD", "0.20"))
REVIEW_MARGIN_THRESHOLD = Decimal(os.getenv("REVIEW_MARGIN_THRESHOLD", "0.10"))
HIGH_CONFIDENCE_COMPARABLE_COUNT = int(os.getenv("HIGH_CONFIDENCE_COMPARABLE_COUNT", "10"))
MEDIUM_CONFIDENCE_COMPARABLE_COUNT = int(os.getenv("MEDIUM_CONFIDENCE_COMPARABLE_COUNT", "5"))

AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "60"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "3"))
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "1.0"))
INCLUDE_PAYPAY = os.getenv("INCLUDE_PAYPAY", "false").lower() == "true"

MAX_TOTAL_TOKENS = int(os.getenv("MAX_TOTAL_TOKENS", "50000"))
LAMBDA_TIMEOUT_SECONDS = int(os.getenv("LAMBDA_TIMEOUT_SECONDS", "840"))
LAMBDA_TIMEOUT_BUFFER = int(os.getenv("LAMBDA_TIMEOUT_BUFFER", "30"))

# 定价参数
EXPECTED_SELLING_FEE_RATE = Decimal(os.getenv("EXPECTED_SELLING_FEE_RATE", "0.10"))
DEFAULT_SHIPPING_COST = Decimal(os.getenv("DEFAULT_SHIPPING_COST", "1500"))
DEFAULT_REPAIR_RESERVE_RATE = Decimal(os.getenv("DEFAULT_REPAIR_RESERVE_RATE", "0.05"))
MIN_COMPARABLE_COUNT = int(os.getenv("MIN_COMPARABLE_COUNT", "3"))
MAX_PRICE_DEVIATION = Decimal(os.getenv("MAX_PRICE_DEVIATION", "1.5"))
RISK_RESERVE_RATE = Decimal(os.getenv("RISK_RESERVE_RATE", "0.03"))

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
    """获取 AI API 密钥"""
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
            raise RuntimeError("Secret 中没有 SecretString 值")
        try:
            secret_dict = json.loads(secret_string)
            api_key = (
                secret_dict.get("apiKey") or 
                secret_dict.get("api_key") or 
                secret_dict.get("key") or
                secret_dict.get("API_KEY")
            )
            if not api_key:
                raise RuntimeError("Secret JSON 中未找到 apiKey/api_key/key/API_KEY")
            _api_key_cache = api_key
        except json.JSONDecodeError:
            _api_key_cache = secret_string
        return _api_key_cache
    except Exception as e:
        logger.error(f"从 Secrets Manager 获取密钥失败: {e}")
        raise RuntimeError(f"无法获取 API 密钥: {e}")


# ==================== Token 和超时控制 ====================

def get_elapsed_seconds():
    """获取 Lambda 已运行秒数"""
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    """获取 Lambda 剩余可用秒数"""
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    """检查 Lambda 是否接近超时"""
    remaining = get_remaining_seconds()
    if remaining <= 0:
        raise RuntimeError(
            f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒, "
            f"超时限制{LAMBDA_TIMEOUT_SECONDS}秒, 缓冲{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_token_limit():
    """检查 Token 使用是否超限"""
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}，中断执行"
        )


def check_limits():
    """同时检查 Token 和超时"""
    check_token_limit()
    check_timeout()


def update_token_usage(usage):
    """更新 Token 使用统计"""
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        logger.info(
            f"Token用量更新: +{total}, 总计={_total_tokens_used}/{MAX_TOTAL_TOKENS}, "
            f"剩余={MAX_TOTAL_TOKENS - _total_tokens_used}"
        )


# ==================== 工具函数 ====================

def to_dynamodb_value(value: Any) -> Any:
    """
    将 Python 值转换为 DynamoDB 可接受的结构。
    关键规则：字符串永远保持字符串，商品 ID 不会被错误转换为数字
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
    """安全转换为 Decimal，失败返回默认值"""
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数，失败返回默认值"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def normalize(value: str) -> str:
    """全角转半角，去除多余空格"""
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
    规范化存储容量。
    示例：256G -> 256GB, 1 tb -> 1TB
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
    """安全转换为布尔值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def determine_shipping_status(shipping_text: str) -> Dict:
    """判断运费状态"""
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
    生成价格匹配键。
    示例：APPLE IPHONE 15 PRO 256GB
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
    # model 名称已经包含 variant 时不重复添加
    if normalized_variant and not model_contains_variant(normalized_model, normalized_variant):
        parts.append(normalized_variant)
    if normalized_storage:
        parts.append(normalized_storage)
    
    combined = " ".join(parts)
    combined = re.sub(r"[^A-Z0-9\s+\-/]", " ", combined)
    combined = re.sub(r"\s+", " ", combined).strip()
    return combined


def model_contains_variant(model_name: str, variant: str) -> bool:
    """检查 model 名称是否已包含 variant"""
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
    """构建 Lambda 响应"""
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    """Lambda 入口函数"""
    global _total_tokens_used, _lambda_start_time
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    
    try:
        keyword = normalize(event.get("keyword", ""))
        if not keyword:
            return response(400, {"error": "keyword 不能为空"})
        
        try:
            active_count = int(event.get("active_count", event.get("count", DEFAULT_ACTIVE_COUNT)))
            closed_count = int(event.get("closed_count", DEFAULT_CLOSED_COUNT))
        except (ValueError, TypeError):
            return response(400, {"error": "active_count、closed_count 必须是有效整数"})
        
        force_reprocess = parse_bool(event.get("force_reprocess", False))
        
        active_count = max(1, min(active_count, MAX_ACTIVE_ITEMS))
        closed_count = max(1, min(closed_count, MAX_CLOSED_ITEMS))
        
        logger.info(
            f"开始商品分析工作流: keyword='{keyword}', "
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
        logger.error(f"工作流执行失败: {e}", exc_info=True)
        return response(500, {
            "error": "内部错误",
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
    新工作流：
    1. active 使用原始 keyword 搜索一次，最多 active_count 条
    2. active 分批发送给 AI 解析型号
    3. closed 使用原始 keyword 搜索一次，最多 closed_count 条
    4. closed 分批发送给 AI 解析型号
    5. 每个 active 用 pricingModelKey 匹配 closed
    6. 全部价格统计和购买建议由程序生成
    """
    start_time = time.time()
    
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
        # 第一步：active 搜索一次
        # ==================================================
        logger.info(f"第一步：active 搜索一次，keyword='{keyword}', count={active_count}")
        
        active_item_ids = scrape_and_save_active(
            keyword=keyword,
            count=active_count,
            force_reprocess=force_reprocess
        )
        
        workflow_result["active_search_count"] = len(active_item_ids)
        
        if not active_item_ids:
            workflow_result["status"] = "NO_ACTIVE_RESULTS"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return workflow_result
        
        # ==================================================
        # 第二步：active 批量 AI 型号解析
        # ==================================================
        try:
            api_key = get_api_key()
        except Exception as exc:
            logger.warning(f"无法取得 AI API Key，仅保存抓取结果: {exc}")
            workflow_result["status"] = "SCRAPED_ONLY"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return workflow_result
        
        active_items = get_active_items_by_ids(
            active_item_ids,
            only_pending=not force_reprocess
        )
        
        if active_items:
            logger.info(f"第二步：批量解析 active 商品，共 {len(active_items)} 条")
            
            active_parse_result = batch_parse_models(active_items)
            
            workflow_result["active_parsed"] = active_parse_result["parsed"]
            workflow_result["active_excluded"] = active_parse_result["excluded"]
            workflow_result["active_review_required"] = active_parse_result["review_required"]
            workflow_result["active_parse_failed"] = active_parse_result["failed"]
            workflow_result["errors"].extend(active_parse_result.get("errors", []))
        
        # ==================================================
        # 第三步：closed 搜索一次
        # ==================================================
        check_limits()
        
        logger.info(f"第三步：closed 搜索一次，keyword='{keyword}', count={closed_count}")
        
        closed_item_ids = scrape_and_save_closed_once(
            keyword=keyword,
            count=closed_count,
            force_reprocess=force_reprocess
        )
        
        workflow_result["closed_search_count"] = len(closed_item_ids)
        
        # ==================================================
        # 第四步：仅解析本次 closed 搜索结果
        # ==================================================
        if closed_item_ids:
            closed_items = get_closed_items_by_ids(
                closed_item_ids,
                only_pending=not force_reprocess
            )
            
            if closed_items:
                logger.info(f"第四步：批量解析 closed 商品，共 {len(closed_items)} 条")
                
                closed_parse_result = batch_parse_closed_models(closed_items)
                
                workflow_result["closed_parsed"] = closed_parse_result["parsed"]
                workflow_result["closed_excluded"] = closed_parse_result["excluded"]
                workflow_result["closed_review_required"] = closed_parse_result["review_required"]
                workflow_result["closed_parse_failed"] = closed_parse_result["failed"]
                workflow_result["errors"].extend(closed_parse_result.get("errors", []))
        
        # ==================================================
        # 第五步：程序估价和购买建议
        # ==================================================
        active_items_for_pricing = get_unpriced_items_for_ids(
            active_item_ids,
            require_model_completed=True,
            include_completed=force_reprocess,
            limit=active_count
        )
        
        if active_items_for_pricing:
            logger.info(f"第五步：程序生成购买建议，共 {len(active_items_for_pricing)} 条")
            
            pricing_result = batch_price_analysis(
                active_items_for_pricing,
                allowed_closed_item_ids=set(closed_item_ids)
            )
            
            workflow_result["pricing_attempted"] = pricing_result["attempted"]
            workflow_result["pricing_completed"] = pricing_result["completed"]
            workflow_result["pricing_insufficient_data"] = pricing_result["insufficient_data"]
            workflow_result["pricing_failed"] = pricing_result["failed"]
        
        # ==================================================
        # 最终状态
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
        
        logger.info("工作流完成: %s", json.dumps(workflow_result, ensure_ascii=False, default=str))
        return workflow_result
        
    except RuntimeError as exc:
        error_message = str(exc)
        if "Token用量已达上限" in error_message or "Lambda超时倒计时" in error_message or "剩余时间不足" in error_message:
            workflow_result["status"] = "INTERRUPTED"
            workflow_result["interrupt_reason"] = error_message
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return workflow_result
        raise
    except Exception as exc:
        logger.error(f"工作流执行失败: {exc}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(exc))
        workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
        return workflow_result


# ==================== 第一步：搜索活跃商品 ====================

def scrape_and_save_active(
    keyword: str,
    count: int = 100,
    force_reprocess: bool = False
) -> List[str]:
    """active 只调用一次 scrape_auctions"""
    logger.info(f"active 单次搜索: keyword='{keyword}', count={count}")
    
    try:
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        items = items[:count]
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
                logger.error(f"保存 active 商品失败 {item.get('itemId')}: {exc}")
        
        logger.info(f"active 单次搜索完成，保存 {len(saved_ids)} 条")
        return saved_ids
        
    except Exception as exc:
        logger.error(f"active 搜索失败: {exc}", exc_info=True)
        return []


def upsert_active_item(
    item: Dict,
    keyword: str,
    force_reprocess: bool = False
):
    """保存或更新活跃商品"""
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


# ==================== 第二步：active AI 型号解析 ====================

def get_active_items_by_ids(
    item_ids: List[str],
    only_pending: bool = True
) -> List[Dict]:
    """通过 ID 列表获取活跃商品"""
    items = []
    for item_id in item_ids:
        try:
            result = active_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if item:
                if not only_pending or item.get("modelStatus") == "PENDING":
                    items.append(item)
        except Exception as e:
            logger.error(f"获取 active 商品 {item_id} 失败: {e}")
    return items


def batch_parse_models(items: List[Dict]) -> Dict:
    """批量解析 active 商品型号"""
    if not items:
        return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    batch_size = MODEL_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        
        logger.info(f"active 型号解析批次 {batch_number}: {len(batch)} 个商品")
        
        items_data = [
            {
                "itemId": str(item["itemID"]),
                "title": item.get("title", ""),
                "itemCondition": item.get("itemCondition", "")
            }
            for item in batch
        ]
        
        prompt = build_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        
        if not result:
            logger.error(f"active 批次 {batch_number} AI 返回空结果")
            for item in batch:
                mark_active_model_failed(str(item["itemID"]), "AI_RESPONSE_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"active 批次{batch_number}（{len(batch)}个商品）AI返回空结果")
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
            
            saved_status = save_active_models(item_id=item_id, parsed=parsed)
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
            totals["errors"].append(f"active 批次{batch_number}: AI未返回{len(missing_ids)}个商品")
        
        if start + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    logger.info(
        f"active 型号解析完成: 成功={totals['parsed']}, "
        f"排除={totals['excluded']}, 需审核={totals['review_required']}, "
        f"失败={totals['failed']}"
    )
    return totals


def build_model_parsing_prompt(items: List[Dict]) -> str:
    """构建 active 商品型号解析 Prompt"""
    items_text = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    
    return f"""
あなたは中古電子製品の商品識別と価格比較適格性判定の専門家です。

以下のYahooオークションの商品タイトルについて、製品モデルと価格に影響する主要スペックを解析し、
価格比較に適格かどうか判定してください。

入力：
{items_text}

以下のJSON形式のみで返してください。全ての入力商品IDを必ず含めてください。

{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名",
          "model": "完全な基本モデル名（容量を含まない）",
          "variant": "Pro/Pro Max/Plus/Ultraなどのバリエーション（ない場合は空文字）",
          "storage": "256GB/1TBなどの容量（該当しない場合は空文字）",
          "confidence": 0.95,
          "evidence": "タイトル内の根拠"
        }}
      ],
      "listingType": "MAIN_PRODUCT",
      "hasAllCriticalParameters": true,
      "missingCriticalParameters": [],
      "criticalParameters": {{}},
      "isAnalysisEligible": true,
      "exclusionReason": ""
    }}
  ]
}}

listingType（商品タイプ）:
- MAIN_PRODUCT: 製品本体
- ACCESSORY: ケース、充電器、ケーブルなどのアクセサリ
- PARTS: 部品
- BROKEN: ジャンク品、故障品
- BOX_ONLY: 箱のみ
- BUNDLE: 単品価格を特定できないセット販売
- UNKNOWN: 商品種別を確定できない

重要ルール：

1. 商品カテゴリごとに、市場価格に大きく影響する必須スペックを判断してください。

2. 例：
   - スマートフォン：正確なシリーズ、Pro/Pro Max/Plusなどのバリエーション、ストレージ容量
   - ノートPC：シリーズと世代、CPU、メモリ、ストレージ容量
   - カメラ：正確な本体型番、ボディのみかレンズキットか
   - ゲーム機：世代、通常版/Slim/Pro、ストレージ容量

3. 必須スペックがタイトルに明記されていない場合：
   - hasAllCriticalParameters = false
   - isAnalysisEligible = false
   - missingCriticalParameters に不足項目を列挙
   - exclusionReason に理由を記録

4. タイトルに明記されていない情報を推測してはいけません。

5. 画像、一般知識、他の商品、出品者情報から値を補完してはいけません。

6. model は完全な製品バージョンを含めてください。
   例：「iPhone 15 Pro」「iPhone 15 Pro Max」
   「iPhone 15」だけにはしないでください。

7. storage は必ず別フィールドとして抽出してください。
   例：256GB、1TB

8. variant にはPro/Pro Max/Plus/Ultra等を入れてください。
   modelフィールドに既に含まれる場合でもvariantにも入れてください。

9. アクセサリ、部品、ジャンク品、箱のみ、セット販売は
   isAnalysisEligible = false にしてください。

10. pricingModelKeyは出力しないでください。プログラムが生成します。

11. 必ず有効なJSONのみを返してください。説明文は一切不要です。
"""


def save_active_models(item_id: str, parsed: Dict) -> str:
    """保存活跃商品型号解析结果"""
    models = parsed.get("models", [])
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    has_all_critical = parse_bool(parsed.get("hasAllCriticalParameters", False))
    is_analysis_eligible = parse_bool(parsed.get("isAnalysisEligible", False))
    missing_parameters = parsed.get("missingCriticalParameters", [])
    critical_parameters = parsed.get("criticalParameters", {})
    exclusion_reason = normalize(parsed.get("exclusionReason", ""))
    
    if not isinstance(models, list):
        models = []
    if not isinstance(missing_parameters, list):
        missing_parameters = []
    if not isinstance(critical_parameters, dict):
        critical_parameters = {}
    
    normalized_models = []
    for model in models:
        if not isinstance(model, dict):
            continue
        brand = normalize(model.get("brand", ""))
        model_name = normalize(model.get("model", ""))
        variant = normalize(model.get("variant", ""))
        storage = normalize_storage(model.get("storage", ""))
        confidence = safe_decimal(model.get("confidence", 0))
        evidence = normalize(model.get("evidence", ""))
        
        if not brand or not model_name:
            continue
        
        pricing_model_key = generate_pricing_model_key(
            brand=brand,
            model_name=model_name,
            storage=storage,
            variant=variant
        )
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "variant": variant,
            "storage": storage,
            "pricingModelKey": pricing_model_key,
            "confidence": str(confidence),
            "evidence": evidence
        })
    
    excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
    exclusion_reasons = []
    
    if listing_type in excluded_types:
        exclusion_reasons.append(f"商品类型不适合价格分析: {listing_type}")
    if not has_all_critical:
        if missing_parameters:
            exclusion_reasons.append("标题缺少影响价格的关键参数: " + ", ".join(str(x) for x in missing_parameters))
        else:
            exclusion_reasons.append("标题缺少影响价格的关键参数")
    if not is_analysis_eligible:
        exclusion_reasons.append(exclusion_reason or "AI判定不适合价格分析")
    
    if not normalized_models:
        status = "REVIEW_REQUIRED"
    elif exclusion_reasons:
        status = "EXCLUDED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in normalized_models):
        status = "REVIEW_REQUIRED"
    else:
        status = "COMPLETED"
    
    final_exclusion_reason = "; ".join(dict.fromkeys(exclusion_reasons))
    now = datetime.now(timezone.utc).isoformat()
    
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                listingType = :listing_type,
                hasAllCriticalParameters = :has_all_critical,
                missingCriticalParameters = :missing_parameters,
                criticalParameters = :critical_parameters,
                isAnalysisEligible = :is_analysis_eligible,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now,
                workflowStatus = :workflow,
                pricingStatus = :pricing_status
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":has_all_critical": has_all_critical,
            ":missing_parameters": missing_parameters,
            ":critical_parameters": to_dynamodb_value(critical_parameters),
            ":is_analysis_eligible": (status == "COMPLETED"),
            ":exclusion_reason": final_exclusion_reason,
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
    """标记活跃商品型号解析失败"""
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


# ==================== 第三步：closed 搜索一次 ====================

def scrape_and_save_closed_once(
    keyword: str,
    count: int = 100,
    force_reprocess: bool = False
) -> List[str]:
    """closed 使用用户原始 keyword 搜索一次"""
    logger.info(f"closed 单次搜索: keyword='{keyword}', count={count}")
    
    try:
        items = scrape_auctions(keyword, "closed", False)
        items = items[:count]
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
                logger.error(f"保存 closed 商品失败 {item.get('itemId')}: {exc}")
        
        logger.info(f"closed 单次搜索完成，保存 {len(saved_ids)} 条")
        return saved_ids
        
    except Exception as exc:
        logger.error(f"closed 搜索失败: {exc}", exc_info=True)
        return []


def upsert_closed_item_once(
    item: Dict,
    search_keyword: str,
    force_reprocess: bool = False
):
    """保存单次搜索到的闭拍商品"""
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


# ==================== 第四步：closed AI 型号解析 ====================

def get_closed_items_by_ids(
    item_ids: List[str],
    only_pending: bool = True
) -> List[Dict]:
    """通过 ID 列表获取本次搜索到的 closed 商品"""
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
            logger.error(f"获取 closed 商品 {item_id} 失败: {e}")
    return items


def batch_parse_closed_models(items: List[Dict]) -> Dict:
    """批量解析本次搜索到的 closed 商品"""
    if not items:
        return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    batch_size = CLOSED_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        
        logger.info(f"closed 型号解析批次 {batch_number}: {len(batch)} 个商品")
        
        items_data = [
            {
                "itemId": str(item["itemID"]),
                "title": item.get("title", ""),
                "price": safe_int(item.get("price", 0)),
                "itemCondition": item.get("itemCondition", "")
            }
            for item in batch
        ]
        
        prompt = build_closed_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        
        if not result:
            logger.error(f"closed 批次 {batch_number} AI 返回空结果")
            for item in batch:
                mark_closed_parse_failed(str(item["itemID"]), "AI_RESPONSE_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"closed 批次{batch_number}（{len(batch)}个商品）AI返回空结果")
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
            
            saved_status = save_closed_models(item_id=item_id, parsed=parsed)
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
            totals["errors"].append(f"closed 批次{batch_number}: AI未返回{len(missing_ids)}个商品")
        
        if start + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    logger.info(
        f"closed 型号解析完成: 成功={totals['parsed']}, "
        f"排除={totals['excluded']}, 需审核={totals['review_required']}, "
        f"失败={totals['failed']}"
    )
    return totals


def build_closed_model_parsing_prompt(items: List[Dict]) -> str:
    """构建 closed 商品型号解析 Prompt"""
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは中古電子製品の商品識別と価格サンプル適格性判定の専門家です。

以下のYahooオークション落札商品のタイトルについて、製品モデルと価格に影響する主要スペックを解析し、
同型商品の価格サンプルとして適格かどうか判定してください。

商品リスト：
{items_text}

以下のJSON形式のみで返してください。全ての入力商品IDを必ず含めてください。

{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名",
          "model": "完全な基本モデル名",
          "variant": "Pro/Pro Max/Plus/Ultraなどのバリエーション（ない場合は空文字）",
          "storage": "256GB/1TBなどの容量（該当しない場合は空文字）",
          "confidence": 0.95,
          "evidence": "タイトル内の根拠"
        }}
      ],
      "listingType": "MAIN_PRODUCT",
      "condition": "USED",
      "hasAllCriticalParameters": true,
      "missingCriticalParameters": [],
      "criticalParameters": {{}},
      "isComparable": true,
      "exclusionReason": ""
    }}
  ]
}}

listingType（商品タイプ）:
- MAIN_PRODUCT: 製品本体
- ACCESSORY: ケース、充電器、ケーブルなどのアクセサリ
- PARTS: 部品
- BROKEN: ジャンク品、故障品
- BOX_ONLY: 箱のみ
- BUNDLE: 単品価格を特定できないセット販売
- UNKNOWN: 商品種別を確定できない

condition（商品状態）:
- NEW: 新品、未使用品
- USED: 通常の中古品
- BROKEN: ジャンク品、故障品
- UNKNOWN: タイトルから状態を判断できない

厳格なルール：

1. 商品カテゴリごとに、市場価格に大きく影響する必須スペックを判断してください。

2. 例：
   - スマートフォン：正確なシリーズ、Pro/Pro Max/Plusなどのバリエーション、ストレージ容量
   - ノートPC：シリーズと世代、CPU、メモリ、ストレージ容量
   - カメラ：正確な本体型番、ボディのみかレンズキットか
   - ゲーム機：世代、通常版/Slim/Pro、ストレージ容量

3. 必須スペックがタイトルに一つでも明記されていない場合：
   - hasAllCriticalParameters = false
   - isComparable = false
   - missingCriticalParameters に不足項目を列挙
   - exclusionReason に理由を記録

4. タイトルに明記されていない情報を推測してはいけません。

5. 画像、一般知識、他の商品、出品者情報から値を補完してはいけません。

6. アクセサリ、部品、ジャンク品、箱のみ、セット販売は
   isComparable = false にしてください。

7. model は完全な製品バージョンを含めてください。

8. storage は必ず別フィールドとして抽出してください。

9. variant にはPro/Pro Max/Plus/Ultra等を入れてください。

10. pricingModelKeyは出力しないでください。プログラムが生成します。

11. 必ず有効なJSONのみを返してください。説明文は一切不要です。
"""


def save_closed_models(item_id: str, parsed: Dict) -> str:
    """保存 closed 商品型号解析结果"""
    models = parsed.get("models", [])
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    condition = normalize(parsed.get("condition", "UNKNOWN")).upper()
    has_all_critical = parse_bool(parsed.get("hasAllCriticalParameters", False))
    ai_is_comparable = parse_bool(parsed.get("isComparable", False))
    missing_parameters = parsed.get("missingCriticalParameters", [])
    critical_parameters = parsed.get("criticalParameters", {})
    exclusion_reason = normalize(parsed.get("exclusionReason", ""))
    
    if not isinstance(models, list):
        models = []
    if not isinstance(missing_parameters, list):
        missing_parameters = []
    if not isinstance(critical_parameters, dict):
        critical_parameters = {}
    
    normalized_models = []
    for model in models:
        if not isinstance(model, dict):
            continue
        brand = normalize(model.get("brand", ""))
        model_name = normalize(model.get("model", ""))
        variant = normalize(model.get("variant", ""))
        storage = normalize_storage(model.get("storage", ""))
        confidence = safe_decimal(model.get("confidence", 0))
        evidence = normalize(model.get("evidence", ""))
        
        if not brand or not model_name:
            continue
        
        pricing_model_key = generate_pricing_model_key(
            brand=brand,
            model_name=model_name,
            storage=storage,
            variant=variant
        )
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "variant": variant,
            "storage": storage,
            "pricingModelKey": pricing_model_key,
            "confidence": str(confidence),
            "evidence": evidence
        })
    
    excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
    exclusion_reasons = []
    
    if listing_type in excluded_types:
        exclusion_reasons.append(f"商品类型不适合作为价格样本: {listing_type}")
    if condition == "BROKEN":
        exclusion_reasons.append("商品状态为故障品")
    if not has_all_critical:
        if missing_parameters:
            exclusion_reasons.append("标题缺少影响价格的关键参数: " + ", ".join(str(x) for x in missing_parameters))
        else:
            exclusion_reasons.append("标题缺少影响价格的关键参数")
    if not ai_is_comparable:
        exclusion_reasons.append(exclusion_reason or "AI判定不能作为价格样本")
    
    if not normalized_models:
        status = "REVIEW_REQUIRED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in normalized_models):
        status = "REVIEW_REQUIRED"
    elif exclusion_reasons:
        status = "EXCLUDED"
    else:
        status = "COMPLETED"
    
    final_is_comparable = (
        status == "COMPLETED"
        and ai_is_comparable
        and has_all_critical
        and listing_type == "MAIN_PRODUCT"
        and condition != "BROKEN"
    )
    
    final_exclusion_reason = "; ".join(dict.fromkeys(reason for reason in exclusion_reasons if reason))
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
                missingCriticalParameters = :missing_parameters,
                criticalParameters = :critical_parameters,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_comparable": final_is_comparable,
            ":condition": condition,
            ":has_all_critical": has_all_critical,
            ":missing_parameters": missing_parameters,
            ":critical_parameters": to_dynamodb_value(critical_parameters),
            ":exclusion_reason": final_exclusion_reason,
            ":now": now
        }
    )
    
    return status


def mark_closed_parse_failed(item_id: str, error: str):
    """标记闭拍商品型号解析失败"""
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


# ==================== 第五步：程序估价和购买建议 ====================

def get_unpriced_items_for_ids(
    item_ids: List[str],
    require_model_completed: bool = True,
    include_completed: bool = False,
    limit: int = 100
) -> List[Dict]:
    """获取待估价的活跃商品"""
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
            logger.error(f"获取待估价商品 {item_id} 失败: {e}")
    return items


def build_closed_comparable_index(closed_item_ids: Set[str]) -> Dict[str, List[Dict]]:
    """读取本次 closed 搜索结果，按 pricingModelKey 建立索引"""
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
            logger.error(f"读取 closed 商品 {item_id} 失败: {e}")
    
    for model_key, items in comparable_index.items():
        items.sort(key=lambda value: value.get("endTime", ""), reverse=True)
        logger.info(f"closed 索引: {model_key} 共有 {len(items)} 个可比商品")
    
    return comparable_index


def get_comparable_closed_items(
    active_item: Dict,
    comparable_index: Dict[str, List[Dict]]
) -> List[Dict]:
    """根据 active 商品的 pricingModelKey 从本次 closed 索引中取得同规格商品"""
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
    """计算 closed 成交价格统计，使用 IQR 方法排除极端异常值"""
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
            "insufficientReason": f"可比数据不足，需要至少{MIN_COMPARABLE_COUNT}个样本，当前只有{count}个",
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
            "insufficientReason": f"排除异常价格后，可比数据不足：需要至少{MIN_COMPARABLE_COUNT}个，当前只有{filtered_count}个",
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
    """根据可比样本数量、价格离散程度和异常值比例，由程序生成定价置信度"""
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
    """将卖家评分转换为百分数"""
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
    """完全由程序判断风险等级和风险因素"""
    risk_score = 0
    risk_factors = []
    reasons = []
    
    comparable_count = safe_int(stats.get("filtered_count", 0))
    spread_ratio = safe_decimal(stats.get("price_spread_ratio", 0))
    
    if comparable_count < 5:
        risk_score += 2
        risk_factors.append(f"有效可比样本较少，仅{comparable_count}个")
    elif comparable_count < 10:
        risk_score += 1
        risk_factors.append(f"有效可比样本数量一般，共{comparable_count}个")
    else:
        reasons.append(f"有效可比样本数量较充足，共{comparable_count}个")
    
    if pricing_confidence < Decimal("0.50"):
        risk_score += 3
        risk_factors.append("价格统计置信度较低")
    elif pricing_confidence < Decimal("0.75"):
        risk_score += 1
        risk_factors.append("价格统计置信度一般")
    else:
        reasons.append(f"价格统计置信度为{pricing_confidence}")
    
    if spread_ratio >= Decimal("0.50"):
        risk_score += 2
        risk_factors.append("同型号成交价格分布非常分散")
    elif spread_ratio >= Decimal("0.30"):
        risk_score += 1
        risk_factors.append("同型号成交价格存在一定波动")
    
    seller_rating = parse_seller_rating(active_item.get("sellerRating"))
    if seller_rating is None:
        risk_score += 1
        risk_factors.append("卖家评分无法确认")
    elif seller_rating < Decimal("95"):
        risk_score += 2
        risk_factors.append(f"卖家评分较低：{seller_rating}%")
    elif seller_rating < Decimal("98"):
        risk_score += 1
        risk_factors.append(f"卖家评分一般：{seller_rating}%")
    else:
        reasons.append(f"卖家评分较高：{seller_rating}%")
    
    seller_type = str(active_item.get("sellerType", "personal")).lower()
    if seller_type == "personal":
        risk_score += 1
        risk_factors.append("商品由个人卖家出售")
    elif seller_type == "store":
        reasons.append("商品由店铺卖家出售")
    
    shipping_status = active_item.get("shippingStatus", "UNKNOWN")
    if shipping_status == "UNKNOWN":
        risk_score += 1
        risk_factors.append("运费无法确认，实际成本可能增加")
    elif shipping_status == "FREE":
        reasons.append("商品为包邮")
    
    active_condition = normalize(active_item.get("itemCondition", ""))
    if not active_condition:
        risk_score += 1
        risk_factors.append("商品状态字段未明确")
    
    if profit_margin < Decimal("0"):
        risk_score += 3
        risk_factors.append("按当前价格购买预计产生亏损")
    elif profit_margin < REVIEW_MARGIN_THRESHOLD:
        risk_score += 2
        risk_factors.append("预计利润率低于审核阈值")
    elif profit_margin < BUY_MARGIN_THRESHOLD:
        risk_score += 1
        risk_factors.append("预计利润率未达到推荐购买阈值")
    else:
        reasons.append("预计利润率达到推荐购买阈值")
    
    if has_buynow_price:
        reasons.append("已同时计算即决价格下的收益")
    
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
    """程序生成购买建议"""
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
    """生成不依赖 AI 的购买建议原因"""
    reasons = []
    comparable_count = safe_int(stats.get("filtered_count", 0))
    
    reasons.append(f"价格判断基于{comparable_count}个同规格有效成交样本")
    reasons.append(f"同规格成交价中位数约为{int(estimated_price)}日元")
    
    if purchase_price > estimated_price:
        reasons.append(f"当前价格比市场中位价高{int(purchase_price - estimated_price)}日元")
    elif purchase_price < estimated_price:
        reasons.append(f"当前价格比市场中位价低{int(estimated_price - purchase_price)}日元")
    else:
        reasons.append("当前价格与市场中位价相同")
    
    if net_profit > 0:
        reasons.append(f"扣除手续费、运费和风险准备金后，预计净利润为{int(net_profit)}日元")
    else:
        reasons.append(f"扣除手续费、运费和风险准备金后，预计亏损{abs(int(net_profit))}日元")
    
    margin_percent = (profit_margin * Decimal("100")).quantize(Decimal("0.1"), ROUND_HALF_UP)
    reasons.append(f"预计销售利润率为{margin_percent}%")
    
    decision_text = {
        "BUY_CANDIDATE": "程序判断利润空间达到购买候选标准",
        "REVIEW": "程序判断需要人工确认商品状态和最终成交价格",
        "AVOID": "程序判断当前价格不具备合理利润空间",
        "INSUFFICIENT_DATA": "可比数据不足，无法生成可靠购买建议"
    }
    
    reasons.append(decision_text.get(decision_signal, "程序无法生成明确建议"))
    return reasons


def get_effective_shipping_cost(item: Dict) -> Decimal:
    """决定采购运费"""
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
    """完全由程序生成价格、风险和购买建议"""
    if not stats.get("is_sufficient"):
        comparable_ids = [str(item_id) for item_id in stats.get("comparableItemIds", [])]
        return to_dynamodb_value({
            "pricingStatus": "INSUFFICIENT_DATA",
            "pricingConfidence": Decimal("0.20"),
            "riskLevel": "HIGH",
            "riskScore": 10,
            "decisionSignal": "INSUFFICIENT_DATA",
            "reasons": [stats.get("insufficientReason", "可比数据不足")],
            "riskFactors": ["有效成交样本不足，无法可靠估价"],
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
    """对所有 active 商品执行程序化价格分析"""
    totals = {"attempted": 0, "completed": 0, "insufficient_data": 0, "failed": 0}
    
    if not items:
        return totals
    
    comparable_index = build_closed_comparable_index({
        str(item_id) for item_id in allowed_closed_item_ids
    })
    
    logger.info(f"closed 可比索引包含 {len(comparable_index)} 个 pricingModelKey")
    
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
            logger.error(f"程序估价失败 {item_id}: {exc}", exc_info=True)
            mark_pricing_failed(item_id, str(exc))
            totals["failed"] += 1
    
    return totals


def save_pricing_result(item_id: str, pricing_result: Dict):
    """保存程序化分析结果"""
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
    """标记估价失败"""
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


# ==================== AI 调用 ====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
    """带重试的 AI 调用"""
    for attempt in range(AI_MAX_RETRIES):
        try:
            check_limits()
            remaining = get_remaining_seconds()
            if remaining < AI_REQUEST_TIMEOUT + 10:
                raise RuntimeError(f"剩余时间不足: 剩余{remaining:.1f}秒")
            
            result, finish_reason = call_ai(prompt)
            
            if result is not None:
                return result
            
            if finish_reason == "length":
                logger.error("AI 输出达到 max_tokens 限制，批次过大，不重试")
                return None
            
            logger.warning(f"AI 返回空结果 (finish_reason={finish_reason})，重试 {attempt + 1}/{AI_MAX_RETRIES}")
            
        except RuntimeError as e:
            error_msg = str(e)
            if "Token用量已达上限" in error_msg or "Lambda超时倒计时" in error_msg or "剩余时间不足" in error_msg:
                raise
            logger.error(f"AI 调用异常 (尝试 {attempt + 1}): {e}")
        except Exception as e:
            logger.error(f"AI 调用异常 (尝试 {attempt + 1}): {e}")
        
        if attempt < AI_MAX_RETRIES - 1:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    logger.error(f"AI 调用失败，已重试 {AI_MAX_RETRIES} 次")
    return None


def call_ai(prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    """调用 AI API"""
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
    """解析 AI 返回的 JSON"""
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
    logger.error(f"无法解析 AI 响应: {content[:500]}")
    return None
