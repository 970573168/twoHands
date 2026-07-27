"""
产品目录定期扫描器 - 优化版
支持两种扫描模式：
1. 目录树遍历：CATEGORY → BRAND → MODEL → PRODUCT（兼容旧版）
2. 直接扫描 PRODUCT（推荐，效率更高）
"""

import os
import json
import time
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key, Attr

# ============ 环境变量 ============
TABLE_NAME = os.environ.get("TABLE_NAME", "ProductCatalog-dev")
ANALYZER_FUNCTION_NAME = os.environ.get("ANALYZER_FUNCTION_NAME", "YahooAuctionAnalyzer-dev")
SCAN_INTERVAL_MINUTES = int(os.environ.get("SCAN_INTERVAL_MINUTES", "120"))
MAX_MODELS_PER_RUN = int(os.environ.get("MAX_MODELS_PER_RUN", "3"))
MAX_ACTIVE_COUNT = int(os.environ.get("MAX_ACTIVE_COUNT", "20"))
MAX_CLOSED_COUNT = int(os.environ.get("MAX_CLOSED_COUNT", "50"))
TODAY_TAG_KEY = os.environ.get("TODAY_TAG_KEY", "last_scanned_date")
ENABLE_SCHEDULED_SCAN = os.environ.get("ENABLE_SCHEDULED_SCAN", "false").lower() == "true"

# 扫描模式：direct（直接扫描 PRODUCT）或 tree（目录树遍历）
SCAN_MODE = os.environ.get("SCAN_MODE", "direct")

# 数据来源标识
DATA_SOURCE = os.environ.get("DATA_SOURCE", "AI_DISCOVERY")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
lambda_client = boto3.client("lambda")


def log(level: str, message: str, **fields):
    """结构化日志"""
    entry = {
        "level": level,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **fields
    }
    print(json.dumps(entry, ensure_ascii=False, default=str))


def normalize_for_key(value: str) -> str:
    """标准化用于 DynamoDB 键的值"""
    value = str(value or "").strip().upper()
    value = value.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
    ))
    value = re.sub(r"[^A-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+", "-", value)
    return value.strip("-")[:180]


def get_today_date() -> str:
    """获取今天的日期字符串（JST）"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y-%m-%d")


# ============================================
# 模式 1：直接扫描 PRODUCT（推荐）
# ============================================

def scan_products_directly(
    today: str,
    max_models: int = 3
) -> List[Dict]:
    """
    直接扫描 PRODUCT 记录，找到今天未分析的产品。
    
    优势：
    - 一次 Scan 即可找到所有待分析产品
    - 不需要遍历 CATEGORY → BRAND → MODEL
    - 读取次数少，速度快
    
    DynamoDB 查询逻辑：
    1. Scan 所有 entity_type=PRODUCT AND status=ACTIVE 的记录
    2. 过滤 last_scanned_date != today 或 last_scanned_date 不存在
    3. 按 last_scanned_at 升序（最久未分析的优先）
    """
    unscanned_products = []
    last_evaluated_key = None
    total_scanned = 0
    page_number = 0
    
    log("INFO", "开始直接扫描 PRODUCT 记录",
        today=today,
        max_models=max_models,
        scan_mode="direct")
    
    while len(unscanned_products) < max_models:
        page_number += 1
        
        scan_params = {
            "FilterExpression": (
                "entity_type = :entity_type "
                "AND #status = :status"
            ),
            "ExpressionAttributeNames": {
                "#status": "status"
            },
            "ExpressionAttributeValues": {
                ":entity_type": "PRODUCT",
                ":status": "ACTIVE"
            },
            "ProjectionExpression": (
                "PK, category, brand, model, "
                "last_scanned_date, last_scanned_at, "
                "last_analysis_status, release_date, confidence"
            ),
            "Limit": 100
        }
        
        if last_evaluated_key:
            scan_params["ExclusiveStartKey"] = last_evaluated_key
        
        try:
            response = table.scan(**scan_params)
        except Exception as e:
            log("WARN", "带投影的扫描失败，尝试完整扫描", error=str(e))
            scan_params.pop("ProjectionExpression", None)
            response = table.scan(**scan_params)
        
        items = response.get("Items", [])
        scanned_count = response.get("ScannedCount", 0)
        total_scanned += scanned_count
        
        log("INFO", "扫描 PRODUCT 分页",
            page=page_number,
            scanned_count=scanned_count,
            matched_count=response.get("Count", 0),
            total_scanned=total_scanned,
            candidates_found=len(unscanned_products))
        
        for item in items:
            if len(unscanned_products) >= max_models:
                break
            
            # 提取产品信息
            category = item.get("category", "")
            brand = item.get("brand", "")
            model = item.get("model", "")
            product_pk = item.get("PK", "")
            last_scanned_date = item.get("last_scanned_date", "")
            last_scanned_at = item.get("last_scanned_at", 0)
            last_analysis_status = item.get("last_analysis_status", "")
            
            # 跳过无效记录
            if not category or not brand or not model:
                continue
            
            # 检查是否今天已扫描
            if last_scanned_date == today:
                log("DEBUG", "产品今天已扫描，跳过",
                    category=category,
                    brand=brand,
                    model=model,
                    last_scanned_date=last_scanned_date)
                continue
            
            unscanned_products.append({
                "category": str(category),
                "brand": str(brand),
                "model": str(model),
                "product_pk": str(product_pk),
                "last_scanned_date": str(last_scanned_date) if last_scanned_date else "",
                "last_scanned_at": int(last_scanned_at) if last_scanned_at else 0,
                "last_analysis_status": str(last_analysis_status) if last_analysis_status else "NEVER_SCANNED",
                "release_date": str(item.get("release_date", "")),
                "confidence": str(item.get("confidence", ""))
            })
        
        last_evaluated_key = response.get("LastEvaluatedKey")
        
        if not last_evaluated_key:
            break
    
    # 按最久未扫描排序（last_scanned_at 升序，从未扫描的排最前）
    unscanned_products.sort(key=lambda x: x.get("last_scanned_at", 0))
    
    log("INFO", "直接扫描 PRODUCT 完成",
        total_products_scanned=total_scanned,
        unscanned_count=len(unscanned_products),
        models=[
            {
                "category": p["category"],
                "brand": p["brand"],
                "model": p["model"],
                "last_scanned": p["last_scanned_date"] or "never"
            }
            for p in unscanned_products
        ])
    
    return unscanned_products[:max_models]


# ============================================
# 模式 2：目录树遍历（兼容旧版）
# ============================================

def scan_active_categories(max_categories: int = 20) -> List[str]:
    """分页扫描 ACTIVE 状态的 CATEGORY 记录"""
    categories = []
    last_evaluated_key = None
    total_scanned = 0
    page_number = 0
    
    while len(categories) < max_categories:
        page_number += 1
        
        scan_params = {
            "FilterExpression": "entity_type = :entity_type AND #status = :status",
            "ExpressionAttributeNames": {"#status": "status", "#name": "name"},
            "ExpressionAttributeValues": {
                ":entity_type": "CATEGORY",
                ":status": "ACTIVE"
            },
            "ProjectionExpression": "PK, SK, #name, entity_type, #status",
            "Limit": 100
        }
        
        if last_evaluated_key:
            scan_params["ExclusiveStartKey"] = last_evaluated_key
        
        try:
            response = table.scan(**scan_params)
        except Exception as e:
            log("WARN", "带投影的扫描失败，尝试完整扫描", error=str(e))
            scan_params.pop("ProjectionExpression", None)
            response = table.scan(**scan_params)
        
        items = response.get("Items", [])
        scanned_count = response.get("ScannedCount", 0)
        total_scanned += scanned_count
        
        for item in items:
            category_name = item.get("name")
            if category_name:
                category_name = str(category_name).strip()
                if category_name and category_name not in categories:
                    categories.append(category_name)
            if len(categories) >= max_categories:
                break
        
        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break
    
    log("INFO", "分类扫描完成",
        category_count=len(categories),
        categories=categories,
        total_scanned=total_scanned,
        pages=page_number)
    
    return categories[:max_categories]


def query_catalog_brands(category: str, limit: int = 10) -> List[Dict]:
    """查询指定品类下的所有品牌"""
    try:
        category_key = normalize_for_key(category)
        
        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"CATEGORY#{category_key}"),
            FilterExpression="entity_type = :entity_type AND #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":entity_type": "BRAND",
                ":status": "ACTIVE"
            },
            Limit=limit
        )
        
        brands = []
        for item in response.get("Items", []):
            brand_name = item.get("brand")
            if brand_name:
                brands.append({
                    "category": category,
                    "brand": brand_name,
                    "last_scanned_date": item.get("last_scanned_date", ""),
                    "last_scanned_at": item.get("last_scanned_at", 0)
                })
        
        return brands
    except Exception as e:
        log("ERROR", "查询品类品牌失败", category=category, error=str(e))
        return []


def get_product_scan_state(product_pk: str) -> Dict:
    """从 PRODUCT#... / META 记录读取扫描状态"""
    if not product_pk:
        return {}
    
    try:
        response = table.get_item(
            Key={"PK": product_pk, "SK": "META"},
            ProjectionExpression="last_scanned_date, last_scanned_at, last_analysis_status"
        )
        return response.get("Item", {})
    except Exception as e:
        log("ERROR", "读取产品扫描状态失败", product_pk=product_pk, error=str(e))
        return {}


def query_catalog_products(category: str, brand: str, limit: int = 5) -> List[Dict]:
    """查询指定品类和品牌下的产品型号"""
    try:
        brand_key = normalize_for_key(brand)
        
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
            FilterExpression="entity_type = :entity_type AND category = :category",
            ExpressionAttributeValues={
                ":entity_type": "BRAND_MODEL",
                ":category": category
            },
            Limit=limit,
            ScanIndexForward=False
        )
        
        products = []
        for item in response.get("Items", []):
            model = item.get("model")
            product_pk = item.get("product_pk", "")
            
            if not model:
                continue
            
            product_state = get_product_scan_state(product_pk)
            
            products.append({
                "category": category,
                "brand": brand,
                "model": model,
                "product_pk": product_pk,
                "last_scanned_date": product_state.get("last_scanned_date", ""),
                "last_scanned_at": product_state.get("last_scanned_at"),
                "last_analysis_status": product_state.get("last_analysis_status", ""),
                "release_date": item.get("release_date", "")
            })
        
        return products
    except Exception as e:
        log("ERROR", "查询产品型号失败", category=category, brand=brand, error=str(e))
        return []


def scan_categories_for_unscanned_models(
    today: str,
    max_models: int = 3,
    max_categories: int = 20
) -> List[Dict]:
    """目录树遍历方式扫描未分析的型号"""
    try:
        categories = scan_active_categories(max_categories=max_categories)
        
        if not categories:
            log("WARN", "没有发现 ACTIVE 分类记录", table=TABLE_NAME)
            return []
        
        unscanned_models = []
        
        for category in categories:
            if len(unscanned_models) >= max_models:
                break
            
            brands = query_catalog_brands(category, limit=10)
            
            for brand_info in brands:
                if len(unscanned_models) >= max_models:
                    break
                
                products = query_catalog_products(
                    category=brand_info["category"],
                    brand=brand_info["brand"],
                    limit=5
                )
                
                for product in products:
                    if len(unscanned_models) >= max_models:
                        break
                    
                    if product.get("last_scanned_date") == today:
                        continue
                    
                    unscanned_models.append(product)
        
        log("INFO", "找到未扫描型号",
            count=len(unscanned_models),
            models=[
                {
                    "category": item.get("category"),
                    "brand": item.get("brand"),
                    "model": item.get("model")
                }
                for item in unscanned_models
            ])
        
        return unscanned_models
        
    except Exception as e:
        log("ERROR", "扫描品类失败", error_type=type(e).__name__, error=str(e))
        return []


# ============================================
# 共同函数
# ============================================

def invoke_analyzer_for_model(
    category: str,
    brand: str,
    model: str,
    max_active: int = 20,
    max_closed: int = 50
) -> Dict:
    """调用分析器 Lambda 分析指定型号"""
    keyword = f"{brand} {model}"
    
    payload = {
        "keyword": keyword,
        "category": category,
        "brand": brand,
        "model": model,
        "active_count": max_active,
        "closed_count": max_closed,
        "force_reprocess": False
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=ANALYZER_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload, ensure_ascii=False)
        )
        
        response_payload = json.loads(response["Payload"].read().decode("utf-8"))
        
        log("INFO", "分析器调用成功",
            category=category,
            brand=brand,
            model=model,
            status_code=response.get("StatusCode"))
        
        return {
            "success": True,
            "response": response_payload
        }
        
    except Exception as e:
        log("ERROR", "分析器调用失败",
            category=category,
            brand=brand,
            model=model,
            error=str(e))
        
        return {
            "success": False,
            "error": str(e)
        }


def update_scan_timestamp(
    product_pk: str,
    category: str,
    brand: str,
    today: str,
    analysis_status: str = "SCANNED"
):
    """更新产品扫描时间戳"""
    now = int(time.time())
    category_key = normalize_for_key(category)
    brand_key = normalize_for_key(brand)
    
    try:
        # 更新产品记录
        if product_pk:
            table.update_item(
                Key={"PK": product_pk, "SK": "META"},
                UpdateExpression="""
                    SET last_scanned_date = :today,
                        last_scanned_at = :now,
                        last_analysis_status = :status
                """,
                ExpressionAttributeValues={
                    ":today": today,
                    ":now": now,
                    ":status": analysis_status
                }
            )
        
        # 更新品牌记录
        table.update_item(
            Key={
                "PK": f"CATEGORY#{category_key}",
                "SK": f"BRAND#{brand_key}"
            },
            UpdateExpression="""
                SET last_scanned_date = :today,
                    last_scanned_at = :now
            """,
            ExpressionAttributeValues={
                ":today": today,
                ":now": now
            }
        )
        
        log("DEBUG", "更新时间戳完成",
            product_pk=product_pk,
            category=category,
            brand=brand)
            
    except Exception as e:
        log("ERROR", "更新时间戳失败",
            product_pk=product_pk,
            error=str(e))


def scan_and_analyze(event: Dict) -> Dict:
    """
    主扫描和分析流程
    
    支持两种模式：
    - direct: 直接扫描 PRODUCT 记录（推荐）
    - tree: 目录树遍历 CATEGORY → BRAND → MODEL → PRODUCT
    """
    today = get_today_date()
    max_models = int(event.get("max_models", MAX_MODELS_PER_RUN))
    max_active = int(event.get("max_active", MAX_ACTIVE_COUNT))
    max_closed = int(event.get("max_closed", MAX_CLOSED_COUNT))
    
    # 确定扫描模式
    scan_mode = event.get("scan_mode", SCAN_MODE)
    
    log("INFO", "开始定期扫描", 
        today=today, 
        max_models=max_models,
        max_active=max_active,
        max_closed=max_closed,
        scan_mode=scan_mode)
    
    # 根据模式选择扫描方法
    if scan_mode == "direct":
        unscanned_models = scan_products_directly(
            today=today,
            max_models=max_models
        )
    else:
        unscanned_models = scan_categories_for_unscanned_models(
            today=today,
            max_models=max_models
        )
    
    if not unscanned_models:
        log("INFO", "没有需要扫描的型号", today=today)
        return {
            "status": "NO_MODELS_TO_SCAN",
            "today": today,
            "scanned_count": 0,
            "scan_mode": scan_mode,
            "results": []
        }
    
    # 逐个发送到分析器
    results = []
    success_count = 0
    fail_count = 0
    
    for model_info in unscanned_models:
        category = model_info["category"]
        brand = model_info["brand"]
        model = model_info["model"]
        product_pk = model_info.get("product_pk", "")
        
        log("INFO", "开始分析型号",
            category=category,
            brand=brand,
            model=model,
            last_scanned=model_info.get("last_scanned_date") or "never",
            last_status=model_info.get("last_analysis_status", "UNKNOWN"))
        
        # 调用分析器
        result = invoke_analyzer_for_model(
            category=category,
            brand=brand,
            model=model,
            max_active=max_active,
            max_closed=max_closed
        )
        
        # 确定分析状态
        if result["success"]:
            analysis_status = "COMPLETED"
            success_count += 1
        else:
            analysis_status = "FAILED"
            fail_count += 1
        
        # 更新扫描时间戳
        update_scan_timestamp(
            product_pk=product_pk,
            category=category,
            brand=brand,
            today=today,
            analysis_status=analysis_status
        )
        
        results.append({
            "category": category,
            "brand": brand,
            "model": model,
            "product_pk": product_pk,
            "success": result["success"],
            "status": analysis_status,
            "error": result.get("error")
        })
        
        # 避免过快调用
        if len(unscanned_models) > 1:
            time.sleep(2)
    
    summary = {
        "status": "COMPLETED",
        "today": today,
        "scan_mode": scan_mode,
        "scanned_count": len(unscanned_models),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results
    }
    
    log("INFO", "扫描完成", **summary)
    return summary


def lambda_handler(event, context):
    """
    Lambda 入口函数
    
    支持的事件格式：
    
    1. CloudWatch Events 定时触发:
       {"source": "aws.events", "max_models": 3}
    
    2. 手动触发 - direct 模式:
       {"source": "manual", "scan_mode": "direct", "max_models": 5}
    
    3. 手动触发 - tree 模式:
       {"source": "manual", "scan_mode": "tree", "max_models": 3, "max_categories": 10}
    """
    try:
        # 检查是否启用了定时扫描
        if not ENABLE_SCHEDULED_SCAN:
            if event.get("source") != "aws.events":
                log("INFO", "定时扫描已禁用，但收到手动触发请求")
            else:
                log("INFO", "定时扫描已禁用，跳过执行")
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": "定时扫描已禁用",
                        "enable_scheduled_scan": False
                    }, ensure_ascii=False)
                }
        
        scan_mode = event.get("scan_mode", SCAN_MODE)
        
        log("INFO", "Lambda 执行开始",
            event=event,
            enable_scheduled_scan=ENABLE_SCHEDULED_SCAN,
            scan_mode=scan_mode,
            scan_interval_minutes=SCAN_INTERVAL_MINUTES)
        
        result = scan_and_analyze(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False, default=str)
        }
        
    except Exception as e:
        log("ERROR", "执行失败", error=str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "内部错误",
                "details": str(e)
            }, ensure_ascii=False)
        }
