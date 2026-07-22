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
    for p in DEFAULT_PARAMS.replace("&amp;", "&").split("&"):
        if p.startswith("n="):
            try:
                return int(p.split("=")[1])
            except ValueError:
                pass
    return 50


def build_url(keyword, page):
    params = {}
    for p in DEFAULT_PARAMS.replace("&amp;", "&").split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v
    n = int(params.get("n", "50"))
    params["p"] = keyword
    params["b"] = str((page - 1) * n + 1)
    return f"{BASE_URL}?{urlencode(params, quote_via=quote)}"


def lambda_handler(event, context):
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
        "body": json.dumps({"scraped": len(items), "saved": saved}, ensure_ascii=False)
    }


def scrape_auctions(keyword):
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

        if len(items) < per_page:
            break

    return all_items


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    container = soup.select_one("#closedSearchItems")
    if not container:
        logger.warning("No #closedSearchItems found")
        return items

    ul = container.find("ul")
    if not ul:
        logger.warning("No ul inside #closedSearchItems")
        return items

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
    """
    基于 HTML 结构树的稳定解析逻辑：
    - 标题：取 p > a[href*="/auction/"] 的文本，fallback 到任意 a 的 title
    - 价格：查找“落札価格”文本区域，提取整数
    - 入札数：a[href*="bid_hist"] 的文本数字
    - 结束时间：包含“終了”的 span 中的日期时间
    - 卖家ID：a[href*="/seller/"] 最后一段
    - 好评率：卖家链接后紧跟的百分数 span
    - 发货地：包含“から発送”的 p 的文本
    """

    # ---- 1. 商品链接 & 标题 ----
    auction_link = None
    title = None

    # 优先选择 p 标签内的商品链接（标题链接）
    for p in li.find_all("p"):
        a = p.find("a", href=re.compile(r"/auction/"))
        if a:
            auction_link = a
            break
    # 如果没找到，取第一个匹配的 a
    if not auction_link:
        auction_link = li.find("a", href=re.compile(r"/auction/"))
    if not auction_link:
        return None

    href = auction_link.get("href")
    auction_id = None
    if href:
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            auction_id = m.group(1)

    # 标题优先取链接的完整文本，其次取 title 属性
    title_text = auction_link.get_text(strip=True)
    if title_text:
        title = title_text
    else:
        title = auction_link.get("title", "").strip()

    # ---- 2. 价格 ----
    price = 0
    # 找包含“落札価格”的文本节点
    price_container = li.find(string=re.compile("落札価格"))
    if price_container:
        # 向上追溯到可能包含数字的父级
        parent = price_container.parent
        # 在父级内寻找数字（円）
        whole_text = parent.get_text(separator=" ", strip=True)
        # 提取数字
        nums = re.findall(r"[\d,]+", whole_text)
        if nums:
            # 通常最后一个数字是落札価格（紧接着的）
            price_str = nums[-1]
            price = int(price_str.replace(",", ""))
    else:
        # 兜底：遍历所有 span 匹配数字（旧逻辑，但限定在价格区域更安全）
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            if re.match(r"^\d[\d,]*円?$", txt):
                price = int(txt.replace(",", "").replace("円", ""))
                break

    # ---- 3. 入札数 ----
    bid_count = 0
    bid_link = li.find("a", href=re.compile(r"bid_hist"))
    if bid_link:
        bid_text = bid_link.get_text(strip=True)
        try:
            bid_count = int(re.sub(r"\D", "", bid_text))
        except ValueError:
            pass

    # ---- 4. 结束时间 ----
    time_text = None
    # 寻找包含“終了”的元素
    ended_elem = li.find(string=re.compile("終了"))
    if ended_elem:
        # 该元素可能是 span，直接取其文本
        time_text = ended_elem.strip()
    else:
        # 尝试在 span 中匹配时间格式
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            if re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", txt):
                time_text = txt
                break
    end_time = parse_end_time(time_text) if time_text else None

    # ---- 5. 卖家 ----
    seller_link = li.find("a", href=re.compile(r"/seller/"))
    seller_id = None
    if seller_link:
        seller_id = seller_link["href"].split("/")[-1]

    # ---- 6. 好评率 ----
    rating = None
    if seller_link:
        # 在卖家链接的同一容器内找后续的 span 包含 %
        parent = seller_link.parent
        if parent:
            spans = parent.find_all("span")
            for sp in spans:
                txt = sp.get_text(strip=True)
                if re.match(r"^\d{1,3}\.\d%$", txt):
                    rating = txt
                    break
    if not rating:
        # 兜底：在整个 li 中找百分数（但要排除其他可能）
        for txt_elem in li.find_all(string=re.compile(r"^\d{1,3}\.\d%$")):
            rating = txt_elem.strip()
            break

    # ---- 7. 发货地 ----
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
    """
    提取结束时间文本中的日期和时间，格式如：
    "7/15 23:03終了" 或 "7/15 23:03"
    返回 ISO 8601 字符串（JST 时区）
    """
    if not text:
        return None
    m = re.search(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        return None
    month, day, hour, minute = map(int, m.groups())
    year = datetime.now().year
    dt = datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))
    return dt.isoformat()


def save_items(items):
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
