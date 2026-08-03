"""
Yahoo! 拍卖链接递归采集 Lambda。

由 EventBridge 定时触发，从起始页开始广度优先递归爬取所有商品列表页，
提取商品链接和目录链接，写入 DynamoDB。
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

def is_listing_page(url: str) -> bool:
    """
    判断是否为商品列表页（需要继续递归）。
    
    Yahoo 拍卖列表页格式：
    - /list3/数字-xxx.html   (大分类列表，如 /list3/23632-category.html)
    - /list/数字-xxx.html    (子分类列表)
    - /category/数字/        (分类页)
    - /category/数字?p=页码  (带分页)
    """
    if not url:
        return False
    parsed = urlsplit(url)
    path = parsed.path
    
    # /list3/ 或 /list/ 开头，后面跟数字
    if re.search(r'/list3?/\d+', path):
        return True
    
    # /category/ 开头
    if path.startswith('/category/'):
        return True
    
    # 首页也算作列表页（作为起点）
    if path in ("/", ""):
        return True
    
    return False


def is_item_page(url: str) -> bool:
    """判断是否为商品详情页（只保存链接，不递归）。"""
    if not url:
        return False
    parsed = urlsplit(url)
    path = parsed.path
    return '/auction/' in path or '/item/' in path


def should_crawl(url: str) -> bool:
    """判断一个 URL 是否应该被爬取（是列表页且不是商品详情页）。"""
    if not url:
        return False
    # 商品详情页不爬
    if is_item_page(url):
        return False
    # 列表页才爬
    return is_listing_page(url)


# ============================================================
# 链接提取
# ============================================================

def extract_links_from_page(html: str, source_url: str, depth: int) -> tuple[list[dict], list[str], list[dict]]:
    """
    从 HTML 中提取所有链接，分类返回。
    
    返回:
        - item_links: 商品详情页链接 (需要保存)
        - listing_urls: 子列表页链接 (需要继续递归)
        - other_links: 其他链接 (可选保存)
    """
    item_links = []
    listing_urls = []
    other_links = []
    seen = set()
    
    if not html:
        return item_links, listing_urls, other_links
    
    soup = BeautifulSoup(html, "html.parser")
    
    for anchor in soup.select("a[href]"):
        url = normalize_url(anchor.get("href"), source_url)
        if not url or url in seen:
            continue
        seen.add(url)
        
        anchor_text = " ".join(anchor.get_text(" ", strip=True).split())
        link_data = {
            "url": url,
            "anchor_text": anchor_text[:500],  # 限制长度
            "source_url": source_url,
            "depth": depth,
        }
        
        if is_item_page(url):
            item_links.append(link_data)
        elif is_listing_page(url):
            # 只保存 URL 用于递归，不保存完整数据（避免重复）
            listing_urls.append(url)
        else:
            other_links.append(link_data)
    
    return item_links, listing_urls, other_links


# ============================================================
# 递归爬取核心
# ============================================================

def crawl_recursive(start_url: str) -> dict:
    """
    广度优先递归爬取所有商品列表页。
    
    返回:
        - all_items: 所有商品链接列表
        - pages_crawled: 实际爬取的页面数
        - listing_urls_found: 发现的列表页总数
        - errors: 错误列表
    """
    all_items = []
    all_listing_urls = set()
    visited_pages = set()
    errors = []
    
    # 初始化队列
    queue = deque()
    if should_crawl(start_url):
        queue.append((start_url, 0))
    else:
        # 如果起始页不是列表页，尝试从首页开始
        logger.warning(f"起始页不是列表页: {start_url}，回退到首页")
        queue.append((DEFAULT_START_URL, 0))
    
    pages_crawled = 0
    
    # 创建 Session 复用连接
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    
    logger.info(f"开始递归爬取，起始页: {queue[0][0]}，最大页面数: {MAX_PAGES}，最大深度: {MAX_DEPTH}")
    
    while queue and pages_crawled < MAX_PAGES and len(all_items) < MAX_LINKS_PER_RUN:
        current_url, depth = queue.popleft()
        
        # 跳过已访问或超出深度
        if current_url in visited_pages:
            continue
        if depth > MAX_DEPTH:
            logger.debug(f"跳过深度 {depth} > {MAX_DEPTH}: {current_url}")
            continue
        
        # 再次确认是否应该爬取
        if not should_crawl(current_url):
            logger.debug(f"跳过非列表页: {current_url}")
            continue
        
        visited_pages.add(current_url)
        all_listing_urls.add(current_url)
        
        logger.info(f"[{pages_crawled + 1}/{MAX_PAGES}] 深度 {depth}: {current_url}")
        
        try:
            response = session.get(current_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            pages_crawled += 1
            
            # 提取链接
            item_links, new_listing_urls, other_links = extract_links_from_page(
                response.text, current_url, depth
            )
            
            # 保存商品链接
            all_items.extend(item_links)
            
            # 将新发现的列表页加入队列（去重）
            new_urls_count = 0
            for new_url in new_listing_urls:
                if new_url not in visited_pages and new_url not in [q[0] for q in queue]:
                    queue.append((new_url, depth + 1))
                    new_urls_count += 1
            
            logger.info(
                f"  发现: {len(item_links)} 个商品, {new_urls_count} 个新列表页, "
                f"队列: {len(queue)}, 总计商品: {len(all_items)}"
            )
            
            # 礼貌性延迟
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
        f"发现 {len(all_listing_urls)} 个列表页, "
        f"收集 {len(all_items)} 个商品链接, "
        f"错误 {len(errors)} 个"
    )
    
    return {
        "all_items": all_items,
        "pages_crawled": pages_crawled,
        "listing_urls_found": len(all_listing_urls),
        "listing_urls": list(all_listing_urls),
        "errors": errors,
    }


# ============================================================
# 单页爬取（兼容模式）
# ============================================================

def crawl_single_page(source_url: str) -> list[dict]:
    """单页爬取模式（原有功能，兼容）。"""
    try:
        response = requests.get(
            source_url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.8"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"请求失败: {source_url}, {e}")
        raise
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    seen = set()
    
    for anchor in soup.select("a[href]"):
        url = normalize_url(anchor.get("href"), source_url)
        if not url or url in seen:
            continue
        seen.add(url)
        links.append({
            "url": url,
            "anchor_text": " ".join(anchor.get_text(" ", strip=True).split()),
            "source_url": source_url,
            "depth": 0,
        })
        if len(links) >= MAX_LINKS_PER_RUN:
            break
    
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
        - source_url: 起始 URL
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
    
    logger.info(f"启动链接采集: source_url={source_url}, recursive={enable_recursive}, max_pages={MAX_PAGES}, max_depth={MAX_DEPTH}")
    
    # 验证 URL
    if not is_allowed_url(source_url):
        raise ValueError(f"source_url 不是允许的页面: {source_url}")
    
    # 执行爬取
    if enable_recursive:
        result = crawl_recursive(source_url)
        links = result["all_items"]
        extra_metrics = {
            "pages_crawled": result["pages_crawled"],
            "listing_urls_found": result["listing_urls_found"],
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
    
    logger.info(f"采集完成: 提取 {len(links)} 条, 去重后 {len(unique_links)} 条, 写入 {saved} 条")
    
    return {
        "statusCode": 200,
        "message": "链接采集完成",
        "source_url": source_url,
        "enable_recursive": enable_recursive,
        "extracted": len(links),
        "unique": len(unique_links),
        "saved": saved,
        "metrics": extra_metrics,
    }
