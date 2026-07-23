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
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Set
import hashlib

import boto3
from boto3.dynamodb.conditions import Key, Attr

# 导入现有的抓取函数
from yahoo_auction_scraper import (
    build_url,
    parse_html,
    scrape_auctions,
    save_items
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
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "1.0"))
INCLUDE_PAYPAY = os.getenv("INCLUDE_PAYPAY", "false").lower() == "true"

# 估价配置
EXPECTED_SELLING_FEE_RATE = float(os.getenv("EXPECTED_SELLING_FEE_RATE", "0.10"))  # 10% 平台手续费
DEFAULT_SHIPPING_COST = int(os.getenv("DEFAULT_SHIPPING_COST", "1500"))  # 默认运费
DEFAULT_REPAIR_RESERVE_RATE = float(os.getenv("DEFAULT_REPAIR_RESERVE_RATE", "0.05"))  # 5% 维修储备金
MIN_COMPARABLE_COUNT = int(os.getenv("MIN_COMPARABLE_COUNT", "3"))  # 最少可比商品数
MAX_PRICE_DEVIATION = float(os.getenv("MAX_PRICE_DEVIATION", "1.5"))  # IQR 倍数
RISK_RESERVE_RATE = float(os.getenv("RISK_RESERVE_RATE", "0.03"))  # 3% 风险准备金

dynamodb = boto3.resource("dynamodb")
active_table = dynamodb.Table(TABLE_NAME_ACTIVE)
closed_table = dynamodb.Table(TABLE_NAME_CLOSED)


def normalize(value: str) -> str:
    """标准化文本"""
    if not value:
        return ""
    value = str(value).strip()
    # 全角转半角
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
    """生成标准化型号键"""
    combined = f"{brand} {model}"
    normalized = normalize(combined).upper()
    # 移除特殊字符，保留字母数字和空格
    normalized = re.sub(r"[^A-Z0-9\s]", " ", normalized)
    # 合并多余空格
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def lambda_handler(event, context):
    """主入口函数"""
    try:
        keyword = normalize(event.get("keyword", ""))
        count = int(event.get("count", DEFAULT_SEARCH_COUNT))
        force_reprocess = event.get("force_reprocess", False)
        
        # 参数验证
        if not keyword:
            return response(400, {"error": "keyword 不能为空"})
        
        count = max(1, min(count, MAX_ACTIVE_ITEMS))
        
        logger.info(f"开始商品分析工作流: keyword='{keyword}', count={count}")
        
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
        "models_identified": 0,
        "closed_scraped": 0,
        "closed_models_parsed": 0,
        "priced_items": 0,
        "errors": []
    }
    
    try:
        # ========== 第一步：搜索并保存活跃商品 ==========
        logger.info(f"第一步：搜索活跃商品: {keyword}")
        active_items = scrape_and_save_active(keyword, count)
        workflow_result["active_scraped"] = len(active_items)
        
        if not active_items:
            logger.info("未找到活跃商品，工作流结束")
            return workflow_result
        
        # 筛选需要解析型号的商品
        items_to_parse = [
            item for item in active_items
            if force_reprocess or item.get("modelStatus") == "PENDING"
        ]
        
        if not items_to_parse:
            logger.info("所有商品型号已解析，跳过型号解析步骤")
        else:
            # ========== 第二步：批量解析活跃商品型号 ==========
            logger.info(f"第二步：批量解析型号 ({len(items_to_parse)} 个商品)")
            parsed_models = batch_parse_models(items_to_parse)
            workflow_result["models_identified"] = len(parsed_models)
        
        # 收集所有活跃商品（包括新解析的）
        all_active = get_active_items_by_keyword(keyword)
        
        # ========== 第三步：搜索闭拍商品 ==========
        # 收集所有已识别的型号（去重）
        unique_models = get_unique_models(all_active)
        
        if not unique_models:
            logger.info("未识别到任何型号，跳过闭拍搜索")
        else:
            logger.info(f"第三步：搜索闭拍商品 ({len(unique_models)} 个型号)")
            for i, model_info in enumerate(unique_models.values()):
                if i > 0:
                    time.sleep(REQUEST_INTERVAL)
                
                model_keyword = f'{model_info["brand"]} {model_info["model"]}'
                closed_items = search_closed_for_model(
                    model_keyword, 
                    model_info,
                    MAX_CLOSED_PER_MODEL
                )
                workflow_result["closed_scraped"] += len(closed_items)
        
        # ========== 第四步：AI 清洗闭拍商品型号 ==========
        unparsed_closed = get_unparsed_closed_items()
        
        if not unparsed_closed:
            logger.info("所有闭拍商品型号已解析")
        else:
            logger.info(f"第四步：清洗闭拍商品型号 ({len(unparsed_closed)} 个商品)")
            parsed_count = batch_parse_closed_models(unparsed_closed)
            workflow_result["closed_models_parsed"] = parsed_count
        
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
        
        logger.info(f"工作流完成: {json.dumps(workflow_result, ensure_ascii=False)}")
        return workflow_result
        
    except Exception as e:
        logger.error(f"工作流出错: {e}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(e))
        return workflow_result


# ==================== 第一步：搜索活跃商品 ====================

def scrape_and_save_active(keyword: str, count: int) -> List[Dict]:
    """搜索活跃商品并保存"""
    # 临时修改环境变量以限制搜索数量
    original_params = os.environ.get("DEFAULT_PARAMS", "n=50&select=6&mode=3")
    os.environ["DEFAULT_PARAMS"] = f"n={count}&select=6&mode=3&s1=end&o1=a"
    os.environ["MAX_PAGES"] = "1"
    os.environ["ITEMS_PER_PAGE"] = str(count)
    
    try:
        # 使用现有抓取函数
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        
        # 保存到 DynamoDB（使用 upsert）
        saved_items = []
        for item in items:
            try:
                upsert_active_item(item, keyword)
                saved_items.append({
                    "itemId": item["itemId"],
                    "title": item.get("title", ""),
                    "price": item.get("price", 0)
                })
            except Exception as e:
                logger.error(f"保存活跃商品失败 {item.get('itemId')}: {e}")
        
        return saved_items
    finally:
        # 恢复环境变量
        os.environ["DEFAULT_PARAMS"] = original_params
        os.environ["MAX_PAGES"] = "1"
        os.environ["ITEMS_PER_PAGE"] = "50"


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
    """获取指定关键词的活跃商品"""
    # 注意：这里需要扫描或使用 GSI，实际项目中应添加 GSI
    # 临时方案：扫描整个表
    response = active_table.scan(
        FilterExpression=Attr("searchKeyword").eq(keyword)
    )
    return response.get("Items", [])


def batch_parse_models(items: List[Dict]) -> List[Dict]:
    """批量解析活跃商品型号"""
    if not items:
        return []
    
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
    result = call_ai(prompt)
    
    if not result:
        logger.error("AI 型号解析返回空结果")
        return []
    
    # 解析结果并保存
    parsed_items = result.get("items", [])
    saved_count = 0
    
    for parsed in parsed_items:
        item_id = parsed.get("itemId")
        models = parsed.get("models", [])
        
        if item_id and models:
            save_active_models(item_id, models)
            saved_count += 1
    
    logger.info(f"型号解析完成: {saved_count}/{len(items)} 个商品")
    return parsed_items


def build_model_parsing_prompt(items: List[Dict]) -> str:
    """构建型号解析提示词"""
    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    
    return f"""
あなたは電子製品の専門家です。以下の商品タイトルから、具体的な製品モデルを特定してください。

商品リスト：
{items_text}

以下のJSON形式で返してください：
{{
  "items": [
    {{
      "itemId": "商品ID",
      "models": [
        {{
          "brand": "ブランド名（例：Lenovo, Apple, Sony）",
          "model": "モデル名（例：ThinkPad X1 Carbon Gen 11, iPhone 14 Pro）",
          "confidence": 0.95,
          "evidence": "タイトルからの証拠（例：タイトルに 'X1 Carbon Gen 11' と明記）"
        }}
      ]
    }}
  ]
}}

ルール：
1. 一つの商品に複数のモデルが含まれる可能性があります（例：'Gen 11 Gen 12 対応'）
2. アクセサリや部品は除外してください（例：ケース、充電器、バッテリー）
3. confidence は 0.0〜1.0 の範囲で、確信度を表します
4. 特定できない場合は空の models 配列を返してください
5. 必ずJSON形式のみを返し、説明文は不要です
6. ブランド名とモデル名は正規化してください（全角→半角、大文字小文字を統一）
"""


def save_active_models(item_id: str, models: List[Dict]):
    """保存活跃商品的型号信息"""
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


def get_unique_models(active_items: List[Dict]) -> Dict[str, Dict]:
    """获取唯一定型号列表"""
    unique = {}
    
    for item in active_items:
        models = item.get("models", [])
        if isinstance(models, str):
            try:
                models = json.loads(models)
            except:
                continue
        
        for model in models:
            key = model.get("normalizedModel")
            if key and key not in unique:
                unique[key] = {
                    "brand": model["brand"],
                    "model": model["model"],
                    "normalizedModel": key
                }
    
    return unique


# ==================== 第三步：搜索闭拍商品 ====================

def search_closed_for_model(keyword: str, model_info: Dict, max_items: int) -> List[Dict]:
    """搜索指定型号的闭拍商品"""
    logger.info(f"搜索闭拍商品: {keyword}")
    
    # 保存原始配置
    original_max_pages = os.environ.get("MAX_PAGES", "1")
    original_items_per_page = os.environ.get("ITEMS_PER_PAGE", "50")
    
    try:
        # 临时修改配置
        pages_needed = max(1, max_items // 50 + 1)
        os.environ["MAX_PAGES"] = str(pages_needed)
        os.environ["ITEMS_PER_PAGE"] = "50"
        
        # 使用现有抓取函数
        items = scrape_auctions(keyword, "closed", False)
        
        # 保存闭拍商品
        saved_items = []
        for item in items:
            try:
                upsert_closed_item(item, model_info)
                saved_items.append(item)
            except Exception as e:
                logger.error(f"保存闭拍商品失败 {item.get('itemId')}: {e}")
        
        return saved_items
    finally:
        # 恢复配置
        os.environ["MAX_PAGES"] = original_max_pages
        os.environ["ITEMS_PER_PAGE"] = original_items_per_page


def upsert_closed_item(item: Dict, model_info: Dict):
    """更新或插入闭拍商品"""
    now = datetime.now(timezone.utc)
    
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
                searchModels = list_append(
                    if_not_exists(searchModels, :empty_list),
                    :search_models
                ),
                modelStatus = if_not_exists(modelStatus, :pending),
                lastScrapedAt = :now,
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
            ":source_model": model_info,
            ":empty_list": [],
            ":search_models": [model_info],
            ":pending": "PENDING",
            ":now": now.isoformat(),
            ":ttl": int((now + timedelta(days=180)).timestamp())
        }
    )


# ==================== 第四步：AI 清洗闭拍型号 ====================

def get_unparsed_closed_items(limit: int = 100) -> List[Dict]:
    """获取未解析型号的闭拍商品"""
    response = closed_table.scan(
        FilterExpression=Attr("modelStatus").eq("PENDING"),
        Limit=limit
    )
    return response.get("Items", [])


def batch_parse_closed_models(items: List[Dict]) -> int:
    """批量解析闭拍商品型号"""
    if not items:
        return 0
    
    # 分批处理（每批最多 20 个）
    batch_size = 20
    total_parsed = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        # 构建请求
        items_data = [
            {
                "itemId": item["itemID"],
                "title": item.get("title", ""),
                "sourceModel": item.get("sourceModel", {})
            }
            for item in batch
        ]
        
        prompt = build_closed_model_parsing_prompt(items_data)
        result = call_ai(prompt)
        
        if not result:
            continue
        
        # 保存结果
        parsed_items = result.get("items", [])
        for parsed in parsed_items:
            item_id = parsed.get("itemId")
            
            if not item_id:
                continue
            
            models = parsed.get("models", [])
            listing_type = parsed.get("listingType", "UNKNOWN")
            is_comparable = parsed.get("isComparable", False)
            
            save_closed_models(item_id, models, listing_type, is_comparable)
            total_parsed += 1
        
        # 批次间延迟
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

listingType の種類：
- MAIN_PRODUCT: 本体（比較可能）
- ACCESSORY: アクセサリ・ケース・保護フィルム
- PARTS: 部品・パーツ
- BROKEN: ジャンク・故障品
- BOX_ONLY: 箱のみ
- BUNDLE: 複数セット
- UNKNOWN: 判断不能

判定ルール：
1. アクセサリ、部品、箱のみは isComparable = false
2. ジャンク品は isComparable = false
3. 複数モデルが混在する場合は models に複数記載
4. 全く関係ない商品は空の models 配列
5. 確信度が低い場合（confidence < 0.7）は REVIEW_REQUIRED として扱う
6. 必ずJSON形式のみを返してください
"""


def save_closed_models(item_id: str, models: List[Dict], listing_type: str, is_comparable: bool):
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
                modelParsedAt = :now
        """,
        ExpressionAttributeValues={
            ":models": normalized_models,
            ":status": status,
            ":listing_type": listing_type,
            ":is_comparable": is_comparable,
            ":now": now
        }
    )


# ==================== 第五步：估价分析 ====================

def get_unpriced_active_items(limit: int = 50) -> List[Dict]:
    """获取未定价的活跃商品"""
    response = active_table.scan(
        FilterExpression=Attr("pricingStatus").eq("PENDING"),
        Limit=limit
    )
    return response.get("Items", [])


def batch_price_analysis(items: List[Dict]) -> int:
    """批量估价分析"""
    if not items:
        return 0
    
    total_priced = 0
    
    for item in items:
        try:
            # 获取对应的可比闭拍商品
            comparable_items = get_comparable_closed_items(item)
            
            # 统计分析
            stats = calculate_price_statistics(comparable_items)
            
            # AI 深度分析
            ai_analysis = ai_price_analysis(item, comparable_items, stats)
            
            # 合并结果并保存
            pricing_result = merge_pricing_result(stats, ai_analysis, item["price"])
            save_pricing_result(item["itemID"], pricing_result)
            
            total_priced += 1
            
            # 请求间隔
            time.sleep(REQUEST_INTERVAL)
            
        except Exception as e:
            logger.error(f"估价失败 {item.get('itemID')}: {e}")
    
    return total_priced


def get_comparable_closed_items(active_item: Dict) -> List[Dict]:
    """获取可比闭拍商品"""
    models = active_item.get("models", [])
    if isinstance(models, str):
        try:
            models = json.loads(models)
        except:
            return []
    
    comparable = []
    seen_ids = set()
    
    for model in models:
        model_key = model.get("normalizedModel")
        if not model_key:
            continue
        
        # 查询闭拍商品
        try:
            response = closed_table.scan(
                FilterExpression=(
                    Attr("modelStatus").eq("COMPLETED") &
                    Attr("isComparable").eq(True) &
                    Attr("price").gt(0)
                )
            )
            
            for item in response.get("Items", []):
                item_models = item.get("models", [])
                if isinstance(item_models, str):
                    try:
                        item_models = json.loads(item_models)
                    except:
                        continue
                
                # 检查型号匹配
                for item_model in item_models:
                    if item_model.get("normalizedModel") == model_key:
                        if item["itemID"] not in seen_ids:
                            comparable.append(item)
                            seen_ids.add(item["itemID"])
                        break
                        
        except Exception as e:
            logger.error(f"查询闭拍商品失败: {e}")
    
    return comparable


def calculate_price_statistics(comparable_items: List[Dict]) -> Dict:
    """计算价格统计"""
    prices = sorted([item["price"] for item in comparable_items if item.get("price", 0) > 0])
    
    if len(prices) < MIN_COMPARABLE_COUNT:
        return {
            "count": len(prices),
            "is_sufficient": False,
            "prices": prices
        }
    
    # 计算分位数
    n = len(prices)
    q1_idx = n // 4
    q2_idx = n // 2
    q3_idx = (3 * n) // 4
    
    q1 = prices[q1_idx]
    median = prices[q2_idx]
    q3 = prices[q3_idx]
    iqr = q3 - q1
    
    # IQR 异常值过滤
    lower_bound = q1 - MAX_PRICE_DEVIATION * iqr
    upper_bound = q3 + MAX_PRICE_DEVIATION * iqr
    
    filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
    
    return {
        "count": len(prices),
        "filtered_count": len(filtered_prices),
        "is_sufficient": len(filtered_prices) >= MIN_COMPARABLE_COUNT,
        "min": min(prices),
        "max": max(prices),
        "q1": q1,
        "median": median,
        "q3": q3,
        "iqr": iqr,
        "filtered_min": min(filtered_prices) if filtered_prices else None,
        "filtered_max": max(filtered_prices) if filtered_prices else None,
        "filtered_median": sorted(filtered_prices)[len(filtered_prices)//2] if filtered_prices else None,
        "prices": prices,
        "filtered_prices": filtered_prices
    }


def ai_price_analysis(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> Dict:
    """AI 深度估价分析"""
    # 准备数据（限制数量以避免 Token 过多）
    max_comparables = 20
    selected_comparables = comparable_items[:max_comparables]
    
    prompt = build_pricing_prompt(active_item, selected_comparables, stats)
    result = call_ai(prompt)
    
    return result or {}


def build_pricing_prompt(active_item: Dict, comparable_items: List[Dict], stats: Dict) -> str:
    """构建估价提示词"""
    # 简化商品数据
    active_data = {
        "itemId": active_item["itemID"],
        "title": active_item.get("title", ""),
        "currentPrice": active_item.get("price", 0),
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
            "listingType": item.get("listingType", "")
        }
        for item in comparable_items
    ]
    
    return f"""
あなたは中古電子製品の価格分析の専門家です。以下の情報を基に、商品の適正価格と購入判断を行ってください。

【分析対象商品】
{json.dumps(active_data, ensure_ascii=False, indent=2)}

【落札相場データ】（最近の類似商品）
{json.dumps(comparables_data[:20], ensure_ascii=False, indent=2)}

【統計データ】
{json.dumps(stats, ensure_ascii=False, indent=2)}

以下のJSON形式で返してください：
{{
  "estimatedMarketPrice": 推定市場価格（円）,
  "estimatedLow": 下限価格（円）,
  "estimatedHigh": 上限価格（円）,
  "maxSuggestedPurchasePrice": 推奨購入上限額（円）,
  "expectedGrossProfit": 予想粗利益（円）,
  "profitMargin": 利益率（0.0〜1.0）,
  "pricingConfidence": 価格信頼度（0.0〜1.0）,
  "riskLevel": "LOW/MEDIUM/HIGH",
  "decisionSignal": "REVIEW/AVOID/INSUFFICIENT_DATA",
  "reasons": ["理由1", "理由2"],
  "riskFactors": ["リスク要因1", "リスク要因2"],
  "comparableItemIds": ["比較可能な商品ID"]
}}

分析ルール：
1. 相場データの中央値を基準とする
2. 外れ値（IQR * 1.5以上）は除外
3. 商品状態（中古/新品/ジャンク）を考慮
4. 出品者評価が低い場合はリスク増
5. 入札数が少ない商品は参考値として扱う
6. 相場データが3件未満の場合は INSUFFICIENT_DATA
7. 利益率20%以上を推奨、10%未満は要検討
8. 必ずJSON形式のみを返してください
"""


def merge_pricing_result(stats: Dict, ai_analysis: Dict, purchase_price: int) -> Dict:
    """合并统计和AI分析结果，计算最终定价"""
    if not stats.get("is_sufficient") or not ai_analysis:
        return {
            "pricingStatus": "INSUFFICIENT_DATA",
            "pricingConfidence": 0.2,
            "reasons": ["可比数据不足"]
        }
    
    # 提取 AI 分析结果
    estimated_price = ai_analysis.get("estimatedMarketPrice", stats["filtered_median"])
    estimated_low = ai_analysis.get("estimatedLow", stats["filtered_min"])
    estimated_high = ai_analysis.get("estimatedHigh", stats["filtered_max"])
    
    # 代码计算费用
    platform_fee = estimated_price * EXPECTED_SELLING_FEE_RATE
    repair_reserve = estimated_price * DEFAULT_REPAIR_RESERVE_RATE
    risk_reserve = estimated_price * RISK_RESERVE_RATE
    shipping_cost = DEFAULT_SHIPPING_COST
    
    # 计算利润
    gross_profit = estimated_price - purchase_price
    net_profit = gross_profit - platform_fee - shipping_cost - repair_reserve - risk_reserve
    profit_margin = net_profit / estimated_price if estimated_price > 0 else 0
    
    # 建议购入价格
    max_purchase_price = int(estimated_price * (1 - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE) - DEFAULT_SHIPPING_COST)
    
    # 决策逻辑
    risk_level = ai_analysis.get("riskLevel", "MEDIUM")
    if net_profit <= 0:
        decision = "AVOID"
    elif profit_margin < 0.10:
        decision = "REVIEW"
    elif risk_level == "HIGH":
        decision = "REVIEW"
    else:
        decision = "REVIEW"  # 保守策略，始终需要人工审核
    
    return {
        "pricingStatus": "COMPLETED",
        "estimatedMarketPrice": int(estimated_price),
        "estimatedLow": int(estimated_low),
        "estimatedHigh": int(estimated_high),
        "maxSuggestedPurchasePrice": max_purchase_price,
        "expectedGrossProfit": int(gross_profit),
        "expectedNetProfit": int(net_profit),
        "profitMargin": round(profit_margin, 3),
        "pricingConfidence": ai_analysis.get("pricingConfidence", 0.7),
        "riskLevel": risk_level,
        "decisionSignal": decision,
        "reasons": ai_analysis.get("reasons", []),
        "riskFactors": ai_analysis.get("riskFactors", []),
        "comparableItemIds": ai_analysis.get("comparableItemIds", []),
        "comparableCount": stats.get("filtered_count", 0),
        "priceBreakdown": {
            "estimatedSellingPrice": int(estimated_price),
            "purchasePrice": purchase_price,
            "platformFee": int(platform_fee),
            "shippingCost": shipping_cost,
            "repairReserve": int(repair_reserve),
            "riskReserve": int(risk_reserve),
            "netProfit": int(net_profit)
        }
    }


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


# ==================== AI 调用 ====================

def call_ai(prompt: str) -> Optional[Dict]:
    """调用 AI API"""
    import urllib.request
    
    body = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "あなたは電子製品の専門家です。必ずJSON形式のみを返してください。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
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
            
            # 清理 JSON
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
            
            return json.loads(content)
            
    except Exception as e:
        logger.error(f"AI API 调用失败: {e}")
        return None


def response(status_code: int, body: Dict) -> Dict:
    """构建 Lambda 响应"""
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }
