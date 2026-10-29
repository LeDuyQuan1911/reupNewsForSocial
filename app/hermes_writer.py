"""Run the installed Hermes agent as the sole author of Facebook draft text."""

import os
from pathlib import Path
import re
import shutil
import subprocess


REPO_ROOT = Path(__file__).resolve().parent.parent
EDITORIAL_BRIEF = REPO_ROOT / "docs" / "editorial-brief.md"


def _clean_cli_output(raw: str) -> str:
    """Hermes may prefix a local session id even with --quiet."""
    return re.sub(r"^session_id:\s*local-[0-9a-f]{64}", "", raw.strip()).strip()


def hermes_executable() -> str:
    configured = os.environ.get("REUP_HERMES_BIN", "").strip()
    if configured:
        path = Path(configured)
        if not path.is_file():
            raise ValueError("REUP_HERMES_BIN không trỏ tới chương trình Hermes")
        return str(path)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        candidate = Path(local_app_data) / "hermes" / "bin" / "hermes.exe"
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("hermes")
    if found:
        return found
    raise ValueError("Hermes chưa được cài. Chạy scripts/setup-hermes.ps1 trước")


def write_with_hermes(article_context: str, previous_draft: str = "") -> str:
    """Send editorial rules and bounded source context to a fresh Hermes turn."""
    if not os.environ.get("REUP_LLM_MODEL", "").strip():
        raise ValueError("Chưa cấu hình REUP_LLM_MODEL cho Hermes")
    if not os.environ.get("REUP_LLM_API_KEY", "").strip():
        raise ValueError("Chưa cấu hình REUP_LLM_API_KEY cho Hermes")
    brief = EDITORIAL_BRIEF.read_text(encoding="utf-8")
    prompt = (
        f"{brief}\n\n## Dữ liệu cho bài đăng hiện tại\n{article_context}\n\n"
        "Hãy viết một bản nháp hoàn chỉnh theo hướng dẫn trên. Chỉ trả nội dung bài đăng."
    )
    if previous_draft:
        prompt += (
            "\n\nBản nháp trước thiếu emoji/icon có ý nghĩa. Hãy viết lại toàn bài, "
            "vẫn chỉ dùng dữ kiện nguồn:\n" + previous_draft[:5000]
        )
    command = [
        hermes_executable(), "chat", "--in", str(REPO_ROOT), "--quiet",
        "--ignore-rules", "--toolsets", "bot_room", "--max-turns", "1", "--run-budget", "100",
        "--source", "tool", "--query-file", "-",
    ]
    try:
        result = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8",
            cwd=REPO_ROOT, timeout=120, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Hermes viết bài quá thời gian chờ") from exc
    if result.returncode != 0:
        raise ValueError("Hermes không tạo được bản nháp; kiểm tra cấu hình 9Router/Hermes")
    draft = _clean_cli_output(result.stdout)
    if not draft or len(draft) > 12000:
        raise ValueError("Hermes trả nội dung bản nháp không hợp lệ")
    return draft


def write_comment_with_hermes(article_context: str, post_body: str) -> str:
    """Ask Hermes for a separate, source-grounded first comment."""
    if not os.environ.get("REUP_LLM_MODEL", "").strip() or not os.environ.get("REUP_LLM_API_KEY", "").strip():
        raise ValueError("Chưa cấu hình Hermes để viết bình luận")
    brief = EDITORIAL_BRIEF.read_text(encoding="utf-8")
    prompt = (
        f"{brief}\n\n## Dữ liệu nguồn\n{article_context}\n\n"
        f"## Bài đăng đã viết\n{post_body[:6000]}\n\n"
        "Viết đúng MỘT bình luận đầu tiên cho bài Facebook này, bằng tiếng Việt, 1–3 câu ngắn. "
        "Bình luận nên gợi một câu hỏi hoặc chi tiết hữu ích cụ thể có căn cứ trong nguồn; "
        "có thể dùng icon phù hợp. Không lặp lại nguyên bài, không bịa dữ kiện, không tự hứa có video. "
        "Chỉ trả nội dung bình luận, không giải thích."
    )
    command = [
        hermes_executable(), "chat", "--in", str(REPO_ROOT), "--quiet",
        "--ignore-rules", "--toolsets", "bot_room", "--max-turns", "1", "--run-budget", "100",
        "--source", "tool", "--query-file", "-",
    ]
    try:
        result = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                encoding="utf-8", cwd=REPO_ROOT, timeout=120, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Hermes viết bình luận quá thời gian chờ") from exc
    comment = _clean_cli_output(result.stdout)
    if result.returncode != 0 or not 1 <= len(comment) <= 2000:
        raise ValueError("Hermes không tạo được bình luận hợp lệ")
    return comment
