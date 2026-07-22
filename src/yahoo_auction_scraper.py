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
DEBUG_LOG_HTML = os.getenv("DEBUG_LOG_HTML", "true").lower() == "true"  # 是否打印 li 的 HTML

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
            # 调试输出：打印整个 <li> 的 HTML 结构（前 1000 字符）
            if DEBUG_LOG_HTML:
                logger.info(f"Parsing LI: {str(li)[:1000]}...")
            item = parse_item(li)
            if item:
                items.append(item)
            else:
                logger.warning("Failed to parse item, skipping.")
        except Exception as e:
            logger.warning(f"Failed to parse item: {e}")
            continue

    return items


def parse_item(li):
    """
    稳定解析单个商品，失败时打印详细日志
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
    if not auction_link:
        auction_link = li.find("a", href=re.compile(r"/auction/"))
    if not auction_link:
        logger.warning("No auction link found in li")
        return None

    href = auction_link.get("href")
    auction_id = None
    if href:
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            auction_id = m.group(1)

    title_text = auction_link.get_text(strip=True)
    if title_text:
        title = title_text
    else:
        title = auction_link.get("title", "").strip()

    if not title:
        logger.warning(f"Title missing for auction {auction_id}")

    # ---- 2. 价格 ----
    price = 0
    price_container = li.find(string=re.compile("落札価格"))
    if price_container:
        parent = price_container.parent
        whole_text = parent.get_text(separator=" ", strip=True)
        nums = re.findall(r"[\d,]+", whole_text)
        if nums:
            price = int(nums[-1].replace(",", ""))
    else:
        # 兜底：找所有 span 里的数字
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            if re.match(r"^\d[\d,]*円?$", txt):
                price = int(txt.replace(",", "").replace("円", ""))
                break
    if price == 0:
        logger.warning(f"Price not found for auction {auction_id}")

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
    end_time = None
    time_text = None

    # 策略1：找文本中包含「終了」的元素
    ended_elem = li.find(lambda tag: tag.name in ["span", "p"] and "終了" in tag.get_text())
    if ended_elem:
        time_text = ended_elem.get_text(strip=True)
        logger.info(f"Found end time element text: {time_text}")
    else:
        # 策略2：用正则全局搜索时间格式
        all_text = li.get_text(separator=" ", strip=True)
        m = re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", all_text)
        if m:
            time_text = m.group()
            logger.info(f"Extracted time by regex: {time_text}")

    if time_text:
        end_time = parse_end_time(time_text)
    else:
        logger.warning(f"Could not extract end time for auction {auction_id}. Full li text: {li.get_text(separator=' ', strip=True)[:300]}")

    # ---- 5. 卖家 ----
    seller_link = li.find("a", href=re.compile(r"/seller/"))
    seller_id = None
    if seller_link:
        seller_id = seller_link["href"].split("/")[-1]
    else:
        logger.warning(f"Seller not found for auction {auction_id}")

    # ---- 6. 好评率 ----
    rating = None
    if seller_link:
        parent = seller_link.parent
        if parent:
            spans = parent.find_all("span")
            for sp in spans:
                txt = sp.get_text(strip=True)
                if re.match(r"^\d{1,3}\.\d%$", txt):
                    rating = txt
                    break
    if not rating:
        # 全局兜底
        for sp in li.find_all("span"):
            txt = sp.get_text(strip=True)
            if re.match(r"^\d{1,3}\.\d%$", txt):
                rating = txt
                break
    if not rating:
        logger.warning(f"Rating not found for auction {auction_id}")

    # ---- 7. 发货地 ----
    prefecture = None
    for p in li.find_all("p"):
        txt = p.get_text(strip=True)
        if "から発送" in txt:
            prefecture = txt.replace("から発送", "").strip()
            break
    if not prefecture:
        logger.warning(f"Prefecture not found for auction {auction_id}")

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
    从结束时间文本中提取日期时间，支持多种格式，返回 ISO 字符串（JST）
    """
    if not text:
        return None
    # 匹配 2026/7/15 23:03 或 7/15 23:03
    m = re.search(r"(\d{1,4})?[\/-]?(\d{1,2})[\/-](\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        logger.warning(f"parse_end_time: could not parse '{text}'")
        return None
    # 如果有年份则用，否则用当前年份
    if m.group(1) and len(m.group(1)) == 4:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
    else:
        month = int(m.group(2))
        day = int(m.group(3))
        year = datetime.now().year

    hour = int(m.group(4))
    minute = int(m.group(5))
    try:
        dt = datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"Invalid date/time: {text} - {e}")
        return None


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
