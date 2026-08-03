"""
Yahoo Auction 商品分析工作流 Lambda
三层决策流：程序估价 → AI重解析 → 人工审核
开放参数限制 + 多级降级匹配
title + detailDescription 详细AI解析

核心修复：
1. HTTP错误响应内容记录
2. API URL默认值设置
3. 按简单/详细解析分别限制 AI 输出长度
4. scrape_closed/scrape_active 新商品自动初始化 modelStatus=PENDING
5. upsert_scraped_item 使用 if_not_exists 不覆盖已有状态
6. update_record 修复 ExpressionAttributeNames 问题
7. 增强日志输出
"""

import os, re, json, time, random, logging, unicodedata, urllib.request, urllib.error, socket
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Any, Set, Tuple, Union
from collections import OrderedDict

import boto3
from token_usage import record_token_usage
from yahoo_auction_scraper import scrape_auctions, scrape_item_detail

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ======================================
# Constants
# ======================================

class Status:
    PENDING = "PENDING"; COMPLETED = "COMPLETED"; FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"; EXCLUDED = "EXCLUDED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"; NOT_APPLICABLE = "NOT_APPLICABLE"
    RUNNING = "RUNNING"; NOT_RUN = "NOT_RUN"

class ListingType:
    MAIN_PRODUCT = "MAIN_PRODUCT"; ACCESSORY = "ACCESSORY"; PARTS = "PARTS"
    BROKEN = "BROKEN"; BOX_ONLY = "BOX_ONLY"; BUNDLE = "BUNDLE"
    RENTAL = "RENTAL"; UNKNOWN = "UNKNOWN"

class ConditionClass:
    NORMAL = "NORMAL"
    JUNK = "JUNK"

# 故障主机是可比商品；只有下列非单一主商品类型会被程序排除。
EXCLUDED_TYPES = {
    ListingType.ACCESSORY, ListingType.PARTS, ListingType.BOX_ONLY,
    ListingType.BUNDLE, ListingType.RENTAL,
}
ALLOWED_LISTING_TYPES = {
    ListingType.MAIN_PRODUCT, ListingType.ACCESSORY, ListingType.PARTS,
    ListingType.BOX_ONLY, ListingType.RENTAL, ListingType.BUNDLE,
    ListingType.UNKNOWN,
}

class Recommendation:
    BUY_CANDIDATE = "BUY_CANDIDATE"
    REVIEW = "REVIEW"
    AVOID = "AVOID"

NON_CRITICAL_FIELDS = {"variant", "color", "carrier", "screen_size", "battery", "graphics_card", "os", "processor", "cpu", "compatibility", "ram", "memory"}
CRITICAL_PARAM_PENALTIES = {"brand": Decimal("0.20"), "model": Decimal("0.30"), "storage": Decimal("0.10"), "other": Decimal("0.05")}
MODEL_FAMILY_SUFFIXES = [" RECON", " RECON LT", " BY", " CS MID", " CS", " MID", " LOW", " HIGH", " PRIMEKNIT", " PRIME KNIT", " PRIME", " PK", " PRO MAX", " PRO", " MAX", " PLUS", " ULTRA", " LITE", " FE", " ELITE", " ELITEBOOK", " PROBOOK", " GEN10", " GEN9", " GEN8", " G10", " G9", " G8", " LIMITED EDITION", " LIMITED", " LE", " SE", " SPECIAL EDITION", " ANNIVERSARY", " OG", " 2023", " 2024", " 2025"]

# ======================================
# Config
# ======================================

def _env(key, default, cast=str):
    v = os.getenv(key, "")
    return cast(v) if v else default

TABLE_ACTIVE = _env("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_CLOSED = _env("TABLE_NAME_CLOSED", "YahooAuctionItems")
PRODUCT_TABLE_NAME = os.environ.get("TABLE_NAME", "ProductCatalog-dev")
BUY_CANDIDATE_TABLE = os.environ.get(
    "BUY_CANDIDATE_TABLE", "YahooAuctionBuyCandidates-dev"
)
FINAL_CHECK_BEFORE_MINUTES = _env("FINAL_CHECK_BEFORE_MINUTES", 15, int)
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
AI_MODE = _env("AI_MODE", "doubao")

_gemini_model = _env("GEMINI_MODEL", "gemini-2.0-flash")
_gemini_url = _env(
    "GEMINI_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
)
if _gemini_model == "gemini-2.0-flash-latest":
    logger.warning("Unsupported Gemini alias configured; using gemini-2.0-flash instead")
    _gemini_model = "gemini-2.0-flash"
    _gemini_url = _gemini_url.replace("gemini-2.0-flash-latest", "gemini-2.0-flash")

AI_CONFIGS = {
    "gemini": {
        "name": "gemini",
        "type": "gemini",
        "url": _gemini_url,
        "model": _gemini_model,
        "timeout": _env("GEMINI_TIMEOUT", 60, int),
        "max_tokens": _env("GEMINI_MAX_TOKENS", 12000, int),
        # ★ 不再从环境变量读 key
    },
    "doubao": {
        "name": "doubao",
        "type": "openai",
        "url": _env("DOUBAO_URL", "https://ws-8lxmxlbemcgcus5u.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions"),
        "model": _env("DOUBAO_MODEL", "qwen-plus-character"),
        "timeout": max(300, _env("DOUBAO_TIMEOUT", 300, int)),
        "max_tokens": _env("DOUBAO_MAX_TOKENS", 12000, int),
    },
    "openai": {
        "name": "openai",
        "type": "openai",
        "url": _env("OPENAI_URL", "https://api.openai.com/v1/chat/completions"),
        "model": _env("OPENAI_MODEL", "gpt-4o-mini"),
        "timeout": _env("OPENAI_TIMEOUT", 60, int),
        "max_tokens": _env("OPENAI_MAX_TOKENS", 12000, int),
    },
}

logger.info(
    "AI runtime config: doubao_timeout=%s gemini_model=%s gemini_timeout=%s openai_timeout=%s",
    AI_CONFIGS["doubao"]["timeout"],
    AI_CONFIGS["gemini"]["model"],
    AI_CONFIGS["gemini"]["timeout"],
    AI_CONFIGS["openai"]["timeout"],
)

BUY_MARGIN = _env("BUY_MARGIN_THRESHOLD", Decimal("0.20"), Decimal)
REVIEW_MARGIN = _env("REVIEW_MARGIN_THRESHOLD", Decimal("0.10"), Decimal)
MIN_COMPARABLE = _env("MIN_COMPARABLE_COUNT", 3, int)
HIGH_CONF = _env("HIGH_CONFIDENCE_COUNT", 10, int)
MED_CONF = _env("MEDIUM_CONFIDENCE_COUNT", 5, int)
ACTIVE_MAX_RATIO = _env("ACTIVE_MAX_RATIO", Decimal("1.0"), Decimal)
MIN_ROI = _env("MIN_ROI", Decimal("0.15"), Decimal)
FEE_RATE = _env("FEE_RATE", Decimal("0.10"), Decimal)
SHIPPING_COST = _env("SHIPPING_COST", Decimal("1500"), Decimal)
REPAIR_RESERVE = _env("REPAIR_RESERVE", Decimal("0.05"), Decimal)
RISK_RESERVE = _env("RISK_RESERVE", Decimal("0.03"), Decimal)
MAX_PRICE_DEV = _env("MAX_PRICE_DEV", Decimal("1.5"), Decimal)
SIMPLE_BATCH = _env("SIMPLE_BATCH", _env("MODEL_BATCH", 25, int), int)
DETAIL_BATCH = _env("DETAIL_BATCH", 10, int)
AI_TIMEOUT = _env("AI_TIMEOUT", 90, int)
AI_RETRIES = _env("AI_RETRIES", 3, int)
MAX_TOKENS = _env("MAX_TOKENS", 250000, int)
SIMPLE_MAX_TOKENS = _env("SIMPLE_MAX_TOKENS", 4000, int)
DETAIL_MAX_TOKENS = _env("DETAIL_MAX_TOKENS", 12000, int)
LAMBDA_TIMEOUT = _env("LAMBDA_TIMEOUT", 840, int)
TIMEOUT_BUFFER = _env("TIMEOUT_BUFFER", 30, int)
DETAIL_DESC_MAX = _env("DETAIL_DESC_MAX", 3000, int)
ACTIVE_TITLE_MAX = _env("ACTIVE_TITLE_MAX", 120, int)
CLOSED_TITLE_MAX = _env("CLOSED_TITLE_MAX", 100, int)
ENABLE_FALLBACK = _env("FALLBACK_MATCH", True, lambda x: x.lower() in ("true","1"))
ENABLE_FAMILY = _env("FAMILY_MATCH", True, lambda x: x.lower() in ("true","1"))
LOG_AI_REQUEST_JSON = _env("LOG_AI_REQUEST_JSON", False, lambda x: x.lower() in ("true", "1"))
LOG_AI_RESPONSE_JSON = _env("LOG_AI_RESPONSE_JSON", False, lambda x: x.lower() in ("true", "1"))

# ======================================
# DynamoDB & State
# ======================================

dynamodb = boto3.resource("dynamodb")
active_db = dynamodb.Table(TABLE_ACTIVE)
closed_db = dynamodb.Table(TABLE_CLOSED)
product_catalog_db = dynamodb.Table(PRODUCT_TABLE_NAME)
buy_candidate_db = dynamodb.Table(BUY_CANDIDATE_TABLE)
secrets = boto3.client("secretsmanager")
sns = boto3.client("sns")
_total_tokens = 0
_start_time = None

# ======================================
# Repository
# ======================================

def update_record(table, item_id: str, fields: Dict):
    """更新 DynamoDB 记录（修复 ExpressionAttributeNames 问题）"""
    fields = {
        **fields,
        "modifiedIndexPk": "ALL",
        "modifiedAt": datetime.now(timezone.utc).isoformat(),
    }
    parts, values, names = [], {}, {}
    
    for k, v in fields.items():
        attr_name = k
        # 处理 DynamoDB 保留字
        if k in ("url", "ttl"):
            names[f"#{k}"] = k
            attr_name = f"#{k}"
        
        parts.append(f"{attr_name} = :{k}")
        values[f":{k}"] = _to_dynamo(v)
    
    kwargs = {
        "Key": {"itemID": str(item_id)},
        "UpdateExpression": "SET " + ", ".join(parts),
        "ExpressionAttributeValues": values,
    }
    
    if names:
        kwargs["ExpressionAttributeNames"] = names
    
    table.update_item(**kwargs)

def upsert_scraped_item(table, item_id: str, fields: Dict, force: bool = False):
    """
    保存抓取到的商品（核心修复）。
    
    逻辑：
    - 新商品：自动设置 modelStatus = PENDING, pricingStatus = PENDING
    - 已有商品：仅更新基础信息，不覆盖已解析的状态（使用 if_not_exists）
    - force=True：强制重置为 PENDING（用于重新处理）
    """
    now = datetime.now(timezone.utc).isoformat()
    parts, values, names = [], {}, {}
    
    # 基础字段
    for k, v in fields.items():
        attr_name = k
        if k in ("url", "ttl"):
            names[f"#{k}"] = k
            attr_name = f"#{k}"
        parts.append(f"{attr_name} = :{k}")
        values[f":{k}"] = _to_dynamo(v)
    
    # ★ 核心：modelStatus 和 pricingStatus 的初始化
    values[":pending"] = Status.PENDING
    values[":now"] = now
    values[":modified_index_pk"] = "ALL"
    
    if force:
        # 强制重置：覆盖已有状态
        parts.append("modelStatus = :pending")
        parts.append("pricingStatus = :pending")
    else:
        # 仅新记录设置默认值，不覆盖已有状态
        parts.append("modelStatus = if_not_exists(modelStatus, :pending)")
        parts.append("pricingStatus = if_not_exists(pricingStatus, :pending)")
    
    parts.append("lastScrapedAt = :now")
    parts.append("modifiedIndexPk = :modified_index_pk")
    parts.append("modifiedAt = :now")
    
    kwargs = {
        "Key": {"itemID": str(item_id)},
        "UpdateExpression": "SET " + ", ".join(parts),
        "ExpressionAttributeValues": values,
    }
    
    if names:
        kwargs["ExpressionAttributeNames"] = names
    
    table.update_item(**kwargs)

def get_record(table, item_id: str) -> Optional[Dict]:
    r = table.get_item(Key={"itemID": str(item_id)})
    return r.get("Item")

def _to_dynamo(v):
    if isinstance(v, float):
        return Decimal(str(v))
    if isinstance(v, Decimal):
        return v
    if isinstance(v, dict):
        return {str(k): _to_dynamo(i) for k,i in v.items()}
    if isinstance(v, (list,tuple)):
        return [_to_dynamo(i) for i in v]
    return v

# ======================================
# Helpers
# ======================================

def sd(v, d=Decimal("0")) -> Decimal:
    try:
        return v if isinstance(v,Decimal) else Decimal(str(v))
    except:
        return d

def si(v, d=0) -> int:
    try:
        return int(v)
    except:
        return d

def norm(text: str) -> str:
    if not text:
        return ""
    t = str(text).strip().translate(str.maketrans("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９","ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    return re.sub(r"\s+"," ",t)

def normalize_pricing_key(value: str) -> str:
    """生成仅含 A-Z、0-9 的通用机器匹配键。"""
    if value is None:
        return ""
    normalized_parts = []
    for character in str(value):
        normalized_character = unicodedata.normalize("NFKC", character)
        # NFKC 会把 ™ 等符号展开成 ASCII 字母；符号本身仍应作为分隔符
        # 丢弃，不能让展示标记改变产品身份。
        if unicodedata.category(character)[0] in {"P", "S", "Z"}:
            continue
        normalized_parts.append(normalized_character)
    normalized = "".join(normalized_parts).upper()
    return re.sub(r"[^A-Z0-9]", "", normalized)

def pricing_key_with_condition(value: str, condition_class: str) -> str:
    """规范化价格键，并在键尚未包含状态时补充状态。"""
    key = normalize_pricing_key(value)
    condition = normalize_pricing_key(condition_class)
    if key and condition and not key.endswith(condition):
        key += condition
    return key

def norm_storage(v) -> str:
    if not v:
        return ""
    t = norm(str(v)).upper()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(GB|G|TB|T)",t)
    if m:
        return f"{m.group(1)}{'GB' if m.group(2) in ('G','GB') else 'TB'}"
    parts = [f"{a}{'GB' if u in ('G','GB') else 'TB'}" for a,u in re.findall(r"(\d+(?:\.\d+)?)\s*(GB|TB|G|T)",t)]
    if parts:
        return " ".join(parts)
    ram = re.search(r'(?:RAM|メモリ)\s*(\d+)\s*GB',t)
    ssd = re.search(r'(?:SSD|M\.2\s*SSD)\s*(\d+)\s*GB',t)
    hdd = re.search(r'(?:HDD)\s*(\d+)\s*(?:GB|TB)',t)
    parts = []
    if ram:
        parts.append(f"RAM{ram.group(1)}GB")
    if ssd:
        parts.append(f"SSD{ssd.group(1)}GB")
    if hdd:
        parts.append(f"HDD{hdd.group(1)}{'TB' if 'TB' in t else 'GB'}")
    return " ".join(parts) if parts else t

def extract_family(model: str) -> str:
    if not model:
        return ""
    n = norm(model).upper()
    for s in MODEL_FAMILY_SUFFIXES:
        if n.endswith(s):
            f = n[:-len(s)].strip()
            if len(f)>=3:
                return f
    w = n.split()
    return " ".join(w[:3]) if len(w)>=4 else (" ".join(w[:2]) if len(w)>=3 else n)

def gen_key(brand, model, storage="", variant=""):
    b = norm(brand).upper() if brand else "UNKNOWN"
    m = norm(model).upper() if model else "UNKNOWN"
    s = norm_storage(storage)
    parts = [b,m]
    if s:
        parts.append(s)
    return normalize_pricing_key(" ".join(parts))

def gen_fallback_key(brand, model, storage=""):
    b = norm(brand).upper() if brand else "UNKNOWN"
    m = norm(model).upper() if model else "UNKNOWN"
    s = norm_storage(storage)
    fam = extract_family(m)
    base = normalize_pricing_key(f"{b} {fam}")
    full = normalize_pricing_key(f"{b} {m}"+(f" {s}" if s else ""))
    model_key = normalize_pricing_key(f"{b} {m}")
    if base==full or base==model_key:
        if s:
            return model_key if model_key!=full else ""
        return ""
    return base

def get_shipping(item: Dict) -> Decimal:
    if item.get("shippingStatus")=="FREE":
        return Decimal("0")
    return sd(item.get("shippingFee"), SHIPPING_COST)

def check_limits():
    if _total_tokens >= MAX_TOKENS:
        raise RuntimeError(f"Token limit exceeded: {_total_tokens}/{MAX_TOKENS}")
    e = 0 if _start_time is None else time.time()-_start_time
    if LAMBDA_TIMEOUT-e-TIMEOUT_BUFFER <= 0:
        raise RuntimeError(f"Timeout approaching: {e:.1f}s elapsed")

# ======================================
# AI Service
# ======================================

def _extract_secret_value(secret_string: str, mode: str) -> str:
    """从 Secrets Manager 的 SecretString 中提取 API Key。"""
    if not secret_string:
        return ""

    try:
        secret_dict = json.loads(secret_string)
    except json.JSONDecodeError:
        return secret_string.strip()

    if not isinstance(secret_dict, dict):
        return ""

    logger.info("Secret JSON keys: %s", list(secret_dict.keys()))
    for key_name in (
        "apiKey",
        "api_key",
        "key",
        "GEMINI_API_KEY",
        "DOUBAO_API_KEY",
        "OPENAI_API_KEY",
        f"{mode.upper()}_API_KEY",
    ):
        val = secret_dict.get(key_name)
        if val:
            logger.info("Found key via '%s'", key_name)
            return str(val).strip()

    first_val = next((v for v in secret_dict.values() if v), "")
    if first_val:
        logger.info("Using first non-empty value from JSON secret")
        return str(first_val).strip()

    return ""


def _is_valid_header_key(key: str, mode: str) -> bool:
    """验证 API Key 能否安全写入 HTTP Header。"""
    if not key or any(char.isspace() for char in key):
        logger.error("Secret value for %s is empty or contains whitespace", mode)
        return False
    try:
        key.encode("ascii")
    except UnicodeEncodeError:
        logger.error("Secret value for %s contains non-ASCII characters", mode)
        return False
    return True


def _get_key(mode: str) -> str:
    """仅从 Secrets Manager 获取 AI API Key。

    API Key 不从 Lambda 环境变量读取，统一通过
    <mode>-api-key-<ENVIRONMENT> 管理；SECRET_NAME 仅作为旧版 Secret 名称兜底。
    """
    env = os.getenv("ENVIRONMENT", "dev")
    secret_names = [f"{mode}-api-key-{env}"]

    legacy_secret = os.getenv("SECRET_NAME", "").strip()
    if legacy_secret:
        secret_names.append(legacy_secret)

    for secret_name in dict.fromkeys(secret_names):
        logger.info("Reading secret: %s", secret_name)
        try:
            response = secrets.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString", "")
            logger.info("Secret retrieved, length=%s", len(secret_string))
            key = _extract_secret_value(secret_string, mode)
            if key and _is_valid_header_key(key, mode):
                return key
        except Exception as e:
            logger.error("Secret read failed for %s: %s: %s", secret_name, type(e).__name__, e)

    return ""

def get_ai_cfg(excluded_modes=None):
    """获取 AI 配置，key 只从 Secrets Manager 读取。

    excluded_modes 只用于一次 call_ai 调用内的故障转移，避免失败状态跨批次保留。
    """
    excluded_modes = set(excluded_modes or ())
    order = [AI_MODE] + [m for m in ["gemini","doubao","openai"] if m != AI_MODE]

    for mode in order:
        if mode in excluded_modes:
            continue
        
        original = AI_CONFIGS.get(mode, {})
        if not original:
            continue
        
        cfg = dict(original)
        
        # ★ 只从 Secrets Manager 读 key
        key = _get_key(mode)
        url = str(cfg.get("url") or "").strip()
        model = str(cfg.get("model") or "").strip()
        
        if not key:
            logger.warning("AI mode %s skipped: API key missing from Secrets Manager", mode)
            continue
        
        if not url:
            logger.warning("AI mode %s skipped: API URL missing", mode)
            continue
        
        if not model:
            logger.warning("AI mode %s skipped: model missing", mode)
            continue
        
        cfg["key"] = key
        
        logger.info("Selected AI mode=%s model=%s url=%s", mode, model, url)
        return cfg
    
    logger.error("No AI config available after checking modes: %s", order)
    return None

def call_ai(prompt: str, max_tokens: int) -> Tuple[Optional[Dict],Optional[str]]:
    global _total_tokens
    logger.info("PROMPT_LENGTH=%s current_tokens=%s", len(prompt), _total_tokens)

    failed_modes = set()
    for attempt in range(3):
        cfg = get_ai_cfg(failed_modes)
        if not cfg:
            logger.error("All AI modes unavailable")
            return None,"ALL_MODES_UNAVAILABLE"
        
        mode, is_gem = cfg["name"], cfg["type"]=="gemini"
        logger.info(f"AI attempt {attempt+1}: mode={mode}, model={cfg['model']}")
        
        output_limit = min(max_tokens, cfg["max_tokens"])
        body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.0,"maxOutputTokens":output_limit}} if is_gem else {"model":cfg["model"],"messages":[{"role":"system","content":"JSONのみ返してください"},{"role":"user","content":prompt}],"temperature":0.0,"max_tokens":output_limit}
        if mode=="doubao":
            body["response_format"]={"type":"json_object"}
        headers = {"x-goog-api-key":cfg["key"],"Content-Type":"application/json"} if is_gem else {"Authorization":f"Bearer {cfg['key']}","Content-Type":"application/json"}

        # 调试开关默认关闭，避免常规运行时输出大量商品文本。
        # 请求日志只记录 JSON body，不记录含 API Key 的 headers。
        if LOG_AI_REQUEST_JSON:
            logger.info(
                "AI_REQUEST_JSON=%s",
                json.dumps(body, ensure_ascii=False, separators=(",", ":"), default=str),
            )
        
        for retry in range(AI_RETRIES):
            try:
                check_limits()
                req = urllib.request.Request(
                    cfg["url"],
                    data=json.dumps(body,ensure_ascii=False).encode(),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req,timeout=cfg["timeout"]) as r:
                    result = json.loads(r.read().decode())

                if LOG_AI_RESPONSE_JSON:
                    logger.info(
                        "AI_RESPONSE_JSON=%s",
                        json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str),
                    )
                
                u = result.get("usageMetadata",{}) or result.get("usage",{})
                tokens_used = u.get("total_tokens",u.get("totalTokenCount",0))
                _total_tokens += tokens_used
                record_token_usage(mode, cfg["model"], u, prompt=prompt,
                                   task_type="AUCTION_ANALYSIS")
                logger.info(f"AI response: mode={mode}, tokens={tokens_used}, total_tokens={_total_tokens}")
                
                if is_gem:
                    if "candidates" in result and result["candidates"]:
                        c = result["candidates"][0]
                        fr = c.get("finishReason","unknown")
                        content = "".join(p.get("text","") for p in c.get("content",{}).get("parts",[]))
                    else:
                        content,fr = "","unknown"
                else:
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0].get("message",{}).get("content","")
                        fr = result["choices"][0].get("finish_reason","unknown")
                    else:
                        content,fr = "","unknown"
                
                logger.info("AI finish: reason=%s OUTPUT_LENGTH=%s", fr, len(content))
                
                if fr=="SAFETY":
                    return None,"safety_blocked"
                parsed = _parse_json(content)
                if parsed is not None:
                    if "items" in parsed:
                        logger.info(f"AI parsed: {len(parsed['items'])} items")
                    return parsed,fr
                else:
                    logger.warning(f"Failed to parse AI response as JSON")
                    
            except RuntimeError:
                raise
            
            # ★★★ FIX 1: HTTP错误响应内容记录 ★★★
            except urllib.error.HTTPError as e:
                try:
                    error_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    error_body = ""
                
                logger.error(
                    "[%s] HTTP error retry=%s status=%s response=%s",
                    mode,
                    retry + 1,
                    e.code,
                    error_body[:3000]
                )
                if e.code in (400, 401, 403, 404):
                    logger.warning(
                        "[%s] non-retryable HTTP status=%s; switching AI mode",
                        mode,
                        e.code,
                    )
                    break
            
            except urllib.error.URLError as e:
                logger.error(
                    "[%s] URL error retry=%s reason=%s",
                    mode,
                    retry + 1,
                    e.reason
                )
            
            except socket.timeout:
                logger.error(
                    "[%s] timeout retry=%s timeout=%s",
                    mode,
                    retry + 1,
                    cfg["timeout"]
                )
            
            except Exception as e:
                logger.exception(
                    "[%s] unexpected AI error retry=%s",
                    mode,
                    retry + 1
                )
            
            if retry < AI_RETRIES-1:
                time.sleep(2**retry+random.uniform(0,1))
        
        failed_modes.add(mode)
        logger.warning(f"Mode {mode} failed, switching to next")
    
    return None,"ALL_MODES_EXHAUSTED"

def _parse_json(content: str) -> Optional[Dict]:
    if not content:
        return None
    content = content.strip()
    for p in [lambda c: json.loads(c), lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```","",c))]:
        try:
            return p(content)
        except:
            pass
    for bracket in ('{','['):
        depth,start = 0,-1
        for i,ch in enumerate(content):
            if ch==bracket:
                if depth==0:
                    start=i
                depth+=1
            elif ch==('}' if bracket=='{' else ']'):
                depth-=1
                if depth==0 and start>=0:
                    try:
                        return json.loads(content[start:i+1])
                    except:
                        break
    return None

# ======================================
# Prompt Templates
# ======================================

ACTIVE_PARSE_PROMPT = """Yahoo!オークションの出品中商品を参照製品と比較してください。
入力:{items_json}
次のJSONだけ返してください:
{{"items":[{{"itemId":"123","matched":true,"listingType":"MAIN_PRODUCT"}}]}}

listingType:
MAIN_PRODUCT=商品本体
ACCESSORY=フード/ケース/フィルター/バッテリー/充電器/互換品
BOX_ONLY=箱のみ/元箱のみ/空箱
PARTS=部品/修理用/部品取り
RENTAL=レンタル/貸出/1日/2日間/往復送料無料
BUNDLE=複数セット
UNKNOWN=判断不能

ルール:
sourceModelと同じ本体ならmatched=true。
ブランドまたはモデルが違う商品本体なら、listingType=MAIN_PRODUCTでもmatched=false。
レンタルはRENTAL。
元箱のみ/箱のみ/空箱はBOX_ONLY。
レンズフード/HB-93/互換フードはACCESSORY。
本体が含まれない場合はMAIN_PRODUCTにしない。
商品本体を特定できなければmodels=[]。
他のフィールドは禁止。"""

COUNTDOWN_ACTIVE_PARSE_PROMPT = """Yahoo!オークションの出品中商品タイトルから、価格比較に使える商品本体のブランドとモデルを抽出してください。
入力:{items_json}

次のJSONだけ返してください:
{{
"items":[
{{
"itemId":"123",
"matched":true,
"listingType":"MAIN_PRODUCT",
"models":[
{{"brand":"Apple","model":"iPhone 13"}}
]
}}
]
}}

listingType:
MAIN_PRODUCT=商品本体
ACCESSORY=ケース/フィルム/充電器/ケーブル/バッテリー/互換品
BOX_ONLY=箱のみ/元箱のみ/空箱
PARTS=部品/修理用/部品取り
RENTAL=レンタル/貸出
BUNDLE=複数セット
UNKNOWN=判断不能

ルール:
1. スマホ本体なら MAIN_PRODUCT。
2. ブランドとモデルが明確に分かる場合だけ models に入れる。
3. iPhone は Pro/Pro Max/Plus/mini/SE を区別してください。
4. Android は Pixel/Galaxy/Xperia/AQUOS/OPPO/Xiaomi 等のモデル名を抽出してください。
5. 容量、キャリア、色はこの簡易解析では不要です。
6. ケース、フィルム、充電器、箱のみ、部品のみは MAIN_PRODUCT にしない。
7. ジャンクや故障したスマホ本体は MAIN_PRODUCT としてよい。
8. 型番が不明な場合は models=[]。
9. JSONのみ返してください。"""

CLOSED_PARSE_PROMPT = """Yahoo!オークションの終了商品を参照製品と比較してください。
入力:{items_json}
次のJSONだけ返してください:
{{"items":[{{"itemId":"123","matched":true,"listingType":"MAIN_PRODUCT"}}]}}

listingType:
MAIN_PRODUCT=商品本体
ACCESSORY=フード/ケース/フィルター/バッテリー/充電器/互換品
BOX_ONLY=箱のみ/元箱のみ/空箱
PARTS=部品/修理用/部品取り
RENTAL=レンタル/貸出/1日/2日間/往復送料無料
BUNDLE=複数セット
UNKNOWN=判断不能

ルール:
sourceModelと同じ本体ならmatched=true。
違うモデルならmatched=false。
レンタルはRENTAL。
元箱のみ/箱のみ/空箱はBOX_ONLY。
レンズフード/HB-93/互換フードはACCESSORY。
本体が含まれない場合はMAIN_PRODUCTにしない。
他のフィールドは禁止。"""

DETAILED_PARSE_PROMPT = """あなたは中古電子製品の識別専門家です。
以下の商品タイトルと商品説明を解析し、価格比較に必要な詳細スペックを抽出してください。

入力：
{items_json}

必ず以下のJSON形式のみを返してください。説明文は一切不要です。
全ての入力 itemId を必ず含めてください。

{{
  "items": [
    {{
      "itemId": "ID",
      "matched": true,
      "brand": "ブランド",
      "model": "完全なモデル名",
      "variant": "Pro/Pro Max/Plus/Ultra/Edition等、価格に影響する派生名。なければ空文字",
      "storage": "容量。例: 128GB, 256GB, RAM16GB SSD512GB 等。なければ空文字",
      "color": "色。説明に明記があれば抽出。なければ空文字",
      "carrier": "SIMフリー/docomo/au/SoftBank/楽天/制限あり等。なければ空文字",
      "networkRestriction": "ネットワーク利用制限の状態。〇/△/×/不明",
      "batteryHealth": "バッテリー最大容量。例: 82%。なければ空文字",
      "cpu": "CPU/SoC。PCやMacで明記があれば抽出",
      "ram": "メモリ容量。PC/Macで明記があれば抽出",
      "gpu": "GPU。明記があれば抽出",
      "screenSize": "画面サイズ。明記があれば抽出",
      "year": "年式/世代。明記があれば抽出",
      "accessories": "付属品。本体のみ/箱あり/充電器あり等",
      "defects": ["画面割れ", "Face ID不良", "バッテリー劣化", "水没", "起動不可 等"],
      "conditionDetail": "商品の状態詳細。例: 美品, 傷あり, ジャンク, 動作確認済み",
      "shortSummary": "100字以内で、商品一致性・状態・付属品・価格面の要点を簡潔にまとめる",
      "riskSummary": "傷、不具合、欠品、動作確認範囲、返品不可などの注意点",
      "buyReason": "marketPrice/currentPrice/profitを踏まえた簡潔な理由",
      "conditionRisk": "LOW/MEDIUM/HIGH",
      "listingType": "MAIN_PRODUCT",
      "condition": "USED",
      "conditionClass": "NORMAL/JUNK",
      "isJunk": false,
      "isLocked": false,
      "isWorking": true,
      "missing": [],
      "pricingCompareKeyParts": {{
        "brand": "比較に使うブランド",
        "model": "比較に使うモデル",
        "variant": "価格に影響する派生",
        "storage": "価格に影響する容量",
        "cpu": "PC/Macの場合、価格に影響するCPU",
        "ram": "PC/Macの場合、価格に影響するRAM",
        "gpu": "PC/Macの場合、価格に影響するGPU",
        "screenSize": "価格に影響する場合のみ"
      }}
    }}
  ]
}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/RENTAL/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

重要ルール：
1. sourceModel と同じ商品本体かを title と description の両方で判断し、違うモデルなら matched=false にしてください
2. 矛盾する場合、description の具体的な記載を優先してください
3. スマホは Pro/Pro Max/Plus/mini/Ultra を必ず区別してください
4. スマホは容量、SIMフリー、ネットワーク利用制限、バッテリー最大容量を可能な限り抽出
5. PC/Macは CPU、RAM、SSD/HDD、GPU、画面サイズ、年式を可能な限り抽出
6. ジャンク、故障、部品取り、画面割れ、起動不可、ロックあり、水没、Face ID不良などは defects に必ず入れる
7. 価格比較に使う項目は pricingCompareKeyParts に入れてください
8. 色やキャリアは抽出するが、pricingCompareKeyParts には価格差が大きい場合のみ入れる
9. 明記されていない情報は推測しない
10. 商品説明から読み取れない重要情報は missing に入れる
11. アクセサリ、部品、空箱、セット品は適切な listingType に分類する。故障した本体は MAIN_PRODUCT とする
12. conditionClass は isJunk=true、defects あり、condition=BROKEN、または listingType=BROKEN の場合 JUNK、それ以外は NORMAL
13. レンズ無し/レンズなし/本体無し/本体なし/本体は含まれません/商品本体なし は本体ではありません。その場合 listingType は BOX_ONLY または ACCESSORY、models は空配列にしてください
14. JSONのみを出力してください
15. matched=true の場合、brand と model は必ず sourceModel の brand/model を優先してください。title または description に sourceModel.model または aliases が明記されている場合、model を一般名に置き換えてはいけません。WH-1000XM5 をワイヤレスヘッドホン、Pixel Watch をスマートウォッチ、NIKKOR Z 24-70mm f/2.8 S をズームレンズ、Z7II をミラーレスカメラにしないでください
16. description に「型番」「MODEL」「モデル」「品番」がある場合、その具体的な型番を model として優先してください
17. matched=true だが model が sourceModel.model と異なる一般名になりそうな場合、model=sourceModel.model にしてください
18. 入力の currentPrice、marketPrice、estimatedProfit、profitMargin、pricingConfidence は shortSummary と buyReason の参考情報です。最終 BUY/AVOID 判定はシステム側で行うため、購入推奨を断定しすぎないでください
19. shortSummary は100字以内で、sourceModelとの一致、商品状態、付属品、価格面の概要を簡潔に含めてください
20. riskSummary は説明文から読み取れる注意点だけを書き、推測しないでください
21. conditionRisk は LOW/MEDIUM/HIGH のいずれかです。LOW=明確な不具合なし・動作確認済み、MEDIUM=傷・使用感・限定的確認・返品不可、HIGH=故障・動作未確認・ジャンク・部品取り・重要機能不良
22. closedReferences は同一モデルとして採用された終了オークションの title と落札 price です。商品同一性、付属品差、状態差、現在価格の妥当性を判断する参考にしてください。ただし、Active商品の title/description と矛盾する仕様を転記しないでください"""


def build_active_parse_prompt(items: List[Dict]) -> str:
    """Active AI 接收一次 sourceModel，并判定标题是否为同一商品。"""
    source_model = (items[0].get("sourceModel", {}) or {}) if items else {}
    items_data = []
    for item in items:
        data = {
            "itemId": str(item.get("itemID","")),
            "title": str(item.get("title", ""))[:ACTIVE_TITLE_MAX],
        }
        items_data.append(data)
    payload = {
        "sourceModel": {
            "brand": source_model.get("brand", ""),
            "model": source_model.get("model", ""),
        },
        "items": items_data,
    }
    return ACTIVE_PARSE_PROMPT.replace(
        "{items_json}",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )


def build_countdown_active_parse_prompt(items: List[Dict]) -> str:
    """倒计时模式不依赖 sourceModel，直接从 active 标题抽取品牌和型号。"""
    items_data = []
    for item in items:
        items_data.append({
            "itemId": str(item.get("itemID", "")),
            "title": str(item.get("title", ""))[:ACTIVE_TITLE_MAX],
            "price": si(item.get("price", 0)),
            "endTime": item.get("endTime", ""),
        })

    payload = {
        "mode": "countdown_active_model_extract",
        "category": "スマホ本体",
        "items": items_data,
    }
    return COUNTDOWN_ACTIVE_PARSE_PROMPT.replace(
        "{items_json}",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )


def build_closed_parse_prompt(items: List[Dict]) -> str:
    """Closed AI 只接收一次 sourceModel，并比较截断后的商品标题。"""
    source_model = (items[0].get("sourceModel", {}) or {}) if items else {}
    items_data = []
    for item in items:
        items_data.append({
            "itemId": str(item.get("itemID", "")),
            "title": str(item.get("title", ""))[:CLOSED_TITLE_MAX],
        })
    payload = {
        "sourceModel": {
            "brand": source_model.get("brand", ""),
            "model": source_model.get("model", ""),
        },
        "items": items_data,
    }
    return CLOSED_PARSE_PROMPT.replace("{items_json}", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def build_description_parse_prompt(items: List[Dict]) -> str:
    """发送 Active 详情，并附带定价采用的 Closed 成交标题和价格。"""
    source_model = (items[0].get("sourceModel", {}) or {}) if items else {}
    items_data = []
    for item in items:
        pricing_result = item.get("pricingResult") or {}
        reference_samples = item.get("closedReferenceSamples")
        if reference_samples is None:
            reference_samples = build_closed_reference_samples(pricing_result, limit=10)
        items_data.append({
            "itemId": str(item.get("itemID", "")),
            "title": item.get("title", ""),
            "description": str(item.get("detailDescription", ""))[:DETAIL_DESC_MAX],
            "currentPrice": si(item.get("price", 0)),
            "buynowPrice": si(item.get("buynowPrice", 0)),
            "marketPrice": si(pricing_result.get("estimatedMarketPrice", 0)),
            "estimatedProfit": si(pricing_result.get("netProfitAtCurrentBid", 0)),
            "profitMargin": str(pricing_result.get("profitMarginAtCurrentBid", "")),
            "pricingConfidence": str(pricing_result.get("pricingConfidence", "")),
            "closedReferences": [
                {
                    "title": str(sample.get("title", ""))[:160],
                    "price": si(sample.get("price", 0)),
                }
                for sample in reference_samples
                if sample.get("title") and si(sample.get("price", 0)) > 0
            ],
        })
    payload = {
        "sourceModel": {
            "brand": source_model.get("brand", ""),
            "model": source_model.get("model", ""),
            "aliases": source_model.get("aliases") or source_model.get("alias") or [],
        },
        "items": items_data,
    }
    return DETAILED_PARSE_PROMPT.replace(
        "{items_json}",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )

# ======================================
# Model Parser (详细参数版)
# ======================================

def norm_detail(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, list):
        return " ".join(str(x).strip() for x in v if str(x).strip())
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return norm(str(v))

def get_condition_class(data: Dict, default: str = ConditionClass.NORMAL) -> str:
    """统一商品状态分类。

    旧数据没有 conditionClass 时默认 NORMAL；对 AI 新返回的数据，也会根据
    isJunk/defects/condition/listingType 进行程序端校正。
    """
    explicit = norm(data.get("conditionClass", "")).upper()
    is_junk = str(data.get("isJunk", "")).lower() in ("true", "1", "yes")
    defects = data.get("defects", []) or []
    condition = norm(data.get("condition", data.get("parsedCondition", ""))).upper()
    listing_type = norm(data.get("listingType", "")).upper()
    if is_junk or bool(defects) or condition == "BROKEN" or listing_type == ListingType.BROKEN:
        return ConditionClass.JUNK
    if explicit == ConditionClass.JUNK:
        return ConditionClass.JUNK
    if explicit == ConditionClass.NORMAL:
        return ConditionClass.NORMAL
    return default if default in (ConditionClass.NORMAL, ConditionClass.JUNK) else ConditionClass.NORMAL

def gen_detailed_key(parsed: Dict) -> str:
    cp = parsed.get("pricingCompareKeyParts",{}) or {}
    b = norm(cp.get("brand") or parsed.get("brand","")).upper()
    m = norm(cp.get("model") or parsed.get("model","")).upper()
    v = norm(cp.get("variant") or parsed.get("variant","")).upper()
    s = norm_storage(cp.get("storage") or parsed.get("storage",""))
    cpu = norm_detail(cp.get("cpu") or parsed.get("cpu","")).upper()
    ram = norm_detail(cp.get("ram") or parsed.get("ram","")).upper()
    gpu = norm_detail(cp.get("gpu") or parsed.get("gpu","")).upper()
    scr = norm_detail(cp.get("screenSize") or parsed.get("screenSize","")).upper()
    
    parts = [b,m]
    if v:
        parts.append(v)
    if s:
        parts.append(s)
    if cpu:
        parts.append(cpu)
    if ram:
        parts.append(ram)
    if gpu:
        parts.append(gpu)
    if scr:
        parts.append(scr)
    parts.append(get_condition_class(parsed))
    
    combined = " ".join(p for p in parts if p)
    return normalize_pricing_key(combined)

def parse_ai_result(parsed: Dict) -> Tuple[List[Dict], str, str, int, List[str], str]:
    brand = norm(parsed.get("brand",""))
    model = norm(parsed.get("model",""))
    variant = norm(parsed.get("variant",""))
    storage = norm_storage(parsed.get("storage",""))
    lt = norm(parsed.get("listingType","UNKNOWN")).upper()
    cond = norm(parsed.get("condition","UNKNOWN")).upper()
    missing = [m for m in (parsed.get("missing") or []) if str(m).lower() not in NON_CRITICAL_FIELDS]
    defects = parsed.get("defects",[]) or []
    is_junk = str(parsed.get("isJunk","")).lower() in ("true","1","yes")
    is_locked = str(parsed.get("isLocked","")).lower() in ("true","1","yes")
    condition_class = get_condition_class(parsed)
    
    has_b, has_m = bool(brand), bool(model)
    is_unk = model.upper() in ("UNKNOWN","不明","N/A","")
    missing_critical = []
    if not has_b:
        missing.append("brand")
        missing_critical.append("brand")
    if not has_m or is_unk:
        missing.append("model")
        missing_critical.append("model")
    if not storage:
        missing_critical.append("storage")
    missing_critical = list(dict.fromkeys(missing_critical))
    mc = len(missing_critical)
    
    identifiable = (has_b or has_m) and not is_unk
    
    models = []
    if identifiable:
        b2 = brand if has_b else "UNKNOWN"
        m2 = model if has_m else "UNKNOWN"
        pk = gen_detailed_key(parsed) or gen_key(b2,m2,storage,variant)
        fk = gen_fallback_key(b2,m2,storage)
        if fk:
            fk = pricing_key_with_condition(fk, condition_class)
        if not fk or fk==pk:
            fk = ""
        fm = extract_family(m2.upper()) if has_m else ""
        
        detailed = {
            "color": norm_detail(parsed.get("color","")),
            "carrier": norm_detail(parsed.get("carrier","")),
            "networkRestriction": norm_detail(parsed.get("networkRestriction","")),
            "batteryHealth": norm_detail(parsed.get("batteryHealth","")),
            "cpu": norm_detail(parsed.get("cpu","")),
            "ram": norm_detail(parsed.get("ram","")),
            "gpu": norm_detail(parsed.get("gpu","")),
            "screenSize": norm_detail(parsed.get("screenSize","")),
            "year": norm_detail(parsed.get("year","")),
            "accessories": norm_detail(parsed.get("accessories","")),
            "defects": defects,
            "conditionDetail": norm_detail(parsed.get("conditionDetail","")),
            "isJunk": is_junk,
            "isLocked": is_locked,
            "isWorking": parsed.get("isWorking"),
            "pricingCompareKeyParts": parsed.get("pricingCompareKeyParts",{})
        }
        
        models.append({
            "brand": b2,
            "model": m2,
            "familyModel": fm if fm!=m2.upper() else "",
            "variant": variant,
            "storage": storage,
            "pricingModelKey": pk,
            "fallbackPricingKey": fk,
            "missingParameterCount": mc,
            "conditionClass": condition_class,
            "detailedParameters": detailed
        })
    
    reasons = []
    if lt in EXCLUDED_TYPES:
        reasons.append(f"Type: {lt}")
    if cond=="BROKEN":
        reasons.append("BROKEN")
    if is_junk:
        reasons.append("JUNK")
    if is_locked:
        reasons.append("LOCKED")
    if defects:
        reasons.append(f"Defects: {','.join(str(d) for d in defects[:5])}")
    
    return models, lt, cond, mc, missing_critical, "; ".join(reasons)

def preserve_source_model_if_matched(parsed: Dict, item: Optional[Dict]) -> Dict:
    """详情明确提到目标型号时，防止 AI 将型号降级成泛称。"""
    parsed = dict(parsed or {})
    source_model = (item or {}).get("sourceModel", {}) or {}
    source_brand = source_model.get("brand", "")
    source_model_name = source_model.get("model", "")
    aliases = source_model.get("aliases") or source_model.get("alias") or []
    if isinstance(aliases, str):
        aliases = [aliases]
    if not source_model_name:
        return parsed

    text = " ".join((
        str((item or {}).get("title", "")),
        str((item or {}).get("detailDescription", "")),
    ))
    text_key = normalize_pricing_key(text)
    candidate_keys = [normalize_pricing_key(source_model_name)]
    candidate_keys.extend(normalize_pricing_key(alias) for alias in aliases if alias)
    mentioned = any(key and key in text_key for key in candidate_keys)
    if mentioned and parsed.get("matched") is not False:
        parsed["matched"] = True
        parsed["brand"] = source_brand or parsed.get("brand", "")
        parsed["model"] = source_model_name
        compare_parts = dict(parsed.get("pricingCompareKeyParts") or {})
        compare_parts["brand"] = source_brand or compare_parts.get("brand", parsed.get("brand", ""))
        compare_parts["model"] = source_model_name
        parsed["pricingCompareKeyParts"] = compare_parts
        logger.info(
            "Source model preserved during detail analysis: itemID=%s model=%s",
            (item or {}).get("itemID", ""), source_model_name,
        )
    return parsed


def save_model(table, item_id: str, parsed: Dict, item: Optional[Dict] = None) -> str:
    parsed = preserve_source_model_if_matched(parsed, item)
    models, lt, cond, mc, missing_critical, excl = parse_ai_result(parsed)
    source_model = (item or {}).get("sourceModel", {}) or {}
    source_mismatch = bool(source_model.get("model")) and parsed.get("matched") is False
    if source_mismatch:
        models = []
        excl = "SOURCE_MODEL_MISMATCH"
    excluded = lt in EXCLUDED_TYPES
    condition_class = get_condition_class(parsed)

    if source_mismatch:
        status = Status.EXCLUDED
    elif not models:
        status = Status.REVIEW_REQUIRED
    elif excluded:
        status = Status.EXCLUDED
    else:
        status = Status.COMPLETED
    
    eligible = not source_mismatch and not excluded and len(models)>0
    update_record(table, item_id, {
        "models": models,
        "modelStatus": status,
        "listingType": lt,
        "conditionClass": condition_class,
        "missingParameterCount": mc,
        "missingCriticalParameters": missing_critical,
        "isComparable": eligible,
        "parsedCondition": cond,
        "exclusionReason": excl,
        "modelParsedAt": datetime.now(timezone.utc).isoformat(),
        "pricingStatus": Status.PENDING if eligible else Status.NOT_APPLICABLE,
        "isAnalysisEligible": eligible,
        "hasAllCriticalParameters": len(models)>0 and mc==0,
        "detailSummary": str(parsed.get("shortSummary", ""))[:500],
        "riskSummary": str(parsed.get("riskSummary", ""))[:500],
        "buyReason": str(parsed.get("buyReason", ""))[:500],
        "conditionRisk": norm(parsed.get("conditionRisk", "")).upper(),
        "aiMatched": parsed.get("matched"),
        "detailAnalyzedAt": datetime.now(timezone.utc).isoformat(),
    })
    logger.info(
        "Detail summary saved: itemID=%s conditionRisk=%s matched=%s summary=%s",
        item_id, parsed.get("conditionRisk", ""), parsed.get("matched"),
        str(parsed.get("shortSummary", ""))[:120],
    )
    
    logger.info(f"Model saved: {item_id} -> {status} (type={lt}, condition={cond}, models={len(models)})")
    return status

def _simple_model(parsed: Dict) -> Optional[Dict]:
    """读取精简 AI 响应中的首个 brand/model，并生成程序所需的匹配键。"""
    models = parsed.get("models", []) or []
    if not isinstance(models, list) or not models or not isinstance(models[0], dict):
        return None
    brand = norm(models[0].get("brand", ""))
    model = norm(models[0].get("model", ""))
    if not brand or not model:
        return None
    family = extract_family(model.upper())
    return {
        "brand": brand,
        "model": model,
        "familyModel": family if family != model.upper() else "",
        "pricingModelKey": pricing_key_with_condition(gen_key(brand, model), ConditionClass.NORMAL),
        "fallbackPricingKey": pricing_key_with_condition(gen_fallback_key(brand, model), ConditionClass.NORMAL),
    }

def save_active_model(table, item_id: str, parsed: Dict, item: Optional[Dict] = None) -> str:
    """保存 Active 精简模型和类型；非本体永不进入 pricing。"""
    source_model = (item or {}).get("sourceModel", {}) or {}
    has_source_model = bool(source_model.get("brand") and source_model.get("model"))
    matched = parsed.get("matched")
    # Active 与 Closed 使用同一比较语义。有参照模型时不再相信 AI
    # 抽取的“另一个正常商品”，只有 matched=true 才可进入定价。
    if has_source_model:
        model = _simple_model({"models": [source_model]}) if matched is True else None
    else:
        model = _simple_model(parsed)
    listing_type = norm(parsed.get("listingType", ListingType.UNKNOWN)).upper()
    if listing_type not in ALLOWED_LISTING_TYPES:
        listing_type = ListingType.UNKNOWN
    excluded = listing_type in EXCLUDED_TYPES
    if model and listing_type == ListingType.MAIN_PRODUCT:
        status = Status.COMPLETED
        pricing_status = Status.PENDING
        eligible = True
    elif excluded or (has_source_model and matched is False):
        status = Status.EXCLUDED
        pricing_status = Status.NOT_APPLICABLE
        eligible = False
    else:
        status = Status.REVIEW_REQUIRED
        pricing_status = Status.NOT_APPLICABLE
        eligible = False
    stored_model = model if listing_type == ListingType.MAIN_PRODUCT else None
    update_record(table, item_id, {
        "models": [stored_model] if stored_model else [],
        "modelStatus": status,
        "listingType": listing_type,
        "modelParsedAt": datetime.now(timezone.utc).isoformat(),
        "pricingStatus": pricing_status,
        "isAnalysisEligible": eligible,
    })
    return status

def save_closed_model(table, item_id: str, parsed: Dict, item: Optional[Dict] = None) -> str:
    """保存 Closed 同型号及 listingType 结果，不保存条件和比较判断字段。"""
    source_model = (item or {}).get("sourceModel", {}) or {}
    model = _simple_model({"models": [source_model]}) if parsed.get("matched") is True else None
    listing_type = norm(parsed.get("listingType", "UNKNOWN")).upper()
    if listing_type not in ALLOWED_LISTING_TYPES:
        listing_type = ListingType.UNKNOWN
    eligible = model is not None and listing_type == ListingType.MAIN_PRODUCT
    status = (
        Status.COMPLETED if eligible
        else Status.EXCLUDED if parsed.get("matched") is False or listing_type in EXCLUDED_TYPES
        else Status.REVIEW_REQUIRED
    )
    update_record(table, item_id, {
        "models": [model] if model else [],
        "modelStatus": status,
        "listingType": listing_type,
        "modelParsedAt": datetime.now(timezone.utc).isoformat(),
        "pricingStatus": Status.PENDING if eligible else Status.NOT_APPLICABLE,
        "isAnalysisEligible": eligible,
    })
    return status

def resolve_closed_without_ai(item: Dict) -> Optional[Dict]:
    """规范化型号已明确出现在标题时，用代码完成常见 Closed 判断。"""
    source_model = item.get("sourceModel", {}) or {}
    model_key = normalize_pricing_key(source_model.get("model", ""))
    title = str(item.get("title", ""))
    title_key = normalize_pricing_key(title)
    if not model_key or model_key not in title_key:
        return None

    normalized_title = unicodedata.normalize("NFKC", title).upper()
    keyword_types = (
        (ListingType.RENTAL, ("レンタル", "貸出", "1日", "2日間", "往復送料無料")),
        (ListingType.BOX_ONLY, ("元箱のみ", "レンズ用元箱", "空箱", "箱のみ", "BOX ONLY", "EMPTY BOX")),
        (ListingType.PARTS, ("部品取り", "修理用", "パーツのみ", "PARTS ONLY")),
        (ListingType.ACCESSORY, (
            "レンズフード", "互換フード", "HB-93", "ケースのみ", "カバーのみ",
            "充電器のみ", "バッテリーのみ", "ACCESSORY ONLY",
        )),
    )
    for listing_type, keywords in keyword_types:
        if any(keyword in normalized_title for keyword in keywords):
            return {"itemId": str(item.get("itemID", "")), "matched": True, "listingType": listing_type}
    return {"itemId": str(item.get("itemID", "")), "matched": True, "listingType": ListingType.MAIN_PRODUCT}

def mark_failed(table, item_id: str, error: str):
    update_record(table, item_id, {
        "modelStatus": Status.FAILED,
        "modelError": error[:500],
        "modelParsedAt": datetime.now(timezone.utc).isoformat()
    })
    logger.warning(f"Model failed: {item_id} -> {error[:100]}")

def batch_parse(table, items: List[Dict], prompt_builder, batch_size: int, max_tokens: int,
                saver=save_model, resolver=None) -> Dict:
    if not items:
        return {"parsed":0,"excluded":0,"review":0,"failed":0,"errors":[]}
    totals = {"parsed":0,"excluded":0,"review":0,"failed":0,"errors":[]}
    
    logger.info(f"Batch parse starting: {len(items)} items, batch_size={batch_size}")

    if resolver:
        program_counts = {"completed": 0, "excluded": 0, "review": 0, "failed": 0}
        unresolved_items = []
        for item in items:
            resolved = resolver(item)
            if resolved is None:
                unresolved_items.append(item)
                continue
            status = saver(table, str(item["itemID"]), resolved, item)
            if status == Status.COMPLETED:
                totals["parsed"] += 1
                program_counts["completed"] += 1
            elif status == Status.EXCLUDED:
                totals["excluded"] += 1
                program_counts["excluded"] += 1
            elif status == Status.REVIEW_REQUIRED:
                totals["review"] += 1
                program_counts["review"] += 1
            else:
                totals["failed"] += 1
                program_counts["failed"] += 1
        logger.info(
            "Program resolver result: total=%s handled=%s to_ai=%s "
            "completed=%s excluded=%s review=%s failed=%s",
            len(items),
            len(items) - len(unresolved_items),
            len(unresolved_items),
            program_counts["completed"],
            program_counts["excluded"],
            program_counts["review"],
            program_counts["failed"],
        )
        items = unresolved_items

    for start in range(0,len(items),batch_size):
        check_limits()
        batch = items[start:start+batch_size]
        item_map = {str(item["itemID"]): item for item in batch}
        logger.info(f"AI parsing batch {start//batch_size+1}/{(len(items)-1)//batch_size+1}, size={len(batch)}")
        
        prompt = prompt_builder(batch)
        tokens_before = _total_tokens
        result, err = call_ai(prompt, max_tokens)
        tokens_used = _total_tokens - tokens_before
        logger.info("TOKENS_PER_ITEM=%s", tokens_used / max(1, len(batch)))
        
        if not result:
            logger.error(f"AI returned empty for batch: {err}")
            for item in batch:
                mark_failed(table, str(item["itemID"]), err or "AI_EMPTY")
            totals["failed"] += len(batch)
            continue
        
        parsed = result.get("items",[]) or []
        logger.info(
            "FIRST_RETURNED_ITEM=%s",
            json.dumps(parsed[0] if parsed else None, ensure_ascii=False, default=str),
        )
        batch_ids = {str(item["itemID"]) for item in batch}
        returned = set()
        for p in parsed:
            if not isinstance(p,dict):
                continue
            iid = str(p.get("itemId","")).strip()
            if not iid or iid not in batch_ids:
                continue
            returned.add(iid)
            s = saver(table, iid, p, item_map[iid])
            if s==Status.COMPLETED:
                totals["parsed"]+=1
            elif s==Status.EXCLUDED:
                totals["excluded"]+=1
            elif s==Status.REVIEW_REQUIRED:
                totals["review"]+=1
            else:
                totals["failed"]+=1
        
        missing_ids = batch_ids-returned
        for mid in missing_ids:
            mark_failed(table, mid, "AI_NOT_RETURNED")
            totals["failed"]+=1
        
        logger.info(f"Batch result: parsed={totals['parsed']}, excluded={totals['excluded']}, review={totals['review']}, failed={totals['failed']}")
        
        if start+batch_size < len(items):
            time.sleep(_env("REQ_INTERVAL",1.0,float))
    
    return totals

# ======================================
# Matching Engine
# ======================================

def build_index(closed_ids: Set[str]) -> Dict[str,List[Dict]]:
    idx = {}
    excluded = 0
    logger.info(f"Building index from {len(closed_ids)} closed items")
    
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus") not in (Status.COMPLETED, Status.REVIEW_REQUIRED):
            continue
        if norm(item.get("listingType", "")).upper() in EXCLUDED_TYPES:
            continue
        if sd(item.get("price",0))<=0:
            continue
        
        models = item.get("models",[])
        if isinstance(models,str):
            try:
                models=json.loads(models)
            except:
                continue
        
        keys = set()
        for m in models:
            if not isinstance(m,dict):
                continue
            mn = norm(m.get("model","")).upper()
            if mn in ("UNKNOWN","不明","N/A",""):
                excluded+=1
                continue
            
            condition_class = get_condition_class(m, get_condition_class(item))
            pk = pricing_key_with_condition(m.get("pricingModelKey", ""), condition_class)
            if pk and pk not in keys:
                keys.add(pk)
                idx.setdefault(pk,[]).append(item)
            
            if ENABLE_FALLBACK:
                fk = pricing_key_with_condition(m.get("fallbackPricingKey", ""), condition_class)
                if fk and fk!=pk:
                    fq = f"FB:{fk}"
                    if fq not in keys:
                        keys.add(fq)
                        idx.setdefault(fq,[]).append(item)
            
            if ENABLE_FAMILY:
                fm = norm(m.get("familyModel","")).upper()
                if fm and fm!=mn:
                    b = norm(m.get("brand","")).upper()
                    if b:
                        fam = normalize_pricing_key(f"{b} {fm} {condition_class}")
                        fq = f"FAM:{fam}"
                        if fq not in keys:
                            keys.add(fq)
                            idx.setdefault(fq,[]).append(item)
    
    for k,v in idx.items():
        v.sort(key=lambda x: x.get("endTime",""), reverse=True)
    logger.info(f"Index built: {len(idx)} unique keys")
    return idx

def find_comp(item: Dict, idx: Dict[str,List[Dict]]) -> Tuple[List[Dict],Dict]:
    models = item.get("models",[])
    if isinstance(models,str):
        try:
            models=json.loads(models)
        except:
            return [],{"level":"ERROR"}
    
    items, seen = [], set()
    exact, fb, fam = 0, 0, 0
    
    for m in models:
        if not isinstance(m,dict):
            continue
        
        condition_class = get_condition_class(m, get_condition_class(item))
        pk = pricing_key_with_condition(m.get("pricingModelKey", ""), condition_class)
        if pk:
            for ci in idx.get(pk,[]):
                iid = str(ci.get("itemID",""))
                if iid and iid not in seen:
                    seen.add(iid)
                    items.append(ci)
            exact = len(items)
        
        if len(items)<MIN_COMPARABLE and ENABLE_FALLBACK:
            fk = pricing_key_with_condition(m.get("fallbackPricingKey", ""), condition_class)
            if fk:
                for ci in idx.get(f"FB:{fk}",[]):
                    iid = str(ci.get("itemID",""))
                    if iid and iid not in seen:
                        seen.add(iid)
                        items.append(ci)
                        fb+=1
        
        if len(items)<MIN_COMPARABLE and ENABLE_FAMILY:
            fm = norm(m.get("familyModel","")).upper()
            if fm:
                b = norm(m.get("brand","")).upper()
                if b:
                    fkey = normalize_pricing_key(f"{b} {fm} {condition_class}")
                    for ci in idx.get(f"FAM:{fkey}",[]):
                        iid = str(ci.get("itemID",""))
                        if iid and iid not in seen:
                            seen.add(iid)
                            items.append(ci)
                            fam+=1
    
    items.sort(key=lambda x: x.get("endTime",""), reverse=True)
    level = "EXACT" if exact>0 else ""
    if fb>0:
        level += "+FALLBACK" if level else "FALLBACK"
    if fam>0:
        level += "+FAMILY" if level else "FAMILY"
    
    return items, {"level":level,"total":len(items),"exact":exact,"fallback":fb,"family":fam}

# ======================================
# Pricing Engine
# ======================================

def calc_stats(items: List[Dict]) -> Dict:
    records = [{"id":str(i.get("itemID","")),"price":sd(i.get("price",0))} for i in items if sd(i.get("price",0))>0]
    records.sort(key=lambda r: r["price"])
    prices = [r["price"] for r in records]
    n = len(prices)
    
    base = {"count":n,"prices":[int(p) for p in prices],"ids":[r["id"] for r in records]}
    if n<MIN_COMPARABLE:
        if n>=1:
            mid = prices[n//2]
            base.update({"f_median":int(mid),"f_min":int(prices[0]),"f_max":int(prices[-1])})
        return {**base,"f_count":n,"suff":False,"reason":f"Need {MIN_COMPARABLE}, got {n}"}
    
    def pct(data,p):
        if not data:
            return Decimal("0")
        if len(data)==1:
            return data[0]
        pos = Decimal(len(data)-1)*p
        lo = int(pos)
        return data[lo]+(data[lo+1]-data[lo])*(pos-Decimal(lo)) if lo+1<len(data) else data[lo]
    
    q1,m,q3 = pct(prices,Decimal("0.25")),pct(prices,Decimal("0.5")),pct(prices,Decimal("0.75"))
    iqr = q3-q1
    lo,hi = q1-MAX_PRICE_DEV*iqr, q3+MAX_PRICE_DEV*iqr
    filtered = [r for r in records if lo<=r["price"]<=hi]
    fp = [r["price"] for r in filtered]
    fn = len(fp)
    
    if fn<MIN_COMPARABLE:
        return {**base,"min":int(prices[0]),"max":int(prices[-1]),"q1":int(q1),"median":int(m),"q3":int(q3),"iqr":int(iqr),"lower":int(lo),"upper":int(hi),"f_count":fn,"suff":False,"reason":f"Outlier: {fn}<{MIN_COMPARABLE}","f_median":int(m),"f_min":int(prices[0]),"f_max":int(prices[-1]),"f_prices":[int(p) for p in fp],"ids":[r["id"] for r in filtered]}
    
    fp.sort()
    fmed = pct(fp,Decimal("0.5"))
    spread = ((max(fp)-min(fp))/fmed).quantize(Decimal("0.001")) if fmed>0 else Decimal("0")
    
    return {**base,"min":int(prices[0]),"max":int(prices[-1]),"q1":int(q1),"median":int(m),"q3":int(q3),"iqr":int(iqr),"lower":int(lo),"upper":int(hi),"f_count":fn,"excl":n-fn,"suff":True,"f_min":int(min(fp)),"f_max":int(max(fp)),"f_median":int(fmed),"f_avg":int((sum(fp)/Decimal(fn)).quantize(Decimal("1"))),"spread":spread,"f_prices":[int(p) for p in fp],"ids":[r["id"] for r in filtered]}

def calc_conf(stats: Dict, item: Dict=None, mi: Dict=None) -> Decimal:
    if not stats.get("suff"):
        return Decimal("0.20")
    cc = stats["f_count"]
    sr = stats.get("spread",Decimal("0"))
    tc = stats["count"]
    ec = stats.get("excl",0)
    conf = Decimal("0.90") if cc>=HIGH_CONF else (Decimal("0.80") if cc>=MED_CONF else Decimal("0.70"))
    if sr>=Decimal("0.5"):
        conf-=Decimal("0.20")
    elif sr>=Decimal("0.3"):
        conf-=Decimal("0.10")
    if tc>0 and Decimal(ec)/Decimal(tc)>=Decimal("0.3"):
        conf-=Decimal("0.10")
    
    if item:
        ml = item.get("missingCriticalParameters",[])
        if isinstance(ml,str):
            try:
                ml=json.loads(ml)
            except:
                ml=[]
        penalty = Decimal("0")
        for p in ml:
            pl = str(p).lower()
            if "brand" in pl:
                penalty+=CRITICAL_PARAM_PENALTIES["brand"]
            elif "model" in pl:
                penalty+=CRITICAL_PARAM_PENALTIES["model"]
            elif "storage" in pl:
                penalty+=CRITICAL_PARAM_PENALTIES["storage"]
            else:
                penalty+=CRITICAL_PARAM_PENALTIES["other"]
        if penalty==Decimal("0") and item.get("missingParameterCount",0)>0:
            penalty = Decimal("0.05")*Decimal(item["missingParameterCount"])
        conf -= penalty
    
    if mi:
        if "FAMILY" in mi.get("level",""):
            conf-=Decimal("0.20")
        elif "FALLBACK" in mi.get("level",""):
            conf-=Decimal("0.10")
    
    return max(Decimal("0.20"),min(Decimal("0.95"),conf)).quantize(Decimal("0.01"))

def calc_risk(item: Dict, stats: Dict, conf: Decimal, margin: Decimal) -> Dict:
    score = 0
    factors, reasons = [], []
    cc = stats.get("f_count",0)
    mc = si(item.get("missingParameterCount",0))
    if mc>0:
        score+=mc*2
        factors.append(f"Missing {mc}")
    if cc<5:
        score+=2
        factors.append(f"Low samples:{cc}")
    elif cc<10:
        score+=1
    else:
        reasons.append(f"Good samples:{cc}")
    if conf<Decimal("0.5"):
        score+=3
    elif conf<Decimal("0.75"):
        score+=1
    
    sr = stats.get("spread",Decimal("0"))
    if sr>=Decimal("0.5"):
        score+=2
    elif sr>=Decimal("0.3"):
        score+=1
    
    r = item.get("sellerRating")
    if r:
        try:
            rr = Decimal(str(r).replace("%",""))
            if rr<Decimal("95"):
                score+=2
            elif rr<Decimal("98"):
                score+=1
        except:
            pass
    if str(item.get("sellerType","")).lower()=="personal":
        score+=1
    if margin<Decimal("0"):
        score+=3
    elif margin<REVIEW_MARGIN:
        score+=2
    elif margin<BUY_MARGIN:
        score+=1
    
    level = "HIGH" if score>=6 else ("MEDIUM" if score>=3 else "LOW")
    return {"level":level,"score":score,"factors":factors,"reasons":reasons}

def calc_profit(est: Decimal, buy: Decimal, ship: Decimal) -> Dict:
    fee = (est*FEE_RATE).quantize(Decimal("1"))
    rep = (est*REPAIR_RESERVE).quantize(Decimal("1"))
    risk = (est*RISK_RESERVE).quantize(Decimal("1"))
    tc = fee+ship+rep+risk
    net = est-buy-tc
    margin = (net/est).quantize(Decimal("0.001")) if est>0 else Decimal("0")
    inv = buy+ship+rep+risk
    roi = (net/inv).quantize(Decimal("0.001")) if inv>0 else Decimal("0")
    bep = (est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE)-ship).quantize(Decimal("1"))
    return {"net":net,"margin":margin,"roi":roi,"fee":fee,"repair":rep,"risk":risk,"tc":tc,"bep":max(0,int(bep)),"tp10":max(0,int((est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE-Decimal("0.1"))-ship).quantize(Decimal("1")))),"tp20":max(0,int((est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE-Decimal("0.2"))-ship).quantize(Decimal("1"))))}

def calc_decision(net: Decimal, margin: Decimal) -> str:
    """完全由代码规则生成购买建议，不调用 AI 风险评估。"""
    if net <= 0:
        return Recommendation.AVOID
    if margin >= Decimal("0.20"):
        return Recommendation.BUY_CANDIDATE
    return Recommendation.REVIEW

def build_result(item: Dict, stats: Dict, buy: Decimal, ship: Decimal, buynow=None, mi=None) -> Dict:
    ep = sd(stats.get("f_median",stats.get("median",0)))
    if ep<=0 and stats.get("prices"):
        ep = Decimal(str(sorted(stats["prices"])[len(stats["prices"])//2]))
    
    if not stats.get("suff"):
        result = {
            "pricingStatus":Status.INSUFFICIENT_DATA,
            "pricingConfidence":Decimal("0.2"),
            "riskLevel":"HIGH",
            "riskScore":10,
            "decisionSignal":Status.INSUFFICIENT_DATA,
            "reasons":[stats.get("reason","Insufficient")],
            "comparableCount":stats.get("f_count",stats.get("count",0)),
            "comparableItemIds":stats.get("ids",[])
        }
        if ep>0:
            p = calc_profit(ep,buy,ship)
            result.update({
                "estimatedMarketPrice":int(ep),
                "currentBidPrice":int(buy),
                "netProfitAtCurrentBid":int(p["net"]),
                "profitMarginAtCurrentBid":p["margin"],
                "roiAtCurrentBid":p["roi"]
            })
        return _to_dynamo(result)
    
    profit = calc_profit(ep,buy,ship)
    conf = calc_conf(stats,item,mi)
    risk = calc_risk(item,stats,conf,profit["margin"])
    cc = stats["f_count"]
    mc = si(item.get("missingParameterCount",0))
    dec = calc_decision(profit["net"], profit["margin"])
    
    reasons = []
    if mi:
        if mi.get("exact",0)>0:
            reasons.append(f"Exact: {mi['exact']}")
        if mi.get("fallback",0)>0:
            reasons.append(f"Fallback: +{mi['fallback']}")
        if mi.get("family",0)>0:
            reasons.append(f"Family: +{mi['family']}")
    reasons.append(f"Market: {int(ep)}")
    reasons.append(f"Net: {int(profit['net'])} ({(profit['margin']*100).quantize(Decimal('0.1'))}%)")
    if mc>0:
        reasons.insert(0,f"Warning: {mc} missing")
    if mi and mi.get("level","") not in ("","EXACT"):
        reasons.insert(0,f"Warning: {mi['level']}")
    
    result = {
        "pricingStatus":Status.COMPLETED,
        "estimatedMarketPrice":int(ep),
        "estimatedLow":int(stats.get("f_min",0)),
        "estimatedHigh":int(stats.get("f_max",0)),
        "currentBidPrice":int(buy),
        "breakEvenPurchasePrice":profit["bep"],
        "targetPurchasePrice10Margin":profit["tp10"],
        "targetPurchasePrice20Margin":profit["tp20"],
        "netProfitAtCurrentBid":int(profit["net"]),
        "profitMarginAtCurrentBid":profit["margin"],
        "roiAtCurrentBid":profit["roi"],
        "pricingConfidence":conf,
        "riskLevel":risk["level"],
        "riskScore":risk["score"],
        "decisionSignal":dec,
        "reasons":reasons+risk["reasons"],
        "riskFactors":risk["factors"],
        "comparableItemIds":stats.get("ids",[]),
        "comparableCount":cc,
        "missingParameterCount":mc,
        "matchInfo":mi or {"level":"EXACT"},
        "priceBreakdown":{
            "estimatedSellingPrice":int(ep),
            "currentBidPrice":int(buy),
            "platformFee":int(profit["fee"]),
            "shippingCost":int(ship),
            "repairReserve":int(profit["repair"]),
            "riskReserve":int(profit["risk"]),
            "netProfit":int(profit["net"])
        }
    }
    if buynow and buynow>0:
        bp = calc_profit(ep,buynow,ship)
        result.update({
            "buynowPrice":int(buynow),
            "netProfitAtBuynow":int(bp["net"]),
            "profitMarginAtBuynow":bp["margin"],
            "roiAtBuynow":bp["roi"]
        })
    return _to_dynamo(result)

def save_pricing(iid: str, result: Dict, rec: str):
    update_record(active_db, iid, {
        "pricingResult":result,
        "pricingStatus":result.get("pricingStatus",Status.FAILED),
        "pricedAt":datetime.now(timezone.utc).isoformat(),
        "purchaseRecommendation":rec
    })
    logger.info(f"Pricing saved: {iid} -> {rec}")


def parse_end_epoch(value: str) -> Optional[int]:
    """将 Yahoo 结束时间转换为 epoch；无法识别时返回 None。"""
    text = str(value or "").strip()
    if not text or text.lower() == "unknown":
        return None
    try:
        return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
        try:
            jst = timezone(timedelta(hours=9))
            return int(datetime.strptime(text, fmt).replace(tzinfo=jst).timestamp())
        except ValueError:
            continue
    return None


def build_closed_reference_samples(pricing: Dict, limit: int = 10) -> List[Dict]:
    """读取定价所用的 Closed 样本；单条读取失败不会阻断推荐写入。"""
    samples = []
    ids = pricing.get("comparableItemIds", []) or []
    for cid in ids[:max(0, min(int(limit), 10))]:
        try:
            item = get_record(closed_db, str(cid))
            if not item:
                continue
            samples.append({
                "itemID": str(item.get("itemID", cid)),
                "title": str(item.get("title", ""))[:160],
                "price": si(item.get("price", 0)),
                "endTime": item.get("endTime", ""),
                "url": item.get("url", ""),
                "sellerType": item.get("sellerType", ""),
                "conditionClass": item.get("conditionClass", ""),
                "listingType": item.get("listingType", ""),
            })
        except Exception as exc:
            logger.warning("Closed reference sample read failed: itemID=%s error=%s", cid, exc)
    return samples


def send_countdown_candidate_email(candidate: Dict):
    """发送倒计时模式候选商品的首次入库通知。"""
    subject = "【倒计时入库】{} {}".format(
        candidate.get("brand", ""), candidate.get("model", "")
    ).strip()
    message = f"""倒计时模式发现新的 BUY_CANDIDATE，已写入候选库。

商品：{candidate.get('title', '')}
当前价：{candidate.get('currentBidPrice', 0)}円
市场价：{candidate.get('marketPrice', 0)}円
预计利润：{candidate.get('netProfitAtCurrentBid', 0)}円
利润率：{candidate.get('profitMarginAtCurrentBid', '')}
ROI：{candidate.get('roiAtCurrentBid', '')}
风险等级：{candidate.get('riskLevel', '')}
置信度：{candidate.get('pricingConfidence', '')}

结束时间：{candidate.get('endTime', '')}
商品链接：
{candidate.get('url', '')}

系统仍会在拍卖结束前进行最终复核。"""
    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject[:100], Message=message)


def upsert_buy_candidate(item_id: str, item: Dict, pricing: Dict,
                         countdown_mode: bool = False):
    """保存 BUY_CANDIDATE；倒计时模式首次入库后立即发送一次邮件。"""
    market_price = si(pricing.get("estimatedMarketPrice", 0))
    if market_price <= 0:
        review_status = "NO_MARKET_PRICE"
        reminder_status = "NOT_SCHEDULED"
    else:
        review_status = "WAITING_FINAL_CHECK"
        reminder_status = "NOT_SENT"

    now = int(time.time())
    end_epoch = parse_end_epoch(item.get("endTime"))
    final_check_at = None
    candidate_status = "ACTIVE"
    reminder_error = ""
    if end_epoch is None:
        review_status = "INVALID_END_TIME"
        reminder_status = "NOT_SCHEDULED"
        reminder_error = "INVALID_END_TIME"
    elif end_epoch <= now:
        candidate_status = "EXPIRED"
        review_status = "EXPIRED"
        reminder_status = "SKIPPED"
        final_check_at = now
    else:
        final_check_at = max(now, end_epoch - FINAL_CHECK_BEFORE_MINUTES * 60)

    existing = buy_candidate_db.get_item(Key={"itemID": str(item_id)}).get("Item", {})
    # 已发送是终态，Analyzer 的再次定价不能造成重复提醒。
    if existing.get("reminderStatus") == "SENT":
        review_status = existing.get("reviewStatus", "FINAL_CHECK_DONE")
        reminder_status = "SENT"
        candidate_status = existing.get("candidateStatus", "ACTIVE")

    models = item.get("models") or [{}]
    model = models[0] if isinstance(models, list) and models else {}
    current_price = si(pricing.get("currentBidPrice", item.get("price", 0)))
    reference_samples = build_closed_reference_samples(pricing, limit=10)
    fields = {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "thumbnailUrl": item.get("thumbnailUrl", ""),
        "keyword": item.get("keyword", ""),
        "brand": model.get("brand", "") if isinstance(model, dict) else "",
        "model": model.get("model", "") if isinstance(model, dict) else "",
        "lastAnalyzedAt": now,
        "updatedAt": now,
        "firstCurrentPrice": existing.get("firstCurrentPrice", current_price),
        "currentBidPrice": current_price,
        "buynowPrice": si(item.get("buynowPrice", 0)),
        "marketPrice": market_price,
        "maxActivePrice": int(Decimal(market_price) * ACTIVE_MAX_RATIO),
        "estimatedMarketPrice": market_price,
        "netProfitAtCurrentBid": si(pricing.get("netProfitAtCurrentBid", 0)),
        "profitMarginAtCurrentBid": str(pricing.get("profitMarginAtCurrentBid", 0)),
        "roiAtCurrentBid": str(pricing.get("roiAtCurrentBid", 0)),
        "purchaseRecommendation": Recommendation.BUY_CANDIDATE,
        "pricingConfidence": str(pricing.get("pricingConfidence", 0)),
        "riskLevel": pricing.get("riskLevel", "HIGH"),
        "riskScore": si(pricing.get("riskScore", 0)),
        "shippingCost": int(get_shipping(item)),
        "endTime": item.get("endTime", ""),
        "candidateStatus": candidate_status,
        "reviewStatus": review_status,
        "reminderStatus": reminder_status,
        "source": "YahooAuctionAnalyzer",
        "detailSummary": item.get("detailSummary", ""),
        "riskSummary": item.get("riskSummary", ""),
        "buyReason": item.get("buyReason", ""),
        "conditionRisk": item.get("conditionRisk", ""),
        "aiMatched": item.get("aiMatched"),
        "referenceClosedSamples": reference_samples,
        "referenceClosedSampleCount": len(reference_samples),
    }
    if end_epoch is not None:
        fields["endEpoch"] = end_epoch
    if final_check_at is not None:
        fields["finalCheckAtEpoch"] = final_check_at
    if reminder_error:
        fields["reminderError"] = reminder_error
    should_send_countdown_email = countdown_mode and not existing
    if should_send_countdown_email:
        fields["countdownNotificationStatus"] = "PENDING"

    expression_names = {}
    values = {":first_detected": now}
    assignments = ["firstDetectedAt = if_not_exists(firstDetectedAt, :first_detected)"]
    for index, (key, value) in enumerate(fields.items()):
        name = f"#field{index}"
        expression_names[name] = key
        token = f":{key}"
        assignments.append(f"{name} = {token}")
        values[token] = _to_dynamo(value)
    buy_candidate_db.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="SET " + ", ".join(assignments),
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=values,
    )
    logger.info(
        "Buy candidate saved: itemID=%s current=%s market=%s profit=%s finalCheckAt=%s",
        item_id, current_price, market_price,
        fields["netProfitAtCurrentBid"], final_check_at,
    )
    logger.info(
        "Buy candidate reference samples saved: itemID=%s sampleCount=%s",
        item_id, len(reference_samples),
    )
    if should_send_countdown_email:
        notification_fields = {"countdownNotificationAt": now}
        try:
            if not SNS_TOPIC_ARN:
                raise RuntimeError("SNS_TOPIC_ARN_MISSING")
            send_countdown_candidate_email(fields)
            notification_fields["countdownNotificationStatus"] = "SENT"
            logger.info("倒计时入库邮件已发送: itemID=%s", item_id)
        except Exception as exc:
            notification_fields.update({
                "countdownNotificationStatus": "FAILED",
                "countdownNotificationError": str(exc)[:500],
            })
            logger.exception("倒计时入库邮件发送失败: itemID=%s", item_id)
        update_record(buy_candidate_db, str(item_id), notification_fields)


def deactivate_buy_candidate(item_id: str, reason: str):
    """取消尚未发送提醒的候选记录。"""
    existing = buy_candidate_db.get_item(Key={"itemID": str(item_id)}).get("Item")
    if not existing or existing.get("reminderStatus") == "SENT":
        return
    now = int(time.time())
    buy_candidate_db.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression=(
            "SET candidateStatus = :cancelled, reviewStatus = :cancelled, "
            "reminderStatus = :skipped, cancelReason = :reason, updatedAt = :now"
        ),
        ExpressionAttributeValues={
            ":cancelled": "CANCELLED", ":skipped": "SKIPPED",
            ":reason": reason, ":now": now,
        },
    )
    logger.info("Buy candidate cancelled: itemID=%s reason=%s", item_id, reason)


def has_usable_model(item: Dict) -> bool:
    """缺少参数或低置信度时仍允许使用已识别出的模型参与初步定价。"""
    models = item.get("models", [])
    if isinstance(models, str):
        try:
            models = json.loads(models)
        except json.JSONDecodeError:
            models = []
    return (
        item.get("modelStatus") in (Status.COMPLETED, Status.REVIEW_REQUIRED)
        and isinstance(models, list)
        and any(isinstance(model, dict) for model in models)
        and str(item.get("listingType", "")).upper() == ListingType.MAIN_PRODUCT
    )


def price_active_item(item_id: str, idx: Dict[str,List[Dict]],
                      sync_candidate: bool = True,
                      countdown_mode: bool = False) -> Optional[Dict]:
    """计算并保存单个 active 商品利润；返回定价结果。"""
    item = get_record(active_db, item_id)
    if not item or not has_usable_model(item):
        return None

    ci, mi = find_comp(item, idx)
    stats = calc_stats(ci)
    current_price = sd(item.get("price", 0))
    shipping = get_shipping(item)
    buynow = sd(item.get("buynowPrice")) if item.get("buynowPrice") else None

    pricing = build_result(item, stats, current_price, shipping, buynow, mi)
    recommendation = calc_decision(
        sd(pricing.get("netProfitAtCurrentBid", 0)),
        sd(pricing.get("profitMarginAtCurrentBid", 0)),
    )
    save_pricing(item_id, pricing, recommendation)
    if sync_candidate:
        try:
            if recommendation == Recommendation.BUY_CANDIDATE:
                upsert_buy_candidate(
                    item_id, item, pricing, countdown_mode=countdown_mode
                )
            else:
                deactivate_buy_candidate(item_id, "REPRICED_NOT_BUY_CANDIDATE")
        except Exception as exc:
            # 推荐库属于旁路能力，写入失败不能破坏现有 pricing 主流程。
            logger.exception("Buy candidate sync failed: itemID=%s error=%s", item_id, exc)
    return pricing


def should_reanalyze_description(item: Dict, pricing: Dict) -> bool:
    """所有初判 BUY_CANDIDATE/REVIEW 都必须经过详情复核。"""
    if pricing.get("pricingStatus") != Status.COMPLETED:
        return False
    recommendation = calc_decision(
        sd(pricing.get("netProfitAtCurrentBid", 0)),
        sd(pricing.get("profitMarginAtCurrentBid", 0)),
    )
    return recommendation in (Recommendation.BUY_CANDIDATE, Recommendation.REVIEW)


def scrape_profitable_active_detail(item_id: str) -> Optional[Dict]:
    """为有利润且缺关键参数的 active 商品按需抓取并保存详情。"""
    detail = scrape_item_detail(item_id)
    if not detail:
        update_record(active_db, item_id, {
            "detailScrapeStatus": "FAILED",
            "detailScrapeError": "scrape_item_detail returned None",
            "detailScrapedAt": datetime.now(timezone.utc).isoformat(),
        })
        return None

    description = detail.get("detailDescriptionCleaned", detail.get("description", "")) or ""
    fields = {
        "detailDescription": description,
        "detailDescriptionRaw": detail.get("detailDescriptionRaw", ""),
        "detailDescriptionCleaned": description,
        "detailDescriptionRawLength": detail.get("detailDescriptionRawLength", 0),
        "detailDescriptionCleanedLength": detail.get("detailDescriptionCleanedLength", len(description)),
        "detailDescriptionLength": detail.get("detailDescriptionLength", len(description)),
        "detailDescriptionCleanRatio": detail.get("detailDescriptionCleanRatio", Decimal("0")),
        "detailCleanedAt": detail.get("detailCleanedAt", ""),
        "detailTitle": detail.get("title", ""),
        "detailUrl": detail.get("url", ""),
        "detailScrapedAt": detail.get("scrapedAt", datetime.now(timezone.utc).isoformat()),
        "detailScrapeStatus": "COMPLETED" if description else "EMPTY",
        "detailScrapeError": "",
    }
    update_record(active_db, item_id, fields)
    logger.info(
        "On-demand detail scraped for profitable active item: %s cleaned_length=%s",
        item_id,
        len(description),
    )
    return {**(get_record(active_db, item_id) or {}), **fields}

# ======================================
# Workflow
# ======================================

def scrape_closed(kw: str, cnt: int, force: bool = False, source_model: Optional[Dict] = None) -> List[str]:
    """抓取已结束商品，新商品自动设为 PENDING"""
    try:
        items = scrape_auctions(
            kw, "closed", False, scrape_details=False,
            brand=(source_model or {}).get("brand", ""),
            model=(source_model or {}).get("model", ""),
            category_id=(source_model or {}).get("category_id", ""),
            aliases=(source_model or {}).get("aliases") or (source_model or {}).get("alias") or [],
        )[:cnt]
        new_count = 0
        
        for item in items:
            try:
                iid = str(item["itemId"])
                existing = get_record(closed_db, iid)
                if not existing:
                    new_count += 1
                
                upsert_scraped_item(
                    closed_db, iid,
                    {
                        "itemType": item.get("itemType", ""),
                        "title": item.get("title", ""),
                        "price": si(item.get("price", 0)),
                        "endTime": item.get("endTime") or "unknown",
                        "url": item.get("url", ""),
                        "sellerId": str(item.get("sellerId") or ""),
                        "sellerRating": str(item.get("sellerRating") or ""),
                        "sellerType": item.get("sellerType", "personal"),
                        "shippingFee": item.get("shippingFee"),
                        "shippingText": item.get("shippingText", ""),
                        "isFreeShipping": item.get("isFreeShipping", False),
                        "itemCondition": item.get("itemCondition"),
                        "thumbnailUrl": item.get("thumbnailUrl", ""),
                        "keyword": kw,
                        "sourceModel": source_model or {},
                    },
                    force=force
                )
            except Exception as e:
                logger.error(f"Save closed failed itemId={item.get('itemId')}: {e}")
        
        logger.info(f"Scraped {len(items)} closed items, {new_count} new")
        return [str(i["itemId"]) for i in items]
    except Exception as e:
        logger.error(f"Closed scrape: {e}")
        return []

def scrape_active(kw: str, cnt: int, max_p: int = 0, force: bool = False,
                  source_model: Optional[Dict] = None) -> List[str]:
    """抓取活跃商品，新商品自动设为 PENDING"""
    try:
        items = scrape_auctions(
            kw,
            "active",
            False,
            scrape_details=False,
            brand=(source_model or {}).get("brand", ""),
            model=(source_model or {}).get("model", ""),
            category_id=(source_model or {}).get("category_id", ""),
            aliases=(source_model or {}).get("aliases") or (source_model or {}).get("alias") or [],
        )
        if max_p > 0:
            before_count = len(items)
            items = [
                item for item in items
                if 0 < si(item.get("price", 0)) <= max_p
            ]
            logger.info(
                "Active price upper filter applied: max_price=%s before=%s after=%s",
                max_p,
                before_count,
                len(items),
            )
        items = items[:cnt]
        new_count = 0
        
        for item in items:
            try:
                iid = str(item["itemId"])
                existing = get_record(active_db, iid)
                if not existing:
                    new_count += 1
                stored_source_model = (existing or {}).get("sourceModel", {}) or {}
                source_model_changed = stored_source_model != (source_model or {})
                
                upsert_scraped_item(
                    active_db, iid,
                    {
                        "itemType": item.get("itemType", ""),
                        "title": item.get("title", ""),
                        "price": si(item.get("price", 0)),
                        "buynowPrice": si(item.get("buynowPrice")) if item.get("buynowPrice") else None,
                        "endTime": item.get("endTime") or "unknown",
                        "url": item.get("url", ""),
                        "sellerId": str(item.get("sellerId") or ""),
                        "sellerRating": str(item.get("sellerRating") or ""),
                        "sellerType": item.get("sellerType", "personal"),
                        "shippingFee": item.get("shippingFee"),
                        "shippingText": item.get("shippingText", ""),
                        "isFreeShipping": item.get("isFreeShipping", False),
                        "itemCondition": item.get("itemCondition"),
                        "thumbnailUrl": item.get("thumbnailUrl", ""),
                        "keyword": kw,
                        "sourceModel": source_model or {},
                    },
                    # Active records are global by auction ID.  Re-run model
                    # matching whenever this auction is viewed under a new
                    # target; otherwise a previous target's COMPLETED result
                    # could be reused for an unrelated product search.
                    force=force or source_model_changed
                )
            except Exception as e:
                logger.error(f"Save active failed itemId={item.get('itemId')}: {e}")
        
        logger.info(f"Scraped {len(items)} active items, {new_count} new")
        return [str(i["itemId"]) for i in items]
    except Exception as e:
        logger.error(f"Active scrape: {e}")
        return []

def _first_identified_model(item: Dict) -> Optional[Dict]:
    """返回 active AI 识别出的首个可搜索型号。"""
    if not has_usable_model(item):
        return None
    models = item.get("models") or []
    if isinstance(models, str):
        try:
            models = json.loads(models)
        except (TypeError, ValueError):
            return None
    for model in models:
        if not isinstance(model, dict):
            continue
        brand = norm(model.get("brand", ""))
        model_name = norm(model.get("model", ""))
        if brand and model_name and model_name.upper() not in ("UNKNOWN", "N/A", "不明"):
            return {**model, "brand": brand, "model": model_name}
    return None


def execute_countdown_workflow(category_id: str, ac: int, cc: int, force: bool) -> Dict:
    """从某个分类下即将结束的 active 商品开始分析。

    与常规型号工作流不同，本入口先用空关键词按分类抓 active，再由 AI 识别
    每件商品的具体型号，最后按识别结果分别抓取 closed 历史成交记录。
    """
    global _start_time
    _start_time = time.time()
    result = {"mode": "countdown", "keyword": "", "category_id": category_id}
    try:
        check_limits()
        logger.info("倒计时步骤 13-14：按分类抓取即将结束商品 category_id=%s", category_id)
        active_ids = scrape_active("", ac, 0, force, {"category_id": category_id})
        result["active"] = len(active_ids)
        if not active_ids:
            return {**result, "status": "NO_ACTIVE"}

        active_items = [get_record(active_db, aid) for aid in active_ids]
        pending_active = [
            item for item in active_items
            if item and (force or item.get("modelStatus") == Status.PENDING)
        ]
        logger.info("倒计时步骤 15：AI 识别 active 具体型号 count=%s", len(pending_active))
        if pending_active:
            result["active_parsed"] = batch_parse(
                active_db, pending_active, build_countdown_active_parse_prompt, SIMPLE_BATCH,
                SIMPLE_MAX_TOKENS, saver=save_active_model,
            )

        identified = {}
        for aid in active_ids:
            model = _first_identified_model(get_record(active_db, aid) or {})
            if model:
                model["category_id"] = category_id
                key = (model["brand"].casefold(), model["model"].casefold())
                identified.setdefault(key, model)
        result["identified_models"] = len(identified)
        if not identified:
            return {**result, "status": "NO_IDENTIFIED_MODEL"}

        logger.info("倒计时步骤 16-17：按 %s 个识别型号抓取并解析 closed", len(identified))
        closed_ids = []
        for model in identified.values():
            check_limits()
            keyword = f'{model["brand"]} {model["model"]}'.strip()
            model_closed_ids = scrape_closed(keyword, cc, force, model)
            closed_ids.extend(iid for iid in model_closed_ids if iid not in closed_ids)
            closed_items = [get_record(closed_db, iid) for iid in model_closed_ids]
            pending_closed = [
                item for item in closed_items
                if item and (force or item.get("modelStatus") == Status.PENDING)
            ]
            if pending_closed:
                batch_parse(
                    closed_db, pending_closed, build_closed_parse_prompt, SIMPLE_BATCH,
                    SIMPLE_MAX_TOKENS, saver=save_closed_model,
                    resolver=resolve_closed_without_ai,
                )
        result["closed"] = len(closed_ids)
        if not closed_ids:
            return {**result, "status": "NO_CLOSED"}

        logger.info("倒计时步骤 18-19：建立 closed 索引并为 active 定价")
        idx = build_index(set(closed_ids))
        result["index_size"] = len(idx)
        priced = 0
        review_ids = []
        for aid in active_ids:
            check_limits()
            item = get_record(active_db, aid)
            if not item or not has_usable_model(item):
                continue
            if not force and item.get("pricingStatus") != Status.PENDING:
                continue
            pricing = price_active_item(aid, idx, sync_candidate=False)
            if pricing:
                priced += 1
                if should_reanalyze_description(item, pricing):
                    review_ids.append(aid)

        logger.info("倒计时步骤 20-21：详情复核并同步 BUY_CANDIDATE count=%s", len(review_ids))
        recheck_items = []
        for aid in review_ids:
            existing = get_record(active_db, aid)
            detail_item = existing if (
                existing and existing.get("detailScrapeStatus") == "COMPLETED"
                and str(existing.get("detailDescription", "")).strip()
            ) else scrape_profitable_active_detail(aid)
            if detail_item and str(detail_item.get("detailDescription", "")).strip():
                detail_item["closedReferenceSamples"] = build_closed_reference_samples(
                    detail_item.get("pricingResult") or {}, limit=10
                )
                recheck_items.append(detail_item)
        if recheck_items:
            result["active_description_reanalysis"] = batch_parse(
                active_db, recheck_items, build_description_parse_prompt,
                DETAIL_BATCH, DETAIL_MAX_TOKENS,
            )
        repriced = 0
        for item in recheck_items:
            aid = str(item.get("itemID", ""))
            current = get_record(active_db, aid) if aid else None
            if current and has_usable_model(current) and price_active_item(
                aid, idx, sync_candidate=True, countdown_mode=True
            ):
                repriced += 1

        result.update({
            "priced": priced,
            "detail_reviewed": len(recheck_items),
            "description_repriced": repriced,
            "status": "COMPLETED",
            "elapsed": round(time.time() - _start_time, 1),
        })
        return result
    except RuntimeError as e:
        return {**result, "status": "INTERRUPTED", "reason": str(e)}
    except Exception as e:
        logger.error("倒计时工作流失败: %s", e, exc_info=True)
        return {**result, "status": "FAILED", "error": str(e)}

def calc_market_price(closed_ids: List[str]) -> Dict:
    """根据成交价分布剔除疑似低价配件簇，再计算市场价。"""
    candidates = []
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus")!=Status.COMPLETED:
            continue
        if norm(item.get("listingType", "")).upper() in EXCLUDED_TYPES:
            continue
        p = si(item.get("price",0))
        if p>0:
            candidates.append({
                "itemID": str(item.get("itemID") or cid),
                "title": str(item.get("title", "")),
                "price": p,
            })

    empty_result = {
        "market_price": 0, "avg_price": 0, "median_price": 0,
        "count": 0, "raw_count": 0,
        "raw_avg_price": 0, "raw_median_price": 0,
        "raw_min_price": 0, "raw_max_price": 0,
        "market_price_suspicious": False,
        "price_filter": {
            "low_price_cluster_removed": False,
            "removed_low_price_count": 0,
            "max_gap_ratio": "0",
            "split_low_max": 0,
            "split_high_min": 0,
        },
    }
    if not candidates:
        logger.info("Raw closed price stats: count=0")
        return empty_result

    candidates.sort(key=lambda candidate: candidate["price"])
    prices = [candidate["price"] for candidate in candidates]
    raw_count = len(prices)

    def median(values):
        count = len(values)
        middle = count // 2
        return values[middle] if count % 2 else (values[middle - 1] + values[middle]) // 2

    raw_avg_price = sum(prices) // raw_count
    raw_median_price = median(prices)
    raw_min_price = prices[0]
    raw_max_price = prices[-1]
    avg_median_ratio = (
        Decimal(raw_avg_price) / Decimal(raw_median_price)
        if raw_median_price > 0 else Decimal("0")
    )
    distribution_suspicious = raw_median_price > 0 and avg_median_ratio >= Decimal("5")
    logger.info(
        "Raw closed price stats: count=%s avg=%s median=%s min=%s max=%s "
        "avg_median_ratio=%s suspicious=%s",
        raw_count, raw_avg_price, raw_median_price, raw_min_price,
        raw_max_price, str(avg_median_ratio), distribution_suspicious,
    )

    max_gap_ratio = Decimal("0")
    split_index = None
    for index in range(raw_count - 1):
        current_price = prices[index]
        next_price = prices[index + 1]
        gap_ratio = Decimal(next_price) / Decimal(current_price)
        if gap_ratio > max_gap_ratio:
            max_gap_ratio = gap_ratio
            split_index = index + 1

    price_filter = {
        "low_price_cluster_removed": False,
        "removed_low_price_count": 0,
        "max_gap_ratio": str(max_gap_ratio.quantize(Decimal("0.001"))) if split_index is not None else "0",
        "split_low_max": prices[split_index - 1] if split_index is not None else 0,
        "split_high_min": prices[split_index] if split_index is not None else 0,
    }
    main_product_prices = prices
    market_price_suspicious = False

    if split_index is not None and max_gap_ratio >= Decimal("3.0"):
        high_price_cluster = prices[split_index:]
        if len(high_price_cluster) >= MIN_COMPARABLE:
            main_product_prices = high_price_cluster
            price_filter["low_price_cluster_removed"] = True
            price_filter["removed_low_price_count"] = split_index
            removed = candidates[:split_index]
            logger.warning(
                "Low-price accessory cluster removed: count=%s range=%s-%s "
                "high_min=%s gap_ratio=%s samples=%s",
                split_index, prices[0], prices[split_index - 1], prices[split_index],
                price_filter["max_gap_ratio"],
                [{"itemID": item["itemID"], "price": item["price"], "title": item["title"][:120]} for item in removed[:10]],
            )
        else:
            market_price_suspicious = True
            logger.warning(
                "Price gap detected but high-price cluster is too small: high_count=%s "
                "required=%s low_max=%s high_min=%s gap_ratio=%s",
                len(high_price_cluster), MIN_COMPARABLE, prices[split_index - 1],
                prices[split_index], price_filter["max_gap_ratio"],
            )
    elif distribution_suspicious:
        market_price_suspicious = True
        logger.warning("Suspicious price distribution has no usable price gap")

    logger.info(
        "Closed price cluster filter: removed=%s removed_count=%s low_max=%s "
        "high_min=%s max_gap_ratio=%s suspicious=%s",
        price_filter["low_price_cluster_removed"],
        price_filter["removed_low_price_count"],
        price_filter["split_low_max"],
        price_filter["split_high_min"],
        price_filter["max_gap_ratio"],
        market_price_suspicious,
    )
    if market_price_suspicious:
        logger.warning("Final market price: market_price=0 suspicious=true")
        return {
            **empty_result,
            "raw_count": raw_count,
            "raw_avg_price": raw_avg_price,
            "raw_median_price": raw_median_price,
            "raw_min_price": raw_min_price,
            "raw_max_price": raw_max_price,
            "market_price_suspicious": True,
            "price_filter": price_filter,
        }

    # Keep the existing IQR safety net when no accessory-cluster split was used.
    if not price_filter["low_price_cluster_removed"] and len(main_product_prices)>=3:
        n = len(main_product_prices)
        q1=main_product_prices[n//4]
        q3=main_product_prices[n*3//4]
        lo=int(q1-MAX_PRICE_DEV*(q3-q1))
        hi=int(q3+MAX_PRICE_DEV*(q3-q1))
        filtered = [p for p in main_product_prices if lo<=p<=hi]
    else:
        filtered = main_product_prices
    if not filtered:
        filtered = main_product_prices

    filtered.sort()
    filtered_count = len(filtered)
    avg_price = sum(filtered) // filtered_count
    median_price = median(filtered)
    market_price = median_price

    logger.info(
        "Calculated market price: market_price=%s avg_price=%s median_price=%s "
        "count=%s raw_count=%s",
        market_price,
        avg_price,
        median_price,
        filtered_count,
        raw_count,
    )
    return {
        "market_price": market_price,
        "avg_price": avg_price,
        "median_price": median_price,
        "count": filtered_count,
        "raw_count": raw_count,
        "raw_avg_price": raw_avg_price,
        "raw_median_price": raw_median_price,
        "raw_min_price": raw_min_price,
        "raw_max_price": raw_max_price,
        "market_price_suspicious": False,
        "price_filter": price_filter,
    }

def execute_workflow(kw: str, ac: int, cc: int, force: bool, source_model: Optional[Dict] = None) -> Dict:
    global _start_time
    _start_time = time.time()
    result = {"keyword":kw}
    
    try:
        # Step 1: 抓取已结束商品
        check_limits()
        logger.info(f"Step 1: Scraping closed auctions for '{kw}'")
        closed_ids = scrape_closed(kw, cc, force, source_model)
        result["closed"] = len(closed_ids)
        if not closed_ids:
            logger.warning("No closed items found")
            return {**result,"status":"NO_CLOSED"}
        
        # Step 2: AI 解析已结束商品
        logger.info(f"Step 2: Loading closed records for AI parsing")
        closed_items = []
        for cid in closed_ids:
            item = get_record(closed_db, cid)
            if item:
                closed_items.append(item)
        
        logger.info(f"Closed records loaded: {len(closed_items)}")
        
        closed_items = [
            i for i in closed_items
            if i and (force or i.get("modelStatus") == Status.PENDING)
        ]
        
        logger.info(f"Closed records pending parse: {len(closed_items)}")
        
        if closed_items:
            logger.info(f"Start closed AI parse: {len(closed_items)} items")
            closed_result = batch_parse(
                closed_db, closed_items, build_closed_parse_prompt, SIMPLE_BATCH,
                SIMPLE_MAX_TOKENS, saver=save_closed_model,
                resolver=resolve_closed_without_ai,
            )
            result["closed_parsed"] = closed_result
            logger.info(f"Closed parse result: {closed_result}")
        else:
            logger.info("No closed items need parsing (all already processed or not in PENDING state)")
        
        # Step 3: 计算已结束商品市场价和 active 商品价格上限
        logger.info("Step 3: Calculating market price")
        pi = calc_market_price(closed_ids)
        market_price = pi.get("market_price", 0)
        max_active_price = (
            int(Decimal(market_price) * ACTIVE_MAX_RATIO)
            if market_price > 0 else 0
        )
        result["market_price"] = market_price
        result["avg_price"] = pi.get("avg_price", 0)
        result["median_price"] = pi.get("median_price", 0)
        result["market_price_count"] = pi.get("count", 0)
        result["raw_price_count"] = pi.get("raw_count", 0)
        result["raw_avg_price"] = pi.get("raw_avg_price", 0)
        result["raw_median_price"] = pi.get("raw_median_price", 0)
        result["raw_min_price"] = pi.get("raw_min_price", 0)
        result["raw_max_price"] = pi.get("raw_max_price", 0)
        result["price_filter"] = pi.get("price_filter", {})
        result["market_price_suspicious"] = bool(pi.get("market_price_suspicious", False))
        result["active_max_ratio"] = str(ACTIVE_MAX_RATIO)
        result["max_active_price"] = max_active_price

        if result["market_price_suspicious"]:
            logger.warning("Market price suspicious; skip active scraping")
            return {**result, "status": "MARKET_PRICE_SUSPICIOUS"}
        if market_price <= 0:
            logger.warning("No valid market price; skip active scraping")
            return {**result, "status": "NO_MARKET_PRICE"}
        
        # Step 4: 抓取活跃商品
        logger.info(
            "Step 4: Scraping active auctions (market_price=%s, "
            "max_active_price=%s, ratio=%s)",
            market_price,
            max_active_price,
            ACTIVE_MAX_RATIO,
        )
        active_ids = scrape_active(kw, ac, max_active_price, force, source_model)
        result["active"] = len(active_ids)
        if not active_ids:
            logger.warning("No active items found")
            return {**result,"status":"NO_ACTIVE"}
        
        # Step 5: AI 解析活跃商品
        logger.info(f"Step 5: Loading active records for AI parsing")
        active_items = []
        for aid in active_ids:
            item = get_record(active_db, aid)
            if item:
                active_items.append(item)
        
        logger.info(f"Active records loaded: {len(active_items)}")
        
        active_items = [
            i for i in active_items
            if i and (force or i.get("modelStatus") == Status.PENDING)
        ]
        
        logger.info(f"Active records pending parse: {len(active_items)}")
        
        if active_items:
            logger.info(f"Start active AI parse: {len(active_items)} items")
            active_result = batch_parse(
                active_db, active_items, build_active_parse_prompt, SIMPLE_BATCH,
                SIMPLE_MAX_TOKENS, saver=save_active_model,
            )
            result["active_parsed"] = active_result
            logger.info(f"Active parse result: {active_result}")
        else:
            logger.info("No active items need parsing (all already processed or not in PENDING state)")
        
        # Step 6: 构建已结束商品索引
        logger.info("Step 6: Building pricing index")
        idx = build_index(set(closed_ids))
        result["index_size"] = len(idx)
        
        # Step 7: 对每个活跃商品进行定价
        logger.info(f"Step 7: Pricing {len(active_ids)} active items")
        priced = 0
        description_recheck_ids = []
        for aid in active_ids:
            try:
                check_limits()
                item = get_record(active_db, aid)

                if not item or not has_usable_model(item):
                    continue
                
                # 只处理待定价的商品
                if not force and item.get("pricingStatus") != Status.PENDING:
                    continue

                # 初步定价只写 active 表，必须等详情复核后才同步推荐库。
                pricing = price_active_item(aid, idx, sync_candidate=False)
                if not pricing:
                    continue
                priced += 1

                if should_reanalyze_description(item, pricing):
                    description_recheck_ids.append(aid)
                    logger.info(
                        "Active item queued for detail recheck: %s recommendation=%s net_profit=%s",
                        aid,
                        calc_decision(
                            sd(pricing.get("netProfitAtCurrentBid", 0)),
                            sd(pricing.get("profitMarginAtCurrentBid", 0)),
                        ),
                        pricing.get("netProfitAtCurrentBid", 0),
                    )
                
            except RuntimeError:
                raise
            except Exception as e:
                logger.error(f"Pricing {aid}: {e}")

        # Step 8: 所有 BUY_CANDIDATE/REVIEW 商品必须使用详情二次分析
        detail_scraped = 0
        reanalyzed = 0
        repriced = 0
        if description_recheck_ids:
            logger.info(
                "Step 8: On-demand detail scrape for %s candidate/review active items",
                len(description_recheck_ids),
            )
            recheck_items = []
            for index, aid in enumerate(description_recheck_ids):
                check_limits()
                existing = get_record(active_db, aid)
                if (
                    existing
                    and existing.get("detailScrapeStatus") == "COMPLETED"
                    and str(existing.get("detailDescription", "")).strip()
                ):
                    detail_item = existing
                    logger.info("Reusing existing active detail: itemID=%s", aid)
                else:
                    detail_item = scrape_profitable_active_detail(aid)
                    if detail_item and str(detail_item.get("detailDescription", "")).strip():
                        detail_scraped += 1
                if detail_item and str(detail_item.get("detailDescription", "")).strip():
                    pricing_result = detail_item.get("pricingResult") or {}
                    detail_item["closedReferenceSamples"] = build_closed_reference_samples(
                        pricing_result, limit=10
                    )
                    recheck_items.append(detail_item)
                if index < len(description_recheck_ids) - 1:
                    time.sleep(_env("DETAIL_REQUEST_INTERVAL", 0.3, float))

            if recheck_items:
                logger.info(
                    "Step 9: Description AI reanalysis for %s active items",
                    len(recheck_items),
                )
                reanalysis_result = batch_parse(
                    active_db,
                    recheck_items,
                    build_description_parse_prompt,
                    DETAIL_BATCH,
                    DETAIL_MAX_TOKENS,
                )
                result["active_description_reanalysis"] = reanalysis_result
                reanalyzed = (
                    reanalysis_result.get("parsed", 0)
                    + reanalysis_result.get("review", 0)
                    + reanalysis_result.get("excluded", 0)
                )

            # 使用详情分析后的最新记录重新计算利润，最终结果才同步推荐库。
            for item in recheck_items:
                aid = str(item.get("itemID", ""))
                if not aid:
                    continue
                try:
                    check_limits()
                    item_after = get_record(active_db, aid)
                    if not item_after or not has_usable_model(item_after):
                        update_record(active_db, aid, {
                            "purchaseRecommendation": Recommendation.AVOID,
                            "pricingStatus": Status.NOT_APPLICABLE,
                        })
                        deactivate_buy_candidate(aid, "DETAIL_REANALYSIS_EXCLUDED")
                        logger.info(
                            "Detail reanalysis excluded active item: itemID=%s listingType=%s",
                            aid, (item_after or {}).get("listingType", "UNKNOWN"),
                        )
                        continue
                    if price_active_item(aid, idx, sync_candidate=True):
                        repriced += 1
                except RuntimeError:
                    raise
                except Exception as e:
                    logger.error(f"Repricing after description analysis {aid}: {e}")
        
        result["priced"] = priced
        result["profitable_detail_scraped"] = detail_scraped
        result["description_reanalyzed"] = reanalyzed
        result["description_repriced"] = repriced
        result["status"] = "COMPLETED"
        result["elapsed"] = round(time.time() - _start_time, 1)
        
        logger.info(f"Workflow completed: {result}")
        return result
        
    except RuntimeError as e:
        logger.warning(f"Workflow interrupted: {e}")
        return {**result, "status": "INTERRUPTED", "reason": str(e)}
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {**result, "status": "FAILED", "error": str(e)}

# ======================================
# Lambda Handler
# ======================================

def lambda_handler(event, context):
    global _total_tokens, _start_time
    _total_tokens = 0
    _start_time = time.time()
    
    try:
        ac = max(1, min(int(event.get("active_count", 100)), 100))
        cc_val = max(1, min(int(event.get("closed_count", 100)), 100))
        force = str(event.get("force_reprocess", "")).lower() in ("true", "1", "yes")
        mode = norm(event.get("mode", "")).lower()
        category_id = norm(event.get("category_id", ""))
        kw = norm(event.get("keyword", ""))

        if mode == "countdown":
            if not category_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "倒计时模式需要 category_id"}, ensure_ascii=False),
                }
            result = execute_countdown_workflow(category_id, ac, cc_val, force)
            return {
                "statusCode": 200,
                "body": json.dumps(result, ensure_ascii=False, default=str),
            }
        if not kw:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "常规模式需要 keyword"}, ensure_ascii=False),
            }
        
        logger.info(f"Starting workflow: kw={kw}, active={ac}, closed={cc_val}, force={force}")
        aliases = event.get("aliases") or event.get("alias") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        source_model = {
            "brand": norm(event.get("brand", "")),
            "model": norm(event.get("model", "")),
            "aliases": [norm(alias) for alias in aliases if norm(alias)],
        }
        if norm(event.get("category", "")):
            source_model["category"] = norm(event.get("category", ""))
        if norm(event.get("category_id", "")):
            source_model["category_id"] = norm(event.get("category_id", ""))
        if not source_model["brand"] or not source_model["model"]:
            # 兼容直接调用：keyword 通常就是 "brand model"，但无法可靠拆分时
            # 仍保留空 sourceModel，由 Closed AI 返回空 models。
            source_model = {}
        result = execute_workflow(kw, ac, cc_val, force, source_model)

        product_pk = event.get("product_pk")
        if event.get("source") == "catalog_scanner" and isinstance(product_pk, str) and product_pk.strip():
            final_status = "COMPLETED" if result.get("status") == "COMPLETED" else "FAILED"
            try:
                product_catalog_db.update_item(
                    Key={"PK": product_pk.strip(), "SK": "META"},
                    UpdateExpression="SET last_analysis_status = :status",
                    ExpressionAttributeValues={":status": final_status},
                )
                logger.info(
                    "Updated ProductCatalog analysis status: product_pk=%s status=%s",
                    product_pk.strip(),
                    final_status,
                )
            except Exception as e:
                logger.error(
                    "Failed to update ProductCatalog analysis status: product_pk=%s status=%s error=%s",
                    product_pk.strip(),
                    final_status,
                    e,
                    exc_info=True,
                )
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False, default=str)
        }
    except Exception as e:
        logger.error(f"Handler: {e}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
