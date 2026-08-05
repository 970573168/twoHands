import os
import sys
import unittest
from urllib.parse import parse_qs, urlsplit


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yahoo_auction_scraper import (
    _search_context_kwargs,
    LocalListingType,
    build_contextual_exclude_keywords,
    build_url,
    parse_html,
    MERCARI_SOURCE,
    classify_listing_type_by_title,
    detect_target_context,
    get_filter_keywords,
    has_main_product_signal,
    normalize_title_for_filter,
    sanitize_search_keyword,
    should_filter_item_by_context,
    simplify_search_keyword,
)


class LocalTitleFilterTest(unittest.TestCase):
    def test_search_url_includes_crawled_category_id(self):
        url = build_url("iphone", 1, "active", category_id="2084317598")
        params = parse_qs(urlsplit(url).query)
        self.assertEqual(params["auccat"], ["2084317598"])
        self.assertEqual(params["p"], ["iphone"])


    def test_mercari_latest_category_url_uses_empty_keyword_and_source(self):
        url = build_url("", 1, "active", category_id="859", website_source=MERCARI_SOURCE)
        parsed = urlsplit(url)
        params = parse_qs(parsed.query)
        self.assertEqual(parsed.netloc, "jp.mercari.com")
        self.assertEqual(params["category_id"], ["859"])
        self.assertEqual(params["status"], ["on_sale"])
        self.assertEqual(params["sort"], ["created_time"])
        self.assertNotIn("keyword", params)

    def test_mercari_parser_extracts_regular_item_cards(self):
        html = """
        <ul><li data-testid="item-cell" data-item-id="m123">
          <a href="/item/m123"><div class="merItemThumbnail" aria-label="SONY カメラ 34,800円の画像">
            <span class="merPrice">¥34,800</span><img src="https://example.com/img.jpg" alt="SONY カメラのサムネイル"/>
          </div></a>
        </li></ul>
        """
        items = parse_html(html, "active", website_source=MERCARI_SOURCE)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["itemId"], "m123")
        self.assertEqual(items[0]["title"], "SONY カメラ")
        self.assertEqual(items[0]["price"], 34800)
        self.assertEqual(items[0]["url"], "https://jp.mercari.com/item/m123")
        self.assertEqual(items[0]["websiteSource"], MERCARI_SOURCE)

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

    def test_attached_cables_do_not_turn_main_products_into_cable_listings(self):
        titles = (
            "PlayStation 5 CFI-1200A ゲーム機本体 電源ケーブル付き",
            "PlayStation 5 CFI-1200A 本体 HDMI付き 動作確認済み",
            "Nintendo Switch 本体 LANケーブル付属 初期化確認済み",
            "PS5 CFI-2000A 本体 USB-Cケーブル コントローラーセット",
        )
        for title in titles:
            with self.subTest(title=title):
                self.assertTrue(has_main_product_signal(title))
                self.assertEqual(
                    classify_listing_type_by_title(title),
                    LocalListingType.MAIN_PRODUCT
                    if "セット" not in title else LocalListingType.BUNDLE,
                )

    def test_only_explicit_standalone_cables_are_filtered(self):
        for title in (
            "PS5 HDMIケーブルのみ",
            "Nintendo Switch 電源ケーブルのみ",
            "LAN ケーブル単体",
        ):
            with self.subTest(title=title):
                self.assertEqual(
                    classify_listing_type_by_title(title),
                    LocalListingType.USB_OR_CABLE,
                )

    def test_negative_body_wording_is_not_a_strong_keep_signal(self):
        self.assertFalse(has_main_product_signal("PlayStation 5 商品本体なし ケーブルのみ"))
        self.assertEqual(
            classify_listing_type_by_title("PlayStation 5 商品本体なし ケーブルのみ"),
            LocalListingType.USB_OR_CABLE,
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

        lens_context = detect_target_context(
            "Nikon NIKKOR Z 24-200", brand="Nikon", model="NIKKOR Z 24-200",
        )
        hood = {"title": "Nikon レンズフード HB-93"}
        self.assertEqual(should_filter_item_by_context(hood, lens_context), (
            True, "NO_CORE_MODEL_KEYWORD",
        ))

        measurement = detect_target_context("Keysight FieldFox N9935B", model="N9935B")
        for title in ("Keysight N2843A プローブ", "Keysight L4411A Multimeter"):
            item = {"title": title}
            self.assertEqual(should_filter_item_by_context(item, measurement), (
                True, "NO_CORE_MODEL_KEYWORD",
            ))
            self.assertEqual(item["localListingType"], LocalListingType.OTHER_BRAND_NOISE)

    def test_attached_accessory_wording_is_kept_for_closed_and_active(self):
        context = detect_target_context("Sony WH-1000XM5", brand="Sony", model="WH-1000XM5")
        titles = (
            "SONY WH-1000XM5 ケース付き",
            "SONY WH-1000XM5 箱付き 元箱付",
            "SONY WH-1000XM5 バッテリー付 充電器付",
            "SONY WH-1000XM5 バッテリー2個 充電器セット",
            "SONY WH-1000XM5 USBケーブル付 付属品付き",
            "SONY WH-1000XM5 ケース 箱 等 付き",
            "SONY WH-1000XM5 写真にあるものが全て",
            "SONY WH-1000XM5 本品のみ",
        )
        for search_type in ("closed", "active"):
            for title in titles:
                with self.subTest(search_type=search_type, title=title):
                    item = {"title": title}
                    self.assertEqual(
                        should_filter_item_by_context(item, context, search_type=search_type),
                        (False, "ATTACHED_ACCESSORY_KEPT"),
                    )

    def test_only_clear_accessory_only_titles_are_strong_exclusions(self):
        context = detect_target_context("Sony WH-1000XM5", model="WH-1000XM5")
        cases = (
            "WH-1000XM5 ケースのみ",
            "WH-1000XM5 バッテリーのみ",
            "WH-1000XM5 互換充電器",
            "WH-1000XM5 ケーブルのみ",
            "WH-1000XM5 イヤーパッド",
            "WH-1000XM5 部品取り",
            "WH-1000XM5 レンタル",
        )
        for title in cases:
            with self.subTest(title=title):
                filtered, reason = should_filter_item_by_context(
                    {"title": title}, context, search_type="closed",
                )
                self.assertTrue(filtered)
                self.assertTrue(reason.startswith("STRONG_EXCLUSION_"))

    def test_closed_manual_requires_only_but_active_manual_does_not(self):
        context = detect_target_context("Sony WH-1000XM5", model="WH-1000XM5")
        title = "SONY WH-1000XM5 説明書あり"
        self.assertFalse(should_filter_item_by_context(
            {"title": title}, context, search_type="closed",
        )[0])
        self.assertEqual(should_filter_item_by_context(
            {"title": title}, context, search_type="active",
        ), (True, "STRONG_EXCLUSION_MANUAL_OR_CATALOG"))

    def test_core_model_terms_reject_unrelated_titles_and_support_lens_and_alias(self):
        headphone = detect_target_context("Sony WH-1000XM5", model="WH-1000XM5")
        self.assertEqual(should_filter_item_by_context(
            {"title": "Sony INZONE H3 ケース付き"}, headphone, search_type="active",
        ), (True, "NO_CORE_MODEL_KEYWORD"))

        lens = detect_target_context(
            "NIKKOR Z 24-70mm f/2.8 S", model="NIKKOR Z 24-70mm f/2.8 S",
        )
        self.assertFalse(should_filter_item_by_context(
            {"title": "Nikon Z 24-70 F2.8 S 元箱付"}, lens, search_type="closed",
        )[0])
        self.assertTrue(should_filter_item_by_context(
            {"title": "Nikon Z 24-70 F4 S 元箱付"}, lens, search_type="closed",
        )[0])

        alias = detect_target_context(
            "Sony WH-1000XM5", model="WH-1000XM5", aliases=["XM5"],
        )
        self.assertFalse(should_filter_item_by_context(
            {"title": "SONY XM5 本体"}, alias, search_type="active",
        )[0])

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
        self.assertNotIn("バッテリー", excludes.split())
        self.assertNotIn("充電器", excludes.split())
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
