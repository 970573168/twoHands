import os
import sys
import unittest


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from search_engine_crawler import (
    extract_category_id, extract_links, extract_links_from_page,
    is_allowed_url, normalize_url,
)


class SearchEngineCrawlerTest(unittest.TestCase):
    def test_extracts_text_normalizes_and_deduplicates_links(self):
        html = """
        <a href="/search/search?p=camera#top"> 相机 <b>拍卖</b> </a>
        <a href="https://auctions.yahoo.co.jp/search/search?p=camera">重复</a>
        <a href="/jp/auction/x123">商品详情</a>
        """
        self.assertEqual(extract_links(html, "https://auctions.yahoo.co.jp/"), [
            {
                "url": "https://auctions.yahoo.co.jp/search/search?p=camera",
                "anchor_text": "相机 拍卖",
                "source_url": "https://auctions.yahoo.co.jp/",
            },
            {
                "url": "https://auctions.yahoo.co.jp/jp/auction/x123",
                "anchor_text": "商品详情",
                "source_url": "https://auctions.yahoo.co.jp/",
            },
        ])

    def test_filters_disallowed_external_and_unsafe_links(self):
        for path in (
            "/alert/notice", "/closeduser/a", "/members/a", "/sell/",
            "/user/name", "/config/a", "/search/advanced", "/follow/item",
        ):
            with self.subTest(path=path):
                self.assertFalse(is_allowed_url(f"https://auctions.yahoo.co.jp{path}"))
        self.assertIsNone(normalize_url("https://example.com/a", "https://auctions.yahoo.co.jp/"))
        self.assertIsNone(normalize_url("javascript:alert(1)", "https://auctions.yahoo.co.jp/"))
        self.assertTrue(is_allowed_url("https://auctions.yahoo.co.jp/jp/auction/a1"))

    def test_limit_is_applied_after_filtering(self):
        html = '<a href="/alert/a">禁用</a><a href="/a">一</a><a href="/b">二</a>'
        links = extract_links(html, "https://auctions.yahoo.co.jp/", limit=1)
        self.assertEqual([link["anchor_text"] for link in links], ["一"])

    def test_directory_link_contains_yahoo_category_id(self):
        url = "https://auctions.yahoo.co.jp/list3/2084317598-category.html"
        self.assertEqual(extract_category_id(url), "2084317598")
        links = extract_links_from_page(
            f'<a href="{url}">スマートフォン本体</a>',
            "https://auctions.yahoo.co.jp/", 2,
        )
        self.assertEqual(links[0]["category_id"], "2084317598")
        self.assertEqual(links[0]["category_name"], "スマートフォン本体")


if __name__ == "__main__":
    unittest.main()
