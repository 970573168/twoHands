import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import patch


os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("SNS_TOPIC_ARN", "arn:aws:sns:ap-northeast-1:123456789012:test")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from final_check_reminder import _email, calculate_final_pricing, process_candidate


class FinalCheckReminderTest(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "itemID": "item-1", "marketPrice": 100000, "shippingCost": 0,
            "endEpoch": 2000, "title": "Camera", "brand": "Nikon",
            "model": "Z", "url": "https://example.test/item",
        }

    def test_final_pricing_uses_saved_market_price(self):
        pricing = calculate_final_pricing(self.candidate, 50000)
        self.assertEqual(pricing["market"], 100000)
        self.assertEqual(pricing["recommendation"], "BUY_CANDIDATE")

    @patch("final_check_reminder.sns.publish")
    def test_reminder_can_publish_chinese_email(self, publish):
        pricing = calculate_final_pricing(self.candidate, 50000)

        _email(self.candidate, 50000, pricing)

        publish.assert_called_once()
        request = publish.call_args.kwargs
        self.assertEqual(
            request["TopicArn"],
            "arn:aws:sns:ap-northeast-1:123456789012:test",
        )
        self.assertIn("【BUY候选】结束前提醒", request["Subject"])
        self.assertIn("第二次复核已通过", request["Message"])
        self.assertIn("当前利润仍满足", request["Message"])

    @patch("final_check_reminder._email")
    @patch("final_check_reminder._update")
    @patch("final_check_reminder.scrape_active_item_current_price")
    @patch("final_check_reminder.lock_candidate", return_value=True)
    def test_sends_only_when_final_check_is_still_buy_candidate(
        self, _lock, scrape_current, update, email
    ):
        scrape_current.return_value = {"price": 50000, "endTime": "1970-01-01T00:33:20Z"}

        result = process_candidate(self.candidate, now=1000)

        self.assertEqual(result, "SENT")
        email.assert_called_once()
        final_fields = update.call_args.args[1]
        self.assertEqual(final_fields["reminderStatus"], "SENT")
        self.assertEqual(final_fields["reviewStatus"], "FINAL_CHECK_DONE")

    @patch("final_check_reminder._email")
    @patch("final_check_reminder._update")
    @patch("final_check_reminder.scrape_active_item_current_price")
    @patch("final_check_reminder.lock_candidate", return_value=True)
    def test_price_increase_cancels_without_email(
        self, _lock, scrape_current, update, email
    ):
        scrape_current.return_value = {"price": 90000, "endTime": "1970-01-01T00:33:20Z"}

        result = process_candidate(self.candidate, now=1000)

        self.assertEqual(result, "SKIPPED")
        email.assert_not_called()
        final_fields = update.call_args.args[1]
        self.assertEqual(final_fields["candidateStatus"], "CANCELLED")
        self.assertEqual(final_fields["skipReason"], "NO_LONGER_BUY_CANDIDATE")

    @patch("final_check_reminder._email")
    @patch("final_check_reminder._update")
    @patch("final_check_reminder.scrape_active_item_current_price")
    @patch("final_check_reminder.lock_candidate", return_value=False)
    def test_lock_prevents_duplicate_processing(self, _lock, scrape_current, update, email):
        self.assertEqual(process_candidate(self.candidate, now=1000), "LOCK_SKIPPED")
        scrape_current.assert_not_called()
        update.assert_not_called()
        email.assert_not_called()


if __name__ == "__main__":
    unittest.main()
