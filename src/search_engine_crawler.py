"""
Yahoo! 拍卖 /list3/* + Mercari 目录链接持久化队列采集 Lambda。

Mercari 与 Yahoo 都使用 requests 静态爬取；Mercari 目录仅解析公开 HTML。
"""

import hashlib
import logging
import os
import re
import time
import json
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs

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
MAX_PAGES = int(os.getenv("LINK_CRAWLER_MAX_PAGES", "20"))
MAX_DEPTH = int(os.getenv("LINK_CRAWLER_MAX_DEPTH", "5"))
REQUEST_INTERVAL = float(os.getenv("LINK_CRAWLER_REQUEST_INTERVAL", "0.8"))
MAX_LINKS_PER_RUN = int(os.getenv("LINK_CRAWLER_MAX_LINKS_PER_RUN", "1000"))
GSI_QUERY_PAGE_SIZE = int(os.getenv("LINK_CRAWLER_GSI_PAGE_SIZE", "25"))
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
        return canonicalize_mercari_category_url(url) is not None
    path = parsed.path or "/"
    return not any(path == rule.rstrip("/") or path.startswith(rule) for rule in DISALLOW)


def canonicalize_category_url(url: str) -> str | None:
    """只保留支持网站的目录/叶子分类页，并归一化为标准 URL。"""
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return None

    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.hostname == MERCARI_HOST:
        return canonicalize_mercari_category_url(url)

    path = parsed.path or "/"
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
        return (parse_qs(parsed.query).get("category_id") or [None])[0]
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
    """判断一个 URL 是否应该被递归爬取；Mercari search leaf 只保存不递归。"""
    if website_source_from_url(url) == MERCARI_SOURCE:
        return is_mercari_directory_url(url)
    return canonicalize_category_url(url) is not None


# ============================================================
# Mercari 静态目录链接提取（requests + BeautifulSoup）
# ============================================================

def canonicalize_mercari_category_url(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return None
    if parsed.scheme not in {"http", "https"} or parsed.hostname != MERCARI_HOST:
        return None
    path = parsed.path or "/"
    if path not in {"/categories", "/search"}:
        return None
    category_id = (parse_qs(parsed.query).get("category_id") or [""])[0].strip()
    if path == "/categories" and not category_id:
        return urlunsplit(("https", MERCARI_HOST, "/categories", "", ""))
    if not category_id:
        return None
    return urlunsplit(("https", MERCARI_HOST, path, f"category_id={category_id}", ""))

def classify_mercari_category_url(url: str) -> dict | None:
    canonical = canonicalize_mercari_category_url(url)
    if not canonical:
        return None
    parsed = urlsplit(canonical)
    if parsed.path == "/categories":
        return {"url": canonical, "link_type": "mercari_directory", "is_leaf": False}
    if parsed.path == "/search":
        return {"url": canonical, "link_type": "mercari_search_leaf", "is_leaf": True}
    return None

def is_mercari_directory_url(url: str) -> bool:
    info = classify_mercari_category_url(url)
    return bool(info and info["link_type"] == "mercari_directory")

def is_mercari_leaf_url(url: str) -> bool:
    info = classify_mercari_category_url(url)
    return bool(info and info["link_type"] == "mercari_search_leaf")

def extract_mercari_links_from_page(html: str, source_url: str, depth: int) -> list[dict]:
    links, seen = [], set()
    if not html:
        return links
    soup = BeautifulSoup(html, "html.parser")

    all_anchors = soup.select("a[href]")
    category_anchors = soup.select('a[href*="category_id"]')
    
    logger.info(
        "Mercari HTML diagnostic: all_anchors=%s category_anchors=%s "
        "category_id_occurrences=%s categories_occurrences=%s search_occurrences=%s",
        len(all_anchors),
        len(category_anchors),
        html.count("category_id"),
        html.count("/categories"),
        html.count("/search"),
    )
    
    for anchor in category_anchors[:10]:
        logger.info(
            "Mercari candidate href=%s text=%s",
            anchor.get("href"),
            clean_anchor_text(anchor.get_text(" ", strip=True)),
        )
    for anchor in soup.select('a[href*="category_id"]'):
        href = anchor.get("href")
        absolute = urljoin(source_url, href or "")
        info = classify_mercari_category_url(absolute)
        if not info or info["url"] in seen:
            continue
        text = clean_anchor_text(anchor.get_text(" ", strip=True))
        if text in BAD_ANCHOR_TEXTS:
            continue
        seen.add(info["url"])
        links.append({
            "url": info["url"], "category_id": extract_category_id(info["url"]) or "",
            "category_name": text, "anchor_text": text, "source_url": source_url,
            "website_source": MERCARI_SOURCE, "source": MERCARI_SOURCE,
            "depth": depth, "link_type": info["link_type"], "is_leaf": info["is_leaf"],
        })
    return links


# ============================================================
# Yahoo 链接提取（使用 requests/BeautifulSoup）
# ============================================================

def clean_anchor_text(text: str) -> str:
    """清洗 anchor 文本，去除多余空白。"""
    return " ".join((text or "").split())[:500]


def extract_yahoo_links_from_page(html: str, source_url: str, depth: int) -> list[dict]:
    """
    从 Yahoo 页面提取 /list3/* 目录链接。
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
        link_type = "list3_directory"
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


def extract_links_from_page(html: str, source_url: str, depth: int) -> list[dict]:
    """
    从页面提取链接，根据来源自动选择提取方式。
    """
    if not html:
        return []
    
    # 判断是否是 Yahoo 页面
    if 'auctions.yahoo.co.jp' in source_url:
        return extract_yahoo_links_from_page(html, source_url, depth)
    
    if MERCARI_HOST in source_url:
        return extract_mercari_links_from_page(html, source_url, depth)
    return []


# ============================================================
# 统一的链接提取入口
# ============================================================

def extract_links_by_source(url: str, html: str, depth: int, 
                            use_selenium: bool = False) -> list[dict]:
    """
    根据 URL 来源使用不同的提取策略。
    
    参数:
        url: 当前页面 URL
        html: 页面 HTML 内容（对 Yahoo 有效）
        depth: 当前深度
        use_selenium: 旧参数，已忽略；Mercari 不再使用浏览器驱动
    
    返回:
        目录链接列表
    """
    source = website_source_from_url(url)
    
    if source == MERCARI_SOURCE:
        return extract_mercari_links_from_page(html, url, depth)
    elif source == YAHOO_SOURCE:
        # Yahoo 使用静态 HTML
        return extract_yahoo_links_from_page(html, url, depth)
    else:
        logger.warning(f"未知的网站来源: {url}")
        return []


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
                is_leaf = if_not_exists(is_leaf, :is_leaf),
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
            ":is_leaf": bool(link.get("is_leaf", False)),
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
    """将当前 PROCESSING 任务标记为 DONE。"""
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
    """简易扫描恢复超时任务。"""
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


def _get_with_retries(session, url: str):
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 429 or 500 <= response.status_code < 600:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else REQUEST_INTERVAL * attempt
                logger.warning("HTTP retryable status: url=%s status=%s attempt=%s retry_after=%s", url, response.status_code, attempt, retry_after)
                if attempt < MAX_ATTEMPTS:
                    time.sleep(max(delay, REQUEST_INTERVAL))
                    continue
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            logger.warning("HTTP request failed: url=%s attempt=%s error=%s", url, attempt, exc)
            if attempt < MAX_ATTEMPTS:
                time.sleep(REQUEST_INTERVAL * attempt)
    if last_exc:
        raise last_exc
    response.raise_for_status()
    return response

def seed_from_homepage(table, website_source: str | None = None) -> dict:
    """队列为空时从目标网站首页发现并持久化第一层目录，并返回可观测结果。"""
    result = {
        "pages_requested": 0,
        "http_status": None,
        "html_length": 0,
        "links_found": 0,
        "inserted": 0,
        "existing": 0,
        "errors": [],
    }
    session = _http_session()
    start_urls = (START_URL_BY_SOURCE[website_source],) if website_source else START_URLS
    for start_url in start_urls:
        source = website_source_from_url(start_url)
        try:
            result["pages_requested"] += 1
            response = _get_with_retries(session, start_url)
            html = response.text or ""
            content_type = response.headers.get("Content-Type", "")
            final_url = getattr(response, "url", start_url) or start_url
            status_code = getattr(response, "status_code", None)
            result["http_status"] = status_code
            result["html_length"] += len(html)
            if source == MERCARI_SOURCE:
                logger.info(
                    "Mercari seed HTTP: website_source=%s requested_url=%s final_url=%s status=%s html_length=%s content_type=%s",
                    source, start_url, final_url, status_code, len(html), content_type,
                )
            extractor = extract_mercari_links_from_page if source == MERCARI_SOURCE else extract_yahoo_links_from_page
            links = extractor(html, final_url, depth=1)
            result["links_found"] += len(links)
            if source == MERCARI_SOURCE:
                logger.info("Mercari seed parse: website_source=%s links_found=%s", source, len(links))
        except Exception as exc:
            message = f"seed page failed url={start_url}: {exc}"
            logger.exception(message)
            result["errors"].append(message)
            continue

        for link in links:
            try:
                write_result = enqueue_discovered_link(table, link, root_url=start_url)
                if write_result["is_new"]:
                    result["inserted"] += 1
                else:
                    result["existing"] += 1
            except Exception as exc:
                message = (
                    "seed DynamoDB write failed "
                    f"category_id={link.get('category_id', '')} "
                    f"category_name={link.get('category_name', '')} "
                    f"url={link.get('url', '')}: {exc}"
                )
                logger.exception(message)
                result["errors"].append(message)
                continue
    return result


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
# 队列消费
# ============================================================

def crawl_queue(table, max_pages: int | None = None, max_depth: int | None = None,
                max_links_per_run: int | None = None, website_source: str | None = None) -> dict:
    """消费 DynamoDB 持久化队列。"""
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
            
            link_type = claimed.get("link_type") or (classify_mercari_category_url(current_url) or {}).get("link_type")
            if link_type == "mercari_search_leaf" or is_mercari_leaf_url(current_url):
                logger.info("Mercari terminal leaf: website_source=%s current_url=%s category_id=%s link_type=%s depth=%s", MERCARI_SOURCE, current_url, extract_category_id(current_url), "mercari_search_leaf", depth)
                mark_queue_done(table, claimed["crawl_id"], 0, 0, True)
                continue
            if depth > depth_limit:
                mark_queue_done(table, claimed["crawl_id"], 0, 0, True)
                continue
            if not should_crawl(current_url):
                mark_queue_done(table, claimed["crawl_id"], 0, 0, False)
                continue
            
            try:
                source = website_source_from_url(current_url)
                response = _get_with_retries(session, current_url)
                html = response.text
                pages_crawled += 1
                if source == MERCARI_SOURCE:
                    discovered = extract_mercari_links_from_page(html, current_url, depth + 1)
                else:
                    discovered = extract_yahoo_links_from_page(html, current_url, depth + 1)
                
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
                logger.info("Directory crawl page: website_source=%s current_url=%s category_id=%s link_type=%s depth=%s discovered_count=%s new_count=%s pages_crawled=%s", source, current_url, extract_category_id(current_url), link_type or "list3_directory", depth, child_count, page_new, pages_crawled)
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
    
    event 参数:
        - max_pages: 本次最大爬取页数
        - max_depth: 最大爬取深度
        - max_links_per_run: 本次最大处理链接数
        - include_counts: 是否返回全表统计
        - source: 可选来源控制 (YAHOO_AUCTION / MERCARI)
    """
    event = event if isinstance(event, dict) else {}
    requested_source = normalize_requested_source(event.get("source"))
    table_name = os.environ["LINK_CRAWLER_TABLE_NAME"]
    logger.info("Link crawler table: %s", table_name)
    table = boto3.resource("dynamodb").Table(table_name)

    # 恢复超时任务
    recovered = recover_stale_processing_items(table)

    # 播种：队列为空时从首页发现
    seed = {"pages_requested": 0, "http_status": None, "html_length": 0, "links_found": 0, "inserted": 0, "existing": 0, "errors": []}
    if not has_queued_items(table, requested_source):
        seed = seed_from_homepage(table, requested_source)
    seeded = int(seed.get("inserted", 0))

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
        "message": "队列式目录采集完成",
        "seeded": seeded,
        "seed": seed,
        "recovered": recovered,
        "metrics": result,
        "source": requested_source or "ALL",
    }

    # 仅手动调试时才统计全表
    if event.get("include_counts"):
        response["table_name"] = table_name
        response["queue"] = {
            "queued": count_queue_status(table, "QUEUED"),
            "processing": count_queue_status(table, "PROCESSING"),
            "done": count_queue_status(table, "DONE"),
            "error": count_queue_status(table, "ERROR"),
        }

    return response

# ============================================================
# 旧测试/运行时代码兼容 wrapper
# ============================================================

def extract_links(html: str, source_url: str, limit: int | None = None) -> list[dict]:
    """兼容旧 API：提取同站普通链接，不影响正式目录 crawler。"""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links, seen = [], set()
    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        absolute = urljoin(source_url, href.strip())
        try:
            parsed = urlsplit(absolute)
            normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))
        except ValueError:
            continue
        if not is_allowed_url(normalized) or normalized in seen:
            continue
        seen.add(normalized)
        links.append({"url": normalized, "anchor_text": clean_anchor_text(anchor.get_text(" ", strip=True)), "source_url": source_url})
        if limit is not None and len(links) >= limit:
            break
    return links


def save_discovered_link(table, link: dict, root_url: str | None = None) -> dict:
    return enqueue_discovered_link(table, link, root_url or link.get("source_url") or link["url"])


def count_remaining_unvisited(table) -> int:
    return count_queue_status(table, "QUEUED")


def get_next_unvisited_url(table) -> str | None:
    items = get_queued_items(table, 1)
    return items[0].get("url") if items else None
