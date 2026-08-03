"""
Yahoo! 拍卖 /list3/* 目录链接持久化队列采集 Lambda。

每个目录都是 DynamoDB 队列项。Lambda 通过 GSI 按深度和发现时间消费任务，
并用条件更新完成 QUEUED -> PROCESSING -> DONE/QUEUED/ERROR 状态流转。
"""

import hashlib
import logging
import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit

import boto3
import requests
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============================================================
# 常量配置
# ============================================================

ALLOWED_HOST = "auctions.yahoo.co.jp"
ALLOWED_LIST3_PREFIX = "/list3/"
DEFAULT_START_URL = "https://auctions.yahoo.co.jp/"
CATEGORY_ID_PATTERN = re.compile(r"/(\d+)-category(?:\.html)?/?$")

# 禁止爬取的路径（robots.txt 规则）
DISALLOW = (
    "/alert/",
    "/closeduser/",
    "/members/",
    "/sell/",
    "/user/",
    "/config/",
    "/search/advanced",
    "/follow/",
    "/login/",
    "/register/",
)

# 从环境变量读取配置
USER_AGENT = os.getenv(
    "LINK_CRAWLER_USER_AGENT",
    "TwoHandsLinkCrawler/1.0 (+https://auctions.yahoo.co.jp/robots.txt)",
)
REQUEST_TIMEOUT = float(os.getenv("LINK_CRAWLER_TIMEOUT", "30"))
MAX_PAGES = int(os.getenv("LINK_CRAWLER_MAX_PAGES", "100"))
MAX_DEPTH = int(os.getenv("LINK_CRAWLER_MAX_DEPTH", "5"))
REQUEST_INTERVAL = float(os.getenv("LINK_CRAWLER_REQUEST_INTERVAL", "0.5"))
MAX_LINKS_PER_RUN = int(os.getenv("LINK_CRAWLER_MAX_LINKS_PER_RUN", "5000"))
GSI_QUERY_PAGE_SIZE = int(os.getenv("LINK_CRAWLER_GSI_PAGE_SIZE", "100"))
MAX_ATTEMPTS = int(os.getenv("LINK_CRAWLER_MAX_ATTEMPTS", "3"))
QUEUE_INDEX_NAME = "queue_status-queue_priority-index"


# ============================================================
# URL 处理函数
# ============================================================

def is_allowed_url(url: str) -> bool:
    """仅允许目标站点的公开 HTTP(S) 页面，并应用指定的 robots 路径规则。"""
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return False
    if parsed.scheme not in {"http", "https"} or parsed.hostname != ALLOWED_HOST:
        return False
    path = parsed.path or "/"
    return not any(path == rule.rstrip("/") or path.startswith(rule) for rule in DISALLOW)


def normalize_url(href: str, source_url: str) -> str | None:
    """将相对链接转成绝对链接，移除 fragment，并拒绝站外及禁抓路径。"""
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
        return None
    absolute = urljoin(source_url, href.strip())
    try:
        parsed = urlsplit(absolute)
        normalized = urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.query,
            ""
        ))
    except ValueError:
        return None
    return normalized if is_allowed_url(normalized) else None


# ============================================================
# 页面类型判断
# ============================================================

def is_list3_page(url: str) -> bool:
    """
    判断是否为 /list3/* 目录页。
    
    当前仅允许：
    - https://auctions.yahoo.co.jp/list3/*
    """
    if not url:
        return False
    
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return False
    
    if parsed.scheme not in {"http", "https"}:
        return False
    
    if parsed.hostname != ALLOWED_HOST:
        return False
    
    path = parsed.path or "/"
    
    return path.startswith(ALLOWED_LIST3_PREFIX)


def extract_category_id(url: str) -> str | None:
    """从 Yahoo ``/list3/.../<数字>-category.html`` URL 提取品类 ID。"""
    if not is_list3_page(url):
        return None
    match = CATEGORY_ID_PATTERN.search(urlsplit(url).path)
    return match.group(1) if match else None


def should_crawl(url: str) -> bool:
    """判断一个 URL 是否应该被递归爬取：仅允许 /list3/*。"""
    if not url:
        return False
    
    if not is_allowed_url(url):
        return False
    
    return is_list3_page(url)


# ============================================================
# 链接提取
# ============================================================

def extract_links_from_page(html: str, source_url: str, depth: int) -> list[dict]:
    """
    从 HTML 中提取 /list3/* 目录链接。
    
    返回:
        - list3_links: /list3/* 目录链接，既用于保存，也用于递归
    """
    list3_links = []
    seen = set()
    
    if not html:
        return list3_links
    
    soup = BeautifulSoup(html, "html.parser")
    
    for anchor in soup.select("a[href]"):
        url = normalize_url(anchor.get("href"), source_url)
        
        if not url or url in seen:
            continue
        
        seen.add(url)
        
        if not is_list3_page(url):
            continue
        
        anchor_text = " ".join(anchor.get_text(" ", strip=True).split())
        
        list3_links.append({
            "url": url,
            "category_id": extract_category_id(url) or "",
            "category_name": anchor_text[:500],
            "anchor_text": anchor_text[:500],
            "source_url": source_url,
            "depth": depth,
            "link_type": "list3_directory",
        })
    
    return list3_links


def extract_links(html: str, source_url: str, limit: int | None = None) -> list[dict]:
    """兼容通用链接提取；目录采集主流程仍只使用 ``extract_links_from_page``。"""
    links, seen = [], set()
    soup = BeautifulSoup(html or "", "html.parser")
    for anchor in soup.select("a[href]"):
        url = normalize_url(anchor.get("href"), source_url)
        if not url or url in seen:
            continue
        seen.add(url)
        links.append({
            "url": url,
            "anchor_text": " ".join(anchor.get_text(" ", strip=True).split())[:500],
            "source_url": source_url,
        })
        if limit is not None and len(links) >= limit:
            break
    return links


# ============================================================
# DynamoDB 状态管理工具函数
# ============================================================

def make_crawl_id(url: str) -> str:
    """一个目录 URL 永远对应同一个 crawl_id。"""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def get_link_record(table, url: str) -> dict | None:
    """从 DynamoDB 获取某个 URL 的记录。"""
    crawl_id = make_crawl_id(url)

    response = table.get_item(
        Key={"crawl_id": crawl_id}
    )

    return response.get("Item")


def is_url_already_crawled(table, url: str) -> bool:
    """判断该 URL 是否已经被递归检索过。"""
    item = get_link_record(table, url)

    if not item:
        return False

    return bool(item.get("is_crawled"))


def get_next_unvisited_url(table) -> str | None:
    """
    从 DynamoDB 中获取最久未爬取的 /list3/* 链接。
    
    查询条件：
    - link_type = 'list3_directory'
    - is_crawled = False 或 crawl_status = 'DISCOVERED'
    - 按 first_seen_at 升序排列（最久远的优先）
    
    使用 GSI: link_type-first_seen_at-index
    """
    try:
        exclusive_start_key = None
        while True:
            query_kwargs = {
                "IndexName": "link_type-first_seen_at-index",
                "KeyConditionExpression": "link_type = :link_type",
                "FilterExpression": "is_crawled = :false_val OR crawl_status = :status",
                "ExpressionAttributeValues": {
                    ":link_type": "list3_directory",
                    ":false_val": False,
                    ":status": "DISCOVERED",
                },
                "ScanIndexForward": True,  # 升序，最旧的在前
                # Limit 在 FilterExpression 之前生效，因此按批读取并继续翻页。
                "Limit": GSI_QUERY_PAGE_SIZE,
            }
            if exclusive_start_key:
                query_kwargs["ExclusiveStartKey"] = exclusive_start_key

            response = table.query(**query_kwargs)
            items = response.get("Items", [])
            if items:
                return items[0].get("url")

            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                return None
        
    except Exception as e:
        logger.warning(f"查询 GSI 失败，可能索引不存在: {e}")
        return None


def is_table_empty(table) -> bool:
    """
    检查表是否为空（没有任何 /list3/* 记录）。
    """
    try:
        response = table.query(
            IndexName="link_type-first_seen_at-index",
            KeyConditionExpression="link_type = :link_type",
            ExpressionAttributeValues={
                ":link_type": "list3_directory",
            },
            Limit=1,
        )
        
        items = response.get("Items", [])
        return len(items) == 0
        
    except Exception as e:
        logger.warning(f"检查表是否为空失败: {e}")
        # 如果 GSI 不存在或查询失败，回退到扫描
        try:
            response = table.scan(Limit=1)
            items = response.get("Items", [])
            return len(items) == 0
        except Exception:
            return True


def save_discovered_link(table, link: dict) -> dict:
    """
    保存发现的 /list3/* 目录链接。

    注意：
    - 不覆盖已经爬过的状态
    - 只在第一次发现时写入 first_seen_at
    - 每次发现都更新 last_seen_at
    """
    now = datetime.now(timezone.utc).isoformat()
    url = link["url"]
    crawl_id = make_crawl_id(url)

    try:
        response = table.update_item(
            Key={"crawl_id": crawl_id},
            UpdateExpression="""
                SET
                    #url = :url,
                    category_id = :category_id,
                    category_name = :category_name,
                    anchor_text = if_not_exists(anchor_text, :anchor_text),
                    source_url = if_not_exists(source_url, :source_url),
                    #depth = if_not_exists(#depth, :depth),
                    link_type = :link_type,
                    crawl_status = if_not_exists(crawl_status, :status),
                    is_crawled = if_not_exists(is_crawled, :false_value),
                    is_terminal = if_not_exists(is_terminal, :false_value),
                    is_exhausted = if_not_exists(is_exhausted, :false_value),
                    first_seen_at = if_not_exists(first_seen_at, :now),
                    last_seen_at = :now,
                    updated_at = :now
                ADD discovered_count :one
            """,
            ExpressionAttributeNames={
                "#url": "url",
                "#depth": "depth",
            },
            ExpressionAttributeValues={
                ":url": url,
                ":category_id": link.get("category_id") or extract_category_id(url) or "",
                ":category_name": link.get("category_name") or link.get("anchor_text", ""),
                ":anchor_text": link.get("anchor_text", ""),
                ":source_url": link.get("source_url", ""),
                ":depth": link.get("depth", 0),
                ":link_type": link.get("link_type", "list3_directory"),
                ":status": "DISCOVERED",
                ":false_value": False,
                ":now": now,
                ":one": 1,
            },
            ReturnValues="ALL_OLD",
        )
        previous_record = response.get("Attributes")
        return {
            "is_new": not bool(previous_record),
            "previous_record": previous_record,
        }
    except Exception as e:
        logger.error(f"保存链接失败 {url}: {e}")
        return {"is_new": False, "previous_record": None, "save_failed": True}


def count_remaining_unvisited(table) -> int:
    """分页统计 GSI 中全部尚未爬取的目录。"""
    remaining = 0
    exclusive_start_key = None

    while True:
        query_kwargs = {
            "IndexName": "link_type-first_seen_at-index",
            "KeyConditionExpression": "link_type = :link_type",
            "FilterExpression": "is_crawled = :false_val OR crawl_status = :status",
            "ExpressionAttributeValues": {
                ":link_type": "list3_directory",
                ":false_val": False,
                ":status": "DISCOVERED",
            },
            "Select": "COUNT",
        }
        if exclusive_start_key:
            query_kwargs["ExclusiveStartKey"] = exclusive_start_key

        response = table.query(**query_kwargs)
        remaining += response.get("Count", 0)
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            return remaining


def utc_now() -> str:
    """返回固定格式的 UTC 时间，避免 ``+00:00`` 与 ``Z`` 混用。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def make_queue_priority(depth: int, created_at: str, crawl_id: str) -> str:
    """生成先按深度、再按发现时间排序的持久化队列优先级。"""
    return f"{int(depth):05d}#{created_at}#{crawl_id}"


def enqueue_discovered_link(table, link: dict, root_url: str) -> dict:
    """将发现的目录幂等写入 DynamoDB 队列；已有状态不会被重置。"""
    url = link["url"]
    crawl_id = make_crawl_id(url)
    now = utc_now()
    depth = int(link.get("depth", 0))
    response = table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression="""
            SET #url = :url,
                link_type = :link_type,
                queue_status = if_not_exists(queue_status, :queued),
                queue_priority = if_not_exists(queue_priority, :priority),
                #depth = if_not_exists(#depth, :depth),
                parent_url = if_not_exists(parent_url, :parent_url),
                root_url = if_not_exists(root_url, :root_url),
                created_at = if_not_exists(created_at, :now),
                first_seen_at = if_not_exists(first_seen_at, :now),
                last_seen_at = :now,
                updated_at = :now,
                attempt_count = if_not_exists(attempt_count, :zero),
                category_id = :category_id,
                category_name = :category_name,
                anchor_text = :anchor_text,
                source_url = :source_url
        """,
        ExpressionAttributeNames={"#url": "url", "#depth": "depth"},
        ExpressionAttributeValues={
            ":url": url, ":link_type": "list3_directory", ":queued": "QUEUED",
            ":priority": make_queue_priority(depth, now, crawl_id), ":depth": depth,
            ":parent_url": link.get("source_url", ""), ":root_url": root_url,
            ":now": now, ":zero": 0,
            ":category_id": link.get("category_id") or extract_category_id(url) or "",
            ":category_name": link.get("category_name") or link.get("anchor_text", ""),
            ":anchor_text": link.get("anchor_text", ""),
            ":source_url": link.get("source_url", ""),
        },
        ReturnValues="ALL_OLD",
    )
    old = response.get("Attributes")
    return {
        "crawl_id": crawl_id,
        "url": url,
        "is_new": not bool(old),
        "previous_status": old.get("queue_status") if old else None,
    }


def get_queued_items(table, limit: int) -> list[dict]:
    """按 BFS 优先级分页读取最多 ``limit`` 个待处理目录。"""
    if limit <= 0:
        return []
    items, exclusive_start_key = [], None
    while len(items) < limit:
        kwargs = {
            "IndexName": QUEUE_INDEX_NAME,
            "KeyConditionExpression": "queue_status = :queued",
            "ExpressionAttributeValues": {":queued": "QUEUED"},
            "ScanIndexForward": True,
            "Limit": limit - len(items),
        }
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        response = table.query(**kwargs)
        items.extend(response.get("Items", []))
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            break
    return items[:limit]


def claim_queue_item(table, crawl_id: str) -> dict | None:
    """以条件更新原子抢占一个 QUEUED 任务。"""
    now = utc_now()
    try:
        response = table.update_item(
            Key={"crawl_id": crawl_id},
            UpdateExpression=("SET queue_status = :processing, claimed_at = :now, "
                              "updated_at = :now ADD attempt_count :one"),
            ConditionExpression="queue_status = :queued",
            ExpressionAttributeValues={
                ":queued": "QUEUED", ":processing": "PROCESSING", ":now": now, ":one": 1,
            },
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return None
        raise


def mark_queue_done(table, crawl_id: str, child_count: int,
                    new_child_count: int, is_terminal: bool) -> dict | None:
    """仅将当前 PROCESSING 任务标记为 DONE。"""
    now = utc_now()
    response = table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression=("SET queue_status = :done, child_count = :child_count, "
                          "new_child_count = :new_child_count, is_terminal = :is_terminal, "
                          "done_at = :now, updated_at = :now REMOVE last_error"),
        ConditionExpression="queue_status = :processing",
        ExpressionAttributeValues={
            ":processing": "PROCESSING", ":done": "DONE", ":child_count": child_count,
            ":new_child_count": new_child_count, ":is_terminal": is_terminal, ":now": now,
        },
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")


def mark_queue_failed(table, item: dict, error_message: str) -> dict | None:
    """按已 claim 的尝试次数将失败任务重新排队或转为 ERROR。"""
    now = utc_now()
    status = "QUEUED" if int(item.get("attempt_count", 0)) < MAX_ATTEMPTS else "ERROR"
    response = table.update_item(
        Key={"crawl_id": item["crawl_id"]},
        UpdateExpression=("SET queue_status = :status, last_error = :error, "
                          "last_error_at = :now, updated_at = :now"),
        ConditionExpression="queue_status = :processing",
        ExpressionAttributeValues={
            ":processing": "PROCESSING", ":status": status,
            ":error": str(error_message)[:1000], ":now": now,
        },
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")


def has_queued_items(table) -> bool:
    """使用队列 GSI 判断是否至少存在一个 QUEUED 项。"""
    response = table.query(
        IndexName=QUEUE_INDEX_NAME,
        KeyConditionExpression="queue_status = :queued",
        ExpressionAttributeValues={":queued": "QUEUED"},
        Limit=1,
    )
    return bool(response.get("Items"))


def count_queue_status(table, status: str) -> int:
    """分页统计指定队列状态的全部记录。"""
    total, exclusive_start_key = 0, None
    while True:
        kwargs = {
            "IndexName": QUEUE_INDEX_NAME,
            "KeyConditionExpression": "queue_status = :status",
            "ExpressionAttributeValues": {":status": status},
            "Select": "COUNT",
        }
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        response = table.query(**kwargs)
        total += int(response.get("Count", 0))
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            return total


def _http_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


def seed_from_homepage(table) -> int:
    """队列为空时从 Yahoo 首页发现并持久化第一层目录。"""
    response = _http_session().get(DEFAULT_START_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    added = 0
    for link in extract_links_from_page(response.text, DEFAULT_START_URL, depth=0):
        result = enqueue_discovered_link(table, link, root_url=link["url"])
        added += int(result["is_new"])
    return added


def recover_stale_processing_items(table, stale_seconds: int = 900) -> int:
    """简易扫描恢复超时任务；生产环境建议使用 queue_status-claimed_at-index。"""
    cutoff = datetime.fromtimestamp(time.time() - stale_seconds, timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    recovered, exclusive_start_key = 0, None
    while True:
        kwargs = {
            "FilterExpression": "queue_status = :processing AND claimed_at < :cutoff",
            "ExpressionAttributeValues": {":processing": "PROCESSING", ":cutoff": cutoff},
            "ProjectionExpression": "crawl_id",
        }
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        response = table.scan(**kwargs)
        for item in response.get("Items", []):
            try:
                table.update_item(
                    Key={"crawl_id": item["crawl_id"]},
                    UpdateExpression="SET queue_status = :queued, updated_at = :now",
                    ConditionExpression="queue_status = :processing AND claimed_at < :cutoff",
                    ExpressionAttributeValues={
                        ":queued": "QUEUED", ":processing": "PROCESSING",
                        ":cutoff": cutoff, ":now": utc_now(),
                    },
                )
                recovered += 1
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
                    raise
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            return recovered


def crawl_queue(table, max_pages: int | None = None, max_depth: int | None = None,
                max_links_per_run: int | None = None) -> dict:
    """消费 DynamoDB 持久化队列，不依赖进程内存恢复进度。"""
    page_limit = MAX_PAGES if max_pages is None else int(max_pages)
    depth_limit = MAX_DEPTH if max_depth is None else int(max_depth)
    link_limit = MAX_LINKS_PER_RUN if max_links_per_run is None else int(max_links_per_run)
    pages_crawled = directories_found = newly_enqueued = 0
    errors = []
    session = _http_session()

    while pages_crawled < page_limit and directories_found < link_limit:
        queued_items = get_queued_items(table, limit=25)
        if not queued_items:
            break
        claimed_any = False
        for queued_item in queued_items:
            if pages_crawled >= page_limit or directories_found >= link_limit:
                break
            claimed = claim_queue_item(table, queued_item["crawl_id"])
            if claimed is None:
                continue
            claimed_any = True
            current_url = claimed["url"]
            depth = int(claimed.get("depth", 0))
            root_url = claimed.get("root_url") or current_url
            if depth > depth_limit or not should_crawl(current_url):
                mark_queue_done(table, claimed["crawl_id"], 0, 0, False)
                continue
            try:
                response = session.get(current_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                pages_crawled += 1
                discovered = extract_links_from_page(response.text, current_url, depth + 1)
                unique_children = {}
                for directory in discovered:
                    if directory["url"] != current_url:
                        unique_children.setdefault(directory["url"], directory)
                page_new = 0
                for directory in unique_children.values():
                    result = enqueue_discovered_link(table, directory, root_url)
                    directories_found += 1
                    if result["is_new"]:
                        page_new += 1
                        newly_enqueued += 1
                child_count = len(unique_children)
                mark_queue_done(
                    table, claimed["crawl_id"], child_count, page_new,
                    is_terminal=child_count == 0,
                )
                if REQUEST_INTERVAL:
                    time.sleep(REQUEST_INTERVAL)
            except Exception as exc:
                message = f"处理失败 {current_url}: {exc}"
                logger.exception(message)
                errors.append(message)
                try:
                    mark_queue_failed(table, claimed, message)
                except Exception:
                    logger.exception("更新失败队列状态失败: %s", current_url)
        if not claimed_any:
            break
    return {
        "pages_crawled": pages_crawled,
        "directories_found": directories_found,
        "newly_enqueued": newly_enqueued,
        "errors": errors,
    }


def lambda_handler(event, context):
    """EventBridge 入口：恢复、播种并消费 DynamoDB 持久化目录队列。"""
    event = event if isinstance(event, dict) else {}
    table = boto3.resource("dynamodb").Table(os.environ["LINK_CRAWLER_TABLE_NAME"])
    recover_stale_processing_items(table)
    seeded = 0
    if not has_queued_items(table):
        seeded = seed_from_homepage(table)
    result = crawl_queue(
        table,
        max_pages=event.get("max_pages"),
        max_depth=event.get("max_depth"),
        max_links_per_run=event.get("max_links_per_run"),
    )
    queue = {
        "queued": count_queue_status(table, "QUEUED"),
        "processing": count_queue_status(table, "PROCESSING"),
        "done": count_queue_status(table, "DONE"),
        "error": count_queue_status(table, "ERROR"),
    }
    return {
        "statusCode": 200,
        "message": "队列式 /list3/* 目录采集完成",
        "seeded": seeded,
        "metrics": result,
        "queue": queue,
    }
