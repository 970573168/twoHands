import hashlib
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
import socket
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

import boto3
from token_usage import record_token_usage

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
secretsmanager = boto3.client("secretsmanager")

# ============================================
# 所有配置项都从环境变量读取
# ============================================

# ========== AI 模式配置 ==========
AI_MODE = os.environ.get("AI_MODE", "doubao")

# Gemini 配置
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-latest")
GEMINI_URL = os.environ.get("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent")
GEMINI_TIMEOUT = int(os.environ.get("GEMINI_TIMEOUT", "60"))
GEMINI_MAX_TOKENS = int(os.environ.get("GEMINI_MAX_TOKENS", "4000"))

# 豆包配置
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "qwen-plus-character")
DOUBAO_URL = os.environ.get("DOUBAO_URL", "https://ws-8lxmxlbemcgcus5u.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions")
DOUBAO_TIMEOUT = int(os.environ.get("DOUBAO_TIMEOUT", "250"))
DOUBAO_MAX_TOKENS = int(os.environ.get("DOUBAO_MAX_TOKENS", "6000"))

# OpenAI 配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_TIMEOUT = int(os.environ.get("OPENAI_TIMEOUT", "60"))
OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "4000"))

# 故障切换冷却时间
AI_FAILOVER_COOLDOWN = int(os.environ.get("AI_FAILOVER_COOLDOWN", "300"))

# ========== 官方售价过滤配置 ==========
MIN_OFFICIAL_PRICE_JPY = int(os.environ.get("MIN_OFFICIAL_PRICE_JPY", "50000"))
SKIP_IF_OFFICIAL_PRICE_MISSING = os.environ.get(
    "SKIP_IF_OFFICIAL_PRICE_MISSING", "false"
).lower() == "true"

# ========== 品类筛选配置（新增） ==========
AUCTION_ANALYSIS_MIN_SCORE = int(os.environ.get("AUCTION_ANALYSIS_MIN_SCORE", "6"))
BLOCK_HIGH_COUNTERFEIT = os.environ.get("BLOCK_HIGH_COUNTERFEIT", "false").lower() == "true"
CATALOG_SAVE_BUT_DISABLE_SCAN = os.environ.get("CATALOG_SAVE_BUT_DISABLE_SCAN", "true").lower() == "true"

# ========== 旧版配置（向后兼容） ==========
SECRET_NAME = os.environ.get("SECRET_NAME", "")
API_URL = os.environ.get("API_URL", "")
MODEL = os.environ.get("AI_MODEL", "")

# ========== API 调用参数配置 ==========
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
TOP_P = float(os.environ.get("TOP_P", "1.0"))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "90"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))

# 系统提示词配置
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", 
    "You are a helpful assistant that returns data in JSON format.")

# 发现任务配置
MAX_CATEGORIES = int(os.environ.get("MAX_CATEGORIES", "20"))
MAX_BRANDS = int(os.environ.get("MAX_BRANDS", "20"))
MAX_MODELS = int(os.environ.get("MAX_MODELS", "50"))

# Token 和超时控制配置
MAX_TOTAL_TOKENS = int(os.environ.get("MAX_TOTAL_TOKENS", "100000"))
LAMBDA_TIMEOUT_SECONDS = int(os.environ.get("LAMBDA_TIMEOUT_SECONDS", "840"))
LAMBDA_TIMEOUT_BUFFER = int(os.environ.get("LAMBDA_TIMEOUT_BUFFER", "30"))

# 处理流程配置
CATEGORY_LIMIT = int(os.environ.get("CATEGORY_LIMIT", "5"))
BRAND_LIMIT = int(os.environ.get("BRAND_LIMIT", "3"))
API_CALL_DELAY = float(os.environ.get("API_CALL_DELAY", "1.0"))

# 重试配置
RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

# 数据来源标识
DATA_SOURCE = os.environ.get("DATA_SOURCE", "AI_DISCOVERY")
LINK_CRAWLER_TABLE_NAME = os.environ.get("LINK_CRAWLER_TABLE_NAME", "")

# GSI 查询回退配置
ENABLE_GSI_QUERY = os.environ.get("ENABLE_GSI_QUERY", "true").lower() == "true"
GSI_QUERY_MAX_RETRIES = int(os.environ.get("GSI_QUERY_MAX_RETRIES", "2"))

# ============================================

# ============================================
# 品类定义（新增）
# ============================================

# 优先品类：小型 + 保值 + 低假货风险
HIGH_PRIORITY_CATEGORIES = {
    # 数码/小型电子
    "スマートフォン", "スマホ", "携帯電話",
    "タブレット", "iPad",
    "パソコン", "ノートパソコン", "PC", "Mac", "MacBook",
    "カメラ", "デジタルカメラ", "ミラーレスカメラ", "一眼レフ",
    "レンズ", "交換レンズ",
    "ゲーム機", "ポータブルゲーム機", "Nintendo Switch", "PS5", "PS4",
    "オーディオ", "ヘッドホン", "イヤホン", "スピーカー", "イヤフォン",
    "スマートウォッチ", "ウェアラブル",
    "モニター", "ディスプレイ",
    "グラフィックボード", "GPU",
    "CPU", "メモリ", "SSD",
    "マザーボード",
    
    # 测量仪器（電動工具は型番識別が不安定なため対象外）
    "測定器", "レーザー測定器",
    
    # 高端文具
    "万年筆", "高級文具",
    
    # 收藏类（低风险）
    "フィギュア", "模型", "ホビー", "プラモデル",
    
    # 音频/乐器
    "ギター", "エレキギター", "アコースティックギター",
    "ベース", "シンセサイザー", "DJ機器",
    "マイク", "オーディオインターフェース",
    
    # 家电（小型高价值）
    "ロボット掃除機", "空気清浄機", "加湿器",
    "コーヒーメーカー", "エスプレッソマシン",
    "ミシン", "アイロン",
    
    # 户外/运动（小型装备）
    "ゴルフクラブ", "テニスラケット",
    "双眼鏡", "望遠鏡",
    "GPS機器", "アクションカメラ",
}

# 中风险品类：可能有假货但制造难度较高
MEDIUM_RISK_CATEGORIES = {
    # 收藏类（中风险）
    "トレーディングカード", "カードゲーム",
    "レトロゲーム", "レトロゲームソフト",
    "限定品", "コレクターズアイテム",
    
    # 品牌配件
    "ブランド時計",
    "腕時計",
    
    # 小型奢侈配件
    "サングラス", "眼鏡",
    "ライター",
    "筆箱", "ペンケース",
}

# 高风险品类：假货较多
HIGH_COUNTERFEIT_RISK_CATEGORIES = {
    "ブランドバッグ", "バッグ",
    "財布", "ブランド財布",
    "ジュエリー", "貴金属", "宝石",
    "スニーカー", "スニーカー限定",
    "衣類", "ブランド衣類",
    "ベルト", "ブランドベルト",
    "時計",  # 泛称时风险更高
}

# 绝对排除品类
BLOCKED_CATEGORIES = {
    "電動工具", "インパクトドライバー", "電動ドリル", "マルチツール",
    "食品", "飲料", "酒", "調味料",
    "健康食品", "サプリメント",
    "家具", "大型家具", "インテリア家具",
    "ベッド", "ソファ", "チェスト", "テレビ台",
    "日用品", "消耗品", "化粧品",
    "雑貨", "ペット用品", "ベビー用品",
    "本", "コミック", "CD", "DVD", "ブルーレイ",
    "文房具",  # 普通文具
    "衣類", "服", "ファッション",  # 普通衣类
    "靴", "サンダル",
    "カーテン", "ラグ", "クッション",
    "シーツ", "布団",
    "食器", "キッチン用品",
    "おもちゃ", "ぬいぐるみ",
}

# 高假货风险品牌（即使品类允许，这些品牌也需特别处理）
HIGH_COUNTERFEIT_BRANDS = {
    "ROLEX", "ロレックス",
    "OMEGA", "オメガ",
    "LOUIS VUITTON", "ルイヴィトン", "ルイ・ヴィトン",
    "CHANEL", "シャネル",
    "HERMES", "エルメス",
    "GUCCI", "グッチ",
    "PRADA", "プラダ",
    "CARTIER", "カルティエ",
    "TIFFANY", "ティファニー",
    "BVLGARI", "ブルガリ",
    "SUPREME", "シュプリーム",
    "NIKE", "ナイキ",  # 限定款假货多
    "ADIDAS", "アディダス",  # 限定款假货多
    "YEEZY", "イージー",
    "JORDAN", "ジョーダン",
    "OFF-WHITE", "オフホワイト",
    "BALENCIAGA", "バレンシアガ",
    "MONCLER", "モンクレール",
    "CANADA GOOSE", "カナダグース",
}

# ============================================

# AI 模式状态管理
_ai_mode_state = {
    "current_mode": None,
    "failed_modes": {},
}

# 全局Token计数器
_total_tokens_used = 0

# 记录Lambda开始时间
_lambda_start_time = None

# GSI 权限状态缓存
_gsi_permission_granted = True

# ============================================
# 官方售价辅助函数
# ============================================

def safe_int_price(value, default: int = 0) -> int:
    """安全转换整数（用于价格）"""
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(",", "").replace("円", "").replace("¥", "").replace("¥", "").strip()
            if not value:
                return default
        return int(float(value))
    except Exception:
        return default


def get_official_price_jpy(product_item: dict) -> int:
    """
    从 PRODUCT 记录中读取官方售价（日元）。
    兼容多个可能字段名。
    """
    candidate_fields = [
        "official_price_jpy", "officialPriceJpy",
        "official_price", "officialPrice",
        "msrp_jpy", "msrp",
        "launch_price_jpy", "launchPriceJpy",
        "retail_price_jpy", "retailPriceJpy",
    ]
    
    for field in candidate_fields:
        if field in product_item:
            price = safe_int_price(product_item.get(field), 0)
            if price > 0:
                return price
    
    return 0


def should_skip_by_official_price(product_item: dict) -> dict:
    """
    判断是否因为官方售价过低而跳过。
    返回: {"skip": bool, "official_price_jpy": int, "reason": str}
    """
    official_price = get_official_price_jpy(product_item)
    
    if official_price <= 0:
        if SKIP_IF_OFFICIAL_PRICE_MISSING:
            return {"skip": True, "official_price_jpy": 0, "reason": "OFFICIAL_PRICE_MISSING"}
        return {"skip": False, "official_price_jpy": 0, "reason": "OFFICIAL_PRICE_MISSING_BUT_ALLOWED"}
    
    if official_price < MIN_OFFICIAL_PRICE_JPY:
        return {"skip": True, "official_price_jpy": official_price, "reason": "OFFICIAL_PRICE_TOO_LOW"}
    
    return {"skip": False, "official_price_jpy": official_price, "reason": "OFFICIAL_PRICE_OK"}


# ============================================
# 品类适合度评分（新增）
# ============================================

def is_good_for_auction_analysis(
    category: str,
    brand: str = "",
    model: str = "",
    official_price_jpy: int = 0
) -> dict:
    """
    判断商品是否适合 Yahoo Auction 自动分析。
    返回: {
        "allowed": bool,
        "risk_level": str,  # "LOW", "MEDIUM", "COUNTERFEIT_REVIEW", "HIGH"
        "reason": str,
        "score": int,
        "catalog_scan_disabled": bool,
        "catalog_scan_disabled_reason": str,
    }
    """
    category_norm = normalize(category)
    brand_norm = normalize(brand).upper()
    model_norm = normalize(model)
    
    result = {
        "allowed": False,
        "risk_level": "HIGH",
        "reason": "",
        "score": 0,
        "catalog_scan_disabled": True,
        "catalog_scan_disabled_reason": "",
    }
    
    # 绝对排除品类
    for blocked in BLOCKED_CATEGORIES:
        if blocked in category_norm:
            result["reason"] = f"BLOCKED_CATEGORY:{blocked}"
            result["catalog_scan_disabled_reason"] = f"品类已被排除: {blocked}"
            return result
    
    # 官方售价过滤
    if official_price_jpy > 0 and official_price_jpy < MIN_OFFICIAL_PRICE_JPY:
        result["reason"] = "OFFICIAL_PRICE_TOO_LOW"
        result["catalog_scan_disabled_reason"] = f"官方售价过低: {official_price_jpy} < {MIN_OFFICIAL_PRICE_JPY}"
        return result
    
    score = 0
    category_matched = "NONE"
    
    # 1. 品类匹配度
    for allowed_cat in HIGH_PRIORITY_CATEGORIES:
        if allowed_cat in category_norm:
            score += 4
            category_matched = "HIGH_PRIORITY"
            break
    
    if category_matched == "NONE":
        for med_cat in MEDIUM_RISK_CATEGORIES:
            if med_cat in category_norm:
                score += 2
                category_matched = "MEDIUM_RISK"
                break
    
    if category_matched == "NONE":
        for risky_cat in HIGH_COUNTERFEIT_RISK_CATEGORIES:
            if risky_cat in category_norm:
                score += 1
                category_matched = "COUNTERFEIT_RISK"
                break
    
    # 2. 价格评分
    if official_price_jpy >= MIN_OFFICIAL_PRICE_JPY:
        score += 2
    elif official_price_jpy >= MIN_OFFICIAL_PRICE_JPY * 0.5:
        score += 1
    
    # 3. 品牌型号明确度
    if len(brand_norm) >= 2:
        score += 1
    if len(model_norm) >= 2:
        score += 1
    
    # 4. 高假货风险品牌检查
    counterfeit_brand = False
    for risky_brand in HIGH_COUNTERFEIT_BRANDS:
        if risky_brand in brand_norm:
            counterfeit_brand = True
            score -= 2
            break
    
    result["score"] = score
    
    # 5. 高假货风险品类处理
    if category_matched == "COUNTERFEIT_RISK" or counterfeit_brand:
        if BLOCK_HIGH_COUNTERFEIT:
            result["reason"] = "HIGH_COUNTERFEIT_RISK_BLOCKED"
            result["risk_level"] = "HIGH"
            result["catalog_scan_disabled_reason"] = "高风险品类/品牌，已阻止自动分析"
            return result
        elif score >= AUCTION_ANALYSIS_MIN_SCORE:
            result["allowed"] = True
            result["risk_level"] = "COUNTERFEIT_REVIEW"
            result["reason"] = "COUNTERFEIT_REVIEW_REQUIRED"
            result["catalog_scan_disabled"] = CATALOG_SAVE_BUT_DISABLE_SCAN
            result["catalog_scan_disabled_reason"] = "高风险品类，需人工审核"
            return result
        else:
            result["reason"] = "HIGH_COUNTERFEIT_LOW_SCORE"
            result["catalog_scan_disabled_reason"] = f"高风险品类且评分不足: {score} < {AUCTION_ANALYSIS_MIN_SCORE}"
            return result
    
    # 6. 中风险品类处理
    if category_matched == "MEDIUM_RISK":
        if score >= AUCTION_ANALYSIS_MIN_SCORE:
            result["allowed"] = True
            result["risk_level"] = "MEDIUM"
            result["reason"] = "MEDIUM_RISK_PASSED"
            result["catalog_scan_disabled"] = False
        else:
            result["reason"] = "MEDIUM_RISK_LOW_SCORE"
            result["catalog_scan_disabled_reason"] = f"中风险品类评分不足: {score} < {AUCTION_ANALYSIS_MIN_SCORE}"
        return result
    
    # 7. 低风险品类处理
    if score >= AUCTION_ANALYSIS_MIN_SCORE:
        result["allowed"] = True
        result["risk_level"] = "LOW"
        result["reason"] = "PASSED"
        result["catalog_scan_disabled"] = False
    else:
        result["reason"] = f"LOW_SCORE:{score}"
        result["catalog_scan_disabled_reason"] = f"评分不足: {score} < {AUCTION_ANALYSIS_MIN_SCORE}"
    
    return result

# ============================================


# ============================================
# AI 配置管理
# ============================================

def _get_api_key_from_secrets(mode: str) -> str:
    """从 Secrets Manager 获取 API Key"""
    secret_name_map = {
        "gemini": f"gemini-api-key-{os.environ.get('ENVIRONMENT', 'dev')}",
        "doubao": f"doubao-api-key-{os.environ.get('ENVIRONMENT', 'dev')}",
        "openai": f"openai-api-key-{os.environ.get('ENVIRONMENT', 'dev')}",
    }
    
    secret_name = secret_name_map.get(mode)
    if not secret_name:
        return ""
    
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString", "")
        if not secret_string:
            return ""
        
        try:
            secret_dict = json.loads(secret_string)
            return (
                secret_dict.get("apiKey") or 
                secret_dict.get("api_key") or 
                secret_dict.get("key") or
                secret_dict.get("GEMINI_API_KEY") or
                secret_dict.get("DOUBAO_API_KEY") or
                secret_dict.get("OPENAI_API_KEY") or
                ""
            )
        except json.JSONDecodeError:
            return secret_string.strip()
    except Exception as e:
        log("DEBUG", "从 Secrets Manager 获取 Key 失败", mode=mode, error=str(e))
        return ""


def get_ai_config(mode: str = None) -> dict:
    """获取 AI 配置"""
    if mode is None:
        mode = AI_MODE
    
    configs = {
        "gemini": {
            "name": "gemini", "type": "gemini", "url": GEMINI_URL,
            "key": GEMINI_API_KEY or _get_api_key_from_secrets("gemini"),
            "model": GEMINI_MODEL, "timeout": GEMINI_TIMEOUT, "max_tokens": GEMINI_MAX_TOKENS,
        },
        "doubao": {
            "name": "doubao", "type": "openai_compatible", "url": DOUBAO_URL,
            "key": DOUBAO_API_KEY or _get_api_key_from_secrets("doubao"),
            "model": DOUBAO_MODEL, "timeout": DOUBAO_TIMEOUT, "max_tokens": DOUBAO_MAX_TOKENS,
        },
        "openai": {
            "name": "openai", "type": "openai_compatible", "url": OPENAI_URL,
            "key": OPENAI_API_KEY or _get_api_key_from_secrets("openai"),
            "model": OPENAI_MODEL, "timeout": OPENAI_TIMEOUT, "max_tokens": OPENAI_MAX_TOKENS,
        }
    }
    
    if mode not in configs and SECRET_NAME and API_URL:
        return {
            "name": "legacy", "type": "openai_compatible", "url": API_URL,
            "key": _get_legacy_api_key(), "model": MODEL or "doubao-seed-2-1-pro-260628",
            "timeout": REQUEST_TIMEOUT, "max_tokens": int(os.environ.get("MAX_TOKENS", "4000")),
        }
    
    if mode not in configs:
        log("WARN", f"未知的 AI_MODE: {mode}，使用 gemini")
        mode = "gemini"
    
    return configs[mode]


def _get_legacy_api_key() -> str:
    if not SECRET_NAME: return ""
    try:
        response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response.get("SecretString", "")
        if not secret_string: return ""
        try:
            secret_data = json.loads(secret_string)
            return secret_data.get("apiKey") or secret_data.get("api_key") or secret_data.get("key") or ""
        except json.JSONDecodeError:
            return secret_string.strip()
    except Exception:
        return ""


def get_available_ai_config() -> dict:
    fallback_order = ["gemini", "doubao", "openai"]
    ordered_modes = [AI_MODE] + [m for m in fallback_order if m != AI_MODE] if AI_MODE in fallback_order else fallback_order
    now = time.time()
    
    for mode in ordered_modes:
        if mode in _ai_mode_state["failed_modes"]:
            fail_time = _ai_mode_state["failed_modes"][mode]
            if now - fail_time < AI_FAILOVER_COOLDOWN:
                log("INFO", f"AI 模式 '{mode}' 冷却中")
                continue
            else:
                del _ai_mode_state["failed_modes"][mode]
        
        config = get_ai_config(mode)
        if config["key"]:
            log("INFO", f"选择 AI 模式: '{mode}'")
            return config
    
    if SECRET_NAME and API_URL:
        legacy_config = get_ai_config("legacy")
        if legacy_config["key"]:
            log("INFO", "使用旧版 AI 配置")
            return legacy_config
    
    raise RuntimeError("所有 AI 模式均不可用")


def mark_ai_mode_failed(mode: str, error: str = ""):
    _ai_mode_state["failed_modes"][mode] = time.time()
    log("WARN", f"AI 模式 '{mode}' 标记为故障", cooldown_seconds=AI_FAILOVER_COOLDOWN, error=error[:100])


def reset_ai_state():
    _ai_mode_state["failed_modes"].clear()
    log("INFO", "AI 模式状态已重置")


# ============================================
# DynamoDB 权限检查和 GSI 查询
# ============================================

def check_dynamodb_permissions():
    global _gsi_permission_granted
    try:
        table.table_status
        log("INFO", "DynamoDB 表权限检查通过")
        if ENABLE_GSI_QUERY:
            try:
                table.query(IndexName="GSI1", KeyConditionExpression=Key("GSI1PK").eq("PERMISSION_CHECK"), Limit=1)
                _gsi_permission_granted = True
                log("INFO", "DynamoDB GSI 查询权限检查通过")
            except Exception as e:
                if "AccessDeniedException" in str(e):
                    _gsi_permission_granted = False
                    log("WARN", "DynamoDB GSI 查询权限不足，将使用备用查询方案")
    except Exception as e:
        log("ERROR", "DynamoDB 权限检查失败", error=str(e)[:200])


def get_latest_model_date(brand):
    """获取指定品牌的最新型号日期（带备用方案）"""
    global _gsi_permission_granted
    brand_key = key_part(brand)
    
    if ENABLE_GSI_QUERY and _gsi_permission_granted:
        for attempt in range(GSI_QUERY_MAX_RETRIES):
            try:
                response = table.query(
                    IndexName="GSI1",
                    KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
                    ScanIndexForward=False, Limit=1
                )
                items = response.get("Items", [])
                if items:
                    return items[0].get("release_date", "")
                return None
            except Exception as e:
                error_str = str(e)
                if "AccessDeniedException" in error_str:
                    _gsi_permission_granted = False
                    break
                if attempt < GSI_QUERY_MAX_RETRIES - 1:
                    time.sleep((2 ** attempt) * 0.5)
                    continue
                break
    
    # Scan 备用方案
    try:
        response = table.scan(
            FilterExpression="brand = :brand AND attribute_exists(release_date)",
            ExpressionAttributeValues={":brand": brand},
            ProjectionExpression="release_date",
            Limit=500
        )
        items = response.get("Items", [])
        valid_dates = [item["release_date"] for item in items if item.get("release_date") and re.match(r"^\d{4}-\d{2}-\d{2}", item["release_date"])]
        return max(valid_dates) if valid_dates else None
    except Exception as e:
        log("WARN", "Scan 备用查询失败", brand=brand, error=str(e)[:200])
        return None


# ============================================
# 详细追踪器类
# ============================================

class DiscoveryTracker:
    """发现任务追踪器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.phase_stack = []
        self.current_phase = None
        self.phase_start_time = None
        
        self.token_details = {
            "categories": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "brands": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "models": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "total": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0}
        }
        
        self.timing_details = {"phases": {}, "api_calls": [], "db_operations": []}
        
        # 价格过滤统计
        self.price_filter_stats = {
            "total_checked": 0,
            "skipped_low_price": 0,
            "skipped_missing_price": 0,
            "passed": 0
        }
        
        # 品类适合度统计（新增）
        self.auction_suitability_stats = {
            "total_checked": 0,
            "allowed": 0,
            "blocked": 0,
            "review_required": 0,
            "by_reason": {},
            "by_risk_level": {"LOW": 0, "MEDIUM": 0, "COUNTERFEIT_REVIEW": 0, "HIGH": 0},
        }
    
    def start_phase(self, phase_name, **metadata):
        if self.current_phase: self.end_phase()
        self.current_phase = phase_name
        self.phase_start_time = time.time()
        self.phase_stack.append(phase_name)
        log("INFO", f"开始阶段: {phase_name}", phase=phase_name, **metadata)
    
    def end_phase(self):
        if not self.current_phase or not self.phase_start_time: return
        elapsed = time.time() - self.phase_start_time
        if self.current_phase not in self.timing_details["phases"]:
            self.timing_details["phases"][self.current_phase] = {"calls": 0, "total_seconds": 0, "min_seconds": float('inf'), "max_seconds": 0}
        phase_stats = self.timing_details["phases"][self.current_phase]
        phase_stats["calls"] += 1
        phase_stats["total_seconds"] += elapsed
        phase_stats["min_seconds"] = min(phase_stats["min_seconds"], elapsed)
        phase_stats["max_seconds"] = max(phase_stats["max_seconds"], elapsed)
        log("INFO", f"阶段完成: {self.current_phase}", duration_seconds=round(elapsed, 2))
        self.current_phase = None
        self.phase_start_time = None
    
    def record_api_call(self, task_type, tokens_used, item_count, success=True, error=None):
        if task_type not in self.token_details: task_type = "total"
        self.token_details[task_type]["api_calls"] += 1
        self.token_details[task_type]["tokens"] += tokens_used
        self.token_details[task_type]["items"] += item_count
        if not success: self.token_details[task_type]["errors"] += 1
        self.token_details["total"]["api_calls"] += 1
        self.token_details["total"]["tokens"] += tokens_used
        self.token_details["total"]["items"] += item_count
        if not success: self.token_details["total"]["errors"] += 1
    
    def record_db_operation(self, operation_type, item_count, success=True):
        self.timing_details["db_operations"].append({
            "timestamp": time.time(), "operation_type": operation_type, "item_count": item_count, "success": success
        })
    
    def record_price_filter(self, skipped: bool, reason: str):
        """记录价格过滤结果"""
        self.price_filter_stats["total_checked"] += 1
        if skipped:
            if "MISSING" in reason:
                self.price_filter_stats["skipped_missing_price"] += 1
            else:
                self.price_filter_stats["skipped_low_price"] += 1
        else:
            self.price_filter_stats["passed"] += 1
    
    def record_auction_suitability(self, result: dict):
        """记录拍卖适合度检查结果（新增）"""
        self.auction_suitability_stats["total_checked"] += 1
        reason = result.get("reason", "UNKNOWN")
        risk_level = result.get("risk_level", "UNKNOWN")
        
        if result.get("allowed"):
            self.auction_suitability_stats["allowed"] += 1
        else:
            self.auction_suitability_stats["blocked"] += 1
        
        if risk_level == "COUNTERFEIT_REVIEW":
            self.auction_suitability_stats["review_required"] += 1
        
        self.auction_suitability_stats["by_reason"][reason] = \
            self.auction_suitability_stats["by_reason"].get(reason, 0) + 1
        self.auction_suitability_stats["by_risk_level"][risk_level] = \
            self.auction_suitability_stats["by_risk_level"].get(risk_level, 0) + 1
    
    def get_summary(self):
        total_elapsed = time.time() - self.start_time
        if self.current_phase: self.end_phase()
        return {
            "total_elapsed_seconds": round(total_elapsed, 2),
            "total_api_calls": self.token_details["total"]["api_calls"],
            "total_tokens_used": self.token_details["total"]["tokens"],
            "total_items_discovered": self.token_details["total"]["items"],
            "total_errors": self.token_details["total"]["errors"],
            "ai_mode_used": _ai_mode_state.get("current_mode", AI_MODE),
            "gsi_query_enabled": ENABLE_GSI_QUERY and _gsi_permission_granted,
            "price_filter": self.price_filter_stats,
            "min_official_price_jpy": MIN_OFFICIAL_PRICE_JPY,
            "auction_suitability": self.auction_suitability_stats,  # 新增
            "auction_analysis_min_score": AUCTION_ANALYSIS_MIN_SCORE,  # 新增
        }


# ============================================

_tracker = None

def log(level, message, **fields):
    entry = {"level": level, "message": message, "total_tokens": _total_tokens_used,
             "elapsed_seconds": get_elapsed_seconds(), **fields}
    print(json.dumps(entry, ensure_ascii=False, default=str))


def get_elapsed_seconds():
    return 0 if _lambda_start_time is None else time.time() - _lambda_start_time


def get_remaining_seconds():
    return max(0, LAMBDA_TIMEOUT_SECONDS - get_elapsed_seconds() - LAMBDA_TIMEOUT_BUFFER)


def check_timeout():
    if get_remaining_seconds() <= 0:
        raise RuntimeError(f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒")


def check_token_limit():
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}")


def check_limits():
    check_token_limit()
    check_timeout()


def normalize(value):
    value = str(value or "").strip()
    value = value.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ))
    return re.sub(r"\s+", " ", value)


def key_part(value):
    value = normalize(value).upper()
    value = re.sub(r"[^A-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+", "-", value)
    return value.strip("-")[:180]


def stable_id(*values):
    raw = "|".join(normalize(value).casefold() for value in values)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def clean_json_content(content):
    if isinstance(content, dict): return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") in ("input_text", "text"):
                text_parts.append(str(part.get("text", "")))
        content = "".join(text_parts)
    text = str(content or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match: text = json_match.group(0)
    return json.loads(text)


def update_token_usage(usage):
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        log("INFO", "Token用量更新", added_tokens=total, total_tokens=_total_tokens_used)


def build_prompt(task):
    task_type = task.get("task_type")
    max_items = int(task.get("max_items", 20))
    search_date = task.get("search_date", "")
    min_price = task.get("min_official_price_jpy", MIN_OFFICIAL_PRICE_JPY)

    if task_type == "DISCOVER_CATEGORIES":
        instruction = (
            "中古市場で価値が落ちにくく、小型または中型で配送しやすく、"
            "偽物のリスクが比較的低い、または偽物の製造難易度が高い商品カテゴリをリストアップしてください。"
            "電子製品に限定しないでください。"
            "ブランド名・型番・モデル名で価格比較しやすいカテゴリを優先してください。"
            "食品、飲料、消耗品、大型家具、日用品、低単価商品、偽物が非常に多いカテゴリは含めないでください。"
            "例：スマートフォン、カメラ、レンズ、ゲーム機、スマートウォッチ、"
            "測定器、万年筆、フィギュア、模型、オーディオ機器。"
        )
    elif task_type == "DISCOVER_BRANDS":
        category = normalize(task.get("category"))
        instruction = (
            f"商品カテゴリ「{category}」の実際のブランドをリストアップしてください。"
            "中古市場で価値が落ちにくく、偽物リスクが低いブランドを優先してください。"
            "高級ブランドでも偽物が多いものは含めないでください。"
        )
    elif task_type == "DISCOVER_MODELS":
        category = normalize(task.get("category"))
        brand = normalize(task.get("brand"))
        date_condition = ""
        if search_date:
            date_condition = f"{search_date}以降に発売された製品のみを含めてください。発売日の降順でリストしてください。"
        price_condition = f"公式販売価格が{min_price}円以上の製品のみを含めてください。" if min_price > 0 else ""
        instruction = (
            f"ブランド「{brand}」のカテゴリ「{category}」において、"
            "中古市場で価値が落ちにくく、小型または中型で配送しやすく、"
            "偽物リスクが低い、または偽物の製造難易度が高い具体的な商品モデルのみをリストアップしてください。"
            f"{date_condition}{price_condition}"
            "食品、飲料、消耗品、大型家具、日用品、低単価商品、偽物が非常に多い商品は絶対に含めないでください。"
            "各エントリにはcategory、brand、model、confidence、release_date、official_price_jpyフィールドを含めてください。"
        )
    else:
        raise ValueError(f"Unknown task_type: {task_type}")

    return f"""
    {instruction}

    「items」配列を含むJSONオブジェクトのみを返してください。最大{max_items}エントリ。
    各エントリには以下のフィールドを含めてください：
    - category: 文字列
    - brand: 文字列または空
    - model: 文字列または空
    - confidence: 0-1の数値またはnull
    - release_date: YYYY-MM-DD形式の文字列または空
    - official_price_jpy: 公式販売価格（日本円、税込）数値またはnull

    ルール：
    - JSONのみを返し、マークダウンや説明は不要
    - あなたの知識ベースのみを使用する
    - 不確かな場合はconfidenceを下げる
    """


# ============================================
# 多 API 调用函数
# ============================================

def call_api(task):
    global _tracker
    check_limits()
    
    max_mode_switches = 3
    last_error = None
    
    for mode_attempt in range(max_mode_switches):
        try:
            config = get_available_ai_config()
        except RuntimeError as e:
            raise RuntimeError(f"所有 AI 模式不可用: {e}") from e
        
        mode_name = config["name"]
        _ai_mode_state["current_mode"] = mode_name
        
        for attempt in range(MAX_RETRIES):
            try:
                api_start_time = time.time()
                if config["type"] == "gemini":
                    items, tokens_used = call_gemini_api(config, task)
                else:
                    items, tokens_used = call_openai_compatible_api(config, task)
                
                api_elapsed = time.time() - api_start_time
                log("INFO", "API请求完成", mode=mode_name, model=config["model"],
                    item_count=len(items), tokens_used=tokens_used, api_duration_seconds=round(api_elapsed, 2))
                
                task_type_key = task.get("task_type", "").split('_')[1].lower()
                if _tracker: _tracker.record_api_call(task_type_key, tokens_used, len(items), success=True)
                
                return items
                
            except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError) as e:
                last_error = f"网络错误: {e}"
                log("ERROR", f"[{mode_name}] 网络错误 (尝试{attempt+1}/{MAX_RETRIES})", error=str(e))
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                log("ERROR", f"[{mode_name}] API调用失败 (尝试{attempt+1}/{MAX_RETRIES})", error=str(e))
            
            if attempt < MAX_RETRIES - 1:
                time.sleep((2 ** attempt) + random.random())
        
        mark_ai_mode_failed(mode_name, str(last_error))
    
    raise RuntimeError(f"所有 AI 模式均调用失败: {last_error}")


def call_gemini_api(config: dict, task: dict) -> tuple:
    prompt = build_prompt(task)
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": TEMPERATURE, "maxOutputTokens": config["max_tokens"], "topP": TOP_P}}
    
    request = urllib.request.Request(config["url"], data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"x-goog-api-key": config["key"], "Content-Type": "application/json"}, method="POST")
    
    with urllib.request.urlopen(request, timeout=config["timeout"]) as response:
        result = json.loads(response.read().decode("utf-8"))
        tokens_used = 0
        usage = result.get("usageMetadata", {})
        if usage: tokens_used = usage.get("promptTokenCount", 0) + usage.get("candidatesTokenCount", 0); update_token_usage({"total_tokens": tokens_used})
        record_token_usage(config["name"], config["model"], usage,
                           prompt=prompt, task_type=task.get("task_type", ""))
        
        content = ""
        if "candidates" in result and result["candidates"]:
            if result["candidates"][0].get("finishReason") == "SAFETY": raise RuntimeError("Gemini 安全过滤触发")
            if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                content = "".join(p.get("text", "") for p in result["candidates"][0]["content"]["parts"])
        
        parsed = clean_json_content(content)
        return parsed.get("items", []) or [], tokens_used


def call_openai_compatible_api(config: dict, task: dict) -> tuple:
    prompt = build_prompt(task)
    body = {"model": config["model"], "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], "temperature": TEMPERATURE, "max_tokens": config["max_tokens"], "top_p": TOP_P}
    if config["name"] == "doubao": body["response_format"] = {"type": "json_object"}
    
    request = urllib.request.Request(config["url"], data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"Authorization": f"Bearer {config['key']}", "Content-Type": "application/json"}, method="POST")
    
    with urllib.request.urlopen(request, timeout=config["timeout"]) as response:
        result = json.loads(response.read().decode("utf-8"))
        usage = result.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)
        update_token_usage(usage)
        record_token_usage(config["name"], config["model"], usage,
                           prompt=prompt, task_type=task.get("task_type", ""))
        
        content = ""
        if "choices" in result and result["choices"]:
            content = result["choices"][0].get("message", {}).get("content", "")
        else:
            content = result.get("content") or result.get("text") or json.dumps(result)
        
        parsed = clean_json_content(content)
        items = parsed.get("items", [])
        if not isinstance(items, list):
            for v in parsed.values():
                if isinstance(v, list): items = v; break
        return items if isinstance(items, list) else [], tokens_used


# ============================================
# 数据库操作
# ============================================

def upsert_category(category, category_id=""):
    global _tracker
    category = normalize(category)
    if not category: return
    try:
        now = int(time.time())
        table.update_item(
            Key={"PK": f"CATEGORY#{key_part(category)}", "SK": "META"},
            UpdateExpression="SET entity_type = :type, #name = :name, category_id = :category_id, #status = :status, first_seen_at = if_not_exists(first_seen_at, :now), last_seen_at = :now, modified_index_pk = :all, modified_at = :modified_at, #source = :source",
            ExpressionAttributeNames={"#name": "name", "#status": "status", "#source": "source"},
            ExpressionAttributeValues={":type": "CATEGORY", ":name": category, ":category_id": str(category_id or ""), ":status": "ACTIVE", ":now": now, ":all": "ALL", ":modified_at": datetime.now(timezone.utc).isoformat(), ":source": "YAHOO_DIRECTORY"}
        )
        if _tracker: _tracker.record_db_operation("upsert_category", 1)
    except Exception as e:
        if _tracker: _tracker.record_db_operation("upsert_category", 0, success=False)
        raise


def upsert_brand(category, brand, category_id=""):
    global _tracker
    category, brand = normalize(category), normalize(brand)
    if not category or not brand: return
    try:
        now = int(time.time())
        table.update_item(
            Key={"PK": f"CATEGORY#{key_part(category)}", "SK": f"BRAND#{key_part(brand)}"},
            UpdateExpression="SET entity_type = :type, category = :category, category_id = :category_id, brand = :brand, #status = :status, first_seen_at = if_not_exists(first_seen_at, :now), last_seen_at = :now, modified_index_pk = :all, modified_at = :modified_at, #source = :source",
            ExpressionAttributeNames={"#status": "status", "#source": "source"},
            ExpressionAttributeValues={":type": "BRAND", ":category": category, ":category_id": str(category_id or ""), ":brand": brand, ":status": "ACTIVE", ":now": now, ":all": "ALL", ":modified_at": datetime.now(timezone.utc).isoformat(), ":source": DATA_SOURCE}
        )
        if _tracker: _tracker.record_db_operation("upsert_brand", 1)
    except Exception as e:
        if _tracker: _tracker.record_db_operation("upsert_brand", 0, success=False)
        raise


def upsert_product(category, brand, model, confidence=None, release_date=None, official_price_jpy=None, category_id=""):
    """
    保存产品型号到 DynamoDB。
    包含：官方售价过滤 + 拍卖适合度检查
    """
    global _tracker
    category, brand, model = normalize(category), normalize(brand), normalize(model)
    if not category or not brand or not model: return
    
    # ============ 拍卖适合度检查（新增） ============
    official_price = safe_int_price(official_price_jpy, 0)
    
    auction_check = is_good_for_auction_analysis(
        category=category,
        brand=brand,
        model=model,
        official_price_jpy=official_price
    )
    
    if _tracker:
        _tracker.record_auction_suitability(auction_check)
    
    if not auction_check["allowed"]:
        log("INFO", "商品不适合 Auction 分析，跳过保存",
            category=category, brand=brand, model=model,
            official_price_jpy=official_price,
            reason=auction_check["reason"],
            score=auction_check["score"],
            risk_level=auction_check["risk_level"])
        return
    # ==========================================
    
    try:
        now = int(time.time())
        product_id = stable_id(category, brand, model)
        product_pk = f"PRODUCT#{product_id}"

        expression = (
            "SET entity_type = :type, category = :category, category_id = :category_id, brand = :brand, "
            "model = :model, normalized_model = :normalized_model, "
            "#status = :status, verification_status = if_not_exists(verification_status, :unverified), "
            "first_seen_at = if_not_exists(first_seen_at, :now), last_seen_at = :now, "
            "modified_index_pk = :all, modified_at = :modified_at, #source = :source"
        )
        values = {
            ":type": "PRODUCT", ":category": category, ":category_id": str(category_id or ""), ":brand": brand,
            ":model": model, ":normalized_model": normalize(model).casefold(),
            ":status": "ACTIVE", ":unverified": "UNVERIFIED", ":now": now,
            ":all": "ALL", ":modified_at": datetime.now(timezone.utc).isoformat(), ":source": DATA_SOURCE
        }
        
        if confidence is not None:
            try:
                values[":confidence"] = str(max(0.0, min(1.0, float(confidence))))
                expression += ", confidence = :confidence"
            except (TypeError, ValueError): pass
        
        if release_date:
            release_date = normalize(release_date)
            if re.match(r"^\d{4}-\d{2}-\d{2}", release_date):
                expression += ", release_date = :release_date"
                values[":release_date"] = release_date
        
        # 保存官方售价
        if official_price > 0:
            expression += ", official_price_jpy = :official_price_jpy"
            values[":official_price_jpy"] = official_price
        
        # 保存拍卖适合度信息（新增）
        expression += (
            ", auction_analysis_score = :auction_score"
            ", auction_analysis_risk_level = :auction_risk"
            ", catalog_scan_disabled = :catalog_scan_disabled"
            ", catalog_scan_disabled_reason = :catalog_disabled_reason"
        )
        values[":auction_score"] = auction_check["score"]
        values[":auction_risk"] = auction_check["risk_level"]
        values[":catalog_scan_disabled"] = auction_check["catalog_scan_disabled"]
        values[":catalog_disabled_reason"] = auction_check.get("catalog_scan_disabled_reason", "")

        table.update_item(
            Key={"PK": product_pk, "SK": "META"},
            UpdateExpression=expression,
            ExpressionAttributeNames={"#status": "status", "#source": "source"},
            ExpressionAttributeValues=values
        )

        gsi1_item = {
            "PK": f"BRAND#{key_part(brand)}",
            "SK": f"MODEL#{key_part(model)}",
            "GSI1PK": f"BRAND#{key_part(brand)}",
            "GSI1SK": release_date if release_date else "0000-00-00",
            "entity_type": "BRAND_MODEL",
            "category": category, "category_id": str(category_id or ""), "brand": brand, "model": model,
            "product_pk": product_pk, "last_seen_at": now,
            "modified_index_pk": "ALL",
            "modified_at": datetime.now(timezone.utc).isoformat(),
            "auction_analysis_score": auction_check["score"],
            "auction_analysis_risk_level": auction_check["risk_level"],
            "catalog_scan_disabled": auction_check["catalog_scan_disabled"],
        }
        if release_date: gsi1_item["release_date"] = release_date
        if official_price: gsi1_item["official_price_jpy"] = official_price
        table.put_item(Item=gsi1_item)
        
        log("INFO", "产品保存成功",
            category=category, brand=brand, model=model,
            auction_score=auction_check["score"],
            risk_level=auction_check["risk_level"],
            catalog_scan_disabled=auction_check["catalog_scan_disabled"])
        
        if _tracker: _tracker.record_db_operation("upsert_product", 1)
    except Exception as e:
        if _tracker: _tracker.record_db_operation("upsert_product", 0, success=False)
        raise


# ============================================
# 主处理逻辑
# ============================================

def get_crawled_categories(limit=MAX_CATEGORIES):
    """读取目录爬虫产生的真实 Yahoo 品类，不再让 AI 猜测品类。"""
    if not LINK_CRAWLER_TABLE_NAME:
        raise RuntimeError("缺少 LINK_CRAWLER_TABLE_NAME，无法读取爬取品类")
    crawler_table = dynamodb.Table(LINK_CRAWLER_TABLE_NAME)
    categories = []
    seen_ids = set()
    scan_kwargs = {
        "FilterExpression": (
            "attribute_exists(category_id) AND category_id <> :empty "
            "AND is_terminal = :true AND child_count = :zero"
        ),
        "ExpressionAttributeValues": {":empty": "", ":true": True, ":zero": 0},
        "ProjectionExpression": (
            "category_id, category_name, anchor_text, #url, "
            "is_terminal, child_count"
        ),
        "ExpressionAttributeNames": {"#url": "url"},
    }
    while len(categories) < limit:
        response = crawler_table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            category_id = normalize(item.get("category_id"))
            category = normalize(item.get("category_name") or item.get("anchor_text"))
            if category_id and category and category_id not in seen_ids:
                seen_ids.add(category_id)
                categories.append({"category": category, "category_id": category_id})
                if len(categories) >= limit:
                    break
        last_key = response.get("LastEvaluatedKey")
        if not last_key or len(categories) >= limit:
            break
        scan_kwargs["ExclusiveStartKey"] = last_key
    return categories

def process_discovery(event):
    global _total_tokens_used, _lambda_start_time, _tracker
    
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    reset_ai_state()
    
    check_dynamodb_permissions()
    
    _tracker = DiscoveryTracker()
    _tracker.start_phase("discovery_start", 
                         ai_mode=AI_MODE, 
                         gsi_enabled=ENABLE_GSI_QUERY and _gsi_permission_granted,
                         min_official_price=MIN_OFFICIAL_PRICE_JPY,
                         auction_analysis_min_score=AUCTION_ANALYSIS_MIN_SCORE)
    
    task_type = event.get("task_type", "DISCOVER_CATEGORIES")
    
    log("INFO", "开始发现处理", task_type=task_type, ai_mode=AI_MODE,
        min_official_price=MIN_OFFICIAL_PRICE_JPY,
        auction_analysis_min_score=AUCTION_ANALYSIS_MIN_SCORE,
        gsi_enabled=ENABLE_GSI_QUERY and _gsi_permission_granted)
    
    try:
        if task_type == "DISCOVER_CATEGORIES":
            target_categories = event.get("target_categories", None)
            
            if target_categories:
                crawled_leaves = get_crawled_categories(MAX_CATEGORIES)
                leaves_by_id = {item["category_id"]: item for item in crawled_leaves}
                leaves_by_name = {item["category"]: item for item in crawled_leaves}
                categories = []
                for item in target_categories:
                    if isinstance(item, dict):
                        category = normalize(item.get("category"))
                        category_id = normalize(item.get("category_id"))
                    else:
                        category, category_id = normalize(item), ""
                    leaf = leaves_by_id.get(category_id) or leaves_by_name.get(category)
                    if leaf:
                        upsert_category(leaf["category"], leaf["category_id"])
                        categories.append(leaf)
                    else:
                        log("WARNING", "跳过非叶子目录", category=category, category_id=category_id)
                log("INFO", "使用指定的叶子品类", categories=categories)
            else:
                categories = get_crawled_categories(MAX_CATEGORIES)
                for item in categories:
                    upsert_category(item["category"], item["category_id"])
                log("INFO", "已加载爬取品类", count=len(categories))
            
            category_count = 0
            for category_item in categories[:CATEGORY_LIMIT]:
                category = category_item["category"]
                category_id = category_item["category_id"]
                if _total_tokens_used >= MAX_TOTAL_TOKENS or get_remaining_seconds() < 60:
                    log("WARN", "停止: Token或时间不足")
                    break
                
                _tracker.start_phase(f"discover_brands_{category}")
                time.sleep(API_CALL_DELAY)
                
                brand_task = {"task_type": "DISCOVER_BRANDS", "category": category, "category_id": category_id, "max_items": MAX_BRANDS}
                brand_items = call_api(brand_task)
                
                brands = []
                for item in brand_items:
                    if isinstance(item, dict) and "brand" in item:
                        brand = normalize(item["brand"])
                        if brand and category: upsert_brand(category, brand, category_id); brands.append((category, category_id, brand))
                
                _tracker.end_phase()
                
                brand_count = 0
                for cat, cat_id, brand in brands[:BRAND_LIMIT]:
                    if _total_tokens_used >= MAX_TOTAL_TOKENS or get_remaining_seconds() < 60: break
                    
                    _tracker.start_phase(f"discover_models_{brand}")
                    time.sleep(API_CALL_DELAY)
                    
                    latest_date = get_latest_model_date(brand)
                    model_task = {
                        "task_type": "DISCOVER_MODELS", "category": cat, "category_id": cat_id, "brand": brand,
                        "max_items": MAX_MODELS, "search_date": latest_date,
                        "min_official_price_jpy": MIN_OFFICIAL_PRICE_JPY
                    }
                    model_items = call_api(model_task)
                    
                    for item in model_items:
                        if isinstance(item, dict) and "model" in item:
                            upsert_product(cat, brand, item.get("model"),
                                           item.get("confidence"), item.get("release_date"),
                                           item.get("official_price_jpy"), cat_id)
                    
                    _tracker.end_phase()
                    brand_count += 1
                
                category_count += 1
            
            summary = _tracker.get_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "发现处理完成",
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "gsi_query_available": ENABLE_GSI_QUERY and _gsi_permission_granted,
                    "summary": summary
                }, ensure_ascii=False)
            }
        
        elif task_type == "DISCOVER_MODELS":
            category = event.get("category", "")
            category_id = event.get("category_id", "")
            brand = event.get("brand", "")
            if not category or not brand:
                return {"statusCode": 400, "body": json.dumps({"error": "需要提供 category 和 brand 参数"}, ensure_ascii=False)}
            
            _tracker.start_phase(f"discover_models_{brand}")
            latest_date = get_latest_model_date(brand)
            task = {"task_type": "DISCOVER_MODELS", "category": category, "category_id": category_id, "brand": brand,
                    "max_items": MAX_MODELS, "search_date": latest_date,
                    "min_official_price_jpy": MIN_OFFICIAL_PRICE_JPY}
            items = call_api(task)
            
            for item in items:
                if isinstance(item, dict) and "model" in item:
                    upsert_product(category, brand, item.get("model"),
                                   item.get("confidence"), item.get("release_date"),
                                   item.get("official_price_jpy"), category_id)
            
            _tracker.end_phase()
            summary = _tracker.get_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "型号发现完成",
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "gsi_query_available": ENABLE_GSI_QUERY and _gsi_permission_granted,
                    "summary": summary
                }, ensure_ascii=False)
            }
        
        else:
            return {"statusCode": 400, "body": json.dumps({"error": f"未知的 task_type: {task_type}"}, ensure_ascii=False)}
    
    except RuntimeError as e:
        error_msg = str(e)
        if any(kw in error_msg for kw in ["Token用量已达上限", "Lambda超时倒计时", "剩余时间不足"]):
            if _tracker:
                _tracker.end_phase()
                summary = _tracker.get_summary()
            log("WARN", "任务中断", reason=error_msg)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "任务已安全中断", "reason": error_msg,
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "gsi_query_available": ENABLE_GSI_QUERY and _gsi_permission_granted,
                    "summary": summary if _tracker else None
                }, ensure_ascii=False)
            }
        raise
    except Exception as e:
        if _tracker: _tracker.end_phase()
        log("ERROR", "处理异常", error_type=type(e).__name__, error=str(e))
        raise


def lambda_handler(event, context):
    global _lambda_start_time, _tracker
    _lambda_start_time = time.time()
    _tracker = None
    
    try:
        log("INFO", "Lambda执行开始", 
            ai_mode=AI_MODE, 
            min_official_price=MIN_OFFICIAL_PRICE_JPY,
            auction_analysis_min_score=AUCTION_ANALYSIS_MIN_SCORE)
        return process_discovery(event)
    except Exception as error:
        log("ERROR", "处理失败", error_type=type(error).__name__, error=str(error))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "内部错误",
                "details": str(error),
                "total_tokens_used": _total_tokens_used,
                "elapsed_seconds": get_elapsed_seconds()
            }, ensure_ascii=False)
        }
