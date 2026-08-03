"""
Yahoo! 拍卖 /list3/* 目录链接采集 Lambda。

由 EventBridge 定时触发，从起始页开始广度优先递归爬取，
只保存和递归进入 /list3/* 目录页面。
"""

import hashlib
import logging
import os
import time
import re
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


def is_listing_page(url: str) -> bool:
    """
    判断是否为需要保存和递归进入的目录页。
    
    当前仅允许：
    - https://auctions.yahoo.co.jp/list3/*
    """
    return is_list3_page(url)


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
# 递归爬取核心
# ============================================================

def crawl_recursive(start_url: str) -> dict:
    """
    广度优先递归爬取 /list3/* 目录页。
    
    起始页可以不是 /list3/*，但只有 /list3/* 会被保存和递归进入。
    
    返回:
        - all_directories: 所有发现的 /list3/* 目录链接
        - pages_crawled: 实际爬取的页面数
        - directories_found: 发现的 /list3/* 目录链接数
        - errors: 错误列表
    """
    all_directories = []
    visited_pages = set()
    saved_directory_urls = set()
    errors = []
    
    # 起始页允许是首页或其他允许页面
    queue = deque()
    queue.append((start_url, 0))
    
    pages_crawled = 0
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    
    logger.info(
        f"开始递归采集 /list3/* 目录，起始页: {start_url}，"
        f"最大页面数: {MAX_PAGES}，最大深度: {MAX_DEPTH}"
    )
    
    while queue and pages_crawled < MAX_PAGES and len(all_directories) < MAX_LINKS_PER_RUN:
        current_url, depth = queue.popleft()
        
        if current_url in visited_pages:
            continue
        
        if depth > MAX_DEPTH:
            logger.debug(f"跳过深度 {depth} > {MAX_DEPTH}: {current_url}")
            continue
        
        # depth=0 是起始页，允许爬取
        # depth>0 时，只允许 /list3/* 页面继续爬取
        if depth > 0 and not should_crawl(current_url):
            logger.debug(f"跳过非 /list3/* 页面: {current_url}")
            continue
        
        visited_pages.add(current_url)
        
        logger.info(f"[{pages_crawled + 1}/{MAX_PAGES}] 深度 {depth}: {current_url}")
        
        try:
            response = session.get(current_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            pages_crawled += 1
            
            # 只提取 /list3/* 目录链接
            new_directories = extract_links_from_page(
                response.text,
                current_url,
                depth
            )
            
            queued_urls = {q[0] for q in queue}
            new_urls_count = 0
            saved_count = 0
            
            for directory in new_directories:
                directory_url = directory["url"]
                
                if directory_url not in saved_directory_urls:
                    all_directories.append(directory)
                    saved_directory_urls.add(directory_url)
                    saved_count += 1
                
                if (
                    should_crawl(directory_url)
                    and directory_url not in visited_pages
                    and directory_url not in queued_urls
                ):
                    queue.append((directory_url, depth + 1))
                    queued_urls.add(directory_url)
                    new_urls_count += 1
            
            logger.info(
                f"  发现 /list3/*: {len(new_directories)} 个, "
                f"新增保存: {saved_count} 个, "
                f"新增递归队列: {new_urls_count} 个, "
                f"队列: {len(queue)}, "
                f"累计目录: {len(all_directories)}"
            )
            
            time.sleep(REQUEST_INTERVAL)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败 {current_url}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue
            
        except Exception as e:
            error_msg = f"处理失败 {current_url}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue
    
    logger.info(
        f"递归完成: 爬取 {pages_crawled} 页, "
        f"收集 {len(all_directories)} 个 /list3/* 目录链接, "
        f"错误 {len(errors)} 个"
    )
    
    return {
        "all_directories": all_directories,
        "pages_crawled": pages_crawled,
        "directories_found": len(all_directories),
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
# DynamoDB 写入
# ============================================================

def save_links(links: list[dict], table) -> int:
    """批量写入 DynamoDB。"""
    if not links:
        return 0
    
    crawled_at = datetime.now(timezone.utc).isoformat()
    saved_count = 0
    
    with table.batch_writer(overwrite_by_pkeys=["crawl_id"]) as batch:
        for link in links:
            try:
                # 生成唯一 ID
                crawl_id = hashlib.sha256(
                    f"{link['source_url']}\n{link['url']}".encode("utf-8")
                ).hexdigest()
                
                batch.put_item(Item={
                    "crawl_id": crawl_id,
                    "url": link["url"],
                    "anchor_text": link.get("anchor_text", ""),
                    "source_url": link["source_url"],
                    "depth": link.get("depth", 0),
                    "link_type": link.get("link_type", "list3_directory"),
                    "crawled_at": crawled_at,
                })
                saved_count += 1
            except Exception as e:
                logger.error(f"写入失败: {link.get('url')}, {e}")
    
    return saved_count


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
    
    logger.info(f"启动 /list3/* 目录采集: source_url={source_url}, recursive={enable_recursive}, max_pages={MAX_PAGES}, max_depth={MAX_DEPTH}")
    
    # 验证 URL
    if not is_allowed_url(source_url):
        raise ValueError(f"source_url 不是允许的页面: {source_url}")
    
    # 执行爬取
    if enable_recursive:
        result = crawl_recursive(source_url)
        links = result["all_directories"]
        extra_metrics = {
            "pages_crawled": result["pages_crawled"],
            "directories_found": result["directories_found"],
            "errors": result["errors"],
        }
    else:
        links = crawl_single_page(source_url)
        extra_metrics = {"pages_crawled": 1}
    
    # 去重（按 URL）
    unique_links = {}
    for link in links:
        if link["url"] not in unique_links:
            unique_links[link["url"]] = link
    
    # 写入 DynamoDB
    table_name = os.environ["LINK_CRAWLER_TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)
    saved = save_links(list(unique_links.values()), table)
    
    logger.info(f"采集完成: 提取 /list3/* 目录 {len(links)} 个, 去重后 {len(unique_links)} 个, 写入 {saved} 个")
    
    return {
        "statusCode": 200,
        "message": "/list3/* 目录采集完成",
        "source_url": source_url,
        "enable_recursive": enable_recursive,
        "extracted": len(links),
        "unique": len(unique_links),
        "saved": saved,
        "metrics": extra_metrics,
    }
