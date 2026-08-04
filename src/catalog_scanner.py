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
LOCK_SECONDS = int(os.environ.get("SCAN_LOCK_SECONDS", "900"))

SCAN_PROFILES = {
    "OFF": {"enabled": False, "active": 0, "closed": 0, "interval": 0},
    "SLOW": {"enabled": True, "active": 10, "closed": 8, "interval": 30},
    "MEDIUM": {"enabled": True, "active": 20, "closed": 10, "interval": 10},
    "FAST": {"enabled": True, "active": 30, "closed": 15, "interval": 5},
}

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


def _scan_directories() -> List[Dict]:
    """读取所有叶子目录，供按分类名字配置挡位使用。"""
    items, start_key = [], None
    while True:
        params = {
            "FilterExpression": "attribute_exists(category_id) AND category_id <> :empty",
            "ExpressionAttributeValues": {":empty": ""},
            "ProjectionExpression": ("crawl_id, category_id, category_name, anchor_text, "
                                     "countdown_scan_profile, countdown_scan_enabled, "
                                     "countdown_active_count, countdown_closed_count, "
                                     "countdown_interval_minutes"),
        }
        if start_key:
            params["ExclusiveStartKey"] = start_key
        response = table.scan(**params)
        items.extend(response.get("Items", []))
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            return items


def _category_name(item: Dict) -> str:
    return str(item.get("category_name") or item.get("anchor_text") or "").strip()


def configure_profiles(event: Dict, now: int = None) -> Dict:
    """按分类名字批量设置 OFF/SLOW/MEDIUM/FAST；空配置返回当前运行配置。"""
    profiles = event.get("profiles")
    if profiles is None:
        profiles = {}
    if not isinstance(profiles, dict):
        raise ValueError("profiles 必须是分类名字到挡位的对象")
    directories = _scan_directories()
    if not profiles:
        current = {}
        for item in directories:
            name = _category_name(item)
            if not name or not item.get("countdown_scan_enabled"):
                continue
            current[name] = {
                "profile": item.get("countdown_scan_profile"),
                "active": item.get("countdown_active_count"),
                "closed": item.get("countdown_closed_count"),
                "interval": item.get("countdown_interval_minutes"),
            }
        return {"状态": "运行中配置", "count": len(current), "profiles": current}

    by_name = {_category_name(item): item for item in directories if _category_name(item)}
    now = int(now if now is not None else time.time())
    updated = {}
    for name, requested_profile in profiles.items():
        profile_name = str(requested_profile).strip().upper()
        if profile_name not in SCAN_PROFILES:
            raise ValueError(f"分类 {name} 的挡位无效，只支持 OFF、SLOW、MEDIUM、FAST")
        item = by_name.get(str(name).strip())
        if not item:
            raise ValueError(f"未找到分类名字：{name}")
        profile = SCAN_PROFILES[profile_name]
        table.update_item(
            Key={"crawl_id": str(item["crawl_id"])},
            UpdateExpression=("SET countdown_scan_profile = :profile, countdown_active_count = :active, "
                              "countdown_closed_count = :closed, countdown_interval_minutes = :interval, "
                              "countdown_scan_enabled = :enabled, countdown_next_scan_at = :next, "
                              "updated_at = :modified REMOVE countdown_scan_lock_until"),
            ConditionExpression="category_id = :category_id",
            ExpressionAttributeValues={
                ":profile": profile_name, ":active": profile["active"], ":closed": profile["closed"],
                ":interval": profile["interval"], ":enabled": profile["enabled"],
                ":next": now if profile["enabled"] else 0,
                ":modified": datetime.now(timezone.utc).isoformat(),
                ":category_id": str(item["category_id"]),
            },
        )
        updated[str(name)] = profile_name
    return {"状态": "配置已更新", "profiles": updated}


def configure_catalog(event: Dict, now: int = None) -> Dict:
    """修改 YahooAuctionLinks 中单个目录的倒计时扫描配置。"""
    directory_id = str(event.get("directory_id", event.get("category_id", ""))).strip()
    if not directory_id:
        raise ValueError("缺少 directory_id（目录 ID）")
    item = _find_directory(directory_id)
    now = int(now if now is not None else time.time())
    active = _integer(event.get("active_count", 20), "active_count", 1, 1000)
    closed = _integer(event.get("closed_count", 10), "closed_count", 1, 1000)
    interval = _integer(event.get("scan_interval_minutes", 10),
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
    interval = _integer(item.get("countdown_interval_minutes"),
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
    active_count = _integer(item.get("countdown_active_count"), "countdown_active_count", 1, 1000)
    closed_count = _integer(item.get("countdown_closed_count"), "countdown_closed_count", 1, 1000)
    payload = {"mode": "countdown", "source": "countdown_directory_scanner",
               "category_id": str(item["category_id"]),
               "category": str(item.get("category_name") or item.get("anchor_text") or "").strip(),
               "active_count": active_count,
               "closed_count": closed_count,
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
            result = (configure_profiles(event) if "profiles" in event or not
                      (event.get("directory_id") or event.get("category_id")) else configure_catalog(event))
        elif mode == "schedule":
            result = run_schedule(event)
        else:
            raise ValueError("mode 只支持 configure 或 schedule")
        return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False)}
    except Exception as exc:
        log("ERROR", "倒计时目录扫描执行失败", error=str(exc))
        return {"statusCode": 400, "body": json.dumps({"错误": str(exc)}, ensure_ascii=False)}
