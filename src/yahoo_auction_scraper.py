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
CLOSED_BASE_URL = os.getenv("CLOSED_BASE_URL", "https://auctions.yahoo.co.jp/closedsearch/closedsearch")
ACTIVE_BASE_URL = os.getenv("ACTIVE_BASE_URL", "https://auctions.yahoo.co.jp/search/search")
DEFAULT_PARAMS = os.getenv("DEFAULT_PARAMS", "n=50&select=6&mode=3&dest_pref_code=23")
MAX_PAGES = int(os.getenv("MAX_PAGES", "1"))
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DEBUG_LOG_HTML = os.getenv("DEBUG_LOG_HTML", "false").lower() == "true"
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "50"))

dynamodb = boto3.resource("dynamodb")


def get_target_table(search_type: str):
    """根据搜索类型返回对应的 DynamoDB 表"""
    if search_type == "active":
        return dynamodb.Table(TABLE_NAME_ACTIVE)
    return dynamodb.Table(TABLE_NAME_CLOSED)


def get_auction_params():
    """
    读取所有以 AUCTION_PARAM_ 开头的环境变量，返回参数字典。
    例如：AUCTION_PARAM_NEW=1 → {"new": "1"}
    注意：环境变量名中的下划线会被保留，但转为小写后作为参数名。
    若需要双下划线转点号等特殊处理，可在此扩展。
    """
    params = {}
    prefix = "AUCTION_PARAM_"
    for key, val in os.environ.items():
        if key.startswith(prefix):
            param_name = key[len(prefix):].lower()
            if val:  # 只添加非空值
                params[param_name] = val
    return params


def build_url(keyword, page, search_type):
    """
    构建请求 URL，合并：
    1. DEFAULT_PARAMS 中的基础参数
    2. AUCTION_PARAM_* 环境变量中的自定义参数（可覆盖基础参数）
    3. 关键词和分页参数
    """
    params = {}

    # 1. 解析 DEFAULT_PARAMS
    for p in DEFAULT_PARAMS.replace("&amp;", "&").split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v

    # 2. 合并自定义参数（优先级更高）
    params.update(get_auction_params())

    # 3. 设置关键词和分页
    params["p"] = keyword
    params["b"] = str((page - 1) * ITEMS_PER_PAGE + 1)

    # 4. 选择基础 URL
    base_url = ACTIVE_BASE_URL if search_type == "active" else CLOSED_BASE_URL

    return f"{base_url}?{urlencode(params, quote_via=quote)}"


def lambda_handler(event, context):
    keyword = event.get("keyword")
    if not keyword:
        logger.error("Missing 'keyword' in event")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing keyword"}, ensure_ascii=False)
        }

    search_type = event.get("search_type", "closed")  # "closed" 或 "active"
    logger.info(f"Scraping for keyword: '{keyword}', type: '{search_type}'")

    items = scrape_auctions(keyword, search_type)

    if not items:
        logger.info("No items found")
        return {
            "statusCode": 200,
            "body": json.dumps({"scraped": 0, "saved": 0, "type": search_type}, ensure_ascii=False)
        }

    table = get_target_table(search_type)
    saved = save_items(items, table)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "scraped": len(items),
            "saved": saved,
            "type": search_type
        }, ensure_ascii=False)
    }


def scrape_auctions(keyword, search_type):
    """抓取所有页面"""
    all_items = []

    for page in range(1, MAX_PAGES + 1):
        url = build_url(keyword, page, search_type)
        logger.info(f"Fetching page {page}: {url}")

        try:
            resp = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": USER_AGENT}
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            continue

        items = parse_html(resp.text, search_type)
        if not items:
            logger.info(f"No items on page {page}, stopping pagination")
            break

        all_items.extend(items)
        logger.info(f"Page {page}: found {len(items)} items (total: {len(all_items)})")

        if len(items) < ITEMS_PER_PAGE:
            logger.info(f"Last page reached (got {len(items)} < {ITEMS_PER_PAGE})")
            break

    return all_items


def parse_html(html, search_type):
    """解析 HTML，提取商品列表"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # 根据搜索类型选择合适的容器
    if search_type == "closed":
        container = soup.select_one("#closedSearchItems")
    else:
        # 活跃拍卖页面可能有不同的容器 ID
        container = soup.select_one("#auctionsItems") or soup.select_one(".Products__items")

    if not container:
        logger.warning(f"No container found for search_type={search_type}, trying body")
        container = soup.body

    if not container:
        logger.warning("No body found in HTML")
        return items

    # 查找商品列表的 ul 元素
    ul = container.find("ul")
    if not ul:
        logger.warning("No ul found in container")
        return items

    for li in ul.find_all("li", recursive=False):
        try:
            if DEBUG_LOG_HTML:
                logger.info(f"Parsing LI: {str(li)[:1000]}...")

            item = parse_item(li)
            if item:
                items.append(item)
            else:
                logger.warning("Failed to parse item, skipping")
        except Exception as e:
            logger.warning(f"Failed to parse item: {e}")
            continue

    return items


def parse_item(li):
    """解析单个商品列表项，提取所有信息"""
    # ---- 1. 商品链接 & 标题 & ID ----
    auction_link = None
    title = None
    auction_id = None

    # 优先选择 p 标签内的商品链接
    for p in li.find_all("p"):
        a = p.find("a", href=re.compile(r"/auction/"))
        if a:
            auction_link = a
            break

    # 回退：查找任何 a 标签
    if not auction_link:
        auction_link = li.find("a", href=re.compile(r"/auction/"))

    if not auction_link:
        logger.warning("No auction link found in li")
        return None

    href = auction_link.get("href", "")
    if href:
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            auction_id = m.group(1)

    if not auction_id:
        logger.warning("Could not extract auction ID")
        return None

    # 提取标题
    title_text = auction_link.get_text(strip=True)
    if title_text:
        title = title_text
    else:
        title = auction_link.get("title", "").strip()

    if not title:
        logger.warning(f"Title missing for auction {auction_id}")

    # ---- 2. 价格 ----
    price = 0
    # 尝试找"落札価格"或"現在価格"
    price_container = li.find(string=re.compile(r"落札価格|現在価格"))
    if price_container:
        parent = price_container.parent
        if parent:
            whole_text = parent.get_text(separator=" ", strip=True)
            nums = re.findall(r"[\d,]+", whole_text)
            if nums:
                try:
                    price = int(nums[-1].replace(",", ""))
                except ValueError:
                    pass

    # 兜底：查找所有 span 中的价格
    if price == 0:
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            m = re.match(r"^([\d,]+)円?$", txt)
            if m:
                try:
                    price = int(m.group(1).replace(",", ""))
                    break
                except ValueError:
                    pass

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

    # 策略1：查找包含"終了"的元素
    ended_elem = li.find(lambda tag: tag.name in ["span", "p"] and "終了" in tag.get_text())
    if ended_elem:
        time_text = ended_elem.get_text(strip=True)
        logger.info(f"Found end time element: {time_text}")
    else:
        # 策略2：全局正则搜索时间格式
        all_text = li.get_text(separator=" ", strip=True)
        m = re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", all_text)
        if m:
            time_text = m.group()
            logger.info(f"Extracted time by regex: {time_text}")

    if time_text:
        end_time = parse_end_time(time_text)
    else:
        logger.warning(f"Could not extract end time for auction {auction_id}")

    # ---- 5. 卖家 ID ----
    seller_id = None
    seller_link = li.find("a", href=re.compile(r"/seller/"))
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

    # 全局兜底查找
    if not rating:
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

    # ---- 8. 缩略图 URL（可选）----
    thumbnail_url = None
    img = li.find("img")
    if img:
        thumbnail_url = img.get("src") or img.get("data-src")

    # ---- 9. 构建返回对象 ----
    item = {
        "auctionId": auction_id,
        "title": title,
        "price": price,
        "bidCount": bid_count,
        "endTime": end_time,
        "sellerId": seller_id,
        "sellerRating": rating,
        "prefecture": prefecture,
        "url": href,
        "thumbnailUrl": thumbnail_url,
        "scrapedAt": datetime.now(timezone.utc).isoformat()
    }

    logger.info(f"Parsed item: {auction_id} - {title[:50]}...")
    return item


def parse_end_time(text):
    """
    从时间文本中提取日期时间，返回 ISO 格式字符串（JST, UTC+9）
    支持格式：
    - "2026/7/15 23:03"
    - "7/15 23:03"
    - "7/15 23時03分"
    """
    if not text:
        return None

    # 清理文本
    text = text.replace("時", ":").replace("分", "")

    # 匹配日期时间
    m = re.search(r"(\d{1,4})?[\/-]?(\d{1,2})[\/-](\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        logger.warning(f"parse_end_time: could not parse '{text}'")
        return None

    # 确定年份
    if m.group(1) and len(m.group(1)) == 4:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
    else:
        year = datetime.now().year
        month = int(m.group(2))
        day = int(m.group(3))

    hour = int(m.group(4))
    minute = int(m.group(5))

    try:
        dt = datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))
        return dt.isoformat()
    except ValueError as e:
        logger.warning(f"Invalid date/time: {text} - {e}")
        return None


def save_items(items, table):
    """
    保存商品到 DynamoDB，使用 ConditionExpression 防止重复插入
    返回成功保存的数量
    """
    saved = 0
    for item in items:
        try:
            table.put_item(
                Item={
                    "auctionId": item["auctionId"],
                    "title": item.get("title", ""),
                    "price": item.get("price", 0),
                    "bidCount": item.get("bidCount", 0),
                    "endTime": item.get("endTime"),
                    "sellerId": item.get("sellerId"),
                    "sellerRating": item.get("sellerRating"),
                    "prefecture": item.get("prefecture"),
                    "url": item.get("url"),
                    "thumbnailUrl": item.get("thumbnailUrl"),
                    "scrapedAt": item.get("scrapedAt"),
                    "ttl": int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())
                },
                ConditionExpression="attribute_not_exists(auctionId)"
            )
            saved += 1
            logger.info(f"Saved: {item['auctionId']}")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            logger.info(f"Skipped duplicate: {item['auctionId']}")
        except Exception as e:
            logger.error(f"Failed to save {item.get('auctionId')}: {e}")

    return saved
