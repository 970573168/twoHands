import hashlib
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
secretsmanager = boto3.client("secretsmanager")


# ==================== 环境变量辅助函数 ====================

def _env_int(key: str, default: int) -> int:
    value = os.getenv(key, "")
    if not value:
        return default
    return int(value)


def _env_float(key: str, default: float) -> float:
    value = os.getenv(key, "")
    if not value:
        return default
    return float(value)


# ============================================
# 所有配置项都从环境变量读取
# ============================================

API_URL = os.environ.get("API_URL", "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions")
MODEL = os.environ.get("AI_MODEL", "doubao-seed-2-1-pro-260628")
SECRET_NAME = os.environ.get("SECRET_NAME", "")
API_KEY = os.environ.get("API_KEY", "")

TEMPERATURE = _env_float("TEMPERATURE", 0.7)
MAX_TOKENS = _env_int("MAX_TOKENS", 4000)
TOP_P = _env_float("TOP_P", 1.0)
REQUEST_TIMEOUT = _env_int("REQUEST_TIMEOUT", 90)
MAX_RETRIES = _env_int("MAX_RETRIES", 3)

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant that returns data in JSON format.")

MAX_CATEGORIES = _env_int("MAX_CATEGORIES", 20)
MAX_BRANDS = _env_int("MAX_BRANDS", 20)
MAX_MODELS = _env_int("MAX_MODELS", 50)

MAX_TOTAL_TOKENS = _env_int("MAX_TOTAL_TOKENS", 100000)
LAMBDA_TIMEOUT_SECONDS = _env_int("LAMBDA_TIMEOUT_SECONDS", 840)
LAMBDA_TIMEOUT_BUFFER = _env_int("LAMBDA_TIMEOUT_BUFFER", 30)

CATEGORY_LIMIT = _env_int("CATEGORY_LIMIT", 5)
BRAND_LIMIT = _env_int("BRAND_LIMIT", 3)
API_CALL_DELAY = _env_float("API_CALL_DELAY", 1.0)

RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

DATA_SOURCE = os.environ.get("DATA_SOURCE", "AI_DISCOVERY")

# ============================================

_api_key_cache = None
_brand_date_cache = {}

_total_tokens_used = 0
_lambda_start_time = None


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
        log("INFO", f"阶段完成: {self.current_phase}", duration_seconds=round(elapsed, 2))
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
            "timestamp": time.time(), "task_type": task_type,
            "tokens_used": tokens_used, "item_count": item_count,
            "success": success, "error": str(error) if error else None
        })
    
    def record_db_operation(self, operation_type, item_count, success=True):
        self.timing_details["db_operations"].append({
            "timestamp": time.time(), "operation_type": operation_type,
            "item_count": item_count, "success": success
        })
    
    def get_summary(self):
        total_elapsed = time.time() - self.start_time
        if self.current_phase:
            self.end_phase()
        phase_stats = {}
        for phase_name, stats in self.timing_details["phases"].items():
            phase_stats[phase_name] = {
                "calls": stats["calls"],
                "total_seconds": round(stats["total_seconds"], 2),
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
            "token_by_task": {
                task_type: {
                    "api_calls": stats["api_calls"], "tokens": stats["tokens"],
                    "items": stats["items"], "errors": stats["errors"],
                    "avg_tokens_per_call": stats["tokens"] / stats["api_calls"] if stats["api_calls"] > 0 else 0,
                    "avg_items_per_call": stats["items"] / stats["api_calls"] if stats["api_calls"] > 0 else 0
                }
                for task_type, stats in self.token_details.items()
                if task_type != "total" and stats["api_calls"] > 0
            }
        }
    
    def log_summary(self):
        summary = self.get_summary()
        log("INFO", "=== 任务执行摘要 ===")
        log("INFO", "总耗时", seconds=summary["total_elapsed_seconds"],
            api_calls=summary["total_api_calls"], total_tokens=summary["total_tokens_used"],
            total_items=summary["total_items_discovered"], errors=summary["total_errors"])
        return summary


_tracker = None


def log(level, message, **fields):
    entry = {
        "level": level, "message": message,
        "total_tokens": _total_tokens_used,
        "elapsed_seconds": get_elapsed_seconds(),
        **fields,
    }
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
        raise RuntimeError(
            f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒, "
            f"超时限制{LAMBDA_TIMEOUT_SECONDS}秒, 缓冲{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_limits():
    check_token_limit()
    check_timeout()


def get_api_key():
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache
    if API_KEY:
        _api_key_cache = API_KEY
        return _api_key_cache
    if not SECRET_NAME:
        raise RuntimeError("未配置 SECRET_NAME 或 API_KEY 环境变量")
    response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
    secret_string = response.get("SecretString")
    if not secret_string:
        raise RuntimeError("API secret has no SecretString value")
    try:
        value = json.loads(secret_string)
        api_key = value.get("apiKey") or value.get("api_key") or value.get("key")
    except json.JSONDecodeError:
        api_key = secret_string
    if not api_key:
        raise RuntimeError("API secret does not contain apiKey")
    _api_key_cache = api_key
    return _api_key_cache


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
                if part.get("type") == "input_text":
                    text_parts.append(str(part.get("text", "")))
                elif part.get("type") == "text":
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
    if brand_key in _brand_date_cache:
        return _brand_date_cache[brand_key]
    try:
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
            ScanIndexForward=False, Limit=1
        )
        items = response.get("Items", [])
        if items:
            latest_date = items[0].get("release_date", "")
            if latest_date:
                _brand_date_cache[brand_key] = latest_date
                return latest_date
        _brand_date_cache[brand_key] = None
        return None
    except Exception as e:
        log("WARN", "获取最新型号日期失败", brand=brand, error=str(e))
        return None


def check_token_limit():
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}，中断执行")


def update_token_usage(usage):
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        log("INFO", "Token用量更新", added_tokens=total, total_tokens=_total_tokens_used,
            limit=MAX_TOTAL_TOKENS, remaining_tokens=MAX_TOTAL_TOKENS - _total_tokens_used)


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
            date_condition = f"{search_date}以降に発売された製品のみを含めてください。"
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
    - JSONのみを返し、マークダウンや説明は不要
    - あなたの知識ベースのみを使用
    - 公式ブランド名とモデル名を使用
    """


def call_api(task):
    global _tracker
    check_limits()
    remaining = get_remaining_seconds()
    if remaining < REQUEST_TIMEOUT + 10:
        raise RuntimeError(f"剩余时间不足: 剩余{remaining:.1f}秒")
    
    prompt = build_prompt(task)
    task_type = task.get("task_type")
    
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": TOP_P
    }

    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_error = None
    error_msg = None

    for attempt in range(MAX_RETRIES):
        request = urllib.request.Request(
            API_URL, data=encoded_body,
            headers={"Authorization": "Bearer " + get_api_key(), "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                else:
                    content = result.get("content") or result.get("text") or json.dumps(result)
                parsed = clean_json_content(content)
                items = parsed.get("items", [])
                if not isinstance(items, list):
                    raise ValueError("API response items is not a list")
                usage = result.get("usage", {})
                update_token_usage(usage)
                if _tracker:
                    task_type_key = task_type.split('_')[1].lower()
                    _tracker.record_api_call(task_type_key, usage.get("total_tokens", 0), len(items), success=True)
                return items
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            error_msg = f"API HTTP {error.code}: {error_body[:1000]}"
            last_error = RuntimeError(error_msg)
            if error.code not in RETRYABLE_CODES:
                break
        except (urllib.error.URLError, TimeoutError) as error:
            error_msg = f"API network error: {error}"
            last_error = RuntimeError(error_msg)
        if attempt < MAX_RETRIES - 1:
            time.sleep((2 ** attempt) + random.random())

    if _tracker:
        _tracker.record_api_call(task_type.split('_')[1].lower(), 0, 0, success=False, error=error_msg)
    raise last_error or RuntimeError("API request failed")


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
                ":now": now, ":source": DATA_SOURCE,
            },
        )
        if _tracker:
            _tracker.record_db_operation("upsert_category", 1)
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
                ":status": "ACTIVE", ":now": now, ":source": DATA_SOURCE,
            },
        )
        if _tracker:
            _tracker.record_db_operation("upsert_brand", 1)
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
            "first_seen_at = if_not_exists(first_seen_at, :now), last_seen_at = :now, "
            "#source = :source"
        )
        values = {
            ":type": "PRODUCT", ":category": category, ":brand": brand,
            ":model": model, ":normalized_model": normalize(model).casefold(),
            ":status": "ACTIVE", ":unverified": "UNVERIFIED",
            ":now": now, ":source": DATA_SOURCE,
        }
        if confidence is not None:
            expression += ", confidence = :confidence"
            values[":confidence"] = str(max(0.0, min(1.0, float(confidence))))
        if release_date and re.match(r"^\d{4}-\d{2}-\d{2}", normalize(release_date)):
            expression += ", release_date = :release_date"
            values[":release_date"] = normalize(release_date)
        table.update_item(
            Key={"PK": product_pk, "SK": "META"},
            UpdateExpression=expression,
            ExpressionAttributeNames={"#status": "status", "#source": "source"},
            ExpressionAttributeValues=values,
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
            _tracker.record_db_operation("upsert_product", 1)
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_product", 0, success=False)
        raise


def process_discovery(event):
    global _total_tokens_used, _lambda_start_time, _tracker
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    _tracker = DiscoveryTracker()
    
    task_type = event.get("task_type", "DISCOVER_CATEGORIES")
    log("INFO", "开始发现处理", task_type=task_type, model=MODEL)
    
    try:
        if task_type == "DISCOVER_CATEGORIES":
            _tracker.start_phase("discover_categories")
            items = call_api({"task_type": "DISCOVER_CATEGORIES", "max_items": MAX_CATEGORIES})
            categories = []
            for item in items:
                if isinstance(item, dict) and "category" in item:
                    category = normalize(item["category"])
                    if category:
                        upsert_category(category)
                        categories.append(category)
            _tracker.end_phase()
            log("INFO", "品类发现完成", count=len(categories))
            
            for category in categories[:CATEGORY_LIMIT]:
                if _total_tokens_used >= MAX_TOTAL_TOKENS or get_remaining_seconds() < REQUEST_TIMEOUT + 10:
                    break
                time.sleep(API_CALL_DELAY)
                _tracker.start_phase(f"discover_brands_{category}")
                brand_items = call_api({"task_type": "DISCOVER_BRANDS", "category": category, "max_items": MAX_BRANDS})
                brands = []
                for item in brand_items:
                    if isinstance(item, dict) and "brand" in item:
                        brand = normalize(item["brand"])
                        if brand:
                            upsert_brand(category, brand)
                            brands.append((category, brand))
                _tracker.end_phase()
                
                for cat, brand in brands[:BRAND_LIMIT]:
                    if _total_tokens_used >= MAX_TOTAL_TOKENS or get_remaining_seconds() < REQUEST_TIMEOUT + 10:
                        break
                    time.sleep(API_CALL_DELAY)
                    _tracker.start_phase(f"discover_models_{brand}")
                    latest_date = get_latest_model_date(brand)
                    model_items = call_api({
                        "task_type": "DISCOVER_MODELS", "category": cat, "brand": brand,
                        "max_items": MAX_MODELS, "search_date": latest_date
                    })
                    for item in model_items:
                        if isinstance(item, dict) and "model" in item:
                            upsert_product(cat, brand, item.get("model"),
                                          item.get("confidence"), item.get("release_date"))
                    _tracker.end_phase()
            
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
            items = call_api({
                "task_type": "DISCOVER_MODELS", "category": category, "brand": brand,
                "max_items": MAX_MODELS, "search_date": latest_date
            })
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
        if "Token用量已达上限" in error_msg or "Lambda超时倒计时" in error_msg:
            if _tracker:
                _tracker.end_phase()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "任务已安全中断", "reason": error_msg,
                    "total_tokens_used": _total_tokens_used,
                    "elapsed_seconds": get_elapsed_seconds()
                }, ensure_ascii=False)
            }
        raise
    except Exception as e:
        if _tracker:
            _tracker.end_phase()
        raise


def lambda_handler(event, context):
    global _lambda_start_time, _tracker
    _lambda_start_time = time.time()
    _tracker = None
    try:
        return process_discovery(event)
    except Exception as error:
        log("ERROR", "处理失败", error_type=type(error).__name__, error=str(error))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "内部错误", "details": str(error),
                "total_tokens_used": _total_tokens_used,
                "elapsed_seconds": get_elapsed_seconds()
            }, ensure_ascii=False)
        }
