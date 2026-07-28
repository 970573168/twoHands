以下是完整的修改后代码，主要变更：

1. **放宽匹配条件**：variant（颜色/运营商）不参与价格匹配
2. **存储容量归一化**：PC内存+硬盘格式标准化
3. **只保留影响价格的关键参数**

```python
"""
Yahoo Auction 商品分析工作流 Lambda (多API模式切换版)
支持通过环境变量 AI_MODE 切换 gemini / doubao / openai
修改：先搜索closed分析价格，再搜索active时设定价格不低于平均价格
放宽匹配条件：只保留一定会影响价格的参数
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


# ==================== 环境变量辅助函数 ====================

def _env_str(key: str, default: str) -> str:
    value = os.getenv(key, "")
    return value if value else default


def _env_int(key: str, default: int) -> int:
    try:
        value = os.getenv(key, "")
        if not value:
            return default
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"环境变量 {key} 值无效，使用默认值 {default}")
        return default


def _env_decimal(key: str, default: str) -> Decimal:
    try:
        value = os.getenv(key, "")
        if not value:
            return Decimal(default)
        return Decimal(value)
    except Exception:
        logger.warning(f"环境变量 {key} 值无效，使用默认值 {default}")
        return Decimal(default)


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key, "")
    if not value:
        return default
    return value.lower() in ("true", "1", "yes", "y")


# ============ 基础环境变量 ============
ENVIRONMENT = _env_str("ENVIRONMENT", "dev")
TABLE_NAME_ACTIVE = _env_str("TABLE_NAME_ACTIVE", "YahooAuctionActiveItems")
TABLE_NAME_CLOSED = _env_str("TABLE_NAME_CLOSED", "YahooAuctionItems")
PRODUCT_TABLE_NAME = _env_str("PRODUCT_TABLE_NAME", "ProductCatalog-dev")

# ============ AI 模式切换配置 ============
AI_MODE = _env_str("AI_MODE", "doubao")

GEMINI_API_KEY = _env_str("GEMINI_API_KEY", "")
GEMINI_MODEL = _env_str("GEMINI_MODEL", "gemini-2.0-flash-latest")
GEMINI_URL = _env_str("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-latest:generateContent")
GEMINI_TIMEOUT = _env_int("GEMINI_TIMEOUT", 60)
GEMINI_MAX_TOKENS = _env_int("GEMINI_MAX_TOKENS", 4000)

DOUBAO_API_KEY = _env_str("DOUBAO_API_KEY", "")
DOUBAO_MODEL = _env_str("DOUBAO_MODEL", "qwen-plus-character")
DOUBAO_URL = _env_str("DOUBAO_URL", "https://ws-8lxmxlbemcgcus5u.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions")
DOUBAO_TIMEOUT = _env_int("DOUBAO_TIMEOUT", 90)
DOUBAO_MAX_TOKENS = _env_int("DOUBAO_MAX_TOKENS", 6000)

OPENAI_API_KEY = _env_str("OPENAI_API_KEY", "")
OPENAI_MODEL = _env_str("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = _env_str("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_TIMEOUT = _env_int("OPENAI_TIMEOUT", 60)
OPENAI_MAX_TOKENS = _env_int("OPENAI_MAX_TOKENS", 4000)

AI_FAILOVER_COOLDOWN = _env_int("AI_FAILOVER_COOLDOWN", 300)

# ============ 工作流配置 ============
DEFAULT_ACTIVE_COUNT = _env_int("DEFAULT_ACTIVE_COUNT", 100)
DEFAULT_CLOSED_COUNT = _env_int("DEFAULT_CLOSED_COUNT", 100)
MAX_ACTIVE_ITEMS = _env_int("MAX_ACTIVE_ITEMS", 100)
MAX_CLOSED_ITEMS = _env_int("MAX_CLOSED_ITEMS", 100)

MODEL_PARSE_BATCH_SIZE = _env_int("MODEL_PARSE_BATCH_SIZE", 100)
CLOSED_PARSE_BATCH_SIZE = _env_int("CLOSED_PARSE_BATCH_SIZE", 100)

BUY_MARGIN_THRESHOLD = _env_decimal("BUY_MARGIN_THRESHOLD", "0.20")
REVIEW_MARGIN_THRESHOLD = _env_decimal("REVIEW_MARGIN_THRESHOLD", "0.10")
HIGH_CONFIDENCE_COMPARABLE_COUNT = _env_int("HIGH_CONFIDENCE_COMPARABLE_COUNT", 10)
MEDIUM_CONFIDENCE_COMPARABLE_COUNT = _env_int("MEDIUM_CONFIDENCE_COMPARABLE_COUNT", 5)

AI_REQUEST_TIMEOUT = _env_int("AI_REQUEST_TIMEOUT", 90)
AI_MAX_RETRIES = _env_int("AI_MAX_RETRIES", 3)
REQUEST_INTERVAL = float(_env_str("REQUEST_INTERVAL", "1.0"))
INCLUDE_PAYPAY = _env_bool("INCLUDE_PAYPAY", False)

MAX_TOTAL_TOKENS = _env_int("MAX_TOTAL_TOKENS", 50000)
LAMBDA_TIMEOUT_SECONDS = _env_int("LAMBDA_TIMEOUT_SECONDS", 840)
LAMBDA_TIMEOUT_BUFFER = _env_int("LAMBDA_TIMEOUT_BUFFER", 30)

EXPECTED_SELLING_FEE_RATE = _env_decimal("EXPECTED_SELLING_FEE_RATE", "0.10")
DEFAULT_SHIPPING_COST = _env_decimal("DEFAULT_SHIPPING_COST", "1500")
DEFAULT_REPAIR_RESERVE_RATE = _env_decimal("DEFAULT_REPAIR_RESERVE_RATE", "0.05")
MIN_COMPARABLE_COUNT = _env_int("MIN_COMPARABLE_COUNT", 3)
MAX_PRICE_DEVIATION = _env_decimal("MAX_PRICE_DEVIATION", "1.5")
RISK_RESERVE_RATE = _env_decimal("RISK_RESERVE_RATE", "0.03")

ACTIVE_PRICE_MIN_RATIO = _env_decimal("ACTIVE_PRICE_MIN_RATIO", "1.0")

RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

dynamodb = boto3.resource("dynamodb")
active_table = dynamodb.Table(TABLE_NAME_ACTIVE)
closed_table = dynamodb.Table(TABLE_NAME_CLOSED)
product_table = dynamodb.Table(PRODUCT_TABLE_NAME)
secretsmanager = boto3.client("secretsmanager")

_total_tokens_used = 0
_lambda_start_time = None

_ai_mode_state = {
    "current_mode": None,
    "failed_modes": {},
}


# ==================== API 调用日志记录器 ====================

class APILogger:
    def __init__(self):
        self.calls: List[Dict] = []
        self.sequence = 0
    
    def log_request(self, api_name: str, model: str, url: str, request_body: Dict, timeout: int) -> int:
        self.sequence += 1
        call_log = {
            "sequence": self.sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_name": api_name, "model": model, "url": url[:150], "timeout": timeout,
            "request": {
                "prompt_length": self._get_prompt_length(request_body),
                "max_tokens": request_body.get("generationConfig", {}).get("maxOutputTokens") or request_body.get("max_tokens", 0),
                "body_preview": self._truncate_body(request_body)
            },
            "response": None, "status": "pending"
        }
        self.calls.append(call_log)
        return self.sequence
    
    def _get_prompt_length(self, body: Dict) -> int:
        if "contents" in body:
            parts = body.get("contents", [{}])[0].get("parts", [{}])
            return len(parts[0].get("text", "")) if parts else 0
        elif "messages" in body:
            return sum(len(m.get("content", "")) for m in body.get("messages", []))
        return 0
    
    def log_response(self, seq: int, status_code: int, response_body: Optional[Dict],
                     tokens_used: int, duration_ms: float, error: str = None,
                     finish_reason: str = None, content_length: int = 0):
        for call in self.calls:
            if call["sequence"] == seq:
                call["status"] = "success" if error is None else "failed"
                call["response"] = {
                    "status_code": status_code, "tokens_used": tokens_used,
                    "duration_ms": round(duration_ms, 2), "finish_reason": finish_reason,
                    "content_length": content_length, "error": error,
                    "response_preview": self._truncate_response(response_body) if response_body else None
                }
                break
    
    def _truncate_body(self, body: Dict) -> Dict:
        truncated = {}
        for key in body:
            if key == "contents" and isinstance(body[key], list):
                truncated[key] = [{"parts": [{"text": (str(p.get("text", ""))[:200] + "...") if len(str(p.get("text", ""))) > 200 else str(p.get("text", ""))} for p in item.get("parts", [])]} for item in body[key][:2]]
            elif key == "messages":
                truncated[key] = [{"role": m.get("role"), "content": (str(m.get("content", ""))[:200] + "...") if len(str(m.get("content", ""))) > 200 else str(m.get("content", ""))} for m in body[key][-2:]]
            elif key in ("generationConfig", "model", "temperature", "max_tokens", "response_format"):
                truncated[key] = body[key]
        return truncated
    
    def _truncate_response(self, response: Dict) -> Dict:
        truncated = {}
        if "candidates" in response:
            truncated["candidates_count"] = len(response.get("candidates", []))
            if response.get("candidates"):
                first = response["candidates"][0]
                truncated["finishReason"] = first.get("finishReason")
                parts = first.get("content", {}).get("parts", [{}])
                content = parts[0].get("text", "") if parts else ""
                truncated["content_preview"] = (content[:300] + "...") if len(content) > 300 else content
        elif "choices" in response:
            truncated["choices_count"] = len(response.get("choices", []))
            if response.get("choices"):
                first = response["choices"][0]
                truncated["finish_reason"] = first.get("finish_reason")
                content = first.get("message", {}).get("content", "")
                truncated["content_preview"] = (content[:300] + "...") if len(content) > 300 else content
        if "usageMetadata" in response: truncated["usage"] = response["usageMetadata"]
        if "usage" in response: truncated["usage"] = response["usage"]
        return truncated
    
    def get_summary(self) -> Dict:
        total = len(self.calls)
        success = sum(1 for c in self.calls if c["status"] == "success")
        failed = sum(1 for c in self.calls if c["status"] == "failed")
        total_tokens = sum(c.get("response", {}).get("tokens_used", 0) for c in self.calls if c.get("response"))
        total_duration = sum(c.get("response", {}).get("duration_ms", 0) for c in self.calls if c.get("response"))
        by_api = {}
        for call in self.calls:
            api_name = call["api_name"]
            if api_name not in by_api:
                by_api[api_name] = {"total": 0, "success": 0, "failed": 0, "tokens": 0, "duration_ms": 0}
            by_api[api_name]["total"] += 1
            if call["status"] == "success": by_api[api_name]["success"] += 1
            else: by_api[api_name]["failed"] += 1
            resp = call.get("response") or {}
            by_api[api_name]["tokens"] += resp.get("tokens_used", 0)
            by_api[api_name]["duration_ms"] += resp.get("duration_ms", 0)
        return {
            "total_calls": total, "success": success, "failed": failed,
            "total_tokens": total_tokens, "total_duration_ms": round(total_duration, 2),
            "total_duration_seconds": round(total_duration / 1000, 2),
            "by_api": {name: {"total": s["total"], "success": s["success"], "failed": s["failed"],
                              "tokens": s["tokens"], "duration_ms": round(s["duration_ms"], 2),
                              "avg_duration_ms": round(s["duration_ms"] / s["total"], 2) if s["total"] > 0 else 0}
                       for name, s in by_api.items()}
        }


# ==================== 阶段计时器 ====================

class StageTimer:
    def __init__(self):
        self.stages: Dict[str, Dict] = OrderedDict()
        self.current_stage = None
        self.stage_start = None
        self.overall_start = time.time()
    
    def start(self, stage_name: str):
        if self.current_stage: self.end()
        self.current_stage = stage_name
        self.stage_start = time.time()
        logger.info(f"⏱️ 阶段开始: {stage_name}")
    
    def end(self):
        if not self.current_stage: return
        elapsed = time.time() - self.stage_start
        if self.current_stage not in self.stages:
            self.stages[self.current_stage] = {"count": 0, "total_seconds": 0, "min_seconds": float('inf'), "max_seconds": 0, "instances": []}
        stage = self.stages[self.current_stage]
        stage["count"] += 1
        stage["total_seconds"] += elapsed
        stage["min_seconds"] = min(stage["min_seconds"], elapsed)
        stage["max_seconds"] = max(stage["max_seconds"], elapsed)
        stage["instances"].append({"timestamp": datetime.now(timezone.utc).isoformat(), "duration_seconds": round(elapsed, 3)})
        logger.info(f"⏱️ 阶段结束: {self.current_stage} - 耗时 {elapsed:.2f}秒")
        self.current_stage = None
        self.stage_start = None
    
    def get_summary(self) -> Dict:
        if self.current_stage: self.end()
        total_elapsed = time.time() - self.overall_start
        stage_summary = {}
        for name, stats in self.stages.items():
            stage_summary[name] = {"count": stats["count"], "total_seconds": round(stats["total_seconds"], 2),
                                   "avg_seconds": round(stats["total_seconds"] / stats["count"], 2) if stats["count"] > 0 else 0,
                                   "min_seconds": round(stats["min_seconds"], 2) if stats["min_seconds"] != float('inf') else 0,
                                   "max_seconds": round(stats["max_seconds"], 2)}
        return {"total_elapsed_seconds": round(total_elapsed, 2), "stages": stage_summary,
                "stage_percentages": {name: round((stats["total_seconds"] / total_elapsed * 100), 1) if total_elapsed > 0 else 0
                                      for name, stats in self.stages.items()}}


# ==================== 全局实例 ====================

_api_logger: Optional[APILogger] = None
_stage_timer: Optional[StageTimer] = None

def get_api_logger() -> APILogger:
    global _api_logger
    if _api_logger is None: _api_logger = APILogger()
    return _api_logger

def get_stage_timer() -> StageTimer:
    global _stage_timer
    if _stage_timer is None: _stage_timer = StageTimer()
    return _stage_timer


# ==================== AI 配置管理 ====================

def _get_api_key_from_secrets(mode: str) -> str:
    env = ENVIRONMENT
    secret_names = [f"{mode}-api-key-{env}", f"{mode}-api-key", f"{mode}/api-key/{env}"]
    for secret_name in secret_names:
        try:
            response = secretsmanager.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString", "")
            if not secret_string: continue
            try:
                secret_dict = json.loads(secret_string)
                key = (secret_dict.get("apiKey") or secret_dict.get("api_key") or secret_dict.get("key") or
                       secret_dict.get("GEMINI_API_KEY") or secret_dict.get("DOUBAO_API_KEY") or
                       secret_dict.get("OPENAI_API_KEY") or "")
                if key:
                    logger.info(f"✅ 成功从 Secret '{secret_name}' 获取 Key (mode={mode})")
                    return key
            except json.JSONDecodeError:
                key = secret_string.strip()
                if key:
                    logger.info(f"✅ 成功从 Secret '{secret_name}' 获取 Key (mode={mode})")
                    return key
        except Exception as e:
            logger.debug(f"Secret '{secret_name}' 获取失败: {type(e).__name__}")
    logger.warning(f"⚠️ 无法从任何 Secret 获取 mode '{mode}' 的 Key")
    return ""


def get_ai_config(mode: str = None) -> Dict:
    if mode is None: mode = AI_MODE
    configs = {
        "gemini": {"name": "gemini", "type": "gemini", "url": GEMINI_URL, "key": GEMINI_API_KEY or _get_api_key_from_secrets("gemini"),
                   "model": GEMINI_MODEL, "timeout": GEMINI_TIMEOUT, "max_tokens": GEMINI_MAX_TOKENS},
        "doubao": {"name": "doubao", "type": "openai_compatible", "url": DOUBAO_URL, "key": DOUBAO_API_KEY or _get_api_key_from_secrets("doubao"),
                   "model": DOUBAO_MODEL, "timeout": DOUBAO_TIMEOUT, "max_tokens": DOUBAO_MAX_TOKENS},
        "openai": {"name": "openai", "type": "openai_compatible", "url": OPENAI_URL, "key": OPENAI_API_KEY or _get_api_key_from_secrets("openai"),
                   "model": OPENAI_MODEL, "timeout": OPENAI_TIMEOUT, "max_tokens": OPENAI_MAX_TOKENS}
    }
    if mode not in configs:
        logger.warning(f"未知的 AI_MODE: {mode}，使用 gemini")
        mode = "gemini"
    return configs[mode]


def get_available_ai_config() -> Optional[Dict]:
    fallback_order = ["gemini", "doubao", "openai"]
    ordered_modes = [AI_MODE] + [m for m in fallback_order if m != AI_MODE] if AI_MODE in fallback_order else fallback_order
    now = time.time()
    for mode in ordered_modes:
        if mode in _ai_mode_state["failed_modes"]:
            fail_time = _ai_mode_state["failed_modes"][mode]
            if now - fail_time < AI_FAILOVER_COOLDOWN:
                logger.info(f"AI 模式 '{mode}' 冷却中，跳过")
                continue
            else: del _ai_mode_state["failed_modes"][mode]
        config = get_ai_config(mode)
        if config["key"]:
            logger.info(f"✅ 选择 AI 模式: '{mode}' (model={config['model']})")
            return config
        else: logger.warning(f"AI 模式 '{mode}' 没有可用的 API Key")
    logger.error("❌ 所有 AI 模式均不可用")
    return None


def mark_ai_mode_failed(mode: str, error: str = ""):
    _ai_mode_state["failed_modes"][mode] = time.time()
    logger.warning(f"❌ AI 模式 '{mode}' 标记为故障")

def reset_ai_state():
    _ai_mode_state["failed_modes"].clear()


# ==================== Token 和超时控制 ====================

def get_elapsed_seconds():
    return 0 if _lambda_start_time is None else time.time() - _lambda_start_time

def get_remaining_seconds():
    return max(0, LAMBDA_TIMEOUT_SECONDS - get_elapsed_seconds() - LAMBDA_TIMEOUT_BUFFER)

def check_timeout():
    if get_remaining_seconds() <= 0:
        raise RuntimeError(f"Lambdaタイムアウト: {get_elapsed_seconds():.1f}秒")

def check_token_limit():
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(f"Token使用量が上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}")

def check_limits():
    check_token_limit()
    check_timeout()

def update_token_usage(usage):
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        logger.info(f"Token使用量: +{total}, 合計={_total_tokens_used}/{MAX_TOTAL_TOKENS}")


# ==================== 工具函数 ====================

def to_dynamodb_value(value: Any) -> Any:
    if isinstance(value, float): return Decimal(str(value))
    if isinstance(value, Decimal): return value
    if isinstance(value, dict): return {str(key): to_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list): return [to_dynamodb_value(item) for item in value]
    if isinstance(value, tuple): return [to_dynamodb_value(item) for item in value]
    if isinstance(value, set): return {str(item) for item in value if str(item)}
    if isinstance(value, str): return value
    return value

def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        if isinstance(value, Decimal): return value
        return Decimal(str(value))
    except: return default

def safe_int(value: Any, default: int = 0) -> int:
    try: return int(value)
    except (ValueError, TypeError): return default

def normalize(value: str) -> str:
    if not value: return ""
    value = str(value).strip()
    value = value.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ))
    return re.sub(r"\s+", " ", value)


def normalize_storage(value: Any) -> str:
    """归一化存储容量，支持PC内存+硬盘混合格式"""
    if value is None: return ""
    text = normalize(str(value)).upper()
    text = re.sub(r"\s+", " ", text).strip()
    
    # 标准存储格式：纯数字+单位
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(GB|G|TB|T)", text)
    if match:
        amount = match.group(1)
        unit = "GB" if match.group(2) in ("G", "GB") else "TB"
        return f"{amount}{unit}"
    
    # 提取所有容量信息
    capacity_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(GB|G|TB|T)', text)
    if capacity_matches:
        capacities = []
        for amount, unit in capacity_matches:
            unit = "GB" if unit in ("G", "GB") else "TB"
            capacities.append(f"{amount}{unit}")
        return " ".join(capacities)
    
    # PC 格式：提取 RAM/SSD/HDD
    ram_match = re.search(r'(?:RAM|メモリ)\s*(\d+)\s*GB', text)
    ssd_match = re.search(r'(?:SSD|M\.2\s*SSD)\s*(\d+)\s*GB', text)
    hdd_match = re.search(r'(?:HDD)\s*(\d+)\s*(?:GB|TB)', text)
    
    parts = []
    if ram_match: parts.append(f"RAM{ram_match.group(1)}GB")
    if ssd_match: parts.append(f"SSD{ssd_match.group(1)}GB")
    if hdd_match:
        unit = "TB" if "TB" in text else "GB"
        parts.append(f"HDD{hdd_match.group(1)}{unit}")
    if parts: return " ".join(parts)
    
    return text


def normalize_storage_for_matching(storage: str) -> str:
    """归一化存储容量用于匹配，忽略颜色/运营商等不影响价格的修饰词"""
    if not storage: return ""
    text = normalize(storage).upper()
    text = re.sub(r"\s+", " ", text).strip()
    
    # 标准存储格式
    if re.fullmatch(r"\d+(?:\.\d+)?\s*(GB|TB|G|T)", text):
        amount = re.search(r"(\d+(?:\.\d+)?)", text).group(1)
        unit = "GB" if "G" in text else "TB"
        return f"{amount}{unit}"
    
    # 提取所有数字+单位
    capacity_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(GB|TB|G|T)', text)
    if capacity_matches:
        capacities = []
        seen = set()
        for amount, unit in capacity_matches:
            unit = "GB" if unit in ("G", "GB") else "TB"
            cap = f"{amount}{unit}"
            if cap not in seen:
                capacities.append(cap)
                seen.add(cap)
        return " ".join(sorted(capacities, key=lambda x: (x[-2:], float(re.search(r'[\d.]+', x).group())), reverse=True))
    
    # PC 格式
    ram_match = re.search(r'(?:RAM|メモリ|メモリー)?\s*(\d+)\s*GB', text)
    ssd_match = re.search(r'(?:SSD|M\.2\s*SSD)\s*(\d+)\s*GB', text)
    hdd_match = re.search(r'(?:HDD)\s*(\d+)\s*(?:GB|TB)', text)
    
    parts = []
    if ram_match: parts.append(f"RAM{ram_match.group(1)}GB")
    if ssd_match: parts.append(f"SSD{ssd_match.group(1)}GB")
    if hdd_match:
        unit = "TB" if "TB" in text else "GB"
        parts.append(f"HDD{hdd_match.group(1)}{unit}")
    if parts: return " ".join(parts)
    
    # 清理非容量信息
    text = re.sub(r'(?:WI-FI|CELLULAR|WIFI|セルラー|SIMフリー|ドコモ|AU|SOFTBANK|KDDI)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool): return value
    if isinstance(value, str): return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def determine_shipping_status(shipping_text: str) -> Dict:
    if not shipping_text or not shipping_text.strip():
        return {"isFreeShipping": False, "shippingStatus": "UNKNOWN", "shippingText": ""}
    text = shipping_text.strip().lower()
    free_keywords = ["送料無料", "送料込み", "送料込", "送料無", "送料0", "送料ゼロ",
                     "free shipping", "shipping free", "shipping included",
                     "free", "0円", "0円送料", "出品者負担"]
    for keyword in free_keywords:
        if keyword.lower() in text.lower():
            return {"isFreeShipping": True, "shippingStatus": "FREE", "shippingText": shipping_text.strip()}
    return {"isFreeShipping": False, "shippingStatus": "CHARGED", "shippingText": shipping_text.strip()}


def generate_pricing_model_key(brand: str, model_name: str, storage: str = "", variant: str = "") -> str:
    """生成价格匹配键。variant（颜色/运营商）不参与匹配，只保留品牌+型号+存储容量"""
    normalized_brand = normalize(brand).upper()
    normalized_model = normalize(model_name).upper()
    normalized_storage = normalize_storage_for_matching(storage)
    
    parts = [normalized_brand, normalized_model]
    if normalized_storage: parts.append(normalized_storage)
    
    combined = " ".join(parts)
    combined = re.sub(r"[^A-Z0-9\s+\-/]", " ", combined)
    combined = re.sub(r"\s+", " ", combined).strip()
    return combined


def model_contains_variant(model_name: str, variant: str) -> bool:
    if not model_name or not variant: return False
    model_tokens = model_name.upper().split()
    variant_tokens = variant.upper().split()
    if len(variant_tokens) > len(model_tokens): return False
    for start in range(0, len(model_tokens) - len(variant_tokens) + 1):
        if model_tokens[start:start + len(variant_tokens)] == variant_tokens: return True
    return False


def response(status_code: int, body: Dict) -> Dict:
    return {"statusCode": status_code, "body": json.dumps(body, ensure_ascii=False, default=str)}


def update_product_status(product_pk: str, status: str, error: str = None):
    if not product_pk: return
    try:
        now = int(time.time())
        today = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
        update_parts = ["last_analysis_status = :status", "last_scanned_date = :today", "last_scanned_at = :now"]
        values = {":status": status, ":today": today, ":now": now}
        if error:
            update_parts.append("last_analysis_error = :error")
            values[":error"] = str(error)[:500]
        product_table.update_item(
            Key={"PK": product_pk, "SK": "META"},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeValues=values
        )
        logger.info(f"PRODUCT 状态已更新: {product_pk} -> {status}")
    except Exception as e:
        logger.error(f"PRODUCT 状态更新失败: {product_pk} -> {e}")


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    global _total_tokens_used, _lambda_start_time, _api_logger, _stage_timer
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    _api_logger = None
    _stage_timer = None
    reset_ai_state()
    
    try:
        keyword = normalize(event.get("keyword", ""))
        if not keyword:
            return response(400, {"error": "keywordは必須です"})
        
        try:
            active_count = int(event.get("active_count", DEFAULT_ACTIVE_COUNT))
            closed_count = int(event.get("closed_count", DEFAULT_CLOSED_COUNT))
        except (ValueError, TypeError):
            return response(400, {"error": "active_count、closed_countは有効な整数である必要があります"})
        
        force_reprocess = parse_bool(event.get("force_reprocess", False))
        product_pk = event.get("product_pk", "")
        
        active_count = max(1, min(active_count, MAX_ACTIVE_ITEMS))
        closed_count = max(1, min(closed_count, MAX_CLOSED_ITEMS))
        
        logger.info(f"商品分析ワークフロー開始: keyword='{keyword}', AI_MODE='{AI_MODE}'")
        
        result = execute_workflow(
            keyword=keyword, active_count=active_count,
            closed_count=closed_count, force_reprocess=force_reprocess
        )
        
        result["execution_stats"] = {
            "total_tokens_used": _total_tokens_used, "token_limit": MAX_TOTAL_TOKENS,
            "elapsed_seconds": get_elapsed_seconds(), "remaining_seconds": get_remaining_seconds(),
            "ai_mode": AI_MODE,
        }
        if _api_logger: result["api_call_logs_summary"] = _api_logger.get_summary()
        if _stage_timer: result["stage_times"] = _stage_timer.get_summary()
        
        if product_pk:
            if result.get("status") == "COMPLETED": update_product_status(product_pk, "COMPLETED")
            elif result.get("status") in ("PARTIAL_COMPLETED", "PARTIAL_FAILED"): update_product_status(product_pk, "PARTIAL", str(result.get("errors", [])))
            elif result.get("status") == "INTERRUPTED": update_product_status(product_pk, "INTERRUPTED", result.get("interrupt_reason", "Unknown"))
            elif result.get("status") == "NO_ACTIVE_RESULTS": update_product_status(product_pk, "NO_RESULTS", "没有找到活跃商品")
            elif result.get("status") == "NO_CLOSED_RESULTS": update_product_status(product_pk, "NO_CLOSED_RESULTS", "没有找到已结束商品")
            else: update_product_status(product_pk, "FAILED", str(result.get("errors", [])))
        
        return response(200, result)
        
    except Exception as e:
        logger.error(f"ワークフロー実行失敗: {e}", exc_info=True)
        product_pk = event.get("product_pk", "")
        if product_pk: update_product_status(product_pk, "FAILED", str(e))
        return response(500, {"error": "内部エラー", "details": str(e)})


def execute_workflow(keyword: str, active_count: int, closed_count: int, force_reprocess: bool) -> Dict:
    """修改后的工作流：先搜索closed分析价格，再搜索active时设定价格不低于平均价格"""
    global _api_logger, _stage_timer
    _api_logger = APILogger()
    _stage_timer = StageTimer()
    start_time = time.time()
    
    workflow_result = {
        "keyword": keyword,
        "closed_search_count": 0, "closed_parsed": 0, "closed_excluded": 0,
        "closed_review_required": 0, "closed_parse_failed": 0,
        "active_search_count": 0, "active_parsed": 0, "active_excluded": 0,
        "active_review_required": 0, "active_parse_failed": 0,
        "pricing_attempted": 0, "pricing_completed": 0,
        "pricing_insufficient_data": 0, "pricing_failed": 0,
        "price_filter_info": {}, "errors": []
    }
    
    try:
        check_limits()
        
        # ============ 第一步：closed 搜索 ============
        _stage_timer.start("01_closed_search")
        closed_item_ids = scrape_and_save_closed_once(keyword=keyword, count=closed_count, force_reprocess=force_reprocess)
        workflow_result["closed_search_count"] = len(closed_item_ids)
        _stage_timer.end()
        
        if not closed_item_ids:
            workflow_result["status"] = "NO_CLOSED_RESULTS"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = _stage_timer.get_summary()
            workflow_result["api_call_logs_summary"] = _api_logger.get_summary()
            return workflow_result
        
        # ============ 第二步：closed AI 解析 ============
        _stage_timer.start("02_closed_ai_parse")
        closed_items = get_closed_items_by_ids(closed_item_ids, only_pending=not force_reprocess)
        if closed_items:
            cr = batch_parse_closed_models(closed_items)
            for k in ("parsed", "excluded", "review_required", "failed"):
                workflow_result[f"closed_{k}"] = cr.get(k, 0)
            workflow_result["errors"].extend(cr.get("errors", []))
        _stage_timer.end()
        
        # ============ 第三步：计算active最低价格 ============
        _stage_timer.start("03_price_filter_calculation")
        price_filter_info = calculate_active_min_price_from_closed(closed_item_ids)
        workflow_result["price_filter_info"] = price_filter_info
        _stage_timer.end()
        
        min_price = price_filter_info.get("min_price", 0)
        logger.info(f"价格筛选: active商品价格不低于 {min_price}円")
        
        # ============ 第四步：active 搜索（价格不低于平均价） ============
        _stage_timer.start("04_active_search_with_min_price")
        active_item_ids = scrape_and_save_active_with_min_price(
            keyword=keyword, count=active_count, min_price=min_price, force_reprocess=force_reprocess
        )
        workflow_result["active_search_count"] = len(active_item_ids)
        _stage_timer.end()
        
        if not active_item_ids:
            workflow_result["status"] = "NO_ACTIVE_RESULTS"
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = _stage_timer.get_summary()
            workflow_result["api_call_logs_summary"] = _api_logger.get_summary()
            return workflow_result
        
        # ============ 第五步：active AI 解析 ============
        _stage_timer.start("05_active_ai_parse")
        active_items = get_active_items_by_ids(active_item_ids, only_pending=not force_reprocess)
        if active_items:
            ar = batch_parse_models(active_items)
            for k in ("parsed", "excluded", "review_required", "failed"):
                workflow_result[f"active_{k}"] = ar.get(k, 0)
            workflow_result["errors"].extend(ar.get("errors", []))
        _stage_timer.end()
        
        # ============ 第六步：价格评估 ============
        _stage_timer.start("06_price_analysis")
        active_items_for_pricing = get_unpriced_items_for_ids(
            active_item_ids, require_model_completed=True, include_completed=force_reprocess, limit=active_count
        )
        if active_items_for_pricing:
            pr = batch_price_analysis(active_items_for_pricing, allowed_closed_item_ids=set(closed_item_ids))
            for k in ("attempted", "completed", "insufficient_data", "failed"):
                workflow_result[f"pricing_{k}"] = pr.get(k, 0)
        _stage_timer.end()
        
        # 最终状态
        if workflow_result["pricing_completed"] > 0: final_status = "COMPLETED"
        elif workflow_result["pricing_insufficient_data"] > 0 or workflow_result["active_excluded"] > 0: final_status = "PARTIAL_COMPLETED"
        elif workflow_result["active_parse_failed"] > 0: final_status = "PARTIAL_FAILED"
        else: final_status = "COMPLETED"
        
        workflow_result["status"] = final_status
        workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
        workflow_result["stage_times"] = _stage_timer.get_summary()
        workflow_result["api_call_logs_summary"] = _api_logger.get_summary()
        
        logger.info("ワークフロー完了: %s", json.dumps(workflow_result, ensure_ascii=False, default=str))
        return workflow_result
        
    except RuntimeError as exc:
        error_message = str(exc)
        if any(kw in error_message for kw in ["Token使用量が上限", "Lambdaタイムアウト", "残り時間不足"]):
            workflow_result["status"] = "INTERRUPTED"
            workflow_result["interrupt_reason"] = error_message
            workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
            workflow_result["stage_times"] = _stage_timer.get_summary() if _stage_timer else {}
            workflow_result["api_call_logs_summary"] = _api_logger.get_summary() if _api_logger else {}
            return workflow_result
        raise
    except Exception as exc:
        logger.error(f"ワークフロー実行失敗: {exc}", exc_info=True)
        workflow_result["status"] = "FAILED"
        workflow_result["errors"].append(str(exc))
        workflow_result["elapsed_seconds"] = round(time.time() - start_time, 1)
        workflow_result["stage_times"] = _stage_timer.get_summary() if _stage_timer else {}
        workflow_result["api_call_logs_summary"] = _api_logger.get_summary() if _api_logger else {}
        return workflow_result


# ==================== 价格筛选 ====================

def calculate_active_min_price_from_closed(closed_item_ids: List[str]) -> Dict:
    all_prices = []
    for item_id in closed_item_ids:
        try:
            result = closed_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item: continue
            if item.get("modelStatus") != "COMPLETED": continue
            if item.get("isComparable") is not True: continue
            if item.get("listingType") != "MAIN_PRODUCT": continue
            if item.get("parsedCondition") == "BROKEN": continue
            price = safe_int(item.get("price", 0))
            if price > 0: all_prices.append(price)
        except Exception as e:
            logger.error(f"读取closed商品价格失败 {item_id}: {e}")
    
    if not all_prices:
        return {"min_price": 0, "avg_price": 0, "median_price": 0, "comparable_count": 0, "all_prices": [], "status": "INSUFFICIENT_DATA"}
    
    all_prices.sort()
    total_count = len(all_prices)
    
    if total_count >= 3:
        q1 = all_prices[total_count // 4]
        q3 = all_prices[total_count * 3 // 4]
        iqr = q3 - q1
        lower_bound = int(q1 - MAX_PRICE_DEVIATION * iqr)
        upper_bound = int(q3 + MAX_PRICE_DEVIATION * iqr)
        filtered_prices = [p for p in all_prices if lower_bound <= p <= upper_bound]
    else:
        filtered_prices = all_prices
    
    if not filtered_prices: filtered_prices = all_prices
    avg_price = sum(filtered_prices) // len(filtered_prices)
    min_price = max(1, int(avg_price * ACTIVE_PRICE_MIN_RATIO))
    
    return {"min_price": min_price, "avg_price": avg_price, "median_price": sorted(filtered_prices)[len(filtered_prices)//2],
            "comparable_count": len(filtered_prices), "total_closed_with_price": total_count,
            "excluded_outliers": total_count - len(filtered_prices), "all_prices": all_prices,
            "filtered_prices": filtered_prices, "price_range": f"{min(all_prices)} ~ {max(all_prices)}", "status": "SUCCESS"}


# ==================== Active 搜索 ====================

def scrape_and_save_active_with_min_price(keyword: str, count: int = 100, min_price: int = 0, force_reprocess: bool = False) -> List[str]:
    logger.info(f"active搜索（最低价 {min_price}円以上）: keyword='{keyword}', count={count}")
    try:
        items = scrape_auctions(keyword=keyword, auction_type="active", include_paypay=INCLUDE_PAYPAY, min_price=min_price if min_price > 0 else None)
        if min_price > 0: items = [item for item in items if safe_int(item.get("price", 0)) >= min_price]
        items = items[:count]
        saved_ids = []
        for item in items:
            try:
                upsert_active_item(item=item, keyword=keyword, force_reprocess=force_reprocess)
                saved_ids.append(str(item["itemId"]))
            except Exception as exc:
                logger.error(f"active商品保存失敗 {item.get('itemId')}: {exc}")
        logger.info(f"active搜索完成（{min_price}円以上）、{len(saved_ids)} 件保存")
        return saved_ids
    except Exception as exc:
        logger.error(f"active搜索（价格筛选）失败: {exc}", exc_info=True)
        try: return scrape_and_save_active(keyword=keyword, count=count, force_reprocess=force_reprocess)
        except Exception as exc2:
            logger.error(f"降级搜索也失败: {exc2}", exc_info=True)
            return []


def scrape_and_save_active(keyword: str, count: int = 100, force_reprocess: bool = False) -> List[str]:
    logger.info(f"active搜索（无价格筛选）: keyword='{keyword}', count={count}")
    try:
        items = scrape_auctions(keyword, "active", INCLUDE_PAYPAY)
        items = items[:count]
        saved_ids = []
        for item in items:
            try:
                upsert_active_item(item=item, keyword=keyword, force_reprocess=force_reprocess)
                saved_ids.append(str(item["itemId"]))
            except Exception as exc:
                logger.error(f"active商品保存失敗 {item.get('itemId')}: {exc}")
        return saved_ids
    except Exception as exc:
        logger.error(f"active搜索失败: {exc}", exc_info=True)
        return []


def upsert_active_item(item: Dict, keyword: str, force_reprocess: bool = False):
    now = datetime.now(timezone.utc)
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    
    set_parts = [
        "itemType = :item_type", "title = :title", "price = :price", "bidCount = :bid_count",
        "endTime = :end_time", "sellerId = :seller_id", "sellerRating = :seller_rating",
        "sellerType = :seller_type", "prefecture = :prefecture", "#url = :url",
        "thumbnailUrl = :thumbnail", "searchKeyword = :keyword", "lastScrapedAt = :now",
        "isFreeShipping = :is_free_shipping", "shippingStatus = :shipping_status",
        "workflowStatus = :workflow", "#ttl = :ttl"
    ]
    values = {
        ":item_type": item.get("itemType", "auction"), ":title": item.get("title", ""),
        ":price": safe_int(item.get("price", 0)), ":bid_count": safe_int(item.get("bidCount", 0)),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": str(item.get("sellerId") or "unknown"),
        ":seller_rating": str(item.get("sellerRating") or "unknown"),
        ":seller_type": item.get("sellerType", "personal"),
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""), ":thumbnail": item.get("thumbnailUrl", ""),
        ":keyword": keyword, ":now": now.isoformat(),
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":workflow": "ACTIVE_SCRAPED",
        ":ttl": int((now + timedelta(days=30)).timestamp()), ":pending": "PENDING"
    }
    if force_reprocess: set_parts.extend(["modelStatus = :pending", "pricingStatus = :pending"])
    else: set_parts.extend(["modelStatus = if_not_exists(modelStatus, :pending)", "pricingStatus = if_not_exists(pricingStatus, :pending)"])
    if item.get("buynowPrice") is not None:
        set_parts.append("buynowPrice = :buynow_price")
        values[":buynow_price"] = safe_int(item.get("buynowPrice"))
    if shipping_text:
        set_parts.append("shippingText = :shipping_text")
        values[":shipping_text"] = shipping_text
    if item.get("itemCondition") is not None:
        set_parts.append("itemCondition = :item_condition")
        values[":item_condition"] = item["itemCondition"]
    
    active_table.update_item(
        Key={"itemID": str(item["itemId"])},
        UpdateExpression="SET " + ", ".join(set_parts),
        ExpressionAttributeNames={"#url": "url", "#ttl": "ttl"},
        ExpressionAttributeValues=values
    )


# ==================== Active AI 模型解析 ====================

def get_active_items_by_ids(item_ids: List[str], only_pending: bool = True) -> List[Dict]:
    items = []
    for item_id in item_ids:
        try:
            result = active_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if item and (not only_pending or item.get("modelStatus") == "PENDING"): items.append(item)
        except Exception as e: logger.error(f"active商品取得失敗 {item_id}: {e}")
    return items


def batch_parse_models(items: List[Dict]) -> Dict:
    if not items: return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    batch_size = MODEL_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        logger.info(f"active モデル解析バッチ {batch_number}: {len(batch)} 商品")
        items_data = [{"itemId": str(item["itemID"]), "title": item.get("title", "")} for item in batch]
        prompt = build_model_parsing_prompt(items_data)
        result, error_info = call_ai_with_retry(prompt)
        
        if not result:
            error_msg = error_info or "AI_RESPONSE_EMPTY"
            logger.error(f"active バッチ {batch_number} AI失败: {error_msg}")
            for item in batch: mark_active_model_failed(str(item["itemID"]), error_msg)
            totals["failed"] += len(batch)
            totals["errors"].append(f"active バッチ{batch_number}（{len(batch)}商品）AI失败: {error_msg}")
            continue
        
        parsed_items = result.get("items", [])
        if not isinstance(parsed_items, list): parsed_items = []
        returned_ids = set()
        for parsed in parsed_items:
            if not isinstance(parsed, dict): continue
            item_id = str(parsed.get("itemId", "")).strip()
            if not item_id: continue
            returned_ids.add(item_id)
            saved_status = save_active_models_minimal(item_id=item_id, parsed=parsed)
            if saved_status == "COMPLETED": totals["parsed"] += 1
            elif saved_status == "EXCLUDED": totals["excluded"] += 1
            elif saved_status == "REVIEW_REQUIRED": totals["review_required"] += 1
            else: totals["failed"] += 1
        
        input_ids = {str(item["itemID"]) for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_active_model_failed(missing_id, "AI_NOT_RETURNED")
            totals["failed"] += 1
        if missing_ids: totals["errors"].append(f"active バッチ{batch_number}: AIが{len(missing_ids)}商品を返しませんでした")
        if start + batch_size < len(items): time.sleep(REQUEST_INTERVAL)
    
    logger.info(f"active モデル解析完了: 成功={totals['parsed']}, 除外={totals['excluded']}, 要確認={totals['review_required']}, 失敗={totals['failed']}")
    return totals


def build_model_parsing_prompt(items: List[Dict]) -> str:
    items_text = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    return f"""あなたは中古電子製品の識別専門家です。
以下の商品タイトルを解析し、モデルと主要スペックを返してください。

入力：
{items_text}

以下のJSON形式のみを返してください。全ての入力IDを含めてください：
{{"items":[{{"itemId":"ID","brand":"ブランド","model":"完全なモデル名","variant":"バリエーションまたは空","storage":"容量または空","listingType":"MAIN_PRODUCT","condition":"USED","missing":[],"confidence":0.95}}]}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

ルール：
1. スマホはPro/Pro Maxを区別し、容量はstorageに
2. PCはシリーズ/世代を区別し、メモリと容量はstorageに
3. 価格に影響するスペックが不足する場合、missingに不足項目名を列挙
4. タイトルに明記されていない情報は推測しない
5. アクセサリ、部品、故障品、空箱、セットは対応するlistingTypeで
6. modelはPro/Pro Maxを区別し、iPhone 15だけにしない
7. JSONのみを出力し、説明文は一切不要"""


# ==================== 放宽匹配条件的关键函数 ====================

# 不影响价格匹配的字段
NON_CRITICAL_FIELDS = {
    "variant", "color", "カラー", "色",
    "carrier", "キャリア", "通信事業者",
    "screen_size", "画面サイズ",
    "battery", "バッテリー",
    "graphics_card", "グラフィックス",
    "os", "operating_system", "OS",
    "processor", "プロセッサー", "cpu", "CPU",
    "compatibility", "互換性",
    "詳細な故障内容",
    "ram", "メモリ", "memory",
}


def parse_ai_result_minimal(parsed: Dict) -> Tuple[List[Dict], str, str, bool, List[str], str]:
    """放宽匹配：variant/颜色/运营商不作为关键参数"""
    brand = normalize(parsed.get("brand", ""))
    model_name = normalize(parsed.get("model", ""))
    variant = normalize(parsed.get("variant", ""))
    storage = normalize_storage(parsed.get("storage", ""))
    confidence = safe_decimal(parsed.get("confidence", 0))
    listing_type = normalize(parsed.get("listingType", "UNKNOWN")).upper()
    condition = normalize(parsed.get("condition", "UNKNOWN")).upper()
    missing = parsed.get("missing", [])
    
    if not isinstance(missing, list): missing = []
    
    # 从missing中移除不影响价格的字段
    critical_missing = [m for m in missing if m.lower() not in NON_CRITICAL_FIELDS]
    
    # 检查核心字段
    if not brand and "brand" not in [m.lower() for m in critical_missing]: critical_missing.append("brand")
    if not model_name and "model" not in [m.lower() for m in critical_missing]: critical_missing.append("model")
    
    has_all_critical = len(critical_missing) == 0
    
    models = []
    if brand and model_name:
        pricing_model_key = generate_pricing_model_key(
            brand=brand, model_name=model_name, storage=storage, variant=""  # variant不参与匹配
        )
        models.append({
            "brand": brand, "model": model_name, "variant": variant,
            "storage": storage, "pricingModelKey": pricing_model_key, "confidence": str(confidence)
        })
    
    excluded_types = {"ACCESSORY", "PARTS", "BROKEN", "BOX_ONLY", "BUNDLE", "UNKNOWN"}
    exclusion_reasons = []
    if listing_type in excluded_types: exclusion_reasons.append(f"商品タイプ不適: {listing_type}")
    if condition == "BROKEN": exclusion_reasons.append("商品状態が故障品")
    if not has_all_critical: exclusion_reasons.append(f"キーパラメータ不足: {', '.join(critical_missing)}")
    
    exclusion_reason = "; ".join(exclusion_reasons)
    return models, listing_type, condition, has_all_critical, critical_missing, exclusion_reason


def save_active_models_minimal(item_id: str, parsed: Dict) -> str:
    models, listing_type, condition, has_all_critical, missing, exclusion_reason = parse_ai_result_minimal(parsed)
    is_analysis_eligible = (listing_type == "MAIN_PRODUCT" and condition != "BROKEN" and has_all_critical and len(models) > 0)
    
    if not models: status = "REVIEW_REQUIRED"
    elif not is_analysis_eligible: status = "EXCLUDED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in models): status = "REVIEW_REQUIRED"
    else: status = "COMPLETED"
    
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""SET models = :models, modelStatus = :status, listingType = :listing_type,
            hasAllCriticalParameters = :has_all_critical, missingCriticalParameters = :missing,
            isAnalysisEligible = :is_analysis_eligible, exclusionReason = :exclusion_reason,
            modelParsedAt = :now, workflowStatus = :workflow, pricingStatus = :pricing_status""",
        ExpressionAttributeValues={
            ":models": models, ":status": status, ":listing_type": listing_type,
            ":has_all_critical": has_all_critical, ":missing": missing,
            ":is_analysis_eligible": is_analysis_eligible, ":exclusion_reason": exclusion_reason,
            ":now": now,
            ":workflow": ("MODEL_PARSED" if status == "COMPLETED" else "MODEL_EXCLUDED" if status == "EXCLUDED" else "MODEL_REVIEW_REQUIRED"),
            ":pricing_status": ("PENDING" if status == "COMPLETED" else "NOT_APPLICABLE")
        }
    )
    return status


def mark_active_model_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="SET modelStatus = :status, modelError = :error, modelParsedAt = :now",
        ExpressionAttributeValues={":status": "FAILED", ":error": error[:500], ":now": now}
    )


# ==================== Closed 搜索和解析 ====================

def scrape_and_save_closed_once(keyword: str, count: int = 100, force_reprocess: bool = False) -> List[str]:
    logger.info(f"closed 単回検索: keyword='{keyword}', count={count}")
    try:
        items = scrape_auctions(keyword, "closed", False)
        items = items[:count]
        saved_ids = []
        for item in items:
            try:
                upsert_closed_item_once(item=item, search_keyword=keyword, force_reprocess=force_reprocess)
                saved_ids.append(str(item["itemId"]))
            except Exception as exc: logger.error(f"closed商品保存失敗 {item.get('itemId')}: {exc}")
        logger.info(f"closed 単回検索完了、{len(saved_ids)} 件保存")
        return saved_ids
    except Exception as exc:
        logger.error(f"closed 検索失敗: {exc}", exc_info=True)
        return []


def upsert_closed_item_once(item: Dict, search_keyword: str, force_reprocess: bool = False):
    now = datetime.now(timezone.utc)
    shipping_text = item.get("shippingText", "")
    shipping_info = determine_shipping_status(shipping_text)
    
    set_parts = [
        "itemType = :item_type", "title = :title", "price = :price", "bidCount = :bid_count",
        "endTime = :end_time", "sellerId = :seller_id", "sellerRating = :seller_rating",
        "sellerType = :seller_type", "prefecture = :prefecture", "#url = :url",
        "thumbnailUrl = :thumbnail", "searchKeyword = :search_keyword", "lastScrapedAt = :now",
        "isFreeShipping = :is_free_shipping", "shippingStatus = :shipping_status", "#ttl = :ttl"
    ]
    values = {
        ":item_type": item.get("itemType", "auction"), ":title": item.get("title", ""),
        ":price": safe_int(item.get("price", 0)), ":bid_count": safe_int(item.get("bidCount", 0)),
        ":end_time": item.get("endTime") or "unknown",
        ":seller_id": str(item.get("sellerId") or "unknown"),
        ":seller_rating": str(item.get("sellerRating") or "unknown"),
        ":seller_type": item.get("sellerType", "personal"),
        ":prefecture": item.get("prefecture") or "unknown",
        ":url": item.get("url", ""), ":thumbnail": item.get("thumbnailUrl", ""),
        ":search_keyword": search_keyword, ":now": now.isoformat(),
        ":is_free_shipping": shipping_info["isFreeShipping"],
        ":shipping_status": shipping_info["shippingStatus"],
        ":ttl": int((now + timedelta(days=180)).timestamp()), ":pending": "PENDING"
    }
    if force_reprocess: set_parts.append("modelStatus = :pending")
    else: set_parts.append("modelStatus = if_not_exists(modelStatus, :pending)")
    if item.get("buynowPrice") is not None:
        set_parts.append("buynowPrice = :buynow_price")
        values[":buynow_price"] = safe_int(item.get("buynowPrice"))
    if shipping_text:
        set_parts.append("shippingText = :shipping_text")
        values[":shipping_text"] = shipping_text
    if item.get("itemCondition") is not None:
        set_parts.append("itemCondition = :item_condition")
        values[":item_condition"] = item["itemCondition"]
    
    closed_table.update_item(
        Key={"itemID": str(item["itemId"])},
        UpdateExpression="SET " + ", ".join(set_parts),
        ExpressionAttributeNames={"#url": "url", "#ttl": "ttl"},
        ExpressionAttributeValues=values
    )


def get_closed_items_by_ids(item_ids: List[str], only_pending: bool = True) -> List[Dict]:
    items = []
    for item_id in item_ids:
        try:
            result = closed_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if item and (not only_pending or item.get("modelStatus") == "PENDING"): items.append(item)
        except Exception as e: logger.error(f"closed商品取得失敗 {item_id}: {e}")
    return items


def batch_parse_closed_models(items: List[Dict]) -> Dict:
    if not items: return {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    batch_size = CLOSED_PARSE_BATCH_SIZE
    totals = {"parsed": 0, "excluded": 0, "review_required": 0, "failed": 0, "errors": []}
    
    for start in range(0, len(items), batch_size):
        check_limits()
        batch = items[start:start + batch_size]
        batch_number = start // batch_size + 1
        logger.info(f"closed モデル解析バッチ {batch_number}: {len(batch)} 商品")
        items_data = [{"itemId": str(item["itemID"]), "title": item.get("title", "")} for item in batch]
        prompt = build_closed_model_parsing_prompt(items_data)
        result, error_info = call_ai_with_retry(prompt)
        
        if not result:
            error_msg = error_info or "AI_RESPONSE_EMPTY"
            logger.error(f"closed バッチ {batch_number} AI失败: {error_msg}")
            for item in batch: mark_closed_parse_failed(str(item["itemID"]), error_msg)
            totals["failed"] += len(batch)
            totals["errors"].append(f"closed バッチ{batch_number}（{len(batch)}商品）AI失败: {error_msg}")
            continue
        
        parsed_items = result.get("items", [])
        if not isinstance(parsed_items, list): parsed_items = []
        returned_ids = set()
        for parsed in parsed_items:
            if not isinstance(parsed, dict): continue
            item_id = str(parsed.get("itemId", "")).strip()
            if not item_id: continue
            returned_ids.add(item_id)
            saved_status = save_closed_models_minimal(item_id=item_id, parsed=parsed)
            if saved_status == "COMPLETED": totals["parsed"] += 1
            elif saved_status == "EXCLUDED": totals["excluded"] += 1
            elif saved_status == "REVIEW_REQUIRED": totals["review_required"] += 1
            else: totals["failed"] += 1
        
        input_ids = {str(item["itemID"]) for item in batch}
        missing_ids = input_ids - returned_ids
        for missing_id in missing_ids:
            mark_closed_parse_failed(missing_id, "AI_NOT_RETURNED")
            totals["failed"] += 1
        if missing_ids: totals["errors"].append(f"closed バッチ{batch_number}: AIが{len(missing_ids)}商品を返しませんでした")
        if start + batch_size < len(items): time.sleep(REQUEST_INTERVAL)
    
    logger.info(f"closed モデル解析完了: 成功={totals['parsed']}, 除外={totals['excluded']}, 要確認={totals['review_required']}, 失敗={totals['failed']}")
    return totals


def build_closed_model_parsing_prompt(items: List[Dict]) -> str:
    items_text = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    return f"""あなたは中古電子製品の識別専門家です。
以下の落札済み商品タイトルを解析し、モデルと主要スペックを返してください。

入力：
{items_text}

以下のJSON形式のみを返してください。全ての入力IDを含めてください：
{{"items":[{{"itemId":"ID","brand":"ブランド","model":"完全なモデル名","variant":"バリエーションまたは空","storage":"容量または空","listingType":"MAIN_PRODUCT","condition":"USED","missing":[],"confidence":0.95}}]}}

listingType: MAIN_PRODUCT/ACCESSORY/PARTS/BROKEN/BOX_ONLY/BUNDLE/UNKNOWN
condition: NEW/USED/BROKEN/UNKNOWN

ルール：
1. スマホはPro/Pro Maxを区別し、容量はstorageに
2. PCはシリーズ/世代を区別し、メモリと容量はstorageに
3. 価格に影響するスペックが不足する場合、missingに不足項目名を列挙
4. タイトルに明記されていない情報は推測しない
5. アクセサリ、部品、故障品、空箱、セットは対応するlistingTypeで
6. modelはPro/Pro Maxを区別し、iPhone 15だけにしない
7. JSONのみを出力し、説明文は一切不要"""


def save_closed_models_minimal(item_id: str, parsed: Dict) -> str:
    models, listing_type, condition, has_all_critical, missing, exclusion_reason = parse_ai_result_minimal(parsed)
    is_comparable = (listing_type == "MAIN_PRODUCT" and condition != "BROKEN" and has_all_critical and len(models) > 0)
    
    if not models: status = "REVIEW_REQUIRED"
    elif not is_comparable: status = "EXCLUDED"
    elif any(safe_decimal(model.get("confidence", 0)) < Decimal("0.7") for model in models): status = "REVIEW_REQUIRED"
    else: status = "COMPLETED"
    
    now = datetime.now(timezone.utc).isoformat()
    closed_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="""SET models = :models, modelStatus = :status, listingType = :listing_type,
            isComparable = :is_comparable, parsedCondition = :condition,
            hasAllCriticalParameters = :has_all_critical, missingCriticalParameters = :missing,
            exclusionReason = :exclusion_reason, modelParsedAt = :now""",
        ExpressionAttributeValues={
            ":models": models, ":status": status, ":listing_type": listing_type,
            ":is_comparable": is_comparable, ":condition": condition,
            ":has_all_critical": has_all_critical, ":missing": missing,
            ":exclusion_reason": exclusion_reason, ":now": now
        }
    )
    return status


def mark_closed_parse_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    closed_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="SET modelStatus = :status, modelError = :error, modelParsedAt = :now",
        ExpressionAttributeValues={":status": "FAILED", ":error": error[:500], ":now": now}
    )


# ==================== 价格评估 ====================

def get_unpriced_items_for_ids(item_ids: List[str], require_model_completed: bool = True, include_completed: bool = False, limit: int = 100) -> List[Dict]:
    items = []
    for item_id in item_ids:
        try:
            result = active_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item: continue
            pricing_status = item.get("pricingStatus", "PENDING")
            if include_completed:
                if pricing_status not in {"PENDING", "COMPLETED", "INSUFFICIENT_DATA", "FAILED"}: continue
            elif pricing_status != "PENDING": continue
            if require_model_completed:
                if item.get("modelStatus") != "COMPLETED": continue
                if item.get("isAnalysisEligible") is not True: continue
                if item.get("hasAllCriticalParameters") is not True: continue
                if item.get("exclusionReason"): continue
            models = item.get("models", [])
            if isinstance(models, str):
                try: models = json.loads(models)
                except json.JSONDecodeError: models = []
            if not isinstance(models, list): continue
            valid_models = [model for model in models if isinstance(model, dict) and model.get("pricingModelKey")]
            if not valid_models: continue
            items.append(item)
            if len(items) >= limit: break
        except Exception as e: logger.error(f"価格評価待ち商品取得失敗 {item_id}: {e}")
    return items


def build_closed_comparable_index(closed_item_ids: Set[str]) -> Dict[str, List[Dict]]:
    comparable_index: Dict[str, List[Dict]] = {}
    for item_id in closed_item_ids:
        try:
            result = closed_table.get_item(Key={"itemID": str(item_id)})
            item = result.get("Item")
            if not item: continue
            if item.get("modelStatus") != "COMPLETED": continue
            if item.get("isComparable") is not True: continue
            if item.get("hasAllCriticalParameters") is not True: continue
            if item.get("listingType") != "MAIN_PRODUCT": continue
            if item.get("parsedCondition") == "BROKEN": continue
            price = safe_decimal(item.get("price", 0))
            if price <= 0: continue
            models = item.get("models", [])
            if isinstance(models, str):
                try: models = json.loads(models)
                except json.JSONDecodeError: continue
            if not isinstance(models, list): continue
            item_keys = set()
            for model in models:
                if not isinstance(model, dict): continue
                pricing_model_key = normalize(model.get("pricingModelKey", "")).upper()
                if not pricing_model_key: continue
                if pricing_model_key in item_keys: continue
                item_keys.add(pricing_model_key)
                comparable_index.setdefault(pricing_model_key, []).append(item)
        except Exception as e: logger.error(f"closed商品読み取り失敗 {item_id}: {e}")
    for model_key, items in comparable_index.items():
        items.sort(key=lambda value: value.get("endTime", ""), reverse=True)
        logger.info(f"closed インデックス: {model_key} 合計 {len(items)} 件の比較可能商品")
    return comparable_index


def get_comparable_closed_items(active_item: Dict, comparable_index: Dict[str, List[Dict]]) -> List[Dict]:
    models = active_item.get("models", [])
    if isinstance(models, str):
        try: models = json.loads(models)
        except json.JSONDecodeError: return []
    if not isinstance(models, list): return []
    comparable_items = []
    seen_ids = set()
    for model in models:
        if not isinstance(model, dict): continue
        pricing_model_key = normalize(model.get("pricingModelKey", "")).upper()
        if not pricing_model_key: continue
        matched_items = comparable_index.get(pricing_model_key, [])
        for closed_item in matched_items:
            item_id = str(closed_item.get("itemID", ""))
            if not item_id: continue
            if item_id in seen_ids: continue
            seen_ids.add(item_id)
            comparable_items.append(closed_item)
    comparable_items.sort(key=lambda value: value.get("endTime", ""), reverse=True)
    return comparable_items


def calculate_price_statistics(comparable_items: List[Dict]) -> Dict:
    price_records = []
    for item in comparable_items:
        try:
            price = safe_decimal(item.get("price", 0))
            if price <= 0: continue
            price_records.append({"itemId": str(item.get("itemID", "")), "price": price, "endTime": item.get("endTime", "")})
        except Exception: continue
    price_records.sort(key=lambda record: record["price"])
    prices = [record["price"] for record in price_records]
    count = len(prices)
    if count < MIN_COMPARABLE_COUNT:
        return {"count": count, "filtered_count": count, "is_sufficient": False,
                "insufficientReason": f"比較データ不足、最低{MIN_COMPARABLE_COUNT}件必要、現在{count}件",
                "prices": [int(p) for p in prices], "filtered_prices": [int(p) for p in prices],
                "comparableItemIds": [r["itemId"] for r in price_records if r["itemId"]]}
    
    def percentile(data: List[Decimal], p: Decimal) -> Decimal:
        if not data: return Decimal("0")
        if len(data) == 1: return data[0]
        pos = Decimal(len(data) - 1) * p
        li = int(pos)
        frac = pos - Decimal(li)
        return data[li] + (data[li+1] - data[li]) * frac if li + 1 < len(data) else data[li]
    
    q1 = percentile(prices, Decimal("0.25"))
    median = percentile(prices, Decimal("0.50"))
    q3 = percentile(prices, Decimal("0.75"))
    iqr = q3 - q1
    lower_bound = q1 - MAX_PRICE_DEVIATION * iqr
    upper_bound = q3 + MAX_PRICE_DEVIATION * iqr
    filtered_records = [r for r in price_records if lower_bound <= r["price"] <= upper_bound]
    filtered_prices = [r["price"] for r in filtered_records]
    filtered_count = len(filtered_prices)
    
    if filtered_count < MIN_COMPARABLE_COUNT:
        return {"count": count, "filtered_count": filtered_count, "is_sufficient": False,
                "insufficientReason": f"異常価格除外後、比較データ不足：最低{MIN_COMPARABLE_COUNT}件必要、現在{filtered_count}件",
                "min": int(min(prices)), "max": int(max(prices)), "q1": int(q1), "median": int(median), "q3": int(q3),
                "iqr": int(iqr), "lowerBound": int(lower_bound), "upperBound": int(upper_bound),
                "prices": [int(p) for p in prices], "filtered_prices": [int(p) for p in filtered_prices],
                "comparableItemIds": [r["itemId"] for r in filtered_records if r["itemId"]]}
    
    filtered_prices.sort()
    f_median = percentile(filtered_prices, Decimal("0.50"))
    f_avg = sum(filtered_prices, Decimal("0")) / Decimal(filtered_count)
    spread = Decimal("0")
    if f_median > 0: spread = ((max(filtered_prices) - min(filtered_prices)) / f_median).quantize(Decimal("0.001"), ROUND_HALF_UP)
    
    return {"count": count, "filtered_count": filtered_count, "excluded_outlier_count": count - filtered_count,
            "is_sufficient": True, "min": int(min(prices)), "max": int(max(prices)),
            "q1": int(q1), "median": int(median), "q3": int(q3), "iqr": int(iqr),
            "lowerBound": int(lower_bound), "upperBound": int(upper_bound),
            "filtered_min": int(min(filtered_prices)), "filtered_max": int(max(filtered_prices)),
            "filtered_median": int(f_median), "filtered_average": int(f_avg.quantize(Decimal("1"), ROUND_HALF_UP)),
            "price_spread_ratio": spread, "prices": [int(p) for p in prices],
            "filtered_prices": [int(p) for p in filtered_prices],
            "comparableItemIds": [str(r["itemId"]) for r in filtered_records if r["itemId"]]}


def calculate_pricing_confidence(stats: Dict) -> Decimal:
    if not stats.get("is_sufficient"): return Decimal("0.20")
    cc = safe_int(stats.get("filtered_count", 0))
    sr = safe_decimal(stats.get("price_spread_ratio", 0))
    tc = safe_int(stats.get("count", 0))
    ec = safe_int(stats.get("excluded_outlier_count", 0))
    if cc >= HIGH_CONFIDENCE_COMPARABLE_COUNT: confidence = Decimal("0.90")
    elif cc >= MEDIUM_CONFIDENCE_COMPARABLE_COUNT: confidence = Decimal("0.80")
    else: confidence = Decimal("0.70")
    if sr >= Decimal("0.50"): confidence -= Decimal("0.20")
    elif sr >= Decimal("0.30"): confidence -= Decimal("0.10")
    if tc > 0 and Decimal(ec) / Decimal(tc) >= Decimal("0.30"): confidence -= Decimal("0.10")
    confidence = max(Decimal("0.20"), min(Decimal("0.95"), confidence))
    return confidence.quantize(Decimal("0.01"), ROUND_HALF_UP)


def parse_seller_rating(value: Any) -> Optional[Decimal]:
    if value is None: return None
    text = str(value).strip()
    if not text or text.lower() == "unknown": return None
    try:
        if text.endswith("%"): return Decimal(text[:-1].strip())
        rating = Decimal(text)
        return rating * Decimal("100") if Decimal("0") <= rating <= Decimal("1") else rating
    except: return None


def determine_programmatic_risk(active_item: Dict, stats: Dict, pricing_confidence: Decimal, profit_margin: Decimal, has_buynow_price: bool) -> Dict:
    risk_score = 0
    risk_factors = []
    reasons = []
    cc = safe_int(stats.get("filtered_count", 0))
    sr = safe_decimal(stats.get("price_spread_ratio", 0))
    
    if cc < 5: risk_score += 2; risk_factors.append(f"有効比較サンプルが少ない、{cc}件のみ")
    elif cc < 10: risk_score += 1; risk_factors.append(f"有効比較サンプル数が普通、合計{cc}件")
    else: reasons.append(f"有効比較サンプル数が十分、合計{cc}件")
    
    if pricing_confidence < Decimal("0.50"): risk_score += 3; risk_factors.append("価格統計信頼度が低い")
    elif pricing_confidence < Decimal("0.75"): risk_score += 1; risk_factors.append("価格統計信頼度が普通")
    else: reasons.append(f"価格統計信頼度は{pricing_confidence}")
    
    if sr >= Decimal("0.50"): risk_score += 2; risk_factors.append("同型落札価格の分布が非常に分散")
    elif sr >= Decimal("0.30"): risk_score += 1; risk_factors.append("同型落札価格にある程度の変動あり")
    
    seller_rating = parse_seller_rating(active_item.get("sellerRating"))
    if seller_rating is None: risk_score += 1; risk_factors.append("出品者評価が確認不可")
    elif seller_rating < Decimal("95"): risk_score += 2; risk_factors.append(f"出品者評価が低い：{seller_rating}%")
    elif seller_rating < Decimal("98"): risk_score += 1; risk_factors.append(f"出品者評価が普通：{seller_rating}%")
    else: reasons.append(f"出品者評価が高い：{seller_rating}%")
    
    seller_type = str(active_item.get("sellerType", "personal")).lower()
    if seller_type == "personal": risk_score += 1; risk_factors.append("個人出品者による商品")
    else: reasons.append("ストア出品者による商品")
    
    shipping_status = active_item.get("shippingStatus", "UNKNOWN")
    if shipping_status == "UNKNOWN": risk_score += 1; risk_factors.append("送料確認不可")
    elif shipping_status == "FREE": reasons.append("送料込み商品")
    
    if not normalize(active_item.get("itemCondition", "")): risk_score += 1; risk_factors.append("商品状態欄が不明確")
    
    if profit_margin < Decimal("0"): risk_score += 3; risk_factors.append("現在価格で購入すると損失見込み")
    elif profit_margin < REVIEW_MARGIN_THRESHOLD: risk_score += 2; risk_factors.append("予想利益率が審査閾値未満")
    elif profit_margin < BUY_MARGIN_THRESHOLD: risk_score += 1; risk_factors.append("予想利益率が推奨購入閾値に達していない")
    else: reasons.append("予想利益率が推奨購入閾値に到達")
    
    if has_buynow_price: reasons.append("即決価格での収益も同時計算済み")
    
    risk_level = "HIGH" if risk_score >= 6 else "MEDIUM" if risk_score >= 3 else "LOW"
    return {"riskLevel": risk_level, "riskScore": risk_score, "riskFactors": risk_factors, "reasons": reasons}


def determine_purchase_decision(net_profit: Decimal, profit_margin: Decimal, risk_level: str, pricing_confidence: Decimal, comparable_count: int) -> str:
    if comparable_count < MIN_COMPARABLE_COUNT: return "INSUFFICIENT_DATA"
    if net_profit <= 0: return "AVOID"
    if profit_margin >= BUY_MARGIN_THRESHOLD and risk_level in {"LOW", "MEDIUM"} and pricing_confidence >= Decimal("0.70"): return "BUY_CANDIDATE"
    if profit_margin >= REVIEW_MARGIN_THRESHOLD and pricing_confidence >= Decimal("0.50"): return "REVIEW"
    if risk_level == "HIGH" and profit_margin < BUY_MARGIN_THRESHOLD: return "AVOID"
    return "REVIEW"


def build_programmatic_reasons(estimated_price: Decimal, purchase_price: Decimal, net_profit: Decimal, profit_margin: Decimal, decision_signal: str, stats: Dict) -> List[str]:
    reasons = []
    cc = safe_int(stats.get("filtered_count", 0))
    reasons.append(f"価格判断は{cc}件の同スペック有効成約サンプルに基づく")
    reasons.append(f"同スペック成約価格中央値は約{int(estimated_price)}円")
    if purchase_price > estimated_price: reasons.append(f"現在価格は市場中央値より{int(purchase_price - estimated_price)}円高い")
    elif purchase_price < estimated_price: reasons.append(f"現在価格は市場中央値より{int(estimated_price - purchase_price)}円低い")
    else: reasons.append("現在価格は市場中央値と同じ")
    if net_profit > 0: reasons.append(f"手数料・送料・リスク準備金控除後、予想純利益は{int(net_profit)}円")
    else: reasons.append(f"手数料・送料・リスク準備金控除後、予想損失{abs(int(net_profit))}円")
    reasons.append(f"予想販売利益率は{(profit_margin * Decimal('100')).quantize(Decimal('0.1'), ROUND_HALF_UP)}%")
    dt = {"BUY_CANDIDATE": "プログラム判断：利益余地が購入候補基準に到達",
          "REVIEW": "プログラム判断：商品状態と最終落札価格の人手確認が必要",
          "AVOID": "プログラム判断：現在価格では合理的な利益余地なし",
          "INSUFFICIENT_DATA": "比較データ不足、信頼できる購入提案を生成不可"}
    reasons.append(dt.get(decision_signal, "プログラムが明確な提案を生成できません"))
    return reasons


def get_effective_shipping_cost(item: Dict) -> Decimal:
    if parse_bool(item.get("isFreeShipping", False)) and str(item.get("shippingStatus", "")).upper() == "FREE": return Decimal("0")
    shipping_fee = item.get("shippingFee")
    if shipping_fee is not None:
        parsed = safe_decimal(shipping_fee, DEFAULT_SHIPPING_COST)
        if parsed >= 0: return parsed
    return DEFAULT_SHIPPING_COST


def generate_programmatic_pricing_result(active_item: Dict, stats: Dict, purchase_price: Decimal, actual_shipping: Decimal = Decimal("0"), buynow_price: Optional[Decimal] = None) -> Dict:
    if not stats.get("is_sufficient"):
        return to_dynamodb_value({"pricingStatus": "INSUFFICIENT_DATA", "pricingConfidence": Decimal("0.20"),
                "riskLevel": "HIGH", "riskScore": 10, "decisionSignal": "INSUFFICIENT_DATA",
                "reasons": [stats.get("insufficientReason", "比較データ不足")],
                "riskFactors": ["有効成約サンプル不足、信頼できる価格評価不可"],
                "comparableCount": safe_int(stats.get("filtered_count", stats.get("count", 0))),
                "comparableItemIds": [str(i) for i in stats.get("comparableItemIds", [])]})
    
    ep = safe_decimal(stats.get("filtered_median", 0))
    el = safe_decimal(stats.get("filtered_min", 0))
    eh = safe_decimal(stats.get("filtered_max", 0))
    pf = (ep * EXPECTED_SELLING_FEE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    rr = (ep * DEFAULT_REPAIR_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    rs = (ep * RISK_RESERVE_RATE).quantize(Decimal("1"), ROUND_HALF_UP)
    tnc = pf + actual_shipping + rr + rs
    np = ep - purchase_price - tnc
    pm = Decimal("0")
    if ep > 0: pm = (np / ep).quantize(Decimal("0.001"), ROUND_HALF_UP)
    ti = purchase_price + actual_shipping + rr + rs
    roi = Decimal("0")
    if ti > 0: roi = (np / ti).quantize(Decimal("0.001"), ROUND_HALF_UP)
    pc = calculate_pricing_confidence(stats)
    cc = safe_int(stats.get("filtered_count", 0))
    prisk = determine_programmatic_risk(active_item, stats, pc, pm, buynow_price is not None and buynow_price > 0)
    ds = determine_purchase_decision(np, pm, prisk["riskLevel"], pc, cc)
    preasons = build_programmatic_reasons(ep, purchase_price, np, pm, ds, stats)
    bep = (ep * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE) - actual_shipping).quantize(Decimal("1"), ROUND_HALF_UP)
    tp10 = (ep * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - Decimal("0.10")) - actual_shipping).quantize(Decimal("1"), ROUND_HALF_UP)
    tp20 = (ep * (Decimal("1") - EXPECTED_SELLING_FEE_RATE - DEFAULT_REPAIR_RESERVE_RATE - RISK_RESERVE_RATE - Decimal("0.20")) - actual_shipping).quantize(Decimal("1"), ROUND_HALF_UP)
    cids = [str(i) for i in stats.get("comparableItemIds", []) if str(i)]
    
    result = {"pricingStatus": "COMPLETED", "analysisMethod": "PROGRAMMATIC",
              "estimatedMarketPrice": int(ep), "estimatedLow": int(el), "estimatedHigh": int(eh),
              "currentBidPrice": int(purchase_price), "breakEvenPurchasePrice": max(0, int(bep)),
              "targetPurchasePrice10Margin": max(0, int(tp10)), "targetPurchasePrice20Margin": max(0, int(tp20)),
              "netProfitAtCurrentBid": int(np), "profitMarginAtCurrentBid": pm, "roiAtCurrentBid": roi,
              "pricingConfidence": pc, "riskLevel": prisk["riskLevel"], "riskScore": prisk["riskScore"],
              "decisionSignal": ds, "reasons": preasons + prisk["reasons"],
              "riskFactors": prisk["riskFactors"], "conditionAdjustment": "NONE",
              "comparableItemIds": cids, "comparableCount": cc,
              "rawComparableCount": safe_int(stats.get("count", 0)),
              "excludedOutlierCount": safe_int(stats.get("excluded_outlier_count", 0)),
              "priceSpreadRatio": safe_decimal(stats.get("price_spread_ratio", 0)),
              "priceBreakdown": {"estimatedSellingPrice": int(ep), "currentBidPrice": int(purchase_price),
                                 "platformFee": int(pf), "shippingCost": int(actual_shipping),
                                 "repairReserve": int(rr), "riskReserve": int(rs), "netProfit": int(np)}}
    
    if buynow_price is not None and buynow_price > 0:
        np_bn = ep - buynow_price - tnc
        pm_bn = Decimal("0")
        if ep > 0: pm_bn = (np_bn / ep).quantize(Decimal("0.001"), ROUND_HALF_UP)
        ti_bn = buynow_price + actual_shipping + rr + rs
        roi_bn = Decimal("0")
        if ti_bn > 0: roi_bn = (np_bn / ti_bn).quantize(Decimal("0.001"), ROUND_HALF_UP)
        br = determine_programmatic_risk(active_item, stats, pc, pm_bn, True)
        bd = determine_purchase_decision(np_bn, pm_bn, br["riskLevel"], pc, cc)
        result.update({"buynowPrice": int(buynow_price), "netProfitAtBuynow": int(np_bn),
                       "profitMarginAtBuynow": pm_bn, "roiAtBuynow": roi_bn,
                       "buynowDecisionSignal": bd, "buynowRiskLevel": br["riskLevel"]})
    
    return to_dynamodb_value(result)


def batch_price_analysis(items: List[Dict], allowed_closed_item_ids: Set[str]) -> Dict:
    totals = {"attempted": 0, "completed": 0, "insufficient_data": 0, "failed": 0}
    if not items: return totals
    comparable_index = build_closed_comparable_index({str(i) for i in allowed_closed_item_ids})
    logger.info(f"closed 比較可能インデックスに {len(comparable_index)} のpricingModelKey")
    for item in items:
        item_id = str(item.get("itemID", ""))
        try:
            check_timeout()
            totals["attempted"] += 1
            ci = get_comparable_closed_items(item, comparable_index)
            stats = calculate_price_statistics(ci)
            pp = safe_decimal(item.get("price", 0))
            ash = get_effective_shipping_cost(item)
            bp = safe_decimal(item.get("buynowPrice")) if item.get("buynowPrice") is not None else None
            if bp is not None and bp <= 0: bp = None
            pr = generate_programmatic_pricing_result(item, stats, pp, ash, bp)
            save_pricing_result(item_id, pr)
            ps = pr.get("pricingStatus")
            if ps == "COMPLETED": totals["completed"] += 1
            elif ps == "INSUFFICIENT_DATA": totals["insufficient_data"] += 1
            else: totals["failed"] += 1
        except RuntimeError: raise
        except Exception as exc:
            logger.error(f"プログラム価格評価失敗 {item_id}: {exc}", exc_info=True)
            mark_pricing_failed(item_id, str(exc))
            totals["failed"] += 1
    return totals


def save_pricing_result(item_id: str, pricing_result: Dict):
    now = datetime.now(timezone.utc).isoformat()
    ps = pricing_result.get("pricingStatus", "FAILED")
    wm = {"COMPLETED": "PRICING_COMPLETED", "INSUFFICIENT_DATA": "PRICING_INSUFFICIENT_DATA", "FAILED": "PRICING_FAILED"}
    ws = wm.get(ps, "PRICING_FAILED")
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="SET pricingResult = :result, pricingStatus = :status, pricedAt = :now, workflowStatus = :workflow, pricingMethod = :method",
        ExpressionAttributeValues={":result": to_dynamodb_value(pricing_result), ":status": ps,
                                   ":now": now, ":workflow": ws, ":method": "PROGRAMMATIC"}
    )


def mark_pricing_failed(item_id: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    active_table.update_item(
        Key={"itemID": str(item_id)},
        UpdateExpression="SET pricingStatus = :status, pricingError = :error, pricedAt = :now, workflowStatus = :workflow, pricingMethod = :method",
        ExpressionAttributeValues={":status": "FAILED", ":error": str(error)[:500], ":now": now,
                                   ":workflow": "PRICING_FAILED", ":method": "PROGRAMMATIC"}
    )


# ==================== AI 调用函数 ====================

def call_ai_with_retry(prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    max_mode_switches = 3
    for mode_attempt in range(max_mode_switches):
        config = get_available_ai_config()
        if not config: return None, "ALL_MODES_UNAVAILABLE"
        mode_name = config["name"]
        timeout = config["timeout"]
        for retry in range(AI_MAX_RETRIES):
            try:
                check_limits()
                if get_remaining_seconds() < timeout + 10: raise RuntimeError(f"残り時間不足")
                logger.info(f"AI调用 [{mode_name}] 第{retry+1}/{AI_MAX_RETRIES}次")
                if config["type"] == "gemini": result, finish_reason = call_gemini_api(config, prompt)
                else: result, finish_reason = call_openai_compatible_api(config, prompt)
                if result is not None: return result, finish_reason
                if finish_reason in ("length", "safety_blocked"): return None, finish_reason
                logger.warning(f"[{mode_name}] 空结果，重试 {retry+1}/{AI_MAX_RETRIES}")
            except RuntimeError as e:
                if any(kw in str(e) for kw in ["Token使用量が上限", "Lambdaタイムアウト", "残り時間不足"]): raise
                logger.error(f"[{mode_name}] RuntimeError: {e}")
            except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError) as e: logger.error(f"[{mode_name}] 网络错误: {e}")
            except Exception as e: logger.error(f"[{mode_name}] 未知错误: {type(e).__name__}: {e}")
            if retry < AI_MAX_RETRIES - 1: time.sleep((2 ** retry) + random.uniform(0, 1))
        logger.warning(f"[{mode_name}] 所有重试失败，切换到备用模式")
        mark_ai_mode_failed(mode_name, f"ALL_RETRIES_FAILED")
    return None, "ALL_MODES_EXHAUSTED"


def call_gemini_api(config: Dict, prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    al = get_api_logger(); st = get_stage_timer()
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.0, "maxOutputTokens": config["max_tokens"]}}
    seq = al.log_request(config["name"], config.get("model", ""), config["url"], body, config["timeout"])
    st.start(f"api_call_{config['name']}_{seq}")
    st_time = time.time()
    try:
        req = urllib.request.Request(config["url"], data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"x-goog-api-key": config["key"], "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=config["timeout"]) as resp:
            dur = (time.time() - st_time) * 1000
            result = json.loads(resp.read().decode("utf-8"))
        st.end()
        usage = result.get("usageMetadata", {})
        tt = 0
        if usage:
            tt = usage.get("promptTokenCount", 0) + usage.get("candidatesTokenCount", 0)
            update_token_usage({"total_tokens": tt})
        content = ""; fr = "unknown"
        if "candidates" in result and result["candidates"]:
            c = result["candidates"][0]; fr = c.get("finishReason", "unknown")
            if "content" in c and "parts" in c["content"]:
                content = "".join(p.get("text", "") for p in c["content"]["parts"])
        al.log_response(seq, 200, result, tt, dur, finish_reason=fr, content_length=len(content))
        if fr == "SAFETY": return None, "safety_blocked"
        return parse_ai_json(content), fr
    except urllib.error.HTTPError as e:
        dur = (time.time() - st_time) * 1000; st.end()
        eb = e.read().decode("utf-8", errors="replace")
        al.log_response(seq, e.code, None, 0, dur, error=f"HTTP {e.code}")
        raise
    except Exception as e:
        dur = (time.time() - st_time) * 1000; st.end()
        al.log_response(seq, 0, None, 0, dur, error=str(e)[:200])
        raise


def call_openai_compatible_api(config: Dict, prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    al = get_api_logger(); st = get_stage_timer()
    body = {"model": config["model"], "messages": [
        {"role": "system", "content": "あなたは電子製品の専門家です。必ず有効なJSON形式のみを返してください。説明文は一切不要です。"},
        {"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": config["max_tokens"]}
    if config["name"] == "doubao": body["response_format"] = {"type": "json_object"}
    seq = al.log_request(config["name"], config["model"], config["url"], body, config["timeout"])
    st.start(f"api_call_{config['name']}_{seq}")
    st_time = time.time()
    try:
        req = urllib.request.Request(config["url"], data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"Authorization": f"Bearer {config['key']}", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=config["timeout"]) as resp:
            dur = (time.time() - st_time) * 1000
            result = json.loads(resp.read().decode("utf-8"))
        st.end()
        usage = result.get("usage", {}); tt = usage.get("total_tokens", 0)
        if usage: update_token_usage(usage)
        content = ""; fr = "unknown"
        if "choices" in result and result["choices"]:
            content = result["choices"][0].get("message", {}).get("content", "")
            fr = result["choices"][0].get("finish_reason", "unknown")
        al.log_response(seq, 200, result, tt, dur, finish_reason=fr, content_length=len(content))
        return parse_ai_json(content), fr
    except urllib.error.HTTPError as e:
        dur = (time.time() - st_time) * 1000; st.end()
        eb = e.read().decode("utf-8", errors="replace")
        al.log_response(seq, e.code, None, 0, dur, error=f"HTTP {e.code}")
        raise
    except Exception as e:
        dur = (time.time() - st_time) * 1000; st.end()
        al.log_response(seq, 0, None, 0, dur, error=str(e)[:200])
        raise


def parse_ai_json(content: str) -> Optional[Dict]:
    if not content: return None
    content = content.strip()
    for attempt in [lambda c: json.loads(c), lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", c)),
                    lambda c: json.loads(re.search(r"\{[\s\S]*\}", c).group(0))]:
        try: return attempt(content)
        except (json.JSONDecodeError, AttributeError): continue
    logger.error(f"AI応答を解析できません: {content[:500]}")
    return None
```
