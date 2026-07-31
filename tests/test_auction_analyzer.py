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
    build_active_parse_prompt,
    build_closed_parse_prompt,
    calc_decision,
    normalize_pricing_key,
    pricing_key_with_condition,
    resolve_closed_without_ai,
    save_active_model,
    save_closed_model,
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

    def test_purchase_decision_uses_only_profit_rules(self):
        self.assertEqual(calc_decision(Decimal("-1"), Decimal("0.50")), Recommendation.AVOID)
        self.assertEqual(calc_decision(Decimal("1"), Decimal("0.20")), Recommendation.BUY_CANDIDATE)
        self.assertEqual(calc_decision(Decimal("1"), Decimal("0.199")), Recommendation.REVIEW)

if __name__ == "__main__":
    unittest.main()
