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


# ==================== 环境变量辅助函数 ====================

def _env_int(key: str, default: int) -> int:
    value = os.getenv(key, "")
    if not value:
        return default
    return int(value)


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key, "")
    if not value:
        return default
    return value.lower() == "true"


# ============ 环境变量 ============
CLOSED_BASE_URL = os.getenv("CLOSED_BASE_URL", "https://auctions.yahoo.co.jp/closedsearch/closedsearch")
ACTIVE_BASE_URL = os.getenv("ACTIVE_BASE_URL", "https://auctions.yahoo.co.jp/search/search")
DEFAULT_PARAMS_CLOSED = os.getenv("DEFAULT_PARAMS_CLOSED", "is_postage_mode=1&dest_pref_code=23&n=60&s1=end&o1=d&mode=3&isdr=0")
DEFAULT_PARAMS_ACTIVE = os.getenv("DEFAULT_PARAMS_ACTIVE", "is_postage_mode=1&dest_pref_code=23&n=60&s1=end&o1=a&mode=3&isdr=0")
MAX_PAGES = _env_int("MAX_PAGES", 2)
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
REQUEST_TIMEOUT = _env_int("REQUEST_TIMEOUT", 30)
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DEBUG_LOG_HTML = _env_bool("DEBUG_LOG_HTML", False)
ITEMS_PER_PAGE = _env_int("ITEMS_PER_PAGE", 50)
INCLUDE_PAYPAY = _env_bool("INCLUDE_PAYPAY", True)

dynamodb = boto3.resource("dynamodb")

PREFECTURES_LIST = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]


def get_target_table(search_type: str):
    if search_type == "active":
        return dynamodb.Table(TABLE_NAME_ACTIVE)
    return dynamodb.Table(TABLE_NAME_CLOSED)


def get_auction_params():
    params = {}
    prefix = "AUCTION_PARAM_"
    for key, val in os.environ.items():
        if key.startswith(prefix):
            param_name = key[len(prefix):].lower()
            if val:
                params[param_name] = val
    return params


def build_url(keyword, page, search_type):
    params = {}

    if search_type == "active":
        default_params_str = DEFAULT_PARAMS_ACTIVE
    else:
        default_params_str = DEFAULT_PARAMS_CLOSED
    
    for p in default_params_str.replace("&amp;", "&").split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v

    params.update(get_auction_params())
    params["p"] = keyword
    params["b"] = str((page - 1) * ITEMS_PER_PAGE + 1)

    base_url = ACTIVE_BASE_URL if search_type == "active" else CLOSED_BASE_URL
    return f"{base_url}?{urlencode(params, quote_via=quote)}"


def lambda_handler(event, context):
    keyword = event.get("keyword")
    if not keyword:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing keyword"}, ensure_ascii=False)
        }

    search_type = event.get("search_type", "closed")
    include_paypay = event.get("include_paypay", INCLUDE_PAYPAY)
    
    logger.info(f"Scraping for keyword: '{keyword}', type: '{search_type}'")

    items = scrape_auctions(keyword, search_type, include_paypay)

    if not items:
        return {
            "statusCode": 200,
            "body": json.dumps({"scraped": 0, "saved": 0, "type": search_type}, ensure_ascii=False)
        }

    table = get_target_table(search_type)
    saved = save_items(items, table)

    logger.info(f"Scraping completed: {len(items)} items scraped, {saved} saved")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "scraped": len(items),
            "saved": saved,
            "type": search_type
        }, ensure_ascii=False)
    }


def scrape_auctions(keyword, search_type, include_paypay=True):
    all_items = []

    for page in range(1, MAX_PAGES + 1):
        url = build_url(keyword, page, search_type)
        logger.info(f"Fetching page {page}: {url}")

        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            continue

        items = parse_html(resp.text, search_type, include_paypay)
        if not items:
            break

        all_items.extend(items)
        logger.info(f"Page {page}: found {len(items)} items (total: {len(all_items)})")

        if len(items) < ITEMS_PER_PAGE:
            break

    logger.info(f"Total items scraped: {len(all_items)}")
    return all_items


def parse_html(html, search_type, include_paypay=True):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    if search_type == "closed":
        container = soup.select_one("#closedSearchItems")
    else:
        selectors = [".Products__list", ".ProductList", "[data-auction-list]", ".SearchResults__list", "#auctionsItems", ".Products__items"]
        container = None
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                break

    product_items = []
    if container:
        product_items = find_product_items_in_container(container, search_type, include_paypay)
    else:
        product_items = find_product_items_in_container(soup.body, search_type, include_paypay)
    
    for li in product_items:
        try:
            item = parse_item(li, include_paypay)
            if item:
                items.append(item)
        except Exception as e:
            logger.warning(f"Failed to parse product item: {e}")
            continue

    return items


def find_product_items_in_container(container, search_type, include_paypay):
    product_items = []
    
    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")
    
    uls = container.find_all("ul")
    
    for ul in uls:
        ul_class = " ".join(ul.get("class", [])).lower()
        
        if any(skip_word in ul_class for skip_word in ["category", "nav", "menu", "footer", "header", "breadcrumb"]):
            continue
        
        has_product_links = False
        for li in ul.find_all("li", recursive=False):
            if li.find("a", href=link_pattern) or li.get("data-auction-id"):
                has_product_links = True
                break
        
        if has_product_links:
            for li in ul.find_all("li", recursive=False):
                li_class = " ".join(li.get("class", [])).lower()
                if "category" in li_class:
                    continue
                if li.find("a", href=link_pattern) or li.get("data-auction-id"):
                    product_items.append(li)
    
    return product_items


def parse_shipping_info(li):
    shipping = {"shippingFee": None, "shippingText": None, "isFreeShipping": False}
    
    postage_elem = li.select_one('.Product__postage')
    if postage_elem:
        shipping_text = postage_elem.get_text(strip=True)
        shipping["shippingText"] = shipping_text
        
        if not shipping_text:
            shipping["shippingFee"] = 0
            shipping["isFreeShipping"] = True
            shipping["shippingText"] = "送料込み"
            return shipping
        
        match = re.search(r'送料(\d[\d,]*)円', shipping_text)
        if match:
            shipping["shippingFee"] = int(match.group(1).replace(',', ''))
            shipping["isFreeShipping"] = False
        elif '無料' in shipping_text:
            shipping["shippingFee"] = 0
            shipping["isFreeShipping"] = True
        elif '未定' in shipping_text:
            shipping["shippingFee"] = None
        elif '着払' in shipping_text:
            shipping["shippingFee"] = None
            shipping["shippingText"] = "着払い"
        else:
            match = re.search(r'(\d[\d,]*)円', shipping_text)
            if match:
                shipping["shippingFee"] = int(match.group(1).replace(',', ''))
    else:
        price_info = li.select_one('.Product__priceInfo')
        if price_info:
            price_info_text = price_info.get_text(strip=True)
            if '送料無料' in price_info_text or '送料込み' in price_info_text:
                shipping["shippingFee"] = 0
                shipping["isFreeShipping"] = True
                shipping["shippingText"] = "送料込み"
            else:
                shipping["shippingFee"] = 0
                shipping["isFreeShipping"] = True
                shipping["shippingText"] = "送料込み(推定)"
    
    return shipping


def parse_seller_location(li):
    prefecture = None
    
    sell_from = li.select_one('.Product__sellFrom')
    if sell_from:
        sell_from_span = sell_from.find('span', class_='u-textGray')
        if sell_from_span:
            sell_from_text = sell_from_span.get_text(strip=True)
            match = re.search(r'(.+?)から発送', sell_from_text)
            if match:
                prefecture = match.group(1).strip()
            else:
                prefecture = sell_from_text.strip()
    
    if not prefecture:
        for p in li.find_all("p"):
            txt = p.get_text(strip=True)
            if "から発送" in txt:
                prefecture = txt.replace("から発送", "").strip()
                break
    
    if not prefecture:
        for elem in li.find_all(['span', 'div', 'p']):
            txt = elem.get_text(strip=True)
            if "から発送" in txt:
                match = re.search(r'(.+?)から発送', txt)
                if match:
                    prefecture = match.group(1).strip()
                    break
    
    if not prefecture:
        li_text = li.get_text()
        for pref in PREFECTURES_LIST:
            if pref in li_text:
                prefecture = pref
                break
    
    return prefecture


def parse_item(li, include_paypay=True):
    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")

    auction_link = li.select_one('.Product__titleLink')
    if not auction_link:
        h3 = li.find('h3', class_='Product__title')
        if h3:
            auction_link = h3.find('a', href=link_pattern)
    if not auction_link:
        for p in li.find_all("p"):
            a = p.find("a", href=link_pattern)
            if a:
                auction_link = a
                break
    if not auction_link:
        auction_link = li.find("a", href=link_pattern)

    if not auction_link:
        return None

    href = auction_link.get("href", "")
    if not href:
        return None
    
    data_id = auction_link.get('data-auction-id', '')
    if data_id:
        item_id = data_id
        item_type = "paypay" if item_id.startswith('z') else "auction"
    else:
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            item_id = m.group(1)
            item_type = "auction"
        else:
            m = re.search(r"/item/([a-z0-9]+)", href)
            if m:
                item_id = m.group(1)
                item_type = "paypay"
            else:
                return None

    title = auction_link.get('data-auction-title', '').strip()
    if not title:
        title = auction_link.get_text(strip=True)
    if not title:
        title = auction_link.get("title", "").strip()

    price = 0
    data_price = auction_link.get('data-auction-price', '')
    if data_price:
        try:
            price = int(data_price)
        except ValueError:
            pass
    else:
        price_value = li.select_one('.Product__priceValue')
        if price_value:
            price_text = price_value.get_text(strip=True)
            match = re.search(r'([\d,]+)円', price_text)
            if match:
                price = int(match.group(1).replace(",", ""))
        else:
            for span in li.find_all("span"):
                txt = span.get_text(strip=True)
                m = re.match(r"^([\d,]+)円$", txt)
                if m:
                    price = int(m.group(1).replace(",", ""))
                    break

    shipping = parse_shipping_info(li)

    buynow_price = None
    price_info_spans = li.select('.Product__price')
    for price_span in price_info_spans:
        label = price_span.select_one('.Product__label')
        if label and '即決' in label.get_text():
            value = price_span.select_one('.Product__priceValue')
            if value:
                value_text = value.get_text(strip=True)
                if value_text != '-':
                    match = re.search(r'([\d,]+)円', value_text)
                    if match:
                        buynow_price = int(match.group(1).replace(',', ''))
            break

    bid_count = 0
    if item_type == "auction":
        bid_link = li.find("a", href=re.compile(r"bid_hist"))
        if bid_link:
            try:
                bid_count = int(re.sub(r"\D", "", bid_link.get_text(strip=True)))
            except ValueError:
                pass

    end_time = None
    product_div = li.find_parent('div', class_='Product') or li
    
    endtime_elem = product_div.select_one('[data-auction-endtime]')
    if endtime_elem:
        endtime_value = endtime_elem.get('data-auction-endtime', '')
        if endtime_value:
            try:
                timestamp = int(endtime_value)
                dt = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=9)))
                end_time = dt.isoformat()
            except (ValueError, OSError):
                pass
    
    if not end_time:
        ended_elem = li.find(lambda tag: tag.name in ["span", "p"] and "終了" in tag.get_text())
        if ended_elem:
            end_time = parse_end_time(ended_elem.get_text(strip=True))
    
    if not end_time:
        all_text = li.get_text(separator=" ", strip=True)
        m = re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", all_text)
        if m:
            end_time = parse_end_time(m.group())
    
    if not end_time:
        timeleft_elem = li.select_one('[data-timeleft]')
        if timeleft_elem:
            timeleft = timeleft_elem.get('data-timeleft', '')
            if timeleft:
                try:
                    seconds_left = int(timeleft)
                    now = datetime.now(timezone(timedelta(hours=9)))
                    end_time = (now + timedelta(seconds=seconds_left)).isoformat()
                except ValueError:
                    pass

    seller_id = None
    seller_id_elem = product_div.select_one('[data-auction-auc-seller-id]')
    if seller_id_elem:
        seller_id = seller_id_elem.get('data-auction-auc-seller-id', '')
    
    if not seller_id:
        for pattern in [re.compile(r"/user/"), re.compile(r"/seller/"), re.compile(r"userID=", re.IGNORECASE)]:
            seller_link = li.find("a", href=pattern)
            if seller_link:
                seller_href = seller_link.get("href", "")
                for p in [r"/user/([^/?#]+)", r"/seller/([^/?#]+)", r"[?&]userID=([^&#]+)"]:
                    match = re.search(p, seller_href, re.IGNORECASE)
                    if match:
                        seller_id = match.group(1)
                        break
                if seller_id:
                    break

    rating = None
    rating_elem = li.select_one('.Product__ratingValue')
    if rating_elem:
        rating_text = rating_elem.get_text(strip=True)
        if rating_text and rating_text != "新規":
            rating = rating_text
    
    if not rating:
        for sp in li.find_all("span"):
            txt = sp.get_text(strip=True)
            if re.match(r"^\d{1,3}\.\d%$", txt):
                rating = txt
                break

    prefecture = parse_seller_location(li)

    seller_type = "store" if li.select_one('.Product__icon--store') else "personal"

    item_condition = None
    for icon in li.select('.Product__icon'):
        icon_text = icon.get_text(strip=True)
        if icon_text in ['未使用', '新品', '中古', '新規']:
            item_condition = icon_text
            break

    thumbnail_url = auction_link.get('data-auction-img', '')
    if not thumbnail_url:
        img = li.find("img")
        if img:
            thumbnail_url = img.get("src") or img.get("data-src")

    return {
        "itemId": item_id,
        "itemType": item_type,
        "title": title,
        "price": price,
        "buynowPrice": buynow_price,
        "shippingFee": shipping["shippingFee"],
        "shippingText": shipping["shippingText"],
        "isFreeShipping": shipping["isFreeShipping"],
        "bidCount": bid_count,
        "endTime": end_time,
        "sellerId": seller_id,
        "sellerRating": rating,
        "sellerType": seller_type,
        "prefecture": prefecture,
        "itemCondition": item_condition,
        "url": href,
        "thumbnailUrl": thumbnail_url,
        "scrapedAt": datetime.now(timezone.utc).isoformat()
    }


def parse_end_time(text):
    if not text:
        return None
    text = text.replace("時", ":").replace("分", "")
    m = re.search(r"(\d{1,4})?[\/-]?(\d{1,2})[\/-](\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        return None
    if m.group(1) and len(m.group(1)) == 4:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        year, month, day = datetime.now().year, int(m.group(2)), int(m.group(3))
    hour, minute = int(m.group(4)), int(m.group(5))
    try:
        dt = datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))
        return dt.isoformat()
    except ValueError:
        return None


def save_items(items, table):
    saved = 0
    for item in items:
        try:
            table.put_item(
                Item={
                    "itemID": item["itemId"],
                    "itemType": item.get("itemType", "unknown"),
                    "title": item.get("title", ""),
                    "price": item.get("price", 0),
                    "buynowPrice": item.get("buynowPrice"),
                    "shippingFee": item.get("shippingFee"),
                    "shippingText": item.get("shippingText", ""),
                    "isFreeShipping": item.get("isFreeShipping", False),
                    "bidCount": item.get("bidCount", 0),
                    "endTime": item.get("endTime") or "unknown",
                    "sellerId": item.get("sellerId") or "unknown",
                    "sellerRating": item.get("sellerRating") or "unknown",
                    "sellerType": item.get("sellerType", "personal"),
                    "prefecture": item.get("prefecture") or "unknown",
                    "itemCondition": item.get("itemCondition"),
                    "url": item.get("url") or "",
                    "thumbnailUrl": item.get("thumbnailUrl") or "",
                    "scrapedAt": item.get("scrapedAt") or datetime.now(timezone.utc).isoformat(),
                    "ttl": int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())
                },
                ConditionExpression="attribute_not_exists(itemID)"
            )
            saved += 1
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            logger.info(f"Skipped duplicate: {item.get('itemId')}")
        except Exception as e:
            logger.error(f"Failed to save {item.get('itemId')}: {e}")
    return saved
