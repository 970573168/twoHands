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

# ============ 过滤词库配置 ============
# 默认排除关键词（配件等），用空格分隔
DEFAULT_EXCLUDE_KEYWORDS = os.getenv("DEFAULT_EXCLUDE_KEYWORDS", 
    "液晶 LCD OLED パネル 画面 タッチパネル フロントパネル バックパネル "
    "バッテリー 交換用 修理用 補修用 部品 パーツ "
    "ケーブル ライトニングケーブル Lightning USB-C "
    "充電器 急速充電 アダプター ACアダプター モバイルバッテリー "
    "ワイヤレス充電 MagSafe "
    "ケース カバー 手帳型 フィルム ガラスフィルム 保護フィルム "
    "液晶フィルム レンズカバー ストラップ ホルダー スタンド "
    "バンパー リング "
    "保護 耐衝撃 防水ケース 防塵 ガード "
    "ジャンク部品 空箱 箱のみ 説明書 付属品のみ "
    "ケーブルのみ ケースのみ フィルムのみ")

# 默认包含关键词（可选，用于OR搜索），用空格分隔
DEFAULT_INCLUDE_KEYWORDS = os.getenv("DEFAULT_INCLUDE_KEYWORDS", "")

# 是否使用默认排除词库
USE_DEFAULT_EXCLUDE = os.getenv("USE_DEFAULT_EXCLUDE", "true").lower() == "true"

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


def get_filter_keywords(event):
    """
    从事件中获取过滤关键词
    优先级：event参数 > 环境变量 > 默认词库
    
    返回:
        tuple: (exclude_keywords_str, include_keywords_str)
            - exclude_keywords_str: 空格分隔的排除关键词字符串（用于ve参数）
            - include_keywords_str: 空格分隔的包含关键词字符串（用于vo参数）
    """
    # 获取排除关键词
    exclude_keywords = event.get("exclude_keywords", "")
    
    # 如果event中没有指定，检查是否使用默认排除词库
    if not exclude_keywords and USE_DEFAULT_EXCLUDE:
        # 使用环境变量中的排除词库，如果没有则使用默认词库
        exclude_keywords = os.getenv("CUSTOM_EXCLUDE_KEYWORDS", DEFAULT_EXCLUDE_KEYWORDS)
        logger.info(f"Using default/custom exclude keywords: {exclude_keywords[:100]}...")
    
    # 获取包含关键词（OR搜索条件）
    include_keywords = event.get("include_keywords", "")
    if not include_keywords:
        include_keywords = DEFAULT_INCLUDE_KEYWORDS
    
    # 清理关键词：去除多余空格，保留单个空格分隔
    if exclude_keywords:
        exclude_keywords = " ".join(exclude_keywords.split())
    if include_keywords:
        include_keywords = " ".join(include_keywords.split())
    
    logger.info(f"Filter keywords - Exclude: '{exclude_keywords[:100]}...', Include: '{include_keywords[:50]}...'")
    
    return exclude_keywords, include_keywords


def build_url(keyword, page, search_type, exclude_keywords="", include_keywords=""):
    """
    构建请求 URL，合并：
    1. 根据搜索类型选择对应的默认参数
    2. AUCTION_PARAM_* 环境变量中的自定义参数（可覆盖基础参数）
    3. 关键词和分页参数
    4. 过滤关键词（va/vo/ve参数）
    
    Yahoo拍卖的搜索参数：
    - va: 主搜索关键词（AND条件）
    - vo: 追加关键词（OR条件）
    - ve: 排除关键词（NOT条件，多个词用空格分隔）
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

    # 3. 设置主搜索关键词（va参数）
    params["va"] = keyword
    
    # 4. 设置包含关键词（vo参数，OR搜索条件）
    if include_keywords:
        params["vo"] = include_keywords
        logger.info(f"Setting vo (OR keywords): {include_keywords}")
    
    # 5. 设置排除关键词（ve参数）
    if exclude_keywords:
        params["ve"] = exclude_keywords
        logger.info(f"Setting ve (exclude keywords): {exclude_keywords[:100]}...")
    
    # 6. 设置分页参数
    params["b"] = str((page - 1) * ITEMS_PER_PAGE + 1)

    # 7. 选择基础 URL
    base_url = ACTIVE_BASE_URL if search_type == "active" else CLOSED_BASE_URL

    # 构建URL，确保va/vo/ve参数正确编码
    # 注意：空格在URL中会被urlencode转为+，这是Yahoo接受的格式
    final_url = f"{base_url}?{urlencode(params, quote_via=quote)}"
    
    logger.info(f"Built URL with va='{keyword}', vo='{include_keywords[:50] if include_keywords else ''}', ve='{exclude_keywords[:50] if exclude_keywords else ''}'")
    
    return final_url


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
    
    # 获取过滤关键词
    exclude_keywords, include_keywords = get_filter_keywords(event)
    
    logger.info(f"Scraping for keyword: '{keyword}', type: '{search_type}', include_paypay: {include_paypay}")
    if exclude_keywords:
        logger.info(f"Excluding keywords: {exclude_keywords}")
    if include_keywords:
        logger.info(f"Including keywords: {include_keywords}")

    items = scrape_auctions(keyword, search_type, include_paypay, exclude_keywords, include_keywords)

    if not items:
        logger.info("No items found")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "scraped": 0, 
                "saved": 0, 
                "type": search_type,
                "filters_applied": {
                    "exclude_keywords": exclude_keywords if exclude_keywords else None,
                    "include_keywords": include_keywords if include_keywords else None
                }
            }, ensure_ascii=False)
        }

    table = get_target_table(search_type)
    saved = save_items(items, table)

    logger.info(f"Scraping completed: {len(items)} items scraped, {saved} saved to DynamoDB")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "scraped": len(items),
            "saved": saved,
            "type": search_type,
            "filters_applied": {
                "exclude_keywords": exclude_keywords if exclude_keywords else None,
                "include_keywords": include_keywords if include_keywords else None
            }
        }, ensure_ascii=False)
    }


def scrape_auctions(keyword, search_type, include_paypay=True, exclude_keywords="", include_keywords=""):
    """抓取所有页面"""
    all_items = []

    for page in range(1, MAX_PAGES + 1):
        url = build_url(keyword, page, search_type, exclude_keywords, include_keywords)
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


# ... 其余函数保持不变（parse_html, find_product_items_in_container, 
#     parse_shipping_info, parse_seller_location, parse_item, 
#     parse_end_time, save_items）...
