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


def record_token_usage(provider, model, usage, *, prompt="", task_type="", table=None):
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
        # Decimal 可避免未来 usage 中出现浮点值时违反 DynamoDB 类型约束。
        target.put_item(Item={key: Decimal(str(value)) if isinstance(value, float) else value
                              for key, value in item.items()})
        return True
    except Exception as error:
        logger.exception("Token 用量记录写入失败: %s", error)
        return False
