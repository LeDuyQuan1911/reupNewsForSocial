import importlib.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from run import hermes_owns_automation


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "hermes-automation-job.py"
SPEC = importlib.util.spec_from_file_location("hermes_automation_job", SCRIPT)
job = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(job)


class HermesAutomationTests(unittest.TestCase):
    def test_dashboard_disables_its_threads_after_handoff(self):
        with TemporaryDirectory() as folder:
            data = Path(folder)
            db = data / "reup.sqlite3"
            self.assertFalse(hermes_owns_automation(db))
            (data / "hermes-automation.enabled").write_text("Hermes", encoding="utf-8")
            self.assertTrue(hermes_owns_automation(db))

    def test_hermes_cycle_keeps_due_posts_when_discovery_disabled(self):
        with TemporaryDirectory() as folder, \
             patch.dict(os.environ, {"REUP_AUTO_ENABLED": "0"}), \
             patch("app.database.initialize"), \
             patch("app.database.add_starter_sources"), \
             patch("app.queue.process_due_posts", return_value=2) as due, \
             patch("app.automation.run_cycle") as discover:
            result = job.run_once(Path(folder))
        self.assertEqual(result, {"due": 2})
        due.assert_called_once()
        discover.assert_not_called()

    def test_overlapping_cycle_is_skipped(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "data").mkdir()
            with job.exclusive_cycle(root) as first:
                with job.exclusive_cycle(root) as second:
                    self.assertTrue(first)
                    self.assertFalse(second)

    def test_deployment_pause_skips_hermes_cycle(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "data").mkdir()
            (root / "data" / "hermes-automation.enabled").touch()
            (root / "data" / "deployment-paused").touch()
            with patch.object(job, "project_root", return_value=root), \
                 patch.object(job, "load_user_environment"), \
                 patch.object(job, "run_once") as cycle:
                self.assertEqual(job.main(), 0)
                cycle.assert_not_called()


if __name__ == "__main__":
    unittest.main()
