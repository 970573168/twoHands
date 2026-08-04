import importlib
import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

with patch("boto3.resource"), patch("boto3.client"):
    catalog_scanner = importlib.import_module("catalog_scanner")


class CatalogScannerTest(unittest.TestCase):
    def setUp(self):
        self.table = Mock()
        self.lambda_client = Mock()
        self.table_patch = patch.object(catalog_scanner, "table", self.table)
        self.lambda_patch = patch.object(catalog_scanner, "lambda_client", self.lambda_client)
        self.table_patch.start()
        self.lambda_patch.start()
        self.addCleanup(self.table_patch.stop)
        self.addCleanup(self.lambda_patch.stop)

    def test_configure_mode_updates_four_catalog_fields(self):
        self.table.scan.return_value = {"Items": [{"crawl_id": "link-1"}]}
        result = catalog_scanner.configure_catalog({
            "category_id": "2084317598", "active_count": 30,
            "closed_count": 80, "scan_interval_minutes": 15,
            "scan_enabled": True,
        }, now=1000)

        self.assertEqual(result["状态"], "配置已更新")
        values = self.table.update_item.call_args.kwargs["ExpressionAttributeValues"]
        self.assertEqual(values[":active"], 30)
        self.assertEqual(values[":closed"], 80)
        self.assertEqual(values[":interval"], 15)
        self.assertIs(values[":enabled"], True)
        self.assertEqual(values[":next"], 1000)
        self.assertEqual(self.table.update_item.call_args.kwargs["Key"], {"crawl_id": "link-1"})

    def test_schedule_only_finds_enabled_due_catalogs(self):
        self.table.scan.return_value = {"Items": [], "ScannedCount": 0}
        catalog_scanner.find_due_catalogs(2000)
        kwargs = self.table.scan.call_args.kwargs
        self.assertIn("link_type = :directory", kwargs["FilterExpression"])
        self.assertIn("countdown_scan_enabled = :enabled", kwargs["FilterExpression"])
        self.assertIn("countdown_next_scan_at <= :now", kwargs["FilterExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":now"], 2000)

    def test_claim_uses_atomic_time_and_lock_guards(self):
        item = {"crawl_id": "link-1", "countdown_interval_minutes": 15}
        self.assertTrue(catalog_scanner.claim_catalog(item, 1000))
        kwargs = self.table.update_item.call_args.kwargs
        self.assertIn("countdown_next_scan_at <= :now", kwargs["ConditionExpression"])
        self.assertIn("countdown_scan_lock_until < :now", kwargs["ConditionExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":next"], 1900)

    def test_dispatch_uses_catalog_counts_and_countdown_mode(self):
        self.lambda_client.invoke.return_value = {"StatusCode": 202}
        item = {
            "crawl_id": "link-1", "category_id": "1", "countdown_active_count": 30,
            "countdown_closed_count": 80,
        }
        self.assertTrue(catalog_scanner.dispatch_to_analyzer(item))
        payload = json.loads(self.lambda_client.invoke.call_args.kwargs["Payload"])
        self.assertEqual(payload["mode"], "countdown")
        self.assertNotIn("keyword", payload)
        self.assertEqual(payload["category_id"], "1")
        self.assertEqual(payload["active_count"], 30)
        self.assertEqual(payload["closed_count"], 80)

    def test_dispatch_failure_releases_lock_and_retries_next_minute(self):
        catalog_scanner.mark_dispatch_failed("link-1", 1000)
        kwargs = self.table.update_item.call_args.kwargs
        self.assertIn("REMOVE countdown_scan_lock_until", kwargs["UpdateExpression"])
        self.assertEqual(kwargs["ExpressionAttributeValues"][":retry"], 1060)
        self.assertEqual(kwargs["ExpressionAttributeValues"][":failed"], "DISPATCH_FAILED")

    def test_lambda_rejects_unknown_mode_in_chinese(self):
        response = catalog_scanner.lambda_handler({"mode": "unknown"}, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("只支持", json.loads(response["body"])["错误"])


if __name__ == "__main__":
    unittest.main()
