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
DEFAULT_PARAMS_CLOSED = os.getenv("DEFAULT_PARAMS_CLOSED", "is_postage_mode=1&dest_pref_code=23&n=60&s1=end&o1=d&mode=3&isdr=0")
DEFAULT_PARAMS_ACTIVE = os.getenv("DEFAULT_PARAMS_ACTIVE", "is_postage_mode=1&dest_pref_code=23&n=60&s1=end&o1=a&mode=3&isdr=0")
MAX_PAGES = int(os.getenv("MAX_PAGES", "1"))
TABLE_NAME_CLOSED = os.getenv("TABLE_NAME_CLOSED", "YahooAuctionItems")
TABLE_NAME_ACTIVE = os.getenv("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DEBUG_LOG_HTML = os.getenv("DEBUG_LOG_HTML", "false").lower() == "true"
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "50"))
INCLUDE_PAYPAY = os.getenv("INCLUDE_PAYPAY", "true").lower() == "true"

dynamodb = boto3.resource("dynamodb")

# 日本47都道府県列表
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
    """根据搜索类型返回对应的 DynamoDB 表"""
    if search_type == "active":
        return dynamodb.Table(TABLE_NAME_ACTIVE)
    return dynamodb.Table(TABLE_NAME_CLOSED)


def get_auction_params():
    """
    读取所有以 AUCTION_PARAM_ 开头的环境变量，返回参数字典。
    例如：AUCTION_PARAM_NEW=1 → {"new": "1"}
    """
    params = {}
    prefix = "AUCTION_PARAM_"
    for key, val in os.environ.items():
        if key.startswith(prefix):
            param_name = key[len(prefix):].lower()
            if val:
                params[param_name] = val
    return params


def build_url(keyword, page, search_type):
    """
    构建请求 URL，合并：
    1. 根据搜索类型选择对应的默认参数
    2. AUCTION_PARAM_* 环境变量中的自定义参数（可覆盖基础参数）
    3. 关键词和分页参数
    """
    params = {}

    # 1. 根据搜索类型解析不同的默认参数
    if search_type == "active":
        default_params_str = DEFAULT_PARAMS_ACTIVE
    else:
        default_params_str = DEFAULT_PARAMS_CLOSED
    
    for p in default_params_str.replace("&amp;", "&").split("&"):
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
    include_paypay = event.get("include_paypay", INCLUDE_PAYPAY)
    
    logger.info(f"Scraping for keyword: '{keyword}', type: '{search_type}', include_paypay: {include_paypay}")

    items = scrape_auctions(keyword, search_type, include_paypay)

    if not items:
        logger.info("No items found")
        return {
            "statusCode": 200,
            "body": json.dumps({"scraped": 0, "saved": 0, "type": search_type}, ensure_ascii=False)
        }

    table = get_target_table(search_type)
    saved = save_items(items, table)

    logger.info(f"Scraping completed: {len(items)} items scraped, {saved} saved to DynamoDB")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "scraped": len(items),
            "saved": saved,
            "type": search_type
        }, ensure_ascii=False)
    }


def scrape_auctions(keyword, search_type, include_paypay=True):
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
            logger.info(f"Page {page} response status: {resp.status_code}, content length: {len(resp.text)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            continue

        items = parse_html(resp.text, search_type, include_paypay)
        if not items:
            logger.info(f"No items found on page {page}, stopping pagination")
            break

        all_items.extend(items)
        logger.info(f"Page {page}: found {len(items)} items (total accumulated: {len(all_items)})")

        if len(items) < ITEMS_PER_PAGE:
            logger.info(f"Last page reached (got {len(items)} items < {ITEMS_PER_PAGE} per page)")
            break

    logger.info(f"Total items scraped across all pages: {len(all_items)}")
    return all_items


def parse_html(html, search_type, include_paypay=True):
    """解析 HTML，提取商品列表"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # 调试：打印页面结构
    if DEBUG_LOG_HTML:
        logger.info("=== DEBUG: Page structure ===")
        for i, ul in enumerate(soup.find_all("ul")):
            classes = " ".join(ul.get("class", []))
            li_count = len(ul.find_all("li", recursive=False))
            logger.info(f"UL #{i}: class='{classes}', li_count={li_count}")
            
            if li_count > 0:
                first_li = ul.find("li", recursive=False)
                li_class = " ".join(first_li.get("class", []))
                logger.info(f"  First LI class: '{li_class}'")
                logger.info(f"  First LI HTML: {str(first_li)[:300]}")
        logger.info("=== END DEBUG ===")

    # 根据搜索类型选择合适的容器
    if search_type == "closed":
        container = soup.select_one("#closedSearchItems")
        logger.info(f"Looking for closed search container: #closedSearchItems - {'Found' if container else 'Not found'}")
    else:
        # 活跃拍卖页面尝试多个可能的选择器
        selectors = [
            ".Products__list",
            ".ProductList",
            "[data-auction-list]",
            ".SearchResults__list",
            "#auctionsItems",
            ".Products__items"
        ]
        container = None
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                logger.info(f"Found active search container using selector: {selector}")
                break
        
        if not container:
            logger.warning("No specific container found for active search, will scan all UL elements")

    # 如果没找到特定容器，扫描所有 ul
    product_items = []
    
    if container:
        logger.info(f"Scanning container for product items")
        product_items = find_product_items_in_container(container, search_type, include_paypay)
    else:
        logger.info("Scanning entire body for product items")
        product_items = find_product_items_in_container(soup.body, search_type, include_paypay)
    
    logger.info(f"Found {len(product_items)} potential product items")
    
    # 解析每个商品
    skipped_count = 0
    for li in product_items:
        try:
            if DEBUG_LOG_HTML:
                logger.info(f"Parsing product LI: {str(li)[:500]}...")

            item = parse_item(li, include_paypay)
            if item:
                items.append(item)
            else:
                skipped_count += 1
        except Exception as e:
            logger.warning(f"Failed to parse product item: {e}")
            skipped_count += 1
            continue

    logger.info(f"Successfully parsed {len(items)} items, skipped {skipped_count} items")
    return items


def find_product_items_in_container(container, search_type, include_paypay):
    """在容器中查找商品列表项"""
    product_items = []
    
    # 构建链接匹配模式
    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")
    
    # 查找所有 ul 元素
    uls = container.find_all("ul")
    logger.info(f"Found {len(uls)} UL elements in container")
    
    for ul_idx, ul in enumerate(uls):
        ul_class = " ".join(ul.get("class", [])).lower()
        
        # 跳过明显的非商品列表
        if any(skip_word in ul_class for skip_word in ["category", "nav", "menu", "footer", "header", "breadcrumb"]):
            logger.info(f"Skipping UL #{ul_idx}: class='{ul_class}' (non-product container)")
            continue
        
        # 检查这个 ul 中是否有商品链接
        has_product_links = False
        for li in ul.find_all("li", recursive=False):
            if li.find("a", href=link_pattern) or li.get("data-auction-id"):
                has_product_links = True
                break
        
        if has_product_links:
            logger.info(f"UL #{ul_idx}: class='{ul_class}' - Found product links")
            for li in ul.find_all("li", recursive=False):
                li_class = " ".join(li.get("class", [])).lower()
                
                # 跳过分类项
                if "category" in li_class:
                    logger.info(f"  Skipping category LI: class='{li_class}'")
                    continue
                
                # 检查是否包含商品链接
                if li.find("a", href=link_pattern) or li.get("data-auction-id"):
                    product_items.append(li)
                    if DEBUG_LOG_HTML:
                        logger.info(f"  Added product LI: class='{li_class}'")
        else:
            logger.info(f"UL #{ul_idx}: class='{ul_class}' - No product links found, skipping")
    
    return product_items


def parse_shipping_info(li):
    """
    解析运费信息（修复版）
    返回格式：{"shippingFee": 190, "shippingText": "＋送料190円", "isFreeShipping": False}
    
    运费状态：
    - None: 运费未知
    - 0: 包邮（送料込み/送料無料）
    - 数字: 具体运费金额（円）
    """
    shipping = {
        "shippingFee": None,  # 运费金额（数字），None表示未知
        "shippingText": None,  # 运费原始文本
        "isFreeShipping": False  # 是否包邮
    }
    
    # 策略1: 查找 Product__postage 元素
    postage_elem = li.select_one('.Product__postage')
    if postage_elem:
        shipping_text = postage_elem.get_text(strip=True)
        shipping["shippingText"] = shipping_text
        logger.info(f"Found shipping text: '{shipping_text}'")
        
        # 如果文本为空，可能是送料込み（包邮）
        if not shipping_text:
            shipping["shippingFee"] = 0
            shipping["isFreeShipping"] = True
            shipping["shippingText"] = "送料込み"
            logger.info("Empty shipping text, assuming free shipping (送料込み)")
            return shipping
        
        # 格式1: "＋送料190円" 或 "送料190円"（包括范围运费 "送料398円〜"）
        match = re.search(r'送料(\d[\d,]*)円', shipping_text)
        if match:
            try:
                shipping["shippingFee"] = int(match.group(1).replace(',', ''))
                shipping["isFreeShipping"] = False
                
                # 如果包含"〜"或"~"（范围运费），记录警告但保留最低金额
                if '〜' in shipping_text or '~' in shipping_text:
                    logger.info(f"Shipping fee range detected: {shipping['shippingFee']}円〜 (minimum)")
                else:
                    logger.info(f"Shipping fee: {shipping['shippingFee']}円")
            except ValueError:
                pass
        
        # 格式2: "送料無料" 或 "無料"
        elif '無料' in shipping_text or '送料無料' in shipping_text:
            shipping["shippingFee"] = 0
            shipping["isFreeShipping"] = True
            logger.info("Free shipping (送料無料)")
        
        # 格式3: "送料未定" 或 "未定"
        elif '未定' in shipping_text:
            shipping["shippingFee"] = None
            shipping["isFreeShipping"] = False
            logger.info("Shipping fee undetermined (送料未定)")
        
        # 格式4: "着払い"
        elif '着払' in shipping_text:
            shipping["shippingFee"] = None
            shipping["isFreeShipping"] = False
            shipping["shippingText"] = "着払い"
            logger.info("Cash on delivery (着払い)")
        
        # 格式5: 其他情况，尝试提取任何数字
        else:
            match = re.search(r'(\d[\d,]*)円', shipping_text)
            if match:
                try:
                    shipping["shippingFee"] = int(match.group(1).replace(',', ''))
                    shipping["isFreeShipping"] = False
                    logger.info(f"Shipping fee extracted from general pattern: {shipping['shippingFee']}円")
                except ValueError:
                    pass
    else:
        # 策略2: 没有找到 Product__postage 元素
        # 检查是否在 Product__priceInfo 中有运费信息
        price_info = li.select_one('.Product__priceInfo')
        if price_info:
            price_info_text = price_info.get_text(strip=True)
            if '送料無料' in price_info_text or '送料込み' in price_info_text:
                shipping["shippingFee"] = 0
                shipping["isFreeShipping"] = True
                shipping["shippingText"] = "送料込み"
                logger.info("Free shipping detected from price info")
            else:
                # 也没有明确的运费信息，可能是包邮
                shipping["shippingFee"] = 0
                shipping["isFreeShipping"] = True
                shipping["shippingText"] = "送料込み(推定)"
                logger.info("No shipping info found, assuming free shipping (送料込み)")
        else:
            logger.info("No shipping info element found")
    
    return shipping


def parse_seller_location(li):
    """
    解析发货地/所在地（修复版）
    返回：prefecture 字符串，如 "東京都"
    """
    prefecture = None
    
    # 策略1: 查找 .Product__sellFrom 中的 span.u-textGray
    sell_from = li.select_one('.Product__sellFrom')
    if sell_from:
        sell_from_span = sell_from.find('span', class_='u-textGray')
        if sell_from_span:
            sell_from_text = sell_from_span.get_text(strip=True)
            logger.debug(f"Product__sellFrom text: '{sell_from_text}'")
            
            # 提取"〇〇県から発送"中的县名
            match = re.search(r'(.+?)から発送', sell_from_text)
            if match:
                prefecture = match.group(1).strip()
                logger.info(f"Prefecture from Product__sellFrom: {prefecture}")
            else:
                # 可能只有县名没有"から発送"
                prefecture = sell_from_text.strip()
                logger.info(f"Prefecture from Product__sellFrom (direct text): {prefecture}")
    
    # 策略2: 查找 "から発送" 文本（原有方法，作为兜底）
    if not prefecture:
        for p in li.find_all("p"):
            txt = p.get_text(strip=True)
            if "から発送" in txt:
                prefecture = txt.replace("から発送", "").strip()
                logger.info(f"Prefecture from 'から発送' pattern: {prefecture}")
                break
    
    # 策略3: 查找 div 中的发货信息
    if not prefecture:
        sell_from_divs = li.select('div[class*="sellFrom"], div[class*="SellFrom"]')
        for div in sell_from_divs:
            txt = div.get_text(strip=True)
            if txt:
                prefecture = txt.strip()
                logger.info(f"Prefecture from sellFrom div: {prefecture}")
                break
    
    # 策略4: 查找 span 或 div 中的 "から発送"
    if not prefecture:
        for elem in li.find_all(['span', 'div', 'p']):
            txt = elem.get_text(strip=True)
            if "から発送" in txt:
                match = re.search(r'(.+?)から発送', txt)
                if match:
                    prefecture = match.group(1).strip()
                    logger.info(f"Prefecture from general 'から発送' search: {prefecture}")
                    break
    
    # 策略5: 全局搜索都道府県名
    if not prefecture:
        li_text = li.get_text()
        for pref in PREFECTURES_LIST:
            if pref in li_text:
                prefecture = pref
                logger.info(f"Prefecture found by name matching: {prefecture}")
                break
    
    return prefecture


def parse_item(li, include_paypay=True):
    """解析单个商品列表项，提取所有信息"""
    # ---- 1. 商品链接 & 标题 & ID ----
    auction_link = None
    title = None
    item_id = None
    item_type = None  # 'auction' 或 'paypay'
    
    # 构建链接匹配模式
    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")

    # 优先使用CSS选择器精确定位标题链接
    title_link = li.select_one('.Product__titleLink')
    if title_link:
        auction_link = title_link
        href = title_link.get('href', '')
        if DEBUG_LOG_HTML:
            logger.info(f"Found title link via Product__titleLink: {href}")
    else:
        # 回退：尝试找 h3 中的链接
        h3 = li.find('h3', class_='Product__title')
        if h3:
            auction_link = h3.find('a', href=link_pattern)
            if auction_link and DEBUG_LOG_HTML:
                logger.info(f"Found title link via h3.Product__title: {auction_link.get('href', '')}")
        
        # 再回退：原有的 p 标签查找逻辑
        if not auction_link:
            for p in li.find_all("p"):
                a = p.find("a", href=link_pattern)
                if a:
                    auction_link = a
                    if DEBUG_LOG_HTML:
                        logger.info(f"Found auction link in p tag: {a.get('href', '')}")
                    break

    # 最终回退：查找任何 a 标签
    if not auction_link:
        auction_link = li.find("a", href=link_pattern)
        if auction_link and DEBUG_LOG_HTML:
            logger.info(f"Found auction link in fallback: {auction_link.get('href', '')}")

    if not auction_link:
        if DEBUG_LOG_HTML:
            # 打印所有链接用于调试
            all_links = [a.get('href', '') for a in li.find_all('a', href=True)]
            logger.info(f"Skipping item - no matching links found. Available links: {all_links[:5]}")
        return None

    href = auction_link.get("href", "")
    if not href:
        logger.warning("Empty href in auction link")
        return None
    
    # 提取商品 ID 和类型
    # 优先从 data-auction-id 属性获取
    data_id = auction_link.get('data-auction-id', '')
    if data_id:
        item_id = data_id
        # 根据ID前缀判断类型（PayPay商品ID以z开头）
        if item_id.startswith('z'):
            item_type = "paypay"
        else:
            item_type = "auction"
        logger.info(f"Found item via data-auction-id: {item_id} (type: {item_type})")
    else:
        # 回退：从URL中提取
        m = re.search(r"/auction/([a-z0-9]+)", href)
        if m:
            item_id = m.group(1)
            item_type = "auction"
            logger.info(f"Found auction item: {item_id}")
        else:
            m = re.search(r"/item/([a-z0-9]+)", href)
            if m:
                item_id = m.group(1)
                item_type = "paypay"
                logger.info(f"Found PayPay item: {item_id}")
    
    if not item_id:
        logger.warning(f"Could not extract item ID from href: {href}")
        return None

    # 提取标题 - 优先使用 data-auction-title 属性
    title = auction_link.get('data-auction-title', '').strip()
    if not title:
        # 回退：使用链接文本
        title = auction_link.get_text(strip=True)
    if not title:
        # 最后回退：使用 title 属性
        title = auction_link.get("title", "").strip()

    if not title:
        logger.warning(f"Title missing for item {item_id} (type: {item_type})")
    else:
        logger.info(f"Title: {title[:100]}")

    # ---- 2. 价格 ----
    price = 0
    price_found = False
    
    # 优先从 data-auction-price 属性获取
    data_price = auction_link.get('data-auction-price', '')
    if data_price:
        try:
            price = int(data_price)
            price_found = True
            logger.info(f"Price found from data-auction-price: {price}")
        except ValueError:
            pass
    
    # 回退：尝试找"落札価格"或"現在価格"或"即決価格"标签
    if not price_found:
        # 查找 Product__priceValue
        price_value = li.select_one('.Product__priceValue')
        if price_value:
            price_text = price_value.get_text(strip=True)
            match = re.search(r'([\d,]+)円', price_text)
            if match:
                try:
                    price = int(match.group(1).replace(",", ""))
                    price_found = True
                    logger.info(f"Price found from Product__priceValue: {price}")
                except ValueError:
                    pass
    
    # 兜底：查找所有 span 中的价格
    if not price_found:
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            m = re.match(r"^([\d,]+)円$", txt)
            if m:
                try:
                    price = int(m.group(1).replace(",", ""))
                    price_found = True
                    logger.info(f"Price found from span: {price}")
                    break
                except ValueError:
                    pass

    if not price_found:
        logger.info(f"Price not found for item {item_id} (type: {item_type})")

    # ---- 3. 运费信息 ----
    shipping = parse_shipping_info(li)

    # ---- 4. 即决价格（BuyNow） ----
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
                        try:
                            buynow_price = int(match.group(1).replace(',', ''))
                            logger.info(f"BuyNow price: {buynow_price}円")
                        except ValueError:
                            pass
            break

    # ---- 5. 入札数（仅拍卖） ----
    bid_count = 0
    if item_type == "auction":
        bid_link = li.find("a", href=re.compile(r"bid_hist"))
        if bid_link:
            bid_text = bid_link.get_text(strip=True)
            try:
                bid_count = int(re.sub(r"\D", "", bid_text))
                logger.info(f"Bid count: {bid_count}")
            except ValueError:
                pass

    # ---- 6. 结束时间 ----
    end_time = None
    
    # 需要在 Product 容器上查找
    product_div = li.find_parent('div', class_='Product')
    if not product_div:
        product_div = li
    
    # 策略1：从 data-auction-endtime 属性获取（Unix 时间戳格式）
    endtime_elem = product_div.select_one('[data-auction-endtime]')
    if endtime_elem:
        endtime_value = endtime_elem.get('data-auction-endtime', '')
        if endtime_value:
            try:
                timestamp = int(endtime_value)
                dt = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=9)))
                end_time = dt.isoformat()
                logger.info(f"End time from data-auction-endtime: {end_time} (timestamp: {timestamp})")
            except (ValueError, OSError) as e:
                logger.warning(f"Failed to parse data-auction-endtime value: {endtime_value} - {e}")
    
    # 策略2：如果上面没找到，尝试查找包含"終了"的元素
    if not end_time:
        ended_elem = li.find(lambda tag: tag.name in ["span", "p"] and "終了" in tag.get_text())
        if ended_elem:
            time_text = ended_elem.get_text(strip=True)
            end_time = parse_end_time(time_text)
            if end_time:
                logger.info(f"End time from ended element: {end_time}")
    
    # 策略3：全局正则搜索时间格式
    if not end_time:
        all_text = li.get_text(separator=" ", strip=True)
        m = re.search(r"\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}", all_text)
        if m:
            time_text = m.group()
            end_time = parse_end_time(time_text)
            if end_time:
                logger.info(f"End time from regex: {end_time}")
    
    # 策略4：从 data-timeleft 计算结束时间
    if not end_time:
        timeleft_elem = li.select_one('[data-timeleft]')
        if timeleft_elem:
            timeleft = timeleft_elem.get('data-timeleft', '')
            if timeleft:
                try:
                    seconds_left = int(timeleft)
                    now = datetime.now(timezone(timedelta(hours=9)))
                    end_time = (now + timedelta(seconds=seconds_left)).isoformat()
                    logger.info(f"End time calculated from data-timeleft: {end_time}")
                except ValueError:
                    pass
    
    if not end_time:
        logger.info(f"No end time found for item {item_id} (type: {item_type})")

    # ---- 7. 卖家 ID ----
    seller_id = None
    
    # 优先从 data-auction-auc-seller-id 获取
    seller_id_elem = product_div.select_one('[data-auction-auc-seller-id]')
    if seller_id_elem:
        seller_id = seller_id_elem.get('data-auction-auc-seller-id', '')
        if seller_id:
            logger.info(f"Seller ID from data-auction-auc-seller-id: {seller_id}")
    
    if not seller_id:
        seller_patterns = [
            re.compile(r"/user/"),
            re.compile(r"/seller/"),
            re.compile(r"userID=", re.IGNORECASE),
            re.compile(r"/show/rating", re.IGNORECASE)
        ]
        
        seller_link = None
        
        for pattern in seller_patterns:
            seller_link = li.find("a", href=pattern)
            if seller_link:
                break
        
        if seller_link:
            seller_href = seller_link.get("href", "")
            
            patterns = [
                r"/user/([^/?#]+)",
                r"/seller/([^/?#]+)",
                r"[?&]userID=([^&#]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, seller_href, re.IGNORECASE)
                if match:
                    seller_id = match.group(1)
                    break
            
            if seller_id:
                logger.info(f"Seller ID from link: {seller_id}")
            else:
                logger.info(f"Seller link found but ID could not be parsed: {seller_href}")
        else:
            logger.info(f"Seller not found for item {item_id} (type: {item_type})")

    # ---- 8. 好评率 ----
    rating = None
    
    # 优先查找 Product__ratingValue
    rating_elem = li.select_one('.Product__ratingValue')
    if rating_elem:
        rating_text = rating_elem.get_text(strip=True)
        if rating_text and rating_text != "新規":
            rating = rating_text
            logger.info(f"Rating found via Product__ratingValue: {rating}")
        elif rating_text == "新規":
            logger.info(f"Seller is new (新規) for item {item_id}")
    
    # 回退：从卖家链接附近查找
    if not rating:
        seller_link_check = li.find("a", href=re.compile(r"/seller/|/user/"))
        if seller_link_check:
            parent = seller_link_check.parent
            if parent:
                for _ in range(3):  # 向上查找3层
                    spans = parent.find_all("span")
                    for sp in spans:
                        txt = sp.get_text(strip=True)
                        if re.match(r"^\d{1,3}\.\d%$", txt):
                            rating = txt
                            logger.info(f"Rating found near seller: {rating}")
                            break
                    if rating:
                        break
                    parent = parent.parent
                    if not parent:
                        break

    # 全局兜底查找
    if not rating:
        for sp in li.find_all("span"):
            txt = sp.get_text(strip=True)
            if re.match(r"^\d{1,3}\.\d%$", txt):
                rating = txt
                logger.info(f"Rating found globally: {rating}")
                break

    if not rating:
        logger.info(f"Rating not found for item {item_id} (type: {item_type})")

    # ---- 9. 发货地（使用新的解析函数）----
    prefecture = parse_seller_location(li)
    if not prefecture:
        logger.info(f"Prefecture not found for item {item_id} (type: {item_type})")

    # ---- 10. 卖家类型（个人/商店） ----
    seller_type = "personal"
    if li.select_one('.Product__icon--store'):
        seller_type = "store"
        logger.info(f"Seller type: store")

    # ---- 11. 商品状态（新品/二手等） ----
    item_condition = None
    condition_icons = li.select('.Product__icon')
    for icon in condition_icons:
        icon_text = icon.get_text(strip=True)
        if icon_text in ['未使用', '新品', '中古', '新規']:
            item_condition = icon_text
            logger.info(f"Item condition: {item_condition}")
            break

    # ---- 12. 缩略图 URL ----
    thumbnail_url = None
    
    # 优先从 data-auction-img 属性获取
    data_img = auction_link.get('data-auction-img', '')
    if data_img:
        thumbnail_url = data_img
        logger.info(f"Thumbnail URL found from data-auction-img")
    else:
        # 回退：查找 img 标签
        img = li.find("img")
        if img:
            thumbnail_url = img.get("src") or img.get("data-src")
            if thumbnail_url:
                logger.info(f"Thumbnail URL found from img tag")

    # ---- 13. 构建返回对象 ----
    item = {
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

    logger.info(f"Successfully parsed item: [{item_type}] {item_id} - {title[:50] if title else 'N/A'}...")
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
        logger.debug("parse_end_time: empty text")
        return None

    # 清理文本
    text = text.replace("時", ":").replace("分", "")

    # 匹配日期时间
    m = re.search(r"(\d{1,4})?[\/-]?(\d{1,2})[\/-](\d{1,2})\s+(\d{1,2}):(\d{2})", text)
    if not m:
        logger.info(f"parse_end_time: could not parse '{text}'")
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
        logger.debug(f"parse_end_time: parsed '{text}' -> {dt.isoformat()}")
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
    skipped_duplicates = 0
    failed = 0
    
    logger.info(f"Starting to save {len(items)} items to DynamoDB table: {table.name}")
    
    for item in items:
        try:
            item_key = item["itemId"]
            
            table.put_item(
                Item={
                    "itemID": item_key,
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
            logger.info(f"Saved to DynamoDB: [{item.get('itemType')}] {item_key} - {item.get('title', 'N/A')[:50]}")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            skipped_duplicates += 1
            logger.info(f"Skipped duplicate: {item_key}")
        except Exception as e:
            failed += 1
            logger.error(f"Failed to save {item.get('itemId')}: {e}")

    logger.info(f"DynamoDB save completed: {saved} saved, {skipped_duplicates} duplicates skipped, {failed} failed")
    return saved
