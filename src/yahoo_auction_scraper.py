import os
import re
import json
import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote

import boto3
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============ 环境变量 ============
BASE_URL = os.getenv("BASE_URL", "https://auctions.yahoo.co.jp/closedsearch/closedsearch")
DEFAULT_PARAMS = os.getenv("DEFAULT_PARAMS", "n=50&select=6&mode=3&dest_pref_code=23")
MAX_PAGES = int(os.getenv("MAX_PAGES", "1"))
TABLE_NAME = os.getenv("TABLE_NAME", "YahooAuctionItems")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def get_items_per_page():
    """从 DEFAULT_PARAMS 中解析每页件数 n，默认 50"""
    for p in DEFAULT_PARAMS.replace("&amp;", "&").split("&"):
        if p.startswith("n="):
            try:
                return int(p.split("=")[1])
            except ValueError:
                pass
    return 50


def build_url(keyword, page):
    """构建请求 URL，正确计算分页参数 b"""
    params = {}
    for p in DEFAULT_PARAMS.replace("&amp;", "&").split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v

    n = int(params.get("n", "50"))
    params["p"] = keyword
    params["b"] = str((page - 1) * n + 1)   # Yahoo 分页起始偏移
    return f"{BASE_URL}?{urlencode(params, quote_via=quote)}"


def lambda_handler(event, context):
    """主入口"""
    keyword = event.get("keyword")
    if not keyword:
        logger.error("Missing 'keyword' in event")
        return {"statusCode": 400, "body": "Missing keyword"}

    logger.info(f"Scraping for keyword: {keyword}")
    items = scrape_auctions(keyword)

    if not items:
        logger.info("No items found")
        return {"statusCode": 200, "body": "No items"}

    saved = save_items(items)
    return {
        "statusCode": 200,
        "body": json.dumps({"scraped": len(items), "saved": saved})
    }


def scrape_auctions(keyword):
    """多页抓取"""
    all_items = []
    per_page = get_items_per_page()

    for page in range(1, MAX_PAGES + 1):
        url = build_url(keyword, page)
        logger.info(f"Fetching page {page}: {url}")
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Request failed: {e}")
            continue

        items = parse_html(resp.text)
        if not items:
            break
        all_items.extend(items)

        # 如果本页数量少于每页数量，说明没有下一页
        if len(items) < per_page:
            break

    return all_items


def parse_html(html):
    """解析 HTML，使用稳定选择器"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # 定位商品列表容器（id 稳定）
    container = soup.select_one("#closedSearchItems")
    if not container:
        logger.warning("No #closedSearchItems found")
        return items

    # 找到 ul 列表（通常只有一层）
    ul = container.find("ul")
    if not ul:
        logger.warning("No ul inside #closedSearchItems")
        return items

    # 遍历直接子 li（每个商品）
    for li in ul.find_all("li", recursive=False):
        try:
            item = parse_item(li)
            if item:
                items.append(item)
        except Exception as e:
            logger.warning(f"Failed to parse item: {e}")
            continue

    return items


def parse_item(li):
    """解析单个商品，全部使用稳定选择器"""
    # ---- 标题 & 拍卖ID ----
    link = li.find("a", href=re.compile(r"/auction/"))
    if not link:
        return None
    href = link.get("href")
    auction_id = None
    if href:
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            auction_id = m.group(1)

    title = link.get("title") or link.get_text(strip=True)

    # ---- 价格 ----
    price = 0
    for span in li.find_all("span"):
        txt = span.get_text(strip=True)
        # 匹配数字（可能含逗号和円）
        if re.match(r"^\d[\d,]*円?$", txt):
            price = int(txt.replace(",", "").replace("円", ""))
            break

    # ---- 入札数 ----
    bid_elem = li.find("a", href=re.compile(r"bid_hist"))
    bid_count = 0
    if bid_elem:
        try:
            bid_count = int(bid_elem.get_text(strip=True))
        except ValueError:
            pass

    # ---- 结束时间 ----
    time_text = None
    for elem in li.find_all(["span", "p"]):
        txt = elem.get_text(strip=True)
        if re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", txt):
            time_text = txt
            break
    end_time = parse_end_time(time_text) if time_text else None

    # ---- 卖家 ----
    seller_link = li.find("a", href=re.compile(r"/seller/"))
    seller_id = None
    if seller_link:
        seller_id = seller_link["href"].split("/")[-1]

    # ---- 好评率 ----
    rating = None
    for elem in li.find_all(["span", "p"]):
        txt = elem.get_text(strip=True)
        if re.match(r"^\d{1,3}\.\d%$", txt):   # 匹配 99.4% 等
            rating = txt
            break

    # ---- 发货地 ----
    prefecture = None
    for p in li.find_all("p"):
        txt = p.get_text(strip=True)
        if "から発送" in txt:
            prefecture = txt.replace("から発送", "").strip()
            break

    if not auction_id:
        return None

    return {
        "auctionId": auction_id,
        "title": title,
        "price": price,
        "bidCount": bid_count,
        "endTime": end_time,
        "sellerId": seller_id,
        "sellerRating": rating,
        "prefecture": prefecture,
        "url": href,
        "scrapedAt": datetime.now(timezone.utc).isoformat()
    }


def parse_end_time(text):
    """从文本中提取结束时间（JST），转为 ISO 格式"""
    m = re.search(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        return None

    month, day, hour, minute = map(int, m.groups())
    year = datetime.now().year

    # 假设为 JST（UTC+9）
    dt = datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))
    return dt.isoformat()


def save_items(items):
    """批量写入 DynamoDB，设置 TTL 为 180 天后"""
    saved = 0
    with table.batch_writer() as batch:
        for item in items:
            try:
                batch.put_item(
                    Item={
                        "auctionId": item["auctionId"],
                        "title": item.get("title"),
                        "price": item.get("price", 0),
                        "bidCount": item.get("bidCount", 0),
                        "endTime": item.get("endTime"),
                        "sellerId": item.get("sellerId"),
                        "sellerRating": item.get("sellerRating"),
                        "prefecture": item.get("prefecture"),
                        "url": item.get("url"),
                        "scrapedAt": item.get("scrapedAt"),
                        "ttl": int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())
                    }
                )
                saved += 1
            except Exception as e:
                logger.error(f"Failed to save {item.get('auctionId')}: {e}")
    return saved
