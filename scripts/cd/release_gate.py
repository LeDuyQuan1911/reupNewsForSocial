"""Allow deployment only for the current main SHA with a successful push CI run."""

import argparse
import json
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SHA = re.compile(r"[0-9a-f]{40}\Z")
REPOSITORY = "LeDuyQuan1911/reupNewsForSocial"
WORKFLOW = "ci.yml"


def is_ci_workflow(path: str) -> bool:
    expected = f".github/workflows/{WORKFLOW}"
    return path == expected or path.startswith(expected + "@")


def eligible(runs: list[dict], sha: str) -> bool:
    """A later failed rerun must revoke an earlier successful run."""
    matches = [run for run in runs if run.get("head_sha") == sha
               and run.get("head_branch") == "main" and run.get("event") == "push"
               and is_ci_workflow(run.get("path", ""))]
    if not matches:
        return False
    latest = max(matches, key=lambda run: (run.get("run_number", 0), run.get("run_attempt", 0)))
    return latest.get("status") == "completed" and latest.get("conclusion") == "success"


def check(sha: str) -> bool:
    if not SHA.fullmatch(sha):
        raise ValueError("Expected a full lowercase commit SHA")
    query = urlencode({"branch": "main", "event": "push", "head_sha": sha, "per_page": 100})
    url = f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/{WORKFLOW}/runs?{query}"
    request = Request(url, headers={"Accept": "application/vnd.github+json",
                                    "User-Agent": "reupNewsForSocial-release-gate"})
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    return eligible(payload.get("workflow_runs", []), sha)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sha")
    args = parser.parse_args()
    try:
        allowed = check(args.sha)
    except Exception as exc:
        print(f"CI status unavailable: {type(exc).__name__}", file=sys.stderr)
        return 2
    print("CI passed" if allowed else "No successful push CI for this exact main commit")
    return 0 if allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
