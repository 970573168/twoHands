import os
import sys
import unittest
from unittest.mock import Mock
from unittest.mock import patch

from botocore.exceptions import ClientError


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from search_engine_crawler import (
    claim_queue_item, count_queue_status, enqueue_discovered_link,
    get_queued_items, lambda_handler, mark_queue_done, mark_queue_failed,
    count_remaining_unvisited,
    extract_category_id, extract_links, extract_links_from_page,
    get_next_unvisited_url, is_allowed_url, normalize_url,
    save_discovered_link, website_source_from_url,
)


class SearchEngineCrawlerTest(unittest.TestCase):
    def test_enqueue_discovered_link_creates_queued_item(self):
        table = Mock()
        table.update_item.return_value = {}
        result = enqueue_discovered_link(table, {
            "url": "https://auctions.yahoo.co.jp/list3/1-category.html",
            "depth": 1,
            "source_url": "https://auctions.yahoo.co.jp/list3/root-category.html",
        }, "https://auctions.yahoo.co.jp/list3/root-category.html")

        self.assertTrue(result["is_new"])
        kwargs = table.update_item.call_args.kwargs
        self.assertEqual(kwargs["ReturnValues"], "ALL_OLD")
        self.assertIn("queue_status", kwargs["UpdateExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":queued"], "QUEUED")

    def test_enqueue_discovered_link_reports_existing_item(self):
        table = Mock()
        table.update_item.return_value = {"Attributes": {"queue_status": "DONE"}}
        result = enqueue_discovered_link(table, {
            "url": "https://auctions.yahoo.co.jp/list3/1-category.html"
        }, "https://auctions.yahoo.co.jp/list3/1-category.html")
        self.assertFalse(result["is_new"])
        self.assertEqual(result["previous_status"], "DONE")

    def test_get_queued_items_uses_queue_index_and_paginates(self):
        table = Mock()
        table.query.side_effect = [
            {"Items": [{"crawl_id": "one"}], "LastEvaluatedKey": {"crawl_id": "one"}},
            {"Items": [{"crawl_id": "two"}]},
        ]
        self.assertEqual(len(get_queued_items(table, 3)), 2)
        first, second = table.query.call_args_list
        self.assertEqual(first.kwargs["IndexName"], "queue_status-queue_priority-index")
        self.assertTrue(first.kwargs["ScanIndexForward"])
        self.assertEqual(second.kwargs["ExclusiveStartKey"], {"crawl_id": "one"})

    def test_claim_queue_item_moves_queued_to_processing(self):
        table = Mock()
        table.update_item.return_value = {"Attributes": {"queue_status": "PROCESSING"}}
        self.assertEqual(claim_queue_item(table, "id")["queue_status"], "PROCESSING")
        kwargs = table.update_item.call_args.kwargs
        self.assertEqual(kwargs["ConditionExpression"], "queue_status = :queued")
        self.assertIn("ADD attempt_count :one", kwargs["UpdateExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":processing"], "PROCESSING")
        self.assertEqual(kwargs["ReturnValues"], "ALL_NEW")

    def test_claim_queue_item_returns_none_when_already_claimed(self):
        table = Mock()
        table.update_item.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException", "Message": "claimed"}},
            "UpdateItem",
        )
        self.assertIsNone(claim_queue_item(table, "id"))

    def test_mark_queue_done_requires_processing(self):
        table = Mock()
        table.update_item.return_value = {}
        mark_queue_done(table, "id", 4, 2, False)
        kwargs = table.update_item.call_args.kwargs
        self.assertEqual(kwargs["ConditionExpression"], "queue_status = :processing")
        for text in ("queue_status", "child_count", "new_child_count", "is_terminal",
                     "REMOVE last_error"):
            self.assertIn(text, kwargs["UpdateExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":done"], "DONE")

    def test_mark_queue_failed_requeues_before_max_attempts(self):
        table = Mock()
        table.update_item.return_value = {}
        mark_queue_failed(table, {"crawl_id": "id", "attempt_count": 2}, "temporary")
        kwargs = table.update_item.call_args.kwargs
        self.assertEqual(kwargs["ExpressionAttributeValues"][":status"], "QUEUED")
        self.assertEqual(kwargs["ConditionExpression"], "queue_status = :processing")

    def test_mark_queue_failed_errors_after_max_attempts(self):
        table = Mock()
        table.update_item.return_value = {}
        mark_queue_failed(table, {"crawl_id": "id", "attempt_count": 3}, "permanent")
        self.assertEqual(
            table.update_item.call_args.kwargs["ExpressionAttributeValues"][":status"],
            "ERROR",
        )

    def test_count_queue_status_sums_all_pages(self):
        table = Mock()
        table.query.side_effect = [
            {"Count": 2, "LastEvaluatedKey": {"crawl_id": "next"}}, {"Count": 5}
        ]
        self.assertEqual(count_queue_status(table, "DONE"), 7)
        self.assertEqual(table.query.call_count, 2)

    @patch("search_engine_crawler.count_queue_status", return_value=0)
    @patch("search_engine_crawler.crawl_queue", return_value={"pages_crawled": 0})
    @patch("search_engine_crawler.seed_from_homepage", return_value=2)
    @patch("search_engine_crawler.has_queued_items", return_value=False)
    @patch("search_engine_crawler.recover_stale_processing_items", return_value=0)
    @patch("search_engine_crawler.boto3.resource")
    @patch("search_engine_crawler.get_next_unvisited_url")
    def test_lambda_no_longer_initializes_single_start_url_queue(
        self, old_start, resource, recover, has_items, seed, crawl, count
    ):
        with patch.dict(os.environ, {"LINK_CRAWLER_TABLE_NAME": "links"}):
            result = lambda_handler({}, None)
        old_start.assert_not_called()
        seed.assert_called_once_with(resource.return_value.Table.return_value)
        crawl.assert_called_once()
        self.assertNotIn("start_url", result)
        self.assertEqual(result["seeded"], 2)

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


    def test_extracts_mercari_category_links_with_site_source(self):
        html = """
        <div class="merListItem"><a href="/categories?category_id=3088">ファッション</a></div>
        <div class="merListItem"><a href="https://jp.mercari.com/categories?category_id=5&foo=bar">本・雑誌・漫画</a></div>
        """

        links = extract_links_from_page(html, "https://jp.mercari.com/categories", 0)

        self.assertEqual(links[0]["url"], "https://jp.mercari.com/categories?category_id=3088")
        self.assertEqual(links[0]["category_id"], "3088")
        self.assertEqual(links[0]["category_name"], "ファッション")
        self.assertEqual(links[0]["website_source"], "MERCARI")
        self.assertEqual(links[0]["source"], "MERCARI")
        self.assertEqual(links[0]["link_type"], "mercari_directory")
        self.assertEqual(links[1]["url"], "https://jp.mercari.com/categories?category_id=5")

    def test_enqueue_discovered_link_persists_website_source(self):
        table = Mock()
        table.update_item.return_value = {}
        enqueue_discovered_link(table, {
            "url": "https://jp.mercari.com/categories?category_id=3088",
            "category_name": "ファッション",
            "anchor_text": "ファッション",
            "website_source": "MERCARI",
            "link_type": "mercari_directory",
        }, "https://jp.mercari.com/categories?category_id=3088")

        kwargs = table.update_item.call_args.kwargs
        self.assertIn("website_source", kwargs["UpdateExpression"])
        self.assertIn("#source", kwargs["UpdateExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":website_source"], "MERCARI")
        self.assertEqual(kwargs["ExpressionAttributeValues"][":link_type"], "mercari_directory")
        self.assertEqual(website_source_from_url("https://jp.mercari.com/categories"), "MERCARI")

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
