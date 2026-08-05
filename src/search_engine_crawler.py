"""
Yahoo! 拍卖 /list3/* 目录链接持久化队列采集 Lambda。

每个目录都是 DynamoDB 队列项。Lambda 通过 GSI 按深度和发现时间消费任务，
并用条件更新完成 QUEUED -> PROCESSING -> DONE/QUEUED/ERROR 状态流转。

优化内容：
1. 严格 URL 过滤：仅保留 /list3/数字-category.html，拒绝 leaf/catlist/query
2. 过滤无效 anchor：空文本、"カテゴリから探す" 等
3. 统一队列状态：queue_status 同步更新 crawl_status/is_crawled
4. 统计改为按需：仅 event.include_counts=true 时统计
5. 优化默认参数：减少单次 Lambda 负载
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

YAHOO_SOURCE = "YAHOO_AUCTION"
MERCARI_SOURCE = "MERCARI"
ALLOWED_HOST = "auctions.yahoo.co.jp"
MERCARI_HOST = "jp.mercari.com"
ALLOWED_HOSTS = {ALLOWED_HOST, MERCARI_HOST}
ALLOWED_LIST3_PREFIX = "/list3/"
DEFAULT_START_URL = "https://auctions.yahoo.co.jp/"
MERCARI_START_URL = "https://jp.mercari.com/categories"
START_URLS = (DEFAULT_START_URL, MERCARI_START_URL)
START_URL_BY_SOURCE = {
    YAHOO_SOURCE: DEFAULT_START_URL,
    MERCARI_SOURCE: MERCARI_START_URL,
}
SOURCE_ALIASES = {
    "YAHOO": YAHOO_SOURCE,
    "YAHOO_AUCTION": YAHOO_SOURCE,
    "MERCARI": MERCARI_SOURCE,
}

# 仅匹配 /list3/.../数字-category.html 的真目录页
CATEGORY_PAGE_PATTERN = re.compile(
    r"^/list3/(?:jp/.+/)?(\d+)-category\.html/?$",
    re.IGNORECASE,
)

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

# 无效的 anchor 文本
BAD_ANCHOR_TEXTS = {
    "",
    "カテゴリから探す",
    "すべて",
    "一覧",
    "カテゴリ一覧",
    "もっと見る",
    "さらに表示",
}

# 从环境变量读取配置
USER_AGENT = os.getenv(
    "LINK_CRAWLER_USER_AGENT",
    "TwoHandsLinkCrawler/1.0 (+https://auctions.yahoo.co.jp/robots.txt)",
)
REQUEST_TIMEOUT = float(os.getenv("LINK_CRAWLER_TIMEOUT", "30"))
MAX_PAGES = int(os.getenv("LINK_CRAWLER_MAX_PAGES", "20"))  # 降低默认值
MAX_DEPTH = int(os.getenv("LINK_CRAWLER_MAX_DEPTH", "5"))
REQUEST_INTERVAL = float(os.getenv("LINK_CRAWLER_REQUEST_INTERVAL", "0.8"))  # 提高间隔
MAX_LINKS_PER_RUN = int(os.getenv("LINK_CRAWLER_MAX_LINKS_PER_RUN", "1000"))  # 降低默认值
GSI_QUERY_PAGE_SIZE = int(os.getenv("LINK_CRAWLER_GSI_PAGE_SIZE", "25"))  # 降低分页大小
MAX_ATTEMPTS = int(os.getenv("LINK_CRAWLER_MAX_ATTEMPTS", "3"))
QUEUE_INDEX_NAME = "queue_status-queue_priority-index"

# ============================================================
# URL 处理函数
# ============================================================

def website_source_from_url(url: str) -> str:
    """根据 URL 域名返回网站来源字段。"""
    try:
        hostname = urlsplit(url).hostname
    except (TypeError, ValueError):
        return ""
    if hostname == MERCARI_HOST:
        return MERCARI_SOURCE
    if hostname == ALLOWED_HOST:
        return YAHOO_SOURCE
    return ""


def normalize_requested_source(source: str | None) -> str | None:
    """将 event.source 控制参数归一化为网站来源；未指定或 EventBridge source 返回 None。"""
    if not source or not isinstance(source, str):
        return None
    normalized = source.strip().upper().replace("-", "_").replace(" ", "_")
    if normalized in {"AWS.EVENTS", "AWS_EVENTS"}:
        return None
    return SOURCE_ALIASES.get(normalized)


def is_allowed_url(url: str) -> bool:
    """仅允许目标站点的公开 HTTP(S) 页面，并应用指定的 robots 路径规则。"""
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return False
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in ALLOWED_HOSTS:
        return False
    if parsed.hostname == MERCARI_HOST:
        return (parsed.path or "/") == "/categories"
    path = parsed.path or "/"
    return not any(path == rule.rstrip("/") or path.startswith(rule) for rule in DISALLOW)


def canonicalize_category_url(url: str) -> str | None:
    """只保留支持网站的目录页，并归一化为标准 URL。"""
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return None

    if parsed.scheme not in {"http", "https"}:
        return None

    path = parsed.path or "/"
    if parsed.hostname == MERCARI_HOST:
        if path != "/categories" or not parsed.query:
            return None
        query_parts = [part for part in parsed.query.split("&") if part.startswith("category_id=")]
        if not query_parts:
            return None
        return urlunsplit(("https", MERCARI_HOST, path, query_parts[0], ""))

    if parsed.hostname != ALLOWED_HOST:
        return None
    if not path.startswith(ALLOWED_LIST3_PREFIX):
        return None
    if path.endswith("-catlist.html") or "-category-leaf.html" in path or parsed.query:
        return None
    match = CATEGORY_PAGE_PATTERN.match(path)
    if not match:
        return None
    return urlunsplit(("https", ALLOWED_HOST, path, "", ""))


def is_list3_page(url: str) -> bool:
    """判断是否为真正的 list3 目录页（非 leaf、非 catlist、无 query）。"""
    return canonicalize_category_url(url) is not None


def extract_category_id(url: str) -> str | None:
    """从 Yahoo 或 Mercari 目录 URL 提取品类 ID。"""
    canonical = canonicalize_category_url(url)
    if not canonical:
        return None
    parsed = urlsplit(canonical)
    if parsed.hostname == MERCARI_HOST:
        for part in parsed.query.split("&"):
            if part.startswith("category_id="):
                return part.split("=", 1)[1]
        return None
    match = CATEGORY_PAGE_PATTERN.match(parsed.path)
    return match.group(1) if match else None


def normalize_url(href: str, source_url: str) -> str | None:
    """将相对链接转成绝对链接，移除 fragment，归一化并过滤。"""
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
            "",
        ))
    except ValueError:
        return None
    if not is_allowed_url(normalized):
        return None
    return canonicalize_category_url(normalized)


def should_crawl(url: str) -> bool:
    """判断一个 URL 是否应该被递归爬取：仅允许 /list3/数字-category.html。"""
    return canonicalize_category_url(url) is not None


# ============================================================
# 链接提取
# ============================================================

def clean_anchor_text(text: str) -> str:
    """清洗 anchor 文本，去除多余空白。"""
    return " ".join((text or "").split())[:500]


def extract_links_from_page(html: str, source_url: str, depth: int) -> list[dict]:
    """
    从 HTML 中提取 /list3/* 目录链接。
    
    过滤规则：
    - 仅保留 /list3/数字-category.html 格式
    - 拒绝空文本和无效 anchor
    - 去重（基于归一化 URL）
    
    返回:
        - list3_links: /list3/* 目录链接列表
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

        anchor_text = clean_anchor_text(anchor.get_text(" ", strip=True))

        # 过滤无效 anchor
        if anchor_text in BAD_ANCHOR_TEXTS:
            continue

        category_id = extract_category_id(url)
        if not category_id:
            continue

        seen.add(url)

        website_source = website_source_from_url(url)
        link_type = "mercari_directory" if website_source == MERCARI_SOURCE else "list3_directory"
        list3_links.append({
            "url": url,
            "category_id": category_id,
            "category_name": anchor_text,
            "anchor_text": anchor_text,
            "source_url": source_url,
            "website_source": website_source,
            "source": website_source,
            "depth": depth,
            "link_type": link_type,
        })

    return list3_links


# ============================================================
# DynamoDB 状态管理工具函数
# ============================================================

def make_crawl_id(url: str) -> str:
    """一个目录 URL 永远对应同一个 crawl_id。"""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def utc_now() -> str:
    """返回固定格式的 UTC 时间。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def make_queue_priority(depth: int, created_at: str, crawl_id: str) -> str:
    """生成先按深度、再按发现时间排序的持久化队列优先级。"""
    return f"{int(depth):05d}#{created_at}#{crawl_id}"


def get_link_record(table, url: str) -> dict | None:
    """从 DynamoDB 获取某个 URL 的记录。"""
    crawl_id = make_crawl_id(url)
    response = table.get_item(Key={"crawl_id": crawl_id})
    return response.get("Item")


def is_url_already_crawled(table, url: str) -> bool:
    """判断该 URL 是否已经被递归检索过。"""
    item = get_link_record(table, url)
    if not item:
        return False
    return bool(item.get("is_crawled"))


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
                is_crawled = if_not_exists(is_crawled, :false_value),
                is_terminal = if_not_exists(is_terminal, :false_value),
                is_exhausted = if_not_exists(is_exhausted, :false_value),
                category_id = if_not_exists(category_id, :category_id),
                category_name = if_not_exists(category_name, :category_name),
                anchor_text = if_not_exists(anchor_text, :anchor_text),
                source_url = if_not_exists(source_url, :source_url),
                website_source = if_not_exists(website_source, :website_source),
                #source = if_not_exists(#source, :website_source),
                crawl_status = if_not_exists(crawl_status, :discovered)
        """,
        ExpressionAttributeNames={"#url": "url", "#depth": "depth", "#source": "source"},
        ExpressionAttributeValues={
            ":url": url,
            ":link_type": link.get("link_type") or ("mercari_directory" if link.get("website_source") == MERCARI_SOURCE else "list3_directory"),
            ":queued": "QUEUED",
            ":priority": make_queue_priority(depth, now, crawl_id),
            ":depth": depth,
            ":parent_url": link.get("source_url", ""),
            ":root_url": root_url,
            ":now": now,
            ":zero": 0,
            ":false_value": False,
            ":category_id": link.get("category_id") or extract_category_id(url) or "",
            ":category_name": link.get("category_name") or link.get("anchor_text", ""),
            ":anchor_text": link.get("anchor_text", ""),
            ":source_url": link.get("source_url", ""),
            ":website_source": link.get("website_source") or link.get("source") or website_source_from_url(url),
            ":discovered": "DISCOVERED",
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


def get_queued_items(table, limit: int, website_source: str | None = None) -> list[dict]:
    """按 BFS 优先级分页读取最多 ``limit`` 个待处理目录，可按网站来源过滤。"""
    if limit <= 0:
        return []
    items, exclusive_start_key = [], None
    while len(items) < limit:
        kwargs = {
            "IndexName": QUEUE_INDEX_NAME,
            "KeyConditionExpression": "queue_status = :queued",
            "ExpressionAttributeValues": {":queued": "QUEUED"},
            "ScanIndexForward": True,
            "Limit": min(limit - len(items), GSI_QUERY_PAGE_SIZE),
        }
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        response = table.query(**kwargs)
        page_items = response.get("Items", [])
        if website_source:
            page_items = [
                item for item in page_items
                if (
                    item.get("website_source")
                    or item.get("source")
                    or website_source_from_url(item.get("url", ""))
                ) == website_source
            ]
        items.extend(page_items)
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
            UpdateExpression=(
                "SET queue_status = :processing, "
                "claimed_at = :now, "
                "updated_at = :now "
                "ADD attempt_count :one"
            ),
            ConditionExpression="queue_status = :queued",
            ExpressionAttributeValues={
                ":queued": "QUEUED",
                ":processing": "PROCESSING",
                ":now": now,
                ":one": 1,
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
    """
    将当前 PROCESSING 任务标记为 DONE。
    同时同步更新旧字段：crawl_status, is_crawled, is_terminal, is_exhausted。
    """
    now = utc_now()
    crawl_status = "TERMINAL" if is_terminal else "CRAWLED"

    response = table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression=(
            "SET queue_status = :done, "
            "crawl_status = :crawl_status, "
            "is_crawled = :true_value, "
            "is_terminal = :is_terminal, "
            "is_exhausted = :is_terminal, "
            "child_count = :child_count, "
            "new_child_count = :new_child_count, "
            "done_at = :now, "
            "updated_at = :now "
            "REMOVE last_error"
        ),
        ConditionExpression="queue_status = :processing",
        ExpressionAttributeValues={
            ":processing": "PROCESSING",
            ":done": "DONE",
            ":crawl_status": crawl_status,
            ":true_value": True,
            ":child_count": child_count,
            ":new_child_count": new_child_count,
            ":is_terminal": is_terminal,
            ":now": now,
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
        UpdateExpression=(
            "SET queue_status = :status, "
            "last_error = :error, "
            "last_error_at = :now, "
            "updated_at = :now"
        ),
        ConditionExpression="queue_status = :processing",
        ExpressionAttributeValues={
            ":processing": "PROCESSING",
            ":status": status,
            ":error": str(error_message)[:1000],
            ":now": now,
        },
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")


def has_queued_items(table, website_source: str | None = None) -> bool:
    """使用队列 GSI 判断是否至少存在一个 QUEUED 项，可按网站来源过滤。"""
    if website_source:
        return bool(get_queued_items(table, 1, website_source=website_source))
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
                        ":queued": "QUEUED",
                        ":processing": "PROCESSING",
                        ":cutoff": cutoff,
                        ":now": utc_now(),
                    },
                )
                recovered += 1
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
                    raise
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            return recovered




def extract_links(html: str, source_url: str, limit: int | None = None) -> list[dict]:
    """兼容旧版通用链接提取测试：仅清洗、去重并返回允许访问的链接。"""
    soup = BeautifulSoup(html or "", "html.parser")
    links, seen = [], set()
    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        parsed = urlsplit(urljoin(source_url, href.strip()))
        normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))
        if normalized in seen or not is_allowed_url(normalized):
            continue
        seen.add(normalized)
        links.append({"url": normalized, "anchor_text": clean_anchor_text(anchor.get_text(" ", strip=True)), "source_url": source_url})
        if limit is not None and len(links) >= limit:
            break
    return links


def save_discovered_link(table, link: dict) -> dict:
    """兼容旧接口，转发到队列写入函数。"""
    return enqueue_discovered_link(table, link, link.get("source_url") or link.get("url", ""))


def get_next_unvisited_url(table) -> str | None:
    """兼容旧接口，按队列索引返回下一条未访问 URL。"""
    for item in get_queued_items(table, 1):
        return item.get("url")
    return None


def count_remaining_unvisited(table) -> int:
    """兼容旧接口，统计 QUEUED 项。"""
    return count_queue_status(table, "QUEUED")

# ============================================================
# HTTP 会话
# ============================================================

def _http_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


# ============================================================
# 播种与队列消费
# ============================================================

def seed_from_homepage(table, website_source: str | None = None) -> int:
    """队列为空时从目标网站首页发现并持久化第一层目录。"""
    session = _http_session()
    added = 0
    start_urls = (START_URL_BY_SOURCE[website_source],) if website_source else START_URLS
    for start_url in start_urls:
        response = session.get(start_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        for link in extract_links_from_page(response.text, start_url, depth=0):
            result = enqueue_discovered_link(table, link, root_url=link["url"])
            added += int(result["is_new"])
    return added


def crawl_queue(table, max_pages: int | None = None, max_depth: int | None = None,
                max_links_per_run: int | None = None, website_source: str | None = None) -> dict:
    """消费 DynamoDB 持久化队列，不依赖进程内存恢复进度。"""
    page_limit = MAX_PAGES if max_pages is None else int(max_pages)
    depth_limit = MAX_DEPTH if max_depth is None else int(max_depth)
    link_limit = MAX_LINKS_PER_RUN if max_links_per_run is None else int(max_links_per_run)
    pages_crawled = directories_found = newly_enqueued = 0
    errors = []
    session = _http_session()

    while pages_crawled < page_limit and directories_found < link_limit:
        queued_items = get_queued_items(table, limit=25, website_source=website_source)
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
                if website_source:
                    discovered = [
                        link for link in discovered
                        if link.get("website_source") == website_source
                    ]
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


# ============================================================
# Lambda 入口
# ============================================================

def lambda_handler(event, context):
    """
    EventBridge 入口：恢复、播种并消费 DynamoDB 持久化目录队列。
    
    可选 event 参数：
    - max_pages: 本次最大爬取页数
    - max_depth: 最大爬取深度
    - max_links_per_run: 本次最大处理链接数
    - include_counts: 是否返回全表统计（默认 false，节省 DynamoDB 查询成本）
    - source: 可选来源控制，Yahoo/YAHOO_AUCTION 只跑 Yahoo，Mercari 只跑 Mercari
    """
    event = event if isinstance(event, dict) else {}
    requested_source = normalize_requested_source(event.get("source"))
    table = boto3.resource("dynamodb").Table(os.environ["LINK_CRAWLER_TABLE_NAME"])

    # 恢复超时任务
    recovered = recover_stale_processing_items(table)

    # 播种：队列为空时从首页发现
    seeded = 0
    if not has_queued_items(table, requested_source):
        seeded = seed_from_homepage(table, requested_source)

    # 消费队列
    result = crawl_queue(
        table,
        max_pages=event.get("max_pages"),
        max_depth=event.get("max_depth"),
        max_links_per_run=event.get("max_links_per_run"),
        website_source=requested_source,
    )

    response = {
        "statusCode": 200,
        "message": "队列式 /list3/* 目录采集完成",
        "seeded": seeded,
        "recovered": recovered,
        "metrics": result,
        "source": requested_source or "ALL",
    }

    # 仅手动调试时才统计全表（避免每次 Lambda 执行昂贵的 COUNT 查询）
    if event.get("include_counts"):
        response["queue"] = {
            "queued": count_queue_status(table, "QUEUED"),
            "processing": count_queue_status(table, "PROCESSING"),
            "done": count_queue_status(table, "DONE"),
            "error": count_queue_status(table, "ERROR"),
        }

    return response
