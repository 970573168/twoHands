"""BUY_CANDIDATE 结束前最终复核与 SNS 邮件提醒 Lambda。"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

from yahoo_auction_scraper import scrape_active_item_current_price


logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUY_CANDIDATE_TABLE = os.environ.get(
    "BUY_CANDIDATE_TABLE", "YahooAuctionBuyCandidates-dev"
)
ACTIVE_TABLE = os.environ.get("ACTIVE_TABLE", "YahooAuctionActiveItems")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
FINAL_CHECK_BATCH_SIZE = int(os.environ.get("FINAL_CHECK_BATCH_SIZE", "20"))
FEE_RATE = Decimal(os.environ.get("FEE_RATE", "0.10"))
SHIPPING_COST = Decimal(os.environ.get("SHIPPING_COST", "1500"))
REPAIR_RESERVE = Decimal(os.environ.get("REPAIR_RESERVE", "0.05"))
RISK_RESERVE = Decimal(os.environ.get("RISK_RESERVE", "0.03"))

dynamodb = boto3.resource("dynamodb")
candidate_db = dynamodb.Table(BUY_CANDIDATE_TABLE)
active_db = dynamodb.Table(ACTIVE_TABLE)
sns = boto3.client("sns")


def _decimal(value, default="0"):
    try:
        return value if isinstance(value, Decimal) else Decimal(str(value))
    except (ValueError, TypeError, ArithmeticError):
        return Decimal(default)


def _end_epoch(value):
    try:
        return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp())
    except (ValueError, TypeError):
        return None


def calculate_final_pricing(candidate, current_price):
    """使用首次分析保存的市场价重新计算利润，不重新抓取 closed。"""
    market = _decimal(
        candidate.get("marketPrice", candidate.get("estimatedMarketPrice", 0))
    )
    buy = _decimal(current_price)
    shipping = _decimal(candidate.get("shippingCost", SHIPPING_COST))
    fee = (market * FEE_RATE).quantize(Decimal("1"))
    repair = (market * REPAIR_RESERVE).quantize(Decimal("1"))
    risk = (market * RISK_RESERVE).quantize(Decimal("1"))
    net = market - buy - fee - shipping - repair - risk
    margin = (net / market).quantize(Decimal("0.001")) if market > 0 else Decimal("0")
    investment = buy + shipping + repair + risk
    roi = (net / investment).quantize(Decimal("0.001")) if investment > 0 else Decimal("0")
    recommendation = (
        "BUY_CANDIDATE" if net > 0 and margin >= Decimal("0.20")
        else ("REVIEW" if net > 0 else "AVOID")
    )
    return {
        "market": int(market), "net": int(net), "margin": margin,
        "roi": roi, "recommendation": recommendation,
    }


def _update(item_id, fields):
    values = {}
    assignments = []
    for name, value in fields.items():
        token = f":{name}"
        assignments.append(f"{name} = {token}")
        values[token] = value
    candidate_db.update_item(
        Key={"itemID": item_id},
        UpdateExpression="SET " + ", ".join(assignments),
        ExpressionAttributeValues=values,
    )


def lock_candidate(item_id):
    try:
        candidate_db.update_item(
            Key={"itemID": item_id},
            UpdateExpression="SET reviewStatus = :running, updatedAt = :now",
            ConditionExpression=(
                "reviewStatus = :waiting AND reminderStatus = :not_sent"
            ),
            ExpressionAttributeValues={
                ":running": "FINAL_CHECK_RUNNING",
                ":waiting": "WAITING_FINAL_CHECK",
                ":not_sent": "NOT_SENT",
                ":now": int(time.time()),
            },
        )
        return True
    except candidate_db.meta.client.exceptions.ConditionalCheckFailedException:
        return False


def _email(candidate, current_price, pricing):
    subject = "【BUY候选】结束前提醒：{} {}".format(
        candidate.get("brand", ""), candidate.get("model", "")
    )
    message = f"""第二次复核已通过，拍卖即将结束。

当前利润仍满足 BUY 候选条件，请及时决定是否出价。

商品：{candidate.get('title', '')}
当前价：{current_price}円
市场价：{pricing['market']}円
预计利润：{pricing['net']}円
利润率：{pricing['margin']}
ROI：{pricing['roi']}
风险等级：{candidate.get('riskLevel', '')}
置信度：{candidate.get('pricingConfidence', '')}

结束时间：{candidate.get('endTime', '')}
商品链接：
{candidate.get('url', '')}

请在结束前确认是否出价。"""
    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject[:100], Message=message)


def send_test_email():
    """通过真实 SNS Topic 发送部署测试邮件，不写入候选表。"""
    if not SNS_TOPIC_ARN:
        raise RuntimeError("缺少 SNS_TOPIC_ARN，无法发送测试邮件")
    now = datetime.now(timezone.utc).isoformat()
    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="【系统测试】Yahoo 拍卖提醒邮件",
        Message=("这是一封真实的邮件发送测试。\n\n"
                 "Yahoo 拍卖最终复核提醒服务已成功连接 SNS。\n"
                 f"测试时间（UTC）：{now}\n"),
    )
    return {"状态": "测试邮件已发送", "消息ID": response.get("MessageId", "")}


def process_candidate(candidate, now=None):
    now = int(now if now is not None else time.time())
    item_id = str(candidate["itemID"])
    if not lock_candidate(item_id):
        return "LOCK_SKIPPED"
    logger.info(
        "Final check started: itemID=%s endEpoch=%s currentTime=%s",
        item_id, candidate.get("endEpoch"), now,
    )

    try:
        current = scrape_active_item_current_price(item_id)
    except Exception:
        logger.exception("Current price fetch raised an error: itemID=%s", item_id)
        current = None
    if not current:
        _update(item_id, {
            "reviewStatus": "FINAL_CHECK_FAILED", "reminderStatus": "FAILED",
            "reminderError": "PRICE_FETCH_FAILED", "updatedAt": now,
        })
        return "PRICE_FETCH_FAILED"

    latest_end_epoch = _end_epoch(current.get("endTime")) or int(candidate.get("endEpoch", 0))
    if current.get("isEnded") or (latest_end_epoch and latest_end_epoch <= now):
        _update(item_id, {
            "candidateStatus": "EXPIRED", "reviewStatus": "EXPIRED",
            "reminderStatus": "SKIPPED", "updatedAt": now,
        })
        logger.info("Reminder skipped: itemID=%s reason=%s", item_id, "AUCTION_ENDED")
        return "EXPIRED"

    current_price = int(current.get("price", 0) or 0)
    if current_price <= 0:
        _update(item_id, {
            "reviewStatus": "FINAL_CHECK_FAILED", "reminderStatus": "FAILED",
            "reminderError": "PRICE_FETCH_FAILED", "updatedAt": now,
        })
        return "PRICE_FETCH_FAILED"

    pricing = calculate_final_pricing(candidate, current_price)
    logger.info(
        "Final check result: itemID=%s recommendation=%s current=%s market=%s net=%s margin=%s",
        item_id, pricing["recommendation"], current_price, pricing["market"],
        pricing["net"], pricing["margin"],
    )
    final_fields = {
        "finalCurrentPrice": current_price,
        "finalNetProfit": pricing["net"],
        "finalMargin": pricing["margin"],
        "finalROI": pricing["roi"],
        "currentBidPrice": current_price,
        "updatedAt": now,
    }
    if pricing["recommendation"] != "BUY_CANDIDATE":
        final_fields.update({
            "reminderStatus": "SKIPPED", "reviewStatus": "FINAL_CHECK_DONE",
            "candidateStatus": "CANCELLED",
            "skipReason": "NO_LONGER_BUY_CANDIDATE",
        })
        _update(item_id, final_fields)
        logger.info(
            "Reminder skipped: itemID=%s reason=%s",
            item_id, "NO_LONGER_BUY_CANDIDATE",
        )
        return "SKIPPED"

    if not SNS_TOPIC_ARN:
        final_fields.update({
            "reviewStatus": "FINAL_CHECK_FAILED", "reminderStatus": "FAILED",
            "reminderError": "SNS_TOPIC_ARN_MISSING",
        })
        _update(item_id, final_fields)
        return "SNS_TOPIC_ARN_MISSING"

    try:
        _email(candidate, current_price, pricing)
    except Exception as exc:
        final_fields.update({
            "reviewStatus": "FINAL_CHECK_FAILED", "reminderStatus": "FAILED",
            "reminderError": f"SNS_PUBLISH_FAILED:{exc}",
        })
        _update(item_id, final_fields)
        logger.exception("Reminder email failed: itemID=%s", item_id)
        return "SNS_PUBLISH_FAILED"
    final_fields.update({
        "reminderStatus": "SENT", "reviewStatus": "FINAL_CHECK_DONE",
        "candidateStatus": "ACTIVE", "remindedAt": now,
    })
    _update(item_id, final_fields)
    logger.info("Reminder email sent: itemID=%s", item_id)
    return "SENT"


def lambda_handler(event, context):
    event = event or {}
    if event.get("mode") == "test_email":
        try:
            result = send_test_email()
            return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False)}
        except Exception as exc:
            logger.exception("测试邮件发送失败")
            return {"statusCode": 500, "body": json.dumps({"错误": str(exc)}, ensure_ascii=False)}
    now = int(time.time())
    response = candidate_db.query(
        IndexName="GSI_FinalCheck",
        KeyConditionExpression=(
            Key("reviewStatus").eq("WAITING_FINAL_CHECK")
            & Key("finalCheckAtEpoch").lte(now)
        ),
        Limit=FINAL_CHECK_BATCH_SIZE,
    )
    outcomes = {}
    for candidate in response.get("Items", []):
        try:
            outcome = process_candidate(candidate, now)
        except Exception as exc:
            logger.exception("Final check failed for %s", candidate.get("itemID"))
            outcome = f"ERROR:{exc}"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    return {
        "statusCode": 200,
        "body": json.dumps({"processed": sum(outcomes.values()), "outcomes": outcomes}),
    }
