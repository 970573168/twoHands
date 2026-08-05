"""将每次 AI 调用的 Token 用量写入独立的 DynamoDB 明细表。"""

import hashlib
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3


logger = logging.getLogger(__name__)

_TOKEN_TOTALS = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
_RECENT_TOKEN_CALLS = []
MAX_RECENT_TOKEN_CALLS = int(os.environ.get("TOKEN_USAGE_RECENT_LIMIT", "100"))
TOKEN_DETAIL_EVERY = int(os.environ.get("TOKEN_USAGE_DETAIL_EVERY", "100"))


def _compact_call(item):
    return {
        "call_id": item["call_id"],
        "occurred_at": item["occurred_at"],
        "provider": item["provider"],
        "model": item["model"],
        "task_type": item["task_type"],
        "category_name": item["category_name"],
        "input_tokens": item["input_tokens"],
        "output_tokens": item["output_tokens"],
        "total_tokens": item["total_tokens"],
    }


def _build_summary(item):
    _TOKEN_TOTALS["calls"] += 1
    _TOKEN_TOTALS["input_tokens"] += item["input_tokens"]
    _TOKEN_TOTALS["output_tokens"] += item["output_tokens"]
    _TOKEN_TOTALS["total_tokens"] += item["total_tokens"]
    _RECENT_TOKEN_CALLS.append(_compact_call(item))
    del _RECENT_TOKEN_CALLS[:-MAX_RECENT_TOKEN_CALLS]
    return {
        "call_id": "SUMMARY",
        "record_type": "SUMMARY",
        "updated_at": item["occurred_at"],
        "function_name": item["function_name"],
        **_TOKEN_TOTALS,
        "recent_limit": MAX_RECENT_TOKEN_CALLS,
        "recent_calls": list(_RECENT_TOKEN_CALLS),
    }


def _to_dynamo_item(item):
    return {key: Decimal(str(value)) if isinstance(value, float) else value
            for key, value in item.items()}


def record_token_usage(provider, model, usage, *, prompt="", task_type="",
                       category_name="", table=None):
    """记录一次已完成的 AI 调用；统计写入失败不会影响主业务。"""
    table_name = os.environ.get("TOKEN_USAGE_TABLE", "")
    if table is None and not table_name:
        return False

    usage = usage or {}
    input_tokens = int(usage.get("prompt_tokens", usage.get("promptTokenCount", 0)) or 0)
    output_tokens = int(usage.get("completion_tokens", usage.get("candidatesTokenCount", 0)) or 0)
    total_tokens = int(
        usage.get("total_tokens", usage.get("totalTokenCount", input_tokens + output_tokens))
        or input_tokens + output_tokens
    )
    now = datetime.now(timezone.utc)
    item = {
        "call_id": f"{now.strftime('%Y%m%dT%H%M%S.%fZ')}#{uuid.uuid4().hex}",
        "occurred_at": now.isoformat(),
        "occurred_date": now.strftime("%Y-%m-%d"),
        "provider": str(provider),
        "model": str(model),
        "task_type": str(task_type),
        "category_name": str(category_name),
        "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "local"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "prompt_chars": len(prompt or ""),
        "prompt_sha256": hashlib.sha256((prompt or "").encode("utf-8")).hexdigest(),
        "created_at_epoch": int(time.time()),
    }

    try:
        target = table or boto3.resource("dynamodb").Table(table_name)
        # 主记录只保留加总和最近 100 条；明细每 100 次额外落一条检查点，避免无用数据无限增长。
        target.put_item(Item=_to_dynamo_item(_build_summary(item)))
        if _TOKEN_TOTALS["calls"] % max(1, TOKEN_DETAIL_EVERY) == 0:
            checkpoint = {**item, "record_type": "CHECKPOINT"}
            target.put_item(Item=_to_dynamo_item(checkpoint))
        return True
    except Exception as error:
        logger.exception("Token 用量记录写入失败: %s", error)
        return False
