"""Process due local jobs. A claimed job is not retried automatically after an uncertain result."""

from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
import logging
import re

from . import database, facebook, llm, media


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def similar_title(left: str, right: str) -> bool:
    normalize = lambda value: re.sub(r"[^\w\s]", "", value.casefold()).strip()
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio() >= 0.82


def process_claimed_post(path: Path, post_id: int) -> None:
    post = database.get_post(path, post_id)
    if post is None or post["status"] != "publishing" or post["test_only"]:
        return
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        prior_titles = database.recent_published_titles(path, since, post_id)
        if any(similar_title(post["article_title"], title) for title in prior_titles):
            database.finish_post(path, post_id, "blocked", error="Tin tương tự đã được đăng trong 14 ngày gần đây")
            return
        images = [image_path.read_bytes() for image_path in media.publishable_post_image_paths(path, post_id)]
        for image in images:
            allowed, reason = llm.check_post(post["body"], image)
            if not allowed:
                database.finish_post(path, post_id, "blocked", error=reason or "Nội dung hoặc ảnh cần xem lại")
                return
    except media.MissingImageError as exc:
        database.finish_post(path, post_id, "blocked", error=str(exc))
        return
    except Exception as exc:
        database.finish_post(path, post_id, "failed", error=f"{type(exc).__name__}: {exc}"[:500])
        return
    try:
        platform_post_id = facebook.publish_page(post["body"], images[0] if len(images) == 1 else images)
    except facebook.PageConfigurationError as exc:
        database.finish_post(path, post_id, "failed", error=str(exc)[:500])
        return
    except Exception as exc:
        database.finish_post(
            path, post_id, "uncertain",
            error=(f"Chưa xác nhận Facebook đã đăng hay chưa: {type(exc).__name__}: {exc}")[:500],
        )
        return
    database.finish_post(path, post_id, "published", platform_post_id=platform_post_id, published_at=now_utc())
    process_video_comment(path, post_id)


def process_video_comment(path: Path, post_id: int) -> None:
    claimed = database.claim_video_comment(path, post_id)
    if claimed is None:
        return
    try:
        comment_id = facebook.comment_video(claimed["platform_post_id"], claimed["video_url"])
    except Exception as exc:
        # A timeout may mean Facebook accepted the comment. Never retry blindly.
        database.finish_video_comment(path, post_id, error=f"{type(exc).__name__}: cần kiểm tra bình luận trên Page")
        logging.warning("Video comment needs reconciliation for post %s: %s", post_id, type(exc).__name__)
    else:
        database.finish_video_comment(path, post_id, comment_id=comment_id)


def process_due_posts(path: Path) -> int:
    ids = database.claim_due_posts(path, now_utc())
    for post_id in ids:
        process_claimed_post(path, post_id)
    for post_id in database.pending_video_comment_ids(path):
        process_video_comment(path, post_id)
    return len(ids)
