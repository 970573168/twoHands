"""
Yahoo Auction 商品分析工作流 Lambda (关键参数验证版)
主要功能：
1. AI 解析型号时同时识别影响价格的关键参数
2. 缺少关键参数的商品标记为 EXCLUDED，不进入后续分析
3. 闭拍商品同样执行关键参数验证和型号匹配
4. 搜索词包含完整关键参数
5. 多层保护确保只有完整、匹配的商品进入价格分析
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
from boto3.dynamodb.conditions import Key, Attr

from yahoo_auction_scraper import (
    scrape_auctions,
    parse_end_time
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============ 环境变量 ============
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
AI_API_URL = os.getenv("AI_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "doubao-seed-2-0-mini-260428")
AI_API_KEY = os.getenv("AI_API_KEY", "")
MAX_CLOSED_PER_MODEL = int(os.getenv("MAX_CLOSED_PER_MODEL", "50"))
DEFAULT_SEARCH_COUNT = int(os.getenv("DEFAULT_SEARCH_COUNT", "3"))
MAX_ACTIVE_ITEMS = int(os.getenv("MAX_ACTIVE_ITEMS", "20"))
AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "60"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "3"))
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "1.0"))
INCLUDE_PAYPAY = os.getenv("INCLUDE_PAYPAY", "false").lower() == "true"
SECRET_NAME = os.getenv("SECRET_NAME", "yahoo-auction-ai-api-key")

MAX_TOTAL_TOKENS = int(os.getenv("MAX_TOTAL_TOKENS", "50000"))
LAMBDA_TIMEOUT_SECONDS = int(os.getenv("LAMBDA_TIMEOUT_SECONDS", "840"))
LAMBDA_TIMEOUT_BUFFER = int(os.getenv("LAMBDA_TIMEOUT_BUFFER", "30"))

MODEL_PARSE_BATCH_SIZE = int(os.getenv("MODEL_PARSE_BATCH_SIZE", "10"))
CLOSED_PARSE_BATCH_SIZE = int(os.getenv("CLOSED_PARSE_BATCH_SIZE", "15"))

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
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache
    if AI_API_KEY:
        _api_key_cache = AI_API_KEY
        logger.info("使用环境变量中的 API Key")
        return _api_key_cache
    try:
        logger.info(f"从 Secrets Manager 获取密钥: {SECRET_NAME}")
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
        logger.info("成功从 Secrets Manager 获取 API Key")
        return _api_key_cache
    except Exception as e:
        logger.error(f"从 Secrets Manager 获取密钥失败: {e}")
        raise RuntimeError(f"无法获取 API 密钥: {e}")


# ==================== Token 和超时控制 ====================

def get_elapsed_seconds():
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    remaining = get_remaining_seconds()
    if remaining <= 0:
        raise RuntimeError(
            f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒, "
            f"超时限制{LAMBDA_TIMEOUT_SECONDS}秒, 缓冲{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_token_limit():
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}，中断执行"
        )


def check_limits():
    check_token_limit()
    check_timeout()


def update_token_usage(usage):
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        logger.info(
            f"Token用量更新: +{total}, 总计={_total_tokens_used}/{MAX_TOTAL_TOKENS}, "
            f"剩余={MAX_TOTAL_TOKENS - _total_tokens_used}"
        )


# ==================== 工具函数 ====================

def to_decimal(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    elif isinstance(value, dict):
        return {k: to_decimal(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_decimal(v) for v in value]
    elif isinstance(value, int):
        return Decimal(str(value))
    elif isinstance(value, str):
        try:
            return Decimal(value)
        except:
            return value
    return value


def normalize(value: str) -> str:
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


def normalize_model_key(brand: str, model: str) -> str:
    combined = f"{brand} {model}"
    normalized = normalize(combined).upper()
    normalized = re.sub(r"[^A-Z0-9\s+\-/]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except:
        return default


def determine_shipping_status(shipping_text: str) -> Dict:
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


def build_closed_search_keyword(model_info: Dict) -> str:
    """构建包含完整关键参数的搜索关键词"""
    parts = [
        normalize(model_info.get("brand", "")),
        normalize(model_info.get("model", "")),
        normalize(model_info.get("storage", ""))
    ]
    return " ".join(x for x in parts if x)


def response(status_code: int, body: Dict) -> Dict:
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    global _total_tokens_used, _lambda_start_time
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    
    try:
        keyword = normalize(event.get("keyword", ""))
        if not keyword:
            return response(400, {"error": "keyword 不能为空"})
        
        try:
            count = int(event.get("count", DEFAULT_SEARCH_COUNT))
        except (ValueError, TypeError):
            return response(400, {
                "error": "count 必须是有效整数",
                "received": str(event.get("count"))
            })
        
        force_reprocess = parse_bool(event.get("force_reprocess", False))
        count = max(1, min(count, MAX_ACTIVE_ITEMS))
        
        logger.info(
            f"开始商品分析工作流: keyword='{keyword}', "
            f"count={count}, force_reprocess={force_reprocess}"
        )
        
        try:
            api_key = get_api_key()
            logger.info("API Key 验证成功")
        except Exception as e:
            logger.warning(f"API Key 获取失败: {e}，仅执行抓取")
            api_key = None
        
        result = execute_workflow(keyword, count, force_reprocess)
        
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


def execute_workflow(keyword: str, count: int, force_reprocess: bool) -> Dict:
    start_time = time.time()
    workflow_result = {
        "keyword": keyword,
        "active_scraped": 0,
        "active_parsed": 0,
        "active_excluded": 0,
        "active_parse_failed": 0,
        "active_review_required": 0,
        "models_found": 0,
        "closed_scraped": 0,
        "closed_parsed": 0,
        "pricing_attempted": 0,
        "pricing_completed": 0,
        "pricing_insufficient_data": 0,
        "pricing_failed": 0,
        "errors": []
    }
    
    try:
        check_limits()
        
        # ========== 第一步 ==========
        logger.info(f"第一步：搜索活跃商品: {keyword}, count={count}")
        active_item_ids = scrape_and_save_active(keyword, count)
        workflow_result["active_scraped"] = len(active_item_ids)
        
        if not active_item_ids:
            logger.info("未找到活跃商品，工作流结束")
            workflow_result["status"] = "COMPLETED"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return workflow_result
        
        try:
            api_key = get_api_key()
            if not api_key:
                logger.info("API Key 未配置，跳过 AI 相关步骤")
                workflow_result["status"] = "SCRAPED_ONLY"
                workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
                return workflow_result
        except:
            logger.info("API Key 获取失败，跳过 AI 相关步骤")
            workflow_result["status"] = "SCRAPED_ONLY"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return workflow_result
        
        # ========== 第二步 ==========
        items_to_parse = get_active_items_by_ids(
            active_item_ids, 
            only_pending=(not force_reprocess)
        )
        
        if items_to_parse:
            check_limits()
            logger.info(f"第二步：批量解析型号和关键参数 ({len(items_to_parse)} 个商品)")
            parse_result = batch_parse_models(items_to_parse)
            workflow_result["active_parsed"] = parse_result["parsed"]
            workflow_result["active_excluded"] = parse_result.get("excluded", 0)
            workflow_result["active_parse_failed"] = parse_result["failed"]
            workflow_result["active_review_required"] = parse_result["review_required"]
            workflow_result["models_found"] = parse_result["models_found"]
            if parse_result["errors"]:
                workflow_result["errors"].extend(parse_result["errors"])
        
        # ========== 第三步 ==========
        all_processed_items = get_all_active_items_by_ids(active_item_ids)
        unique_models = get_unique_models(all_processed_items)
        
        if unique_models:
            check_limits()
            logger.info(f"第三步：搜索闭拍商品 ({len(unique_models)} 个型号)")
            for i, (model_key, model_info) in enumerate(unique_models.items()):
                check_limits()
                logger.info(f"  搜索型号 [{i+1}/{len(unique_models)}]: {model_info['brand']} {model_info['model']} {model_info.get('storage', '')}")
                
                model_keyword = build_closed_search_keyword(model_info)
                closed_items = search_closed_for_model(
                    model_keyword, 
                    model_info,
                    MAX_CLOSED_PER_MODEL
                )
                workflow_result["closed_scraped"] += len(closed_items)
                if i < len(unique_models) - 1:
                    time.sleep(REQUEST_INTERVAL)
        else:
            logger.info("第三步：未找到符合分析条件的型号，跳过闭拍搜索")
        
        # ========== 第四步 ==========
        unparsed_closed = get_unparsed_closed_items(limit=100)
        
        if unparsed_closed:
            check_limits()
            logger.info(f"第四步：清洗闭拍商品型号和关键参数 ({len(unparsed_closed)} 个商品)")
            parsed_count = batch_parse_closed_models(unparsed_closed)
            workflow_result["closed_parsed"] = parsed_count
        else:
            logger.info("第四步：没有需要清洗的闭拍商品")
        
        # ========== 第五步 ==========
        unpriced_items = get_unpriced_items_for_ids(
            active_item_ids,
            require_model_completed=True
        )
        
        if unpriced_items:
            check_limits()
            logger.info(f"第五步：估价分析 ({len(unpriced_items)} 个商品)")
            pricing_result = batch_price_analysis(unpriced_items)
            workflow_result["pricing_attempted"] = pricing_result["attempted"]
            workflow_result["pricing_completed"] = pricing_result["completed"]
            workflow_result["pricing_insufficient_data"] = pricing_result["insufficient_data"]
            workflow_result["pricing_failed"] = pricing_result["failed"]
        else:
            logger.info("第五步：没有需要估价的商品")
        
        elapsed = time.time() - start_time
        workflow_result["elapsed_seconds"] = round(elapsed, 1)
        
        if workflow_result["active_scraped"] == 0:
            workflow_result["status"] = "NO_RESULTS"
        elif workflow_result["active_parsed"] == 0 and workflow_result["active_parse_failed"] > 0:
            workflow_result["status"] = "PARTIAL_FAILED"
            if not workflow_result["errors"]:
                workflow_result["errors"].append("所有活跃商品型号解析失败")
        elif workflow_result["pricing_completed"] > 0:
            workflow_result["status"] = "COMPLETED"
        elif workflow_result["pricing_insufficient_data"] == workflow_result["pricing_attempted"] and workflow_result["pricing_attempted"] > 0:
            workflow_result["status"] = "PARTIAL_COMPLETED"
            workflow_result["errors"].append(
                f"型号解析完成，但{workflow_result['pricing_insufficient_data']}个商品因闭拍数据不足无法估价"
            )
        elif workflow_result["active_parsed"] > 0:
            workflow_result["status"] = "PARTIAL_COMPLETED"
        else:
            workflow_result["status"] = "COMPLETED"
        
        logger.info(f"工作流完成: {json.dumps(workflow_result, ensure_ascii=False, default=str)}")
        return workflow_result
        
    except RuntimeError as e:
        error_msg = str(e)
        if "Token用量已达上限" in error_msg or "Lambda超时倒计时" in error_msg or "剩余时间不足" in error_msg:
            logger.warning(f"工作流安全中断: {error_msg}")
            workflow_result["status"] = "INTERRUPTED"
            workflow_result["interrupt_reason"] = error_msg
            workflow_result["total_tokens_used"] = _total_tokens_used
            workflow_result["elapsed_seconds"] = time.time() - start_time
            return workflow_result
        raise
    except Exception as e:
        logger.error(f"工作流出错: {e}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(e))
        workflow_result["elapsed_seconds"] = time.time() - start_time
        return workflow_result


# ==================== 第一步：搜索活跃商品 ====================

def scrape_and_save_active(keyword: str, count: int) -> List[str]:
    logger.info(f"开始抓取活跃商品: keyword='{keyword}', count={count}")
    try:
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        if len(items) > count:
            logger.warning(
                f"抓取器返回 {len(items)} 个商品，超过请求的 {count} 个，"
                f"将只处理前 {count} 个"
            )
            items = items[:count]
        saved_ids = []
        for item in items:
            try:
                upsert_active_item(item, keyword)
                saved_ids.append(item["itemId"])
            except Exception as e:
                logger.error(f"保存活跃商品失败 {item.get('itemId')}: {e}")
        logger.info(f"成功抓取并保存 {len(saved_ids)} 个活跃商品")
        return saved_ids
    except Exception as e:
        logger.error(f"抓取活跃商品失败: {e}")
        return []


def upsert_active_item(item: Dict, keyword: str):
    now = datetime.now(timezone.utc)
    buynow_price = item.get("buynowPrice")
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    seller_type = item.get("sellerType", "personal")
    item_condition = item.get("itemCondition")
    
    update_expr = """
        SET itemType = :item_type,
            title = :title,
            price = :price,
            bidCount = :bid_count,
            endTime = :end_time,
            sellerId = :seller_id,
            sellerRating = :seller_rating,
            sellerType = :seller_type,
            prefecture = :prefecture,
            #url = :url,
            thumbnailUrl = :thumbnail,
            searchKeyword = :keyword,
            lastScrapedAt = :now,
            isFreeShipping = :is_free_shipping,
            shippingStatus = :shipping_status,
            modelStatus = if_not_exists(modelStatus, :model_pending),
            pricingStatus = if_not_exists(pricingStatus, :pricing_pending),
            workflowStatus = :scraped,
            #ttl = :ttl
    """
    
    expr_values = {
        ":item_type": item.get("itemType", "auction"),
        ":title": item.get("title", ""),
        ":price": item.get("price", 0),
        ":bid_count": item.get("bidCount", 0),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": item.get("sellerId") or "unknown",
        ":seller_rating": item.get("sellerRating") or "unknown",
        ":seller_type": seller_type,
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""),
        ":thumbnail": item.get("thumbnailUrl", ""),
        ":keyword": keyword,
        ":now": now.isoformat(),
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":model_pending": "PENDING",
        ":pricing_pending": "PENDING",
        ":scraped": "ACTIVE_SCRAPED",
        ":ttl": int((now + timedelta(days=30)).timestamp())
    }
    
    if buynow_price is not None:
        update_expr += ", buynowPrice = :buynow_price"
        expr_values[":buynow_price"] = buynow_price
    if shipping_text:
        update_expr += ", shippingText = :shipping_text"
        expr_values[":shipping_text"] = shipping_text
    if item_condition is not None:
        update_expr += ", itemCondition = :item_condition"
        expr_values[":item_condition"] = item_condition
    
    active_table.update_item(
        Key={"itemID": item["itemId"]},
        UpdateExpression=update_expr,
        ExpressionAttributeNames={
            "#url": "url",
            "#ttl": "ttl"
        },
        ExpressionAttributeValues=expr_values
    )


# ==================== 第二步：型号解析（含关键参数验证）====================

def get_active_items_by_ids(item_ids: List[str], only_pending: bool = True) -> List[Dict]:
    items = []
    for item_id in item_ids:
        try:
            response = active_table.get_item(Key={"itemID": item_id})
            item = response.get("Item")
            if item:
                if not only_pending or item.get("modelStatus") == "PENDING":
                    items.append(item)
        except Exception as e:
            logger.error(f"获取商品 {item_id} 失败: {e}")
    return items


def get_all_active_items_by_ids(item_ids: List[str]) -> List[Dict]:
    items = []
    for item_id in item_ids:
        try:
            response = active_table.get_item(Key={"itemID": item_id})
            item = response.get("Item")
            if item:
                items.append(item)
        except Exception as e:
            logger.error(f"获取商品 {item_id} 失败: {e}")
    return items


def batch_parse_models(items: List[Dict]) -> Dict:
    if not items:
        return {"parsed": 0, "excluded": 0, "review_required": 0, "models_found": 0, "failed": 0, "errors": []}
    
    batch_size = MODEL_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "models_found": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        batch = items[start:start + batch_size]
        check_limits()
        logger.info(f"解析批次 {start//batch_size + 1}: {len(batch)} 个商品")
        
        items_data = [{"itemId": item["itemID"], "title": item.get("title", "")} for item in batch]
        
        prompt = build_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        
        if not result:
            logger.error(f"批次 {start//batch_size + 1} AI 返回空结果")
            for item in batch:
                mark_active_model_failed(item["itemID"], "AI_RESPONSE_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"批次{start//batch_size + 1}({len(batch)}个商品) AI返回空结果")
            continue
        
        parsed_items = result.get("items", [])
        returned_ids = set()
        
        for parsed in parsed_items:
            item_id = parsed.get("itemId")
            
            if not item_id:
                continue
            
            returned_ids.add(item_id)
            saved_status = save_active_models(item_id, parsed)
            
            if saved_status == "COMPLETED":
                totals["parsed"] += 1
                totals["models_found"] += len(parsed.get("models", []))
            elif saved_status == "EXCLUDED":
                totals["excluded"] += 1
            elif saved_status == "REVIEW_REQUIRED":
                totals["review_required"] += 1
        
        input_ids = {item["itemID"] for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_active_model_failed(missing_id, "AI_NOT_RETURNED")
            totals["failed"] += 1
        if missing_ids:
            totals["errors"].append(f"批次{start//batch_size + 1}: AI未返回{len(missing_ids)}个商品")
        
        if start + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    logger.info(
        f"型号解析完成: 成功={totals['parsed']}, "
        f"排除={totals['excluded']}, "
        f"需审核={totals['review_required']}, "
        f"失败={totals['failed']}"
    )
    return totals


def build_model_parsing_prompt(items: List[Dict]) -> str:
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは中古電子製品の商品識別と価格比較適格性判定の専門家です。

以下のYahooオークションの商品タイトルについて、具体的な製品モデルを解析し、
価格に大きな影響を与える必須パラメータがタイトルに明記されているか判定してください。

商品リスト：
{items_text}

以下のJSON形式のみで返してください。
全ての商品IDを必ず含めてください。

{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名",
          "model": "容量などを含まない基本モデル名",
          "storage": "256GBなど。該当しない場合は空文字",
          "normalizedModel": "価格比較用の完全な正規化モデル",
          "confidence": 0.95,
          "evidence": "タイトル内の根拠"
        }}
      ],
      "listingType": "MAIN_PRODUCT",
      "isAccessory": false,
      "hasAllCriticalParameters": true,
      "missingCriticalParameters": [],
      "criticalParameters": {{
        "パラメータ名": {{
          "value": "タイトルから取得した値",
          "evidence": "タイトル内の根拠"
        }}
      }},
      "isAnalysisEligible": true,
      "exclusionReason": ""
    }}
  ]
}}

listingType:
- MAIN_PRODUCT: 製品本体
- ACCESSORY: ケース、充電器、ケーブル、保護フィルム等
- PARTS: 部品
- BROKEN: ジャンク、故障品
- BOX_ONLY: 箱のみ
- BUNDLE: 比較困難な複数商品セット
- UNKNOWN: 商品種類を確定できない

重要ルール：

1. 商品カテゴリごとに、市場価格へ大きな影響を与える必須パラメータを判断してください。

2. 例：
   - スマートフォン：正確なシリーズ、Pro/Pro Max/Plus等のバリエーション、ストレージ容量
   - ノートPC：正確なシリーズと世代、CPU、メモリ、ストレージ容量
   - カメラ：正確な本体型番、ボディのみかレンズキットか
   - ゲーム機：世代、通常版/Slim/Pro、ストレージ容量

3. 必須パラメータがタイトルに一つでも明記されていない場合：
   - hasAllCriticalParameters = false
   - isAnalysisEligible = false
   - missingCriticalParameters に不足項目を入れる
   - exclusionReason に理由を入れる

4. タイトルに明記されていない情報を推測してはいけません。

5. 画像、一般知識、他の商品、出品者情報から値を補完してはいけません。

6. 型番から仕様が一意に確定できる場合でも、タイトル内に型番が明記されている場合に限り、
   evidence にその型番を記録してください。不確実な型番対応は推測しないでください。

7. アクセサリ、部品、箱のみ、ジャンク、比較困難なセット商品は：
   - isAnalysisEligible = false

8. normalizedModel は価格が異なる仕様を区別できる形式にしてください。
   例：
   - APPLE IPHONE 15 PRO 256GB
   - APPLE IPHONE 15 PRO MAX 256GB
   - LENOVO THINKPAD X1 CARBON GEN 11 I7 16GB 512GB

9. 色は通常、必須パラメータにしないでください。
   ただし限定版など市場価格へ大きな影響を与える場合は必須にできます。

10. 必ず有効なJSONのみを返してください。
"""


def save_active_models(item_id: str, parsed: Dict) -> str:
    """保存活跃商品型号（含关键参数验证）"""
    models = parsed.get("models", [])
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    is_accessory = parse_bool(parsed.get("isAccessory", False))
    has_all_critical = parse_bool(parsed.get("hasAllCriticalParameters", False))
    is_analysis_eligible = parse_bool(parsed.get("isAnalysisEligible", False))
    missing_parameters = parsed.get("missingCriticalParameters", [])
    critical_parameters = parsed.get("criticalParameters", {})
    exclusion_reason = normalize(parsed.get("exclusionReason", ""))
    
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
        storage = normalize(model.get("storage", ""))
        ai_normalized_model = normalize(model.get("normalizedModel", "")).upper()
        
        if not brand or not model_name:
            continue
        
        if ai_normalized_model:
            normalized_key = ai_normalized_model
        else:
            key_parts = [brand, model_name]
            if storage:
                key_parts.append(storage)
            normalized_key = normalize_model_key(key_parts[0], " ".join(key_parts[1:]))
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "storage": storage,
            "normalizedModel": normalized_key,
            "confidence": str(model.get("confidence", 0)),
            "evidence": normalize(model.get("evidence", ""))
        })
    
    excluded_listing_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
    exclusion_reasons = []
    
    if listing_type in excluded_listing_types:
        exclusion_reasons.append(f"商品类型不适合价格分析: {listing_type}")
    if is_accessory:
        exclusion_reasons.append("商品是配件")
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
        Key={"itemID": item_id},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                listingType = :listing_type,
                isAccessory = :is_accessory,
                hasAllCriticalParameters = :has_all_critical,
                missingCriticalParameters = :missing_parameters,
                criticalParameters = :critical_parameters,
                isAnalysisEligible = :is_analysis_eligible,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now,
                workflowStatus = :workflow
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_accessory": is_accessory,
            ":has_all_critical": has_all_critical,
            ":missing_parameters": missing_parameters,
            ":critical_parameters": to_decimal(critical_parameters),
            ":is_analysis_eligible": (status == "COMPLETED"),
            ":exclusion_reason": final_exclusion_reason,
            ":now": now,
            ":workflow": (
                "MODEL_PARSED" if status == "COMPLETED"
                else "MODEL_EXCLUDED" if status == "EXCLUDED"
                else "MODEL_REVIEW_REQUIRED"
            )
        }
    )
    
    return status


def mark_active_model_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET modelStatus = :status,
                modelError = :error,
                modelParsedAt = :now,
                modelRetryCount = if_not_exists(modelRetryCount, :zero) + :one
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error,
            ":now": now,
            ":zero": 0,
            ":one": 1
        }
    )


def get_unique_models(active_items: List[Dict]) -> Dict[str, Dict]:
    """获取唯一定型号列表（只返回 COMPLETED + isAnalysisEligible + hasAllCriticalParameters）"""
    unique = {}
    for item in active_items:
        if item.get("modelStatus") != "COMPLETED":
            continue
        if item.get("isAnalysisEligible") is not True:
            continue
        if item.get("hasAllCriticalParameters") is not True:
            continue
        
        models = item.get("models", [])
        if isinstance(models, str):
            try:
                models = json.loads(models)
            except json.JSONDecodeError:
                continue
        if not isinstance(models, list):
            continue
        
        for model in models:
            if not isinstance(model, dict):
                continue
            key = model.get("normalizedModel")
            if key and key not in unique:
                unique[key] = {
                    "brand": model.get("brand", ""),
                    "model": model.get("model", ""),
                    "storage": model.get("storage", ""),
                    "normalizedModel": key
                }
    return unique


# ==================== 第三步：搜索闭拍商品 ====================

def search_closed_for_model(keyword: str, model_info: Dict, max_items: int) -> List[Dict]:
    logger.info(f"  搜索闭拍商品: {keyword}")
    try:
        items = scrape_auctions(keyword, "closed", False)
        items = items[:max_items]
        logger.info(f"  找到 {len(items)} 个闭拍商品")
        saved_items = []
        for item in items:
            try:
                upsert_closed_item(item, model_info)
                saved_items.append(item)
            except Exception as e:
                logger.error(f"  保存闭拍商品失败 {item.get('itemId')}: {e}")
        return saved_items
    except Exception as e:
        logger.error(f"  搜索闭拍商品失败: {e}")
        return []


def upsert_closed_item(item: Dict, model_info: Dict):
    now = datetime.now(timezone.utc)
    model_key = model_info.get("normalizedModel", "")
    buynow_price = item.get("buynowPrice")
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    seller_type = item.get("sellerType", "personal")
    item_condition = item.get("itemCondition")
    
    update_expr = """
        SET itemType = :item_type,
            title = :title,
            price = :price,
            bidCount = :bid_count,
            endTime = :end_time,
            sellerId = :seller_id,
            sellerRating = :seller_rating,
            sellerType = :seller_type,
            prefecture = :prefecture,
            #url = :url,
            thumbnailUrl = :thumbnail,
            sourceModel = :source_model,
            isFreeShipping = :is_free_shipping,
            shippingStatus = :shipping_status,
            modelStatus = if_not_exists(modelStatus, :pending),
            lastScrapedAt = :now,
            #ttl = :ttl
        ADD searchModelKeys :model_key_set
    """
    
    expr_values = {
        ":item_type": item.get("itemType", "auction"),
        ":title": item.get("title", ""),
        ":price": item.get("price", 0),
        ":bid_count": item.get("bidCount", 0),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": item.get("sellerId") or "unknown",
        ":seller_rating": item.get("sellerRating") or "unknown",
        ":seller_type": seller_type,
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""),
        ":thumbnail": item.get("thumbnailUrl", ""),
        ":source_model": model_info,
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":pending": "PENDING",
        ":now": now.isoformat(),
        ":ttl": int((now + timedelta(days=180)).timestamp()),
        ":model_key_set": {model_key} if model_key else set()
    }
    
    if buynow_price is not None:
        update_expr += ", buynowPrice = :buynow_price"
        expr_values[":buynow_price"] = buynow_price
    if shipping_text:
        update_expr += ", shippingText = :shipping_text"
        expr_values[":shipping_text"] = shipping_text
    if item_condition is not None:
        update_expr += ", itemCondition = :item_condition"
        expr_values[":item_condition"] = item_condition
    
    closed_table.update_item(
        Key={"itemID": item["itemId"]},
        UpdateExpression=update_expr,
        ExpressionAttributeNames={
            "#url": "url",
            "#ttl": "ttl"
        },
        ExpressionAttributeValues=expr_values
    )


# ==================== 第四步：AI 清洗闭拍型号（含关键参数验证和型号匹配）====================

def get_unparsed_closed_items(limit: int = 100) -> List[Dict]:
    all_items = []
    last_key = None
    while len(all_items) < limit:
        params = {
            "FilterExpression": Attr("modelStatus").eq("PENDING"),
            "Limit": min(limit - len(all_items), 100)
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        response = closed_table.scan(**params)
        all_items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return all_items[:limit]


def batch_parse_closed_models(items: List[Dict]) -> int:
    if not items:
        return 0
    batch_size = CLOSED_PARSE_BATCH_SIZE
    total_parsed = 0
    for i in range(0, len(items), batch_size):
        check_limits()
        batch = items[i:i + batch_size]
        items_data = [
            {
                "itemId": item["itemID"],
                "title": item.get("title", ""),
                "price": safe_int(item.get("price", 0)),
                "sourceModel": item.get("sourceModel", {}),
                "itemCondition": item.get("itemCondition", ""),
                "sellerType": item.get("sellerType", "personal")
            }
            for item in batch
        ]
        prompt = build_closed_model_parsing_prompt(items_data)
        result = call_ai_with_retry(prompt)
        if not result:
            continue
        
        parsed_items = result.get("items", [])
        returned_ids = set()
        for parsed in parsed_items:
            item_id = parsed.get("itemId")
            if not item_id:
                continue
            returned_ids.add(item_id)
            
            models = parsed.get("models", [])
            listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
            is_comparable = parse_bool(parsed.get("isComparable", False))
            condition = parsed.get("condition", "UNKNOWN")
            exclusion_reason = normalize(parsed.get("exclusionReason", ""))
            has_all_critical = parse_bool(parsed.get("hasAllCriticalParameters", False))
            missing_parameters = parsed.get("missingCriticalParameters", [])
            critical_parameters = parsed.get("criticalParameters", {})
            matches_source_model = parse_bool(parsed.get("matchesSourceModel", False))
            
            if not isinstance(missing_parameters, list):
                missing_parameters = []
            if not isinstance(critical_parameters, dict):
                critical_parameters = {}
            
            excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
            effective_comparable = (
                bool(models)
                and listing_type not in excluded_types
                and is_comparable
                and has_all_critical
                and matches_source_model
            )
            
            save_closed_models(
                item_id=item_id,
                models=models,
                listing_type=listing_type,
                is_comparable=effective_comparable,
                condition=condition,
                exclusion_reason=exclusion_reason,
                has_all_critical=has_all_critical,
                missing_parameters=missing_parameters,
                critical_parameters=critical_parameters,
                matches_source_model=matches_source_model
            )
            total_parsed += 1
        
        input_ids = {item["itemID"] for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_closed_parse_failed(missing_id, "AI_NOT_RETURNED")
        
        if i + batch_size < len(items):
            time.sleep(REQUEST_INTERVAL)
    
    return total_parsed


def build_closed_model_parsing_prompt(items: List[Dict]) -> str:
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは中古電子製品の商品識別と価格比較適格性判定の専門家です。

以下のYahooオークション落札商品のタイトルを解析し、
検索対象モデルと価格比較可能か判定してください。

商品リスト：
{items_text}

以下のJSON形式のみで返してください。

{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名",
          "model": "基本モデル名",
          "storage": "256GBなど。該当しない場合は空文字",
          "normalizedModel": "価格比較用の完全な正規化モデル",
          "confidence": 0.95,
          "evidence": "タイトル内の根拠"
        }}
      ],
      "listingType": "MAIN_PRODUCT",
      "condition": "USED",
      "hasAllCriticalParameters": true,
      "missingCriticalParameters": [],
      "criticalParameters": {{
        "パラメータ名": {{
          "value": "タイトルから取得した値",
          "evidence": "タイトル内の根拠"
        }}
      }},
      "matchesSourceModel": true,
      "isComparable": true,
      "exclusionReason": ""
    }}
  ]
}}

listingType:
- MAIN_PRODUCT
- ACCESSORY
- PARTS
- BROKEN
- BOX_ONLY
- BUNDLE
- UNKNOWN

condition:
- NEW
- USED
- BROKEN
- UNKNOWN

重要ルール：

1. 商品カテゴリごとに、市場価格へ大きな影響を与える必須パラメータを判断してください。

2. 必須パラメータがタイトルに一つでも明記されていない場合：
   - hasAllCriticalParameters = false
   - isComparable = false
   - missingCriticalParameters に不足項目を記録
   - exclusionReason に理由を記録

3. タイトルに明記されていない情報を推測してはいけません。

4. sourceModel とタイトルから解析したモデルを比較してください。

5. 基本モデル、バリエーション、容量など、
   価格へ大きな影響を与える仕様が sourceModel と異なる場合：
   - matchesSourceModel = false
   - isComparable = false

6. アクセサリ、部品、ジャンク、箱のみ、比較困難なセット商品は
   isComparable = false にしてください。

7. normalizedModel は容量など価格差を生む仕様を含めてください。

8. 例：
   - APPLE IPHONE 15 PRO 128GB
   - APPLE IPHONE 15 PRO 256GB
   - APPLE IPHONE 15 PRO MAX 256GB

9. 全ての入力商品IDを必ず含めてください。

10. 必ず有効なJSONのみを返してください。
"""


def save_closed_models(
    item_id: str,
    models: List[Dict],
    listing_type: str,
    is_comparable: bool,
    condition: str = "UNKNOWN",
    exclusion_reason: str = "",
    has_all_critical: bool = False,
    missing_parameters: Optional[List[str]] = None,
    critical_parameters: Optional[Dict] = None,
    matches_source_model: bool = False
):
    """保存闭拍商品型号（含关键参数验证和型号匹配）"""
    missing_parameters = missing_parameters or []
    critical_parameters = critical_parameters or {}
    
    normalized_models = []
    for model in models:
        if not isinstance(model, dict):
            continue
        
        brand = normalize(model.get("brand", ""))
        model_name = normalize(model.get("model", ""))
        storage = normalize(model.get("storage", ""))
        ai_normalized = normalize(model.get("normalizedModel", "")).upper()
        
        if not brand or not model_name:
            continue
        
        if ai_normalized:
            normalized_key = ai_normalized
        else:
            full_model = " ".join(x for x in [model_name, storage] if x)
            normalized_key = normalize_model_key(brand, full_model)
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "storage": storage,
            "normalizedModel": normalized_key,
            "confidence": str(model.get("confidence", 0)),
            "evidence": normalize(model.get("evidence", ""))
        })
    
    if not normalized_models:
        status = "REVIEW_REQUIRED"
    elif not has_all_critical:
        status = "EXCLUDED"
    elif not matches_source_model:
        status = "EXCLUDED"
    elif not is_comparable:
        status = "EXCLUDED"
    elif any(safe_decimal(m.get("confidence", 0)) < Decimal("0.7") for m in normalized_models):
        status = "REVIEW_REQUIRED"
    else:
        status = "COMPLETED"
    
    now = datetime.now(timezone.utc).isoformat()
    
    closed_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                listingType = :listing_type,
                isComparable = :is_comparable,
                parsedCondition = :condition_val,
                hasAllCriticalParameters = :has_all_critical,
                missingCriticalParameters = :missing_parameters,
                criticalParameters = :critical_parameters,
                matchesSourceModel = :matches_source_model,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_comparable": (status == "COMPLETED" and is_comparable),
            ":condition_val": condition,
            ":has_all_critical": has_all_critical,
            ":missing_parameters": missing_parameters,
            ":critical_parameters": to_decimal(critical_parameters),
            ":matches_source_model": matches_source_model,
            ":exclusion_reason": normalize(exclusion_reason),
            ":now": now
        }
    )


def mark_closed_parse_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    closed_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET modelStatus = :status,
                modelError = :error,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error,
            ":now": now
        }
    )


# ==================== 第五步：估价分析 ====================

def get_unpriced_items_for_ids(
    item_ids: List[str], 
    require_model_completed: bool = True,
    limit: int = 50
) -> List[Dict]:
    """获取未定价的活跃商品（多重保护）"""
    items = []
    for item_id in item_ids:
        try:
            response = active_table.get_item(Key={"itemID": item_id})
            item = response.get("Item")
            if not item:
                continue
            
            if item.get("pricingStatus") != "PENDING":
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
            if not models:
                continue
            
            items.append(item)
            if len(items) >= limit:
                break
        except Exception as e:
            logger.error(f"获取商品 {item_id} 失败: {e}")
    return items


def batch_price_analysis(items: List[Dict]) -> Dict:
    if not items:
        return {"attempted": 0, "completed": 0, "insufficient_data": 0, "failed": 0}
    
    totals = {"attempted": 0, "completed": 0, "insufficient_data": 0, "failed": 0}
    
    for item in items:
        try:
            check_limits()
            totals["attempted"] += 1
            
            comparable_items = get_comparable_closed_items(item)
            stats = calculate_price_statistics(comparable_items)
            
            if stats["is_sufficient"]:
                ai_analysis = ai_price_analysis(item, comparable_items, stats)
            else:
                ai_analysis = {}
            
            purchase_price = safe_decimal(item.get("price", 0))
            shipping_status = item.get("shippingStatus", "UNKNOWN")
            is_free_shipping = item.get("isFreeShipping", False)
            
            if is_free_shipping and shipping_status == "FREE":
                actual_shipping = Decimal("0")
            else:
                shipping_fee = item.get("shippingFee")
                if shipping_fee is not None:
                    actual_shipping = safe_decimal(shipping_fee, DEFAULT_SHIPPING_COST)
                else:
                    actual_shipping = DEFAULT_SHIPPING_COST
            
            buynow_price = safe_decimal(item.get("buynowPrice")) if item.get("buynowPrice") else None
            
            pricing_result = merge_pricing_result(
                stats, ai_analysis, purchase_price, 
                actual_shipping, buynow_price
            )
            save_pricing_result(item["itemID"], pricing_result)
            
            if pricing_result.get("pricingStatus") == "COMPLETED":
                totals["completed"] += 1
            elif pricing_result.get("pricingStatus") == "INSUFFICIENT_DATA":
                totals["insufficient_data"] += 1
            else:
                totals["completed"] += 1
            
            time.sleep(REQUEST_INTERVAL)
            
        except RuntimeError as e:
            error_msg = str(e)
            if "Token用量已达上限" in error_msg or "Lambda超时倒计时" in error_msg:
                logger.warning(f"估价分析中断: {error_msg}")
                break
            raise
        except Exception as e:
            logger.error(f"估价失败 {item.get('itemID')}: {e}")
            mark_pricing_failed(item["itemID"], str(e))
            totals["failed"] += 1
    
    return totals


def get_comparable_closed_items(active_item: Dict) -> List[Dict]:
    """获取可比闭拍商品（多重保护：只返回完全匹配的 COMPLETED 商品）"""
    models = active_item.get("models", [])
    if isinstance(models, str):
        try:
            models = json.loads(models)
        except json.JSONDecodeError:
            return []
    if not isinstance(models, list):
        return []
    
    comparable = []
    seen_ids = set()
    
    for model in models:
        if not isinstance(model, dict):
            continue
        model_key = model.get("normalizedModel")
        if not model_key:
            continue
        
        try:
            response = closed_table.scan(
                FilterExpression=(
                    Attr("modelStatus").eq("COMPLETED") &
                    Attr("isComparable").eq(True) &
                    Attr("hasAllCriticalParameters").eq(True) &
                    Attr("matchesSourceModel").eq(True) &
                    Attr("price").gt(0)
                ),
                Limit=200
            )
            
            for closed_item in response.get("Items", []):
                if closed_item["itemID"] in seen_ids:
                    continue
                
                item_models = closed_item.get("models", [])
                if isinstance(item_models, str):
                    try:
                        item_models = json.loads(item_models)
                    except json.JSONDecodeError:
                        continue
                if not isinstance(item_models, list):
                    continue
                
                for item_model in item_models:
                    if isinstance(item_model, dict) and item_model.get("normalizedModel") == model_key:
                        comparable.append(closed_item)
                        seen_ids.add(closed_item["itemID"])
                        break
        except Exception as e:
            logger.error(f"查询闭拍商品失败: {e}")
    
    comparable.sort(key=lambda x: x.get("endTime", ""), reverse=True)
    return comparable


def calculate_price_statistics(comparable_items: List[Dict]) -> Dict:
    prices = []
    for item in comparable_items:
        try:
            price = safe_decimal(item.get("price", 0))
            if price > 0:
                prices.append(price)
        except:
            continue
    prices.sort()
    n = len(prices)
    
    if n < MIN_COMPARABLE_COUNT:
        return {"count": n, "is_sufficient": False, "prices": [int(p) for p in prices]}
    
    def percentile(data: List[Decimal], p: float) -> Decimal:
        k = (len(data) - 1) * p
        f = int(k)
        c = k - f
        if f + 1 < len(data):
            return data[f] + (data[f + 1] - data[f]) * Decimal(str(c))
        return data[f]
    
    q1 = percentile(prices, 0.25)
    median = percentile(prices, 0.50)
    q3 = percentile(prices, 0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - MAX_PRICE_DEVIATION * iqr
    upper_bound = q3 + MAX_PRICE_DEVIATION * iqr
    filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
    
    return {
        "count": n,
        "filtered_count": len(filtered_prices),
        "is_sufficient": len(filtered_prices) >= MIN_COMPARABLE_COUNT,
        "min": int(min(prices)),
        "max": int(max(prices)),
        "q1": int(q1),
        "median": int(median),
        "q3": int(q3),
        "iqr": int(iqr),
        "filtered_min": int(min(filtered_prices)) if filtered_prices else None,
        "filtered_max": int(max(filtered_prices)) if filtered_prices else None,
        "filtered_median": int(sorted(filtered_prices)[len(filtered_prices)//2]) if filtered_prices else None,
        "prices": [int(p) for p in prices],
        "filtered_prices": [int(p) for p in filtered_prices]
    }


def ai_price_analysis(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> Dict:
    max_comparables = 20
    selected_comparables = comparable_items[:max_comparables]
    prompt = build_pricing_prompt(active_item, selected_comparables, stats)
    result = call_ai_with_retry(prompt)
    return result or {}


def build_pricing_prompt(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> str:
    active_data = {
        "itemId": active_item["itemID"],
        "title": active_item.get("title", ""),
        "currentBid": safe_int(active_item.get("price", 0)),
        "buynowPrice": safe_int(active_item.get("buynowPrice")) if active_item.get("buynowPrice") else None,
        "bidCount": safe_int(active_item.get("bidCount", 0)),
        "sellerRating": active_item.get("sellerRating", ""),
        "sellerType": active_item.get("sellerType", "personal"),
        "itemCondition": active_item.get("itemCondition", ""),
        "shippingStatus": active_item.get("shippingStatus", "UNKNOWN"),
        "isFreeShipping": active_item.get("isFreeShipping", False),
        "prefecture": active_item.get("prefecture", ""),
        "models": active_item.get("models", [])
    }
    
    comparables_data = [
        {
            "itemId": item["itemID"],
            "title": item.get("title", ""),
            "price": safe_int(item.get("price", 0)),
            "bidCount": safe_int(item.get("bidCount", 0)),
            "endTime": item.get("endTime", ""),
            "listingType": item.get("listingType", ""),
            "condition": item.get("parsedCondition", "UNKNOWN"),
            "sellerRating": item.get("sellerRating", ""),
            "sellerType": item.get("sellerType", "personal"),
            "shippingStatus": item.get("shippingStatus", "UNKNOWN"),
            "itemCondition": item.get("itemCondition", "")
        }
        for item in comparable_items[:20]
    ]
    
    return f"""
あなたは中古電子製品の価格分析の専門家です。以下の情報を基に、商品のリスク評価を行ってください。

【分析対象商品】
{json.dumps(active_data, ensure_ascii=False, indent=2)}

【落札相場データ】
{json.dumps(comparables_data, ensure_ascii=False, indent=2)}

【統計データ】
{json.dumps(stats, ensure_ascii=False, indent=2)}

以下のJSON形式で返してください（金額計算は不要です）：
{{
  "pricingConfidence": 0.8,
  "riskLevel": "LOW",
  "decisionSignal": "REVIEW",
  "reasons": ["理由1", "理由2"],
  "riskFactors": ["リスク要因1", "リスク要因2"],
  "conditionAdjustment": "NONE",
  "usableComparableItemIds": ["ID1", "ID2"]
}}

riskLevel: LOW/MEDIUM/HIGH
decisionSignal: BUY_CANDIDATE/REVIEW/AVOID/INSUFFICIENT_DATA
conditionAdjustment: NONE/NEEDS_CHECK/MAJOR_DIFFERENCE

分析ルール：
1. 商品状態の違いを評価（新品/中古/ジャンク）
2. 出品者タイプ（個人/ストア）と評価を考慮
3. 送料の有無を考慮
4. 即決価格がある場合はその妥当性も評価
5. 必ず有効なJSON形式のみを返してください
"""


def merge_pricing_result(
    stats: Dict, 
    ai_analysis: Dict, 
    purchase_price: Decimal,
    actual_shipping: Decimal = Decimal("0"),
    buynow_price: Optional[Decimal] = None
) -> Dict:
    if not stats.get("is_sufficient"):
        return to_decimal({
            "pricingStatus": "INSUFFICIENT_DATA",
            "pricingConfidence": 0.2,
            "reasons": ["可比数据不足（需要至少3个可比样本）"],
            "comparableCount": stats.get("count", 0)
        })
    
    estimated_price = Decimal(str(stats["filtered_median"]))
    estimated_low = Decimal(str(stats["filtered_min"]))
    estimated_high = Decimal(str(stats["filtered_max"]))
    
    platform_fee = (estimated_price * EXPECTED_SELLING_FEE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    repair_reserve = (estimated_price * DEFAULT_REPAIR_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    risk_reserve = (estimated_price * RISK_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    
    total_costs = platform_fee + actual_shipping + repair_reserve + risk_reserve
    
    net_profit_at_bid = estimated_price - purchase_price - total_costs
    profit_margin_at_bid = (net_profit_at_bid / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP) if estimated_price > 0 else Decimal("0")
    
    net_profit_buynow = None
    profit_margin_buynow = None
    if buynow_price and buynow_price > 0:
        net_profit_buynow = estimated_price - buynow_price - total_costs
        profit_margin_buynow = (net_profit_buynow / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP) if estimated_price > 0 else Decimal("0")
    
    target_margin_20 = Decimal("0.20")
    target_margin_10 = Decimal("0.10")
    
    break_even_price = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE)
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_20 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - target_margin_20)
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_10 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - target_margin_10)
        - actual_shipping
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    risk_level = ai_analysis.get("riskLevel", "MEDIUM")
    pricing_confidence = Decimal(str(ai_analysis.get("pricingConfidence", 0.7)))
    
    if buynow_price and net_profit_buynow and net_profit_buynow > 0 and profit_margin_buynow >= Decimal("0.15"):
        decision = "BUY_CANDIDATE"
    elif net_profit_at_bid <= 0:
        decision = "AVOID"
    elif risk_level == "HIGH" or pricing_confidence < Decimal("0.5"):
        decision = "REVIEW"
    elif profit_margin_at_bid >= Decimal("0.20") and pricing_confidence >= Decimal("0.75") and risk_level == "LOW":
        decision = "BUY_CANDIDATE"
    else:
        decision = "REVIEW"
    
    result = {
        "pricingStatus": "COMPLETED",
        "estimatedMarketPrice": int(estimated_price),
        "estimatedLow": int(estimated_low),
        "estimatedHigh": int(estimated_high),
        "currentBidPrice": int(purchase_price),
        "breakEvenPurchasePrice": int(break_even_price),
        "targetPurchasePrice20Margin": int(target_price_20),
        "targetPurchasePrice10Margin": int(target_price_10),
        "netProfitAtCurrentBid": int(net_profit_at_bid),
        "profitMarginAtCurrentBid": float(profit_margin_at_bid),
        "pricingConfidence": float(pricing_confidence),
        "riskLevel": risk_level,
        "decisionSignal": decision,
        "reasons": ai_analysis.get("reasons", []),
        "riskFactors": ai_analysis.get("riskFactors", []),
        "conditionAdjustment": ai_analysis.get("conditionAdjustment", "NONE"),
        "comparableItemIds": ai_analysis.get("usableComparableItemIds", []),
        "comparableCount": stats.get("filtered_count", 0),
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
    
    if buynow_price and buynow_price > 0:
        result["buynowPrice"] = int(buynow_price)
        result["netProfitAtBuynow"] = int(net_profit_buynow) if net_profit_buynow else None
        result["profitMarginAtBuynow"] = float(profit_margin_buynow) if profit_margin_buynow else None
    
    return to_decimal(result)


def save_pricing_result(item_id: str, pricing_result: Dict):
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET pricingResult = :result,
                pricingStatus = :status,
                pricedAt = :now,
                workflowStatus = :workflow
        """,
        ExpressionAttributeValues={
            ":result": pricing_result,
            ":status": pricing_result.get("pricingStatus", "FAILED"),
            ":now": now,
            ":workflow": "PRICING_COMPLETED"
        }
    )


def mark_pricing_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET pricingStatus = :status,
                pricingError = :error,
                pricedAt = :now
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error[:500],
            ":now": now
        }
    )


# ==================== AI 调用 ====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
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
                logger.warning(f"AI调用中断: {error_msg}")
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
    try:
        api_key = get_api_key()
    except Exception as e:
        logger.error(f"获取 API Key 失败: {e}")
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
        "temperature": 0.3,
        "max_tokens": 4000,
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
                
                if finish_reason == "length":
                    logger.warning("AI 响应被截断: finish_reason=length")
                elif finish_reason == "stop":
                    logger.debug("AI 响应正常完成: finish_reason=stop")
                else:
                    logger.warning(f"AI 响应完成原因: finish_reason={finish_reason}")
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
        logger.error(f"AI API 调用失败: {e}")
        raise


def parse_ai_json(content: str) -> Optional[Dict]:
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
