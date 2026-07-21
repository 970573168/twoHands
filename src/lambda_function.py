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

# 修改为豆包模型配置
API_URL = os.environ.get("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
MODEL = os.environ.get("DOUBAO_MODEL", "doubao-seed-2-1-pro-260628")
SECRET_NAME = os.environ.get("DOUBAO_SECRET_NAME", os.environ.get("DEEPSEEK_SECRET_NAME", ""))
MAX_CATEGORIES = int(os.environ.get("MAX_CATEGORIES", "20"))
MAX_BRANDS = int(os.environ.get("MAX_BRANDS", "20"))
MAX_MODELS = int(os.environ.get("MAX_MODELS", "50"))
MAX_TOTAL_TOKENS = int(os.environ.get("MAX_TOTAL_TOKENS", "100000"))  # Token上限，默认10万

_api_key_cache = None
_brand_date_cache = {}  # 品牌日期缓存

# 全局Token计数器
_total_tokens_used = 0


def log(level, message, **fields):
    entry = {
        "level": level,
        "message": message,
        "total_tokens": _total_tokens_used,
        **fields,
    }
    print(json.dumps(entry, ensure_ascii=False, default=str))


def get_api_key():
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache

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
    # 全角英数字转换为半角
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
    
    # 检查缓存
    if brand_key in _brand_date_cache:
        return _brand_date_cache[brand_key]
    
    try:
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"BRAND#{brand_key}"),
            ScanIndexForward=False,  # 降序排列，最新的在前
            Limit=1
        )
        items = response.get("Items", [])
        if items:
            latest_date = items[0].get("release_date", "")
            if latest_date:
                _brand_date_cache[brand_key] = latest_date  # 缓存结果
                return latest_date
        
        _brand_date_cache[brand_key] = None  # 缓存空结果
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
        # 豆包API的usage字段通常包含 total_tokens
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        log("INFO", "Token用量更新", 
            added_tokens=total, 
            total_tokens=_total_tokens_used,
            limit=MAX_TOTAL_TOKENS)


def build_deepseek_prompt(task):
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
    """调用豆包API"""
    # 调用前检查Token限制
    check_token_limit()
    
    prompt = build_deepseek_prompt(task)
    
    # 豆包API使用 messages 格式
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that returns data in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    retryable_codes = {408, 409, 429, 500, 502, 503, 504}
    last_error = None

    for attempt in range(3):
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
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                # 豆包API响应格式：choices[0].message.content
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
                
                # 更新Token用量
                usage = result.get("usage", {})
                update_token_usage(usage)
                
                log("INFO", "API request completed", 
                    model=MODEL, 
                    usage=usage, 
                    item_count=len(items),
                    total_tokens=_total_tokens_used)
                
                return items

        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(
                f"API HTTP {error.code}: {error_body[:1000]}"
            )
            if error.code not in retryable_codes:
                raise last_error

        except (urllib.error.URLError, TimeoutError) as error:
            last_error = RuntimeError(f"API network error: {error}")

        if attempt < 2:
            delay = (2 ** attempt) + random.random()
            time.sleep(delay)

    raise last_error or RuntimeError("API request failed")


# 向后兼容，保留原函数名
def call_deepseek(task):
    return call_api(task)


def upsert_category(category):
    category = normalize(category)
    if not category:
        return

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
            ":source": "DOUBAO_AI",
        },
    )


def upsert_brand(category, brand):
    category = normalize(category)
    brand = normalize(brand)
    if not category or not brand:
        return

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
            ":source": "DOUBAO_AI",
        },
    )


def upsert_product(category, brand, model, confidence=None, release_date=None):
    category = normalize(category)
    brand = normalize(brand)
    model = normalize(model)
    if not category or not brand or not model:
        return

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
        ":source": "DOUBAO_AI",
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

    # 创建GSI1索引项，用于按品牌查询并按发布日期排序
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


def process_discovery(event):
    """主发现处理逻辑（手动触发入口）"""
    global _total_tokens_used
    _total_tokens_used = 0  # 每次执行重置Token计数
    
    task_type = event.get("task_type", "DISCOVER_CATEGORIES")
    
    log("INFO", "开始发现处理", task_type=task_type, model=MODEL, token_limit=MAX_TOTAL_TOKENS)
    
    try:
        if task_type == "DISCOVER_CATEGORIES":
            # 发现品类
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
            
            log("INFO", "品类发现完成", count=len(categories))
            
            # 从发现的品类中发现品牌
            for category in categories[:5]:  # 限制处理前5个品类
                # 每次API调用前检查Token限制
                if _total_tokens_used >= MAX_TOTAL_TOKENS:
                    log("WARN", "Token用量接近上限，停止品牌发现", 
                        category=category, 
                        total_tokens=_total_tokens_used)
                    break
                
                time.sleep(1)
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
                
                log("INFO", "品牌发现完成", category=category, count=len(brands))
                
                # 从发现的品牌中发现型号
                for cat, brand in brands[:3]:
                    # 每次API调用前检查Token限制
                    if _total_tokens_used >= MAX_TOTAL_TOKENS:
                        log("WARN", "Token用量接近上限，停止型号发现", 
                            category=cat, 
                            brand=brand, 
                            total_tokens=_total_tokens_used)
                        break
                    
                    time.sleep(1)
                    
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
                    
                    log("INFO", "型号发现完成", category=cat, brand=brand, count=model_count)
                
                # 内层循环也可能因Token限制而中断
                if _total_tokens_used >= MAX_TOTAL_TOKENS:
                    break
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "发现处理完成",
                    "categories_discovered": len(categories),
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS
                }, ensure_ascii=False)
            }
        
        elif task_type == "DISCOVER_MODELS":
            category = event.get("category", "")
            brand = event.get("brand", "")
            
            if not category or not brand:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "需要提供 category 和 brand 参数"}, ensure_ascii=False)
                }
            
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
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "型号发现完成",
                    "models_discovered": model_count,
                    "search_date": latest_date,
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS
                }, ensure_ascii=False)
            }
        
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"未知的 task_type: {task_type}"}, ensure_ascii=False)
            }
    
    except RuntimeError as e:
        if "Token用量已达上限" in str(e):
            log("WARN", "Token用量达到上限，任务中断", 
                total_tokens=_total_tokens_used, 
                limit=MAX_TOTAL_TOKENS)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Token用量达到上限，任务已安全中断",
                    "total_tokens_used": _total_tokens_used,
                    "token_limit": MAX_TOTAL_TOKENS
                }, ensure_ascii=False)
            }
        raise


def lambda_handler(event, context):
    """Lambda入口函数，支持手动触发"""
    try:
        log("INFO", "Lambda执行开始", event=event)
        
        return process_discovery(event)
        
    except Exception as error:
        log(
            "ERROR",
            "处理失败",
            error_type=type(error).__name__,
            error=str(error),
            total_tokens=_total_tokens_used
        )
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "内部错误",
                "details": str(error),
                "total_tokens_used": _total_tokens_used
            }, ensure_ascii=False)
        }
