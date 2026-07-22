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

# 环境变量
BASE_URL = os.getenv("BASE_URL", "https://auctions.yahoo.co.jp/closedsearch/closedsearch")
DEFAULT_PARAMS = os.getenv("DEFAULT_PARAMS", "n=50&select=6&mode=3&dest_pref_code=23")
MAX_PAGES = int(os.getenv("MAX_PAGES", "1"))
TABLE_NAME = os.getenv("TABLE_NAME", "YahooAuctionItems")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


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
    """抓取多页拍卖数据"""
    all_items = []
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
        # 如果本页数量少于每页数量（默认50），说明没有下一页
        if len(items) < 50:
            break
    return all_items


def build_url(keyword, page):
    """构建请求URL"""
    params = {}
    # 解析默认参数
    for p in DEFAULT_PARAMS.split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v
    params["p"] = keyword
    params["b"] = str(page)
    return f"{BASE_URL}?{urlencode(params, quote_via=quote)}"


def parse_html(html):
    """解析HTML，提取商品列表"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # 商品列表容器（根据实际页面结构）
    ul = soup.find("ul", class_=re.compile(r"sc-93f00b27-1"))
    if not ul:
        logger.warning("No item list found")
        return items

    for li in ul.find_all("li", class_=re.compile(r"sc-93f00b27-2")):
        try:
            item = parse_item(li)
            if item:
                items.append(item)
        except Exception as e:
            logger.warning(f"Failed to parse item: {e}")
            continue

    return items


def parse_item(li):
    """解析单个商品元素"""
    # 拍卖ID
    link = li.find("a", class_=re.compile(r"sc-c91b7830-5"))
    if not link:
        return None
    href = link.get("href")
    auction_id = None
    if href:
        match = re.search(r"(?:auction/)([a-z0-9]+)", href)
        if match:
            auction_id = match.group(1)

    # 标题
    title_elem = li.find("a", class_=re.compile(r"sc-c91b7830-12"))
    title = title_elem.get("title") or title_elem.get_text(strip=True) if title_elem else None

    # 价格
    price_elem = li.find("span", class_=re.compile(r"sc-c91b7830-17 fRZzUL"))
    price_str = price_elem.get_text(strip=True) if price_elem else "0"
    price = int(re.sub(r"[^\d]", "", price_str)) if price_str else 0

    # 入札数
    bid_elem = li.find("a", href=re.compile(r"bid_hist"))
    bid_count = int(bid_elem.get_text(strip=True)) if bid_elem else 0

    # 结束时间
    time_elem = li.find("span", class_=re.compile(r"gv-u-fontSize10--"))
    time_text = time_elem.get_text(strip=True) if time_elem else ""
    end_time = parse_end_time(time_text) if time_text else None

    # 卖家信息
    seller_link = li.find("a", class_=re.compile(r"sc-c91b7830-34"))
    seller_id = seller_link.get("href", "").split("/")[-1] if seller_link else None
    rating_elem = li.find("span", class_=re.compile(r"gv-u-fontSize12--"))
    rating = rating_elem.get_text(strip=True) if rating_elem else None

    # 发货地
    pref_elem = li.find("p", class_=re.compile(r"gv-u-fontSize12--"))
    prefecture = pref_elem.get_text(strip=True) if pref_elem else None
    # 去除“から発送”
    if prefecture and "から発送" in prefecture:
        prefecture = prefecture.replace("から発送", "").strip()

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
    """解析结束时间，格式如 '7/15 23:03'，假设年份为当前年份，若已过则减一年？我们只保存为ISO"""
    try:
        # 示例: "7/15 23:03"
        parts = text.split()
        if len(parts) != 2:
            return None
        date_part, time_part = parts
        month, day = date_part.split("/")
        hour, minute = time_part.split(":")
        now = datetime.now(timezone.utc)
        # 假设为当前年份，若月份小于当前月份则可能为去年，但页面显示的是结束时间，可能已过去，我们保留原样
        year = now.year
        # 构建本地时间（JST），然后转为UTC
        dt = datetime(year, int(month), int(day), int(hour), int(minute))
        # 雅虎拍卖时间是JST (UTC+9)
        dt = dt.replace(tzinfo=timezone(timedelta(hours=9)))
        return dt.isoformat()
    except Exception:
        return None


def save_items(items):
    """批量写入DynamoDB"""
    saved = 0
    with table.batch_writer() as batch:
        for item in items:
            try:
                # 使用 auctionId 作为分区键
                batch.put_item(
                    Item={
                        "auctionId": item["auctionId"],
                        "title": item.get("title"),
                        "price": item.get("price"),
                        "bidCount": item.get("bidCount"),
                        "endTime": item.get("endTime"),
                        "sellerId": item.get("sellerId"),
                        "sellerRating": item.get("sellerRating"),
                        "prefecture": item.get("prefecture"),
                        "url": item.get("url"),
                        "scrapedAt": item.get("scrapedAt"),
                        "ttl": int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())  # 180天后过期
                    }
                )
                saved += 1
            except Exception as e:
                logger.error(f"Failed to save item {item.get('auctionId')}: {e}")
    return saved
