"""
Yahoo! 拍卖 /list3/* 目录链接增量采集 Lambda。

由 EventBridge 定时触发，智能选择起始点：
- 表为空时：从雅虎首页开始
- 表不为空时：从最久未爬取的 /list3/* 链接开始

只保存和递归进入 /list3/* 目录页面。

增量特性：
- 每个目录链接维护状态字段（is_crawled, crawl_status）
- 优先爬取最久入库的未爬取链接
- 已爬过但未穷尽的目录会重新访问以发现新子目录
- 精确标记已到底部的目录
- 支持错误重试
"""

import hashlib
import logging
import os
import re
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
        # 查询未爬取的 /list3/* 链接，按入库时间升序
        response = table.query(
            IndexName="link_type-first_seen_at-index",
            KeyConditionExpression="link_type = :link_type",
            FilterExpression="is_crawled = :false_val OR crawl_status = :status",
            ExpressionAttributeValues={
                ":link_type": "list3_directory",
                ":false_val": False,
                ":status": "DISCOVERED",
            },
            ScanIndexForward=True,  # 升序，最旧的在前
            Limit=1,
        )
        
        items = response.get("Items", [])
        if items:
            return items[0].get("url")
        
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

    try:
        table.update_item(
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
        )
    except Exception as e:
        logger.error(f"保存链接失败 {url}: {e}")


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

def crawl_recursive(start_url: str, table, is_cold_start: bool = False) -> dict:
    """
    广度优先递归爬取 /list3/* 目录页。

    增量特点：
    - 冷启动时从雅虎首页开始
    - 热启动时从最久未爬取的 /list3/* 链接开始
    - 已爬过但未穷尽的目录会重新访问以发现新子目录
    - 已经 is_crawled=True 且 is_exhausted=True 的链接，下次不再递归
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

    start_type = "冷启动（从首页开始）" if is_cold_start else f"热启动（从 {start_url} 开始）"
    logger.info(
        f"{start_type}，"
        f"最大页面数: {MAX_PAGES}，最大深度: {MAX_DEPTH}"
    )

    while queue and pages_crawled < MAX_PAGES and len(all_directories) < MAX_LINKS_PER_RUN:
        current_url, depth = queue.popleft()

        if current_url in visited_pages:
            continue

        if depth > MAX_DEPTH:
            logger.debug(f"跳过深度 {depth} > {MAX_DEPTH}: {current_url}")
            continue

        # 首页（非 /list3/*）在冷启动时允许爬取
        # 热启动时起始点已经是 /list3/*，深度从 0 开始，所以 depth>0 过滤仍然有效
        if depth > 0 and not should_crawl(current_url):
            logger.debug(f"跳过非 /list3/* 页面: {current_url}")
            continue

        # 如果是 /list3/*，并且之前已经递归检索过且已穷尽，跳过
        # 已爬过但未穷尽的目录会重新爬取以发现新子目录
        if is_list3_page(current_url) and is_url_already_crawled(table, current_url):
            record = get_link_record(table, current_url)
            if record and (record.get("is_exhausted") or record.get("is_terminal")):
                skipped_crawled_count += 1
                logger.info(f"跳过已检索且已穷尽目录: {current_url}")
                continue
            else:
                # 已爬过但未穷尽，重新爬取以发现新子目录
                logger.info(f"重新爬取未穷尽目录: {current_url}")

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

                # 先保存发现状态，状态为 DISCOVERED
                save_discovered_link(table, directory)
                all_directories.append(directory)
                newly_saved_count += 1

                # 检查子目录是否已爬过
                already_crawled = is_url_already_crawled(table, directory_url)

                if already_crawled:
                    already_crawled_child_count += 1

                # 进入递归队列的条件：
                # 1. 是 /list3/* 页面
                # 2. 未被访问过
                # 3. 未在队列中
                # 4. 如果已爬过，需要检查是否还有未爬取的子孙目录
                if (
                    should_crawl(directory_url)
                    and directory_url not in visited_pages
                    and directory_url not in queued_urls
                ):
                    if already_crawled:
                        # 已爬过的目录：检查是否已穷尽
                        record = get_link_record(table, directory_url)
                        if record and (record.get("is_exhausted") or record.get("is_terminal")):
                            logger.debug(f"  跳过已穷尽子目录: {directory_url}")
                            continue
                        else:
                            logger.debug(f"  重新入队未穷尽子目录: {directory_url}")

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

            # 只有 /list3/* 页面本身才标记为已爬
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
                f"已检索子目录: {already_crawled_child_count} 个, "
                f"新增递归队列: {newly_queued_count} 个, "
                f"是否到底: {is_terminal}, "
                f"是否穷尽: {is_exhausted}, "
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
        f"跳过已穷尽 {skipped_crawled_count} 个, "
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
# Lambda Handler
# ============================================================

def lambda_handler(event, context):
    """
    EventBridge 入口。
    
    智能起始点选择：
    - 表为空（首次运行）：从雅虎拍卖首页开始
    - 表不为空（后续运行）：从最久未爬取的 /list3/* 链接开始
    
    支持事件参数:
        - max_pages: 最大爬取页数（可选）
        - max_depth: 最大深度（可选）
    """
    event = event if isinstance(event, dict) else {}
    
    # 读取参数（不再需要 source_url）
    max_pages_override = event.get("max_pages")
    max_depth_override = event.get("max_depth")
    
    # 全局覆盖（用于单次调用）
    global MAX_PAGES, MAX_DEPTH
    if max_pages_override:
        MAX_PAGES = int(max_pages_override)
    if max_depth_override:
        MAX_DEPTH = int(max_depth_override)
    
    # 获取 DynamoDB table
    table_name = os.environ["LINK_CRAWLER_TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)
    
    # 智能选择起始 URL
    is_cold_start = False
    start_url = DEFAULT_START_URL
    
    # 检查表是否为空
    if is_table_empty(table):
        is_cold_start = True
        logger.info("表为空，冷启动：从雅虎首页开始采集")
    else:
        # 从表中获取最久未爬取的 /list3/* 链接
        next_url = get_next_unvisited_url(table)
        if next_url:
            start_url = next_url
            logger.info(f"热启动：从最久未爬取链接开始 - {start_url}")
        else:
            # 所有链接都已爬取完毕
            logger.info("所有 /list3/* 链接已爬取完毕，检查首页是否有新链接")
            is_cold_start = True
            start_url = DEFAULT_START_URL
    
    logger.info(
        f"启动 /list3/* 目录增量采集: "
        f"start_url={start_url}, "
        f"max_pages={MAX_PAGES}, "
        f"max_depth={MAX_DEPTH}, "
        f"is_cold_start={is_cold_start}"
    )
    
    # 验证 URL
    if not is_allowed_url(start_url):
        raise ValueError(f"start_url 不是允许的页面: {start_url}")
    
    # 执行爬取
    result = crawl_recursive(start_url, table, is_cold_start)
    links = result["all_directories"]
    
    # 去重，仅用于返回统计
    unique_links = {}
    for link in links:
        if link["url"] not in unique_links:
            unique_links[link["url"]] = link
    
    saved = len(unique_links)
    
    # 统计剩余未爬取数量
    remaining = 0
    try:
        response = table.query(
            IndexName="link_type-first_seen_at-index",
            KeyConditionExpression="link_type = :link_type",
            FilterExpression="is_crawled = :false_val OR crawl_status = :status",
            ExpressionAttributeValues={
                ":link_type": "list3_directory",
                ":false_val": False,
                ":status": "DISCOVERED",
            },
            Select="COUNT",
        )
        remaining = response.get("Count", 0)
    except Exception:
        pass
    
    logger.info(
        f"采集完成: 本次发现 /list3/* 目录 {len(links)} 个, "
        f"去重后 {len(unique_links)} 个, "
        f"已写入或更新 DynamoDB {saved} 个, "
        f"剩余未爬取约 {remaining} 个"
    )
    
    return {
        "statusCode": 200,
        "message": "/list3/* 目录增量采集完成",
        "start_url": start_url,
        "is_cold_start": is_cold_start,
        "extracted": len(links),
        "unique": len(unique_links),
        "saved_or_updated": saved,
        "remaining_unvisited": remaining,
        "metrics": {
            "pages_crawled": result["pages_crawled"],
            "directories_found": result["directories_found"],
            "skipped_crawled": result["skipped_crawled"],
            "terminal_count": result["terminal_count"],
            "errors": result["errors"],
        },
    }
