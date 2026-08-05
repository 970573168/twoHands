import os
import sys
import unittest
from unittest.mock import Mock, patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from token_usage import record_token_usage


class TokenUsageTest(unittest.TestCase):
    @patch("token_usage.uuid.uuid4")
    @patch("token_usage.time.time", return_value=1234)
    def test_writes_summary_with_latest_token_call(self, _time, uuid4):
        uuid4.return_value.hex = "abc"
        table = Mock()

        saved = record_token_usage(
            "gemini",
            "gemini-test",
            {"promptTokenCount": 12, "candidatesTokenCount": 8, "totalTokenCount": 20},
            prompt="测试提示",
            task_type="DISCOVER_MODELS",
            category_name="デジタルカメラ",
            table=table,
        )

        self.assertTrue(saved)
        item = table.put_item.call_args.kwargs["Item"]
        self.assertEqual(item["call_id"], "SUMMARY")
        self.assertEqual(item["record_type"], "SUMMARY")
        self.assertGreaterEqual(item["calls"], 1)
        self.assertGreaterEqual(item["input_tokens"], 12)
        self.assertGreaterEqual(item["output_tokens"], 8)
        self.assertGreaterEqual(item["total_tokens"], 20)
        self.assertEqual(item["recent_limit"], 100)
        latest = item["recent_calls"][-1]
        self.assertEqual(latest["provider"], "gemini")
        self.assertEqual(latest["model"], "gemini-test")
        self.assertEqual(latest["input_tokens"], 12)
        self.assertEqual(latest["output_tokens"], 8)
        self.assertEqual(latest["total_tokens"], 20)
        self.assertEqual(latest["task_type"], "DISCOVER_MODELS")
        self.assertEqual(latest["category_name"], "デジタルカメラ")
        self.assertTrue(latest["call_id"].endswith("#abc"))

    def test_storage_failure_does_not_break_ai_workflow(self):
        table = Mock()
        table.put_item.side_effect = RuntimeError("DynamoDB unavailable")

        self.assertFalse(record_token_usage("openai", "model", {}, table=table))

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_table_configuration_is_a_noop(self):
        self.assertFalse(record_token_usage("openai", "model", {}))
