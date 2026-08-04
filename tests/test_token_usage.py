import os
import sys
import unittest
from unittest.mock import Mock, patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from token_usage import record_token_usage


class TokenUsageTest(unittest.TestCase):
    @patch("token_usage.uuid.uuid4")
    @patch("token_usage.time.time", return_value=1234)
    def test_writes_one_detailed_record_per_call(self, _time, uuid4):
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
        self.assertEqual(item["provider"], "gemini")
        self.assertEqual(item["model"], "gemini-test")
        self.assertEqual(item["input_tokens"], 12)
        self.assertEqual(item["output_tokens"], 8)
        self.assertEqual(item["total_tokens"], 20)
        self.assertEqual(item["prompt_chars"], 4)
        self.assertEqual(item["task_type"], "DISCOVER_MODELS")
        self.assertEqual(item["category_name"], "デジタルカメラ")
        self.assertTrue(item["call_id"].endswith("#abc"))

    def test_storage_failure_does_not_break_ai_workflow(self):
        table = Mock()
        table.put_item.side_effect = RuntimeError("DynamoDB unavailable")

        self.assertFalse(record_token_usage("openai", "model", {}, table=table))

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_table_configuration_is_a_noop(self):
        self.assertFalse(record_token_usage("openai", "model", {}))
