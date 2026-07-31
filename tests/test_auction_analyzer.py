import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import Mock, patch


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auction_analyzer import (
    Recommendation,
    Status,
    batch_parse,
    build_active_parse_prompt,
    build_closed_parse_prompt,
    calc_market_price,
    calc_decision,
    normalize_pricing_key,
    pricing_key_with_condition,
    resolve_closed_without_ai,
    save_active_model,
    save_closed_model,
    scrape_active,
    upsert_buy_candidate,
    update_record,
)


class NormalizePricingKeyTest(unittest.TestCase):
    def test_removes_all_separators_from_equivalent_keys(self):
        variants = (
            "NIKON NIKKOR Z 85MM F1.2 S NORMAL",
            "NIKON NIKKOR Z 85MM F/1.2 S NORMAL",
            "NIKON-NIKKOR-Z-85MM-F1.2-S-NORMAL",
        )

        normalized = {normalize_pricing_key(value) for value in variants}

        self.assertEqual(normalized, {"NIKONNIKKORZ85MMF12SNORMAL"})

    def test_applies_unicode_nfkc_before_filtering(self):
        self.assertEqual(
            normalize_pricing_key("Ｎｉｋｏｎ　８５ＭＭ　Ｆ／１．２ ™"),
            "NIKON85MMF12",
        )

    def test_removes_every_non_ascii_alphanumeric_character(self):
        self.assertEqual(normalize_pricing_key("Ab_c-d.e, (f)+® 日本語"), "ABCDEF")

    def test_condition_is_not_duplicated_on_canonical_key(self):
        self.assertEqual(
            pricing_key_with_condition("Nikon Z5 Normal", "NORMAL"),
            "NIKONZ5NORMAL",
        )


class LeanAiWorkflowTest(unittest.TestCase):
    @patch("auction_analyzer.time.time", return_value=1_000)
    @patch("auction_analyzer.buy_candidate_db")
    def test_buy_candidate_is_scheduled_without_sending_email(self, candidate_db, _time):
        candidate_db.get_item.return_value = {}
        item = {
            "title": "Nikon lens", "url": "https://example.test/item",
            "thumbnailUrl": "thumb", "keyword": "Nikon lens",
            "models": [{"brand": "Nikon", "model": "Z lens"}],
            "price": 62000, "buynowPrice": 0, "shippingFee": 1000,
            "endTime": "1970-01-01T00:33:20+00:00",
        }
        pricing = {
            "estimatedMarketPrice": 77000, "currentBidPrice": 62000,
            "netProfitAtCurrentBid": 11000,
            "profitMarginAtCurrentBid": Decimal("0.143"),
            "roiAtCurrentBid": Decimal("0.18"),
            "pricingConfidence": Decimal("0.80"), "riskLevel": "LOW", "riskScore": 2,
        }

        upsert_buy_candidate("item-1", item, pricing)

        kwargs = candidate_db.update_item.call_args.kwargs
        values = kwargs["ExpressionAttributeValues"]
        self.assertIn("firstDetectedAt = if_not_exists", kwargs["UpdateExpression"])
        self.assertIn("WAITING_FINAL_CHECK", values.values())
        self.assertIn("NOT_SENT", values.values())
        self.assertIn(1100, values.values())

    @patch("auction_analyzer.buy_candidate_db")
    def test_buy_candidate_with_invalid_end_time_is_not_scheduled(self, candidate_db):
        candidate_db.get_item.return_value = {}

        upsert_buy_candidate("item-2", {"endTime": "unknown"}, {
            "estimatedMarketPrice": 10000,
        })

        values = candidate_db.update_item.call_args.kwargs["ExpressionAttributeValues"]
        self.assertIn("INVALID_END_TIME", values.values())
        self.assertIn("NOT_SCHEDULED", values.values())

    @patch("auction_analyzer.upsert_scraped_item")
    @patch("auction_analyzer.get_record", return_value=None)
    @patch("auction_analyzer.scrape_auctions")
    def test_active_scrape_filters_current_price_by_market_upper_limit(
        self, scrape_auctions, _get_record, upsert_scraped_item
    ):
        scrape_auctions.return_value = [
            {"itemId": "invalid", "price": 0, "buynowPrice": 10},
            {"itemId": "cheap", "price": 80, "buynowPrice": 200},
            {"itemId": "limit", "price": 100},
            {"itemId": "expensive", "price": 101},
        ]

        item_ids = scrape_active("camera", 10, max_p=100)

        self.assertEqual(item_ids, ["cheap", "limit"])
        self.assertNotIn("min_price", scrape_auctions.call_args.kwargs)
        saved_ids = [call.args[1] for call in upsert_scraped_item.call_args_list]
        self.assertEqual(saved_ids, ["cheap", "limit"])

    @patch("auction_analyzer.get_record")
    def test_market_price_uses_filtered_closed_median(self, get_record):
        records = {
            "1": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 100},
            "2": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 105},
            "3": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 110},
            "4": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 115},
            "5": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 10000},
            "excluded": {"modelStatus": Status.COMPLETED, "listingType": "ACCESSORY", "price": 50},
            "pending": {"modelStatus": Status.PENDING, "listingType": "MAIN_PRODUCT", "price": 90},
        }
        get_record.side_effect = lambda _table, item_id: records[item_id]

        result = calc_market_price(list(records))

        self.assertEqual(result, {
            "market_price": 107,
            "avg_price": 107,
            "median_price": 107,
            "count": 4,
            "raw_count": 5,
        })

    @patch("auction_analyzer.get_record", return_value=None)
    def test_market_price_returns_zero_statistics_without_prices(self, _get_record):
        self.assertEqual(calc_market_price(["missing"]), {
            "market_price": 0,
            "avg_price": 0,
            "median_price": 0,
            "count": 0,
            "raw_count": 0,
        })

    def test_every_analyzer_update_refreshes_modified_order_fields(self):
        table = Mock()

        update_record(table, "a1", {"price": 100})

        values = table.update_item.call_args.kwargs["ExpressionAttributeValues"]
        self.assertEqual(values[":modifiedIndexPk"], "ALL")
        self.assertRegex(
            values[":modifiedAt"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        )

    def test_active_prompt_keeps_item_id_and_only_requests_brand_model(self):
        prompt = build_active_parse_prompt([{"itemID": "a1", "title": "Apple iPhone 15" + "x" * 200}])
        self.assertIn('"itemId":"a1"', prompt)
        self.assertIn('"models"', prompt)
        self.assertNotIn("x" * 121, prompt)
        self.assertNotIn("confidence", prompt)
        self.assertNotIn("evidence", prompt)

    def test_closed_prompt_uses_source_model_and_has_no_removed_fields(self):
        prompt = build_closed_parse_prompt([{
            "itemID": "c1",
            "title": "Apple iPhone 15 本体",
            "sourceModel": {"brand": "Apple", "model": "iPhone 15"},
        }])
        self.assertIn('"itemId":"c1"', prompt)
        self.assertIn('"sourceModel":{"brand":"Apple","model":"iPhone 15"}', prompt)
        self.assertIn('"matched":true', prompt)
        self.assertNotIn('"models"', prompt)
        self.assertEqual(prompt.count('"sourceModel"'), 1)
        for removed in ("confidence", "condition", "isComparable", "exclusionReason"):
            self.assertNotIn(removed, prompt)

    @patch("auction_analyzer.update_record")
    def test_active_storage_omits_confidence_and_evidence(self, update_record):
        save_active_model(Mock(), "a1", {
            "models": [{"brand": "Apple", "model": "iPhone 15", "confidence": 0.9, "evidence": "title"}],
        })
        fields = update_record.call_args.args[2]
        self.assertNotIn("confidence", fields["models"][0])
        self.assertNotIn("evidence", fields["models"][0])

    @patch("auction_analyzer.update_record")
    def test_closed_storage_uses_source_model_and_omits_removed_fields(self, update_record):
        table = Mock()
        save_closed_model(table, "c1", {
            "matched": True,
            "listingType": "MAIN_PRODUCT",
            "condition": "USED",
            "isComparable": True,
            "exclusionReason": "",
        }, {"sourceModel": {"brand": "Nikon", "model": "Z 85mm F1.2 S"}})
        fields = update_record.call_args.args[2]
        self.assertEqual(fields["models"][0]["brand"], "Nikon")
        self.assertEqual(fields["models"][0]["model"], "Z 85mm F1.2 S")
        for removed in ("condition", "isComparable", "exclusionReason"):
            self.assertNotIn(removed, fields)
        table.get_item.assert_not_called()

    def test_closed_title_and_model_can_be_resolved_without_ai(self):
        item = {
            "itemID": "c1",
            "title": "Bosch GBH2-26DFR ハンマードリル",
            "sourceModel": {"brand": "Bosch", "model": "GBH 2-26 DFR"},
        }
        self.assertEqual(resolve_closed_without_ai(item), {
            "itemId": "c1", "matched": True, "listingType": "MAIN_PRODUCT",
        })

    def test_uncertain_closed_model_is_left_for_ai(self):
        item = {
            "itemID": "c2",
            "title": "Bosch コードレスハンマードリル",
            "sourceModel": {"brand": "Bosch", "model": "GBH 2-26 DFR"},
        }
        self.assertIsNone(resolve_closed_without_ai(item))

    @patch("auction_analyzer.call_ai")
    @patch("auction_analyzer.check_limits")
    @patch("auction_analyzer.logger.info")
    def test_batch_parse_logs_program_and_ai_counts(self, log_info, _check_limits, call_ai):
        items = [{"itemID": str(index)} for index in range(5)]
        statuses = {
            "0": Status.COMPLETED,
            "1": Status.COMPLETED,
            "2": Status.EXCLUDED,
            "3": Status.COMPLETED,
            "4": Status.EXCLUDED,
        }

        def resolver(item):
            return {"status": statuses[item["itemID"]]} if int(item["itemID"]) < 3 else None

        def saver(_table, item_id, parsed, _item):
            return parsed.get("status", statuses[item_id])

        call_ai.return_value = ({
            "items": [
                {"itemId": "3", "status": Status.COMPLETED},
                {"itemId": "4", "status": Status.EXCLUDED},
            ],
        }, None)

        result = batch_parse(
            Mock(), items, lambda batch: "prompt", 10, 100,
            saver=saver, resolver=resolver,
        )

        log_info.assert_any_call(
            "Program resolver result: total=%s handled=%s to_ai=%s "
            "completed=%s excluded=%s review=%s failed=%s",
            5, 3, 2, 2, 1, 0, 0,
        )
        log_info.assert_any_call("AI parsing batch 1/1, size=2")
        self.assertEqual(result["parsed"], 3)
        self.assertEqual(result["excluded"], 2)

    def test_purchase_decision_uses_only_profit_rules(self):
        self.assertEqual(calc_decision(Decimal("-1"), Decimal("0.50")), Recommendation.AVOID)
        self.assertEqual(calc_decision(Decimal("1"), Decimal("0.20")), Recommendation.BUY_CANDIDATE)
        self.assertEqual(calc_decision(Decimal("1"), Decimal("0.199")), Recommendation.REVIEW)

if __name__ == "__main__":
    unittest.main()
