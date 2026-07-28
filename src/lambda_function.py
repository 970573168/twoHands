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
DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "doubao-seed-2-0-mini-260428")
DOUBAO_URL = os.environ.get("DOUBAO_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
DOUBAO_TIMEOUT = int(os.environ.get("DOUBAO_TIMEOUT", "180"))
DOUBAO_MAX_TOKENS = int(os.environ.get("DOUBAO_MAX_TOKENS", "6000"))

# OpenAI 配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_TIMEOUT = int(os.environ.get("OPENAI_TIMEOUT", "60"))
OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "4000"))

# 故障切换冷却时间
AI_FAILOVER_COOLDOWN = int(os.environ.get("AI_FAILOVER_COOLDOWN", "300"))

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
            "name": "gemini",
            "type": "gemini",
            "url": GEMINI_URL,
            "key": GEMINI_API_KEY or _get_api_key_from_secrets("gemini"),
            "model": GEMINI_MODEL,
            "timeout": GEMINI_TIMEOUT,
            "max_tokens": GEMINI_MAX_TOKENS,
        },
        "doubao": {
            "name": "doubao",
            "type": "openai_compatible",
            "url": DOUBAO_URL,
            "key": DOUBAO_API_KEY or _get_api_key_from_secrets("doubao"),
            "model": DOUBAO_MODEL,
            "timeout": DOUBAO_TIMEOUT,
            "max_tokens": DOUBAO_MAX_TOKENS,
        },
        "openai": {
            "name": "openai",
            "type": "openai_compatible",
            "url": OPENAI_URL,
            "key": OPENAI_API_KEY or _get_api_key_from_secrets("openai"),
            "model": OPENAI_MODEL,
            "timeout": OPENAI_TIMEOUT,
            "max_tokens": OPENAI_MAX_TOKENS,
        }
    }
    
    # 向后兼容旧配置
    if mode not in configs and SECRET_NAME and API_URL:
        return {
            "name": "legacy",
            "type": "openai_compatible",
            "url": API_URL,
            "key": _get_legacy_api_key(),
            "model": MODEL or "doubao-seed-2-1-pro-260628",
            "timeout": REQUEST_TIMEOUT,
            "max_tokens": int(os.environ.get("MAX_TOKENS", "4000")),
        }
    
    if mode not in configs:
        log("WARN", f"未知的 AI_MODE: {mode}，使用 gemini")
        mode = "gemini"
    
    return configs[mode]


def _get_legacy_api_key() -> str:
    """获取旧版 API Key（向后兼容）"""
    if not SECRET_NAME:
        return ""
    try:
        response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response.get("SecretString", "")
        if not secret_string:
            return ""
        try:
            secret_data = json.loads(secret_string)
            return secret_data.get("apiKey") or secret_data.get("api_key") or secret_data.get("key") or ""
        except json.JSONDecodeError:
            return secret_string.strip()
    except Exception:
        return ""


def get_available_ai_config() -> dict:
    """获取可用的 AI 配置，考虑故障切换"""
    fallback_order = ["gemini", "doubao", "openai"]
    
    if AI_MODE in fallback_order:
        ordered_modes = [AI_MODE] + [m for m in fallback_order if m != AI_MODE]
    else:
        ordered_modes = fallback_order
    
    now = time.time()
    
    for mode in ordered_modes:
        if mode in _ai_mode_state["failed_modes"]:
            fail_time = _ai_mode_state["failed_modes"][mode]
            if now - fail_time < AI_FAILOVER_COOLDOWN:
                log("INFO", f"AI 模式 '{mode}' 冷却中", remaining_seconds=int(AI_FAILOVER_COOLDOWN - (now - fail_time)))
                continue
            else:
                log("INFO", f"AI 模式 '{mode}' 冷却结束，重新可用")
                del _ai_mode_state["failed_modes"][mode]
        
        config = get_ai_config(mode)
        if config["key"]:
            log("INFO", f"选择 AI 模式: '{mode}'")
            return config
    
    # 尝试旧版配置
    if SECRET_NAME and API_URL:
        legacy_config = get_ai_config("legacy")
        if legacy_config["key"]:
            log("INFO", "使用旧版 AI 配置")
            return legacy_config
    
    raise RuntimeError("所有 AI 模式均不可用")


def mark_ai_mode_failed(mode: str, error: str = ""):
    """标记 AI 模式故障"""
    _ai_mode_state["failed_modes"][mode] = time.time()
    log("WARN", f"AI 模式 '{mode}' 标记为故障", cooldown_seconds=AI_FAILOVER_COOLDOWN, error=error[:100])


def reset_ai_state():
    """重置 AI 状态"""
    _ai_mode_state["failed_modes"].clear()
    log("INFO", "AI 模式状态已重置")


# ============================================
# 详细追踪器类
# ============================================

class DiscoveryTracker:
    """发现任务追踪器 - 记录Token消耗和时间花费"""
    
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
        
        self.timing_details = {
            "phases": {},
            "api_calls": [],
            "db_operations": []
        }
        
        self.summary = {
            "categories_discovered": 0,
            "brands_discovered": 0,
            "models_discovered": 0,
            "total_api_calls": 0,
            "total_tokens_used": 0,
            "elapsed_seconds": 0
        }
    
    def start_phase(self, phase_name, **metadata):
        if self.current_phase:
            self.end_phase()
        self.current_phase = phase_name
        self.phase_start_time = time.time()
        self.phase_stack.append(phase_name)
        log("INFO", f"开始阶段: {phase_name}", phase=phase_name, **metadata)
    
    def end_phase(self):
        if not self.current_phase or not self.phase_start_time:
            return
        elapsed = time.time() - self.phase_start_time
        if self.current_phase not in self.timing_details["phases"]:
            self.timing_details["phases"][self.current_phase] = {
                "calls": 0, "total_seconds": 0, "min_seconds": float('inf'), "max_seconds": 0, "avg_seconds": 0
            }
        phase_stats = self.timing_details["phases"][self.current_phase]
        phase_stats["calls"] += 1
        phase_stats["total_seconds"] += elapsed
        phase_stats["min_seconds"] = min(phase_stats["min_seconds"], elapsed)
        phase_stats["max_seconds"] = max(phase_stats["max_seconds"], elapsed)
        phase_stats["avg_seconds"] = phase_stats["total_seconds"] / phase_stats["calls"]
        log("INFO", f"阶段完成: {self.current_phase}", phase=self.current_phase, duration_seconds=round(elapsed, 2))
        if self.phase_stack and self.phase_stack[-1] == self.current_phase:
            self.phase_stack.pop()
        self.current_phase = None
        self.phase_start_time = None
    
    def record_api_call(self, task_type, tokens_used, item_count, success=True, error=None):
        if task_type not in self.token_details:
            task_type = "total"
        self.token_details[task_type]["api_calls"] += 1
        self.token_details[task_type]["tokens"] += tokens_used
        self.token_details[task_type]["items"] += item_count
        if not success:
            self.token_details[task_type]["errors"] += 1
        self.token_details["total"]["api_calls"] += 1
        self.token_details["total"]["tokens"] += tokens_used
        self.token_details["total"]["items"] += item_count
        if not success:
            self.token_details["total"]["errors"] += 1
        self.timing_details["api_calls"].append({
            "timestamp": time.time(), "task_type": task_type, "tokens_used": tokens_used,
            "item_count": item_count, "success": success, "error": str(error) if error else None
        })
    
    def record_db_operation(self, operation_type, item_count, success=True):
        self.timing_details["db_operations"].append({
            "timestamp": time.time(), "operation_type": operation_type, "item_count": item_count, "success": success
        })
    
    def get_summary(self):
        total_elapsed = time.time() - self.start_time
        if self.current_phase:
            self.end_phase()
        phase_stats = {}
        for phase_name, stats in self.timing_details["phases"].items():
            phase_stats[phase_name] = {
                "calls": stats["calls"], "total_seconds": round(stats["total_seconds"], 2),
                "avg_seconds": round(stats["avg_seconds"], 2),
                "min_seconds": round(stats["min_seconds"], 2) if stats["min_seconds"] != float('inf') else 0,
                "max_seconds": round(stats["max_seconds"], 2)
            }
        return {
            "total_elapsed_seconds": round(total_elapsed, 2),
            "total_api_calls": self.token_details["total"]["api_calls"],
            "total_tokens_used": self.token_details["total"]["tokens"],
            "total_items_discovered": self.token_details["total"]["items"],
            "total_errors": self.token_details["total"]["errors"],
            "phase_stats": phase_stats,
            "ai_mode_used": _ai_mode_state.get("current_mode", AI_MODE),
        }
    
    def log_summary(self):
        summary = self.get_summary()
        log("INFO", "=== 任务执行摘要 ===")
        log("INFO", "总耗时", seconds=summary["total_elapsed_seconds"], api_calls=summary["total_api_calls"],
            total_tokens=summary["total_tokens_used"], total_items=summary["total_items_discovered"],
            errors=summary["total_errors"], ai_mode=summary["ai_mode_used"])
        return summary


# ============================================

_tracker = None

def log(level, message, **fields):
    entry = {"level": level, "message": message, "total_tokens": _total_tokens_used,
             "elapsed_seconds": get_elapsed_seconds(), **fields}
    print(json.dumps(entry, ensure_ascii=False, default=str))


def get_elapsed_seconds():
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    remaining = get_remaining_seconds()
    if remaining <= 0:
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
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
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
    if isinstance(content, dict):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") in ("input_text", "text"):
                    text_parts.append(str(part.get("text", "")))
        content = "".join(text_parts)
    text = str(content or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        text = json_match.group(0)
    return json.loads(text)


def get_latest_model_date(brand):
    brand_key = key_part(brand)
    try:
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get("Items", [])
        if items:
            return items[0].get("release_date", "")
        return None
    except Exception as e:
        log("WARN", "获取最新型号日期失败", brand=brand, error=str(e))
        return None


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

    if task_type == "DISCOVER_CATEGORIES":
        instruction = (
            "一般的な電子製品のカテゴリをリストアップしてください。"
            "各エントリにはcategoryフィールドのみを含めてください。"
        )
    elif task_type == "DISCOVER_BRANDS":
        category = normalize(task.get("category"))
        instruction = (
            f"電子製品カテゴリ「{category}」の実際のブランドをリストアップしてください。"
            "各エントリにはcategoryとbrandフィールドを含めてください。"
        )
    elif task_type == "DISCOVER_MODELS":
        category = normalize(task.get("category"))
        brand = normalize(task.get("brand"))
        date_condition = ""
        if search_date:
            date_condition = f"{search_date}以降に発売された製品のみを含めてください。発売日の降順でリストしてください。"
        instruction = (
            f"ブランド「{brand}」のカテゴリ「{category}」における具体的な製品モデルをリストアップしてください。"
            f"{date_condition}"
            "各エントリにはcategory、brand、model、confidence、release_dateフィールドを含めてください。"
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

    ルール：
    - JSONのみを返し、マークダウンや説明は不要
    - あなたの知識ベースのみを使用する
    - 不確かな場合はconfidenceを下げる
    """


# ============================================
# 多 API 调用函数
# ============================================

def call_api(task):
    """调用 AI API - 支持多模式切换"""
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
        timeout = config["timeout"]
        
        remaining = get_remaining_seconds()
        if remaining < timeout + 10:
            raise RuntimeError(f"剩余时间不足: {remaining:.1f}秒")
        
        # 单个模式重试
        for attempt in range(MAX_RETRIES):
            try:
                api_start_time = time.time()
                
                if config["type"] == "gemini":
                    items, tokens_used = call_gemini_api(config, task)
                else:
                    items, tokens_used = call_openai_compatible_api(config, task)
                
                api_elapsed = time.time() - api_start_time
                
                log("INFO", "API请求完成",
                    mode=mode_name, model=config["model"],
                    item_count=len(items), tokens_used=tokens_used,
                    api_duration_seconds=round(api_elapsed, 2))
                
                task_type_key = task.get("task_type", "").split('_')[1].lower()
                if _tracker:
                    _tracker.record_api_call(task_type_key, tokens_used, len(items), success=True)
                
                return items
                
            except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError) as e:
                last_error = f"网络错误: {e}"
                log("ERROR", f"[{mode_name}] 网络错误 (尝试{attempt+1}/{MAX_RETRIES})", error=str(e))
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                log("ERROR", f"[{mode_name}] API调用失败 (尝试{attempt+1}/{MAX_RETRIES})", error=str(e))
            
            if attempt < MAX_RETRIES - 1:
                delay = (2 ** attempt) + random.random()
                time.sleep(delay)
        
        # 当前模式所有重试失败
        mark_ai_mode_failed(mode_name, str(last_error))
    
    raise RuntimeError(f"所有 AI 模式均调用失败: {last_error}")


def call_gemini_api(config: dict, task: dict) -> tuple:
    """调用 Gemini API"""
    prompt = build_prompt(task)
    
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": config["max_tokens"],
            "topP": TOP_P
        }
    }
    
    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    
    request = urllib.request.Request(
        config["url"],
        data=encoded_body,
        headers={
            "x-goog-api-key": config["key"],
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(request, timeout=config["timeout"]) as response:
        result = json.loads(response.read().decode("utf-8"))
        
        tokens_used = 0
        usage = result.get("usageMetadata", {})
        if usage:
            tokens_used = usage.get("promptTokenCount", 0) + usage.get("candidatesTokenCount", 0)
            update_token_usage({"total_tokens": tokens_used})
        
        content = ""
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if candidate.get("finishReason") == "SAFETY":
                raise RuntimeError("Gemini 安全过滤触发")
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                content = "".join(part.get("text", "") for part in parts)
        
        parsed = clean_json_content(content)
        items = parsed.get("items", [])
        if not isinstance(items, list):
            items = []
        
        return items, tokens_used


def call_openai_compatible_api(config: dict, task: dict) -> tuple:
    """调用 OpenAI 兼容 API（豆包、OpenAI 等）"""
    prompt = build_prompt(task)
    
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": config["max_tokens"],
        "top_p": TOP_P
    }
    
    # 豆包支持 response_format
    if config["name"] == "doubao":
        body["response_format"] = {"type": "json_object"}
    
    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    
    request = urllib.request.Request(
        config["url"],
        data=encoded_body,
        headers={
            "Authorization": f"Bearer {config['key']}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(request, timeout=config["timeout"]) as response:
        result = json.loads(response.read().decode("utf-8"))
        
        usage = result.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)
        update_token_usage(usage)
        
        content = ""
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")
        else:
            content = result.get("content") or result.get("text") or json.dumps(result)
        
        parsed = clean_json_content(content)
        items = parsed.get("items", [])
        if not isinstance(items, list):
            for key, value in parsed.items():
                if isinstance(value, list):
                    items = value
                    break
            if not isinstance(items, list):
                items = []
        
        return items, tokens_used


# ============================================
# 数据库操作
# ============================================

def upsert_category(category):
    global _tracker
    category = normalize(category)
    if not category:
        return
    try:
        now = int(time.time())
        table.update_item(
            Key={"PK": f"CATEGORY#{key_part(category)}", "SK": "META"},
            UpdateExpression=(
                "SET entity_type = :type, #name = :name, #status = :status, "
                "first_seen_at = if_not_exists(first_seen_at, :now), "
                "last_seen_at = :now, #source = :source"
            ),
            ExpressionAttributeNames={"#name": "name", "#status": "status", "#source": "source"},
            ExpressionAttributeValues={
                ":type": "CATEGORY", ":name": category, ":status": "ACTIVE",
                ":now": now, ":source": DATA_SOURCE
            }
        )
        if _tracker:
            _tracker.record_db_operation("upsert_category", 1, success=True)
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_category", 0, success=False)
        raise


def upsert_brand(category, brand):
    global _tracker
    category = normalize(category)
    brand = normalize(brand)
    if not category or not brand:
        return
    try:
        now = int(time.time())
        table.update_item(
            Key={"PK": f"CATEGORY#{key_part(category)}", "SK": f"BRAND#{key_part(brand)}"},
            UpdateExpression=(
                "SET entity_type = :type, category = :category, brand = :brand, "
                "#status = :status, first_seen_at = if_not_exists(first_seen_at, :now), "
                "last_seen_at = :now, #source = :source"
            ),
            ExpressionAttributeNames={"#status": "status", "#source": "source"},
            ExpressionAttributeValues={
                ":type": "BRAND", ":category": category, ":brand": brand,
                ":status": "ACTIVE", ":now": now, ":source": DATA_SOURCE
            }
        )
        if _tracker:
            _tracker.record_db_operation("upsert_brand", 1, success=True)
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_brand", 0, success=False)
        raise


def upsert_product(category, brand, model, confidence=None, release_date=None):
    global _tracker
    category = normalize(category)
    brand = normalize(brand)
    model = normalize(model)
    if not category or not brand or not model:
        return
    try:
        now = int(time.time())
        product_id = stable_id(category, brand, model)
        product_pk = f"PRODUCT#{product_id}"

        expression = (
            "SET entity_type = :type, category = :category, brand = :brand, "
            "model = :model, normalized_model = :normalized_model, "
            "#status = :status, verification_status = if_not_exists(verification_status, :unverified), "
            "first_seen_at = if_not_exists(first_seen_at, :now), last_seen_at = :now, #source = :source"
        )
        values = {
            ":type": "PRODUCT", ":category": category, ":brand": brand,
            ":model": model, ":normalized_model": normalize(model).casefold(),
            ":status": "ACTIVE", ":unverified": "UNVERIFIED", ":now": now, ":source": DATA_SOURCE
        }
        if confidence is not None:
            try:
                values[":confidence"] = str(max(0.0, min(1.0, float(confidence))))
                expression += ", confidence = :confidence"
            except (TypeError, ValueError):
                pass
        if release_date:
            release_date = normalize(release_date)
            if re.match(r"^\d{4}-\d{2}-\d{2}", release_date):
                expression += ", release_date = :release_date"
                values[":release_date"] = release_date

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
            "category": category, "brand": brand, "model": model,
            "product_pk": product_pk, "last_seen_at": now
        }
        if release_date:
            gsi1_item["release_date"] = release_date
        table.put_item(Item=gsi1_item)
        
        if _tracker:
            _tracker.record_db_operation("upsert_product", 1, success=True)
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_product", 0, success=False)
        raise


# ============================================
# 主处理逻辑
# ============================================

def process_discovery(event):
    global _total_tokens_used, _lambda_start_time, _tracker
    
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    reset_ai_state()
    
    _tracker = DiscoveryTracker()
    _tracker.start_phase("discovery_start", ai_mode=AI_MODE)
    
    task_type = event.get("task_type", "DISCOVER_CATEGORIES")
    
    log("INFO", "开始发现处理", task_type=task_type, ai_mode=AI_MODE)
    
    try:
        if task_type == "DISCOVER_CATEGORIES":
            _tracker.start_phase("discover_categories")
            task = {"task_type": "DISCOVER_CATEGORIES", "max_items": MAX_CATEGORIES}
            items = call_api(task)
            
            categories = []
            for item in items:
                if isinstance(item, dict) and "category" in item:
                    category = normalize(item["category"])
                    if category:
                        upsert_category(category)
                        categories.append(category)
            
            _tracker.end_phase()
            log("INFO", "品类发现完成", count=len(categories))
            
            category_count = 0
            for category in categories[:CATEGORY_LIMIT]:
                if _total_tokens_used >= MAX_TOTAL_TOKENS:
                    log("WARN", "Token用量接近上限，停止")
                    break
                if get_remaining_seconds() < 60:
                    log("WARN", "剩余时间不足，停止")
                    break
                
                _tracker.start_phase(f"discover_brands_{category}")
                time.sleep(API_CALL_DELAY)
                
                brand_task = {"task_type": "DISCOVER_BRANDS", "category": category, "max_items": MAX_BRANDS}
                brand_items = call_api(brand_task)
                
                brands = []
                for item in brand_items:
                    if isinstance(item, dict) and "brand" in item:
                        brand = normalize(item["brand"])
                        if brand and category:
                            upsert_brand(category, brand)
                            brands.append((category, brand))
                
                _tracker.end_phase()
                
                brand_count = 0
                for cat, brand in brands[:BRAND_LIMIT]:
                    if _total_tokens_used >= MAX_TOTAL_TOKENS:
                        break
                    if get_remaining_seconds() < 60:
                        break
                    
                    _tracker.start_phase(f"discover_models_{brand}")
                    time.sleep(API_CALL_DELAY)
                    
                    latest_date = get_latest_model_date(brand)
                    model_task = {
                        "task_type": "DISCOVER_MODELS", "category": cat,
                        "brand": brand, "max_items": MAX_MODELS, "search_date": latest_date
                    }
                    model_items = call_api(model_task)
                    
                    model_count = 0
                    for item in model_items:
                        if isinstance(item, dict) and "model" in item:
                            upsert_product(cat, brand, item.get("model"),
                                           item.get("confidence"), item.get("release_date"))
                            model_count += 1
                    
                    _tracker.end_phase()
                    brand_count += 1
                
                category_count += 1
            
            summary = _tracker.log_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "发现处理完成",
                    "categories_discovered": len(categories),
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "summary": summary
                }, ensure_ascii=False)
            }
        
        elif task_type == "DISCOVER_MODELS":
            category = event.get("category", "")
            brand = event.get("brand", "")
            if not category or not brand:
                return {"statusCode": 400, "body": json.dumps({"error": "需要提供 category 和 brand 参数"}, ensure_ascii=False)}
            
            _tracker.start_phase(f"discover_models_{brand}")
            latest_date = get_latest_model_date(brand)
            task = {"task_type": "DISCOVER_MODELS", "category": category, "brand": brand,
                    "max_items": MAX_MODELS, "search_date": latest_date}
            items = call_api(task)
            
            model_count = 0
            for item in items:
                if isinstance(item, dict) and "model" in item:
                    upsert_product(category, brand, item.get("model"),
                                   item.get("confidence"), item.get("release_date"))
                    model_count += 1
            
            _tracker.end_phase()
            summary = _tracker.log_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "型号发现完成",
                    "models_discovered": model_count,
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds(),
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
                    "summary": summary if _tracker else None
                }, ensure_ascii=False)
            }
        raise
    except Exception as e:
        if _tracker:
            _tracker.end_phase()
        log("ERROR", "处理异常", error_type=type(e).__name__, error=str(e))
        raise


def lambda_handler(event, context):
    global _lambda_start_time, _tracker
    _lambda_start_time = time.time()
    _tracker = None
    
    try:
        log("INFO", "Lambda执行开始", ai_mode=AI_MODE)
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
