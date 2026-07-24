"""
Yahoo Auction 商品分析工作流 Lambda
功能：
1. 搜索活跃商品并解析型号
2. 搜索对应闭拍商品
3. AI 清洗闭拍商品型号
4. AI 估价和利润分析

依赖新版抓取器 (支持运费、即决价格、卖家类型、商品状态等字段)
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
from typing import List, Dict, Optional, Any

import boto3
from boto3.dynamodb.conditions import Key, Attr

# 导入现有的抓取函数
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

# 新增：Secrets Manager 配置
SECRET_NAME = os.getenv("SECRET_NAME", "")
USE_SECRETS_MANAGER = os.getenv("USE_SECRETS_MANAGER", "false").lower() == "true"

# 新增：Token 和超时控制配置
MAX_TOTAL_TOKENS = int(os.getenv("MAX_TOTAL_TOKENS", "100000"))
LAMBDA_TIMEOUT_SECONDS = int(os.getenv("LAMBDA_TIMEOUT_SECONDS", "840"))
LAMBDA_TIMEOUT_BUFFER = int(os.getenv("LAMBDA_TIMEOUT_BUFFER", "30"))

# 估价配置 - 使用 Decimal 避免浮点数问题
EXPECTED_SELLING_FEE_RATE = Decimal(os.getenv("EXPECTED_SELLING_FEE_RATE", "0.10"))
DEFAULT_SHIPPING_COST = Decimal(os.getenv("DEFAULT_SHIPPING_COST", "1500"))
DEFAULT_REPAIR_RESERVE_RATE = Decimal(os.getenv("DEFAULT_REPAIR_RESERVE_RATE", "0.05"))
MIN_COMPARABLE_COUNT = int(os.getenv("MIN_COMPARABLE_COUNT", "3"))
MAX_PRICE_DEVIATION = Decimal(os.getenv("MAX_PRICE_DEVIATION", "1.5"))
RISK_RESERVE_RATE = Decimal(os.getenv("RISK_RESERVE_RATE", "0.03"))

# 重试配置
RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

dynamodb = boto3.resource("dynamodb")
active_table = dynamodb.Table(TABLE_NAME_ACTIVE)
closed_table = dynamodb.Table(TABLE_NAME_CLOSED)

# 初始化 Secrets Manager 客户端
secretsmanager = boto3.client("secretsmanager") if USE_SECRETS_MANAGER else None

# 全局变量
_api_key_cache = None
_total_tokens_used = 0
_lambda_start_time = None


# ==================== 密钥管理函数 ====================

def get_api_key():
    """获取 API 密钥（支持 Secrets Manager）"""
    global _api_key_cache
    
    # 如果已缓存，直接返回
    if _api_key_cache:
        return _api_key_cache
    
    # 优先使用环境变量中的 API Key
    if AI_API_KEY:
        _api_key_cache = AI_API_KEY
        logger.info("使用环境变量中的 API Key")
        return _api_key_cache
    
    # 使用 Secrets Manager
    if USE_SECRETS_MANAGER and SECRET_NAME:
        try:
            logger.info(f"从 Secrets Manager 获取密钥: {SECRET_NAME}")
            response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
            secret_string = response.get("SecretString")
            
            if not secret_string:
                raise RuntimeError("Secret 中没有 SecretString 值")
            
            # 尝试解析 JSON 格式的 Secret
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
                # 如果不是 JSON，直接使用字符串
                _api_key_cache = secret_string
            
            logger.info("成功从 Secrets Manager 获取 API Key")
            return _api_key_cache
            
        except Exception as e:
            logger.error(f"从 Secrets Manager 获取密钥失败: {e}")
            raise RuntimeError(f"无法获取 API 密钥: {e}")
    
    raise RuntimeError("未配置 API 密钥（请设置 AI_API_KEY 或启用 USE_SECRETS_MANAGER 并配置 SECRET_NAME）")


# ==================== Token 和超时控制函数 ====================

def get_elapsed_seconds():
    """获取从 Lambda 开始到现在的运行时间（秒）"""
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    """获取 Lambda 剩余可用时间（秒）"""
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    """检查是否接近 Lambda 超时"""
    remaining = get_remaining_seconds()
    if remaining <= 0:
        raise RuntimeError(
            f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒, "
            f"超时限制{LAMBDA_TIMEOUT_SECONDS}秒, 缓冲{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_token_limit():
    """检查 Token 是否超过限制"""
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}，中断执行"
        )


def check_limits():
    """检查所有限制条件（Token + 超时）"""
    check_token_limit()
    check_timeout()


def update_token_usage(usage):
    """更新全局 Token 用量"""
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
    """递归转换浮点数为 Decimal，确保 DynamoDB 兼容"""
    if isinstance(value, float):
        return Decimal(str(value))
    elif isinstance(value, dict):
        return {k: to_decimal(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_decimal(v) for v in value]
    elif isinstance(value, int):
        return Decimal(str(value))
    elif isinstance(value, str):
        # 尝试转换数字字符串
        try:
            return Decimal(value)
        except:
            return value
    return value


def normalize(value: str) -> str:
    """标准化文本"""
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
    """生成标准化型号键，保留重要的特殊字符"""
    combined = f"{brand} {model}"
    normalized = normalize(combined).upper()
    normalized = re.sub(r"[^A-Z0-9\s+\-/]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_bool(value: Any) -> bool:
    """安全转换布尔值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """安全转换为 Decimal"""
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except:
        return default


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    """主入口函数"""
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
            f"count={count}, force_reprocess={force_reprocess}, "
            f"token_limit={MAX_TOTAL_TOKENS}, "
            f"lambda_timeout={LAMBDA_TIMEOUT_SECONDS}s, "
            f"use_secrets_manager={USE_SECRETS_MANAGER}"
        )
        
        # 验证 API Key 可用性
        try:
            api_key = get_api_key()
            logger.info("API Key 验证成功")
        except Exception as e:
            logger.warning(f"API Key 获取失败: {e}，仅执行抓取")
            api_key = None
        
        result = execute_workflow(keyword, count, force_reprocess)
        
        # 添加执行统计信息
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
    """执行完整工作流"""
    start_time = time.time()
    workflow_result = {
        "keyword": keyword,
        "active_scraped": 0,
        "active_parsed": 0,
        "active_review_required": 0,
        "models_found": 0,
        "closed_scraped": 0,
        "closed_parsed": 0,
        "priced_items": 0,
        "errors": []
    }
    
    try:
        # 检查超时和 Token 限制
        check_limits()
        
        # ========== 第一步：搜索并保存活跃商品 ==========
        logger.info(f"第一步：搜索活跃商品: {keyword}")
        active_item_ids = scrape_and_save_active(keyword, count)
        workflow_result["active_scraped"] = len(active_item_ids)
        
        if not active_item_ids:
            logger.info("未找到活跃商品，工作流结束")
            return workflow_result
        
        # 重新从 DynamoDB 读取完整的商品信息
        all_active = get_active_items_by_keyword(keyword)
        
        # 检查 API Key 是否可用
        try:
            api_key = get_api_key()
            if not api_key:
                logger.info("API Key 未配置，跳过 AI 相关步骤")
                return workflow_result
        except:
            logger.info("API Key 获取失败，跳过 AI 相关步骤")
            return workflow_result
        
        # 筛选需要解析型号的商品
        items_to_parse = [
            item for item in all_active
            if force_reprocess or item.get("modelStatus") == "PENDING"
        ]
        
        if items_to_parse:
            # 检查限制条件
            check_limits()
            
            # ========== 第二步：批量解析活跃商品型号 ==========
            logger.info(f"第二步：批量解析型号 ({len(items_to_parse)} 个商品)")
            parse_result = batch_parse_models(items_to_parse)
            workflow_result["active_parsed"] = parse_result["parsed"]
            workflow_result["active_review_required"] = parse_result["review_required"]
            workflow_result["models_found"] = parse_result["models_found"]
        
        # 重新读取以获取最新状态
        all_active = get_active_items_by_keyword(keyword)
        
        # ========== 第三步：搜索闭拍商品 ==========
        unique_models = get_unique_models(all_active)
        
        if unique_models:
            logger.info(f"第三步：搜索闭拍商品 ({len(unique_models)} 个型号)")
            total_closed = 0
            for i, model_info in enumerate(unique_models.values()):
                # 检查限制条件
                check_limits()
                
                if i > 0:
                    time.sleep(REQUEST_INTERVAL)
                
                model_keyword = f'{model_info["brand"]} {model_info["model"]}'
                closed_items = search_closed_for_model(
                    model_keyword, 
                    model_info,
                    MAX_CLOSED_PER_MODEL
                )
                total_closed += len(closed_items)
            workflow_result["closed_scraped"] = total_closed
        
        # ========== 第四步：AI 清洗闭拍商品型号 ==========
        unparsed_closed = get_unparsed_closed_items()
        
        if unparsed_closed:
            # 检查限制条件
            check_limits()
            
            logger.info(f"第四步：清洗闭拍商品型号 ({len(unparsed_closed)} 个商品)")
            parsed_count = batch_parse_closed_models(unparsed_closed)
            workflow_result["closed_parsed"] = parsed_count
        
        # ========== 第五步：估价分析 ==========
        unpriced_items = get_unpriced_active_items()
        
        if unpriced_items:
            # 检查限制条件
            check_limits()
            
            logger.info(f"第五步：估价分析 ({len(unpriced_items)} 个商品)")
            priced_count = batch_price_analysis(unpriced_items)
            workflow_result["priced_items"] = priced_count
        
        elapsed = time.time() - start_time
        workflow_result["elapsed_seconds"] = round(elapsed, 1)
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
        return workflow_result


# ==================== 第一步：搜索活跃商品 ====================

def scrape_and_save_active(keyword: str, count: int) -> List[str]:
    """搜索活跃商品并保存，返回 itemID 列表"""
    original_params = os.environ.get("DEFAULT_PARAMS_ACTIVE", "")
    original_max_pages = os.environ.get("MAX_PAGES", "1")
    original_items_per_page = os.environ.get("ITEMS_PER_PAGE", "50")
    
    # 设置活跃搜索参数
    os.environ["DEFAULT_PARAMS_ACTIVE"] = f"is_postage_mode=1&dest_pref_code=23&n={count}&s1=end&o1=a&mode=3&isdr=0"
    os.environ["MAX_PAGES"] = "1"
    os.environ["ITEMS_PER_PAGE"] = str(count)
    
    try:
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        
        saved_ids = []
        for item in items:
            try:
                upsert_active_item(item, keyword)
                saved_ids.append(item["itemId"])
            except Exception as e:
                logger.error(f"保存活跃商品失败 {item.get('itemId')}: {e}")
        
        return saved_ids
    finally:
        if original_params:
            os.environ["DEFAULT_PARAMS_ACTIVE"] = original_params
        os.environ["MAX_PAGES"] = original_max_pages
        os.environ["ITEMS_PER_PAGE"] = original_items_per_page


def upsert_active_item(item: Dict, keyword: str):
    """更新或插入活跃商品（支持新版抓取器所有字段）"""
    now = datetime.now(timezone.utc)
    
    # 处理可能为 None 的字段
    buynow_price = item.get("buynowPrice")
    shipping_fee = item.get("shippingFee")
    shipping_text = item.get("shippingText", "")
    is_free_shipping = item.get("isFreeShipping", False)
    seller_type = item.get("sellerType", "personal")
    item_condition = item.get("itemCondition")
    
    # 构建更新表达式
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
        ":model_pending": "PENDING",
        ":pricing_pending": "PENDING",
        ":scraped": "ACTIVE_SCRAPED",
        ":ttl": int((now + timedelta(days=30)).timestamp())
    }
    
    # 添加可选字段
    if buynow_price is not None:
        update_expr += ", buynowPrice = :buynow_price"
        expr_values[":buynow_price"] = buynow_price
    
    if shipping_fee is not None:
        update_expr += ", shippingFee = :shipping_fee, shippingText = :shipping_text, isFreeShipping = :is_free_shipping"
        expr_values[":shipping_fee"] = shipping_fee
        expr_values[":shipping_text"] = shipping_text
        expr_values[":is_free_shipping"] = is_free_shipping
    
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


# ==================== 第二步：型号解析 ====================

def get_active_items_by_keyword(keyword: str) -> List[Dict]:
    """获取指定关键词的活跃商品（支持分页）"""
    all_items = []
    last_key = None
    
    while True:
        params = {
            "FilterExpression": Attr("searchKeyword").eq(keyword)
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        
        response = active_table.scan(**params)
        all_items.extend(response.get("Items", []))
        
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    
    return all_items


def batch_parse_models(items: List[Dict]) -> Dict:
    """批量解析活跃商品型号"""
    if not items:
        return {"parsed": 0, "review_required": 0, "models_found": 0}
    
    # 检查限制条件
    check_limits()
    
    items_data = [
        {
            "itemId": item["itemID"],
            "title": item.get("title", ""),
            "price": safe_int(item.get("price", 0)),
            "itemCondition": item.get("itemCondition", ""),
            "sellerType": item.get("sellerType", "personal")
        }
        for item in items
    ]
    
    prompt = build_model_parsing_prompt(items_data)
    result = call_ai_with_retry(prompt)
    
    if not result:
        logger.error("AI 型号解析返回空结果")
        for item in items:
            mark_active_model_failed(item["itemID"], "AI_RESPONSE_EMPTY")
        return {"parsed": 0, "review_required": 0, "models_found": 0, "failed": len(items)}
    
    parsed_items = result.get("items", [])
    parsed_count = 0
    review_count = 0
    models_count = 0
    returned_ids = set()
    
    for parsed in parsed_items:
        item_id = parsed.get("itemId")
        models = parsed.get("models", [])
        
        if item_id:
            returned_ids.add(item_id)
            saved_status = save_active_models(item_id, models)
            if saved_status == "COMPLETED":
                parsed_count += 1
                models_count += len(models)
            elif saved_status == "REVIEW_REQUIRED":
                review_count += 1
    
    input_ids = {item["itemID"] for item in items}
    missing_ids = input_ids - returned_ids
    for missing_id in missing_ids:
        mark_active_model_failed(missing_id, "AI_NOT_RETURNED")
    
    logger.info(
        f"型号解析完成: 成功={parsed_count}, "
        f"需审核={review_count}, 模型数={models_count}, "
        f"AI未返回={len(missing_ids)}"
    )
    
    return {
        "parsed": parsed_count,
        "review_required": review_count,
        "models_found": models_count,
        "missing": len(missing_ids)
    }


def build_model_parsing_prompt(items: List[Dict]) -> str:
    """构建型号解析提示词"""
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは電子製品の専門家です。以下のYahooオークションの商品タイトルから、具体的な製品モデルを特定してください。

商品リスト：
{items_text}

以下のJSON形式で返してください。各商品IDに対して必ず結果を含めてください：
{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名（例：Lenovo, Apple, Sony）",
          "model": "モデル名（例：ThinkPad X1 Carbon Gen 11, iPhone 14 Pro）",
          "confidence": 0.95,
          "evidence": "タイトルからの証拠"
        }}
      ],
      "isAccessory": false
    }}
  ]
}}

ルール：
1. 各商品IDに対して必ずエントリを作成してください
2. 一つの商品に複数のモデルが含まれる可能性があります
3. アクセサリ（ケース、充電器、バッテリー等）の場合は isAccessory = true
4. confidence は 0.0〜1.0 の範囲です
5. 特定できない場合は models を空配列にしてください
6. 必ず有効なJSON形式のみを返してください
7. 全ての入力商品IDを含めてください
"""


def save_active_models(item_id: str, models: List[Dict]) -> str:
    """保存活跃商品的型号信息，返回状态"""
    normalized_models = []
    for model in models:
        brand = normalize(model.get("brand", ""))
        model_name = normalize(model.get("model", ""))
        
        if not brand or not model_name:
            continue
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "normalizedModel": normalize_model_key(brand, model_name),
            "confidence": str(model.get("confidence", 0)),
            "evidence": normalize(model.get("evidence", ""))
        })
    
    status = "COMPLETED" if normalized_models else "REVIEW_REQUIRED"
    now = datetime.now(timezone.utc).isoformat()
    
    active_table.update_item(
        Key={"itemID": item_id},
        UpdateExpression="""
            SET models = :models,
                modelStatus = :status,
                modelParsedAt = :now,
                workflowStatus = :workflow
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":now": now,
            ":workflow": "MODEL_PARSED"
        }
    )
    
    return status


def mark_active_model_failed(item_id: str, error: str):
    """标记活跃商品型号解析失败"""
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
    """获取唯一定型号列表"""
    unique = {}
    
    for item in active_items:
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
                    "normalizedModel": key
                }
    
    return unique


# ==================== 第三步：搜索闭拍商品 ====================

def search_closed_for_model(keyword: str, model_info: Dict, max_items: int) -> List[Dict]:
    """搜索指定型号的闭拍商品"""
    logger.info(f"搜索闭拍商品: {keyword}")
    
    original_params = os.environ.get("DEFAULT_PARAMS_CLOSED", "")
    original_max_pages = os.environ.get("MAX_PAGES", "1")
    original_items_per_page = os.environ.get("ITEMS_PER_PAGE", "50")
    
    try:
        pages_needed = (max_items + 49) // 50
        os.environ["DEFAULT_PARAMS_CLOSED"] = "is_postage_mode=1&dest_pref_code=23&n=50&s1=end&o1=d&mode=3&isdr=0"
        os.environ["MAX_PAGES"] = str(max(1, pages_needed))
        os.environ["ITEMS_PER_PAGE"] = "50"
        
        items = scrape_auctions(keyword, "closed", False)
        items = items[:max_items]
        
        saved_items = []
        for item in items:
            try:
                upsert_closed_item(item, model_info)
                saved_items.append(item)
            except Exception as e:
                logger.error(f"保存闭拍商品失败 {item.get('itemId')}: {e}")
        
        return saved_items
    finally:
        if original_params:
            os.environ["DEFAULT_PARAMS_CLOSED"] = original_params
        os.environ["MAX_PAGES"] = original_max_pages
        os.environ["ITEMS_PER_PAGE"] = original_items_per_page


def upsert_closed_item(item: Dict, model_info: Dict):
    """更新或插入闭拍商品（支持新版抓取器所有字段）"""
    now = datetime.now(timezone.utc)
    model_key = model_info.get("normalizedModel", "")
    
    # 处理可选字段
    buynow_price = item.get("buynowPrice")
    shipping_fee = item.get("shippingFee")
    shipping_text = item.get("shippingText", "")
    is_free_shipping = item.get("isFreeShipping", False)
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
        ":pending": "PENDING",
        ":now": now.isoformat(),
        ":ttl": int((now + timedelta(days=180)).timestamp()),
        ":model_key_set": {model_key} if model_key else set()
    }
    
    if buynow_price is not None:
        update_expr += ", buynowPrice = :buynow_price"
        expr_values[":buynow_price"] = buynow_price
    
    if shipping_fee is not None:
        update_expr += ", shippingFee = :shipping_fee, shippingText = :shipping_text, isFreeShipping = :is_free_shipping"
        expr_values[":shipping_fee"] = shipping_fee
        expr_values[":shipping_text"] = shipping_text
        expr_values[":is_free_shipping"] = is_free_shipping
    
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


# ==================== 第四步：AI 清洗闭拍型号 ====================

def get_unparsed_closed_items(limit: int = 100) -> List[Dict]:
    """获取未解析型号的闭拍商品"""
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
    """批量解析闭拍商品型号"""
    if not items:
        return 0
    
    batch_size = 20
    total_parsed = 0
    
    for i in range(0, len(items), batch_size):
        # 检查限制条件
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
            listing_type = parsed.get("listingType", "UNKNOWN")
            is_comparable = parsed.get("isComparable", False)
            condition = parsed.get("condition", "UNKNOWN")
            exclusion_reason = parsed.get("exclusionReason", "")
            
            excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
            effective_comparable = (
                bool(models)
                and listing_type not in excluded_types
                and is_comparable
            )
            
            save_closed_models(
                item_id, models, listing_type, 
                effective_comparable, condition, exclusion_reason
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
    """构建闭拍型号解析提示词"""
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは中古電子製品の専門家です。以下のYahooオークションの落札商品が、検索対象モデルと一致するか判定してください。

商品リスト：
{items_text}

以下のJSON形式で返してください：
{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名",
          "model": "モデル名",
          "confidence": 0.95
        }}
      ],
      "listingType": "MAIN_PRODUCT",
      "condition": "USED",
      "isComparable": true,
      "exclusionReason": ""
    }}
  ]
}}

listingType:
- MAIN_PRODUCT: 本体
- ACCESSORY: アクセサリ
- PARTS: 部品
- BROKEN: ジャンク
- BOX_ONLY: 箱のみ
- BUNDLE: 複数セット
- UNKNOWN: 不明

condition:
- NEW: 新品
- USED: 中古
- BROKEN: 故障
- UNKNOWN: 不明

ルール：
1. アクセサリ、部品、箱のみは isComparable = false
2. ジャンク品は isComparable = false
3. 全ての入力商品IDを含めてください
4. 必ず有効なJSON形式のみを返してください
"""


def save_closed_models(
    item_id: str, 
    models: List[Dict], 
    listing_type: str, 
    is_comparable: bool,
    condition: str = "UNKNOWN",
    exclusion_reason: str = ""
):
    """保存闭拍商品型号"""
    normalized_models = []
    for model in models:
        brand = normalize(model.get("brand", ""))
        model_name = normalize(model.get("model", ""))
        
        if not brand or not model_name:
            continue
        
        normalized_models.append({
            "brand": brand,
            "model": model_name,
            "normalizedModel": normalize_model_key(brand, model_name),
            "confidence": str(model.get("confidence", 0))
        })
    
    if not normalized_models:
        status = "REVIEW_REQUIRED"
    elif any(float(m.get("confidence", 0)) < 0.7 for m in normalized_models):
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
                condition = :condition,
                exclusionReason = :exclusion_reason,
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_comparable": is_comparable,
            ":condition": condition,
            ":exclusion_reason": exclusion_reason,
            ":now": now
        }
    )


def mark_closed_parse_failed(item_id: str, error: str):
    """标记闭拍商品解析失败"""
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

def get_unpriced_active_items(limit: int = 50) -> List[Dict]:
    """获取未定价的活跃商品"""
    all_items = []
    last_key = None
    
    while len(all_items) < limit:
        params = {
            "FilterExpression": Attr("pricingStatus").eq("PENDING"),
            "Limit": min(limit - len(all_items), 100)
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        
        response = active_table.scan(**params)
        all_items.extend(response.get("Items", []))
        
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    
    return all_items[:limit]


def batch_price_analysis(items: List[Dict]) -> int:
    """批量估价分析"""
    if not items:
        return 0
    
    total_priced = 0
    
    for item in items:
        try:
            # 检查限制条件
            check_limits()
            
            comparable_items = get_comparable_closed_items(item)
            stats = calculate_price_statistics(comparable_items)
            
            if stats["is_sufficient"]:
                ai_analysis = ai_price_analysis(item, comparable_items, stats)
            else:
                ai_analysis = {}
            
            # 计算实际成本
            purchase_price = safe_decimal(item.get("price", 0))
            
            # 考虑运费
            actual_shipping = safe_decimal(item.get("shippingFee"), DEFAULT_SHIPPING_COST)
            if item.get("isFreeShipping", False) or actual_shipping == 0:
                actual_shipping = Decimal("0")
            
            # 考虑即决价格
            buynow_price = safe_decimal(item.get("buynowPrice")) if item.get("buynowPrice") else None
            
            pricing_result = merge_pricing_result(
                stats, ai_analysis, purchase_price, 
                actual_shipping, buynow_price
            )
            save_pricing_result(item["itemID"], pricing_result)
            
            total_priced += 1
            
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
    
    return total_priced


def get_comparable_closed_items(active_item: Dict) -> List[Dict]:
    """获取可比闭拍商品"""
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
    """计算价格统计"""
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
        return {
            "count": n,
            "is_sufficient": False,
            "prices": [int(p) for p in prices]
        }
    
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
    """AI 深度估价分析"""
    max_comparables = 20
    selected_comparables = comparable_items[:max_comparables]
    
    prompt = build_pricing_prompt(active_item, selected_comparables, stats)
    result = call_ai_with_retry(prompt)
    
    return result or {}


def build_pricing_prompt(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> str:
    """构建估价提示词"""
    active_data = {
        "itemId": active_item["itemID"],
        "title": active_item.get("title", ""),
        "currentBid": safe_int(active_item.get("price", 0)),
        "buynowPrice": safe_int(active_item.get("buynowPrice")) if active_item.get("buynowPrice") else None,
        "bidCount": safe_int(active_item.get("bidCount", 0)),
        "sellerRating": active_item.get("sellerRating", ""),
        "sellerType": active_item.get("sellerType", "personal"),
        "itemCondition": active_item.get("itemCondition", ""),
        "shippingFee": safe_int(active_item.get("shippingFee")) if active_item.get("shippingFee") is not None else None,
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
            "condition": item.get("condition", "UNKNOWN"),
            "sellerRating": item.get("sellerRating", ""),
            "sellerType": item.get("sellerType", "personal"),
            "shippingFee": safe_int(item.get("shippingFee")) if item.get("shippingFee") is not None else None,
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
    """合并统计和AI分析结果，代码计算所有金额"""
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
    
    # 代码计算所有费用
    platform_fee = (estimated_price * EXPECTED_SELLING_FEE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    repair_reserve = (estimated_price * DEFAULT_REPAIR_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    risk_reserve = (estimated_price * RISK_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    
    # 总成本（含运费）
    total_costs = platform_fee + actual_shipping + repair_reserve + risk_reserve
    
    # 当前出价利润
    net_profit_at_bid = estimated_price - purchase_price - total_costs
    profit_margin_at_bid = (net_profit_at_bid / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP) if estimated_price > 0 else Decimal("0")
    
    # 即决价格利润（如果有）
    net_profit_buynow = None
    profit_margin_buynow = None
    if buynow_price and buynow_price > 0:
        net_profit_buynow = estimated_price - buynow_price - total_costs
        profit_margin_buynow = (net_profit_buynow / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP) if estimated_price > 0 else Decimal("0")
    
    # 计算不同利润目标下的购入价格
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
    
    # 决策逻辑
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
    
    # 添加即决价格信息
    if buynow_price and buynow_price > 0:
        result["buynowPrice"] = int(buynow_price)
        result["netProfitAtBuynow"] = int(net_profit_buynow) if net_profit_buynow else None
        result["profitMarginAtBuynow"] = float(profit_margin_buynow) if profit_margin_buynow else None
    
    return to_decimal(result)


def save_pricing_result(item_id: str, pricing_result: Dict):
    """保存估价结果"""
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
    """标记估价失败"""
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


# ==================== AI 调用（支持 Secrets Manager 和 Token 控制）====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
    """调用 AI API（带重试、Token 控制和超时检查）"""
    for attempt in range(AI_MAX_RETRIES):
        try:
            # 检查限制条件
            check_limits()
            
            # 检查剩余时间是否足够
            remaining = get_remaining_seconds()
            if remaining < AI_REQUEST_TIMEOUT + 10:
                raise RuntimeError(
                    f"剩余时间不足，无法完成API调用: 剩余{remaining:.1f}秒, "
                    f"请求超时{AI_REQUEST_TIMEOUT}秒"
                )
            
            result = call_ai(prompt)
            if result is not None:
                return result
            
            logger.warning(f"AI 返回空结果，重试 {attempt + 1}/{AI_MAX_RETRIES}")
            
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


def call_ai(prompt: str) -> Optional[Dict]:
    """调用 AI API（使用 Secrets Manager 获取密钥）"""
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
            
            # 提取并更新 Token 使用量
            usage = result.get("usage", {})
            if usage:
                update_token_usage(usage)
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
            else:
                content = result.get("content", "")
            
            return parse_ai_json(content)
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"AI API HTTP {e.code}: {error_body[:500]}")
        
        if e.code in RETRYABLE_CODES:
            raise
        return None
        
    except Exception as e:
        logger.error(f"AI API 调用失败: {e}")
        return None


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


def response(status_code: int, body: Dict) -> Dict:
    """构建 Lambda 响应"""
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }
