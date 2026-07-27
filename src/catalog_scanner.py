"""
产品目录定期扫描器
定期扫描 ProductCatalog 表，找到符合条件的品牌/型号组合，
发送到 YahooAuctionAnalyzer 进行分析
"""

import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Set, Tuple
from decimal import Decimal

import boto3

# ============ 环境变量 ============
TABLE_NAME = os.environ.get("TABLE_NAME", "ProductCatalog-dev")
ANALYZER_FUNCTION_NAME = os.environ.get("ANALYZER_FUNCTION_NAME", "YahooAuctionAnalyzer-dev")
SCAN_INTERVAL_MINUTES = int(os.environ.get("SCAN_INTERVAL_MINUTES", "120"))  # 默认2小时
MAX_MODELS_PER_RUN = int(os.environ.get("MAX_MODELS_PER_RUN", "3"))
MAX_ACTIVE_COUNT = int(os.environ.get("MAX_ACTIVE_COUNT", "20"))
MAX_CLOSED_COUNT = int(os.environ.get("MAX_CLOSED_COUNT", "50"))
TODAY_TAG_KEY = os.environ.get("TODAY_TAG_KEY", "last_scanned_date")
ENABLE_SCHEDULED_SCAN = os.environ.get("ENABLE_SCHEDULED_SCAN", "false").lower() == "true"

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


def get_today_date() -> str:
    """获取今天的日期字符串（JST）"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y-%m-%d")


def query_catalog_brands(category: str, limit: int = 10) -> List[Dict]:
    """
    查询指定品类下的所有品牌
    
    Args:
        category: 品类名称
        limit: 最大返回数量
        
    Returns:
        品牌列表
    """
    try:
        category_key = normalize_for_key(category)
        
        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"CATEGORY#{category_key}"),
            FilterExpression="entity_type = :entity_type AND #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
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
                    "last_analysis_date": item.get("last_analysis_date", "")
                })
        
        return brands
    except Exception as e:
        log("ERROR", "查询品类品牌失败", category=category, error=str(e))
        return []


def query_catalog_products(
    category: str,
    brand: str,
    limit: int = 5
) -> List[Dict]:
    """
    查询指定品类和品牌下的产品型号
    
    Args:
        category: 品类名称
        brand: 品牌名称
        limit: 最大返回数量
        
    Returns:
        产品型号列表
    """
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
            ScanIndexForward=False  # 最新的在前
        )
        
        products = []
        for item in response.get("Items", []):
            model = item.get("model")
            if model:
                products.append({
                    "category": category,
                    "brand": brand,
                    "model": model,
                    "product_pk": item.get("product_pk", ""),
                    "last_scanned_date": item.get("last_scanned_date", ""),
                    "last_analysis_date": item.get("last_analysis_date", ""),
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
    """
    扫描所有品类，找到今天还没有被扫描的型号
    
    Args:
        today: 今天的日期字符串
        max_models: 最多返回的型号数量
        max_categories: 最多扫描的品类数量
        
    Returns:
        待分析的型号列表
    """
    # 先获取所有品类
    try:
        response = table.scan(
            FilterExpression="entity_type = :entity_type AND #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":entity_type": "CATEGORY",
                ":status": "ACTIVE"
            },
            Limit=max_categories
        )
        
        categories = []
        for item in response.get("Items", []):
            category_name = item.get("name")
            if category_name:
                categories.append(category_name)
        
        log("INFO", "扫描品类", count=len(categories), categories=categories)
        
        unscanned_models = []
        
        for category in categories:
            if len(unscanned_models) >= max_models:
                break
            
            # 获取该品类下的品牌
            brands = query_catalog_brands(category, limit=10)
            
            for brand_info in brands:
                if len(unscanned_models) >= max_models:
                    break
                
                # 检查品牌今天是否已经扫描过
                if brand_info.get("last_scanned_date") == today:
                    continue
                
                # 获取该品牌下的产品型号
                products = query_catalog_products(
                    category=brand_info["category"],
                    brand=brand_info["brand"],
                    limit=5
                )
                
                for product in products:
                    if len(unscanned_models) >= max_models:
                        break
                    
                    # 检查型号今天是否已经分析过
                    if product.get("last_analysis_date") == today:
                        continue
                    
                    unscanned_models.append(product)
        
        log("INFO", "找到未扫描型号", count=len(unscanned_models))
        return unscanned_models
        
    except Exception as e:
        log("ERROR", "扫描品类失败", error=str(e))
        return []


def invoke_analyzer_for_model(
    category: str,
    brand: str,
    model: str,
    search_count: int = 20,
    max_active: int = 20,
    max_closed: int = 50
) -> Dict:
    """
    调用分析器 Lambda 分析指定型号
    
    Args:
        category: 品类名称
        brand: 品牌名称
        model: 型号名称
        search_count: 搜索数量
        max_active: 最大活跃商品数
        max_closed: 最大闭拍商品数
        
    Returns:
        调用结果
    """
    # 构建搜索关键词
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
            InvocationType="RequestResponse",  # 同步调用
            Payload=json.dumps(payload, ensure_ascii=False)
        )
        
        response_payload = json.loads(response["Payload"].read().decode("utf-8"))
        
        log("INFO", "分析器调用成功",
            category=category,
            brand=brand,
            model=model,
            status_code=response.get("StatusCode"),
            response=response_payload)
        
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
    """
    更新产品、品牌的扫描时间戳
    
    Args:
        product_pk: 产品主键
        category: 品类名称
        brand: 品牌名称
        today: 今天的日期
        analysis_status: 分析状态
    """
    now = int(time.time())
    category_key = normalize_for_key(category)
    brand_key = normalize_for_key(brand)
    
    try:
        # 更新产品记录
        if product_pk:
            table.update_item(
                Key={
                    "PK": product_pk,
                    "SK": "META"
                },
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
        
        log("DEBUG", "更新时间戳",
            product_pk=product_pk,
            category=category,
            brand=brand,
            today=today,
            status=analysis_status)
            
    except Exception as e:
        log("ERROR", "更新时间戳失败",
            product_pk=product_pk,
            category=category,
            brand=brand,
            error=str(e))


def normalize_for_key(value: str) -> str:
    """标准化用于 DynamoDB 键的值"""
    import re
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


def scan_and_analyze(event: Dict) -> Dict:
    """
    主扫描和分析流程
    
    Args:
        event: Lambda 事件
        
    Returns:
        执行结果
    """
    today = get_today_date()
    max_models = int(event.get("max_models", MAX_MODELS_PER_RUN))
    max_active = int(event.get("max_active", MAX_ACTIVE_COUNT))
    max_closed = int(event.get("max_closed", MAX_CLOSED_COUNT))
    
    log("INFO", "开始定期扫描", 
        today=today, 
        max_models=max_models,
        max_active=max_active,
        max_closed=max_closed)
    
    # 找到今天未扫描的型号
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
            product_pk=product_pk)
        
        # 调用分析器
        result = invoke_analyzer_for_model(
            category=category,
            brand=brand,
            model=model,
            search_count=max_active,  # 使用 max_active 作为搜索数量
            max_active=max_active,
            max_closed=max_closed
        )
        
        # 更新扫描时间戳
        if result["success"]:
            analysis_status = result["response"].get("status", "COMPLETED")
            success_count += 1
        else:
            analysis_status = "FAILED"
            fail_count += 1
        
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
    
    支持两种触发方式：
    1. 手动触发：通过 event 传递参数
    2. 定时触发：通过 CloudWatch Events 触发
    """
    try:
        # 检查是否启用了定时扫描
        if not ENABLE_SCHEDULED_SCAN:
            # 检查是否是手动触发（手动触发时允许运行）
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
        
        log("INFO", "Lambda 执行开始",
            event=event,
            enable_scheduled_scan=ENABLE_SCHEDULED_SCAN,
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
