import os
import sys
import unittest


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yahoo_auction_scraper import (
    _search_context_kwargs,
    LocalListingType,
    build_contextual_exclude_keywords,
    classify_listing_type_by_title,
    detect_target_context,
    get_filter_keywords,
    normalize_title_for_filter,
    sanitize_search_keyword,
    should_filter_item_by_context,
    simplify_search_keyword,
)


class LocalTitleFilterTest(unittest.TestCase):
    def test_clear_main_products_remain_main_products(self):
        titles = (
            "Panasonic LUMIX H-X025 LEICA DG SUMMILUX 25mm F1.4 ASPH レンズ",
            "SONY SEL2470GM2 FE 24-70mm F2.8 GM II",
            "FUJIFILM XF 16-55mm F2.8 R LM WR",
            "KEYSIGHT B2901A Precision Source/Measure Unit",
            "MITSUBISHI ELECTRIC GT2512-STBA 表示器",
            "Makita BL1830B 純正 バッテリー",
        )
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(
                    classify_listing_type_by_title(title),
                    LocalListingType.MAIN_PRODUCT,
                )

    def test_noise_titles_are_classified_before_bundle_words(self):
        cases = {
            "iPhone8送料無料 バッテリー 交換 セット 修理 電池": LocalListingType.BATTERY_OR_CHARGER,
            "G061a 元箱のみ Nikon NIKKOR Z 24-200mm レンズ用元箱": LocalListingType.BOX_ONLY,
            "NP-FZ100 互換バッテリー + 互換充電器": LocalListingType.BATTERY_OR_CHARGER,
            "COMMERCIAL PHOTO コマーシャル・フォト": LocalListingType.MANUAL_OR_CATALOG,
            "SmallRig L型ブラケット": LocalListingType.ACCESSORY,
            "SONY 保護フィルム OverLay": LocalListingType.CASE_OR_FILM,
            "SONY アイピースカップ": LocalListingType.ACCESSORY,
            "iPhone XR ケース 手帳型": LocalListingType.CASE_OR_FILM,
            "Apple iPhone 空箱 8個セット": LocalListingType.BOX_ONLY,
            "Leica レンズキャップ": LocalListingType.ACCESSORY,
            "Leica マウントアダプター": LocalListingType.ADAPTER_OR_MOUNT,
            "Pioneer リモコン": LocalListingType.REMOTE_ONLY,
            "Pioneer カーオーディオ": LocalListingType.CAR_AUDIO_OR_CARPLAY,
            "KEIYO CarPlay": LocalListingType.CAR_AUDIO_OR_CARPLAY,
            "iPhone用 USBメモリ": LocalListingType.USB_OR_CABLE,
            "バッグ / カーディガン / ペンケース": LocalListingType.CLOTHING_OR_BAG,
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(classify_listing_type_by_title(title), expected)

    def test_specific_noise_rule_wins_over_later_clothing_or_bundle_word(self):
        self.assertEqual(
            classify_listing_type_by_title("保護フィルム 2個セット"),
            LocalListingType.CASE_OR_FILM,
        )

    def test_context_keeps_target_battery_and_adapter(self):
        battery_context = detect_target_context("Makita BL1860B", model="BL1860B")
        battery = {"title": "Makita BL1860B 互換バッテリー"}
        self.assertEqual(should_filter_item_by_context(battery, battery_context), (
            False, "TARGET_BATTERY_OR_CHARGER",
        ))

        adapter_context = detect_target_context("Leica Mマウントアダプター")
        adapter = {"title": "Leica Mマウントアダプター"}
        self.assertEqual(should_filter_item_by_context(adapter, adapter_context), (False, ""))

    def test_context_filters_battery_accessory_and_other_measurement_models(self):
        camera_context = detect_target_context("Sony α7R IV", brand="Sony", model="α7R IV")
        battery = {"title": "NP-FZ100 互換バッテリー + 互換充電器"}
        self.assertTrue(should_filter_item_by_context(battery, camera_context)[0])

        lens_context = detect_target_context("Nikon NIKKOR Z 24-200")
        hood = {"title": "Nikon レンズフード HB-93"}
        self.assertEqual(should_filter_item_by_context(hood, lens_context), (
            True, "ACCESSORY_NOT_MAIN_PRODUCT",
        ))

        measurement = detect_target_context("Keysight FieldFox N9935B", model="N9935B")
        for title in ("Keysight N2843A プローブ", "Keysight L4411A Multimeter"):
            item = {"title": title}
            self.assertEqual(should_filter_item_by_context(item, measurement), (
                True, "DIFFERENT_MEASUREMENT_MODEL",
            ))
            self.assertEqual(item["localListingType"], LocalListingType.OTHER_BRAND_NOISE)

    def test_bundle_is_kept_by_default_and_removed_in_strict_mode(self):
        item = {"title": "Makita 工具本体 バッテリー 充電器 セット"}
        context = detect_target_context("Makita 工具")
        self.assertFalse(should_filter_item_by_context(item, context)[0])
        self.assertEqual(item["localListingType"], LocalListingType.BUNDLE)

        bundle = {"title": "Nikon カメラ 2台セット"}
        self.assertEqual(should_filter_item_by_context(bundle, {}, strict=True), (
            True, "BUNDLE_STRICT",
        ))

    def test_contextual_url_excludes_do_not_kill_battery_target(self):
        excludes = build_contextual_exclude_keywords({
            "keyword": "Makita BL1860B バッテリー", "model": "BL1860B",
        })
        self.assertNotIn("バッテリー", excludes)
        self.assertNotIn("充電器", excludes)
        self.assertIn("空箱", excludes)

    def test_explicit_empty_url_excludes_are_respected(self):
        excludes, includes = get_filter_keywords({
            "keyword": "Sony α7R IV",
            "exclude_keywords": "",
        })
        self.assertEqual(excludes, "")
        self.assertEqual(includes, "")

    def test_source_model_accepts_object_and_string_event_shapes(self):
        self.assertEqual(
            _search_context_kwargs({"sourceModel": {"brand": "Sony", "model": "α7R IV"}})["model"],
            "α7R IV",
        )
        self.assertEqual(
            _search_context_kwargs({"sourceModel": "N9935B"})["model"],
            "N9935B",
        )

    def test_keyword_normalization_and_simplification_keep_model(self):
        self.assertEqual(normalize_title_for_filter("  ｉＰｈｏｎｅ　XR  "), "IPHONE XR")
        self.assertEqual(sanitize_search_keyword("Nikon Z 85mm f/1.2 S"), "Nikon Z 85mm f 1.2 S")
        self.assertEqual(
            simplify_search_keyword("Keysight Technologies FieldFox Handheld RF Analyzer N9935B"),
            "Keysight N9935B",
        )


if __name__ == "__main__":
    unittest.main()
