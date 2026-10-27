import os
import subprocess
import unittest
from unittest.mock import patch

from app import hermes_writer


class HermesWriterTests(unittest.TestCase):
    def test_passes_editorial_context_to_hermes_stdin(self):
        settings = {"REUP_LLM_MODEL": "test-model", "REUP_LLM_API_KEY": "test-only"}
        output = subprocess.CompletedProcess([], 0, "💡 Bài nháp\n\n#AI #Tech", "")
        with patch.dict(os.environ, settings), \
             patch("app.hermes_writer.hermes_executable", return_value="hermes"), \
             patch("app.hermes_writer.subprocess.run", return_value=output) as run:
            draft = hermes_writer.write_with_hermes("Tiêu đề: Test\nNguồn: https://example.com")
        self.assertIn("💡", draft)
        command = run.call_args.args[0]
        self.assertEqual(command[:2], ["hermes", "chat"])
        self.assertIn("--query-file", command)
        self.assertEqual(command[command.index("--toolsets") + 1], "bot_room")
        self.assertIn("-", command)
        prompt = run.call_args.kwargs["input"]
        self.assertIn("Tiêu đề: Test", prompt)
        self.assertIn("ít nhất một emoji/icon", prompt)
        self.assertNotIn("test-only", prompt)
        self.assertNotIn("test-only", command)

    def test_does_not_fall_back_when_hermes_fails(self):
        settings = {"REUP_LLM_MODEL": "test-model", "REUP_LLM_API_KEY": "test-only"}
        failed = subprocess.CompletedProcess([], 1, "", "details")
        with patch.dict(os.environ, settings), \
             patch("app.hermes_writer.hermes_executable", return_value="hermes"), \
             patch("app.hermes_writer.subprocess.run", return_value=failed):
            with self.assertRaisesRegex(ValueError, "Hermes không tạo"):
                hermes_writer.write_with_hermes("Tiêu đề: Test")

    def test_writes_separate_comment_with_source_context(self):
        settings = {"REUP_LLM_MODEL": "test-model", "REUP_LLM_API_KEY": "test-only"}
        output = subprocess.CompletedProcess([], 0, "💬 Bạn sẽ thử tính năng này chứ?", "")
        with patch.dict(os.environ, settings), \
             patch("app.hermes_writer.hermes_executable", return_value="hermes"), \
             patch("app.hermes_writer.subprocess.run", return_value=output) as run:
            comment = hermes_writer.write_comment_with_hermes(
                "Tiêu đề: Test\nNguồn: https://example.com", "🔎 Nội dung bài đăng"
            )
        self.assertEqual(comment, "💬 Bạn sẽ thử tính năng này chứ?")
        self.assertIn("Nguồn: https://example.com", run.call_args.kwargs["input"])
        self.assertIn("🔎 Nội dung bài đăng", run.call_args.kwargs["input"])


if __name__ == "__main__":
    unittest.main()
