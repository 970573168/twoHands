"""
型号批量分析 Lambda (定时触发)
功能：
1. 定时扫描数据库中的型号目录
2. 并发分析未处理的型号（默认3个并发）
3. 分析完成后记录时间戳
4. 单次执行最多分析6个型号
"""

import os
import re
import json
import time
import logging
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ==================== 环境变量辅助函数 ====================

def _env_int(key: str, default: int) -> int:
    value = os.getenv(key, "")
    if not value:
        return default
    return int(value)


def _env_decimal(key: str, default: str) -> Decimal:
    value = os.getenv(key, "")
    if not value:
        return Decimal(default)
    return Decimal(value)


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key, "")
    if not value:
        return default
    return value.lower() == "true"


# ============ 环境变量 ============
TABLE_NAME = os.getenv("TABLE_NAME", "YahooAuctionModelCatalog")
AI_API_URL = os.getenv("AI_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "doubao-seed-2-0-mini-260428")
AI_API_KEY = os.getenv("AI_API_KEY", "")
SECRET_NAME = os.getenv("SECRET_NAME", "yahoo-auction-ai-api-key")

SCHEDULE_ENABLED = _env_bool("SCHEDULE_ENABLED", False)
SCHEDULE_INTERVAL_HOURS = _env_int("SCHEDULE_INTERVAL_HOURS", 12)
MAX_MODELS_PER_RUN = _env_int("MAX_MODELS_PER_RUN", 6)
MAX_CONCURRENT_ANALYSIS = _env_int("MAX_CONCURRENT_ANALYSIS", 3)

AI_REQUEST_TIMEOUT = _env_int("AI_REQUEST_TIMEOUT", 90)
AI_MAX_RETRIES = _env_int("AI_MAX_RETRIES", 3)
AI_MAX_OUTPUT_TOKENS = _env_int("AI_MAX_OUTPUT_TOKENS", 4000)

CATEGORIES_TO_SCAN = os.getenv("CATEGORIES_TO_SCAN", "スマートフォン,タブレット,ノートPC,ゲーム機,カメラ")
MIN_CONFIDENCE_THRESHOLD = _env_decimal("MIN_CONFIDENCE_THRESHOLD", "0.5")

MAX_TOTAL_TOKENS = _env_int("MAX_TOTAL_TOKENS", 50000)
LAMBDA_TIMEOUT_SECONDS = _env_int("LAMBDA_TIMEOUT_SECONDS", 840)
LAMBDA_TIMEOUT_BUFFER = _env_int("LAMBDA_TIMEOUT_BUFFER", 60)

RETRYABLE_CODES = {408, 409, 429, 500, 502, 503, 504}

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
secretsmanager = boto3.client("secretsmanager")

_api_key_cache = None
_total_tokens_used = 0
_lambda_start_time = None


# ==================== 密钥管理 ====================

def get_api_key():
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache
    if AI_API_KEY:
        _api_key_cache = AI_API_KEY
        return _api_key_cache
    try:
        response = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response.get("SecretString")
        if not secret_string:
            raise RuntimeError("SecretにSecretStringがありません")
        try:
            secret_dict = json.loads(secret_string)
            api_key = (
                secret_dict.get("apiKey") or 
                secret_dict.get("api_key") or 
                secret_dict.get("key") or
                secret_dict.get("API_KEY")
            )
            if not api_key:
                raise RuntimeError("Secret JSONにapiKey/api_key/key/API_KEYが見つかりません")
            _api_key_cache = api_key
        except json.JSONDecodeError:
            _api_key_cache = secret_string
        return _api_key_cache
    except Exception as e:
        logger.error(f"Secrets Managerからのキー取得失敗: {e}")
        raise RuntimeError(f"APIキー取得不可: {e}")


# ==================== Token 和超时控制 ====================

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
            f"Lambdaタイムアウトカウントダウン: 実行時間{get_elapsed_seconds():.1f}秒, "
            f"タイムアウト制限{LAMBDA_TIMEOUT_SECONDS}秒, バッファ{LAMBDA_TIMEOUT_BUFFER}秒"
        )


def check_token_limit():
    if _total_tokens_used >= MAX_TOTAL_TOKENS:
        raise RuntimeError(
            f"Token使用量が上限に達しました: {_total_tokens_used}/{MAX_TOTAL_TOKENS}、実行中断"
        )


def check_limits():
    check_token_limit()
    check_timeout()


def update_token_usage(usage):
    global _total_tokens_used
    if usage:
        total = usage.get("total_tokens", 0)
        _total_tokens_used += total
        logger.info(
            f"Token使用量更新: +{total}, 合計={_total_tokens_used}/{MAX_TOTAL_TOKENS}, "
            f"残り={MAX_TOTAL_TOKENS - _total_tokens_used}"
        )


# ==================== 工具函数 ====================

def normalize(value: str) -> str:
    if not value:
        return ""
    value = str(value).strip()
    value = value.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
    ))
    return re.sub(r"\s+", " ", value)


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except:
        return default


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "y")
    return bool(value)


def response(status_code: int, body: Dict) -> Dict:
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False, default=str)
    }


# ==================== 数据库操作 ====================

def get_unanalyzed_models(categories: List[str], limit: int = 10) -> List[Dict]:
    unanalyzed_models = []
    
    for category in categories:
        if len(unanalyzed_models) >= limit:
            break
        
        try:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(f"CATEGORY#{category}"),
                FilterExpression=Attr("entity_type").eq("BRAND_MODEL"),
                Limit=50
            )
            
            brand_models = response.get("Items", [])
            
            for item in brand_models:
                if len(unanalyzed_models) >= limit:
                    break
                
                last_analyzed = item.get("last_analyzed_at")
                analysis_status = item.get("analysis_status", "PENDING")
                
                if not last_analyzed or analysis_status == "PENDING":
                    unanalyzed_models.append(item)
                    
        except Exception as e:
            logger.error(f"品类 {category} 查询失败: {e}")
            continue
    
    return unanalyzed_models[:limit]


def update_model_analysis_result(model_pk: str, analysis_result: Dict):
    now = datetime.now(timezone.utc).isoformat()
    
    table.update_item(
        Key={"PK": model_pk, "SK": "META"},
        UpdateExpression="""
            SET analysis_result = :result,
                analysis_status = :status,
                last_analyzed_at = :now,
                analyzed_at = :now
        """,
        ExpressionAttributeValues={
            ":result": analysis_result,
            ":status": "COMPLETED",
            ":now": now
        }
    )


def mark_model_analysis_failed(model_pk: str, error: str):
    now = datetime.now(timezone.utc).isoformat()
    
    table.update_item(
        Key={"PK": model_pk, "SK": "META"},
        UpdateExpression="""
            SET analysis_status = :status,
                analysis_error = :error,
                last_analyzed_at = :now
        """,
        ExpressionAttributeValues={
            ":status": "FAILED",
            ":error": error[:500],
            ":now": now
        }
    )


# ==================== AI 分析 ====================

def build_model_analysis_prompt(model_info: Dict) -> str:
    brand = model_info.get("brand", "")
    model = model_info.get("model", "")
    category = model_info.get("category", "")
    
    return f"""あなたは中古電子製品の市場分析専門家です。

以下の製品について、中古市場での価値と需要を分析してください。

製品情報：
- カテゴリ: {category}
- ブランド: {brand}
- モデル: {model}

以下のJSON形式で分析結果を返してください：

{{
  "market_analysis": {{
    "demand_level": "HIGH/MEDIUM/LOW",
    "price_range_jpy": {{
      "min": 最低価格（数値）,
      "max": 最高価格（数値）,
      "typical": 一般的な価格（数値）
    }},
    "depreciation_rate": "月間価値減少率（例：0.05）",
    "popular_features": ["人気の特徴1", "特徴2"],
    "target_buyers": ["想定購入者層1", "層2"],
    "seasonal_factors": "季節要因の説明"
  }},
  "resale_potential": {{
    "score": 1-10の数値,
    "margin_potential": "HIGH/MEDIUM/LOW",
    "turnover_speed": "FAST/MEDIUM/SLOW",
    "risk_factors": ["リスク要因1", "要因2"],
    "notes": "特記事項"
  }},
  "spec_analysis": {{
    "key_selling_points": ["セールスポイント1", "ポイント2"],
    "common_issues": ["よくある問題1", "問題2"],
    "accessories_value": "付属品の価値への影響"
  }}
}}

必ず有効なJSONのみを返してください。説明文は一切不要です。"""


def analyze_single_model(model_info: Dict) -> Tuple[Dict, Optional[Dict]]:
    model_pk = model_info.get("PK", "")
    brand = model_info.get("brand", "")
    model = model_info.get("model", "")
    
    logger.info(f"开始分析型号: {brand} {model}")
    
    try:
        prompt = build_model_analysis_prompt(model_info)
        result = call_ai_with_retry(prompt)
        
        if result:
            logger.info(f"型号分析完成: {brand} {model}")
            return model_info, result
        else:
            logger.warning(f"型号分析返回空结果: {brand} {model}")
            return model_info, None
            
    except Exception as e:
        logger.error(f"型号分析失败 {brand} {model}: {e}")
        return model_info, None


# ==================== AI 调用 ====================

def call_ai_with_retry(prompt: str) -> Optional[Dict]:
    for attempt in range(AI_MAX_RETRIES):
        try:
            check_limits()
            remaining = get_remaining_seconds()
            if remaining < AI_REQUEST_TIMEOUT + 10:
                raise RuntimeError(f"残り時間不足: 残り{remaining:.1f}秒")
            
            result, finish_reason = call_ai(prompt)
            
            if result is not None:
                return result
            
            if finish_reason == "length":
                logger.error("AI出力がmax_tokens制限に達しました。リトライしません")
                return None
            
            logger.warning(f"AIが空結果を返しました (finish_reason={finish_reason})、リトライ {attempt + 1}/{AI_MAX_RETRIES}")
            
        except RuntimeError as e:
            error_msg = str(e)
            if "Token使用量が上限" in error_msg or "Lambdaタイムアウト" in error_msg or "残り時間不足" in error_msg:
                raise
            logger.error(f"AI呼び出し例外 (試行 {attempt + 1}): {e}")
        except Exception as e:
            logger.error(f"AI呼び出し例外 (試行 {attempt + 1}): {e}")
        
        if attempt < AI_MAX_RETRIES - 1:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    logger.error(f"AI呼び出し失敗、{AI_MAX_RETRIES}回リトライ済み")
    return None


def call_ai(prompt: str) -> Tuple[Optional[Dict], Optional[str]]:
    try:
        api_key = get_api_key()
    except Exception as e:
        raise
    
    body = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "あなたは中古電子製品の市場分析専門家です。必ず有効なJSON形式のみを返してください。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": AI_MAX_OUTPUT_TOKENS,
        "response_format": {"type": "json_object"}
    }
    
    encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    
    request = urllib.request.Request(
        AI_API_URL,
        data=encoded_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(request, timeout=AI_REQUEST_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            usage = result.get("usage", {})
            if usage:
                update_token_usage(usage)
            
            finish_reason = None
            content = ""
            
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason", "unknown")
            else:
                content = result.get("content", "")
                finish_reason = result.get("finish_reason", "unknown")
            
            parsed = parse_ai_json(content)
            return parsed, finish_reason
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"AI API HTTP {e.code}: {error_body[:500]}")
        if e.code in RETRYABLE_CODES:
            raise
        return None, f"http_{e.code}"
    except Exception as e:
        raise


def parse_ai_json(content: str) -> Optional[Dict]:
    if not content:
        return None
    content = content.strip()
    parse_attempts = [
        lambda c: json.loads(c),
        lambda c: json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", c)),
        lambda c: json.loads(re.search(r"\{[\s\S]*\}", c).group(0)),
    ]
    for attempt in parse_attempts:
        try:
            return attempt(content)
        except (json.JSONDecodeError, AttributeError):
            continue
    logger.error(f"AI応答を解析できません: {content[:500]}")
    return None


# ==================== 主处理逻辑 ====================

def process_model_analysis(event: Dict = None) -> Dict:
    global _total_tokens_used, _lambda_start_time
    _total_tokens_used = 0
    _lambda_start_time = time.time()
    
    start_time = time.time()
    
    result = {
        "status": "SUCCESS",
        "models_scanned": 0,
        "models_analyzed": 0,
        "models_failed": 0,
        "models_skipped": 0,
        "total_tokens_used": 0,
        "elapsed_seconds": 0,
        "details": []
    }
    
    try:
        categories = [cat.strip() for cat in CATEGORIES_TO_SCAN.split(",") if cat.strip()]
        logger.info(f"扫描品类: {categories}")
        
        unanalyzed_models = get_unanalyzed_models(categories, MAX_MODELS_PER_RUN * 2)
        
        if not unanalyzed_models:
            logger.info("没有未分析的型号")
            result["status"] = "NO_MODELS_TO_ANALYZE"
            result["elapsed_seconds"] = round(time.time() - start_time, 1)
            return result
        
        logger.info(f"找到 {len(unanalyzed_models)} 个未分析型号，将处理最多 {MAX_MODELS_PER_RUN} 个")
        
        models_to_analyze = unanalyzed_models[:MAX_MODELS_PER_RUN]
        result["models_scanned"] = len(unanalyzed_models)
        
        analyzed_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_ANALYSIS) as executor:
            future_to_model = {
                executor.submit(analyze_single_model, model): model
                for model in models_to_analyze
            }
            
            for future in as_completed(future_to_model):
                model_info = future_to_model[future]
                model_pk = model_info.get("PK", "")
                brand = model_info.get("brand", "")
                model_name = model_info.get("model", "")
                
                try:
                    check_limits()
                    
                    model_data, analysis_result = future.result()
                    
                    if analysis_result:
                        update_model_analysis_result(model_pk, analysis_result)
                        analyzed_count += 1
                        
                        result["details"].append({
                            "model_pk": model_pk,
                            "brand": brand,
                            "model": model_name,
                            "status": "SUCCESS"
                        })
                        
                        logger.info(f"型号分析成功: {brand} {model_name}")
                    else:
                        mark_model_analysis_failed(model_pk, "AI_RESPONSE_EMPTY")
                        failed_count += 1
                        
                        result["details"].append({
                            "model_pk": model_pk,
                            "brand": brand,
                            "model": model_name,
                            "status": "FAILED",
                            "error": "AI返回空结果"
                        })
                        
                except RuntimeError as e:
                    error_msg = str(e)
                    if "Token使用量が上限" in error_msg or "Lambdaタイムアウト" in error_msg:
                        logger.warning(f"分析中断: {error_msg}")
                        mark_model_analysis_failed(model_pk, error_msg)
                        failed_count += 1
                        break
                    else:
                        mark_model_analysis_failed(model_pk, str(e))
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"型号分析异常 {brand} {model_name}: {e}")
                    mark_model_analysis_failed(model_pk, str(e))
                    failed_count += 1
        
        result["models_analyzed"] = analyzed_count
        result["models_failed"] = failed_count
        result["models_skipped"] = len(models_to_analyze) - analyzed_count - failed_count
        
    except RuntimeError as e:
        error_msg = str(e)
        if "Token使用量が上限" in error_msg or "Lambdaタイムアウト" in error_msg:
            result["status"] = "INTERRUPTED"
            result["interrupt_reason"] = error_msg
            logger.warning(f"任务安全中断: {error_msg}")
        else:
            raise
            
    except Exception as e:
        logger.error(f"処理失敗: {e}", exc_info=True)
        result["status"] = "FAILED"
        result["error"] = str(e)
    
    result["total_tokens_used"] = _total_tokens_used
    result["elapsed_seconds"] = round(time.time() - start_time, 1)
    
    logger.info(f"分析完成: {json.dumps(result, ensure_ascii=False, default=str)}")
    return result


# ==================== Lambda 入口 ====================

def lambda_handler(event, context):
    global _lambda_start_time
    _lambda_start_time = time.time()
    
    logger.info(f"Lambda执行开始: event={json.dumps(event, ensure_ascii=False, default=str)}")
    
    try:
        if not SCHEDULE_ENABLED:
            logger.info("定时调度已禁用，执行手动触发分析")
            result = process_model_analysis(event)
            return response(200, result)
        
        source = event.get("source", "")
        if source == "aws.events":
            logger.info(f"定时触发执行 (间隔: {SCHEDULE_INTERVAL_HOURS}小时)")
            result = process_model_analysis()
            return response(200, result)
        else:
            logger.info("手动触发执行")
            result = process_model_analysis(event)
            return response(200, result)
            
    except Exception as e:
        logger.error(f"Lambda执行失败: {e}", exc_info=True)
        return response(500, {
            "error": "内部エラー",
            "details": str(e),
            "total_tokens_used": _total_tokens_used,
            "elapsed_seconds": get_elapsed_seconds()
        })
