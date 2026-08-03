"""
Yahoo! 拍卖 /list3/* 目录链接增量采集 Lambda。

由 EventBridge 定时触发，从起始页开始广度优先递归爬取，
只保存和递归进入 /list3/* 目录页面。

增量特性：
- 每个目录链接维护状态字段（is_crawled, is_terminal, crawl_status）
- 下次运行时自动跳过已爬取的目录
- 精确标记已到底部的目录
- 支持错误重试
"""

import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit
from collections import deque

import boto3
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============================================================
# 常量配置
# ============================================================

ALLOWED_HOST = "auctions.yahoo.co.jp"
ALLOWED_LIST3_PREFIX = "/list3/"
DEFAULT_START_URL = "https://auctions.yahoo.co.jp/"

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
ENABLE_RECURSIVE = os.getenv("LINK_CRAWLER_ENABLE_RECURSIVE", "true").lower() == "true"
MAX_LINKS_PER_RUN = int(os.getenv("LINK_CRAWLER_MAX_LINKS_PER_RUN", "5000"))


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
            "anchor_text": anchor_text[:500],
            "source_url": source_url,
            "depth": depth,
            "link_type": "list3_directory",
        })
    
    return list3_links


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


def save_discovered_link(table, link: dict) -> None:
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

    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression="""
            SET
                #url = :url,
                anchor_text = if_not_exists(anchor_text, :anchor_text),
                source_url = if_not_exists(source_url, :source_url),
                depth = if_not_exists(depth, :depth),
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
        },
        ExpressionAttributeValues={
            ":url": url,
            ":anchor_text": link.get("anchor_text", ""),
            ":source_url": link.get("source_url", ""),
            ":depth": link.get("depth", 0),
            ":link_type": link.get("link_type", "list3_directory"),
            ":status": "DISCOVERED",
            ":false_value": False,
            ":now": now,
            ":one": 1,
        },
    )


def mark_link_crawled(
    table,
    url: str,
    child_count: int,
    new_child_count: int,
    is_terminal: bool,
    is_exhausted: bool,
) -> None:
    """标记某个 /list3/* 目录已经被递归检索过。"""
    now = datetime.now(timezone.utc).isoformat()
    crawl_id = make_crawl_id(url)

    crawl_status = "TERMINAL" if is_terminal else "CRAWLED"

    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression="""
            SET
                is_crawled = :true_value,
                is_terminal = :is_terminal,
                is_exhausted = :is_exhausted,
                crawl_status = :crawl_status,
                child_count = :child_count,
                new_child_count = :new_child_count,
                crawled_at = :now,
                updated_at = :now
            REMOVE last_error
        """,
        ExpressionAttributeValues={
            ":true_value": True,
            ":is_terminal": is_terminal,
            ":is_exhausted": is_exhausted,
            ":crawl_status": crawl_status,
            ":child_count": child_count,
            ":new_child_count": new_child_count,
            ":now": now,
        },
    )


def mark_link_error(table, url: str, error_message: str) -> None:
    """标记某个目录爬取失败。"""
    now = datetime.now(timezone.utc).isoformat()
    crawl_id = make_crawl_id(url)

    table.update_item(
        Key={"crawl_id": crawl_id},
        UpdateExpression="""
            SET
                crawl_status = :status,
                last_error = :error,
                updated_at = :now
        """,
        ExpressionAttributeValues={
            ":status": "ERROR",
            ":error": error_message[:1000],
            ":now": now,
        },
    )


# ============================================================
# 递归爬取核心（增量版）
# ============================================================

def crawl_recursive(start_url: str, table) -> dict:
    """
    广度优先递归爬取 /list3/* 目录页。

    增量特点：
    - 起始页可以不是 /list3/*
    - 只保存 /list3/* 目录链接
    - 只递归进入 /list3/*
    - 已经 is_crawled=True 的链接，下次不再递归
    - 没有发现子 /list3/* 的链接，标记为 is_terminal=True
    """
    all_directories = []
    visited_pages = set()
    queued_urls = set()
    errors = []

    queue = deque()
    queue.append((start_url, 0))
    queued_urls.add(start_url)

    pages_crawled = 0
    skipped_crawled_count = 0
    terminal_count = 0

    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    logger.info(
        f"开始增量递归采集 /list3/* 目录，起始页: {start_url}，"
        f"最大页面数: {MAX_PAGES}，最大深度: {MAX_DEPTH}"
    )

    while queue and pages_crawled < MAX_PAGES and len(all_directories) < MAX_LINKS_PER_RUN:
        current_url, depth = queue.popleft()

        if current_url in visited_pages:
            continue

        if depth > MAX_DEPTH:
            logger.debug(f"跳过深度 {depth} > {MAX_DEPTH}: {current_url}")
            continue

        # depth=0 是起始页，允许爬取。
        # depth>0 以后，只允许 /list3/*。
        if depth > 0 and not should_crawl(current_url):
            logger.debug(f"跳过非 /list3/* 页面: {current_url}")
            continue

        # 如果是 /list3/*，并且之前已经递归检索过，本次跳过。
        # 起始页如果不是 /list3/*，例如首页，仍然允许每次爬一次作为入口。
        if is_list3_page(current_url) and is_url_already_crawled(table, current_url):
            skipped_crawled_count += 1
            logger.info(f"跳过已检索目录: {current_url}")
            continue

        visited_pages.add(current_url)

        logger.info(f"[{pages_crawled + 1}/{MAX_PAGES}] 深度 {depth}: {current_url}")

        try:
            response = session.get(current_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            pages_crawled += 1

            # 被发现的链接深度应该是当前页面 depth + 1
            new_directories = extract_links_from_page(
                response.text,
                current_url,
                depth + 1
            )

            child_urls = set()
            newly_saved_count = 0
            newly_queued_count = 0
            already_crawled_child_count = 0

            for directory in new_directories:
                if len(all_directories) >= MAX_LINKS_PER_RUN:
                    break

                directory_url = directory["url"]

                # 避免把当前页面自己当成子目录
                if directory_url == current_url:
                    continue

                child_urls.add(directory_url)

                # 先保存发现状态，状态为 DISCOVERED。
                save_discovered_link(table, directory)
                all_directories.append(directory)
                newly_saved_count += 1

                # 如果这个目录已经爬过，下次不再入队
                if is_url_already_crawled(table, directory_url):
                    already_crawled_child_count += 1
                    continue

                # 没爬过的 /list3/* 才进入递归队列
                if (
                    should_crawl(directory_url)
                    and directory_url not in visited_pages
                    and directory_url not in queued_urls
                ):
                    queue.append((directory_url, depth + 1))
                    queued_urls.add(directory_url)
                    newly_queued_count += 1

            child_count = len(child_urls)

            # 真正到底部：页面里没有任何其他 /list3/* 子目录
            is_terminal = child_count == 0

            # 本轮已经没有新的可递归目录
            is_exhausted = newly_queued_count == 0

            if is_terminal:
                terminal_count += 1

            # 只有 /list3/* 页面本身才标记为已爬。
            # 如果 current_url 是首页，不写成目录记录。
            if is_list3_page(current_url):
                mark_link_crawled(
                    table=table,
                    url=current_url,
                    child_count=child_count,
                    new_child_count=newly_queued_count,
                    is_terminal=is_terminal,
                    is_exhausted=is_exhausted,
                )

            logger.info(
                f"  发现 /list3/*: {len(new_directories)} 个, "
                f"子目录: {child_count} 个, "
                f"新增保存: {newly_saved_count} 个, "
                f"已检索子目录跳过: {already_crawled_child_count} 个, "
                f"新增递归队列: {newly_queued_count} 个, "
                f"是否到底: {is_terminal}, "
                f"队列: {len(queue)}, "
                f"累计发现: {len(all_directories)}"
            )

            time.sleep(REQUEST_INTERVAL)

        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败 {current_url}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            if is_list3_page(current_url):
                mark_link_error(table, current_url, error_msg)

            continue

        except Exception as e:
            error_msg = f"处理失败 {current_url}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            if is_list3_page(current_url):
                mark_link_error(table, current_url, error_msg)

            continue

    logger.info(
        f"递归完成: 爬取 {pages_crawled} 页, "
        f"本次发现 {len(all_directories)} 个 /list3/* 目录链接, "
        f"跳过已检索 {skipped_crawled_count} 个, "
        f"到底目录 {terminal_count} 个, "
        f"错误 {len(errors)} 个"
    )

    return {
        "all_directories": all_directories,
        "pages_crawled": pages_crawled,
        "directories_found": len(all_directories),
        "skipped_crawled": skipped_crawled_count,
        "terminal_count": terminal_count,
        "errors": errors,
    }


# ============================================================
# 单页爬取（兼容模式）
# ============================================================

def crawl_single_page(source_url: str) -> list[dict]:
    """单页模式：只提取 /list3/* 目录链接。"""
    try:
        response = requests.get(
            source_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "ja,en;q=0.8",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"请求失败: {source_url}, {e}")
        raise
    
    links = extract_links_from_page(response.text, source_url, 0)
    
    if len(links) > MAX_LINKS_PER_RUN:
        links = links[:MAX_LINKS_PER_RUN]
    
    return links


# ============================================================
# Lambda Handler
# ============================================================

def lambda_handler(event, context):
    """
    EventBridge 入口。
    
    支持事件参数:
        - source_url: 起始 URL (可以是任何允许的 Yahoo 拍卖页面)
        - enable_recursive: 是否启用递归
        - max_pages: 最大爬取页数
        - max_depth: 最大深度
    """
    event = event if isinstance(event, dict) else {}
    
    # 读取参数
    source_url = event.get("source_url") or os.getenv("LINK_CRAWLER_START_URL", DEFAULT_START_URL)
    enable_recursive = event.get("enable_recursive", ENABLE_RECURSIVE)
    max_pages_override = event.get("max_pages")
    max_depth_override = event.get("max_depth")
    
    # 全局覆盖（用于单次调用）
    global MAX_PAGES, MAX_DEPTH
    if max_pages_override:
        MAX_PAGES = int(max_pages_override)
    if max_depth_override:
        MAX_DEPTH = int(max_depth_override)
    
    logger.info(f"启动 /list3/* 目录增量采集: source_url={source_url}, recursive={enable_recursive}, max_pages={MAX_PAGES}, max_depth={MAX_DEPTH}")
    
    # 验证 URL
    if not is_allowed_url(source_url):
        raise ValueError(f"source_url 不是允许的页面: {source_url}")
    
    # 获取 DynamoDB table（提前创建，因为 crawl_recursive 需要）
    table_name = os.environ["LINK_CRAWLER_TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)
    
    # 执行爬取
    if enable_recursive:
        result = crawl_recursive(source_url, table)
        links = result["all_directories"]
        extra_metrics = {
            "pages_crawled": result["pages_crawled"],
            "directories_found": result["directories_found"],
            "skipped_crawled": result["skipped_crawled"],
            "terminal_count": result["terminal_count"],
            "errors": result["errors"],
        }
    else:
        links = crawl_single_page(source_url)
        
        # 单页模式也使用增量保存
        for link in links:
            save_discovered_link(table, link)
        
        extra_metrics = {"pages_crawled": 1}
    
    # 去重，仅用于返回统计
    unique_links = {}
    for link in links:
        if link["url"] not in unique_links:
            unique_links[link["url"]] = link
    
    saved = len(unique_links)
    
    logger.info(
        f"采集完成: 本次发现 /list3/* 目录 {len(links)} 个, "
        f"去重后 {len(unique_links)} 个, "
        f"已写入或更新 DynamoDB {saved} 个"
    )
    
    return {
        "statusCode": 200,
        "message": "/list3/* 目录增量采集完成",
        "source_url": source_url,
        "enable_recursive": enable_recursive,
        "extracted": len(links),
        "unique": len(unique_links),
        "saved_or_updated": saved,
        "metrics": extra_metrics,
    }
