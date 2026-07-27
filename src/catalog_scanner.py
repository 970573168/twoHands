"""
产品目录定期扫描器
定期扫描 ProductCatalog 表，找到符合条件的品牌/型号组合，
发送到 YahooAuctionAnalyzer 进行分析
"""

import os
import json
import time
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Set, Tuple
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

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


def diagnose_category_records():
    """诊断分类记录（临时调试用）"""
    try:
        response = table.scan(
            ProjectionExpression="PK, SK, entity_type, #name, #status",
            ExpressionAttributeNames={
                "#name": "name",
                "#status": "status"
            },
            Limit=50
        )
        
        items = response.get("Items", [])
        
        log("INFO", "分类记录诊断",
            table=TABLE_NAME,
            count=len(items),
            scanned_count=response.get("ScannedCount", 0),
            items=items[:10])  # 只显示前10条
        
        # 统计不同类型的记录
        type_counts = {}
        for item in items:
            entity_type = item.get("entity_type", "UNKNOWN")
            status = item.get("status", "UNKNOWN")
            key = f"{entity_type}/{status}"
            type_counts[key] = type_counts.get(key, 0) + 1
        
        log("INFO", "记录类型统计", type_counts=type_counts)
        
    except Exception as e:
        log("ERROR", "诊断分类记录失败", error=str(e))


def scan_active_categories(max_categories: int = 20) -> List[str]:
    """
    分页扫描 ACTIVE 状态的 CATEGORY 记录。
    
    DynamoDB Scan 的 Limit 是过滤前的最大评估条目数，
    因此必须处理 LastEvaluatedKey 进行分页扫描。
    """
    categories = []
    last_evaluated_key = None
    total_scanned = 0
    page_number = 0
    
    while len(categories) < max_categories:
        page_number += 1
        
        scan_params = {
            "FilterExpression": "entity_type = :entity_type AND #status = :status",
            "ExpressionAttributeNames": {
                "#status": "status"
            },
            "ExpressionAttributeValues": {
                ":entity_type": "CATEGORY",
                ":status": "ACTIVE"
            },
            "ProjectionExpression": "PK, SK, #name, entity_type, #status",
            "Limit": 100
        }
        
        scan_params["ExpressionAttributeNames"]["#name"] = "name"
        
        if last_evaluated_key:
            scan_params["ExclusiveStartKey"] = last_evaluated_key
        
        try:
            response = table.scan(**scan_params)
        except Exception as e:
            # 如果 ProjectionExpression 包含不存在的字段，尝试简化查询
            log("WARN", "带投影的扫描失败，尝试完整扫描", error=str(e))
            scan_params.pop("ProjectionExpression", None)
            scan_params["ExpressionAttributeNames"]["#name"] = "name"
            response = table.scan(**scan_params)
        
        items = response.get("Items", [])
        scanned_count = response.get("ScannedCount", 0)
        total_scanned += scanned_count
        
        log("INFO", "扫描分类分页",
            page=page_number,
            scanned_count=scanned_count,
            matched_count=response.get("Count", 0),
            total_scanned=total_scanned,
            has_more=bool(response.get("LastEvaluatedKey")))
        
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
                    "last_scanned_at": item.get("last_scanned_at", 0)
                })
        
        return brands
    except Exception as e:
        log("ERROR", "查询品类品牌失败", category=category, error=str(e))
        return []


def get_product_scan_state(product_pk: str) -> Dict:
    """
    从 PRODUCT#... / META 记录读取扫描状态
    
    Args:
        product_pk: 产品主键
        
    Returns:
        产品的扫描状态信息
    """
    if not product_pk:
        return {}
    
    try:
        response = table.get_item(
            Key={
                "PK": product_pk,
                "SK": "META"
            },
            ProjectionExpression="last_scanned_date, last_scanned_at, last_analysis_status"
        )
        
        return response.get("Item", {})
        
    except Exception as e:
        log("ERROR", "读取产品扫描状态失败",
            product_pk=product_pk,
            error=str(e))
        return {}


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
            product_pk = item.get("product_pk", "")
            
            if not model:
                continue
            
            # 从正式的 PRODUCT 记录读取扫描状态
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
    """
    扫描所有品类，找到今天尚未成功扫描的型号。
    使用分页扫描确保能找到所有 ACTIVE 分类。
    """
    try:
        # 使用分页扫描获取所有 ACTIVE 分类
        categories = scan_active_categories(max_categories=max_categories)
        
        log("INFO", "扫描品类",
            count=len(categories),
            categories=categories)
        
        if not categories:
            log("WARN", "没有发现 ACTIVE 分类记录",
                table=TABLE_NAME)
            return []
        
        unscanned_models = []
        
        for category in categories:
            if len(unscanned_models) >= max_models:
                break
            
            # 获取该品类下的品牌
            brands = query_catalog_brands(category, limit=10)
            
            log("INFO", "查询分类品牌完成",
                category=category,
                brand_count=len(brands))
            
            for brand_info in brands:
                if len(unscanned_models) >= max_models:
                    break
                
                # 获取该品牌下的产品型号
                products = query_catalog_products(
                    category=brand_info["category"],
                    brand=brand_info["brand"],
                    limit=5
                )
                
                log("INFO", "查询品牌型号完成",
                    category=category,
                    brand=brand_info["brand"],
                    product_count=len(products))
                
                for product in products:
                    if len(unscanned_models) >= max_models:
                        break
                    
                    # 检查型号今天是否已经扫描过（从正式 PRODUCT 记录读取）
                    if product.get("last_scanned_date") == today:
                        log("DEBUG", "型号今天已扫描，跳过",
                            category=product["category"],
                            brand=product["brand"],
                            model=product["model"],
                            last_scanned_date=product["last_scanned_date"])
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
        log("ERROR", "扫描品类失败",
            error_type=type(e).__name__,
            error=str(e))
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
    更新产品和品牌的扫描时间戳
    
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
        # 更新产品记录（PRODUCT#... / META）
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
            
            log("DEBUG", "更新产品扫描时间戳",
                product_pk=product_pk,
                today=today,
                status=analysis_status)
        
        # 更新品牌记录（CATEGORY#... / BRAND#...）
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
        
        log("DEBUG", "更新品牌扫描时间戳",
            category=category,
            brand=brand,
            today=today)
            
    except Exception as e:
        log("ERROR", "更新时间戳失败",
            product_pk=product_pk,
            category=category,
            brand=brand,
            error=str(e))


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
            # 尝试从响应中提取状态
            try:
                response_body = result["response"]
                if isinstance(response_body, dict):
                    if "body" in response_body:
                        body = json.loads(response_body["body"]) if isinstance(response_body["body"], str) else response_body["body"]
                        analysis_status = body.get("status", "COMPLETED")
                    else:
                        analysis_status = response_body.get("status", "COMPLETED")
                else:
                    analysis_status = "COMPLETED"
            except:
                analysis_status = "COMPLETED"
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
        
        # 临时诊断：检查表中的记录类型
        diagnose_category_records()
        
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
