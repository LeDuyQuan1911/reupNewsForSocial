"""Hermes cron entry point for this repository's automatic Page workflow."""

import json
import os
from pathlib import Path
import sys
from contextlib import contextmanager
from datetime import datetime, timezone


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_POINTER = SCRIPT_DIR / "reupnews-root.txt"
ENV_NAMES = (
    "REUP_LLM_BASE_URL", "REUP_LLM_MODEL", "REUP_LLM_VISION_MODEL",
    "REUP_LLM_IMAGE_MODEL", "REUP_LLM_API_KEY", "REUP_HERMES_BIN",
    "REUP_AUTO_ENABLED", "REUP_FACEBOOK_PAGE_ID", "REUP_FACEBOOK_PAGE_TOKEN",
    "REUP_FACEBOOK_AUTH_MODE", "REUP_FACEBOOK_SYSTEM_USER_TOKEN",
    "REUP_META_GRAPH_VERSION", "REUP_SECRET_KEY",
)


def load_user_environment() -> None:
    """Get current User settings even when the Hermes gateway predates them."""
    if sys.platform != "win32":
        return
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        for name in ENV_NAMES:
            try:
                value, _ = winreg.QueryValueEx(key, name)
            except FileNotFoundError:
                continue
            if isinstance(value, str) and value.strip():
                os.environ[name] = value


def project_root() -> Path:
    root = Path(ROOT_POINTER.read_text(encoding="utf-8").strip().lstrip("\ufeff")).resolve()
    if not (root / "app" / "automation.py").is_file():
        raise RuntimeError("Không tìm thấy repo reupNewsForSocial; cài lại lịch Hermes")
    return root


def run_once(root: Path) -> dict[str, int]:
    previous_dir = Path.cwd()
    sys.path.insert(0, str(root))
    try:
        os.chdir(root)
        from app import automation, database, queue

        db_path = root / "data" / "reup.sqlite3"
        database.initialize(db_path)
        database.add_starter_sources(db_path)
        due = queue.process_due_posts(db_path)
        result = automation.run_cycle(db_path) if automation.enabled() else {}
        return {"due": due, **result}
    finally:
        os.chdir(previous_dir)
        sys.path.remove(str(root))


@contextmanager
def exclusive_cycle(root: Path):
    """Skip overlapping cron fires while a slow Hermes draft is still running."""
    lock_path = root / "data" / "hermes-job.lock"
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            handle.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def main() -> int:
    load_user_environment()
    root = project_root()
    if "--check" in sys.argv[1:]:
        print("Hermes automation job ready")
        return 0
    if not (root / "data" / "hermes-automation.enabled").exists():
        raise RuntimeError("Hermes chưa nhận quyền điều phối tự động của repo")
    if (root / "data" / "deployment-paused").exists():
        return 0
    with exclusive_cycle(root) as acquired:
        if not acquired:
            return 0
        if (root / "data" / "deployment-paused").exists():
            return 0
        try:
            result = run_once(root)
        except Exception as exc:
            write_status(root, "failed", {"error": type(exc).__name__})
            raise
        write_status(root, "ok", result)
    if any(result.values()):
        print("Hermes cycle: " + ", ".join(f"{key}={value}" for key, value in result.items()))
    return 0


def write_status(root: Path, status: str, details: dict) -> None:
    target = root / "data" / "hermes-last-cycle.json"
    temporary = target.with_suffix(".tmp")
    payload = {"at": datetime.now(timezone.utc).isoformat(), "status": status, **details}
    temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Hermes automation cycle failed: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
