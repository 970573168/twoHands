import os
import sys
import unittest


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auction_analyzer import normalize_pricing_key, pricing_key_with_condition


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


if __name__ == "__main__":
    unittest.main()
