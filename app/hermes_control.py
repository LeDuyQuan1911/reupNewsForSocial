"""Read and control only this repository's installed Hermes cron job."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
from pathlib import Path
import re
import subprocess

from .hermes_writer import hermes_executable


SCRIPT_NAME = "reupnews-automation.py"
JOB_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{8,64}")
JOB_LINE_PATTERN = re.compile(r"^\s*([A-Za-z0-9_-]{8,64})\s+\[([a-z]+)\]\s*$")
RUN_LINE_PATTERN = re.compile(r"^\s*([A-Za-z0-9_-]{8,64})\s+(\w+)\s+job=([A-Za-z0-9_-]+).*?\s(\d{4}-\d{2}-\d{2}T\S+)\s*$")


class HermesControlError(RuntimeError):
    pass


def _job_id(root: Path) -> str:
    if not (root / "data" / "hermes-automation.enabled").is_file():
        raise HermesControlError("Hermes chưa nhận quyền chạy tự động cho repo này")
    try:
        value = (root / "data" / "hermes-cron-job-id.txt").read_text(encoding="ascii").strip()
    except OSError as exc:
        raise HermesControlError("Không tìm thấy ID job Hermes của repo này") from exc
    if not JOB_ID_PATTERN.fullmatch(value):
        raise HermesControlError("ID job Hermes không hợp lệ")
    return value


def _command(*args: str) -> str:
    try:
        result = subprocess.run(
            [hermes_executable(), "cron", *args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, check=False,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise HermesControlError("Không kết nối được với Hermes CLI") from exc
    if result.returncode != 0:
        raise HermesControlError("Hermes từ chối thao tác; kiểm tra gateway và cron")
    return result.stdout[:100_000]


def _verified_job(root: Path, listing: str | None = None) -> tuple[str, str]:
    job_id = _job_id(root)
    lines = (listing if listing is not None else _command("list", "--all")).splitlines()
    for index, line in enumerate(lines):
        match = JOB_LINE_PATTERN.fullmatch(line)
        if not match or match.group(1) != job_id:
            continue
        details = []
        for following in lines[index + 1:]:
            if JOB_LINE_PATTERN.fullmatch(following):
                break
            details.append(following.strip())
        script = next((value.split(":", 1)[1].strip() for value in details if value.startswith("Script:")), "")
        workdir = next((value.split(":", 1)[1].strip() for value in details if value.startswith("Workdir:")), "")
        if script != SCRIPT_NAME or not workdir or os.path.normcase(str(Path(workdir).resolve())) != os.path.normcase(str(root.resolve())):
            raise HermesControlError("Job Hermes không thuộc repo này")
        return job_id, match.group(2)
    raise HermesControlError("Không tìm thấy job Hermes của repo này")


def snapshot(root: Path) -> dict:
    result = {"gateway_running": False, "job_state": "unknown", "runs": [], "error": None}
    try:
        job_id = _job_id(root)
        with ThreadPoolExecutor(max_workers=3) as pool:
            listing = pool.submit(_command, "list", "--all")
            gateway = pool.submit(_command, "status")
            runs = pool.submit(_command, "runs", job_id, "--limit", "5")
            verified_id, state = _verified_job(root, listing.result())
            gateway_output = gateway.result()
            runs_output = runs.result()
        result["job_state"] = state
        result["gateway_running"] = "Gateway is running" in gateway_output
        for line in runs_output.splitlines():
            match = RUN_LINE_PATTERN.fullmatch(line)
            if not match or match.group(3) != verified_id:
                continue
            try:
                datetime.fromisoformat(match.group(4))
            except ValueError:
                continue
            result["runs"].append({"status": match.group(2), "at": match.group(4)})
    except HermesControlError as exc:
        result["error"] = str(exc)
    return result


def control_job(root: Path, action: str) -> str:
    if action not in {"pause", "resume", "run"}:
        raise HermesControlError("Thao tác Hermes không hợp lệ")
    job_id, state = _verified_job(root)
    if action == "pause" and state != "active":
        raise HermesControlError("Job Hermes không ở trạng thái đang chạy")
    if action in {"resume", "run"} and state != ("paused" if action == "resume" else "active"):
        raise HermesControlError("Trạng thái job Hermes không cho phép thao tác này")
    _command(action, job_id)
    return {
        "pause": "Đã tạm dừng Hermes. Các bài đến giờ sẽ chờ đến khi tiếp tục.",
        "resume": "Đã tiếp tục lịch Hermes.",
        "run": "Đã yêu cầu Hermes chạy một lượt ở nhịp cron tiếp theo.",
    }[action]
