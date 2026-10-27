import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "release_gate", Path(__file__).resolve().parents[1] / "scripts" / "cd" / "release_gate.py"
)
release_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_gate)


class ReleaseGateTests(unittest.TestCase):
    SHA = "a" * 40

    def run_record(self, **changes):
        record = {"head_sha": self.SHA, "head_branch": "main", "event": "push",
                  "path": ".github/workflows/ci.yml@refs/heads/main",
                  "run_number": 4, "run_attempt": 1, "status": "completed", "conclusion": "success"}
        record.update(changes)
        return record

    def test_only_exact_main_push_is_accepted(self):
        self.assertTrue(release_gate.eligible([self.run_record()], self.SHA))
        for change in ({"head_sha": "b" * 40}, {"event": "pull_request"},
                       {"head_branch": "other"}, {"conclusion": "failure"},
                       {"status": "in_progress"},
                       {"path": ".github/workflows/other.yml@refs/heads/main"}):
            self.assertFalse(release_gate.eligible([self.run_record(**change)], self.SHA))

    def test_latest_rerun_controls_result(self):
        runs = [self.run_record(run_attempt=1),
                self.run_record(run_attempt=2, conclusion="failure")]
        self.assertFalse(release_gate.eligible(runs, self.SHA))


if __name__ == "__main__":
    unittest.main()
