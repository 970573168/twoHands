"""Yahoo! 拍卖链接采集 Lambda。

由 EventBridge 定时触发，读取页面中的 ``a[href]``，经过简单的 robots 路径
过滤后将链接、锚文本和来源页面写入 DynamoDB。
"""

import hashlib
import logging
import os
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit

import boto3
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_HOST = "auctions.yahoo.co.jp"
DEFAULT_START_URL = "https://auctions.yahoo.co.jp/"
DISALLOW = (
    "/alert/",
    "/closeduser/",
    "/members/",
    "/sell/",
    "/user/",
    "/config/",
    "/search/advanced",
    "/follow/",
)
USER_AGENT = os.getenv(
    "LINK_CRAWLER_USER_AGENT",
    "TwoHandsLinkCrawler/1.0 (+https://auctions.yahoo.co.jp/robots.txt)",
)
REQUEST_TIMEOUT = float(os.getenv("LINK_CRAWLER_TIMEOUT", "20"))
MAX_LINKS = int(os.getenv("LINK_CRAWLER_MAX_LINKS", "500"))


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
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    absolute = urljoin(source_url, href.strip())
    try:
        parsed = urlsplit(absolute)
        normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))
    except ValueError:
        return None
    return normalized if is_allowed_url(normalized) else None


def extract_links(html: str, source_url: str, limit: int = MAX_LINKS) -> list[dict]:
    """提取去重后的链接与可见锚文本；同一 URL 保留首次出现的文字。"""
    links = []
    seen = set()
    soup = BeautifulSoup(html or "", "html.parser")
    for anchor in soup.select("a[href]"):
        url = normalize_url(anchor.get("href"), source_url)
        if not url or url in seen:
            continue
        seen.add(url)
        links.append({
            "url": url,
            "anchor_text": " ".join(anchor.get_text(" ", strip=True).split()),
            "source_url": source_url,
        })
        if len(links) >= limit:
            break
    return links


def save_links(links: list[dict], table) -> int:
    """批量写入 DynamoDB；crawl_id 避免同一链接在不同来源页之间互相覆盖。"""
    crawled_at = datetime.now(timezone.utc).isoformat()
    with table.batch_writer(overwrite_by_pkeys=["crawl_id"]) as batch:
        for link in links:
            batch.put_item(Item={
                "crawl_id": hashlib.sha256(
                    f"{link['source_url']}\n{link['url']}".encode("utf-8")
                ).hexdigest(),
                **link,
                "crawled_at": crawled_at,
            })
    return len(links)


def lambda_handler(event, context):
    """EventBridge 入口；事件可通过 ``source_url`` 临时指定站内起始页。"""
    event = event if isinstance(event, dict) else {}
    source_url = event.get("source_url") or os.getenv("LINK_CRAWLER_START_URL", DEFAULT_START_URL)
    if not is_allowed_url(source_url):
        raise ValueError("source_url 必须是 auctions.yahoo.co.jp 的允许抓取页面")

    response = requests.get(
        source_url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.8"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    links = extract_links(response.text, source_url)
    table_name = os.environ["LINK_CRAWLER_TABLE_NAME"]
    saved = save_links(links, boto3.resource("dynamodb").Table(table_name))
    logger.info("链接采集完成 source_url=%s extracted=%d saved=%d", source_url, len(links), saved)
    return {
        "statusCode": 200,
        "message": "链接采集完成",
        "source_url": source_url,
        "extracted": len(links),
        "saved": saved,
    }
