"""
产品目录定期扫描器 - 纯调度器版本
职责：
1. 扫描 PRODUCT 表找到今天未分析的型号
2. 标记为 QUEUED
3. 异步触发 YahooAuctionAnalyzer
4. 不等待结果，不管理状态-
"""

import os
import json
import time
import random
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

import boto3
from boto3.dynamodb.conditions import Key

# ============ 环境变量 ============
TABLE_NAME = os.environ.get("TABLE_NAME", "ProductCatalog-dev")
ANALYZER_FUNCTION_NAME = os.environ.get("ANALYZER_FUNCTION_NAME", "YahooAuctionAnalyzer-dev")
MAX_MODELS_PER_RUN = int(os.environ.get("MAX_MODELS_PER_RUN", "10"))
MAX_ACTIVE_COUNT = int(os.environ.get("MAX_ACTIVE_COUNT", "20"))
MAX_CLOSED_COUNT = int(os.environ.get("MAX_CLOSED_COUNT", "50"))

# ============ 平滑控制环境变量 ============
DISPATCH_INTERVAL_SECONDS = float(os.environ.get("DISPATCH_INTERVAL_SECONDS", "0.3"))
DISPATCH_JITTER_SECONDS = float(os.environ.get("DISPATCH_JITTER_SECONDS", "0.2"))
STARTUP_JITTER_SECONDS = float(os.environ.get("STARTUP_JITTER_SECONDS", "1"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "5"))
BATCH_INTERVAL_SECONDS = float(os.environ.get("BATCH_INTERVAL_SECONDS", "1"))

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


def smooth_sleep(
    base_seconds: float,
    jitter_seconds: float = 0,
    reason: str = "smooth_control"
):
    """
    平滑控制等待。
    base_seconds: 固定等待秒数
    jitter_seconds: 随机抖动秒数，实际等待 base + [0, jitter]
    """
    if base_seconds <= 0 and jitter_seconds <= 0:
        return

    jitter = random.uniform(0, jitter_seconds) if jitter_seconds > 0 else 0
    sleep_seconds = base_seconds + jitter

    if sleep_seconds <= 0:
        return

    log("INFO", "平滑控制等待",
        reason=reason,
        base_seconds=base_seconds,
        jitter_seconds=jitter_seconds,
        actual_sleep_seconds=round(sleep_seconds, 3))

    time.sleep(sleep_seconds)


def scan_unanalyzed_products(today: str, max_models: int = MAX_MODELS_PER_RUN) -> List[Dict]:
    """
    直接扫描 PRODUCT 记录，找到今天未分析的产品。
    
    筛选条件：
    - entity_type = PRODUCT
    - status = ACTIVE
    - last_scanned_date != today（包括 None/空字符串）
    - analysis_status != QUEUED（避免重复投递）
    """
    unscanned_products = []
    last_evaluated_key = None
    total_scanned = 0
    
    log("INFO", "开始扫描未分析 PRODUCT",
        today=today,
        max_models=max_models)
    
    while True:
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
                "last_scanned_date, last_analysis_status, modified_at"
            ),
            "Limit": 100
        }
        
        if last_evaluated_key:
            scan_params["ExclusiveStartKey"] = last_evaluated_key
        
        response = table.scan(**scan_params)
        items = response.get("Items", [])
        total_scanned += response.get("ScannedCount", 0)
        
        for item in items:
            category = str(item.get("category", ""))
            brand = str(item.get("brand", ""))
            model = str(item.get("model", ""))
            product_pk = str(item.get("PK", ""))
            last_scanned_date = str(item.get("last_scanned_date", ""))
            last_analysis_status = str(item.get("last_analysis_status", ""))
            
            # 跳过无效记录
            if not category or not brand or not model or not product_pk:
                continue
            
            # 跳过今天已扫描的
            if last_scanned_date == today:
                continue
            
            # 跳过已经 QUEUED 的（避免重复投递）
            if last_analysis_status == "QUEUED":
                continue
            
            unscanned_products.append({
                "category": category,
                "brand": brand,
                "model": model,
                "product_pk": product_pk,
                "last_scanned_date": last_scanned_date,
                "last_analysis_status": last_analysis_status,
                "modified_at": str(item.get("modified_at", "")),
            })
        
        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break
    
    log("INFO", "扫描完成",
        total_scanned=total_scanned,
        unscanned_count=len(unscanned_products),
        products=[
            {
                "category": p["category"],
                "brand": p["brand"],
                "model": p["model"]
            }
            for p in unscanned_products
        ])
    
    # Scan 本身不保证顺序；统一优先处理最近修改的产品。
    unscanned_products.sort(key=lambda product: product["modified_at"], reverse=True)
    return unscanned_products[:max_models]


def mark_as_queued(product_pk: str, today: str) -> bool:
    """
    标记产品为 QUEUED 状态。
    使用 ConditionExpression 防止重复标记。
    """
    now = int(time.time())
    
    try:
        table.update_item(
            Key={
                "PK": product_pk,
                "SK": "META"
            },
            UpdateExpression="""
                SET last_analysis_status = :queued,
                    last_scanned_date = :today,
                    last_scanned_at = :now,
                    modified_index_pk = :all,
                    modified_at = :modified_at
            """,
            ConditionExpression=(
                "attribute_not_exists(last_analysis_status) "
                "OR last_analysis_status <> :queued"
            ),
            ExpressionAttributeValues={
                ":queued": "QUEUED",
                ":today": today,
                ":now": now,
                ":all": "ALL",
                ":modified_at": datetime.now(timezone.utc).isoformat()
            }
        )
        return True
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        log("DEBUG", "产品已标记为 QUEUED，跳过",
            product_pk=product_pk)
        return False
    except Exception as e:
        log("ERROR", "标记 QUEUED 失败",
            product_pk=product_pk,
            error=str(e))
        return False


def dispatch_to_analyzer(
    category: str,
    brand: str,
    model: str,
    product_pk: str,
    max_active: int = 20,
    max_closed: int = 50
) -> bool:
    """
    异步触发 Analyzer Lambda。
    使用 InvocationType="Event" 实现真正的异步调用。
    """
    keyword = f"{brand} {model}"
    
    payload = {
        "keyword": keyword,
        "category": category,
        "brand": brand,
        "model": model,
        "product_pk": product_pk,  # 传给 Analyzer，让它自己更新状态
        "active_count": max_active,
        "closed_count": max_closed,
        "force_reprocess": False,
        "source": "catalog_scanner"  # 标记来源
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=ANALYZER_FUNCTION_NAME,
            InvocationType="Event",  # 异步调用，不等待结果
            Payload=json.dumps(payload, ensure_ascii=False)
        )
        
        log("INFO", "已投递到 Analyzer",
            category=category,
            brand=brand,
            model=model,
            product_pk=product_pk,
            status_code=response.get("StatusCode"))
        
        return response.get("StatusCode") in (200, 202)
        
    except Exception as e:
        log("ERROR", "投递失败",
            category=category,
            brand=brand,
            model=model,
            error=str(e))
        return False


def scan_and_dispatch(event: Dict) -> Dict:
    """
    主流程：扫描 → 标记 → 平滑投递
    """
    today = get_today_date()
    max_models = int(event.get("max_models", MAX_MODELS_PER_RUN))
    max_active = int(event.get("max_active", MAX_ACTIVE_COUNT))
    max_closed = int(event.get("max_closed", MAX_CLOSED_COUNT))

    # 允许手动触发时覆盖平滑参数
    dispatch_interval = float(event.get("dispatch_interval_seconds", DISPATCH_INTERVAL_SECONDS))
    dispatch_jitter = float(event.get("dispatch_jitter_seconds", DISPATCH_JITTER_SECONDS))
    batch_size = int(event.get("batch_size", BATCH_SIZE))
    batch_interval = float(event.get("batch_interval_seconds", BATCH_INTERVAL_SECONDS))

    if batch_size <= 0:
        batch_size = 1

    log("INFO", "CatalogScanner 开始执行",
        today=today,
        max_models=max_models,
        max_active=max_active,
        max_closed=max_closed,
        dispatch_interval_seconds=dispatch_interval,
        dispatch_jitter_seconds=dispatch_jitter,
        batch_size=batch_size,
        batch_interval_seconds=batch_interval)

    # 1. 扫描未分析产品
    products = scan_unanalyzed_products(
        today=today,
        max_models=max_models
    )

    if not products:
        log("INFO", "没有需要分析的产品", today=today)
        return {
            "status": "NO_PRODUCTS_TO_SCAN",
            "today": today,
            "dispatched": 0,
            "results": []
        }

    # 2. 标记 QUEUED 并平滑投递
    results = []
    dispatched = 0
    skipped = 0
    failed = 0

    for index, product in enumerate(products):
        category = product["category"]
        brand = product["brand"]
        model = product["model"]
        product_pk = product["product_pk"]

        # 批次间隔控制
        if index > 0 and index % batch_size == 0 and batch_interval > 0:
            smooth_sleep(
                base_seconds=batch_interval,
                jitter_seconds=dispatch_jitter,
                reason="batch_interval"
            )

        # 单个投递间隔控制
        # 第一个产品不等待，第二个开始等待
        if index > 0:
            smooth_sleep(
                base_seconds=dispatch_interval,
                jitter_seconds=dispatch_jitter,
                reason="dispatch_interval"
            )

        # 先标记 QUEUED
        if not mark_as_queued(product_pk, today):
            skipped += 1
            results.append({
                "category": category,
                "brand": brand,
                "model": model,
                "status": "SKIPPED",
                "reason": "ALREADY_QUEUED"
            })
            continue

        # 再投递到 Analyzer
        success = dispatch_to_analyzer(
            category=category,
            brand=brand,
            model=model,
            product_pk=product_pk,
            max_active=max_active,
            max_closed=max_closed
        )

        if success:
            dispatched += 1
            results.append({
                "category": category,
                "brand": brand,
                "model": model,
                "status": "DISPATCHED"
            })
        else:
            failed += 1
            results.append({
                "category": category,
                "brand": brand,
                "model": model,
                "status": "FAILED",
                "reason": "INVOKE_FAILED"
            })

    summary = {
        "status": "COMPLETED",
        "today": today,
        "total_found": len(products),
        "dispatched": dispatched,
        "skipped": skipped,
        "failed": failed,
        "smooth_control": {
            "dispatch_interval_seconds": dispatch_interval,
            "dispatch_jitter_seconds": dispatch_jitter,
            "batch_size": batch_size,
            "batch_interval_seconds": batch_interval
        },
        "results": results
    }

    log("INFO", "CatalogScanner 执行完成", **summary)
    return summary


def lambda_handler(event, context):
    """
    Lambda 入口函数
    
    支持 CloudWatch Events 定时触发和手动触发。
    定时任务的启停由 EventBridge 规则的 State 统一控制。
    """
    try:
        log("INFO", "Lambda 执行开始", source=event.get("source", "manual"))
        
        # 启动错峰：避免多个定时任务或重试实例同时投递
        startup_jitter = float(event.get("startup_jitter_seconds", STARTUP_JITTER_SECONDS))

        if startup_jitter > 0:
            smooth_sleep(
                base_seconds=0,
                jitter_seconds=startup_jitter,
                reason="startup_jitter"
            )

        result = scan_and_dispatch(event)
        
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
