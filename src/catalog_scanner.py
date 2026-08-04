"""Yahoo 拍卖目录倒计时扫描 Lambda。

倒计时配置直接保存在 ``YahooAuctionLinks`` 的叶子目录记录上。调度器按
``category_id`` 调用 Analyzer 的倒计时分析，不再依赖 ProductCatalog 商品表。
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List

import boto3

TABLE_NAME = os.environ.get("LINK_CRAWLER_TABLE_NAME", "YahooAuctionLinks-dev")
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
    print(json.dumps({"level": level, "message": message,
                      "timestamp": datetime.now(timezone.utc).isoformat(), **fields},
                     ensure_ascii=False, default=str))


def _integer(value, name: str, minimum: int, maximum: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} 必须是整数") from exc
    if not minimum <= result <= maximum:
        raise ValueError(f"{name} 必须在 {minimum} 到 {maximum} 之间")
    return result


def _find_directory(directory_id: str) -> Dict:
    """按 category_id 查找 YahooAuctionLinks 中的目录记录。"""
    response = table.scan(
        FilterExpression="category_id = :directory_id AND attribute_exists(crawl_id)",
        ExpressionAttributeValues={":directory_id": directory_id},
        ProjectionExpression="crawl_id, category_id, category_name, anchor_text",
    )
    items = response.get("Items", [])
    if not items:
        raise ValueError(f"未找到目录 ID：{directory_id}")
    return items[0]


def configure_catalog(event: Dict, now: int = None) -> Dict:
    """修改 YahooAuctionLinks 中单个目录的倒计时扫描配置。"""
    directory_id = str(event.get("directory_id", event.get("category_id", ""))).strip()
    if not directory_id:
        raise ValueError("缺少 directory_id（目录 ID）")
    item = _find_directory(directory_id)
    now = int(now if now is not None else time.time())
    active = _integer(event.get("active_count", DEFAULT_ACTIVE_COUNT), "active_count", 1, 1000)
    closed = _integer(event.get("closed_count", DEFAULT_CLOSED_COUNT), "closed_count", 1, 1000)
    interval = _integer(event.get("scan_interval_minutes", DEFAULT_INTERVAL_MINUTES),
                        "scan_interval_minutes", 1, 10080)
    enabled = event.get("scan_enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("scan_enabled 必须是布尔值")
    table.update_item(
        Key={"crawl_id": str(item["crawl_id"])},
        UpdateExpression=("SET countdown_active_count = :active, countdown_closed_count = :closed, "
                          "countdown_interval_minutes = :interval, countdown_scan_enabled = :enabled, "
                          "countdown_next_scan_at = :next, updated_at = :modified "
                          "REMOVE countdown_scan_lock_until"),
        ConditionExpression="category_id = :directory_id",
        ExpressionAttributeValues={
            ":active": active, ":closed": closed, ":interval": interval,
            ":enabled": enabled, ":next": now if enabled else 0,
            ":modified": datetime.now(timezone.utc).isoformat(), ":directory_id": directory_id,
        },
    )
    return {"状态": "配置已更新", "目录ID": directory_id, "是否开启扫描": enabled,
            "active数量": active, "closed数量": closed, "扫描间隔分钟": interval}


def find_due_catalogs(now: int, limit: int = MAX_MODELS_PER_RUN) -> List[Dict]:
    """从 YahooAuctionLinks 查找已开启且到期的有效目录。"""
    due, start_key = [], None
    while len(due) < limit:
        params = {
            "FilterExpression": ("attribute_exists(category_id) AND category_id <> :empty "
                                 "AND countdown_scan_enabled = :enabled AND "
                                 "(attribute_not_exists(countdown_next_scan_at) OR countdown_next_scan_at <= :now)"),
            "ExpressionAttributeValues": {":empty": "", ":enabled": True, ":now": now},
            "ProjectionExpression": ("crawl_id, category_id, category_name, anchor_text, "
                                     "countdown_active_count, countdown_closed_count, "
                                     "countdown_interval_minutes, countdown_next_scan_at"),
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
    interval = _integer(item.get("countdown_interval_minutes", DEFAULT_INTERVAL_MINUTES),
                        "countdown_interval_minutes", 1, 10080)
    try:
        lock_until = now + min(LOCK_SECONDS, max(30, interval * 60 - 1))
        table.update_item(
            Key={"crawl_id": str(item["crawl_id"])},
            UpdateExpression=("SET countdown_scan_lock_until = :lock, countdown_last_scan_at = :now, "
                              "countdown_next_scan_at = :next, last_analysis_status = :queued"),
            ConditionExpression=("countdown_scan_enabled = :enabled AND "
                                 "(attribute_not_exists(countdown_next_scan_at) OR countdown_next_scan_at <= :now) AND "
                                 "(attribute_not_exists(countdown_scan_lock_until) OR countdown_scan_lock_until < :now)"),
            ExpressionAttributeValues={":enabled": True, ":now": now, ":lock": lock_until,
                                       ":next": now + interval * 60, ":queued": "QUEUED"},
        )
        return True
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return False


def dispatch_to_analyzer(item: Dict) -> bool:
    payload = {"mode": "countdown", "source": "countdown_directory_scanner",
               "category_id": str(item["category_id"]),
               "active_count": int(item.get("countdown_active_count", DEFAULT_ACTIVE_COUNT)),
               "closed_count": int(item.get("countdown_closed_count", DEFAULT_CLOSED_COUNT)),
               "force_reprocess": False}
    response = lambda_client.invoke(FunctionName=ANALYZER_FUNCTION_NAME, InvocationType="Event",
                                    Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    return response.get("StatusCode") == 202


def mark_dispatch_failed(crawl_id: str, now: int):
    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression=("SET countdown_next_scan_at = :retry, last_analysis_status = :failed "
                          "REMOVE countdown_scan_lock_until"),
        ConditionExpression="countdown_last_scan_at = :now",
        ExpressionAttributeValues={":retry": now + 60, ":failed": "DISPATCH_FAILED", ":now": now},
    )


def run_schedule(event: Dict, now: int = None) -> Dict:
    now = int(now if now is not None else time.time())
    limit = _integer(event.get("max_models", MAX_MODELS_PER_RUN), "max_models", 1, 100)
    results = []
    for item in find_due_catalogs(now, limit):
        crawl_id, directory_id = str(item.get("crawl_id", "")), str(item.get("category_id", ""))
        if not crawl_id or not directory_id or not claim_catalog(item, now):
            results.append({"目录ID": directory_id, "状态": "已被其他实例处理"})
            continue
        try:
            sent = dispatch_to_analyzer(item)
        except Exception as exc:
            log("ERROR", "投递 Analyzer 失败", directory_id=directory_id, error=str(exc))
            sent = False
        if not sent:
            try:
                mark_dispatch_failed(crawl_id, now)
            except Exception as exc:
                log("ERROR", "释放扫描锁失败", directory_id=directory_id, error=str(exc))
        results.append({"目录ID": directory_id, "状态": "已投递" if sent else "投递失败"})
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
