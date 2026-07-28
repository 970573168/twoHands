"""
Yahoo Auction 商品分析工作流 Lambda
三层决策流：程序估价 → AI重解析 → 人工审核
开放参数限制 + 多级降级匹配
"""

import os
import re
import json
import time
import random
import logging
import urllib.request
import urllib.error
import socket
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Any, Set, Tuple, Union
from collections import OrderedDict

import boto3
from yahoo_auction_scraper import scrape_auctions

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ======================================
# Constants
# ======================================

class Status:
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXCLUDED = "EXCLUDED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    RUNNING = "RUNNING"
    NOT_RUN = "NOT_RUN"

class ListingType:
    MAIN_PRODUCT = "MAIN_PRODUCT"
    ACCESSORY = "ACCESSORY"
    PARTS = "PARTS"
    BROKEN = "BROKEN"
    BOX_ONLY = "BOX_ONLY"
    BUNDLE = "BUNDLE"
    UNKNOWN = "UNKNOWN"

EXCLUDED_TYPES = {ListingType.ACCESSORY, ListingType.PARTS, ListingType.BROKEN, ListingType.BOX_ONLY, ListingType.BUNDLE, ListingType.UNKNOWN}

class Recommendation:
    BUY = "BUY"
    REVIEW = "REVIEW"
    NO = "NO"
    AI_RECHECK = "AI_RECHECK"
    MANUAL_REVIEW = "MANUAL_REVIEW"

NON_CRITICAL_FIELDS = {"variant", "color", "カラー", "色", "carrier", "キャリア", "通信事業者", "screen_size", "画面サイズ", "battery", "バッテリー", "graphics_card", "グラフィックス", "os", "operating_system", "OS", "processor", "プロセッサー", "cpu", "CPU", "compatibility", "互換性", "ram", "メモリ", "memory"}

CRITICAL_PARAM_PENALTIES = {"brand": Decimal("0.20"), "model": Decimal("0.30"), "storage": Decimal("0.10"), "other": Decimal("0.05")}

MODEL_FAMILY_SUFFIXES = [" RECON", " RECON LT", " BY", " CS MID", " CS", " MID", " LOW", " HIGH", " PRIMEKNIT", " PRIME KNIT", " PRIME", " PK", " PRO MAX", " PRO", " MAX", " PLUS", " ULTRA", " LITE", " FE", " ELITE", " ELITEBOOK", " PROBOOK", " GEN10", " GEN9", " GEN8", " G10", " G9", " G8", " LIMITED EDITION", " LIMITED", " LE", " SE", " SPECIAL EDITION", " ANNIVERSARY", " OG", " 2023", " 2024", " 2025"]

SHIPPING_FREE_KEYWORDS = ["送料無料", "送料込み", "送料込", "送料無", "送料0", "送料ゼロ", "free shipping", "shipping free", "shipping included", "free", "0円", "出品者負担"]

# ======================================
# Config
# ======================================

def _env(key, default, cast=str):
    v = os.getenv(key, "")
    if not v: return default
    try: return cast(v)
    except: return default

ENVIRONMENT = _env("ENVIRONMENT", "dev")
TABLE_ACTIVE = _env("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_CLOSED = _env("TABLE_NAME_CLOSED", "YahooAuctionItems")
PRODUCT_TABLE = _env("PRODUCT_TABLE_NAME", "ProductCatalog-dev")

AI_MODE = _env("AI_MODE", "doubao")
AI_CONFIGS = {
    "gemini": {"name": "gemini", "type": "gemini", "url": _env("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-latest:generateContent"), "model": _env("GEMINI_MODEL", "gemini-2.0-flash-latest"), "timeout": _env("GEMINI_TIMEOUT", 60, int), "max_tokens": _env("GEMINI_MAX_TOKENS", 4000, int)},
    "doubao": {"name": "doubao", "type": "openai_compatible", "url": _env("DOUBAO_URL", "https://ws-8lxmxlbemcgcus5u.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions"), "model": _env("DOUBAO_MODEL", "qwen-plus-character"), "timeout": _env("DOUBAO_TIMEOUT", 90, int), "max_tokens": _env("DOUBAO_MAX_TOKENS", 6000, int)},
    "openai": {"name": "openai", "type": "openai_compatible", "url": _env("OPENAI_URL", "https://api.openai.com/v1/chat/completions"), "model": _env("OPENAI_MODEL", "gpt-4o-mini"), "timeout": _env("OPENAI_TIMEOUT", 60, int), "max_tokens": _env("OPENAI_MAX_TOKENS", 4000, int)},
}

# 为各AI配置添加API Key
for mode in AI_CONFIGS:
    AI_CONFIGS[mode]["key"] = _env(f"{mode.upper()}_API_KEY", "")

BUY_MARGIN = _env("BUY_MARGIN_THRESHOLD", Decimal("0.20"), Decimal)
REVIEW_MARGIN = _env("REVIEW_MARGIN_THRESHOLD", Decimal("0.10"), Decimal)
MIN_COMPARABLE = _env("MIN_COMPARABLE_COUNT", 3, int)
HIGH_CONFIDENCE_COUNT = _env("HIGH_CONFIDENCE_COMPARABLE_COUNT", 10, int)
MEDIUM_CONFIDENCE_COUNT = _env("MEDIUM_CONFIDENCE_COMPARABLE_COUNT", 5, int)
PRICE_MIN_RATIO = _env("ACTIVE_PRICE_MIN_RATIO", Decimal("0.5"), Decimal)
MIN_ROI = _env("POTENTIAL_OPPORTUNITY_MIN_ROI", Decimal("0.15"), Decimal)
FEE_RATE = _env("EXPECTED_SELLING_FEE_RATE", Decimal("0.10"), Decimal)
SHIPPING_COST = _env("DEFAULT_SHIPPING_COST", Decimal("1500"), Decimal)
REPAIR_RESERVE = _env("DEFAULT_REPAIR_RESERVE_RATE", Decimal("0.05"), Decimal)
RISK_RESERVE = _env("RISK_RESERVE_RATE", Decimal("0.03"), Decimal)
MAX_PRICE_DEV = _env("MAX_PRICE_DEVIATION", Decimal("1.5"), Decimal)

MODEL_BATCH = _env("MODEL_PARSE_BATCH_SIZE", 100, int)
CLOSED_BATCH = _env("CLOSED_PARSE_BATCH_SIZE", 100, int)
AI_TIMEOUT = _env("AI_REQUEST_TIMEOUT", 90, int)
AI_RETRIES = _env("AI_MAX_RETRIES", 3, int)
MAX_TOKENS = _env("MAX_TOTAL_TOKENS", 50000, int)
LAMBDA_TIMEOUT = _env("LAMBDA_TIMEOUT_SECONDS", 840, int)
TIMEOUT_BUFFER = _env("LAMBDA_TIMEOUT_BUFFER", 30, int)
REQ_INTERVAL = _env("REQUEST_INTERVAL", 1.0, float)
DETAIL_LAMBDA = _env("DETAIL_ANALYZER_LAMBDA", "YahooAuctionDetailAnalyzer")
ENABLE_DETAIL = _env("ENABLE_DETAIL_REPARSE", True, lambda x: x.lower() in ("true", "1", "yes"))
ENABLE_FALLBACK = _env("FALLBACK_MATCH_ENABLED", True, lambda x: x.lower() in ("true", "1", "yes"))
ENABLE_FAMILY = _env("FAMILY_MATCH_ENABLED", True, lambda x: x.lower() in ("true", "1", "yes"))
AI_COOLDOWN = _env("AI_FAILOVER_COOLDOWN", 300, int)

# ======================================
# DynamoDB & AWS Clients
# ======================================

dynamodb = boto3.resource("dynamodb")
active_db = dynamodb.Table(TABLE_ACTIVE)
closed_db = dynamodb.Table(TABLE_CLOSED)
product_db = dynamodb.Table(PRODUCT_TABLE)
secrets = boto3.client("secretsmanager")
lambda_client = boto3.client("lambda")

_total_tokens = 0
_start_time = None
_ai_state = {"failed_modes": {}}

# ======================================
# Repository Layer
# ======================================

def update_record(table, item_id: str, fields: Dict, key_name: str = "itemID"):
    """统一的DynamoDB更新操作"""
    parts = []
    values = {}
    names = {}
    
    for k, v in fields.items():
        key = f":{k}"
        parts.append(f"{k} = {key}")
        values[key] = _to_dynamo(v)
    
    # 处理保留字
    for reserved in ("url", "ttl"):
        if reserved in fields:
            names[f"#{reserved}"] = reserved
            parts = [p.replace(f"{reserved} =", f"#{reserved} =") for p in parts]
    
    try:
        table.update_item(
            Key={key_name: str(item_id)},
            UpdateExpression="SET " + ", ".join(parts),
            ExpressionAttributeNames=names if names else None,
            ExpressionAttributeValues=values
        )
    except Exception as e:
        logger.error(f"更新 {table.name} {item_id} 失败: {e}")
        raise

def get_record(table, item_id: str, key_name: str = "itemID") -> Optional[Dict]:
    """统一的DynamoDB读取操作"""
    try:
        result = table.get_item(Key={key_name: str(item_id)})
        return result.get("Item")
    except Exception as e:
        logger.error(f"读取 {table.name} {item_id} 失败: {e}")
        return None

def _to_dynamo(v):
    if isinstance(v, float): return Decimal(str(v))
    if isinstance(v, Decimal): return v
    if isinstance(v, dict): return {str(k): _to_dynamo(i) for k, i in v.items()}
    if isinstance(v, (list, tuple)): return [_to_dynamo(i) for i in v]
    if isinstance(v, set): return {str(i) for i in v if str(i)}
    return v

# ======================================
# Helper Functions
# ======================================

def safe_decimal(v, default=Decimal("0")) -> Decimal:
    try: return v if isinstance(v, Decimal) else Decimal(str(v))
    except: return default

def safe_int(v, default=0) -> int:
    try: return int(v)
    except: return default

def normalize(text: str) -> str:
    if not text: return ""
    text = str(text).strip()
    text = text.translate(str.maketrans("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    return re.sub(r"\s+", " ", text)

def normalize_storage(val) -> str:
    if not val: return ""
    text = normalize(str(val)).upper()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(GB|G|TB|T)", text)
    if m: return f"{m.group(1)}{'GB' if m.group(2) in ('G','GB') else 'TB'}"
    
    parts = []
    for amt, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(GB|TB|G|T)", text):
        parts.append(f"{amt}{'GB' if unit in ('G','GB') else 'TB'}")
    if parts: return " ".join(parts)
    
    ram = re.search(r'(?:RAM|メモリ)\s*(\d+)\s*GB', text)
    ssd = re.search(r'(?:SSD|M\.2\s*SSD)\s*(\d+)\s*GB', text)
    hdd = re.search(r'(?:HDD)\s*(\d+)\s*(?:GB|TB)', text)
    parts = []
    if ram: parts.append(f"RAM{ram.group(1)}GB")
    if ssd: parts.append(f"SSD{ssd.group(1)}GB")
    if hdd: parts.append(f"HDD{hdd.group(1)}{'TB' if 'TB' in text else 'GB'}")
    return " ".join(parts) if parts else text

def extract_model_family(model: str) -> str:
    if not model: return ""
    n = normalize(model).upper()
    for suffix in MODEL_FAMILY_SUFFIXES:
        if n.endswith(suffix):
            f = n[:-len(suffix)].strip()
            if len(f) >= 3: return f
    words = n.split()
    return " ".join(words[:3]) if len(words) >= 4 else (" ".join(words[:2]) if len(words) >= 3 else n)

def generate_key(brand, model, storage="", variant=""):
    b = normalize(brand).upper() if brand else "UNKNOWN"
    m = normalize(model).upper() if model else "UNKNOWN"
    s = normalize_storage(storage)
    parts = [b, m]
    if s: parts.append(s)
    return re.sub(r"[^A-Z0-9\s+\-/]", " ", " ".join(parts)).strip()

def generate_fallback_key(brand, model, storage=""):
    b = normalize(brand).upper() if brand else "UNKNOWN"
    m = normalize(model).upper() if model else "UNKNOWN"
    s = normalize_storage(storage)
    family = extract_model_family(m)
    base = re.sub(r"[^A-Z0-9\s+\-/]", " ", f"{b} {family}").strip()
    full = re.sub(r"[^A-Z0-9\s+\-/]", " ", f"{b} {m}" + (f" {s}" if s else "")).strip()
    if base == full or base == f"{b} {m}":
        if s:
            no_s = re.sub(r"[^A-Z0-9\s+\-/]", " ", f"{b} {m}").strip()
            return no_s if no_s != full else ""
        return ""
    return base

def shipping_info(text: str) -> Dict:
    if not text or not text.strip(): return {"free": False, "status": "UNKNOWN"}
    t = text.strip().lower()
    for kw in SHIPPING_FREE_KEYWORDS:
        if kw.lower() in t: return {"free": True, "status": "FREE"}
    return {"free": False, "status": "CHARGED"}

def get_shipping_cost(item: Dict) -> Decimal:
    if item.get("shippingStatus") == "FREE": return Decimal("0")
    fee = item.get("shippingFee")
    return safe_decimal(fee, SHIPPING_COST) if fee is not None else SHIPPING_COST

def check_limits():
    if _total_tokens >= MAX_TOKENS:
        raise RuntimeError(f"Token limit: {_total_tokens}/{MAX_TOKENS}")
    elapsed = 0 if _start_time is None else time.time() - _start_time
    if LAMBDA_TIMEOUT - elapsed - TIMEOUT_BUFFER <= 0:
        raise RuntimeError(f"Timeout: {elapsed:.1f}s")

# ======================================
# AI Service
# ======================================

def _get_ai_key(mode: str) -> str:
    env = ENVIRONMENT
    names = [f"{mode}-api-key-{env}", f"{mode}-api-key", f"{mode}/api-key/{env}"]
    for name in names:
        try:
            resp = secrets.get_secret_value(SecretId=name)
            s = resp.get("SecretString", "")
            if not s: continue
            try:
                d = json.loads(s)
                k = d.get("apiKey") or d.get("api_key") or d.get("key") or d.get(f"{mode.upper()}_API_KEY") or ""
            except:
                k = s.strip()
            if k: return k
        except: pass
    return ""

def get_ai_config() -> Optional[Dict]:
    order = [AI_MODE] + [m for m in ["gemini", "doubao", "openai"] if m != AI_MODE]
    now = time.time()
    for mode in order:
        if mode in _ai_state["failed_modes"]:
            if now - _ai_state["failed_modes"][mode] < AI_COOLDOWN: continue
            del _ai_state["failed_modes"][mode]
        cfg = AI_CONFIGS.get(mode, {})
        key = cfg.get("key") or _get_ai_key(mode)
        if key:
            cfg["key"] = key
            return cfg
    return None

def _build_gemini_body(prompt: str, cfg: Dict) -> Dict:
    return {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.0, "maxOutputTokens": cfg["max_tokens"]}}

def _build_openai_body(prompt: str, cfg: Dict) -> Dict:
    body = {"model": cfg["model"], "messages": [{"role": "system", "content": "あなたは電子製品の専門家です。必ず有効なJSON形式のみを返してください。"}, {"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": cfg["max_tokens"]}
    if cfg["name"] == "doubao": body["response_format"] = {"type": "json_object"}
    return body

def _parse_gemini_response(result: Dict) -> Tuple[str, str]:
    if "candidates" in result and result["candidates"]:
        c = result["candidates"][0]
        fr = c.get("finishReason", "unknown")
        content = "".join(p.get("text", "") for p in c.get("content", {}).get("parts", []))
        return content, fr
    return "", "unknown"

def _parse_openai_response(result: Dict) -> Tuple[str, str]:
    if "choices" in result and result["choices"]:
        c = result["choices"][0]
        return c.get("message", {}).get("content", ""), c.get("finish_reason", "unknown")
    return "", "unknown"

def call_ai(prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    global _total_tokens
    
    for _ in range(3):
        cfg = get_ai_config()
        if not cfg: return None, "ALL_MODES_UNAVAILABLE"
        
        mode = cfg["name"]
        is_gemini = cfg["type"] == "gemini"
        body = _build_gemini_body(prompt, cfg) if is_gemini else _build_openai_body(prompt, cfg)
        url = cfg["url"]
        timeout = cfg["timeout"]
        headers = {"x-goog-api-key": cfg["key"], "Content-Type": "application/json"} if is_gemini else {"Authorization": f"Bearer {cfg['key']}", "Content-Type": "application/json"}
        
        for retry in range(AI_RETRIES):
            try:
                check_limits()
                if (LAMBDA_TIMEOUT - (time.time() - _start_time) - TIMEOUT_BUFFER) < timeout + 10:
                    raise RuntimeError("Insufficient time")
                
                req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                
                usage = result.get("usageMetadata", {}) or result.get("usage", {})
                _total_tokens += usage.get("total_tokens", usage.get("totalTokenCount", 0))
                
                content, fr = _parse_gemini_response(result) if is_gemini else _parse_openai_response(result)
                
                if fr == "SAFETY": return None, "safety_blocked"
                
                parsed = _parse_json(content)
                if parsed is not None: return parsed, fr
                
                logger.warning(f"[{mode}] Empty result, retry {retry+1}")
            except RuntimeError: raise
            except Exception as e:
                logger.error(f"[{mode}] Error: {type(e).__name__}: {str(e)[:100]}")
            
            if retry < AI_RETRIES - 1:
                time.sleep((2 ** retry) + random.uniform(0, 1))
        
        logger.warning(f"[{mode}] All retries failed")
        _ai_state["failed_modes"][mode] = time.time()
    
    return None, "ALL_MODES_EXHAUSTED"

def _parse_json(content: str) -> Optional[Dict]:
    if not content: return None
    content = content.strip()
    
    for parser in [lambda c: json.loads(c), lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", c))]:
        try: return parser(content)
        except: pass
    
    # 栈匹配提取第一个完整JSON
    for bracket in ('{', '['):
        depth = 0
        start = -1
        for i, ch in enumerate(content):
            if ch == bracket:
                if depth == 0: start = i
                depth += 1
            elif ch == ('}' if bracket == '{' else ']'):
                depth -= 1
                if depth == 0 and start >= 0:
                    try: return json.loads(content[start:i+1])
                    except: break
    return None

# ======================================
# Prompt Templates
# ======================================

PARSE_RULES = """ルール：
1. スマホはPro/Pro Maxを区別し、容量はstorageに
2. PCはシリーズ/世代を区別し、メモリと容量はstorageに
3. 価格に影響するスペックが不足する場合、missingに不足項目名を列挙
4. タイトルに明記されていない情報は推測しない
5. アクセサリ、部品、故障品、空箱、セットは対応するlistingTypeで
6. modelはPro/Pro Maxを区別し、省略しない
7. JSONのみを出力し、説明文は一切不要"""

OUTPUT_FORMAT = """{{"items":[{{"itemId":"ID","brand":"ブランド","model":"完全なモデル名","variant":"バリエーションまたは空","storage":"容量または空","listingType":"MAIN_PRODUCT","condition":"USED","missing":[],"confidence":0.95}}]}}
listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN"""

def build_parse_prompt(items: List[Dict]) -> str:
    return f"""あなたは中古電子製品の識別専門家です。
以下の商品タイトルを解析し、モデルと主要スペックを返してください。

入力：
{json.dumps(items, ensure_ascii=False, separators=(",", ":"))}

以下のJSON形式のみを返してください。全ての入力IDを含めてください：
{OUTPUT_FORMAT}

{PARSE_RULES}"""

def build_detail_prompt(item_id: str, title: str, desc: str, spec: str) -> str:
    data = {"itemId": item_id, "title": title, "description": (desc or "")[:2000], "specification": (spec or "")[:2000]}
    example = {"itemId": item_id, "brand": "ブランド名", "model": "完全なモデル名", "variant": "", "storage": "", "listingType": "MAIN_PRODUCT", "condition": "USED", "missing": [], "confidence": 0.95}
    
    return f"""あなたは中古電子製品の識別専門家です。商品説明と仕様を参考に、より正確なモデルを特定してください。

【入力】
{json.dumps(data, ensure_ascii=False, indent=2)}

【出力形式】
{json.dumps({"items": [example]}, ensure_ascii=False, indent=2)}

【注意】
1. 商品説明から型番やスペックを抽出
2. タイトルにない情報も説明文から補完
3. スマホはPro/Pro Maxを区別、容量はstorageに
4. PCはシリーズ/世代を区別
5. 靴のサイズ(cm)はvariantに
6. 推測不可情報はmissingに追加
7. JSONのみ出力"""

# ======================================
# Model Parser
# ======================================

def parse_ai_result(parsed: Dict) -> Tuple[List[Dict], str, str, int, str]:
    """解析AI返回结果，返回(models, listing_type, condition, missing_count, exclusion_reason)"""
    brand = normalize(parsed.get("brand", ""))
    model = normalize(parsed.get("model", ""))
    variant = normalize(parsed.get("variant", ""))
    storage = normalize_storage(parsed.get("storage", ""))
    confidence = safe_decimal(parsed.get("confidence", 0))
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    condition = normalize(parsed.get("condition", "UNKNOWN")).upper()
    missing = [m for m in (parsed.get("missing") or []) if m.lower() not in NON_CRITICAL_FIELDS]
    
    has_brand = bool(brand)
    has_model = bool(model)
    is_unknown = model.upper() in ("UNKNOWN", "不明", "N/A", "")
    
    missing_count = 0
    if not has_brand:
        if "brand" not in [m.lower() for m in missing]: missing.append("brand")
        missing_count += 1
    if not has_model or is_unknown:
        if "model" not in [m.lower() for m in missing]: missing.append("model")
        missing_count += 1
    if not storage: missing_count += 1
    
    identifiable = (has_brand or has_model) and not is_unknown
    
    models = []
    if identifiable:
        b = brand if has_brand else "UNKNOWN"
        m = model if has_model else "UNKNOWN"
        pk = generate_key(b, m, storage)
        fk = generate_fallback_key(b, m, storage)
        if not fk or fk == pk: fk = ""
        fm = extract_model_family(m.upper()) if has_model else ""
        
        models.append({"brand": b, "model": m, "familyModel": fm if fm != m.upper() else "", "variant": variant, "storage": storage, "pricingModelKey": pk, "fallbackPricingKey": fk, "confidence": str(confidence), "missingParameterCount": missing_count})
    
    reasons = []
    if listing_type in EXCLUDED_TYPES: reasons.append(f"商品タイプ不適: {listing_type}")
    if condition == "BROKEN": reasons.append("故障品")
    
    return models, listing_type, condition, missing_count, "; ".join(reasons)

def save_model(table, item_id: str, parsed: Dict) -> str:
    """保存模型解析结果，返回状态"""
    models, listing_type, condition, missing_count, exclusion = parse_ai_result(parsed)
    
    excluded = listing_type in EXCLUDED_TYPES
    is_broken = condition == "BROKEN"
    low_conf = any(safe_decimal(m.get("confidence", 0)) < Decimal("0.7") for m in models)
    
    if not models: status = Status.REVIEW_REQUIRED
    elif excluded or is_broken: status = Status.EXCLUDED
    elif low_conf: status = Status.REVIEW_REQUIRED
    else: status = Status.COMPLETED
    
    eligible = not excluded and not is_broken and len(models) > 0
    
    update_record(table, item_id, {
        "models": models, "modelStatus": status, "listingType": listing_type,
        "missingParameterCount": missing_count, "missingCriticalParameters": [m for m in (parsed.get("missing") or []) if m.lower() not in NON_CRITICAL_FIELDS],
        "isComparable": eligible, "parsedCondition": condition, "exclusionReason": exclusion,
        "modelParsedAt": datetime.now(timezone.utc).isoformat(),
        "pricingStatus": Status.PENDING if eligible else Status.NOT_APPLICABLE,
        "isAnalysisEligible": eligible,
        "hasAllCriticalParameters": len(models) > 0
    })
    return status

def mark_model_failed(table, item_id: str, error: str):
    update_record(table, item_id, {"modelStatus": Status.FAILED, "modelError": error[:500], "modelParsedAt": datetime.now(timezone.utc).isoformat()})

def batch_parse(table, items: List[Dict], prompt_builder, batch_size: int) -> Dict:
    """统一的批量解析"""
    if not items: return {"parsed": 0, "excluded": 0, "review": 0, "failed": 0, "errors": []}
    
    totals = {"parsed": 0, "excluded": 0, "review": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        n = start // batch_size + 1
        
        prompt = prompt_builder([{"itemId": str(i["itemID"]), "title": i.get("title", "")} for i in batch])
        result, err = call_ai(prompt)
        
        if not result:
            for item in batch: mark_model_failed(table, str(item["itemID"]), err or "AI_EMPTY")
            totals["failed"] += len(batch)
            totals["errors"].append(f"Batch {n} AI failed: {err}")
            continue
        
        parsed = result.get("items", [])
        if not isinstance(parsed, list): parsed = []
        
        returned = set()
        for p in parsed:
            if not isinstance(p, dict): continue
            iid = str(p.get("itemId", "")).strip()
            if not iid: continue
            returned.add(iid)
            
            s = save_model(table, iid, p)
            if s == Status.COMPLETED: totals["parsed"] += 1
            elif s == Status.EXCLUDED: totals["excluded"] += 1
            elif s == Status.REVIEW_REQUIRED: totals["review"] += 1
            else: totals["failed"] += 1
        
        missing = {str(i["itemID"]) for i in batch} - returned
        for mid in missing:
            mark_model_failed(table, mid, "AI_NOT_RETURNED")
            totals["failed"] += 1
        
        if start + batch_size < len(items): time.sleep(REQ_INTERVAL)
    
    return totals

# ======================================
# Matching Engine
# ======================================

def build_comparable_index(closed_ids: Set[str]) -> Dict[str, List[Dict]]:
    """构建可比较索引，支持精确/降级/家族匹配"""
    idx = {}
    excluded = 0
    
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus") != Status.COMPLETED: continue
        if item.get("listingType") != ListingType.MAIN_PRODUCT: continue
        if item.get("parsedCondition") == "BROKEN": continue
        if safe_decimal(item.get("price", 0)) <= 0: continue
        
        models = item.get("models", [])
        if isinstance(models, str):
            try: models = json.loads(models)
            except: continue
        
        keys = set()
        for m in models:
            if not isinstance(m, dict): continue
            mn = normalize(m.get("model", "")).upper()
            if mn in ("UNKNOWN", "不明", "N/A", ""): excluded += 1; continue
            
            # 精确匹配
            pk = normalize(m.get("pricingModelKey", "")).upper()
            if pk and pk not in keys:
                keys.add(pk); idx.setdefault(pk, []).append(item)
            
            # 降级匹配
            if ENABLE_FALLBACK:
                fk = normalize(m.get("fallbackPricingKey", "")).upper()
                if fk and fk != pk:
                    fq = f"FB:{fk}"
                    if fq not in keys: keys.add(fq); idx.setdefault(fq, []).append(item)
            
            # 家族匹配
            if ENABLE_FAMILY:
                fm = normalize(m.get("familyModel", "")).upper()
                if fm and fm != mn:
                    b = normalize(m.get("brand", "")).upper()
                    if b:
                        fam = re.sub(r"[^A-Z0-9\s+\-/]", " ", f"{b} {fm}").strip()
                        fq = f"FAM:{fam}"
                        if fq not in keys: keys.add(fq); idx.setdefault(fq, []).append(item)
    
    if excluded: logger.warning(f"Excluded {excluded} UNKNOWN models")
    for k, v in idx.items(): v.sort(key=lambda x: x.get("endTime", ""), reverse=True)
    return idx

def find_comparable(active_item: Dict, idx: Dict[str, List[Dict]]) -> Tuple[List[Dict], Dict]:
    """查找可比较商品，支持多级降级"""
    models = active_item.get("models", [])
    if isinstance(models, str):
        try: models = json.loads(models)
        except: return [], {"level": "ERROR"}
    
    items, seen = [], set()
    exact, fallback, family = 0, 0, 0
    
    for m in models:
        if not isinstance(m, dict): continue
        
        # 精确
        pk = normalize(m.get("pricingModelKey", "")).upper()
        if pk:
            for ci in idx.get(pk, []):
                iid = str(ci.get("itemID", ""))
                if iid and iid not in seen: seen.add(iid); items.append(ci)
            exact = len(items)
        
        # 降级 (数量不足时)
        if len(items) < MIN_COMPARABLE and ENABLE_FALLBACK:
            fk = normalize(m.get("fallbackPricingKey", "")).upper()
            if fk:
                for ci in idx.get(f"FB:{fk}", []):
                    iid = str(ci.get("itemID", ""))
                    if iid and iid not in seen: seen.add(iid); items.append(ci); fallback += 1
        
        # 家族 (仍不足时)
        if len(items) < MIN_COMPARABLE and ENABLE_FAMILY:
            fm = normalize(m.get("familyModel", "")).upper()
            if fm:
                b = normalize(m.get("brand", "")).upper()
                if b:
                    fam = re.sub(r"[^A-Z0-9\s+\-/]", " ", f"{b} {fm}").strip()
                    for ci in idx.get(f"FAM:{fam}", []):
                        iid = str(ci.get("itemID", ""))
                        if iid and iid not in seen: seen.add(iid); items.append(ci); family += 1
    
    items.sort(key=lambda x: x.get("endTime", ""), reverse=True)
    level = "EXACT" if exact > 0 else ""
    if fallback > 0: level += "+FALLBACK" if level else "FALLBACK"
    if family > 0: level += "+FAMILY" if level else "FAMILY"
    
    return items, {"level": level, "total": len(items), "exact": exact, "fallback": fallback, "family": family}

# ======================================
# Pricing Engine
# ======================================

def calc_stats(items: List[Dict]) -> Dict:
    """计算价格统计"""
    records = []
    for item in items:
        p = safe_decimal(item.get("price", 0))
        if p > 0: records.append({"id": str(item.get("itemID", "")), "price": p})
    
    records.sort(key=lambda r: r["price"])
    prices = [r["price"] for r in records]
    n = len(prices)
    
    base = {"count": n, "prices": [int(p) for p in prices], "ids": [r["id"] for r in records]}
    
    if n < MIN_COMPARABLE:
        if n >= 1:
            mid = prices[n // 2]
            base.update({"filtered_median": int(mid), "filtered_min": int(prices[0]), "filtered_max": int(prices[-1])})
        return {**base, "filtered_count": n, "sufficient": False, "reason": f"Need {MIN_COMPARABLE}, got {n}"}
    
    def pct(data, p):
        if not data: return Decimal("0")
        if len(data) == 1: return data[0]
        pos = Decimal(len(data) - 1) * p
        lo = int(pos)
        return data[lo] + (data[lo+1] - data[lo]) * (pos - Decimal(lo)) if lo + 1 < len(data) else data[lo]
    
    q1, med, q3 = pct(prices, Decimal("0.25")), pct(prices, Decimal("0.5")), pct(prices, Decimal("0.75"))
    iqr = q3 - q1
    lo, hi = q1 - MAX_PRICE_DEV * iqr, q3 + MAX_PRICE_DEV * iqr
    filtered = [r for r in records if lo <= r["price"] <= hi]
    fp = [r["price"] for r in filtered]
    fn = len(fp)
    
    if fn < MIN_COMPARABLE:
        return {**base, "min": int(prices[0]), "max": int(prices[-1]), "q1": int(q1), "median": int(med), "q3": int(q3), "iqr": int(iqr), "lower": int(lo), "upper": int(hi), "filtered_count": fn, "sufficient": False, "reason": f"After outlier removal: {fn} < {MIN_COMPARABLE}", "filtered_median": int(med), "filtered_min": int(prices[0]), "filtered_max": int(prices[-1]), "filtered_prices": [int(p) for p in fp], "ids": [r["id"] for r in filtered]}
    
    fp.sort()
    fmed = pct(fp, Decimal("0.5"))
    favg = sum(fp, Decimal("0")) / Decimal(fn)
    spread = ((max(fp) - min(fp)) / fmed).quantize(Decimal("0.001")) if fmed > 0 else Decimal("0")
    
    return {**base, "min": int(prices[0]), "max": int(prices[-1]), "q1": int(q1), "median": int(med), "q3": int(q3), "iqr": int(iqr), "lower": int(lo), "upper": int(hi), "filtered_count": fn, "excluded_count": n - fn, "sufficient": True, "filtered_min": int(min(fp)), "filtered_max": int(max(fp)), "filtered_median": int(fmed), "filtered_avg": int(favg.quantize(Decimal("1"))), "spread": spread, "filtered_prices": [int(p) for p in fp], "ids": [r["id"] for r in filtered]}

def calc_confidence(stats: Dict, active_item: Dict = None, match_info: Dict = None) -> Decimal:
    """计算可信度"""
    if not stats.get("sufficient"): return Decimal("0.20")
    
    cc = stats["filtered_count"]
    sr = stats.get("spread", Decimal("0"))
    tc = stats["count"]
    ec = stats.get("excluded_count", 0)
    
    conf = Decimal("0.90") if cc >= HIGH_CONFIDENCE_COUNT else (Decimal("0.80") if cc >= MEDIUM_CONFIDENCE_COUNT else Decimal("0.70"))
    if sr >= Decimal("0.5"): conf -= Decimal("0.20")
    elif sr >= Decimal("0.3"): conf -= Decimal("0.10")
    if tc > 0 and Decimal(ec) / Decimal(tc) >= Decimal("0.3"): conf -= Decimal("0.10")
    
    # 参数缺失惩罚
    if active_item:
        missing_list = active_item.get("missingCriticalParameters", [])
        if isinstance(missing_list, str):
            try: missing_list = json.loads(missing_list)
            except: missing_list = []
        
        penalty = Decimal("0")
        for p in missing_list:
            pl = str(p).lower()
            if "brand" in pl: penalty += CRITICAL_PARAM_PENALTIES["brand"]
            elif "model" in pl: penalty += CRITICAL_PARAM_PENALTIES["model"]
            elif "storage" in pl: penalty += CRITICAL_PARAM_PENALTIES["storage"]
            else: penalty += CRITICAL_PARAM_PENALTIES["other"]
        
        if penalty == Decimal("0") and active_item.get("missingParameterCount", 0) > 0:
            penalty = Decimal("0.05") * Decimal(active_item["missingParameterCount"])
        conf -= penalty
    
    # 降级惩罚
    if match_info:
        lvl = match_info.get("level", "")
        if "FAMILY" in lvl: conf -= Decimal("0.20")
        elif "FALLBACK" in lvl: conf -= Decimal("0.10")
    
    return max(Decimal("0.20"), min(Decimal("0.95"), conf)).quantize(Decimal("0.01"))

def calc_risk(item: Dict, stats: Dict, conf: Decimal, margin: Decimal) -> Dict:
    """计算风险评估"""
    score = 0
    factors, reasons = [], []
    cc = stats.get("filtered_count", 0)
    
    mc = safe_int(item.get("missingParameterCount", 0))
    if mc > 0: score += mc * 2; factors.append(f"Missing {mc} params")
    
    if cc < 5: score += 2; factors.append(f"Low samples: {cc}")
    elif cc < 10: score += 1
    else: reasons.append(f"Good samples: {cc}")
    
    if conf < Decimal("0.5"): score += 3
    elif conf < Decimal("0.75"): score += 1
    
    sr = stats.get("spread", Decimal("0"))
    if sr >= Decimal("0.5"): score += 2
    elif sr >= Decimal("0.3"): score += 1
    
    # 卖家评估
    rating = item.get("sellerRating")
    if rating:
        try:
            r = Decimal(str(rating).replace("%", ""))
            if r < Decimal("95"): score += 2; factors.append(f"Low rating: {r}%")
            elif r < Decimal("98"): score += 1
        except: pass
    
    if str(item.get("sellerType", "")).lower() == "personal": score += 1
    
    if margin < Decimal("0"): score += 3
    elif margin < REVIEW_MARGIN: score += 2
    elif margin < BUY_MARGIN: score += 1
    
    level = "HIGH" if score >= 6 else ("MEDIUM" if score >= 3 else "LOW")
    return {"level": level, "score": score, "factors": factors, "reasons": reasons}

def calc_profit(est_price: Decimal, purchase: Decimal, shipping: Decimal) -> Dict:
    """计算利润"""
    fee = (est_price * FEE_RATE).quantize(Decimal("1"))
    repair = (est_price * REPAIR_RESERVE).quantize(Decimal("1"))
    risk = (est_price * RISK_RESERVE).quantize(Decimal("1"))
    total_cost = fee + shipping + repair + risk
    net = est_price - purchase - total_cost
    margin = (net / est_price).quantize(Decimal("0.001")) if est_price > 0 else Decimal("0")
    
    investment = purchase + shipping + repair + risk
    roi = (net / investment).quantize(Decimal("0.001")) if investment > 0 else Decimal("0")
    
    bep = (est_price * (Decimal("1") - FEE_RATE - REPAIR_RESERVE - RISK_RESERVE) - shipping).quantize(Decimal("1"))
    
    return {"net": net, "margin": margin, "roi": roi, "fee": fee, "repair": repair, "risk": risk, "total_cost": total_cost, "bep": max(0, int(bep)), "tp10": max(0, int((est_price * (Decimal("1") - FEE_RATE - REPAIR_RESERVE - RISK_RESERVE - Decimal("0.1")) - shipping).quantize(Decimal("1")))), "tp20": max(0, int((est_price * (Decimal("1") - FEE_RATE - REPAIR_RESERVE - RISK_RESERVE - Decimal("0.2")) - shipping).quantize(Decimal("1"))))}

def calc_decision(net: Decimal, margin: Decimal, roi: Decimal, conf: Decimal, risk_level: str, cc: int, missing: int, status: str) -> str:
    """三层次决策"""
    if status == Status.INSUFFICIENT_DATA:
        return Recommendation.AI_RECHECK if net > 0 and roi >= MIN_ROI else Recommendation.NO
    
    if net <= 0: return Recommendation.NO
    
    if cc < MIN_COMPARABLE:
        return Recommendation.AI_RECHECK if roi >= MIN_ROI else Recommendation.NO
    
    if missing >= 2 and conf < Decimal("0.6"): return Recommendation.AI_RECHECK
    
    if margin >= BUY_MARGIN and risk_level in ("LOW", "MEDIUM") and conf >= Decimal("0.7"):
        return Recommendation.BUY
    elif margin >= REVIEW_MARGIN and conf >= Decimal("0.5"):
        return Recommendation.REVIEW
    elif roi >= MIN_ROI:
        return Recommendation.AI_RECHECK
    
    return Recommendation.NO

def build_pricing_result(item: Dict, stats: Dict, purchase_price: Decimal, shipping: Decimal, buynow=None, match_info=None) -> Dict:
    """生成完整定价结果"""
    ep = safe_decimal(stats.get("filtered_median", stats.get("median", 0)))
    if ep <= 0 and stats.get("prices"): ep = Decimal(str(sorted(stats["prices"])[len(stats["prices"]) // 2]))
    
    if not stats.get("sufficient"):
        result = {"pricingStatus": Status.INSUFFICIENT_DATA, "pricingConfidence": Decimal("0.2"), "riskLevel": "HIGH", "riskScore": 10, "decisionSignal": Status.INSUFFICIENT_DATA, "reasons": [stats.get("reason", "Data insufficient")], "comparableCount": stats.get("filtered_count", stats.get("count", 0)), "comparableItemIds": stats.get("ids", [])}
        
        if ep > 0:
            profit = calc_profit(ep, purchase_price, shipping)
            result.update({"estimatedMarketPrice": int(ep), "currentBidPrice": int(purchase_price), "netProfitAtCurrentBid": int(profit["net"]), "profitMarginAtCurrentBid": profit["margin"], "roiAtCurrentBid": profit["roi"]})
        return _to_dynamo(result)
    
    profit = calc_profit(ep, purchase_price, shipping)
    conf = calc_confidence(stats, item, match_info)
    risk = calc_risk(item, stats, conf, profit["margin"])
    cc = stats["filtered_count"]
    mc = safe_int(item.get("missingParameterCount", 0))
    decision = calc_decision(profit["net"], profit["margin"], profit["roi"], conf, risk["level"], cc, mc, Status.COMPLETED)
    
    reasons = []
    if match_info:
        lvl = match_info.get("level", "EXACT")
        if match_info.get("exact", 0) > 0: reasons.append(f"Based on {match_info['exact']} exact matches")
        if match_info.get("fallback", 0) > 0: reasons.append(f"Added {match_info['fallback']} fallback matches")
        if match_info.get("family", 0) > 0: reasons.append(f"Added {match_info['family']} family matches")
    
    reasons.append(f"Market median: {int(ep)} yen")
    if purchase_price > ep: reasons.append(f"Price above market by {int(purchase_price - ep)}")
    else: reasons.append(f"Price below market by {int(ep - purchase_price)}")
    reasons.append(f"Net profit: {int(profit['net'])} yen ({(profit['margin']*100).quantize(Decimal('0.1'))}%)")
    
    signals = {Status.INSUFFICIENT_DATA: "Insufficient data", "BUY_CANDIDATE": "Buy candidate", "REVIEW": "Needs review", "AVOID": "Avoid"}
    
    if mc > 0: reasons.insert(0, f"Warning: {mc} params missing")
    if match_info and match_info.get("level", "") not in ("", "EXACT"): reasons.insert(0, f"Warning: Using {match_info['level']} matching")
    
    result = {"pricingStatus": Status.COMPLETED, "analysisMethod": "PROGRAMMATIC", "estimatedMarketPrice": int(ep), "estimatedLow": int(stats.get("filtered_min", 0)), "estimatedHigh": int(stats.get("filtered_max", 0)), "currentBidPrice": int(purchase_price), "breakEvenPurchasePrice": profit["bep"], "targetPurchasePrice10Margin": profit["tp10"], "targetPurchasePrice20Margin": profit["tp20"], "netProfitAtCurrentBid": int(profit["net"]), "profitMarginAtCurrentBid": profit["margin"], "roiAtCurrentBid": profit["roi"], "pricingConfidence": conf, "riskLevel": risk["level"], "riskScore": risk["score"], "decisionSignal": signals.get(decision, decision), "reasons": reasons + risk["reasons"], "riskFactors": risk["factors"], "comparableItemIds": stats.get("ids", []), "comparableCount": cc, "missingParameterCount": mc, "matchInfo": match_info or {"level": "EXACT"}, "priceBreakdown": {"estimatedSellingPrice": int(ep), "currentBidPrice": int(purchase_price), "platformFee": int(profit["fee"]), "shippingCost": int(shipping), "repairReserve": int(profit["repair"]), "riskReserve": int(profit["risk"]), "netProfit": int(profit["net"])}}
    
    if buynow and buynow > 0:
        bnp = calc_profit(ep, buynow, shipping)
        result.update({"buynowPrice": int(buynow), "netProfitAtBuynow": int(bnp["net"]), "profitMarginAtBuynow": bnp["margin"], "roiAtBuynow": bnp["roi"]})
    
    return _to_dynamo(result)

def save_pricing(item_id: str, result: Dict, recommendation: str):
    """保存定价结果和购买推荐"""
    _, hidden_profit, roi = calc_potential(result, safe_decimal(result.get("currentBidPrice", 0)))
    update_record(active_db, item_id, {"pricingResult": result, "pricingStatus": result.get("pricingStatus", Status.FAILED), "pricedAt": datetime.now(timezone.utc).isoformat(), "pricingMethod": "PROGRAMMATIC", "purchaseRecommendation": recommendation, "potentialOpportunity": hidden_profit > 0 and roi >= MIN_ROI, "estimatedHiddenProfit": int(hidden_profit), "estimatedHiddenROI": roi})

def calc_potential(result: Dict, price: Decimal) -> Tuple[bool, Decimal, Decimal]:
    """计算潜在机会"""
    ep = safe_decimal(result.get("estimatedMarketPrice", 0))
    if ep <= 0: return False, Decimal("0"), Decimal("0")
    
    cost = price + SHIPPING_COST + ep * (FEE_RATE + REPAIR_RESERVE + RISK_RESERVE)
    profit = ep - cost
    roi = profit / cost if cost > 0 else Decimal("0")
    return profit > 0 and roi >= MIN_ROI, profit, roi

# ======================================
# Detail Reparse Service
# ======================================

def invoke_detail(item_id: str, url: str) -> Optional[Dict]:
    """调用Detail Lambda"""
    try:
        resp = lambda_client.invoke(FunctionName=DETAIL_LAMBDA, InvocationType="RequestResponse", Payload=json.dumps({"itemId": item_id, "url": url}, ensure_ascii=False))
        payload = resp.get("Payload")
        if not payload: return None
        
        if hasattr(payload, 'read'): data = json.loads(payload.read().decode('utf-8'))
        elif isinstance(payload, (str, bytes)): data = json.loads(payload if isinstance(payload, str) else payload.decode('utf-8'))
        else: return None
        
        if isinstance(data, dict):
            if data.get("statusCode") == 200:
                body = data.get("body", "{}")
                return json.loads(body) if isinstance(body, str) else body
            if "title" in data or "description" in data: return data
        return None
    except Exception as e:
        logger.error(f"Detail Lambda failed: {e}")
        return None

def reparse_detail(item_id: str, item: Dict, detail: Dict) -> Optional[Dict]:
    """用详情重新解析"""
    prompt = build_detail_prompt(item_id, item.get("title", ""), detail.get("description", ""), detail.get("specification", ""))
    result, _ = call_ai(prompt)
    if not result: return None
    items = result.get("items", [])
    return items[0] if isinstance(items, list) and len(items) > 0 else None

def batch_detail_reparse(items: List[Dict], closed_ids: Set[str]) -> Dict:
    """批量Detail Reparse"""
    result = {"success": 0, "failed": 0}
    
    for item in items:
        iid = str(item.get("itemID", ""))
        try:
            check_limits()
            update_record(active_db, iid, {"detailAnalysisStatus": Status.RUNNING})
            
            url = item.get("url", "")
            if not url:
                update_record(active_db, iid, {"detailAnalysisStatus": Status.FAILED, "detailAnalysisError": "NO_URL"})
                result["failed"] += 1; continue
            
            detail = invoke_detail(iid, url)
            if not detail:
                update_record(active_db, iid, {"detailAnalysisStatus": Status.FAILED, "detailAnalysisError": "LAMBDA_FAILED"})
                result["failed"] += 1; continue
            
            reparsed = reparse_detail(iid, item, detail)
            if not reparsed:
                update_record(active_db, iid, {"detailAnalysisStatus": Status.FAILED, "detailAnalysisError": "REPARSE_FAILED"})
                result["failed"] += 1; continue
            
            # 更新模型并重新估价
            save_model(active_db, iid, reparsed)
            active = get_record(active_db, iid)
            if not active: continue
            
            idx = build_comparable_index(closed_ids)
            ci, mi = find_comparable(active, idx)
            stats = calc_stats(ci)
            pp = safe_decimal(active.get("price", 0))
            sh = get_shipping_cost(active)
            bp = safe_decimal(active.get("buynowPrice")) if active.get("buynowPrice") else None
            
            pr = build_pricing_result(active, stats, pp, sh, bp, mi)
            rec = calc_decision(safe_decimal(pr.get("netProfitAtCurrentBid", 0)), safe_decimal(pr.get("profitMarginAtCurrentBid", 0)), safe_decimal(pr.get("roiAtCurrentBid", 0)), safe_decimal(pr.get("pricingConfidence", 0)), pr.get("riskLevel", "HIGH"), safe_int(pr.get("comparableCount", 0)), safe_int(active.get("missingParameterCount", 0)), pr.get("pricingStatus", Status.INSUFFICIENT_DATA))
            
            if rec == Recommendation.AI_RECHECK:
                rec = Recommendation.MANUAL_REVIEW
                mark_manual_review(iid, "INSUFFICIENT_DATA_AFTER_DETAIL")
            
            save_pricing(iid, pr, rec)
            update_record(active_db, iid, {"detailAnalysisStatus": Status.COMPLETED})
            result["success"] += 1
        except RuntimeError: raise
        except Exception as e:
            logger.error(f"Detail reparse failed {iid}: {e}")
            update_record(active_db, iid, {"detailAnalysisStatus": Status.FAILED, "detailAnalysisError": str(e)[:200]})
            result["failed"] += 1
    
    return result

def mark_manual_review(item_id: str, reason: str):
    update_record(active_db, item_id, {"needsHumanReview": True, "reviewReason": reason, "purchaseRecommendation": Recommendation.MANUAL_REVIEW, "reviewFlaggedAt": datetime.now(timezone.utc).isoformat()})

def get_recheck_items(ids: List[str]) -> List[Dict]:
    items = []
    for iid in ids:
        item = get_record(active_db, iid)
        if item and item.get("purchaseRecommendation") == Recommendation.AI_RECHECK and item.get("detailAnalysisStatus") in (None, Status.NOT_RUN, "NOT_RUN"):
            items.append(item)
    return items

def get_manual_items(ids: List[str]) -> List[str]:
    result = []
    for iid in ids:
        item = get_record(active_db, iid)
        if not item: continue
        if item.get("purchaseRecommendation") == Recommendation.AI_RECHECK and item.get("detailAnalysisStatus") in (Status.COMPLETED, Status.FAILED):
            result.append(iid)
        elif item.get("needsHumanReview"):
            result.append(iid)
    return result

# ======================================
# Search & Scrape
# ======================================

def upsert_item(table, item: Dict, keyword: str, ttl_days: int, force=False):
    now = datetime.now(timezone.utc)
    si = shipping_info(item.get("shippingText", ""))
    
    fields = {"itemType": item.get("itemType", "auction"), "title": item.get("title", ""), "price": safe_int(item.get("price", 0)), "bidCount": safe_int(item.get("bidCount", 0)), "endTime": item.get("endTime") or "unknown", "sellerId": str(item.get("sellerId") or "unknown"), "sellerRating": str(item.get("sellerRating") or "unknown"), "sellerType": item.get("sellerType", "personal"), "prefecture": item.get("prefecture") or "unknown", "url": item.get("url", ""), "thumbnailUrl": item.get("thumbnailUrl", ""), "searchKeyword": keyword, "lastScrapedAt": now.isoformat(), "isFreeShipping": si["free"], "shippingStatus": si["status"], "ttl": int((now + timedelta(days=ttl_days)).timestamp())}
    
    if force: fields["modelStatus"] = Status.PENDING; fields["pricingStatus"] = Status.PENDING
    else: fields["modelStatus_if"] = Status.PENDING; fields["pricingStatus_if"] = Status.PENDING
    
    if item.get("buynowPrice"): fields["buynowPrice"] = safe_int(item["buynowPrice"])
    if item.get("shippingText"): fields["shippingText"] = item["shippingText"]
    if item.get("itemCondition"): fields["itemCondition"] = item["itemCondition"]
    
    # 处理 if_not_exists
    if "modelStatus_if" in fields:
        fields.pop("modelStatus_if")
        # 简化：直接用 PENDING（实际应使用 if_not_exists）
    
    update_record(table, str(item["itemId"]), {k: v for k, v in fields.items() if not k.endswith("_if")})

def scrape_active(keyword: str, count: int, min_price: int = 0, force=False) -> List[str]:
    try:
        items = scrape_auctions(keyword=keyword, auction_type="active", include_paypay=False, min_price=min_price if min_price > 0 else None)
        if min_price > 0: items = [i for i in items if safe_int(i.get("price", 0)) >= min_price]
        items = items[:count]
        for item in items:
            try: upsert_item(active_db, item, keyword, 30, force)
            except Exception as e: logger.error(f"Save active failed {item.get('itemId')}: {e}")
        return [str(i["itemId"]) for i in items]
    except Exception as e:
        logger.error(f"Active scrape failed: {e}")
        return []

def scrape_closed(keyword: str, count: int, force=False) -> List[str]:
    try:
        items = scrape_auctions(keyword, "closed", False)[:count]
        for item in items:
            try: upsert_item(closed_db, item, keyword, 180, force)
            except Exception as e: logger.error(f"Save closed failed {item.get('itemId')}: {e}")
        return [str(i["itemId"]) for i in items]
    except Exception as e:
        logger.error(f"Closed scrape failed: {e}")
        return []

def calc_min_price(closed_ids: List[str]) -> Dict:
    prices = []
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus") != Status.COMPLETED: continue
        if item.get("listingType") != ListingType.MAIN_PRODUCT or item.get("parsedCondition") == "BROKEN": continue
        p = safe_int(item.get("price", 0))
        if p > 0: prices.append(p)
    
    if not prices: return {"min": 0, "avg": 0, "median": 0, "count": 0}
    
    prices.sort()
    n = len(prices)
    
    if n >= 3:
        q1 = prices[n // 4]; q3 = prices[n * 3 // 4]
        lo = int(q1 - MAX_PRICE_DEV * (q3 - q1))
        hi = int(q3 + MAX_PRICE_DEV * (q3 - q1))
        filtered = [p for p in prices if lo <= p <= hi]
    else:
        filtered = prices
    
    if not filtered: filtered = prices
    avg = sum(filtered) // len(filtered)
    return {"min": max(1, int(avg * PRICE_MIN_RATIO)), "avg": avg, "median": sorted(filtered)[len(filtered)//2], "count": len(filtered)}

# ======================================
# Workflow
# ======================================

def execute_workflow(keyword: str, active_count: int, closed_count: int, force: bool) -> Dict:
    global _api_logger, _stage_timer
    start = time.time()
    result = {"keyword": keyword, "errors": []}
    
    try:
        check_limits()
        
        # Step 1: Closed search
        closed_ids = scrape_closed(keyword, closed_count, force)
        result["closed_count"] = len(closed_ids)
        if not closed_ids: return {**result, "status": "NO_CLOSED"}
        
        # Step 2: Closed parse
        closed_items = [get_record(closed_db, cid) for cid in closed_ids]
        closed_items = [i for i in closed_items if i and (force or i.get("modelStatus") == Status.PENDING)]
        if closed_items:
            r = batch_parse(closed_db, closed_items, build_parse_prompt, CLOSED_BATCH)
            result.update({f"closed_{k}": v for k, v in r.items()})
        
        # Step 3: Calc min price
        price_info = calc_min_price(closed_ids)
        result["price_filter"] = price_info
        min_p = price_info.get("min", 0)
        
        # Step 4: Active search
        active_ids = scrape_active(keyword, active_count, min_p, force)
        result["active_count"] = len(active_ids)
        if not active_ids: return {**result, "status": "NO_ACTIVE"}
        
        # Step 5: Active parse
        active_items = [get_record(active_db, aid) for aid in active_ids]
        active_items = [i for i in active_items if i and (force or i.get("modelStatus") == Status.PENDING)]
        if active_items:
            r = batch_parse(active_db, active_items, build_parse_prompt, MODEL_BATCH)
            result.update({f"active_{k}": v for k, v in r.items()})
        
        # Step 6: Pricing (Layer 1)
        idx = build_comparable_index(set(closed_ids))
        pricing_items = []
        for aid in active_ids:
            item = get_record(active_db, aid)
            if not item: continue
            ps = item.get("pricingStatus", Status.PENDING)
            if force:
                if ps not in (Status.PENDING, Status.COMPLETED, Status.INSUFFICIENT_DATA, Status.FAILED): continue
            elif ps != Status.PENDING: continue
            if item.get("modelStatus") != Status.COMPLETED: continue
            lt = str(item.get("listingType", "")).upper()
            if lt in EXCLUDED_TYPES: continue
            if str(item.get("parsedCondition", "")).upper() == "BROKEN": continue
            
            models = item.get("models", [])
            if isinstance(models, str):
                try: models = json.loads(models)
                except: continue
            if any(m.get("pricingModelKey") for m in (models if isinstance(models, list) else []) if isinstance(m, dict)):
                pricing_items.append(item)
        
        for item in pricing_items[:active_count]:
            try:
                check_limits()
                iid = str(item["itemID"])
                ci, mi = find_comparable(item, idx)
                stats = calc_stats(ci)
                pp = safe_decimal(item.get("price", 0))
                sh = get_shipping_cost(item)
                bp = safe_decimal(item.get("buynowPrice")) if item.get("buynowPrice") else None
                
                pr = build_pricing_result(item, stats, pp, sh, bp, mi)
                rec = calc_decision(safe_decimal(pr.get("netProfitAtCurrentBid", 0)), safe_decimal(pr.get("profitMarginAtCurrentBid", 0)), safe_decimal(pr.get("roiAtCurrentBid", 0)), safe_decimal(pr.get("pricingConfidence", 0)), pr.get("riskLevel", "HIGH"), safe_int(pr.get("comparableCount", 0)), safe_int(item.get("missingParameterCount", 0)), pr.get("pricingStatus", Status.INSUFFICIENT_DATA))
                
                save_pricing(iid, pr, rec)
            except RuntimeError: raise
            except Exception as e:
                logger.error(f"Pricing failed {iid}: {e}")
                update_record(active_db, iid, {"pricingStatus": Status.FAILED, "pricingError": str(e)[:500]})
        
        # Step 7: Detail Reparse (Layer 2)
        if ENABLE_DETAIL:
            recheck = get_recheck_items(active_ids)
            result["recheck_count"] = len(recheck)
            if recheck:
                dr = batch_detail_reparse(recheck, set(closed_ids))
                result["reparse_success"] = dr["success"]
                result["reparse_failed"] = dr["failed"]
        
        # Step 8: Manual Review (Layer 3)
        manual = get_manual_items(active_ids)
        for mid in manual: mark_manual_review(mid, "FINAL_REVIEW")
        result["manual_review"] = len(manual)
        
        # Final stats
        counts = {"BUY": 0, "REVIEW": 0, "NO": 0, "AI_RECHECK": 0, "MANUAL_REVIEW": 0}
        for aid in active_ids:
            item = get_record(active_db, aid)
            if item:
                rec = item.get("purchaseRecommendation", "")
                if rec in counts: counts[rec] += 1
        result["recommendations"] = counts
        
        result["status"] = "COMPLETED"
        result["elapsed"] = round(time.time() - start, 1)
        return result
    except RuntimeError as e:
        return {**result, "status": "INTERRUPTED", "reason": str(e), "elapsed": round(time.time() - start, 1)}
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {**result, "status": "FAILED", "errors": result.get("errors", []) + [str(e)], "elapsed": round(time.time() - start, 1)}

# ======================================
# Lambda Handler
# ======================================

def lambda_handler(event, context):
    global _total_tokens, _start_time
    _total_tokens = 0
    _start_time = time.time()
    
    try:
        keyword = normalize(event.get("keyword", ""))
        if not keyword: return {"statusCode": 400, "body": json.dumps({"error": "keyword required"}, ensure_ascii=False)}
        
        active_count = max(1, min(int(event.get("active_count", 100)), 100))
        closed_count = max(1, min(int(event.get("closed_count", 100)), 100))
        force = str(event.get("force_reprocess", "")).lower() in ("true", "1", "yes")
        product_pk = event.get("product_pk", "")
        
        result = execute_workflow(keyword, active_count, closed_count, force)
        
        # Update product status
        if product_pk:
            now = int(time.time())
            today = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
            status = result.get("status", "FAILED")
            try:
                product_db.update_item(Key={"PK": product_pk, "SK": "META"}, UpdateExpression="SET last_analysis_status = :s, last_scanned_date = :d, last_scanned_at = :n", ExpressionAttributeValues={":s": status, ":d": today, ":n": now})
            except: pass
        
        return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False, default=str)}
    except Exception as e:
        logger.error(f"Handler failed: {e}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)}, ensure_ascii=False)}
