"""
Yahoo Auction 商品分析工作流 Lambda
三层决策流：程序估价 → AI重解析 → 人工审核
开放参数限制 + 多级降级匹配
title + detailDescription 详细AI解析

核心修复：
1. scrape_closed/scrape_active 新商品自动初始化 modelStatus=PENDING
2. upsert_scraped_item 使用 if_not_exists 不覆盖已有状态
3. update_record 修复 ExpressionAttributeNames 问题
4. 增强日志输出
"""

import os, re, json, time, random, logging, urllib.request, urllib.error, socket
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
    PENDING = "PENDING"; COMPLETED = "COMPLETED"; FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"; EXCLUDED = "EXCLUDED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"; NOT_APPLICABLE = "NOT_APPLICABLE"
    RUNNING = "RUNNING"; NOT_RUN = "NOT_RUN"

class ListingType:
    MAIN_PRODUCT = "MAIN_PRODUCT"; ACCESSORY = "ACCESSORY"; PARTS = "PARTS"
    BROKEN = "BROKEN"; BOX_ONLY = "BOX_ONLY"; BUNDLE = "BUNDLE"; UNKNOWN = "UNKNOWN"

EXCLUDED_TYPES = {ListingType.ACCESSORY, ListingType.PARTS, ListingType.BROKEN, ListingType.BOX_ONLY, ListingType.BUNDLE, ListingType.UNKNOWN}

class Recommendation:
    BUY = "BUY"; REVIEW = "REVIEW"; NO = "NO"
    AI_RECHECK = "AI_RECHECK"; MANUAL_REVIEW = "MANUAL_REVIEW"

NON_CRITICAL_FIELDS = {"variant", "color", "carrier", "screen_size", "battery", "graphics_card", "os", "processor", "cpu", "compatibility", "ram", "memory"}
CRITICAL_PARAM_PENALTIES = {"brand": Decimal("0.20"), "model": Decimal("0.30"), "storage": Decimal("0.10"), "other": Decimal("0.05")}
MODEL_FAMILY_SUFFIXES = [" RECON", " RECON LT", " BY", " CS MID", " CS", " MID", " LOW", " HIGH", " PRIMEKNIT", " PRIME KNIT", " PRIME", " PK", " PRO MAX", " PRO", " MAX", " PLUS", " ULTRA", " LITE", " FE", " ELITE", " ELITEBOOK", " PROBOOK", " GEN10", " GEN9", " GEN8", " G10", " G9", " G8", " LIMITED EDITION", " LIMITED", " LE", " SE", " SPECIAL EDITION", " ANNIVERSARY", " OG", " 2023", " 2024", " 2025"]

# ======================================
# Config
# ======================================

def _env(key, default, cast=str):
    v = os.getenv(key, ""); return cast(v) if v else default

TABLE_ACTIVE = _env("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_CLOSED = _env("TABLE_NAME_CLOSED", "YahooAuctionItems")
AI_MODE = _env("AI_MODE", "doubao")
AI_CONFIGS = {
    "gemini": {"name": "gemini", "type": "gemini", "url": _env("GEMINI_URL", ""), "model": _env("GEMINI_MODEL", "gemini-2.0-flash"), "timeout": _env("GEMINI_TIMEOUT", 60, int), "max_tokens": _env("GEMINI_MAX_TOKENS", 4000, int), "key": _env("GEMINI_API_KEY", "")},
    "doubao": {"name": "doubao", "type": "openai", "url": _env("DOUBAO_URL", ""), "model": _env("DOUBAO_MODEL", "qwen-plus"), "timeout": _env("DOUBAO_TIMEOUT", 90, int), "max_tokens": _env("DOUBAO_MAX_TOKENS", 6000, int), "key": _env("DOUBAO_API_KEY", "")},
    "openai": {"name": "openai", "type": "openai", "url": _env("OPENAI_URL", ""), "model": _env("OPENAI_MODEL", "gpt-4o-mini"), "timeout": _env("OPENAI_TIMEOUT", 60, int), "max_tokens": _env("OPENAI_MAX_TOKENS", 4000, int), "key": _env("OPENAI_API_KEY", "")},
}

BUY_MARGIN = _env("BUY_MARGIN_THRESHOLD", Decimal("0.20"), Decimal)
REVIEW_MARGIN = _env("REVIEW_MARGIN_THRESHOLD", Decimal("0.10"), Decimal)
MIN_COMPARABLE = _env("MIN_COMPARABLE_COUNT", 3, int)
HIGH_CONF = _env("HIGH_CONFIDENCE_COUNT", 10, int); MED_CONF = _env("MEDIUM_CONFIDENCE_COUNT", 5, int)
PRICE_MIN_RATIO = _env("PRICE_MIN_RATIO", Decimal("0.5"), Decimal)
MIN_ROI = _env("MIN_ROI", Decimal("0.15"), Decimal)
FEE_RATE = _env("FEE_RATE", Decimal("0.10"), Decimal); SHIPPING_COST = _env("SHIPPING_COST", Decimal("1500"), Decimal)
REPAIR_RESERVE = _env("REPAIR_RESERVE", Decimal("0.05"), Decimal); RISK_RESERVE = _env("RISK_RESERVE", Decimal("0.03"), Decimal)
MAX_PRICE_DEV = _env("MAX_PRICE_DEV", Decimal("1.5"), Decimal)
MODEL_BATCH = _env("MODEL_BATCH", 100, int); CLOSED_BATCH = _env("CLOSED_BATCH", 100, int)
AI_TIMEOUT = _env("AI_TIMEOUT", 90, int); AI_RETRIES = _env("AI_RETRIES", 3, int)
MAX_TOKENS = _env("MAX_TOKENS", 50000, int)
LAMBDA_TIMEOUT = _env("LAMBDA_TIMEOUT", 840, int); TIMEOUT_BUFFER = _env("TIMEOUT_BUFFER", 30, int)
DETAIL_DESC_MAX = _env("DETAIL_DESC_MAX", 3000, int)
ENABLE_FALLBACK = _env("FALLBACK_MATCH", True, lambda x: x.lower() in ("true","1")); ENABLE_FAMILY = _env("FAMILY_MATCH", True, lambda x: x.lower() in ("true","1"))

# ======================================
# DynamoDB & State
# ======================================

dynamodb = boto3.resource("dynamodb")
active_db = dynamodb.Table(TABLE_ACTIVE); closed_db = dynamodb.Table(TABLE_CLOSED)
secrets = boto3.client("secretsmanager")
_total_tokens = 0; _start_time = None; _ai_state = {"failed_modes": {}}

# ======================================
# Repository (修复版)
# ======================================

def update_record(table, item_id: str, fields: Dict):
    """更新 DynamoDB 记录（修复 ExpressionAttributeNames 问题）"""
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
    
    if force:
        # 强制重置：覆盖已有状态
        parts.append("modelStatus = :pending")
        parts.append("pricingStatus = :pending")
    else:
        # 仅新记录设置默认值，不覆盖已有状态
        parts.append("modelStatus = if_not_exists(modelStatus, :pending)")
        parts.append("pricingStatus = if_not_exists(pricingStatus, :pending)")
    
    parts.append("lastScrapedAt = :now")
    
    kwargs = {
        "Key": {"itemID": str(item_id)},
        "UpdateExpression": "SET " + ", ".join(parts),
        "ExpressionAttributeValues": values,
    }
    
    if names:
        kwargs["ExpressionAttributeNames"] = names
    
    table.update_item(**kwargs)

def get_record(table, item_id: str) -> Optional[Dict]:
    r = table.get_item(Key={"itemID": str(item_id)}); return r.get("Item")

def _to_dynamo(v):
    if isinstance(v, float): return Decimal(str(v))
    if isinstance(v, Decimal): return v
    if isinstance(v, dict): return {str(k): _to_dynamo(i) for k,i in v.items()}
    if isinstance(v, (list,tuple)): return [_to_dynamo(i) for i in v]
    return v

# ======================================
# Helpers
# ======================================

def sd(v, d=Decimal("0")) -> Decimal:
    try: return v if isinstance(v,Decimal) else Decimal(str(v))
    except: return d

def si(v, d=0) -> int:
    try: return int(v)
    except: return d

def norm(text: str) -> str:
    if not text: return ""
    t = str(text).strip().translate(str.maketrans("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９","ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    return re.sub(r"\s+"," ",t)

def norm_storage(v) -> str:
    if not v: return ""
    t = norm(str(v)).upper()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(GB|G|TB|T)",t)
    if m: return f"{m.group(1)}{'GB' if m.group(2) in ('G','GB') else 'TB'}"
    parts = [f"{a}{'GB' if u in ('G','GB') else 'TB'}" for a,u in re.findall(r"(\d+(?:\.\d+)?)\s*(GB|TB|G|T)",t)]
    if parts: return " ".join(parts)
    ram = re.search(r'(?:RAM|メモリ)\s*(\d+)\s*GB',t); ssd = re.search(r'(?:SSD|M\.2\s*SSD)\s*(\d+)\s*GB',t)
    hdd = re.search(r'(?:HDD)\s*(\d+)\s*(?:GB|TB)',t)
    parts = []
    if ram: parts.append(f"RAM{ram.group(1)}GB")
    if ssd: parts.append(f"SSD{ssd.group(1)}GB")
    if hdd: parts.append(f"HDD{hdd.group(1)}{'TB' if 'TB' in t else 'GB'}")
    return " ".join(parts) if parts else t

def extract_family(model: str) -> str:
    if not model: return ""
    n = norm(model).upper()
    for s in MODEL_FAMILY_SUFFIXES:
        if n.endswith(s):
            f = n[:-len(s)].strip()
            if len(f)>=3: return f
    w = n.split(); return " ".join(w[:3]) if len(w)>=4 else (" ".join(w[:2]) if len(w)>=3 else n)

def gen_key(brand, model, storage="", variant=""):
    b = norm(brand).upper() if brand else "UNKNOWN"
    m = norm(model).upper() if model else "UNKNOWN"
    s = norm_storage(storage)
    parts = [b,m]; 
    if s: parts.append(s)
    return re.sub(r"[^A-Z0-9\s+\-/]"," "," ".join(parts)).strip()

def gen_fallback_key(brand, model, storage=""):
    b = norm(brand).upper() if brand else "UNKNOWN"
    m = norm(model).upper() if model else "UNKNOWN"
    s = norm_storage(storage); fam = extract_family(m)
    base = re.sub(r"[^A-Z0-9\s+\-/]"," ",f"{b} {fam}").strip()
    full = re.sub(r"[^A-Z0-9\s+\-/]"," ",f"{b} {m}"+(f" {s}" if s else "")).strip()
    if base==full or base==f"{b} {m}":
        if s:
            ns = re.sub(r"[^A-Z0-9\s+\-/]"," ",f"{b} {m}").strip()
            return ns if ns!=full else ""
        return ""
    return base

def get_shipping(item: Dict) -> Decimal:
    if item.get("shippingStatus")=="FREE": return Decimal("0")
    return sd(item.get("shippingFee"), SHIPPING_COST)

def check_limits():
    if _total_tokens >= MAX_TOKENS: raise RuntimeError(f"Token limit exceeded")
    e = 0 if _start_time is None else time.time()-_start_time
    if LAMBDA_TIMEOUT-e-TIMEOUT_BUFFER <= 0: raise RuntimeError("Timeout approaching")

# ======================================
# AI Service
# ======================================

def _get_key(mode: str) -> str:
    for n in [f"{mode}-api-key-{os.getenv('ENVIRONMENT','dev')}",f"{mode}-api-key",f"{mode}/api-key/{os.getenv('ENVIRONMENT','dev')}"]:
        try:
            r = secrets.get_secret_value(SecretId=n); s = r.get("SecretString","")
            if not s: continue
            try: d=json.loads(s); k=d.get("apiKey") or d.get("api_key") or d.get("key") or ""
            except: k=s.strip()
            if k: return k
        except: pass
    return ""

def get_ai_cfg():
    order = [AI_MODE]+[m for m in ["gemini","doubao","openai"] if m!=AI_MODE]
    now = time.time()
    for mode in order:
        if mode in _ai_state["failed_modes"]:
            if now-_ai_state["failed_modes"][mode] < _env("AI_COOLDOWN",300,int): continue
            del _ai_state["failed_modes"][mode]
        c = AI_CONFIGS.get(mode,{})
        k = c.get("key") or _get_key(mode)
        if k: c["key"]=k; return c
    return None

def call_ai(prompt: str) -> Tuple[Optional[Dict],Optional[str]]:
    global _total_tokens
    logger.info(f"AI call: prompt length={len(prompt)}, current tokens={_total_tokens}")
    
    for attempt in range(3):
        cfg = get_ai_cfg()
        if not cfg:
            logger.error("All AI modes unavailable")
            return None,"ALL_MODES_UNAVAILABLE"
        
        mode, is_gem = cfg["name"], cfg["type"]=="gemini"
        logger.info(f"AI attempt {attempt+1}: mode={mode}, model={cfg['model']}")
        
        body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.0,"maxOutputTokens":cfg["max_tokens"]}} if is_gem else {"model":cfg["model"],"messages":[{"role":"system","content":"JSONのみ返してください"},{"role":"user","content":prompt}],"temperature":0.0,"max_tokens":cfg["max_tokens"]}
        if mode=="doubao": body["response_format"]={"type":"json_object"}
        headers = {"x-goog-api-key":cfg["key"],"Content-Type":"application/json"} if is_gem else {"Authorization":f"Bearer {cfg['key']}","Content-Type":"application/json"}
        
        for retry in range(AI_RETRIES):
            try:
                check_limits()
                req = urllib.request.Request(cfg["url"],data=json.dumps(body,ensure_ascii=False).encode(),headers=headers,method="POST")
                with urllib.request.urlopen(req,timeout=cfg["timeout"]) as r:
                    result = json.loads(r.read().decode())
                
                u = result.get("usageMetadata",{}) or result.get("usage",{})
                tokens_used = u.get("total_tokens",u.get("totalTokenCount",0))
                _total_tokens += tokens_used
                logger.info(f"AI response: mode={mode}, tokens={tokens_used}, total_tokens={_total_tokens}")
                
                if is_gem:
                    if "candidates" in result and result["candidates"]:
                        c = result["candidates"][0]; fr = c.get("finishReason","unknown")
                        content = "".join(p.get("text","") for p in c.get("content",{}).get("parts",[]))
                    else: content,fr = "","unknown"
                else:
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0].get("message",{}).get("content","")
                        fr = result["choices"][0].get("finish_reason","unknown")
                    else: content,fr = "","unknown"
                
                logger.info(f"AI finish: reason={fr}, content_length={len(content)}")
                
                if fr=="SAFETY": return None,"safety_blocked"
                parsed = _parse_json(content)
                if parsed is not None:
                    if "items" in parsed:
                        logger.info(f"AI parsed: {len(parsed['items'])} items")
                    return parsed,fr
                else:
                    logger.warning(f"Failed to parse AI response as JSON")
                    
            except RuntimeError: raise
            except Exception as e: logger.error(f"[{mode}] retry {retry+1}: {type(e).__name__}: {e}")
            if retry < AI_RETRIES-1: time.sleep(2**retry+random.uniform(0,1))
        
        _ai_state["failed_modes"][mode]=time.time()
        logger.warning(f"Mode {mode} failed, switching to next")
    
    return None,"ALL_MODES_EXHAUSTED"

def _parse_json(content: str) -> Optional[Dict]:
    if not content: return None
    content = content.strip()
    for p in [lambda c: json.loads(c), lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```","",c))]:
        try: return p(content)
        except: pass
    for bracket in ('{','['):
        depth,start = 0,-1
        for i,ch in enumerate(content):
            if ch==bracket:
                if depth==0: start=i
                depth+=1
            elif ch==('}' if bracket=='{' else ']'):
                depth-=1
                if depth==0 and start>=0:
                    try: return json.loads(content[start:i+1])
                    except: break
    return None

# ======================================
# Prompt Templates (title + description)
# ======================================

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
      "listingType": "MAIN_PRODUCT",
      "condition": "USED",
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
      }},
      "confidence": 0.95
    }}
  ]
}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

重要ルール：
1. title と description の両方を使って判断してください
2. 矛盾する場合、description の具体的な記載を優先してください
3. スマホは Pro/Pro Max/Plus/mini/Ultra を必ず区別してください
4. スマホは容量、SIMフリー、ネットワーク利用制限、バッテリー最大容量を可能な限り抽出
5. PC/Macは CPU、RAM、SSD/HDD、GPU、画面サイズ、年式を可能な限り抽出
6. ジャンク、故障、部品取り、画面割れ、起動不可、ロックあり、水没、Face ID不良などは defects に必ず入れる
7. 価格比較に使う項目は pricingCompareKeyParts に入れてください
8. 色やキャリアは抽出するが、pricingCompareKeyParts には価格差が大きい場合のみ入れる
9. 明記されていない情報は推測しない
10. 商品説明から読み取れない重要情報は missing に入れる
11. アクセサリ、部品、空箱、セット品、ジャンク品は適切な listingType に分類
12. JSONのみを出力してください"""

def build_parse_prompt(items: List[Dict]) -> str:
    items_data = []
    for item in items:
        data = {"itemId": str(item.get("itemID","")), "title": item.get("title",""), "description": str(item.get("detailDescription",""))[:DETAIL_DESC_MAX], "price": si(item.get("price",0)), "itemCondition": str(item.get("itemCondition","")), "shippingText": str(item.get("shippingText",""))}
        items_data.append(data)
    return DETAILED_PARSE_PROMPT.replace("{items_json}", json.dumps(items_data, ensure_ascii=False, separators=(",",":")))

# ======================================
# Model Parser (详细参数版)
# ======================================

def norm_detail(v: Any) -> str:
    if v is None: return ""
    if isinstance(v, list): return " ".join(str(x).strip() for x in v if str(x).strip())
    if isinstance(v, dict): return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return norm(str(v))

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
    if v: parts.append(v)
    if s: parts.append(s)
    if cpu: parts.append(cpu)
    if ram: parts.append(ram)
    if gpu: parts.append(gpu)
    if scr: parts.append(scr)
    
    combined = " ".join(p for p in parts if p)
    combined = re.sub(r"[^A-Z0-9ぁ-んァ-ン一-龥\s+\-/\.]"," ",combined)
    return re.sub(r"\s+"," ",combined).strip()

def parse_ai_result(parsed: Dict) -> Tuple[List[Dict], str, str, int, str]:
    brand = norm(parsed.get("brand",""))
    model = norm(parsed.get("model",""))
    variant = norm(parsed.get("variant",""))
    storage = norm_storage(parsed.get("storage",""))
    conf = sd(parsed.get("confidence",0))
    lt = norm(parsed.get("listingType","UNKNOWN")).upper()
    cond = norm(parsed.get("condition","UNKNOWN")).upper()
    missing = [m for m in (parsed.get("missing") or []) if str(m).lower() not in NON_CRITICAL_FIELDS]
    defects = parsed.get("defects",[]) or []
    is_junk = str(parsed.get("isJunk","")).lower() in ("true","1","yes")
    is_locked = str(parsed.get("isLocked","")).lower() in ("true","1","yes")
    
    has_b, has_m = bool(brand), bool(model)
    is_unk = model.upper() in ("UNKNOWN","不明","N/A","")
    mc = 0
    if not has_b: missing.append("brand"); mc += 1
    if not has_m or is_unk: missing.append("model"); mc += 1
    if not storage: mc += 1
    
    identifiable = (has_b or has_m) and not is_unk
    
    models = []
    if identifiable:
        b2 = brand if has_b else "UNKNOWN"
        m2 = model if has_m else "UNKNOWN"
        pk = gen_detailed_key(parsed) or gen_key(b2,m2,storage,variant)
        fk = gen_fallback_key(b2,m2,storage)
        if not fk or fk==pk: fk = ""
        fm = extract_family(m2.upper()) if has_m else ""
        
        detailed = {"color": norm_detail(parsed.get("color","")), "carrier": norm_detail(parsed.get("carrier","")), "networkRestriction": norm_detail(parsed.get("networkRestriction","")), "batteryHealth": norm_detail(parsed.get("batteryHealth","")), "cpu": norm_detail(parsed.get("cpu","")), "ram": norm_detail(parsed.get("ram","")), "gpu": norm_detail(parsed.get("gpu","")), "screenSize": norm_detail(parsed.get("screenSize","")), "year": norm_detail(parsed.get("year","")), "accessories": norm_detail(parsed.get("accessories","")), "defects": defects, "conditionDetail": norm_detail(parsed.get("conditionDetail","")), "isJunk": is_junk, "isLocked": is_locked, "isWorking": parsed.get("isWorking"), "pricingCompareKeyParts": parsed.get("pricingCompareKeyParts",{})}
        
        models.append({"brand": b2, "model": m2, "familyModel": fm if fm!=m2.upper() else "", "variant": variant, "storage": storage, "pricingModelKey": pk, "fallbackPricingKey": fk, "confidence": str(conf), "missingParameterCount": mc, "detailedParameters": detailed})
    
    reasons = []
    if lt in EXCLUDED_TYPES: reasons.append(f"Type: {lt}")
    if cond=="BROKEN": reasons.append("BROKEN")
    if is_junk: reasons.append("JUNK")
    if is_locked: reasons.append("LOCKED")
    if defects: reasons.append(f"Defects: {','.join(str(d) for d in defects[:5])}")
    
    return models, lt, cond, mc, "; ".join(reasons)

def save_model(table, item_id: str, parsed: Dict) -> str:
    models, lt, cond, mc, excl = parse_ai_result(parsed)
    excluded = lt in EXCLUDED_TYPES
    broken = cond=="BROKEN"
    low_conf = any(sd(m.get("confidence",0))<Decimal("0.7") for m in models)
    
    if not models: status = Status.REVIEW_REQUIRED
    elif excluded or broken: status = Status.EXCLUDED
    elif low_conf: status = Status.REVIEW_REQUIRED
    else: status = Status.COMPLETED
    
    eligible = not excluded and not broken and len(models)>0
    update_record(table, item_id, {"models": models, "modelStatus": status, "listingType": lt, "missingParameterCount": mc, "isComparable": eligible, "parsedCondition": cond, "exclusionReason": excl, "modelParsedAt": datetime.now(timezone.utc).isoformat(), "pricingStatus": Status.PENDING if eligible else Status.NOT_APPLICABLE, "isAnalysisEligible": eligible, "hasAllCriticalParameters": len(models)>0})
    
    logger.info(f"Model saved: {item_id} -> {status} (type={lt}, condition={cond}, models={len(models)})")
    return status

def mark_failed(table, item_id: str, error: str):
    update_record(table, item_id, {"modelStatus": Status.FAILED, "modelError": error[:500], "modelParsedAt": datetime.now(timezone.utc).isoformat()})
    logger.warning(f"Model failed: {item_id} -> {error[:100]}")

def batch_parse(table, items: List[Dict], prompt_builder, batch_size: int) -> Dict:
    if not items: return {"parsed":0,"excluded":0,"review":0,"failed":0,"errors":[]}
    totals = {"parsed":0,"excluded":0,"review":0,"failed":0,"errors":[]}
    
    logger.info(f"Batch parse starting: {len(items)} items, batch_size={batch_size}")
    
    for start in range(0,len(items),batch_size):
        check_limits()
        batch = items[start:start+batch_size]
        logger.info(f"AI parsing batch {start//batch_size+1}/{(len(items)-1)//batch_size+1}, size={len(batch)}")
        
        result, err = call_ai(prompt_builder(batch))
        
        if not result:
            logger.error(f"AI returned empty for batch: {err}")
            for item in batch: mark_failed(table, str(item["itemID"]), err or "AI_EMPTY")
            totals["failed"] += len(batch); continue
        
        parsed = result.get("items",[]) or []
        returned = set()
        for p in parsed:
            if not isinstance(p,dict): continue
            iid = str(p.get("itemId","")).strip()
            if not iid: continue
            returned.add(iid)
            s = save_model(table, iid, p)
            if s==Status.COMPLETED: totals["parsed"]+=1
            elif s==Status.EXCLUDED: totals["excluded"]+=1
            elif s==Status.REVIEW_REQUIRED: totals["review"]+=1
            else: totals["failed"]+=1
        
        missing_ids = {str(i["itemID"]) for i in batch}-returned
        for mid in missing_ids:
            mark_failed(table, mid, "AI_NOT_RETURNED"); totals["failed"]+=1
        
        logger.info(f"Batch result: parsed={totals['parsed']}, excluded={totals['excluded']}, review={totals['review']}, failed={totals['failed']}")
        
        if start+batch_size < len(items): time.sleep(_env("REQ_INTERVAL",1.0,float))
    
    return totals

# ======================================
# Matching Engine
# ======================================

def build_index(closed_ids: Set[str]) -> Dict[str,List[Dict]]:
    idx = {}; excluded = 0
    logger.info(f"Building index from {len(closed_ids)} closed items")
    
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus")!=Status.COMPLETED: continue
        if item.get("listingType")!=ListingType.MAIN_PRODUCT or item.get("parsedCondition")=="BROKEN": continue
        if sd(item.get("price",0))<=0: continue
        
        models = item.get("models",[])
        if isinstance(models,str):
            try: models=json.loads(models)
            except: continue
        
        keys = set()
        for m in models:
            if not isinstance(m,dict): continue
            mn = norm(m.get("model","")).upper()
            if mn in ("UNKNOWN","不明","N/A",""): excluded+=1; continue
            
            pk = norm(m.get("pricingModelKey","")).upper()
            if pk and pk not in keys: keys.add(pk); idx.setdefault(pk,[]).append(item)
            
            if ENABLE_FALLBACK:
                fk = norm(m.get("fallbackPricingKey","")).upper()
                if fk and fk!=pk:
                    fq = f"FB:{fk}"
                    if fq not in keys: keys.add(fq); idx.setdefault(fq,[]).append(item)
            
            if ENABLE_FAMILY:
                fm = norm(m.get("familyModel","")).upper()
                if fm and fm!=mn:
                    b = norm(m.get("brand","")).upper()
                    if b:
                        fam = re.sub(r"[^A-Z0-9\s+\-/]"," ",f"{b} {fm}").strip()
                        fq = f"FAM:{fam}"
                        if fq not in keys: keys.add(fq); idx.setdefault(fq,[]).append(item)
    
    for k,v in idx.items(): v.sort(key=lambda x: x.get("endTime",""), reverse=True)
    logger.info(f"Index built: {len(idx)} unique keys")
    return idx

def find_comp(item: Dict, idx: Dict[str,List[Dict]]) -> Tuple[List[Dict],Dict]:
    models = item.get("models",[])
    if isinstance(models,str):
        try: models=json.loads(models)
        except: return [],{"level":"ERROR"}
    
    items, seen = [], set()
    exact, fb, fam = 0, 0, 0
    
    for m in models:
        if not isinstance(m,dict): continue
        
        pk = norm(m.get("pricingModelKey","")).upper()
        if pk:
            for ci in idx.get(pk,[]):
                iid = str(ci.get("itemID",""))
                if iid and iid not in seen: seen.add(iid); items.append(ci)
            exact = len(items)
        
        if len(items)<MIN_COMPARABLE and ENABLE_FALLBACK:
            fk = norm(m.get("fallbackPricingKey","")).upper()
            if fk:
                for ci in idx.get(f"FB:{fk}",[]):
                    iid = str(ci.get("itemID",""))
                    if iid and iid not in seen: seen.add(iid); items.append(ci); fb+=1
        
        if len(items)<MIN_COMPARABLE and ENABLE_FAMILY:
            fm = norm(m.get("familyModel","")).upper()
            if fm:
                b = norm(m.get("brand","")).upper()
                if b:
                    fkey = re.sub(r"[^A-Z0-9\s+\-/]"," ",f"{b} {fm}").strip()
                    for ci in idx.get(f"FAM:{fkey}",[]):
                        iid = str(ci.get("itemID",""))
                        if iid and iid not in seen: seen.add(iid); items.append(ci); fam+=1
    
    items.sort(key=lambda x: x.get("endTime",""), reverse=True)
    level = "EXACT" if exact>0 else ""
    if fb>0: level += "+FALLBACK" if level else "FALLBACK"
    if fam>0: level += "+FAMILY" if level else "FAMILY"
    
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
        if not data: return Decimal("0")
        if len(data)==1: return data[0]
        pos = Decimal(len(data)-1)*p; lo = int(pos)
        return data[lo]+(data[lo+1]-data[lo])*(pos-Decimal(lo)) if lo+1<len(data) else data[lo]
    
    q1,m,q3 = pct(prices,Decimal("0.25")),pct(prices,Decimal("0.5")),pct(prices,Decimal("0.75"))
    iqr = q3-q1; lo,hi = q1-MAX_PRICE_DEV*iqr, q3+MAX_PRICE_DEV*iqr
    filtered = [r for r in records if lo<=r["price"]<=hi]
    fp = [r["price"] for r in filtered]; fn = len(fp)
    
    if fn<MIN_COMPARABLE:
        return {**base,"min":int(prices[0]),"max":int(prices[-1]),"q1":int(q1),"median":int(m),"q3":int(q3),"iqr":int(iqr),"lower":int(lo),"upper":int(hi),"f_count":fn,"suff":False,"reason":f"Outlier: {fn}<{MIN_COMPARABLE}","f_median":int(m),"f_min":int(prices[0]),"f_max":int(prices[-1]),"f_prices":[int(p) for p in fp],"ids":[r["id"] for r in filtered]}
    
    fp.sort(); fmed = pct(fp,Decimal("0.5"))
    spread = ((max(fp)-min(fp))/fmed).quantize(Decimal("0.001")) if fmed>0 else Decimal("0")
    
    return {**base,"min":int(prices[0]),"max":int(prices[-1]),"q1":int(q1),"median":int(m),"q3":int(q3),"iqr":int(iqr),"lower":int(lo),"upper":int(hi),"f_count":fn,"excl":n-fn,"suff":True,"f_min":int(min(fp)),"f_max":int(max(fp)),"f_median":int(fmed),"f_avg":int((sum(fp)/Decimal(fn)).quantize(Decimal("1"))),"spread":spread,"f_prices":[int(p) for p in fp],"ids":[r["id"] for r in filtered]}

def calc_conf(stats: Dict, item: Dict=None, mi: Dict=None) -> Decimal:
    if not stats.get("suff"): return Decimal("0.20")
    cc = stats["f_count"]; sr = stats.get("spread",Decimal("0")); tc = stats["count"]; ec = stats.get("excl",0)
    conf = Decimal("0.90") if cc>=HIGH_CONF else (Decimal("0.80") if cc>=MED_CONF else Decimal("0.70"))
    if sr>=Decimal("0.5"): conf-=Decimal("0.20")
    elif sr>=Decimal("0.3"): conf-=Decimal("0.10")
    if tc>0 and Decimal(ec)/Decimal(tc)>=Decimal("0.3"): conf-=Decimal("0.10")
    
    if item:
        ml = item.get("missingCriticalParameters",[])
        if isinstance(ml,str):
            try: ml=json.loads(ml)
            except: ml=[]
        penalty = Decimal("0")
        for p in ml:
            pl = str(p).lower()
            if "brand" in pl: penalty+=CRITICAL_PARAM_PENALTIES["brand"]
            elif "model" in pl: penalty+=CRITICAL_PARAM_PENALTIES["model"]
            elif "storage" in pl: penalty+=CRITICAL_PARAM_PENALTIES["storage"]
            else: penalty+=CRITICAL_PARAM_PENALTIES["other"]
        if penalty==Decimal("0") and item.get("missingParameterCount",0)>0: penalty = Decimal("0.05")*Decimal(item["missingParameterCount"])
        conf -= penalty
    
    if mi:
        if "FAMILY" in mi.get("level",""): conf-=Decimal("0.20")
        elif "FALLBACK" in mi.get("level",""): conf-=Decimal("0.10")
    
    return max(Decimal("0.20"),min(Decimal("0.95"),conf)).quantize(Decimal("0.01"))

def calc_risk(item: Dict, stats: Dict, conf: Decimal, margin: Decimal) -> Dict:
    score = 0; factors, reasons = [], []
    cc = stats.get("f_count",0); mc = si(item.get("missingParameterCount",0))
    if mc>0: score+=mc*2; factors.append(f"Missing {mc}")
    if cc<5: score+=2; factors.append(f"Low samples:{cc}")
    elif cc<10: score+=1
    else: reasons.append(f"Good samples:{cc}")
    if conf<Decimal("0.5"): score+=3
    elif conf<Decimal("0.75"): score+=1
    
    sr = stats.get("spread",Decimal("0"))
    if sr>=Decimal("0.5"): score+=2
    elif sr>=Decimal("0.3"): score+=1
    
    r = item.get("sellerRating")
    if r:
        try:
            rr = Decimal(str(r).replace("%",""))
            if rr<Decimal("95"): score+=2
            elif rr<Decimal("98"): score+=1
        except: pass
    if str(item.get("sellerType","")).lower()=="personal": score+=1
    if margin<Decimal("0"): score+=3
    elif margin<REVIEW_MARGIN: score+=2
    elif margin<BUY_MARGIN: score+=1
    
    level = "HIGH" if score>=6 else ("MEDIUM" if score>=3 else "LOW")
    return {"level":level,"score":score,"factors":factors,"reasons":reasons}

def calc_profit(est: Decimal, buy: Decimal, ship: Decimal) -> Dict:
    fee = (est*FEE_RATE).quantize(Decimal("1")); rep = (est*REPAIR_RESERVE).quantize(Decimal("1"))
    risk = (est*RISK_RESERVE).quantize(Decimal("1")); tc = fee+ship+rep+risk
    net = est-buy-tc; margin = (net/est).quantize(Decimal("0.001")) if est>0 else Decimal("0")
    inv = buy+ship+rep+risk; roi = (net/inv).quantize(Decimal("0.001")) if inv>0 else Decimal("0")
    bep = (est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE)-ship).quantize(Decimal("1"))
    return {"net":net,"margin":margin,"roi":roi,"fee":fee,"repair":rep,"risk":risk,"tc":tc,"bep":max(0,int(bep)),"tp10":max(0,int((est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE-Decimal("0.1"))-ship).quantize(Decimal("1")))),"tp20":max(0,int((est*(Decimal("1")-FEE_RATE-REPAIR_RESERVE-RISK_RESERVE-Decimal("0.2"))-ship).quantize(Decimal("1"))))}

def calc_decision(net: Decimal, margin: Decimal, roi: Decimal, conf: Decimal, risk: str, cc: int, mc: int, status: str) -> str:
    if status==Status.INSUFFICIENT_DATA: return Recommendation.AI_RECHECK if net>0 and roi>=MIN_ROI else Recommendation.NO
    if net<=0: return Recommendation.NO
    if cc<MIN_COMPARABLE: return Recommendation.AI_RECHECK if roi>=MIN_ROI else Recommendation.NO
    if mc>=2 and conf<Decimal("0.6"): return Recommendation.AI_RECHECK
    if margin>=BUY_MARGIN and risk in ("LOW","MEDIUM") and conf>=Decimal("0.7"): return Recommendation.BUY
    if margin>=REVIEW_MARGIN and conf>=Decimal("0.5"): return Recommendation.REVIEW
    if roi>=MIN_ROI: return Recommendation.AI_RECHECK
    return Recommendation.NO

def build_result(item: Dict, stats: Dict, buy: Decimal, ship: Decimal, buynow=None, mi=None) -> Dict:
    ep = sd(stats.get("f_median",stats.get("median",0)))
    if ep<=0 and stats.get("prices"): ep = Decimal(str(sorted(stats["prices"])[len(stats["prices"])//2]))
    
    if not stats.get("suff"):
        result = {"pricingStatus":Status.INSUFFICIENT_DATA,"pricingConfidence":Decimal("0.2"),"riskLevel":"HIGH","riskScore":10,"decisionSignal":Status.INSUFFICIENT_DATA,"reasons":[stats.get("reason","Insufficient")],"comparableCount":stats.get("f_count",stats.get("count",0)),"comparableItemIds":stats.get("ids",[])}
        if ep>0:
            p = calc_profit(ep,buy,ship)
            result.update({"estimatedMarketPrice":int(ep),"currentBidPrice":int(buy),"netProfitAtCurrentBid":int(p["net"]),"profitMarginAtCurrentBid":p["margin"],"roiAtCurrentBid":p["roi"]})
        return _to_dynamo(result)
    
    profit = calc_profit(ep,buy,ship); conf = calc_conf(stats,item,mi)
    risk = calc_risk(item,stats,conf,profit["margin"]); cc = stats["f_count"]; mc = si(item.get("missingParameterCount",0))
    dec = calc_decision(profit["net"],profit["margin"],profit["roi"],conf,risk["level"],cc,mc,Status.COMPLETED)
    
    reasons = []
    if mi:
        if mi.get("exact",0)>0: reasons.append(f"Exact: {mi['exact']}")
        if mi.get("fallback",0)>0: reasons.append(f"Fallback: +{mi['fallback']}")
        if mi.get("family",0)>0: reasons.append(f"Family: +{mi['family']}")
    reasons.append(f"Market: {int(ep)}"); reasons.append(f"Net: {int(profit['net'])} ({(profit['margin']*100).quantize(Decimal('0.1'))}%)")
    if mc>0: reasons.insert(0,f"Warning: {mc} missing")
    if mi and mi.get("level","") not in ("","EXACT"): reasons.insert(0,f"Warning: {mi['level']}")
    
    result = {"pricingStatus":Status.COMPLETED,"estimatedMarketPrice":int(ep),"estimatedLow":int(stats.get("f_min",0)),"estimatedHigh":int(stats.get("f_max",0)),"currentBidPrice":int(buy),"breakEvenPurchasePrice":profit["bep"],"targetPurchasePrice10Margin":profit["tp10"],"targetPurchasePrice20Margin":profit["tp20"],"netProfitAtCurrentBid":int(profit["net"]),"profitMarginAtCurrentBid":profit["margin"],"roiAtCurrentBid":profit["roi"],"pricingConfidence":conf,"riskLevel":risk["level"],"riskScore":risk["score"],"decisionSignal":dec,"reasons":reasons+risk["reasons"],"riskFactors":risk["factors"],"comparableItemIds":stats.get("ids",[]),"comparableCount":cc,"missingParameterCount":mc,"matchInfo":mi or {"level":"EXACT"},"priceBreakdown":{"estimatedSellingPrice":int(ep),"currentBidPrice":int(buy),"platformFee":int(profit["fee"]),"shippingCost":int(ship),"repairReserve":int(profit["repair"]),"riskReserve":int(profit["risk"]),"netProfit":int(profit["net"])}}
    if buynow and buynow>0:
        bp = calc_profit(ep,buynow,ship); result.update({"buynowPrice":int(buynow),"netProfitAtBuynow":int(bp["net"]),"profitMarginAtBuynow":bp["margin"],"roiAtBuynow":bp["roi"]})
    return _to_dynamo(result)

def save_pricing(iid: str, result: Dict, rec: str):
    update_record(active_db, iid, {"pricingResult":result,"pricingStatus":result.get("pricingStatus",Status.FAILED),"pricedAt":datetime.now(timezone.utc).isoformat(),"purchaseRecommendation":rec})
    logger.info(f"Pricing saved: {iid} -> {rec}")

# ======================================
# Workflow (核心修复)
# ======================================

def scrape_closed(kw: str, cnt: int, force: bool = False) -> List[str]:
    """抓取已结束商品，新商品自动设为 PENDING"""
    try:
        items = scrape_auctions(kw, "closed", False)[:cnt]
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
                        "detailDescription": item.get("detailDescription", ""),
                        "detailTitle": item.get("detailTitle", ""),
                        "detailUrl": item.get("detailUrl", ""),
                        "detailScrapedAt": item.get("detailScrapedAt", ""),
                        "detailDescriptionLength": item.get("detailDescriptionLength", 0),
                        "detailScrapeStatus": item.get("detailScrapeStatus", "NOT_SCRAPED"),
                        "detailScrapeError": item.get("detailScrapeError", ""),
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

def scrape_active(kw: str, cnt: int, min_p: int = 0, force: bool = False) -> List[str]:
    """抓取活跃商品，新商品自动设为 PENDING"""
    try:
        items = scrape_auctions(kw, "active", False, min_price=min_p if min_p > 0 else None)
        if min_p > 0:
            items = [i for i in items if si(i.get("price", 0)) >= min_p]
        items = items[:cnt]
        new_count = 0
        
        for item in items:
            try:
                iid = str(item["itemId"])
                existing = get_record(active_db, iid)
                if not existing:
                    new_count += 1
                
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
                        "detailDescription": item.get("detailDescription", ""),
                        "detailTitle": item.get("detailTitle", ""),
                        "detailUrl": item.get("detailUrl", ""),
                        "detailScrapedAt": item.get("detailScrapedAt", ""),
                        "detailDescriptionLength": item.get("detailDescriptionLength", 0),
                        "detailScrapeStatus": item.get("detailScrapeStatus", "NOT_SCRAPED"),
                        "detailScrapeError": item.get("detailScrapeError", ""),
                    },
                    force=force
                )
            except Exception as e:
                logger.error(f"Save active failed itemId={item.get('itemId')}: {e}")
        
        logger.info(f"Scraped {len(items)} active items, {new_count} new")
        return [str(i["itemId"]) for i in items]
    except Exception as e:
        logger.error(f"Active scrape: {e}")
        return []

def calc_min_price(closed_ids: List[str]) -> Dict:
    prices = []
    for cid in closed_ids:
        item = get_record(closed_db, cid)
        if not item or item.get("modelStatus")!=Status.COMPLETED: continue
        if item.get("listingType")!=ListingType.MAIN_PRODUCT or item.get("parsedCondition")=="BROKEN": continue
        p = si(item.get("price",0)); 
        if p>0: prices.append(p)
    if not prices: return {"min":0}
    prices.sort(); n=len(prices)
    if n>=3:
        q1=prices[n//4]; q3=prices[n*3//4]; lo=int(q1-MAX_PRICE_DEV*(q3-q1)); hi=int(q3+MAX_PRICE_DEV*(q3-q1))
        filtered = [p for p in prices if lo<=p<=hi]
    else: filtered = prices
    if not filtered: filtered = prices
    min_price = max(1,int(sum(filtered)//len(filtered)*PRICE_MIN_RATIO))
    logger.info(f"Calculated min price: {min_price} (from {len(prices)} prices)")
    return {"min": min_price}

def execute_workflow(kw: str, ac: int, cc: int, force: bool) -> Dict:
    global _start_time; _start_time = time.time()
    result = {"keyword":kw}
    
    try:
        # Step 1: 抓取已结束商品
        check_limits()
        logger.info(f"Step 1: Scraping closed auctions for '{kw}'")
        closed_ids = scrape_closed(kw, cc, force)
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
            closed_result = batch_parse(closed_db, closed_items, build_parse_prompt, CLOSED_BATCH)
            result["closed_parsed"] = closed_result
            logger.info(f"Closed parse result: {closed_result}")
        else:
            logger.info("No closed items need parsing (all already processed or not in PENDING state)")
        
        # Step 3: 计算最低建议价格
        logger.info("Step 3: Calculating min price")
        pi = calc_min_price(closed_ids); mp = pi.get("min",0)
        result["min_price"] = mp
        
        # Step 4: 抓取活跃商品
        logger.info(f"Step 4: Scraping active auctions (min_price={mp})")
        active_ids = scrape_active(kw, ac, mp, force)
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
            active_result = batch_parse(active_db, active_items, build_parse_prompt, MODEL_BATCH)
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
        for aid in active_ids:
            try:
                check_limits()
                item = get_record(active_db, aid)
                
                if not item or item.get("modelStatus") != Status.COMPLETED:
                    continue
                if str(item.get("listingType", "")).upper() in EXCLUDED_TYPES:
                    continue
                
                # 只处理待定价的商品
                if not force and item.get("pricingStatus") != Status.PENDING:
                    continue
                
                ci, mi = find_comp(item, idx)
                stats = calc_stats(ci)
                pp = sd(item.get("price", 0))
                sh = get_shipping(item)
                bp = sd(item.get("buynowPrice")) if item.get("buynowPrice") else None
                
                pr = build_result(item, stats, pp, sh, bp, mi)
                rec = calc_decision(
                    sd(pr.get("netProfitAtCurrentBid", 0)),
                    sd(pr.get("profitMarginAtCurrentBid", 0)),
                    sd(pr.get("roiAtCurrentBid", 0)),
                    sd(pr.get("pricingConfidence", 0)),
                    pr.get("riskLevel", "HIGH"),
                    si(pr.get("comparableCount", 0)),
                    si(item.get("missingParameterCount", 0)),
                    pr.get("pricingStatus", Status.INSUFFICIENT_DATA)
                )
                save_pricing(aid, pr, rec)
                priced += 1
                
            except RuntimeError:
                raise
            except Exception as e:
                logger.error(f"Pricing {aid}: {e}")
        
        result["priced"] = priced
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
    _total_tokens = 0; _start_time = time.time()
    
    try:
        kw = norm(event.get("keyword", ""))
        if not kw:
            return {"statusCode": 400, "body": json.dumps({"error": "keyword required"})}
        
        ac = max(1, min(int(event.get("active_count", 100)), 100))
        cc_val = max(1, min(int(event.get("closed_count", 100)), 100))
        force = str(event.get("force_reprocess", "")).lower() in ("true", "1", "yes")
        
        logger.info(f"Starting workflow: kw={kw}, active={ac}, closed={cc_val}, force={force}")
        result = execute_workflow(kw, ac, cc_val, force)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False, default=str)
        }
    except Exception as e:
        logger.error(f"Handler: {e}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
