import os
import re
import json
import time
import logging
import ipaddress
import unicodedata
from decimal import Decimal
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
PUBLIC_IP_CHECK_URL = os.getenv("PUBLIC_IP_CHECK_URL", "https://checkip.amazonaws.com").strip()
PUBLIC_IP_CHECK_TIMEOUT = float(os.getenv("PUBLIC_IP_CHECK_TIMEOUT", "5"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DEBUG_LOG_HTML = os.getenv("DEBUG_LOG_HTML", "false").lower() == "true"
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "50"))
INCLUDE_PAYPAY = os.getenv("INCLUDE_PAYPAY", "true").lower() == "true"
#限定STORE以及AUCTION用于限定拍卖
AUCTION_ABATCH = os.getenv("AUCTION_ABATCH", "1,2")

# ============ 详情爬取控制 ============
ENABLE_DETAIL_SCRAPE_ON_SEARCH = os.getenv("ENABLE_DETAIL_SCRAPE_ON_SEARCH", "true").lower() == "true"
DETAIL_REQUEST_INTERVAL = float(os.getenv("DETAIL_REQUEST_INTERVAL", "0.3"))
DETAIL_DESCRIPTION_MAX_CHARS = int(os.getenv("DETAIL_DESCRIPTION_MAX_CHARS", "3000"))
AUCTION_DETAIL_BASE = os.getenv("AUCTION_DETAIL_BASE", "https://auctions.yahoo.co.jp/jp/auction")

# ============ 过滤词库配置 ============
DEFAULT_EXCLUDE_KEYWORDS = os.getenv("DEFAULT_EXCLUDE_KEYWORDS",
    "空箱 元箱のみ 説明書 カタログ レンタル")

DEFAULT_INCLUDE_KEYWORDS = os.getenv("DEFAULT_INCLUDE_KEYWORDS", "")
USE_DEFAULT_EXCLUDE = os.getenv("USE_DEFAULT_EXCLUDE", "true").lower() == "true"
ENABLE_LOCAL_TITLE_FILTER = os.getenv("ENABLE_LOCAL_TITLE_FILTER", "true").lower() == "true"
LOCAL_TITLE_FILTER_STRICT = os.getenv("LOCAL_TITLE_FILTER_STRICT", "false").lower() == "true"


class LocalListingType:
    MAIN_PRODUCT = "MAIN_PRODUCT"
    ACCESSORY = "ACCESSORY"
    BOX_ONLY = "BOX_ONLY"
    PARTS = "PARTS"
    RENTAL = "RENTAL"
    BUNDLE = "BUNDLE"
    MANUAL_OR_CATALOG = "MANUAL_OR_CATALOG"
    CASE_OR_FILM = "CASE_OR_FILM"
    BATTERY_OR_CHARGER = "BATTERY_OR_CHARGER"
    ADAPTER_OR_MOUNT = "ADAPTER_OR_MOUNT"
    REMOTE_ONLY = "REMOTE_ONLY"
    CAR_AUDIO_OR_CARPLAY = "CAR_AUDIO_OR_CARPLAY"
    USB_OR_CABLE = "USB_OR_CABLE"
    CLOTHING_OR_BAG = "CLOTHING_OR_BAG"
    OTHER_BRAND_NOISE = "OTHER_BRAND_NOISE"
    UNKNOWN = "UNKNOWN"

# ============ 运输相关关键词 ============
SHIPPING_RELATED_KEYWORDS = [
    "送料", "発送", "配送", "運送", "宅配便", "郵便",
    "配送方法", "配送業者", "発送方法", "発送準備",
    "同梱", "まとめて購入", "まとめて取引",
    "お取引について", "お取引の取消し",
    "支払い金額", "お支払い", "お支払い金額", "振込手数料",
    "購入価格+消費税+送料", "送料元払い", "着払い",
    "佐川急便", "ヤマト運輸", "日本郵便", "ゆうパック",
    "長期不在", "再配達", "返却",
    "ご注文のキャンセル", "キャンセル対応",
    "注文確認メール", "ご注文前",
    "決済情報", "決済不可能",
    "弊社都合", "受け取り拒否",
    "ノークレーム", "ノーリターン",
    "ご注文点数", "注文から",
]

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

dynamodb = boto3.resource("dynamodb")


def log_public_egress_ip(action="", request_id=""):
    """每次 Lambda 调用开始时查询并记录爬虫的公网出口 IP。"""
    if not PUBLIC_IP_CHECK_URL:
        logger.warning("Public egress IP check skipped: PUBLIC_IP_CHECK_URL is empty")
        return None

    try:
        response = requests.get(
            PUBLIC_IP_CHECK_URL,
            timeout=PUBLIC_IP_CHECK_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        public_ip = response.text.strip()
        ipaddress.ip_address(public_ip)
        logger.info(
            "Crawler public egress IP: ip=%s action=%s request_id=%s",
            public_ip,
            action or "unknown",
            request_id or "unknown",
        )
        return public_ip
    except (requests.exceptions.RequestException, ValueError) as exc:
        logger.warning(
            "Public egress IP check failed: action=%s request_id=%s error=%s",
            action or "unknown",
            request_id or "unknown",
            exc,
        )
        return None


def get_target_table(search_type: str):
    """根据搜索类型返回对应的 DynamoDB 表"""
    if search_type == "active":
        return dynamodb.Table(TABLE_NAME_ACTIVE)
    return dynamodb.Table(TABLE_NAME_CLOSED)


def get_auction_params():
    """读取所有以 AUCTION_PARAM_ 开头的环境变量"""
    params = {}
    prefix = "AUCTION_PARAM_"
    for key, val in os.environ.items():
        if key.startswith(prefix):
            param_name = key[len(prefix):].lower()
            if val:
                params[param_name] = val
    return params


def normalize_title_for_filter(title: str) -> str:
    """统一全半角、大小写和空白，同时保留日文、英文、数字及型号符号。"""
    normalized = unicodedata.normalize("NFKC", str(title or "")).upper()
    return re.sub(r"\s+", " ", normalized).strip()


def _contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


MAIN_PRODUCT_SIGNALS = (
    "ゲーム機本体", "通電確認", "初期化確認済み", "動作確認済み",
)

CABLE_ONLY_SIGNALS = (
    "ケーブルのみ", "ケーブル単体", "HDMIケーブルのみ", "HDMI ケーブルのみ",
    "電源ケーブルのみ", "電源 ケーブルのみ", "LANケーブルのみ", "LAN ケーブルのみ",
    "充電ケーブルのみ", "充電 ケーブルのみ", "転送ケーブルのみ", "転送 ケーブルのみ",
)


def has_main_product_signal(title: str) -> bool:
    """检测明确的本体/工作状态信号；不把“本体なし”当作保留依据。"""
    text = normalize_title_for_filter(title)
    if _contains_any(text, ("本体なし", "本体無し", "本体は含まれません", "商品本体なし")):
        return False
    return (
        _contains_any(text, MAIN_PRODUCT_SIGNALS)
        or "本体" in text
        or re.search(r"(?:^|[^A-Z0-9])CFI-[A-Z0-9-]+", text) is not None
    )


def is_cable_only_title(title: str) -> bool:
    """只识别明确表示线缆单卖的标题，避免误伤“电源线附带”的本体。"""
    text = normalize_title_for_filter(title)
    return _contains_any(text, CABLE_ONLY_SIGNALS)


def classify_listing_type_by_title(title: str) -> str:
    text = normalize_title_for_filter(title)
    # Two explicit exceptions avoid ambiguous substrings: ペンケース is a bag
    # rather than a device case, and a tool body with its battery/charger is a
    # bundle even though the charger rule is evaluated before general bundles.
    if "本体" in text and _contains_any(text, ("セット", "一式", "まとめ")):
        return LocalListingType.BUNDLE
    if _contains_any(text, ("カーディガン", "ショルダーバッグ", "レザーバッグ", "ペンケース", "バッグ", "財布")):
        return LocalListingType.CLOTHING_OR_BAG
    # Strong product evidence wins over weak port/cable/accessory wording, but
    # never overrides an explicit standalone cable listing.
    if has_main_product_signal(text) and not is_cable_only_title(text):
        definitive_noise = (
            "レンタル", "貸出", "貸し出し", "1日~", "2日間", "往復送料無料", "管理NL",
            "空箱", "箱のみ", "元箱のみ", "外箱のみ", "EMPTY BOX", "BOX ONLY",
            "カタログ", "説明書", "取扱説明書", "マニュアル", "パンフレット", "雑誌",
            "スマホケース", "手帳型", "保護フィルム", "液晶フィルム", "ガラスフィルム",
            "リモコン", "VXX", "AXD", "PWW", "CARPLAY", "カーオーディオ",
            "USBメモリ", "USB メモリ",
        )
        if not _contains_any(text, definitive_noise):
            return LocalListingType.MAIN_PRODUCT
    rules = (
        (LocalListingType.RENTAL, (
            "レンタル", "貸出", "貸し出し", "1日~", "2日間", "往復送料無料", "管理NL",
        )),
        (LocalListingType.BOX_ONLY, (
            "空箱", "箱のみ", "元箱のみ", "外箱のみ", "レンズ用元箱",
            "元箱 複数", "元箱 4個", "APPLE IPHONE 空箱", "EMPTY BOX", "BOX ONLY",
        )),
        (LocalListingType.MANUAL_OR_CATALOG, (
            "カタログ", "説明書", "取扱説明書", "マニュアル", "パンフレット",
            "雑誌", "COMMERCIAL PHOTO", "コマーシャル・フォト",
        )),
        (LocalListingType.CASE_OR_FILM, (
            "スマホケース", "手帳型", "ガラスフィルム", "保護フィルム", "液晶フィルム",
            "レンズカバー", "OVERLAY", "9H", "耐衝撃", "全面保護", "ケース", "カバー", "フィルム",
        )),
        (LocalListingType.REMOTE_ONLY, ("リモコン", "VXX", "AXD", "PWW")),
        (LocalListingType.CAR_AUDIO_OR_CARPLAY, (
            "CARPLAY", "ANDROID AUTO", "カーオーディオ", "ディスプレイオーディオ",
            "楽ナビ", "バックカメラ", "カロッツェリア", "IPOD IPHONE",
        )),
        (LocalListingType.USB_OR_CABLE, (
            "USBメモリ", "USB メモリ", "LIGHTNING", "USB-C", "TYPE-C",
            "ミラーリング", *CABLE_ONLY_SIGNALS,
        )),
        (LocalListingType.ADAPTER_OR_MOUNT, (
            "マウントアダプター", "変換アダプター", "アダプター", "Mマウント", "Lマウント",
            "L39", "M39", "LM →", "RFマウント", "Eマウントアダプター", "Kマウント", "ヘリコイド付",
        )),
        (LocalListingType.ACCESSORY, (
            "レンズフード", "バヨネットフード", "フードキャップ", "レンズキャップ",
            "アイカップ", "アイピース", "L型ブラケット", "フォグリップ", "ブラケット",
            "グリップ", "ストラップ", "センターキャップ", "ヘッドシェル", "ツィーター",
            "スピーカー", "シェル付きカートリッジ",
        )),
        (LocalListingType.BATTERY_OR_CHARGER, (
            "互換バッテリー", "交換用バッテリー", "バッテリー交換", "修理 電池",
            "急速充電器", "USB充電器", "ACアダプター", "モバイルバッテリー",
            "充電器", "LP-E6", "NP-FZ100 互換",
        )),
        (LocalListingType.PARTS, (
            "部品", "パーツ", "修理用", "補修用", "交換用", "部品取り",
            "ジャンク部品", "背面カメラ", "SIMカードトレイ", "純正イヤホン",
        )),
        (LocalListingType.CLOTHING_OR_BAG, (
            "カーディガン", "ショルダーバッグ", "レザーバッグ", "ペンケース",
            "バッグ", "財布", "インク", "コンバーター",
        )),
    )
    for listing_type, keywords in rules:
        if _contains_any(text, keywords):
            return listing_type
    if re.search(r"(?:^|\s)(?:1D|2D|AUX)(?:\s|$)", text):
        return LocalListingType.CAR_AUDIO_OR_CARPLAY
    # 付属品を列挙しただけのレンズ商品は bundle にしない。
    if not ("レンズ" in text and _contains_any(text, ("元箱", "フード付き"))):
        if _contains_any(text, (
            "まとめ売り", "5点セット", "2台セット", "4台セット", "5個セット",
            "まとめ", "セット", "複数", "大量", "一式",
        )):
            return LocalListingType.BUNDLE
    return LocalListingType.MAIN_PRODUCT


def _model_tokens(text):
    normalized = normalize_title_for_filter(text)
    tokens = re.findall(r"(?=[A-Z0-9.-]*[A-Z])(?=[A-Z0-9.-]*\d)[A-Z0-9][A-Z0-9.-]{3,}", normalized)
    return list(dict.fromkeys(token.strip(".-") for token in tokens if token.strip(".-")))


def detect_target_context(keyword: str, category: str = "", brand: str = "", model: str = "") -> dict:
    target = normalize_title_for_filter(" ".join((keyword or "", category or "", brand or "", model or "")))
    keyword_model = normalize_title_for_filter(" ".join((keyword or "", model or "")))
    def has(values, source=keyword_model):
        return _contains_any(source, values)
    return {
        "is_phone": has(("IPHONE", "スマホ")),
        "is_camera_body": has(("Α1", "Α7", "Α9", "EOS", "R5", "R6", "Z9", "カメラ")),
        "is_lens": has(("NIKKOR", "SEL", "FE", "XF", "FUJINON", "SUMMILUX", "LUMIX", "DG", "F1.4", "F2.8", "24-70", "16-55", "24-200", "レンズ")),
        "is_battery": has(("BL1830B", "BL1860B", "BL1850B", "BL1890", "NP-FZ100", "LP-E6", "バッテリー", "充電池")),
        "is_charger": has(("充電器", "DC18RF", "ACアダプター", "ACK-E6")),
        "is_adapter": has(("アダプター", "マウント", "変換")),
        "is_measurement_device": _contains_any(target, ("KEYSIGHT", "AGILENT", "HIOKI", "ANALYZER", "MULTIMETER", "OSCILLOSCOPE", "FIELDFOX", "N9935B", "B2901A", "B2902A", "L4411A", "DAQ970A", "8163B", "測定器", "アナライザ")),
        "is_industrial_unit": _contains_any(target, ("MITSUBISHI ELECTRIC", "三菱電機", "AJ65", "GT25", "GT27", "ユニット", "表示器", "GOT")),
        "is_car_audio": _contains_any(target, ("CARPLAY", "カーオーディオ", "PIONEER", "カロッツェリア")),
        "is_parts": has(("部品", "パーツ", "修理用", "補修用")),
        "is_accessory": has(("フード", "キャップ", "グリップ", "ブラケット")),
        "target_tokens": _model_tokens(" ".join((model or "", keyword or ""))),
    }


def should_filter_item_by_context(item: dict, context: dict, strict: bool = False) -> tuple[bool, str]:
    listing_type = item.get("localListingType") or classify_listing_type_by_title(item.get("title", ""))
    item["localListingType"] = listing_type
    title = normalize_title_for_filter(item.get("title", ""))
    model_tokens = context.get("target_tokens", [])
    if context.get("is_measurement_device") and model_tokens:
        if not any(token in title for token in model_tokens):
            item["localListingType"] = LocalListingType.OTHER_BRAND_NOISE
            return True, "DIFFERENT_MEASUREMENT_MODEL"
    if context.get("is_industrial_unit") and model_tokens:
        if not any(token in title for token in model_tokens):
            item["localListingType"] = LocalListingType.OTHER_BRAND_NOISE
            return True, "DIFFERENT_INDUSTRIAL_MODEL"

    always_filtered = {
        LocalListingType.RENTAL, LocalListingType.BOX_ONLY,
        LocalListingType.MANUAL_OR_CATALOG, LocalListingType.CASE_OR_FILM,
        LocalListingType.REMOTE_ONLY, LocalListingType.USB_OR_CABLE,
        LocalListingType.CLOTHING_OR_BAG,
    }
    if listing_type in always_filtered:
        return True, listing_type
    if listing_type == LocalListingType.CAR_AUDIO_OR_CARPLAY:
        return (False, "TARGET_CAR_AUDIO") if context.get("is_car_audio") else (True, listing_type)
    if listing_type == LocalListingType.ACCESSORY:
        if context.get("is_accessory"):
            return False, "TARGET_ACCESSORY"
        if context.get("is_lens") or context.get("is_camera_body"):
            return True, "ACCESSORY_NOT_MAIN_PRODUCT"
    if listing_type == LocalListingType.ADAPTER_OR_MOUNT and not context.get("is_adapter"):
        return True, "ADAPTER_NOT_TARGET"
    if listing_type == LocalListingType.BATTERY_OR_CHARGER:
        if context.get("is_battery") or context.get("is_charger"):
            return False, "TARGET_BATTERY_OR_CHARGER"
        return True, "BATTERY_OR_CHARGER_NOT_TARGET"
    if listing_type == LocalListingType.PARTS and not context.get("is_parts"):
        return True, "PARTS_NOT_TARGET"
    if listing_type == LocalListingType.BUNDLE and strict:
        return True, "BUNDLE_STRICT"
    return False, ""


def sanitize_search_keyword(keyword: str) -> str:
    text = unicodedata.normalize("NFKC", str(keyword or ""))
    text = re.sub(r"[/()\[\]{}|→＋+]", " ", text)
    text = re.sub(r"[^A-Za-z0-9ぁ-んァ-ヶ一-龥々ー.\-\sΑ-Ωα-ω]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def simplify_search_keyword(keyword: str) -> str:
    sanitized = sanitize_search_keyword(keyword)
    words = sanitized.split()
    if not words:
        return ""
    if len(words) <= 6:
        return sanitized
    tokens = _model_tokens(sanitized)
    brand = words[0]
    strongest = max(tokens, key=lambda token: (any(c.isdigit() for c in token), len(token)), default="")
    if strongest and strongest.upper() != brand.upper():
        return f"{brand} {strongest}"
    return " ".join(words[:4])


def build_contextual_exclude_keywords(event):
    context = detect_target_context(
        event.get("keyword", ""), event.get("category", ""),
        event.get("brand", ""), event.get("model", ""),
    )
    words = ["空箱", "元箱のみ", "説明書", "カタログ", "レンタル"]
    if context["is_lens"] or context["is_camera_body"] or context["is_phone"]:
        words.extend(("ケース", "フィルム", "互換バッテリー", "レンズフード", "レンズキャップ"))
        if not context["is_charger"]:
            words.append("充電器")
    if context["is_measurement_device"]:
        words.extend(("ケース", "ケーブル", "取扱説明書", "カタログ"))
        target = normalize_title_for_filter(" ".join((event.get("keyword", ""), event.get("model", ""))))
        if "PROBE" not in target and "プローブ" not in target:
            words.append("プローブ")
    return " ".join(dict.fromkeys(words))


def _optional_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


def _search_context_kwargs(event):
    source_model = event.get("sourceModel", {}) or {}
    if isinstance(source_model, dict):
        source_brand = source_model.get("brand", "")
        source_model_name = source_model.get("model", "")
    else:
        # Some upstream callers send sourceModel as the model-name string
        # rather than the catalog object.  Accept both event shapes.
        source_brand = ""
        source_model_name = str(source_model)
    return {
        "category": event.get("category", ""),
        "brand": event.get("brand") or source_brand,
        "model": event.get("model") or source_model_name,
        "enable_local_title_filter": _optional_bool(event.get("enable_local_title_filter")),
        "local_title_filter_strict": _optional_bool(event.get("local_title_filter_strict")),
    }


def get_filter_keywords(event):
    """从事件中获取过滤关键词"""
    if "exclude_keywords" in event:
        exclude_keywords = event.get("exclude_keywords", "")
    elif USE_DEFAULT_EXCLUDE:
        exclude_keywords = build_contextual_exclude_keywords(event)
    else:
        exclude_keywords = ""
    
    include_keywords = event.get("include_keywords", "")
    if not include_keywords:
        include_keywords = DEFAULT_INCLUDE_KEYWORDS
    
    if exclude_keywords:
        exclude_keywords = " ".join(exclude_keywords.split())
    if include_keywords:
        include_keywords = " ".join(include_keywords.split())
    
    return exclude_keywords, include_keywords


def build_url(keyword, page, search_type, exclude_keywords="", include_keywords="", min_price=None):
    """构建请求 URL"""
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
    # Yahoo 的普通搜索框使用 p。此前改成高级搜索参数 va 后，部分关键词
    # （尤其是型号、英文编号）会得到不同或空的结果集。
    params["p"] = sanitize_search_keyword(keyword)
    params["abatch"] = AUCTION_ABATCH
    
    if include_keywords:
        params["vo"] = include_keywords
    
    if exclude_keywords:
        params["ve"] = exclude_keywords
    
    if min_price is not None and min_price > 0:
        params["min"] = str(min_price)
        params["price_type"] = "currentprice"
    
    params["b"] = str((page - 1) * ITEMS_PER_PAGE + 1)
    
    base_url = ACTIVE_BASE_URL if search_type == "active" else CLOSED_BASE_URL
    return f"{base_url}?{urlencode(params, quote_via=quote)}"


# ======================================
# 详情页URL构建
# ======================================

def build_detail_url(item_id):
    """构建商品详情页URL"""
    item_id = str(item_id).strip()
    base = AUCTION_DETAIL_BASE.rstrip('/')
    return f"{base}/{item_id}/description"


# ======================================
# 详情爬虫函数
# ======================================

DETAIL_NOISE_SECTION_PATTERN = re.compile(
    r"^(?:[【\[（(〈《<]*\s*)?"
    r"(?:お?問(?:い)?合わせ|出品拠点情報|注意事項|返品|落札後|"
    r"お?支払い|発送|配送|送料|状態ランク基準|店舗情報|会社概要|営業(?:時間|日))"
)
DETAIL_PRODUCT_SECTION_PATTERN = re.compile(
    r"^(?:[【\[（(〈《<]*\s*)?"
    r"(?:商品説明|商品詳細|商品の状態|状態|仕様|スペック|付属品|動作確認|製品情報)"
)
DETAIL_NOISE_LINE_PATTERNS = (
    re.compile(r"(?:〒\s*\d{3}-?\d{4}|住所[：:]|所在地[：:]|店舗住所[：:])"),
    re.compile(r"(?:営業時間|定休日|問い合わせ番号|お問い合わせ番号|管理番号)[：:]?"),
    re.compile(r"(?:電話|TEL|FAX)[：:]?\s*\d{2,}", re.IGNORECASE),
    re.compile(r"Yahoo!?\s*(?:JAPAN|オークション).*(?:トップ|ヘルプ|利用規約|プライバシー)"),
    re.compile(r"^(?:Yahoo!?\s*JAPAN|ヘルプ・お問い合わせ|利用規約|プライバシー(?:センター|ポリシー))$"),
    re.compile(r"Copyright\s*\(?(?:C|©)|無断転載", re.IGNORECASE),
)


def _description_to_text(text):
    """将详情 HTML 转为保留换行的纯文本。"""
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def clean_detail_description(text):
    """删除店铺、交易、配送及 Yahoo 页脚信息，保留商品本身的描述。"""
    plain_text = _description_to_text(text)

    lines = plain_text.split("\n")
    cleaned_lines = []
    skipping_noise_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line in ("&nbsp;", "nbsp;", "&amp;nbsp;", "&amp;nbsp"):
            continue

        if len(line) < 2 and not re.search(r"[A-Za-z0-9ぁ-んァ-ン一-龥]", line):
            continue

        if DETAIL_PRODUCT_SECTION_PATTERN.match(line):
            skipping_noise_section = False

        if DETAIL_NOISE_SECTION_PATTERN.match(line):
            skipping_noise_section = True
            continue

        if skipping_noise_section:
            continue

        if any(pattern.search(line) for pattern in DETAIL_NOISE_LINE_PATTERNS):
            continue

        if any(keyword in line for keyword in SHIPPING_RELATED_KEYWORDS):
            continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)

    # 去掉装饰符号，保留内容
    cleaned = re.sub(r"[【】★■◆◇●○◎]", " ", cleaned)
    # 删除分隔线
    cleaned = re.sub(r"[-_=ー－]{3,}", " ", cleaned)
    # 删除多余空格和空行
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def clean_description(text):
    """兼容旧调用名称。"""
    return clean_detail_description(text)


def scrape_item_detail(item_id):
    """
    爬取单个商品的详情描述
    
    返回:
        dict or None: {
            "itemId", "title", "description", "url", "scrapedAt"
        }
    """
    url = build_detail_url(item_id)
    logger.info(f"Scraping detail for item {item_id}")
    
    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT}
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Detail request failed for {item_id}: {e}")
        return None
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 提取标题
    title = None
    
    # 从 JSON-LD 提取
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        try:
            ld_json = json.loads(script_tag.string)
            if isinstance(ld_json, dict):
                title = ld_json.get("name", "")
        except json.JSONDecodeError:
            pass
    
    # 从 title 标签提取
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            title = re.sub(r'^Yahoo!オークション\s*-\s*', '', title_text)
    
    if not title:
        title = "Unknown Title"
    
    # 提取原始描述；清洗在完整提取后统一执行
    raw_description = ""
    
    # 从 __NEXT_DATA__ JSON 提取
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        try:
            data = json.loads(next_data.string)
            
            def find_desc(obj, depth=0):
                if depth > 10:
                    return None
                if isinstance(obj, dict):
                    if "descriptionHtml" in obj and obj["descriptionHtml"]:
                        return obj["descriptionHtml"]
                    for v in obj.values():
                        result = find_desc(v, depth + 1)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_desc(item, depth + 1)
                        if result:
                            return result
                return None
            
            raw_desc = find_desc(data) or ""
            if raw_desc:
                raw_description = _description_to_text(raw_desc)
        except (json.JSONDecodeError, KeyError):
            pass
    
    # 兜底：从 template 或 body 提取
    if not raw_description:
        template_tag = soup.find("template", attrs={"shadowrootmode": "open"})
        target = template_tag or soup.find("body")
        if target:
            raw_description = target.get_text(separator="\n", strip=True)

    cleaned_description = clean_detail_description(raw_description)
    cleaned_description = cleaned_description[:DETAIL_DESCRIPTION_MAX_CHARS]
    raw_length = len(raw_description)
    cleaned_length = len(cleaned_description)
    clean_ratio = (
        (Decimal(cleaned_length) / Decimal(raw_length)).quantize(Decimal("0.0001"))
        if raw_length else Decimal("0")
    )
    cleaned_at = datetime.now(timezone.utc).isoformat()
    
    result = {
        "itemId": item_id,
        "title": title,
        "description": cleaned_description,
        "detailDescription": cleaned_description,
        "detailDescriptionRaw": raw_description,
        "detailDescriptionCleaned": cleaned_description,
        "detailDescriptionRawLength": raw_length,
        "detailDescriptionCleanedLength": cleaned_length,
        "detailDescriptionLength": cleaned_length,
        "detailDescriptionCleanRatio": clean_ratio,
        "detailCleanedAt": cleaned_at,
        "url": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(
        "Detail scraped for %s: raw_len=%s cleaned_len=%s clean_ratio=%s",
        item_id, raw_length, cleaned_length, clean_ratio
    )
    return result


def scrape_active_item_current_price(item_id):
    """从商品详情页读取最终复核所需的当前价、即决价和结束时间。"""
    url = build_detail_url(item_id)
    try:
        response = requests.get(
            url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.warning("Current price request failed for %s: %s", item_id, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    result = {"itemId": str(item_id), "url": url}

    def walk(value, depth=0):
        if depth > 12:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).lower()
                if normalized in ("currentprice", "price") and "price" not in result:
                    try:
                        result["price"] = int(Decimal(str(child)))
                    except (ValueError, TypeError, ArithmeticError):
                        pass
                elif normalized in ("buynowprice", "buyoutprice") and "buynowPrice" not in result:
                    try:
                        result["buynowPrice"] = int(Decimal(str(child)))
                    except (ValueError, TypeError, ArithmeticError):
                        pass
                elif normalized in ("endtime", "enddate", "pricevaliduntil") and "endTime" not in result:
                    if child:
                        result["endTime"] = str(child)
                elif normalized in ("isclosed", "isended", "ended") and child is True:
                    result["isEnded"] = True
                walk(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                walk(child, depth + 1)

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            walk(json.loads(script.string or "{}"))
        except json.JSONDecodeError:
            continue
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        try:
            walk(json.loads(next_data.string or "{}"))
        except json.JSONDecodeError:
            pass

    page_text = soup.get_text(" ", strip=True)
    if any(marker in page_text for marker in ("オークションは終了", "このオークションは終了")):
        result["isEnded"] = True
    return result if int(result.get("price", 0) or 0) > 0 else None


def enrich_item_with_detail(item):
    """
    给列表页解析出的 item 补充详情描述。
    搜索 closed / active 时直接调用。
    """
    item_id = str(item.get("itemId", "")).strip()
    if not item_id:
        return item

    detail = scrape_item_detail(item_id)

    if not detail:
        item["detailScrapeStatus"] = "FAILED"
        item["detailScrapeError"] = "scrape_item_detail returned None"
        item["detailScrapedAt"] = datetime.now(timezone.utc).isoformat()
        item["detailDescription"] = ""
        item["detailDescriptionRaw"] = ""
        item["detailDescriptionCleaned"] = ""
        item["detailDescriptionRawLength"] = 0
        item["detailDescriptionCleanedLength"] = 0
        item["detailTitle"] = ""
        item["detailUrl"] = build_detail_url(item_id)
        item["detailDescriptionLength"] = 0
        item["detailDescriptionCleanRatio"] = Decimal("0")
        item["detailCleanedAt"] = ""
        return item

    description = detail.get("description", "") or ""

    item["detailDescriptionRaw"] = detail.get("detailDescriptionRaw", "")
    item["detailDescriptionCleaned"] = detail.get("detailDescriptionCleaned", description)
    item["detailDescription"] = item["detailDescriptionCleaned"]
    item["detailDescriptionRawLength"] = detail.get("detailDescriptionRawLength", 0)
    item["detailDescriptionCleanedLength"] = detail.get("detailDescriptionCleanedLength", len(description))
    item["detailTitle"] = detail.get("title", "")
    # 列表页标题缺失时用详情页标题修复顶层 title，Analyzer 读取的是顶层字段。
    if not str(item.get("title", "")).strip() and item["detailTitle"] not in ("", "Unknown Title"):
        item["title"] = item["detailTitle"]
    item["detailUrl"] = detail.get("url", "")
    item["detailScrapedAt"] = detail.get("scrapedAt", datetime.now(timezone.utc).isoformat())
    item["detailDescriptionLength"] = detail.get("detailDescriptionLength", len(description))
    item["detailDescriptionCleanRatio"] = detail.get("detailDescriptionCleanRatio", Decimal("0"))
    item["detailCleanedAt"] = detail.get("detailCleanedAt", "")
    item["detailScrapeStatus"] = "COMPLETED" if description else "EMPTY"
    item["detailScrapeError"] = ""

    return item


def scrape_multiple_details(item_ids, save_to_db=False, search_type="active"):
    """
    批量爬取多个商品详情
    
    参数:
        item_ids: 商品ID列表
        save_to_db: 是否保存到 DynamoDB
        search_type: active / closed
    """
    results = []
    table = get_target_table(search_type) if save_to_db else None
    
    for index, item_id in enumerate(item_ids):
        detail = scrape_item_detail(item_id)

        if detail:
            results.append(detail)

            if save_to_db and table:
                try:
                    desc = detail.get("description", "")
                    table.update_item(
                        Key={"itemID": item_id},
                        UpdateExpression="""
                            SET detailDescription = :desc,
                                detailDescriptionRaw = :raw,
                                detailDescriptionCleaned = :cleaned,
                                detailDescriptionRawLength = :raw_length,
                                detailDescriptionCleanedLength = :cleaned_length,
                                detailDescriptionCleanRatio = :clean_ratio,
                                detailCleanedAt = :cleaned_at,
                                detailTitle = :title,
                                detailUrl = :url,
                                detailScrapedAt = :now,
                                detailDescriptionLength = :length,
                                detailScrapeStatus = :status,
                                modifiedIndexPk = :modified_index_pk,
                                modifiedAt = :now
                        """,
                        ExpressionAttributeValues={
                            ":desc": desc[:DETAIL_DESCRIPTION_MAX_CHARS],
                            ":raw": detail.get("detailDescriptionRaw", ""),
                            ":cleaned": detail.get("detailDescriptionCleaned", desc),
                            ":raw_length": detail.get("detailDescriptionRawLength", 0),
                            ":cleaned_length": detail.get("detailDescriptionCleanedLength", len(desc)),
                            ":clean_ratio": detail.get("detailDescriptionCleanRatio", Decimal("0")),
                            ":cleaned_at": detail.get("detailCleanedAt", ""),
                            ":title": detail.get("title", ""),
                            ":url": detail.get("url", ""),
                            ":now": detail.get("scrapedAt", datetime.now(timezone.utc).isoformat()),
                            ":length": len(desc),
                            ":status": "COMPLETED" if desc else "EMPTY",
                            ":modified_index_pk": "ALL",
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to save detail for {item_id}: {e}")
        
        if index < len(item_ids) - 1:
            time.sleep(DETAIL_REQUEST_INTERVAL)
    
    return results


# ======================================
# Lambda Handler
# ======================================

def lambda_handler(event, context):
    """
    主入口函数
    
    支持的模式:
    1. search: 搜索商品列表（含详情抓取）
    2. detail: 爬取单个商品详情
    3. batch_detail: 批量爬取商品详情
    4. scrape_and_parse: 搜索 + 详情爬取一体化
    """
    action = event.get("action", "search")
    request_id = getattr(context, "aws_request_id", "") if context else ""
    log_public_egress_ip(action=action, request_id=request_id)
    
    # ========== 模式1：搜索商品（含详情） ==========
    if action == "search":
        keyword = event.get("keyword")
        if not keyword:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing keyword"}, ensure_ascii=False)
            }
        
        search_type = event.get("search_type", "closed")
        include_paypay = event.get("include_paypay", INCLUDE_PAYPAY)
        min_price = event.get("min_price")
        if min_price is not None:
            try:
                min_price = int(min_price)
            except (ValueError, TypeError):
                min_price = None
        
        exclude_keywords, include_keywords = get_filter_keywords(event)
        
        logger.info(f"Scraping for keyword: '{keyword}', type: '{search_type}'")
        
        items = scrape_auctions(keyword, search_type, include_paypay,
                                exclude_keywords, include_keywords, min_price,
                                **_search_context_kwargs(event))
        
        if not items:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "scraped": 0,
                    "saved": 0,
                    "type": search_type,
                    "min_price_applied": min_price
                }, ensure_ascii=False)
            }
        
        table = get_target_table(search_type)
        saved = save_items(items, table)
        
        # 统计详情抓取情况
        detail_stats = {
            "total": len(items),
            "completed": sum(1 for i in items if i.get("detailScrapeStatus") == "COMPLETED"),
            "empty": sum(1 for i in items if i.get("detailScrapeStatus") == "EMPTY"),
            "failed": sum(1 for i in items if i.get("detailScrapeStatus") == "FAILED"),
            "not_scraped": sum(1 for i in items if i.get("detailScrapeStatus") in (None, "", "NOT_SCRAPED")),
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "scraped": len(items),
                "saved": saved,
                "type": search_type,
                "min_price_applied": min_price,
                "detail_stats": detail_stats,
                "filters_applied": {
                    "exclude_keywords": exclude_keywords if exclude_keywords else None,
                    "include_keywords": include_keywords if include_keywords else None
                }
            }, ensure_ascii=False)
        }
    
    # ========== 模式2：爬取单个商品详情 ==========
    elif action == "detail":
        item_id = event.get("item_id") or event.get("itemId") or event.get("auctionId")
        if not item_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing item_id"}, ensure_ascii=False)
            }
        
        detail = scrape_item_detail(item_id)
        if not detail:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Failed to scrape detail for {item_id}"}, ensure_ascii=False)
            }
        
        # 可选保存到DB
        if event.get("save_to_db"):
            table = get_target_table(event.get("search_type", "active"))
            try:
                table.update_item(
                    Key={"itemID": item_id},
                    UpdateExpression="""
                        SET detailDescription = :desc,
                            detailDescriptionRaw = :raw,
                            detailDescriptionCleaned = :cleaned,
                            detailDescriptionRawLength = :raw_len,
                            detailDescriptionCleanedLength = :cleaned_len,
                            detailDescriptionCleanRatio = :clean_ratio,
                            detailCleanedAt = :cleaned_at,
                            detailTitle = :title,
                            detailUrl = :url,
                            detailScrapedAt = :now,
                            detailDescriptionLength = :len,
                            detailScrapeStatus = :status,
                            modifiedIndexPk = :modified_index_pk,
                            modifiedAt = :now
                    """,
                    ExpressionAttributeValues={
                        ":desc": detail["description"],
                        ":raw": detail.get("detailDescriptionRaw", ""),
                        ":cleaned": detail.get("detailDescriptionCleaned", detail["description"]),
                        ":raw_len": detail.get("detailDescriptionRawLength", 0),
                        ":cleaned_len": detail.get("detailDescriptionCleanedLength", len(detail["description"])),
                        ":clean_ratio": detail.get("detailDescriptionCleanRatio", Decimal("0")),
                        ":cleaned_at": detail.get("detailCleanedAt", ""),
                        ":title": detail["title"],
                        ":url": detail["url"],
                        ":now": detail["scrapedAt"],
                        ":len": len(detail["description"]),
                        ":status": "COMPLETED" if detail["description"] else "EMPTY",
                        ":modified_index_pk": "ALL",
                    }
                )
            except Exception as e:
                logger.error(f"Failed to save detail: {e}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "itemId": detail["itemId"],
                "title": detail["title"],
                "description": detail["description"],
                "detailDescriptionRaw": detail.get("detailDescriptionRaw", ""),
                "detailDescriptionCleaned": detail.get("detailDescriptionCleaned", ""),
                "detailDescriptionRawLength": detail.get("detailDescriptionRawLength", 0),
                "detailDescriptionCleanedLength": detail.get("detailDescriptionCleanedLength", 0),
                "detailDescriptionLength": detail.get("detailDescriptionLength", 0),
                "detailDescriptionCleanRatio": detail.get("detailDescriptionCleanRatio", Decimal("0")),
                "detailCleanedAt": detail.get("detailCleanedAt", ""),
                "url": detail["url"],
                "scrapedAt": detail["scrapedAt"]
            }, ensure_ascii=False, default=str)
        }
    
    # ========== 模式3：批量爬取商品详情 ==========
    elif action == "batch_detail":
        item_ids = event.get("item_ids") or event.get("itemIds") or []
        if not item_ids:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing item_ids"}, ensure_ascii=False)
            }
        
        if isinstance(item_ids, str):
            item_ids = [i.strip() for i in item_ids.split(",") if i.strip()]
        
        save_to_db = event.get("save_to_db", True)
        search_type = event.get("search_type", "active")
        
        results = scrape_multiple_details(item_ids, save_to_db=save_to_db, search_type=search_type)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "total": len(item_ids),
                "scraped": len(results),
                "results": results[:10],  # 只返回前10条
                "item_ids": item_ids[:10]
            }, ensure_ascii=False, default=str)
        }
    
    # ========== 模式4：搜索 + 详情爬取一体化 ==========
    elif action == "scrape_and_parse":
        keyword = event.get("keyword")
        if not keyword:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing keyword"}, ensure_ascii=False)
            }
        
        search_type = event.get("search_type", "closed")
        include_paypay = event.get("include_paypay", INCLUDE_PAYPAY)
        exclude_keywords, include_keywords = get_filter_keywords(event)
        
        items = scrape_auctions(keyword, search_type, include_paypay,
                                exclude_keywords, include_keywords, event.get("min_price"),
                                **_search_context_kwargs(event))
        
        if not items:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "search": {"scraped": 0, "saved": 0},
                    "details": {"total": 0, "success": 0},
                    "type": search_type
                }, ensure_ascii=False)
            }
        
        table = get_target_table(search_type)
        saved = save_items(items, table)
        
        detail_stats = {
            "completed": sum(1 for i in items if i.get("detailScrapeStatus") == "COMPLETED"),
            "empty": sum(1 for i in items if i.get("detailScrapeStatus") == "EMPTY"),
            "failed": sum(1 for i in items if i.get("detailScrapeStatus") == "FAILED"),
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "search": {"scraped": len(items), "saved": saved},
                "details": {
                    "total": len(items),
                    "success": detail_stats["completed"],
                    "empty": detail_stats["empty"],
                    "failed": detail_stats["failed"],
                },
                "type": search_type,
                "item_ids": [item["itemId"] for item in items[:20]]
            }, ensure_ascii=False, default=str)
        }
    
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False)
        }


# ======================================
# 搜索和解析函数
# ======================================

def scrape_auctions(keyword, search_type, include_paypay=True,
                    exclude_keywords="", include_keywords="", min_price=None,
                    scrape_details=None, category="", brand="", model="",
                    enable_local_title_filter=None,
                    local_title_filter_strict=None):
    """抓取列表页；scrape_details 可显式控制是否同步抓取详情。"""
    if scrape_details is None:
        scrape_details = ENABLE_DETAIL_SCRAPE_ON_SEARCH
    if enable_local_title_filter is None:
        enable_local_title_filter = ENABLE_LOCAL_TITLE_FILTER
    if local_title_filter_strict is None:
        local_title_filter_strict = LOCAL_TITLE_FILTER_STRICT

    if not include_keywords:
        include_keywords = DEFAULT_INCLUDE_KEYWORDS

    all_items = []

    for page in range(1, MAX_PAGES + 1):
        url = build_url(keyword, page, search_type, exclude_keywords, include_keywords, min_price)
        logger.info(f"Fetching page {page}: {url}")

        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                simplified = simplify_search_keyword(keyword)
                if simplified:
                    retry_url = build_url(
                        simplified, page, search_type, exclude_keywords,
                        include_keywords, min_price,
                    )
                    logger.warning(
                        "Search returned 404; retrying once: original=%s simplified=%s",
                        keyword, simplified,
                    )
                    try:
                        resp = requests.get(
                            retry_url, timeout=REQUEST_TIMEOUT,
                            headers={"User-Agent": USER_AGENT},
                        )
                        resp.raise_for_status()
                    except requests.exceptions.RequestException as retry_error:
                        logger.error("Simplified search retry failed for page %s: %s", page, retry_error)
                        continue
                else:
                    logger.error("Request failed for page %s: %s", page, e)
                    continue
            else:
                logger.error("Request failed for page %s: %s", page, e)
                continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            continue

        items = parse_html(resp.text, search_type, include_paypay)
        if not items:
            break
        parsed_item_count = len(items)

        if enable_local_title_filter:
            context = detect_target_context(keyword, category, brand, model)
            before = len(items)
            kept, removed = [], []
            for item in items:
                should_filter, reason = should_filter_item_by_context(
                    item, context, strict=local_title_filter_strict,
                )
                item["localFilterReason"] = reason
                (removed if should_filter else kept).append(item)
            logger.info(
                "Local title filter: keyword=%s before=%s after=%s removed=%s",
                keyword, before, len(kept), len(removed),
            )
            for item in removed[:10]:
                logger.info(
                    "Filtered item: type=%s reason=%s title=%s",
                    item.get("localListingType"), item.get("localFilterReason"),
                    item.get("title", "")[:160],
                )
            items = kept

        # 普通爬虫可同步抓详情；分析工作流会显式关闭并按利润延迟抓取
        if scrape_details:
            enriched_items = []
            for index, item in enumerate(items):
                try:
                    enriched_item = enrich_item_with_detail(item)
                    enriched_items.append(enriched_item)
                except Exception as e:
                    logger.error(f"详情补充失败 itemId={item.get('itemId')}: {e}")
                    item["detailScrapeStatus"] = "FAILED"
                    item["detailScrapeError"] = str(e)[:500]
                    item["detailScrapedAt"] = datetime.now(timezone.utc).isoformat()
                    enriched_items.append(item)

                # 请求间隔
                if index < len(items) - 1:
                    time.sleep(DETAIL_REQUEST_INTERVAL)

            items = enriched_items

        all_items.extend(items)

        if parsed_item_count < ITEMS_PER_PAGE:
            break

    logger.info(f"Total items scraped: {len(all_items)}")
    return all_items


def parse_html(html, search_type, include_paypay=True):
    """解析 HTML，提取商品列表"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    if search_type == "closed":
        container = soup.select_one("#closedSearchItems")
    else:
        selectors = [".Products__list", ".ProductList", "[data-auction-list]",
                     ".SearchResults__list", "#auctionsItems", ".Products__items"]
        container = None
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                break

    product_items = find_product_items_in_container(
        container if container else soup.body, search_type, include_paypay
    )

    for li in product_items:
        try:
            item = parse_item(li, include_paypay)
            if item:
                items.append(item)
        except Exception as e:
            logger.warning(f"Failed to parse product item: {e}")

    logger.info(f"Parsed {len(items)} items")
    return items


def find_product_items_in_container(container, search_type, include_paypay):
    """在容器中查找商品列表项"""
    product_items = []

    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")

    uls = ([container] if getattr(container, "name", None) == "ul" else []) + container.find_all("ul")
    for ul in uls:
        ul_class = " ".join(ul.get("class", [])).lower()

        if any(skip in ul_class for skip in ["category", "nav", "menu", "footer", "header", "breadcrumb"]):
            continue

        has_links = any(
            li.find("a", href=link_pattern) or li.get("data-auction-id")
            for li in ul.find_all("li", recursive=False)
        )

        if has_links:
            for li in ul.find_all("li", recursive=False):
                li_class = " ".join(li.get("class", [])).lower()
                if "category" in li_class:
                    continue
                if li.find("a", href=link_pattern) or li.get("data-auction-id"):
                    product_items.append(li)

    return product_items


def parse_shipping_info(li):
    """解析运费信息"""
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
            try:
                shipping["shippingFee"] = int(match.group(1).replace(',', ''))
            except ValueError:
                pass
        elif '無料' in shipping_text or '送料無料' in shipping_text:
            shipping["shippingFee"] = 0
            shipping["isFreeShipping"] = True

    return shipping


def parse_seller_location(li):
    """解析发货地"""
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
    """解析单个商品列表项"""
    if include_paypay:
        link_pattern = re.compile(r"(/auction/|paypayfleamarket\.yahoo\.co\.jp/item/)")
    else:
        link_pattern = re.compile(r"/auction/")

    # 优先选择真正承载标题/元数据的链接。直接取第一个 /auction/ 链接时，
    # Yahoo 新版 closed 页面经常会选中只有图片、没有文本的链接。
    link_candidates = li.find_all("a", href=link_pattern)
    auction_link = li.select_one('a.Product__titleLink, a[data-auction-title]')
    if not auction_link:
        title_container = li.select_one(
            '.Product__title, [class*="ProductTitle"], [class*="ItemTitle"]'
        )
        if title_container:
            auction_link = title_container.find('a', href=link_pattern)
    if not auction_link and link_candidates:
        auction_link = max(
            link_candidates,
            key=lambda link: (
                bool(link.get('data-auction-title')),
                bool(link.get('title') or link.get('aria-label')),
                len(link.get_text(" ", strip=True)),
            ),
        )

    if not auction_link:
        return None

    href = auction_link.get("href", "")
    if not href:
        return None

    # 提取商品 ID 和类型
    item_id = None
    item_type = None

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

    if not item_id:
        return None

    # 提取标题
    title_sources = [
        auction_link.get('data-auction-title', ''),
        auction_link.get_text(" ", strip=True),
        auction_link.get("title", ""),
        auction_link.get("aria-label", ""),
    ]
    metadata_link = li.select_one('[data-auction-title]')
    title_sources.insert(0, li.get('data-auction-title', ''))
    if metadata_link:
        title_sources.insert(0, metadata_link.get('data-auction-title', ''))
    title_elem = li.select_one(
        '.Product__title, .Product__titleLink, [class*="ProductTitle"], '
        '[class*="ItemTitle"], h3'
    )
    if title_elem:
        title_sources.append(title_elem.get_text(" ", strip=True))
    image = li.find('img')
    if image:
        title_sources.extend([image.get('alt', ''), image.get('title', '')])
    title = next((str(value).strip() for value in title_sources if str(value).strip()), "")
    if not title:
        logger.warning("商品标题缺失: itemId=%s url=%s", item_id, href)

    # 提取价格
    price = 0
    price_metadata = li.select_one('[data-auction-price]')
    data_price = (
        auction_link.get('data-auction-price', '')
        or li.get('data-auction-price', '')
        or (price_metadata.get('data-auction-price', '') if price_metadata else '')
    )
    if data_price:
        try:
            price = int(data_price)
        except ValueError:
            pass

    if price == 0:
        price_value = li.select_one('.Product__priceValue')
        if price_value:
            price_text = price_value.get_text(strip=True)
            match = re.search(r'([\d,]+)円', price_text)
            if match:
                try:
                    price = int(match.group(1).replace(",", ""))
                except ValueError:
                    pass

    if price == 0:
        for span in li.find_all("span"):
            txt = span.get_text(strip=True)
            m = re.match(r"^([\d,]+)円$", txt)
            if m:
                try:
                    price = int(m.group(1).replace(",", ""))
                    break
                except ValueError:
                    pass

    # 运费
    shipping = parse_shipping_info(li)

    # 即决价格
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
                        except ValueError:
                            pass
            break

    # 入札数
    bid_count = 0
    if item_type == "auction":
        bid_elem = li.select_one('[data-auction-bidcount], [data-bid-count]')
        if bid_elem:
            raw_bid_count = (
                bid_elem.get('data-auction-bidcount')
                or bid_elem.get('data-bid-count')
                or ''
            )
            match = re.search(r'\d+', str(raw_bid_count).replace(',', ''))
            if match:
                bid_count = int(match.group())
        if bid_count == 0:
            bid_elem = li.find("a", href=re.compile(r"bid_hist|bidHistory", re.I))
        if bid_count == 0 and not bid_elem:
            bid_elem = li.select_one('.Product__bid, [class*="BidCount"], [class*="bidCount"]')
        if bid_count == 0 and bid_elem:
            match = re.search(r'\d[\d,]*', bid_elem.get_text(" ", strip=True))
            if match:
                bid_count = int(match.group().replace(',', ''))
        if bid_count == 0:
            match = re.search(r'入札(?:件数)?\s*[：:]?\s*(\d[\d,]*)', li.get_text(" ", strip=True))
            if match:
                bid_count = int(match.group(1).replace(',', ''))

    # 结束时间
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
            time_text = ended_elem.get_text(strip=True)
            end_time = parse_end_time(time_text)

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

    # 卖家ID
    seller_id = None
    seller_id_elem = product_div.select_one('[data-auction-auc-seller-id]')
    if seller_id_elem:
        seller_id = seller_id_elem.get('data-auction-auc-seller-id', '')

    if not seller_id:
        seller_patterns = [
            re.compile(r"/user/"), re.compile(r"/seller/"),
            re.compile(r"userID=", re.IGNORECASE), re.compile(r"/show/rating", re.IGNORECASE)
        ]
        seller_link = None
        for pattern in seller_patterns:
            seller_link = li.find("a", href=pattern)
            if seller_link:
                break
        if seller_link:
            seller_href = seller_link.get("href", "")
            for pattern in [r"/user/([^/?#]+)", r"/seller/([^/?#]+)", r"[?&]userID=([^&#]+)"]:
                match = re.search(pattern, seller_href, re.IGNORECASE)
                if match:
                    seller_id = match.group(1)
                    break

    # 好评率
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

    # 发货地
    prefecture = parse_seller_location(li)

    # 卖家类型
    seller_type = "store" if li.select_one('.Product__icon--store') else "personal"

    # 商品状态
    item_condition = None
    condition_icons = li.select('.Product__icon')
    for icon in condition_icons:
        icon_text = icon.get_text(strip=True)
        if icon_text in ['未使用', '新品', '中古', '新規']:
            item_condition = icon_text
            break

    # 缩略图
    thumbnail_url = auction_link.get('data-auction-img', '')
    if not thumbnail_url:
        img = li.find("img")
        if img:
            thumbnail_url = img.get("src") or img.get("data-src") or ""

    # 构建返回对象
    item = {
        "itemId": item_id,
        "itemType": item_type,
        "title": title,
        "localListingType": classify_listing_type_by_title(title),
        "localFilterReason": "",
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

    return item


def parse_end_time(text):
    """解析结束时间"""
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
    """保存商品到 DynamoDB，包含详情描述"""
    saved = 0
    skipped_duplicates = 0
    failed = 0

    for item in items:
        try:
            item_key = item["itemId"]
            modified_at = datetime.now(timezone.utc).isoformat()
            table.put_item(
                Item={
                    "itemID": item_key,
                    "modifiedIndexPk": "ALL",
                    "modifiedAt": modified_at,
                    "itemType": item.get("itemType", "unknown"),
                    "title": item.get("title", ""),
                    "localListingType": item.get("localListingType", LocalListingType.UNKNOWN),
                    "localFilterReason": item.get("localFilterReason", ""),
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
                    
                    # 详情字段
                    "detailDescription": item.get("detailDescription", ""),
                    "detailDescriptionRaw": item.get("detailDescriptionRaw", ""),
                    "detailDescriptionCleaned": item.get("detailDescriptionCleaned", ""),
                    "detailDescriptionRawLength": item.get("detailDescriptionRawLength", 0),
                    "detailDescriptionCleanedLength": item.get("detailDescriptionCleanedLength", 0),
                    "detailDescriptionCleanRatio": item.get("detailDescriptionCleanRatio", Decimal("0")),
                    "detailCleanedAt": item.get("detailCleanedAt", ""),
                    "detailTitle": item.get("detailTitle", ""),
                    "detailUrl": item.get("detailUrl", ""),
                    "detailScrapedAt": item.get("detailScrapedAt", ""),
                    "detailDescriptionLength": item.get("detailDescriptionLength", 0),
                    "detailScrapeStatus": item.get("detailScrapeStatus", "NOT_SCRAPED"),
                    "detailScrapeError": item.get("detailScrapeError", ""),
                    
                    "ttl": int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())
                },
                ConditionExpression="attribute_not_exists(itemID)"
            )
            saved += 1

        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            skipped_duplicates += 1
            
            # 已存在时也刷新列表字段。旧逻辑只更新详情，导致第一次保存为空的
            # closed title、bidCount、价格等字段以后永远无法被修复。
            try:
                title = str(item.get("title", "")).strip()
                list_updates = [
                    "price = :price", "buynowPrice = :buynow", "shippingFee = :shipping_fee",
                    "shippingText = :shipping_text", "isFreeShipping = :free_shipping",
                    "bidCount = :bid_count", "endTime = :end_time", "sellerId = :seller_id",
                    "sellerRating = :seller_rating", "sellerType = :seller_type",
                    "prefecture = :prefecture", "itemCondition = :item_condition",
                    "#item_url = :item_url", "thumbnailUrl = :thumbnail", "scrapedAt = :scraped_at",
                    "localListingType = :local_listing_type", "localFilterReason = :local_filter_reason",
                ]
                if title:
                    list_updates.insert(0, "#item_title = :item_title")
                table.update_item(
                    Key={"itemID": item["itemId"]},
                    UpdateExpression="SET " + ", ".join(list_updates) + ", " + """
                            detailDescription = :desc,
                            detailDescriptionRaw = :raw,
                            detailDescriptionCleaned = :cleaned,
                            detailDescriptionRawLength = :raw_len,
                            detailDescriptionCleanedLength = :cleaned_len,
                            detailDescriptionCleanRatio = :clean_ratio,
                            detailCleanedAt = :cleaned_at,
                            detailTitle = :detail_title,
                            detailUrl = :detail_url,
                            detailScrapedAt = :detail_scraped_at,
                            detailDescriptionLength = :detail_len,
                            detailScrapeStatus = :detail_status,
                            detailScrapeError = :detail_error,
                            lastDetailUpdatedAt = :now,
                            modifiedIndexPk = :modified_index_pk,
                            modifiedAt = :now
                    """,
                    ExpressionAttributeNames={
                        "#item_url": "url",
                        **({"#item_title": "title"} if title else {}),
                    },
                    ExpressionAttributeValues={
                        **({":item_title": title} if title else {}),
                        ":price": item.get("price", 0),
                        ":buynow": item.get("buynowPrice"),
                        ":shipping_fee": item.get("shippingFee"),
                        ":shipping_text": item.get("shippingText", ""),
                        ":free_shipping": item.get("isFreeShipping", False),
                        ":bid_count": item.get("bidCount", 0),
                        ":end_time": item.get("endTime") or "unknown",
                        ":seller_id": item.get("sellerId") or "unknown",
                        ":seller_rating": item.get("sellerRating") or "unknown",
                        ":seller_type": item.get("sellerType", "personal"),
                        ":prefecture": item.get("prefecture") or "unknown",
                        ":item_condition": item.get("itemCondition"),
                        ":item_url": item.get("url") or "",
                        ":thumbnail": item.get("thumbnailUrl") or "",
                        ":scraped_at": item.get("scrapedAt") or datetime.now(timezone.utc).isoformat(),
                        ":local_listing_type": item.get("localListingType", LocalListingType.UNKNOWN),
                        ":local_filter_reason": item.get("localFilterReason", ""),
                        ":modified_index_pk": "ALL",
                        ":desc": item.get("detailDescription", ""),
                        ":raw": item.get("detailDescriptionRaw", ""),
                        ":cleaned": item.get("detailDescriptionCleaned", ""),
                        ":raw_len": item.get("detailDescriptionRawLength", 0),
                        ":cleaned_len": item.get("detailDescriptionCleanedLength", 0),
                        ":clean_ratio": item.get("detailDescriptionCleanRatio", Decimal("0")),
                        ":cleaned_at": item.get("detailCleanedAt", ""),
                        ":detail_title": item.get("detailTitle", ""),
                        ":detail_url": item.get("detailUrl", ""),
                        ":detail_scraped_at": item.get("detailScrapedAt", ""),
                        ":detail_len": item.get("detailDescriptionLength", 0),
                        ":detail_status": item.get("detailScrapeStatus", "NOT_SCRAPED"),
                        ":detail_error": item.get("detailScrapeError", ""),
                        ":now": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to update detail for duplicate {item.get('itemId')}: {e}")

        except Exception as e:
            failed += 1
            logger.error(f"Failed to save {item.get('itemId')}: {e}")

    logger.info(f"Saved: {saved}, Skipped: {skipped_duplicates}, Failed: {failed}")
    return saved
