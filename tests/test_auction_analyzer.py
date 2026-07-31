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
    ListingType,
    Recommendation,
    Status,
    batch_parse,
    build_active_parse_prompt,
    build_closed_parse_prompt,
    build_description_parse_prompt,
    calc_market_price,
    calc_decision,
    execute_workflow,
    normalize_pricing_key,
    pricing_key_with_condition,
    resolve_closed_without_ai,
    price_active_item,
    save_active_model,
    save_closed_model,
    save_model,
    scrape_active,
    should_reanalyze_description,
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
    def test_buy_and_review_always_require_detail_recheck(self):
        base = {"pricingStatus": Status.COMPLETED, "netProfitAtCurrentBid": 1}
        self.assertTrue(should_reanalyze_description({}, {
            **base, "profitMarginAtCurrentBid": Decimal("0.20"),
        }))
        self.assertTrue(should_reanalyze_description({}, {
            **base, "profitMarginAtCurrentBid": Decimal("0.10"),
        }))
        self.assertFalse(should_reanalyze_description({}, {
            "pricingStatus": Status.COMPLETED,
            "netProfitAtCurrentBid": -1,
            "profitMarginAtCurrentBid": Decimal("0.50"),
        }))
        self.assertFalse(should_reanalyze_description({}, {
            **base, "pricingStatus": Status.INSUFFICIENT_DATA,
            "profitMarginAtCurrentBid": Decimal("0.30"),
        }))

    @patch("auction_analyzer.deactivate_buy_candidate")
    @patch("auction_analyzer.upsert_buy_candidate")
    @patch("auction_analyzer.save_pricing")
    @patch("auction_analyzer.build_result")
    @patch("auction_analyzer.calc_stats", return_value={})
    @patch("auction_analyzer.find_comp", return_value=([], {}))
    @patch("auction_analyzer.get_record")
    def test_initial_pricing_does_not_sync_buy_candidate(
        self, get_record, _find_comp, _calc_stats, build_result, save_pricing,
        upsert_candidate, deactivate_candidate,
    ):
        item = {
            "itemID": "a1", "modelStatus": Status.COMPLETED,
            "listingType": ListingType.MAIN_PRODUCT,
            "models": [{"brand": "Nikon", "model": "Z 85"}],
            "price": 100, "shippingFee": 0,
        }
        get_record.return_value = item
        build_result.return_value = {
            "pricingStatus": Status.COMPLETED,
            "netProfitAtCurrentBid": 100,
            "profitMarginAtCurrentBid": Decimal("0.20"),
        }

        result = price_active_item("a1", {}, sync_candidate=False)

        self.assertEqual(result, build_result.return_value)
        save_pricing.assert_called_once()
        upsert_candidate.assert_not_called()
        deactivate_candidate.assert_not_called()

    def test_detail_prompt_explicitly_excludes_missing_lens_or_body(self):
        prompt = build_description_parse_prompt([{
            "itemID": "a1",
            "title": "NIKKOR Z 85mm 元箱",
            "detailDescription": "レンズ無し。元箱とマニュアルのみです。",
        }])
        self.assertIn("レンズ無し", prompt)
        self.assertIn("本体は含まれません", prompt)
        self.assertIn("listingType は BOX_ONLY または ACCESSORY", prompt)

    @patch("auction_analyzer.update_record")
    def test_detail_reanalysis_excludes_box_only_from_pricing(self, update_record):
        status = save_model(Mock(), "a1", {
            "brand": "Nikon", "model": "NIKKOR Z 85mm f/1.2 S",
            "listingType": ListingType.BOX_ONLY,
        })
        fields = update_record.call_args.args[2]
        self.assertEqual(status, Status.EXCLUDED)
        self.assertEqual(fields["modelStatus"], Status.EXCLUDED)
        self.assertEqual(fields["pricingStatus"], Status.NOT_APPLICABLE)
        self.assertFalse(fields["isAnalysisEligible"])

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

        source_model = {"brand": "Sony", "model": "PlayStation 5"}
        item_ids = scrape_active("camera", 10, max_p=100, source_model=source_model)

        self.assertEqual(item_ids, ["cheap", "limit"])
        self.assertNotIn("min_price", scrape_auctions.call_args.kwargs)
        saved_ids = [call.args[1] for call in upsert_scraped_item.call_args_list]
        self.assertEqual(saved_ids, ["cheap", "limit"])
        for call in upsert_scraped_item.call_args_list:
            self.assertEqual(call.args[2]["sourceModel"], source_model)
            # A record without a previous sourceModel must be reset so that an
            # old model result can never be reused for this target.
            self.assertTrue(call.kwargs["force"])

    @patch("auction_analyzer.get_record")
    def test_market_price_uses_filtered_closed_median(self, get_record):
        records = {
            "1": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 100},
            "2": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 105},
            "3": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 110},
            "4": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 115},
            "excluded": {"modelStatus": Status.COMPLETED, "listingType": "ACCESSORY", "price": 50},
            "pending": {"modelStatus": Status.PENDING, "listingType": "MAIN_PRODUCT", "price": 90},
        }
        get_record.side_effect = lambda _table, item_id: records[item_id]

        result = calc_market_price(list(records))

        self.assertEqual(result["market_price"], 107)
        self.assertEqual(result["avg_price"], 107)
        self.assertEqual(result["median_price"], 107)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["raw_count"], 4)
        self.assertFalse(result["market_price_suspicious"])
        self.assertFalse(result["price_filter"]["low_price_cluster_removed"])

    @patch("auction_analyzer.get_record")
    def test_market_price_removes_low_price_accessory_cluster(self, get_record):
        prices = [980, 1500, 2500, 3980, 4980, 6800, 8900, 98000, 110000, 125000]
        records = {
            str(index): {
                "itemID": str(index),
                "title": f"closed item {index}",
                "modelStatus": Status.COMPLETED,
                "listingType": ListingType.MAIN_PRODUCT,
                "price": price,
            }
            for index, price in enumerate(prices)
        }
        get_record.side_effect = lambda _table, item_id: records[item_id]

        result = calc_market_price(list(records))

        self.assertEqual(result["market_price"], 110000)
        self.assertEqual(result["avg_price"], 111000)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["raw_count"], 10)
        self.assertFalse(result["market_price_suspicious"])
        self.assertEqual(result["price_filter"], {
            "low_price_cluster_removed": True,
            "removed_low_price_count": 7,
            "max_gap_ratio": "11.011",
            "split_low_max": 8900,
            "split_high_min": 98000,
        })

    @patch("auction_analyzer.get_record")
    def test_market_price_is_suspicious_when_high_cluster_is_too_small(self, get_record):
        records = {
            "1": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 100},
            "2": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 105},
            "3": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 110},
            "4": {"modelStatus": Status.COMPLETED, "listingType": "MAIN_PRODUCT", "price": 10000},
        }
        get_record.side_effect = lambda _table, item_id: records[item_id]

        result = calc_market_price(list(records))

        self.assertTrue(result["market_price_suspicious"])
        self.assertEqual(result["market_price"], 0)
        self.assertEqual(result["raw_count"], 4)

    @patch("auction_analyzer.get_record")
    def test_market_price_is_suspicious_without_a_usable_gap(self, get_record):
        prices = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        get_record.side_effect = lambda _table, item_id: {
            "modelStatus": Status.COMPLETED,
            "listingType": ListingType.MAIN_PRODUCT,
            "price": prices[int(item_id)],
        }

        result = calc_market_price([str(index) for index in range(len(prices))])

        self.assertTrue(result["market_price_suspicious"])
        self.assertEqual(result["price_filter"]["max_gap_ratio"], "2.000")

    @patch("auction_analyzer.scrape_active")
    @patch("auction_analyzer.calc_market_price")
    @patch("auction_analyzer.get_record")
    @patch("auction_analyzer.scrape_closed", return_value=["c1"])
    @patch("auction_analyzer.check_limits")
    def test_workflow_skips_active_when_market_price_is_suspicious(
        self, _check_limits, _scrape_closed, get_record, calc_market_price, scrape_active
    ):
        get_record.return_value = {"itemID": "c1", "modelStatus": Status.COMPLETED}
        calc_market_price.return_value = {
            "market_price": 0,
            "market_price_suspicious": True,
            "raw_count": 4,
            "price_filter": {"low_price_cluster_removed": False},
        }

        result = execute_workflow("Nikon Z 7II", 10, 10, False, {
            "brand": "Nikon", "model": "Z 7II",
        })

        self.assertEqual(result["status"], "MARKET_PRICE_SUSPICIOUS")
        self.assertTrue(result["market_price_suspicious"])
        scrape_active.assert_not_called()

    @patch("auction_analyzer.get_record", return_value=None)
    def test_market_price_returns_zero_statistics_without_prices(self, _get_record):
        result = calc_market_price(["missing"])
        self.assertEqual(result["market_price"], 0)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["raw_count"], 0)
        self.assertFalse(result["market_price_suspicious"])

    def test_every_analyzer_update_refreshes_modified_order_fields(self):
        table = Mock()

        update_record(table, "a1", {"price": 100})

        values = table.update_item.call_args.kwargs["ExpressionAttributeValues"]
        self.assertEqual(values[":modifiedIndexPk"], "ALL")
        self.assertRegex(
            values[":modifiedAt"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        )

    def test_active_prompt_compares_title_with_source_model(self):
        prompt = build_active_parse_prompt([{
            "itemID": "a1",
            "title": "Sony INZONE H3" + "x" * 200,
            "sourceModel": {"brand": "Sony", "model": "PlayStation 5"},
        }])
        self.assertIn('"itemId":"a1"', prompt)
        self.assertIn('"sourceModel":{"brand":"Sony","model":"PlayStation 5"}', prompt)
        self.assertIn('"matched":true', prompt)
        self.assertIn('"listingType":"MAIN_PRODUCT"', prompt)
        self.assertIn("違う商品本体", prompt)
        self.assertIn("レンタルはRENTAL", prompt)
        self.assertNotIn("x" * 121, prompt)
        self.assertEqual(prompt.count('"sourceModel"'), 1)
        for forbidden in (
            "confidence", "evidence", "reason", "exclusionReason", "condition",
            "conditionClass", "riskFactors",
        ):
            self.assertNotIn(forbidden, prompt)

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
        for removed in (
            "confidence", "evidence", "reason", "condition", "conditionClass",
            "isComparable", "exclusionReason", "riskFactors",
        ):
            self.assertNotIn(removed, prompt)

    @patch("auction_analyzer.update_record")
    def test_active_storage_omits_confidence_and_evidence(self, update_record):
        save_active_model(Mock(), "a1", {
            "models": [{"brand": "Apple", "model": "iPhone 15", "confidence": 0.9, "evidence": "title"}],
            "listingType": "MAIN_PRODUCT",
        })
        fields = update_record.call_args.args[2]
        self.assertNotIn("confidence", fields["models"][0])
        self.assertNotIn("evidence", fields["models"][0])

    @patch("auction_analyzer.update_record")
    def test_active_non_products_are_excluded_from_pricing(self, update_record):
        cases = (
            ("【2日間から~レンタル】Nikon NIKKOR Z 24-200mm f/4-6.3 VR", "RENTAL"),
            ("【往復送料無料】NIKKOR Z 24-200mm レンタル", "RENTAL"),
            ("G061b【中古美品 元箱のみ】Nikon NIKKOR Z 24-200mm レンズ用元箱", "BOX_ONLY"),
            ("Nikon バヨネットフード HB-93 NIKKOR Z 24-200mm用", "ACCESSORY"),
        )
        for index, (title, listing_type) in enumerate(cases):
            with self.subTest(title=title):
                status = save_active_model(Mock(), str(index), {
                    "models": [], "listingType": listing_type,
                }, {"title": title})
                fields = update_record.call_args.args[2]
                self.assertEqual(status, Status.EXCLUDED)
                self.assertEqual(fields["listingType"], listing_type)
                self.assertEqual(fields["modelStatus"], Status.EXCLUDED)
                self.assertEqual(fields["pricingStatus"], Status.NOT_APPLICABLE)
                self.assertFalse(fields["isAnalysisEligible"])

    @patch("auction_analyzer.update_record")
    def test_active_main_product_is_eligible_for_pricing(self, update_record):
        status = save_active_model(Mock(), "main", {
            "models": [{"brand": "Nikon", "model": "NIKKOR Z 24-200mm f/4-6.3 VR"}],
            "listingType": ListingType.MAIN_PRODUCT,
        }, {"title": "ニコン NIKKOR Z 24-200mm f/4-6.3 VR"})

        fields = update_record.call_args.args[2]
        self.assertEqual(status, Status.COMPLETED)
        self.assertEqual(fields["pricingStatus"], Status.PENDING)
        self.assertTrue(fields["isAnalysisEligible"])

    @patch("auction_analyzer.update_record")
    def test_active_different_main_product_is_excluded_from_pricing(self, update_record):
        source_model = {"brand": "Sony", "model": "PlayStation 5"}
        status = save_active_model(Mock(), "different", {
            "matched": False,
            "listingType": ListingType.MAIN_PRODUCT,
        }, {
            "title": "Sony INZONE H3",
            "sourceModel": source_model,
        })

        fields = update_record.call_args.args[2]
        self.assertEqual(status, Status.EXCLUDED)
        self.assertEqual(fields["models"], [])
        self.assertEqual(fields["listingType"], ListingType.MAIN_PRODUCT)
        self.assertEqual(fields["pricingStatus"], Status.NOT_APPLICABLE)
        self.assertFalse(fields["isAnalysisEligible"])

    @patch("auction_analyzer.update_record")
    def test_active_matched_product_uses_source_model_for_pricing(self, update_record):
        source_model = {"brand": "Sony", "model": "PlayStation 5"}
        status = save_active_model(Mock(), "matched", {
            "matched": True,
            "listingType": ListingType.MAIN_PRODUCT,
        }, {"sourceModel": source_model})

        fields = update_record.call_args.args[2]
        self.assertEqual(status, Status.COMPLETED)
        self.assertEqual(fields["models"][0]["brand"], "Sony")
        self.assertEqual(fields["models"][0]["model"], "PlayStation 5")
        self.assertTrue(fields["isAnalysisEligible"])

    @patch("auction_analyzer.update_record")
    def test_active_invalid_listing_type_is_unknown_and_not_eligible(self, update_record):
        status = save_active_model(Mock(), "unknown", {
            "models": [{"brand": "Nikon", "model": "Z"}],
            "listingType": "INVALID",
        })

        fields = update_record.call_args.args[2]
        self.assertEqual(status, Status.REVIEW_REQUIRED)
        self.assertEqual(fields["listingType"], ListingType.UNKNOWN)
        self.assertEqual(fields["pricingStatus"], Status.NOT_APPLICABLE)
        self.assertFalse(fields["isAnalysisEligible"])

    def test_closed_resolver_excludes_rental_box_and_accessory_titles(self):
        source_model = {"brand": "Nikon", "model": "NIKKOR Z 24-200mm F4-6.3 VR"}
        cases = (
            ("【2日間から~レンタル】Nikon NIKKOR Z 24-200mm F4-6.3 VR", "RENTAL"),
            ("中古美品 元箱のみ NIKKOR Z 24-200mm F4-6.3 VR", "BOX_ONLY"),
            ("バヨネットフード HB-93 NIKKOR Z 24-200mm F4-6.3 VR用", "ACCESSORY"),
        )
        for index, (title, listing_type) in enumerate(cases):
            with self.subTest(title=title):
                self.assertEqual(resolve_closed_without_ai({
                    "itemID": str(index), "title": title, "sourceModel": source_model,
                }), {
                    "itemId": str(index), "matched": True, "listingType": listing_type,
                })

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
