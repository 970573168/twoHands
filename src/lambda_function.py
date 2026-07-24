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

# ============================================
# 所有配置项都从环境变量读取
# ============================================

# API 配置
API_URL = os.environ.get("API_URL", "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions")
MODEL = os.environ.get("AI_MODEL", "doubao-seed-2-1-pro-260628")
SECRET_NAME = os.environ.get("SECRET_NAME", "")
API_KEY = os.environ.get("API_KEY", "")

# API 调用参数配置
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4000"))
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

_api_key_cache = None
_brand_date_cache = {}

# 全局Token计数器
_total_tokens_used = 0

# 记录Lambda开始时间
_lambda_start_time = None

# ============================================
# 新增：详细追踪器类
# ============================================

class DiscoveryTracker:
    """发现任务追踪器 - 记录Token消耗和时间花费"""
    
    def __init__(self):
        self.start_time = time.time()
        self.phase_stack = []
        self.current_phase = None
        self.phase_start_time = None
        
        # Token消耗详情
        self.token_details = {
            "categories": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "brands": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "models": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0},
            "total": {"api_calls": 0, "tokens": 0, "items": 0, "errors": 0}
        }
        
        # 时间花费详情
        self.timing_details = {
            "phases": {},
            "api_calls": [],
            "db_operations": []
        }
        
        # 汇总统计
        self.summary = {
            "categories_discovered": 0,
            "brands_discovered": 0,
            "models_discovered": 0,
            "total_api_calls": 0,
            "total_tokens_used": 0,
            "elapsed_seconds": 0
        }
    
    def start_phase(self, phase_name, **metadata):
        """开始一个新的处理阶段"""
        # 如果有当前阶段，先结束它
        if self.current_phase:
            self.end_phase()
        
        self.current_phase = phase_name
        self.phase_start_time = time.time()
        self.phase_stack.append(phase_name)
        
        log("INFO", f"开始阶段: {phase_name}", 
            phase=phase_name,
            stack_depth=len(self.phase_stack),
            **metadata)
    
    def end_phase(self):
        """结束当前阶段"""
        if not self.current_phase or not self.phase_start_time:
            return
        
        elapsed = time.time() - self.phase_start_time
        
        # 记录阶段耗时
        if self.current_phase not in self.timing_details["phases"]:
            self.timing_details["phases"][self.current_phase] = {
                "calls": 0,
                "total_seconds": 0,
                "min_seconds": float('inf'),
                "max_seconds": 0,
                "avg_seconds": 0
            }
        
        phase_stats = self.timing_details["phases"][self.current_phase]
        phase_stats["calls"] += 1
        phase_stats["total_seconds"] += elapsed
        phase_stats["min_seconds"] = min(phase_stats["min_seconds"], elapsed)
        phase_stats["max_seconds"] = max(phase_stats["max_seconds"], elapsed)
        phase_stats["avg_seconds"] = phase_stats["total_seconds"] / phase_stats["calls"]
        
        log("INFO", f"阶段完成: {self.current_phase}",
            phase=self.current_phase,
            duration_seconds=round(elapsed, 2),
            total_elapsed=round(time.time() - self.start_time, 2))
        
        # 弹出栈
        if self.phase_stack and self.phase_stack[-1] == self.current_phase:
            self.phase_stack.pop()
        
        self.current_phase = None
        self.phase_start_time = None
    
    def record_api_call(self, task_type, tokens_used, item_count, success=True, error=None):
        """记录API调用"""
        if task_type not in self.token_details:
            task_type = "total"
        
        # 更新token统计
        self.token_details[task_type]["api_calls"] += 1
        self.token_details[task_type]["tokens"] += tokens_used
        self.token_details[task_type]["items"] += item_count
        if not success:
            self.token_details[task_type]["errors"] += 1
        
        # 更新总计
        self.token_details["total"]["api_calls"] += 1
        self.token_details["total"]["tokens"] += tokens_used
        self.token_details["total"]["items"] += item_count
        if not success:
            self.token_details["total"]["errors"] += 1
        
        # 记录API调用详情
        self.timing_details["api_calls"].append({
            "timestamp": time.time(),
            "task_type": task_type,
            "tokens_used": tokens_used,
            "item_count": item_count,
            "success": success,
            "error": str(error) if error else None
        })
        
        log("INFO", "API调用记录",
            task_type=task_type,
            tokens_used=tokens_used,
            item_count=item_count,
            success=success,
            total_tokens=self.token_details["total"]["tokens"],
            total_api_calls=self.token_details["total"]["api_calls"])
    
    def record_db_operation(self, operation_type, item_count, success=True):
        """记录数据库操作"""
        self.timing_details["db_operations"].append({
            "timestamp": time.time(),
            "operation_type": operation_type,
            "item_count": item_count,
            "success": success
        })
        
        log("DEBUG", "数据库操作记录",
            operation_type=operation_type,
            item_count=item_count,
            success=success)
    
    def get_summary(self):
        """获取汇总统计"""
        total_elapsed = time.time() - self.start_time
        
        # 如果有未结束的阶段，结束它
        if self.current_phase:
            self.end_phase()
        
        # 计算各阶段统计
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
                    "api_calls": stats["api_calls"],
                    "tokens": stats["tokens"],
                    "items": stats["items"],
                    "errors": stats["errors"],
                    "avg_tokens_per_call": stats["tokens"] / stats["api_calls"] if stats["api_calls"] > 0 else 0,
                    "avg_items_per_call": stats["items"] / stats["api_calls"] if stats["api_calls"] > 0 else 0
                }
                for task_type, stats in self.token_details.items()
                if task_type != "total" and stats["api_calls"] > 0
            },
            "token_breakdown_percentage": {
                task_type: round((stats["tokens"] / self.token_details["total"]["tokens"] * 100), 2)
                for task_type, stats in self.token_details.items()
                if task_type != "total" and stats["tokens"] > 0 and self.token_details["total"]["tokens"] > 0
            },
            "api_call_efficiency": {
                "tokens_per_item": self.token_details["total"]["tokens"] / self.token_details["total"]["items"] 
                                   if self.token_details["total"]["items"] > 0 else 0,
                "items_per_call": self.token_details["total"]["items"] / self.token_details["total"]["api_calls"]
                                 if self.token_details["total"]["api_calls"] > 0 else 0
            }
        }
    
    def log_summary(self):
        """输出汇总日志"""
        summary = self.get_summary()
        
        log("INFO", "=== 任务执行摘要 ===")
        log("INFO", "总耗时",
            seconds=summary["total_elapsed_seconds"],
            api_calls=summary["total_api_calls"],
            total_tokens=summary["total_tokens_used"],
            total_items=summary["total_items_discovered"],
            errors=summary["total_errors"])
        
        # 各阶段耗时
        for phase, stats in summary["phase_stats"].items():
            log("INFO", f"阶段统计: {phase}",
                calls=stats["calls"],
                total_seconds=stats["total_seconds"],
                avg_seconds=stats["avg_seconds"],
                min_seconds=stats["min_seconds"],
                max_seconds=stats["max_seconds"])
        
        # Token消耗详情
        for task_type, stats in summary["token_by_task"].items():
            log("INFO", f"Token消耗: {task_type}",
                api_calls=stats["api_calls"],
                tokens=stats["tokens"],
                items=stats["items"],
                avg_tokens_per_call=round(stats["avg_tokens_per_call"], 2),
                avg_items_per_call=round(stats["avg_items_per_call"], 2))
        
        # Token百分比
        if summary["token_breakdown_percentage"]:
            log("INFO", "Token消耗占比",
                breakdown=summary["token_breakdown_percentage"])
        
        # 效率指标
        log("INFO", "效率指标",
            tokens_per_item=round(summary["api_call_efficiency"]["tokens_per_item"], 2),
            items_per_call=round(summary["api_call_efficiency"]["items_per_call"], 2))
        
        return summary

# ============================================

# 全局追踪器实例
_tracker = None

def log(level, message, **fields):
    entry = {
        "level": level,
        "message": message,
        "total_tokens": _total_tokens_used,
        "elapsed_seconds": get_elapsed_seconds(),
        **fields,
    }
    print(json.dumps(entry, ensure_ascii=False, default=str))


def get_elapsed_seconds():
    """获取从Lambda开始到现在的运行时间（秒）"""
    if _lambda_start_time is None:
        return 0
    return time.time() - _lambda_start_time


def get_remaining_seconds():
    """获取Lambda剩余可用时间（秒）"""
    elapsed = get_elapsed_seconds()
    remaining = LAMBDA_TIMEOUT_SECONDS - elapsed - LAMBDA_TIMEOUT_BUFFER
    return max(0, remaining)


def check_timeout():
    """检查是否接近Lambda超时"""
    remaining = get_remaining_seconds()
    if remaining <= 0:
        raise RuntimeError(
            f"Lambda超时倒计时: 已运行{get_elapsed_seconds():.1f}秒, "
            f"超时限制{LAMBDA_TIMEOUT_SECONDS}秒, 缓冲{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_limits():
    """检查所有限制条件（Token + 超时）"""
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
    """从数据库获取该品牌最晚发布的型号发布日期（带缓存）"""
    brand_key = key_part(brand)
    
    if brand_key in _brand_date_cache:
        return _brand_date_cache[brand_key]
    
    try:
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
            ScanIndexForward=False,
            Limit=1
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
    """检查Token是否超过限制"""
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token用量已达上限: {_total_tokens_used}/{MAX_TOTAL_TOKENS}，中断执行"
        )


def update_token_usage(usage):
    """更新全局Token用量"""
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        log("INFO", "Token用量更新", 
            added_tokens=total, 
            total_tokens=_total_tokens_used,
            limit=MAX_TOTAL_TOKENS,
            remaining_tokens=MAX_TOTAL_TOKENS - _total_tokens_used)


def build_prompt(task):
    task_type = task.get("task_type")
    max_items = int(task.get("max_items", 20))
    search_date = task.get("search_date", "")

    if task_type == "DISCOVER_CATEGORIES":
        instruction = (
            "一般的な電子製品のカテゴリをリストアップしてください。"
            "各エントリにはcategoryフィールドのみを含めてください。"
            "ブランド、アクセサリ、サービス、重複する同義語は含めないでください。"
        )
    elif task_type == "DISCOVER_BRANDS":
        category = normalize(task.get("category"))
        instruction = (
            f"電子製品カテゴリ「{category}」の実際のブランドをリストアップしてください。"
            "各エントリにはcategoryとbrandフィールドを含めてください。"
            "架空のブランドを作成しないでください。"
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
            "モデルは製品シリーズではなく、具体的な製品モデルである必要があります。"
        )
    else:
        raise ValueError(f"Unknown task_type: {task_type}")

    prompt = f"""
    {instruction}

    「items」配列を含むJSONオブジェクトのみを返してください。最大{max_items}エントリ。
    各エントリには以下のフィールドを含めてください（オプションフィールドは空文字列）：
    - category: 文字列
    - brand: 文字列または空
    - model: 文字列または空
    - confidence: 0-1の数値またはnull
    - release_date: YYYY-MM-DD形式の文字列または空（該当する場合）

    ルール：
    - JSONのみを返し、マークダウンや説明は不要
    - あなたの知識ベースのみを使用し、web_searchや外部検索は使用しないでください
    - 信頼できるソースからの実際の電子製品データのみを含める
    - 不確かな場合はconfidenceを下げ、推測しない
    - 大文字小文字、スペース、全角/半角文字を正規化して重複をマージ
    - 公式ブランド名とモデル名を使用
    """

    return prompt


def call_api(task):
    """调用 AI API"""
    global _tracker
    
    check_limits()
    
    remaining = get_remaining_seconds()
    if remaining < REQUEST_TIMEOUT + 10:
        raise RuntimeError(
            f"剩余时间不足，无法完成API调用: 剩余{remaining:.1f}秒, "
            f"请求超时{REQUEST_TIMEOUT}秒"
        )
    
    prompt = build_prompt(task)
    task_type = task.get("task_type")
    
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": TOP_P
    }

    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_error = None
    
    # 开始API调用计时
    api_start_time = time.time()
    success = False
    items = []
    error_msg = None

    for attempt in range(MAX_RETRIES):
        request = urllib.request.Request(
            API_URL,
            data=encoded_body,
            headers={
                "Authorization": "Bearer " + get_api_key(),
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    content = message.get("content", "")
                else:
                    content = result.get("content") or result.get("text") or json.dumps(result)

                parsed = clean_json_content(content)
                items = parsed.get("items", [])
                if not isinstance(items, list):
                    if "items" in parsed:
                        items = parsed["items"]
                    else:
                        for key, value in parsed.items():
                            if isinstance(value, list):
                                items = value
                                break
                
                if not isinstance(items, list):
                    raise ValueError("API response items is not a list")
                
                usage = result.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                update_token_usage(usage)
                
                success = True
                api_elapsed = time.time() - api_start_time
                
                log("INFO", "API请求完成", 
                    model=MODEL, 
                    task_type=task_type,
                    usage=usage, 
                    item_count=len(items),
                    total_tokens=_total_tokens_used,
                    api_duration_seconds=round(api_elapsed, 2),
                    remaining_seconds=get_remaining_seconds())
                
                # 记录API调用到追踪器
                if _tracker:
                    task_type_key = task_type.split('_')[1].lower()  # DISCOVER_CATEGORIES -> categories
                    _tracker.record_api_call(
                        task_type_key,
                        total_tokens,
                        len(items),
                        success=True
                    )
                
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
            delay = (2 ** attempt) + random.random()
            time.sleep(delay)

    # API调用失败
    api_elapsed = time.time() - api_start_time
    
    # 记录失败的API调用
    if _tracker:
        task_type_key = task_type.split('_')[1].lower()
        _tracker.record_api_call(
            task_type_key,
            0,  # 没有消耗token
            0,
            success=False,
            error=error_msg
        )
    
    log("ERROR", "API调用失败",
        task_type=task_type,
        error=error_msg,
        api_duration_seconds=round(api_elapsed, 2))
    
    raise last_error or RuntimeError("API request failed")


def upsert_category(category):
    """插入或更新品类"""
    global _tracker
    
    category = normalize(category)
    if not category:
        return

    try:
        now = int(time.time())
        table.update_item(
            Key={
                "PK": f"CATEGORY#{key_part(category)}",
                "SK": "META",
            },
            UpdateExpression=(
                "SET entity_type = :type, #name = :name, #status = :status, "
                "first_seen_at = if_not_exists(first_seen_at, :now), "
                "last_seen_at = :now, #source = :source"
            ),
            ExpressionAttributeNames={
                "#name": "name",
                "#status": "status",
                "#source": "source",
            },
            ExpressionAttributeValues={
                ":type": "CATEGORY",
                ":name": category,
                ":status": "ACTIVE",
                ":now": now,
                ":source": DATA_SOURCE,
            },
        )
        
        if _tracker:
            _tracker.record_db_operation("upsert_category", 1, success=True)
            
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_category", 0, success=False)
        raise


def upsert_brand(category, brand):
    """插入或更新品牌"""
    global _tracker
    
    category = normalize(category)
    brand = normalize(brand)
    if not category or not brand:
        return

    try:
        now = int(time.time())
        table.update_item(
            Key={
                "PK": f"CATEGORY#{key_part(category)}",
                "SK": f"BRAND#{key_part(brand)}",
            },
            UpdateExpression=(
                "SET entity_type = :type, category = :category, brand = :brand, "
                "#status = :status, first_seen_at = if_not_exists(first_seen_at, :now), "
                "last_seen_at = :now, #source = :source"
            ),
            ExpressionAttributeNames={
                "#status": "status",
                "#source": "source",
            },
            ExpressionAttributeValues={
                ":type": "BRAND",
                ":category": category,
                ":brand": brand,
                ":status": "ACTIVE",
                ":now": now,
                ":source": DATA_SOURCE,
            },
        )
        
        if _tracker:
            _tracker.record_db_operation("upsert_brand", 1, success=True)
            
    except Exception as e:
        if _tracker:
            _tracker.record_db_operation("upsert_brand", 0, success=False)
        raise


def upsert_product(category, brand, model, confidence=None, release_date=None):
    """插入或更新产品"""
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
            ":type": "PRODUCT",
            ":category": category,
            ":brand": brand,
            ":model": model,
            ":normalized_model": normalize(model).casefold(),
            ":status": "ACTIVE",
            ":unverified": "UNVERIFIED",
            ":now": now,
            ":source": DATA_SOURCE,
        }

        if confidence is not None:
            try:
                confidence_value = str(max(0.0, min(1.0, float(confidence))))
                expression += ", confidence = :confidence"
                values[":confidence"] = confidence_value
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
            ExpressionAttributeNames={
                "#status": "status",
                "#source": "source",
            },
            ExpressionAttributeValues=values,
        )

        gsi1_item = {
            "PK": f"BRAND#{key_part(brand)}",
            "SK": f"MODEL#{key_part(model)}",
            "GSI1PK": f"BRAND#{key_part(brand)}",
            "GSI1SK": release_date if release_date else "0000-00-00",
            "entity_type": "BRAND_MODEL",
            "category": category,
            "brand": brand,
            "model": model,
            "product_pk": product_pk,
            "last_seen_at": now
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


def process_discovery(event):
    """主发现处理逻辑（手动触发入口）"""
    global _total_tokens_used, _lambda_start_time, _tracker
    
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    
    # 初始化追踪器
    _tracker = DiscoveryTracker()
    _tracker.start_phase("discovery_start", 
                         task_type=event.get("task_type"),
                         model=MODEL,
                         token_limit=MAX_TOTAL_TOKENS,
                         lambda_timeout=LAMBDA_TIMEOUT_SECONDS)
    
    task_type = event.get("task_type", "DISCOVER_CATEGORIES")
    
    log("INFO", "开始发现处理", 
        task_type=task_type, 
        model=MODEL, 
        token_limit=MAX_TOTAL_TOKENS,
        lambda_timeout=LAMBDA_TIMEOUT_SECONDS,
        lambda_timeout_buffer=LAMBDA_TIMEOUT_BUFFER,
        config={
            "api_url": API_URL,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "category_limit": CATEGORY_LIMIT,
            "brand_limit": BRAND_LIMIT,
            "api_call_delay": API_CALL_DELAY
        })
    
    try:
        if task_type == "DISCOVER_CATEGORIES":
            # ========================================
            # 阶段1: 发现品类
            # ========================================
            _tracker.start_phase("discover_categories")
            
            task = {
                "task_type": "DISCOVER_CATEGORIES",
                "max_items": MAX_CATEGORIES
            }
            items = call_api(task)
            
            categories = []
            for item in items:
                if isinstance(item, dict) and "category" in item:
                    category = normalize(item["category"])
                    if category:
                        upsert_category(category)
                        categories.append(category)
            
            _tracker.end_phase()
            log("INFO", "品类发现完成", count=len(categories), categories=categories[:10])
            
            # ========================================
            # 阶段2: 发现品牌
            # ========================================
            category_count = 0
            for category in categories[:CATEGORY_LIMIT]:
                # 检查限制
                if _total_tokens_used >= MAX_TOTAL_TOKENS:
                    log("WARN", "Token用量接近上限，停止品牌发现", 
                        category=category, 
                        total_tokens=_total_tokens_used)
                    break
                
                if get_remaining_seconds() < REQUEST_TIMEOUT + 10:
                    log("WARN", "剩余时间不足，停止品牌发现",
                        category=category,
                        remaining_seconds=get_remaining_seconds())
                    break
                
                _tracker.start_phase(f"discover_brands_{category}")
                time.sleep(API_CALL_DELAY)
                
                brand_task = {
                    "task_type": "DISCOVER_BRANDS",
                    "category": category,
                    "max_items": MAX_BRANDS
                }
                brand_items = call_api(brand_task)
                
                brands = []
                for item in brand_items:
                    if isinstance(item, dict) and "brand" in item:
                        brand = normalize(item["brand"])
                        if brand and category:
                            upsert_brand(category, brand)
                            brands.append((category, brand))
                
                _tracker.end_phase()
                log("INFO", "品牌发现完成", category=category, count=len(brands))
                
                # ========================================
                # 阶段3: 发现型号
                # ========================================
                brand_count = 0
                for cat, brand in brands[:BRAND_LIMIT]:
                    # 检查限制
                    if _total_tokens_used >= MAX_TOTAL_TOKENS:
                        log("WARN", "Token用量接近上限，停止型号发现", 
                            category=cat, 
                            brand=brand, 
                            total_tokens=_total_tokens_used)
                        break
                    
                    if get_remaining_seconds() < REQUEST_TIMEOUT + 10:
                        log("WARN", "剩余时间不足，停止型号发现",
                            category=cat,
                            brand=brand,
                            remaining_seconds=get_remaining_seconds())
                        break
                    
                    _tracker.start_phase(f"discover_models_{brand}")
                    time.sleep(API_CALL_DELAY)
                    
                    latest_date = get_latest_model_date(brand)
                    
                    model_task = {
                        "task_type": "DISCOVER_MODELS",
                        "category": cat,
                        "brand": brand,
                        "max_items": MAX_MODELS,
                        "search_date": latest_date
                    }
                    model_items = call_api(model_task)
                    
                    model_count = 0
                    for item in model_items:
                        if isinstance(item, dict) and "model" in item:
                            upsert_product(
                                category=cat,
                                brand=brand,
                                model=item.get("model"),
                                confidence=item.get("confidence"),
                                release_date=item.get("release_date")
                            )
                            model_count += 1
                    
                    _tracker.end_phase()
                    log("INFO", "型号发现完成", category=cat, brand=brand, count=model_count)
                    brand_count += 1
                
                category_count += 1
                if _total_tokens_used >= MAX_TOTAL_TOKENS:
                    break
                if get_remaining_seconds() < REQUEST_TIMEOUT + 10:
                    break
            
            # 输出汇总报告
            summary = _tracker.log_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "发现处理完成",
                    "categories_discovered": len(categories),
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "remaining_seconds": get_remaining_seconds(),
                    "summary": summary
                }, ensure_ascii=False)
            }
        
        elif task_type == "DISCOVER_MODELS":
            # ========================================
            # 单品牌型号发现
            # ========================================
            category = event.get("category", "")
            brand = event.get("brand", "")
            
            if not category or not brand:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "需要提供 category 和 brand 参数"}, ensure_ascii=False)
                }
            
            _tracker.start_phase(f"discover_models_{brand}")
            
            latest_date = get_latest_model_date(brand)
            
            task = {
                "task_type": "DISCOVER_MODELS",
                "category": category,
                "brand": brand,
                "max_items": MAX_MODELS,
                "search_date": latest_date
            }
            items = call_api(task)
            
            model_count = 0
            for item in items:
                if isinstance(item, dict) and "model" in item:
                    upsert_product(
                        category=category,
                        brand=brand,
                        model=item.get("model"),
                        confidence=item.get("confidence"),
                        release_date=item.get("release_date")
                    )
                    model_count += 1
            
            _tracker.end_phase()
            
            summary = _tracker.log_summary()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "型号发现完成",
                    "models_discovered": model_count,
                    "search_date": latest_date,
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "remaining_seconds": get_remaining_seconds(),
                    "summary": summary
                }, ensure_ascii=False)
            }
        
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"未知的 task_type: {task_type}"}, ensure_ascii=False)
            }
    
    except RuntimeError as e:
        error_msg = str(e)
        if "Token用量已达上限" in error_msg or "Lambda超时倒计时" in error_msg or "剩余时间不足" in error_msg:
            # 记录中断时的状态
            if _tracker:
                _tracker.end_phase()  # 结束当前阶段
                summary = _tracker.get_summary()
            
            log("WARN", "任务中断", 
                reason=error_msg,
                total_tokens=_total_tokens_used, 
                limit=MAX_TOTAL_TOKENS,
                elapsed_seconds=get_elapsed_seconds(),
                remaining_seconds=get_remaining_seconds(),
                summary=summary if _tracker else None)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "任务已安全中断",
                    "reason": error_msg,
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS,
                    "elapsed_seconds": get_elapsed_seconds(),
                    "remaining_seconds": get_remaining_seconds(),
                    "summary": summary if _tracker else None
                }, ensure_ascii=False)
            }
        raise
    
    except Exception as e:
        # 记录异常
        if _tracker:
            _tracker.end_phase()
        
        log("ERROR", "处理异常",
            error_type=type(e).__name__,
            error=str(e),
            total_tokens=_total_tokens_used,
            elapsed_seconds=get_elapsed_seconds())
        
        raise


def lambda_handler(event, context):
    """Lambda入口函数，支持手动触发"""
    global _lambda_start_time, _tracker
    
    _lambda_start_time = time.time()
    _tracker = None
    
    try:
        log("INFO", "Lambda执行开始", 
            event=event,
            lambda_timeout=LAMBDA_TIMEOUT_SECONDS,
            lambda_timeout_buffer=LAMBDA_TIMEOUT_BUFFER,
            max_total_tokens=MAX_TOTAL_TOKENS)
        
        return process_discovery(event)
        
    except Exception as error:
        log(
            "ERROR",
            "处理失败",
            error_type=type(error).__name__,
            error=str(error),
            total_tokens=_total_tokens_used,
            elapsed_seconds=get_elapsed_seconds()
        )
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "内部错误",
                "details": str(error),
                "total_tokens_used": _total_tokens_used,
                "elapsed_seconds": get_elapsed_seconds()
            }, ensure_ascii=False)
        }
