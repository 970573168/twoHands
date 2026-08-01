import importlib
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


class CatalogScannerCycleTest(unittest.TestCase):
    def setUp(self):
        self.table = Mock()
        self.table.scan.return_value = {
            "Items": [],
            "ScannedCount": 0,
        }
        self.table_patch = patch.object(catalog_scanner, "table", self.table)
        self.table_patch.start()
        self.addCleanup(self.table_patch.stop)

    @staticmethod
    def product(pk, last_scanned_date=None, status="COMPLETED"):
        item = {
            "PK": pk,
            "category": "カメラ",
            "brand": "Sony",
            "model": pk,
            "entity_type": "PRODUCT",
            "status": "ACTIVE",
            "last_analysis_status": status,
            "modified_at": "2026-07-31T00:00:00+00:00",
        }
        if last_scanned_date is not None:
            item["last_scanned_date"] = last_scanned_date
        return item

    def test_prioritizes_never_scanned_then_oldest_due_product(self):
        self.table.scan.return_value = {
            "Items": [
                self.product("four-days", "2026-07-28"),
                self.product("never"),
                self.product("three-days", "2026-07-29"),
                self.product("ten-days", "2026-07-22"),
                self.product("recent", "2026-07-30"),
            ],
            "ScannedCount": 5,
        }

        products = catalog_scanner.scan_unanalyzed_products("2026-08-01", 10)

        self.assertEqual(
            [product["product_pk"] for product in products],
            ["never", "ten-days", "four-days", "three-days"],
        )

    def test_skips_queued_products_even_when_due(self):
        self.table.scan.return_value = {
            "Items": [self.product("queued", "2026-01-01", "QUEUED")],
            "ScannedCount": 1,
        }

        self.assertEqual(
            catalog_scanner.scan_unanalyzed_products("2026-08-01", 10),
            [],
        )

    def test_queue_update_guards_the_three_day_cycle(self):
        self.table.update_item.return_value = {}

        self.assertTrue(catalog_scanner.mark_as_queued("model", "2026-08-01"))

        kwargs = self.table.update_item.call_args.kwargs
        self.assertIn("last_scanned_date <= :cutoff_date", kwargs["ConditionExpression"])
        self.assertEqual(
            kwargs["ExpressionAttributeValues"][":cutoff_date"],
            "2026-07-29",
        )

    @patch.object(catalog_scanner, "get_today_date", return_value="2026-08-01")
    def test_stops_immediately_when_no_product_reached_three_days(self, _today):
        self.table.scan.return_value = {
            "Items": [self.product("recent", "2026-07-30")],
            "ScannedCount": 1,
        }

        result = catalog_scanner.scan_and_dispatch({})

        self.assertEqual(result["status"], "NO_PRODUCTS_TO_SCAN")
        self.assertEqual(result["dispatched"], 0)
        self.assertIn("已停止", result["message"])


if __name__ == "__main__":
    unittest.main()
