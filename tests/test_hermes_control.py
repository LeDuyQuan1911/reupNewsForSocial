import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import hermes_control


class HermesControlTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "data").mkdir()
        (self.root / "data" / "hermes-automation.enabled").touch()
        (self.root / "data" / "hermes-cron-job-id.txt").write_text("2dbe20d52af5", encoding="ascii")

    def tearDown(self):
        self.directory.cleanup()

    def listing(self, script="reupnews-automation.py", workdir=None, state="active"):
        return (f"  2dbe20d52af5 [{state}]\n"
                f"    Script:    {script}\n"
                f"    Workdir:   {workdir or self.root}\n")

    def test_snapshot_parses_only_installed_job(self):
        outputs = {
            ("list", "--all"): self.listing(),
            ("status",): "✓ Gateway is running — cron jobs will fire automatically",
            ("runs", "2dbe20d52af5", "--limit", "5"):
                "abc123456789 completed job=2dbe20d52af5 source=builtin 2026-10-26T23:34:52+07:00\n",
        }
        with patch("app.hermes_control._command", side_effect=lambda *args: outputs[args]) as command:
            result = hermes_control.snapshot(self.root)
        self.assertIsNone(result["error"])
        self.assertTrue(result["gateway_running"])
        self.assertEqual(result["runs"][0]["status"], "completed")
        command.assert_any_call("runs", "2dbe20d52af5", "--limit", "5")

    def test_control_rejects_other_job_and_unknown_action(self):
        with patch("app.hermes_control._command", return_value=self.listing(script="other.py")) as command:
            with self.assertRaises(hermes_control.HermesControlError):
                hermes_control.control_job(self.root, "pause")
            command.assert_called_once_with("list", "--all")
        with self.assertRaises(hermes_control.HermesControlError):
            hermes_control.control_job(self.root, "delete")

    def test_pause_and_resume_verify_state(self):
        with patch("app.hermes_control._command", side_effect=[self.listing(), "Paused"]) as command:
            hermes_control.control_job(self.root, "pause")
            command.assert_any_call("pause", "2dbe20d52af5")
        with patch("app.hermes_control._command", side_effect=[self.listing(state="paused"), "Resumed"]) as command:
            hermes_control.control_job(self.root, "resume")
            command.assert_any_call("resume", "2dbe20d52af5")


if __name__ == "__main__":
    unittest.main()
