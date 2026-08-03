import os
import sys
import unittest
from unittest.mock import Mock


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from search_engine_crawler import (
    count_remaining_unvisited,
    extract_category_id, extract_links, extract_links_from_page,
    get_next_unvisited_url, is_allowed_url, normalize_url,
    save_discovered_link,
)


class SearchEngineCrawlerTest(unittest.TestCase):
    def test_next_unvisited_url_continues_after_empty_filtered_page(self):
        table = Mock()
        table.query.side_effect = [
            {"Items": [], "LastEvaluatedKey": {"crawl_id": "old"}},
            {"Items": [{"url": "https://auctions.yahoo.co.jp/list3/2-category.html"}]},
        ]

        self.assertEqual(
            get_next_unvisited_url(table),
            "https://auctions.yahoo.co.jp/list3/2-category.html",
        )
        self.assertEqual(table.query.call_count, 2)
        self.assertNotIn("ExclusiveStartKey", table.query.call_args_list[0].kwargs)
        self.assertEqual(
            table.query.call_args_list[1].kwargs["ExclusiveStartKey"],
            {"crawl_id": "old"},
        )

    def test_remaining_unvisited_sums_all_query_pages(self):
        table = Mock()
        table.query.side_effect = [
            {"Count": 3, "LastEvaluatedKey": {"crawl_id": "page-2"}},
            {"Count": 4},
        ]

        self.assertEqual(count_remaining_unvisited(table), 7)
        self.assertEqual(table.query.call_count, 2)

    def test_save_discovered_link_reports_new_and_existing_items(self):
        link = {"url": "https://auctions.yahoo.co.jp/list3/1-category.html"}
        table = Mock()
        table.update_item.side_effect = [{}, {"Attributes": {"crawl_id": "existing"}}]

        self.assertTrue(save_discovered_link(table, link)["is_new"])
        self.assertFalse(save_discovered_link(table, link)["is_new"])
        self.assertEqual(
            table.update_item.call_args.kwargs["ReturnValues"], "ALL_OLD"
        )

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
