import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.local_env import load_local_env


class LocalEnvTests(unittest.TestCase):
    def test_file_overrides_inherited_setting_and_preserves_equals(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, ".env").write_text(
                "# local settings\nREUP_LLM_MODEL=ag/test\nREUP_LLM_API_KEY='key=part'\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"REUP_LLM_MODEL": "inherited"}):
                self.assertTrue(load_local_env(Path(folder)))
                self.assertEqual(os.environ["REUP_LLM_MODEL"], "ag/test")
                self.assertEqual(os.environ["REUP_LLM_API_KEY"], "key=part")

    def test_missing_file_does_not_change_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {"REUP_LLM_MODEL": "inherited"}):
                self.assertFalse(load_local_env(Path(folder)))
                self.assertEqual(os.environ["REUP_LLM_MODEL"], "inherited")

    def test_invalid_line_reports_number_without_value(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, ".env").write_text("# header\nprivate-secret\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2") as error:
                load_local_env(Path(folder))
            self.assertNotIn("private-secret", str(error.exception))
