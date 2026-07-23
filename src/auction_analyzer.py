"""
Yahoo Auction 商品分析工作流 Lambda
功能：
1. 搜索活跃商品并解析型号
2. 搜索对应闭拍商品
3. AI 清洗闭拍商品型号
4. AI 估价和利润分析
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
from typing import List, Dict, Optional, Set, Any, Union

import boto3
from boto3.dynamodb.conditions import Key, Attr

# 导入现有的抓取函数
from yahoo_auction_scraper import scrape_auctions

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

# 估价配置 - 使用 Decimal 避免浮点数问题
EXPECTED_SELLING_FEE_RATE = Decimal(os.getenv("EXPECTED_SELLING_FEE_RATE", "0.10"))
DEFAULT_SHIPPING_COST = Decimal(os.getenv("DEFAULT_SHIPPING_COST", "1500"))
DEFAULT_REPAIR_RESERVE_RATE = Decimal(os.getenv("DEFAULT_REPAIR_RESERVE_RATE", "0.05"))
MIN_COMPARABLE_COUNT = int(os.getenv("MIN_COMPARABLE_COUNT", "3"))
MAX_PRICE_DEVIATION = Decimal(os.getenv("MAX_PRICE_DEVIATION", "1.5"))
RISK_RESERVE_RATE = Decimal(os.getenv("RISK_RESERVE_RATE", "0.03"))

dynamodb = boto3.resource("dynamodb")
active_table = dynamodb.Table(TABLE_NAME_ACTIVE)
closed_table = dynamodb.Table(TABLE_NAME_CLOSED)


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
    # 保留字母、数字、空格、加号、减号、斜杠
    normalized = re.sub(r"[^A-Z0-9\s+\-/]", " ", normalized)
    # 合并多余空格
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_bool(value: Any) -> bool:
    """安全转换布尔值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def parse_int(value: Any, default: int = 0) -> int:
    """安全转换整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def lambda_handler(event, context):
    """主入口函数"""
    try:
        # 安全获取并验证参数
        keyword = normalize(event.get("keyword", ""))
        
        if not keyword:
            return response(400, {"error": "keyword 不能为空"})
        
        # 安全转换 count
        try:
            count = int(event.get("count", DEFAULT_SEARCH_COUNT))
        except (ValueError, TypeError):
            return response(400, {
                "error": "count 必须是有效整数",
                "received": str(event.get("count"))
            })
        
        # 安全转换 force_reprocess
        force_reprocess = parse_bool(event.get("force_reprocess", False))
        
        count = max(1, min(count, MAX_ACTIVE_ITEMS))
        
        logger.info(
            f"开始商品分析工作流: keyword='{keyword}', "
            f"count={count}, force_reprocess={force_reprocess}"
        )
        
        # 验证 AI API 配置
        if not AI_API_KEY:
            return response(500, {"error": "AI_API_KEY 环境变量未配置"})
        
        # 执行工作流
        result = execute_workflow(keyword, count, force_reprocess)
        
        return response(200, result)
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}", exc_info=True)
        return response(500, {
            "error": "内部错误",
            "details": str(e)
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
        # ========== 第一步：搜索并保存活跃商品 ==========
        logger.info(f"第一步：搜索活跃商品: {keyword}")
        active_item_ids = scrape_and_save_active(keyword, count)
        workflow_result["active_scraped"] = len(active_item_ids)
        
        if not active_item_ids:
            logger.info("未找到活跃商品，工作流结束")
            return workflow_result
        
        # 重新从 DynamoDB 读取完整的商品信息
        all_active = get_active_items_by_keyword(keyword)
        
        # 筛选需要解析型号的商品
        items_to_parse = [
            item for item in all_active
            if force_reprocess or item.get("modelStatus") == "PENDING"
        ]
        
        if not items_to_parse:
            logger.info("所有商品型号已解析，跳过型号解析步骤")
        else:
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
        
        if not unique_models:
            logger.info("未识别到任何型号，跳过闭拍搜索")
        else:
            logger.info(f"第三步：搜索闭拍商品 ({len(unique_models)} 个型号)")
            total_closed = 0
            for i, model_info in enumerate(unique_models.values()):
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
        
        if not unparsed_closed:
            logger.info("所有闭拍商品型号已解析")
        else:
            logger.info(f"第四步：清洗闭拍商品型号 ({len(unparsed_closed)} 个商品)")
            parsed_count = batch_parse_closed_models(unparsed_closed)
            workflow_result["closed_parsed"] = parsed_count
        
        # ========== 第五步：估价分析 ==========
        unpriced_items = get_unpriced_active_items()
        
        if not unpriced_items:
            logger.info("所有商品已估价")
        else:
            logger.info(f"第五步：估价分析 ({len(unpriced_items)} 个商品)")
            priced_count = batch_price_analysis(unpriced_items)
            workflow_result["priced_items"] = priced_count
        
        # 完成
        elapsed = time.time() - start_time
        workflow_result["elapsed_seconds"] = round(elapsed, 1)
        workflow_result["status"] = "COMPLETED"
        
        logger.info(f"工作流完成: {json.dumps(workflow_result, ensure_ascii=False, default=str)}")
        return workflow_result
        
    except Exception as e:
        logger.error(f"工作流出错: {e}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(e))
        return workflow_result


# ==================== 第一步：搜索活跃商品 ====================

def scrape_and_save_active(keyword: str, count: int) -> List[str]:
    """搜索活跃商品并保存，返回 itemID 列表"""
    original_params = os.environ.get("DEFAULT_PARAMS", "")
    original_max_pages = os.environ.get("MAX_PAGES", "1")
    original_items_per_page = os.environ.get("ITEMS_PER_PAGE", "50")
    
    os.environ["DEFAULT_PARAMS"] = f"n={count}&select=6&mode=3&s1=end&o1=a"
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
            os.environ["DEFAULT_PARAMS"] = original_params
        os.environ["MAX_PAGES"] = original_max_pages
        os.environ["ITEMS_PER_PAGE"] = original_items_per_page


def upsert_active_item(item: Dict, keyword: str):
    """更新或插入活跃商品"""
    now = datetime.now(timezone.utc)
    
    active_table.update_item(
        Key={"itemID": item["itemId"]},
        UpdateExpression="""
            SET itemType = :item_type,
                title = :title,
                price = :price,
                bidCount = :bid_count,
                endTime = :end_time,
                sellerId = :seller_id,
                sellerRating = :seller_rating,
                prefecture = :prefecture,
                #url = :url,
                thumbnailUrl = :thumbnail,
                searchKeyword = :keyword,
                lastScrapedAt = :now,
                modelStatus = if_not_exists(modelStatus, :model_pending),
                pricingStatus = if_not_exists(pricingStatus, :pricing_pending),
                workflowStatus = :scraped,
                #ttl = :ttl
        """,
        ExpressionAttributeNames={
            "#url": "url",
            "#ttl": "ttl"
        },
        ExpressionAttributeValues={
            ":item_type": item.get("itemType", "auction"),
            ":title": item.get("title", ""),
            ":price": item.get("price", 0),
            ":bid_count": item.get("bidCount", 0),
            ":end_time": item.get("endTime") or "unknown",
            ":seller_id": item.get("sellerId") or "unknown",
            ":seller_rating": item.get("sellerRating") or "unknown",
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
    """批量解析活跃商品型号，返回统计信息"""
    if not items:
        return {"parsed": 0, "review_required": 0, "models_found": 0}
    
    # 构建请求数据
    items_data = [
        {
            "itemId": item["itemID"],
            "title": item.get("title", "")
        }
        for item in items
    ]
    
    # 调用 AI
    prompt = build_model_parsing_prompt(items_data)
    result = call_ai_with_retry(prompt)
    
    if not result:
        logger.error("AI 型号解析返回空结果")
        # 标记所有商品为失败
        for item in items:
            mark_active_model_failed(item["itemID"], "AI_RESPONSE_EMPTY")
        return {"parsed": 0, "review_required": 0, "models_found": 0, "failed": len(items)}
    
    # 解析结果并保存
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
    
    # 标记 AI 未返回的商品
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
      ]
    }}
  ]
}}

ルール：
1. 各商品IDに対して必ずエントリを作成してください
2. 一つの商品に複数のモデルが含まれる可能性があります
3. アクセサリや部品は除外してください
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
    
    original_max_pages = os.environ.get("MAX_PAGES", "1")
    original_items_per_page = os.environ.get("ITEMS_PER_PAGE", "50")
    
    try:
        # 正确计算页数（向上取整）
        pages_needed = (max_items + 49) // 50
        os.environ["MAX_PAGES"] = str(max(1, pages_needed))
        os.environ["ITEMS_PER_PAGE"] = "50"
        
        items = scrape_auctions(keyword, "closed", False)
        
        # 限制数量
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
        os.environ["MAX_PAGES"] = original_max_pages
        os.environ["ITEMS_PER_PAGE"] = original_items_per_page


def upsert_closed_item(item: Dict, model_info: Dict):
    """更新或插入闭拍商品，避免重复追加 searchModels"""
    now = datetime.now(timezone.utc)
    model_key = model_info.get("normalizedModel", "")
    
    # 使用 SET 添加去重逻辑
    closed_table.update_item(
        Key={"itemID": item["itemId"]},
        UpdateExpression="""
            SET itemType = :item_type,
                title = :title,
                price = :price,
                bidCount = :bid_count,
                endTime = :end_time,
                sellerId = :seller_id,
                sellerRating = :seller_rating,
                prefecture = :prefecture,
                #url = :url,
                thumbnailUrl = :thumbnail,
                sourceModel = :source_model,
                modelStatus = if_not_exists(modelStatus, :pending),
                lastScrapedAt = :now,
                #ttl = :ttl
            ADD searchModelKeys :model_key_set
        """,
        ExpressionAttributeNames={
            "#url": "url",
            "#ttl": "ttl"
        },
        ExpressionAttributeValues={
            ":item_type": item.get("itemType", "auction"),
            ":title": item.get("title", ""),
            ":price": item.get("price", 0),
            ":bid_count": item.get("bidCount", 0),
            ":end_time": item.get("endTime") or "unknown",
            ":seller_id": item.get("sellerId") or "unknown",
            ":seller_rating": item.get("sellerRating") or "unknown",
            ":prefecture": item.get("prefecture") or "unknown",
            ":url": item.get("url", ""),
            ":thumbnail": item.get("thumbnailUrl", ""),
            ":source_model": model_info,
            ":pending": "PENDING",
            ":now": now.isoformat(),
            ":ttl": int((now + timedelta(days=180)).timestamp()),
            ":model_key_set": {model_key} if model_key else set()
        }
    )


# ==================== 第四步：AI 清洗闭拍型号 ====================

def get_unparsed_closed_items(limit: int = 100) -> List[Dict]:
    """获取未解析型号的闭拍商品（支持分页）"""
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
        batch = items[i:i + batch_size]
        
        items_data = [
            {
                "itemId": item["itemID"],
                "title": item.get("title", ""),
                "sourceModel": item.get("sourceModel", {})
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
            
            # 代码层增加规则验证
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
        
        # 标记未返回的商品
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

以下のJSON形式で返してください。各商品IDに対して必ず結果を含めてください：
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

listingType の種類：
- MAIN_PRODUCT: 本体（比較可能）
- ACCESSORY: アクセサリ・ケース・保護フィルム
- PARTS: 部品・パーツ
- BROKEN: ジャンク・故障品
- BOX_ONLY: 箱のみ
- BUNDLE: 複数セット
- UNKNOWN: 判断不能

condition の種類：
- NEW: 新品
- USED: 中古
- BROKEN: 故障・ジャンク
- UNKNOWN: 不明

判定ルール：
1. アクセサリ、部品、箱のみは isComparable = false
2. ジャンク品は isComparable = false
3. 複数モデルが混在する場合は models に複数記載
4. 全く関係ない商品は空の models 配列
5. 確信度が低い場合（confidence < 0.7）は REVIEW_REQUIRED として扱う
6. 全ての入力商品IDを含めてください
7. 必ず有効なJSON形式のみを返してください
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
    
    # 判断状态
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
    """获取未定价的活跃商品（支持分页）"""
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
            comparable_items = get_comparable_closed_items(item)
            stats = calculate_price_statistics(comparable_items)
            
            if stats["is_sufficient"]:
                ai_analysis = ai_price_analysis(item, comparable_items, stats)
            else:
                ai_analysis = {}
            
            # 确保 purchase_price 是 Decimal
            purchase_price = Decimal(str(item.get("price", 0)))
            pricing_result = merge_pricing_result(stats, ai_analysis, purchase_price)
            save_pricing_result(item["itemID"], pricing_result)
            
            total_priced += 1
            
            time.sleep(REQUEST_INTERVAL)
            
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
            # 使用 scan 但添加型号过滤（理想情况应使用 GSI）
            response = closed_table.scan(
                FilterExpression=(
                    Attr("modelStatus").eq("COMPLETED") &
                    Attr("isComparable").eq(True) &
                    Attr("price").gt(0)
                ),
                Limit=200  # 限制扫描数量
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
    
    # 按结束时间排序，取最近的
    comparable.sort(
        key=lambda x: x.get("endTime", ""),
        reverse=True
    )
    
    return comparable


def calculate_price_statistics(comparable_items: List[Dict]) -> Dict:
    """计算价格统计（使用 Decimal）"""
    # 提取价格并转为 Decimal
    prices = []
    for item in comparable_items:
        try:
            price = Decimal(str(item.get("price", 0)))
            if price > 0:
                prices.append(price)
        except (ValueError, TypeError):
            continue
    
    prices.sort()
    n = len(prices)
    
    if n < MIN_COMPARABLE_COUNT:
        return {
            "count": n,
            "is_sufficient": False,
            "prices": [int(p) for p in prices]
        }
    
    # 计算分位数（使用线性插值）
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
    
    # IQR 异常值过滤
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
    """AI 深度估价分析（仅返回定性信息）"""
    max_comparables = 20
    selected_comparables = comparable_items[:max_comparables]
    
    prompt = build_pricing_prompt(active_item, selected_comparables, stats)
    result = call_ai_with_retry(prompt)
    
    return result or {}


def build_pricing_prompt(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> str:
    """构建估价提示词（AI 只负责定性分析）"""
    active_data = {
        "itemId": active_item["itemID"],
        "title": active_item.get("title", ""),
        "currentBid": active_item.get("price", 0),
        "bidCount": active_item.get("bidCount", 0),
        "sellerRating": active_item.get("sellerRating", ""),
        "models": active_item.get("models", [])
    }
    
    comparables_data = [
        {
            "itemId": item["itemID"],
            "title": item.get("title", ""),
            "price": item.get("price", 0),
            "bidCount": item.get("bidCount", 0),
            "endTime": item.get("endTime", ""),
            "listingType": item.get("listingType", ""),
            "condition": item.get("condition", "UNKNOWN")
        }
        for item in comparable_items[:20]
    ]
    
    return f"""
あなたは中古電子製品の価格分析の専門家です。以下の情報を基に、商品のリスク評価と価格調整を行ってください。

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
  "usableComparableItemIds": ["ID1", "ID2"]
}}

riskLevel:
- LOW: リスクが低い（明確な商品、信頼できる出品者）
- MEDIUM: 中程度のリスク
- HIGH: 高リスク（不明瞭な説明、低評価の出品者）

decisionSignal:
- BUY_CANDIDATE: 購入候補（高利益率、低リスク）
- REVIEW: 要確認
- AVOID: 購入非推奨
- INSUFFICIENT_DATA: データ不足

分析ルール：
1. 商品状態の違いを評価
2. 出品者評価に基づくリスク判断
3. 相場データの質と信頼性
4. 説明文の明確さ
5. 必ず有効なJSON形式のみを返してください
"""


def merge_pricing_result(stats: Dict, ai_analysis: Dict, purchase_price: Decimal) -> Dict:
    """合并统计和AI分析结果，代码计算所有金额"""
    if not stats.get("is_sufficient"):
        return to_decimal({
            "pricingStatus": "INSUFFICIENT_DATA",
            "pricingConfidence": 0.2,
            "reasons": ["可比数据不足（需要至少3个可比样本）"],
            "comparableCount": stats.get("count", 0)
        })
    
    # 使用统计中位数作为估算售价
    estimated_price = Decimal(str(stats["filtered_median"]))
    estimated_low = Decimal(str(stats["filtered_min"]))
    estimated_high = Decimal(str(stats["filtered_max"]))
    
    # 代码计算所有费用
    platform_fee = (estimated_price * EXPECTED_SELLING_FEE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    repair_reserve = (estimated_price * DEFAULT_REPAIR_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    risk_reserve = (estimated_price * RISK_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    shipping_cost = DEFAULT_SHIPPING_COST
    
    # 计算利润
    gross_spread = estimated_price - purchase_price
    total_costs = platform_fee + shipping_cost + repair_reserve + risk_reserve
    net_profit = gross_spread - total_costs
    profit_margin = (net_profit / estimated_price).quantize(Decimal("0.001"), ROUND_HALF_UP) if estimated_price > 0 else Decimal("0")
    
    # 计算不同利润目标下的购入价格
    target_margin_20 = Decimal("0.20")
    target_margin_10 = Decimal("0.10")
    
    break_even_price = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE)
        - shipping_cost
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_20 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - target_margin_20)
        - shipping_cost
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    target_price_10 = (
        estimated_price * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - target_margin_10)
        - shipping_cost
    ).quantize(Decimal("1"), ROUND_HALF_UP)
    
    # 决策逻辑
    risk_level = ai_analysis.get("riskLevel", "MEDIUM")
    pricing_confidence = Decimal(str(ai_analysis.get("pricingConfidence", 0.7)))
    
    if net_profit <= 0:
        decision = "AVOID"
    elif risk_level == "HIGH" or pricing_confidence < Decimal("0.5"):
        decision = "REVIEW"
    elif profit_margin >= Decimal("0.20") and pricing_confidence >= Decimal("0.75") and risk_level == "LOW":
        decision = "BUY_CANDIDATE"
    else:
        decision = "REVIEW"
    
    return to_decimal({
        "pricingStatus": "COMPLETED",
        "estimatedMarketPrice": int(estimated_price),
        "estimatedLow": int(estimated_low),
        "estimatedHigh": int(estimated_high),
        "currentBidPrice": int(purchase_price),
        "breakEvenPurchasePrice": int(break_even_price),
        "targetPurchasePrice20Margin": int(target_price_20),
        "targetPurchasePrice10Margin": int(target_price_10),
        "grossSpread": int(gross_spread),
        "netProfitAfterCosts": int(net_profit),
        "profitMargin": float(profit_margin),
        "pricingConfidence": float(pricing_confidence),
        "riskLevel": risk_level,
        "decisionSignal": decision,
        "reasons": ai_analysis.get("reasons", []),
        "riskFactors": ai_analysis.get("riskFactors", []),
        "comparableItemIds": ai_analysis.get("usableComparableItemIds", []),
        "comparableCount": stats.get("filtered_count", 0),
        "priceBreakdown": {
            "estimatedSellingPrice": int(estimated_price),
            "currentBidPrice": int(purchase_price),
            "platformFee": int(platform_fee),
            "shippingCost": int(shipping_cost),
            "repairReserve": int(repair_reserve),
            "riskReserve": int(risk_reserve),
            "netProfit": int(net_profit)
        }
    })


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
            ":error": error[:500],  # 限制错误信息长度
            ":now": now
        }
    )


# ==================== AI 调用（增强版） ====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
    """调用 AI API（带重试和错误处理）"""
    for attempt in range(AI_MAX_RETRIES):
        try:
            result = call_ai(prompt)
            if result is not None:
                return result
            
            logger.warning(f"AI 返回空结果，重试 {attempt + 1}/{AI_MAX_RETRIES}")
            
        except Exception as e:
            logger.error(f"AI 调用异常 (尝试 {attempt + 1}): {e}")
        
        if attempt < AI_MAX_RETRIES - 1:
            # 指数退避 + 随机抖动
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    logger.error(f"AI 调用失败，已重试 {AI_MAX_RETRIES} 次")
    return None


def call_ai(prompt: str) -> Optional[Dict]:
    """调用 AI API"""
    if not AI_API_KEY:
        raise ValueError("AI_API_KEY 未配置")
    
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
        "response_format": {"type": "json_object"}  # 强制 JSON 输出
    }
    
    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    
    request = urllib.request.Request(
        AI_API_URL,
        data=encoded_body,
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(request, timeout=AI_REQUEST_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
            else:
                content = result.get("content", "")
            
            return parse_ai_json(content)
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"AI API HTTP {e.code}: {error_body[:500]}")
        
        if e.code == 429:
            raise  # 限流，触发重试
        return None
        
    except Exception as e:
        logger.error(f"AI API 调用失败: {e}")
        return None


def parse_ai_json(content: str) -> Optional[Dict]:
    """解析 AI 返回的 JSON（增强容错）"""
    if not content:
        return None
    
    content = content.strip()
    
    # 尝试多种解析方式
    parse_attempts = [
        # 1. 直接解析
        lambda c: json.loads(c),
        # 2. 移除 markdown 代码块
        lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", c)),
        # 3. 提取 JSON 对象
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
