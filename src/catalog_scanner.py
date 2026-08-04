"""倒计时目录扫描 Lambda。

支持两种模式：
1. ``configure``：修改 YahooAuctionLinks 目录记录的 active/closed 数量、扫描间隔和启停状态。
2. ``schedule``：由每分钟 EventBridge 触发，查找到期目录并异步投递 Analyzer。
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "YahooAuctionLinks-dev")
ANALYZER_FUNCTION_NAME = os.environ.get("ANALYZER_FUNCTION_NAME", "YahooAuctionAnalyzer-dev")
MAX_MODELS_PER_RUN = int(os.environ.get("MAX_MODELS_PER_RUN", "10"))
DEFAULT_ACTIVE_COUNT = int(os.environ.get("MAX_ACTIVE_COUNT", "20"))
DEFAULT_CLOSED_COUNT = int(os.environ.get("MAX_CLOSED_COUNT", "50"))
DEFAULT_INTERVAL_MINUTES = int(os.environ.get("DEFAULT_SCAN_INTERVAL_MINUTES", "180"))
LOCK_SECONDS = int(os.environ.get("SCAN_LOCK_SECONDS", "900"))

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
lambda_client = boto3.client("lambda")


def log(level: str, message: str, **fields):
    print(json.dumps({
        "level": level, "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(), **fields,
    }, ensure_ascii=False, default=str))


def _integer(value, name: str, minimum: int, maximum: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} 必须是整数") from exc
    if not minimum <= result <= maximum:
        raise ValueError(f"{name} 必须在 {minimum} 到 {maximum} 之间")
    return result


def _resolve_crawl_id(event: Dict) -> str:
    """配置接口可使用内部 crawl_id，也可直接使用用户可见的目录 ID。"""
    crawl_id = str(event.get("crawl_id", "")).strip()
    if crawl_id:
        return crawl_id
    category_id = str(event.get("category_id", "")).strip()
    if not category_id:
        raise ValueError("缺少 category_id")
    start_key = None
    while True:
        params = {
            "FilterExpression": "link_type = :directory AND category_id = :category_id",
            "ExpressionAttributeValues": {
                ":directory": "list3_directory", ":category_id": category_id,
            },
            "ProjectionExpression": "crawl_id",
            "Limit": 100,
        }
        if start_key:
            params["ExclusiveStartKey"] = start_key
        response = table.scan(**params)
        items = response.get("Items", [])
        if items:
            return str(items[0]["crawl_id"])
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            raise ValueError(f"未找到目录 ID：{category_id}")


def configure_catalog(event: Dict, now: int = None) -> Dict:
    """模式一：修改单个 YahooAuctionLinks 目录的倒计时扫描配置。"""
    crawl_id = _resolve_crawl_id(event)
    now = int(now if now is not None else time.time())
    active = _integer(event.get("active_count", DEFAULT_ACTIVE_COUNT), "active_count", 1, 1000)
    closed = _integer(event.get("closed_count", DEFAULT_CLOSED_COUNT), "closed_count", 1, 1000)
    interval = _integer(
        event.get("scan_interval_minutes", DEFAULT_INTERVAL_MINUTES),
        "scan_interval_minutes", 1, 10080,
    )
    enabled = event.get("scan_enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("scan_enabled 必须是布尔值")

    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression=(
            "SET countdown_active_count = :active, countdown_closed_count = :closed, "
            "countdown_interval_minutes = :interval, countdown_scan_enabled = :enabled, "
            "countdown_next_scan_at = :next, updated_at = :modified "
            "REMOVE countdown_scan_lock_until"
        ),
        ConditionExpression="attribute_exists(category_id)",
        ExpressionAttributeValues={
            ":active": active, ":closed": closed, ":interval": interval,
            ":enabled": enabled, ":next": now if enabled else 0,
            ":modified": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {
        "状态": "配置已更新", "目录记录ID": crawl_id, "是否开启扫描": enabled,
        "active数量": active, "closed数量": closed, "扫描间隔分钟": interval,
    }


def find_due_catalogs(now: int, limit: int = MAX_MODELS_PER_RUN) -> List[Dict]:
    """遍历 YahooAuctionLinks，返回已开启且到达下次扫描时间的目录。"""
    due, start_key = [], None
    while len(due) < limit:
        params = {
            "FilterExpression": (
                "link_type = :directory AND attribute_exists(category_id) "
                "AND countdown_scan_enabled = :enabled "
                "AND (attribute_not_exists(countdown_next_scan_at) OR countdown_next_scan_at <= :now)"
            ),
            "ExpressionAttributeValues": {
                ":directory": "list3_directory", ":enabled": True, ":now": now,
            },
            "ProjectionExpression": (
                "crawl_id, category_id, category_name, countdown_active_count, "
                "countdown_closed_count, countdown_interval_minutes, countdown_next_scan_at"
            ),
            "Limit": 100,
        }
        if start_key:
            params["ExclusiveStartKey"] = start_key
        response = table.scan(**params)
        due.extend(response.get("Items", []))
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
    due.sort(key=lambda item: int(item.get("countdown_next_scan_at", 0)))
    return due[:limit]


def claim_catalog(item: Dict, now: int) -> bool:
    """原子抢占到期目录，避免每分钟调度、重试或并发实例重复投递。"""
    interval = _integer(
        item.get("countdown_interval_minutes", DEFAULT_INTERVAL_MINUTES),
        "countdown_interval_minutes", 1, 10080,
    )
    try:
        lock_until = now + min(LOCK_SECONDS, max(30, interval * 60 - 1))
        table.update_item(
            Key={"crawl_id": str(item["crawl_id"])},
            UpdateExpression=(
                "SET countdown_scan_lock_until = :lock, countdown_last_scan_at = :now, "
                "countdown_next_scan_at = :next, last_analysis_status = :queued"
            ),
            ConditionExpression=(
                "countdown_scan_enabled = :enabled "
                "AND (attribute_not_exists(countdown_next_scan_at) OR countdown_next_scan_at <= :now) "
                "AND (attribute_not_exists(countdown_scan_lock_until) OR countdown_scan_lock_until < :now)"
            ),
            ExpressionAttributeValues={
                ":enabled": True, ":now": now, ":lock": lock_until,
                ":next": now + interval * 60, ":queued": "QUEUED",
            },
        )
        return True
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return False


def dispatch_to_analyzer(item: Dict) -> bool:
    payload = {
        "mode": "countdown", "source": "countdown_catalog_scanner",
        "category_id": str(item["category_id"]),
        "active_count": int(item.get("countdown_active_count", DEFAULT_ACTIVE_COUNT)),
        "closed_count": int(item.get("countdown_closed_count", DEFAULT_CLOSED_COUNT)),
        "force_reprocess": False,
    }
    response = lambda_client.invoke(
        FunctionName=ANALYZER_FUNCTION_NAME, InvocationType="Event",
        Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
    return response.get("StatusCode") == 202


def mark_dispatch_failed(crawl_id: str, now: int):
    """投递失败后释放本实例持有的锁，并安排一分钟后重试。"""
    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression=(
            "SET countdown_next_scan_at = :retry, last_analysis_status = :failed "
            "REMOVE countdown_scan_lock_until"
        ),
        ConditionExpression="countdown_last_scan_at = :now",
        ExpressionAttributeValues={
            ":retry": now + 60, ":failed": "DISPATCH_FAILED", ":now": now,
        },
    )


def run_schedule(event: Dict, now: int = None) -> Dict:
    """模式二：每分钟查找到期目录，抢占后触发倒计时分析。"""
    now = int(now if now is not None else time.time())
    limit = _integer(event.get("max_models", MAX_MODELS_PER_RUN), "max_models", 1, 100)
    results = []
    for item in find_due_catalogs(now, limit):
        crawl_id = str(item.get("crawl_id", ""))
        if not crawl_id or not claim_catalog(item, now):
            results.append({"目录记录ID": crawl_id, "状态": "已被其他实例处理"})
            continue
        try:
            sent = dispatch_to_analyzer(item)
        except Exception as exc:
            log("ERROR", "投递 Analyzer 失败", crawl_id=crawl_id, error=str(exc))
            sent = False
        if not sent:
            try:
                mark_dispatch_failed(crawl_id, now)
            except Exception as exc:
                log("ERROR", "释放扫描锁失败", crawl_id=crawl_id, error=str(exc))
        results.append({"目录记录ID": crawl_id, "状态": "已投递" if sent else "投递失败"})
    return {"状态": "扫描完成", "到期数量": len(results), "结果": results}


def lambda_handler(event, context):
    event = event or {}
    try:
        mode = event.get("mode", "schedule")
        if mode == "configure":
            result = configure_catalog(event)
        elif mode == "schedule":
            result = run_schedule(event)
        else:
            raise ValueError("mode 只支持 configure 或 schedule")
        return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False)}
    except Exception as exc:
        log("ERROR", "倒计时目录扫描执行失败", error=str(exc))
        return {"statusCode": 400, "body": json.dumps({"错误": str(exc)}, ensure_ascii=False)}
