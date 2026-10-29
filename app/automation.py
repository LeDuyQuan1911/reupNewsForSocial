"""Bounded, restart-safe discovery and preparation for automatic Page posting."""

from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import logging
import os
import re

from . import database, discovery, hermes_research, llm, media, queue, research, video


BANGKOK = ZoneInfo("Asia/Bangkok")
MAX_ARTICLE_AGE = timedelta(hours=48)


def enabled() -> bool:
    return os.environ.get("REUP_AUTO_ENABLED", "").strip() == "1"


def page_ready() -> bool:
    mode = os.environ.get("REUP_FACEBOOK_AUTH_MODE", "page_token").strip() or "page_token"
    token_name = "REUP_FACEBOOK_SYSTEM_USER_TOKEN" if mode == "system_user" else "REUP_FACEBOOK_PAGE_TOKEN"
    return bool(
        mode in {"page_token", "system_user"}
        and re.fullmatch(r"\d+", os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip())
        and os.environ.get(token_name, "").strip()
        and re.fullmatch(r"v\d+\.\d+", os.environ.get("REUP_META_GRAPH_VERSION", "").strip())
    )


def models_ready() -> bool:
    return bool(os.environ.get("REUP_LLM_MODEL", "").strip()
                and os.environ.get("REUP_LLM_VISION_MODEL", "").strip())


def daily_bounds(now: datetime) -> tuple[str, str]:
    local_day = now.astimezone(BANGKOK).date()
    start = datetime.combine(local_day, time.min, BANGKOK).astimezone(timezone.utc)
    return start.isoformat(), (start + timedelta(days=1)).isoformat()


def prepare_articles(path: Path, now: datetime) -> int:
    if not models_ready():
        return 0
    daily_limit = database.get_posting_settings(path)["posts_per_day"]
    start, end = daily_bounds(now)
    cutoff = (now - MAX_ARTICLE_AGE).isoformat()
    prepared = 0
    attempts_this_cycle = 0
    while attempts_this_cycle < daily_limit * 2:
        article = database.claim_automation_article(path, now.isoformat(), start, end, cutoff, daily_limit)
        if article is None:
            break
        attempts_this_cycle += 1
        article_id = article["id"]
        post_id = article["automation_post_id"]
        try:
            recent = (now - timedelta(days=14)).isoformat()
            if any(queue.similar_title(article["title"], title)
                   for title in database.active_post_titles(path, recent, article_id)):
                database.finish_automation_job(path, article_id, "blocked", error="Tin tương tự đã được chọn đăng")
                continue
            if post_id is None:
                post_id = database.make_automation_draft(path, article_id)
                database.record_automation_post(path, article_id, post_id)
            post = database.get_post(path, post_id)
            try:
                image_paths = media.post_image_paths(path, post_id)
            except media.MissingImageError:
                media.prepare_post_image(path, post_id)
                image_paths = media.post_image_paths(path, post_id)
            body = llm.write_draft(article["title"], article["summary"], article["url"], post["source_kind"])
            comment = llm.write_first_comment(article["title"], article["summary"], article["url"], body)
            if post["source_kind"] not in {"github", "hermes_github"} and not post["video_url"]:
                try:
                    found_video = video.find_relevant_video(article["url"], article["title"], article["summary"])
                    if found_video:
                        database.set_post_video(path, post_id, found_video)
                except Exception as exc:
                    logging.warning("Video discovery skipped for article %s: %s", article_id, type(exc).__name__)
            database.update_draft(path, post_id, body)
            database.set_first_comment(path, post_id, comment)
            try:
                image_paths = media.publishable_post_image_paths(path, post_id)
            except media.MissingImageError as exc:
                message = str(exc)
                database.block_automation_draft(path, post_id, message)
                database.finish_automation_job(path, article_id, "blocked", post_id, message)
                continue
            approved = 0
            rejected = []
            last_reason = "Nội dung hoặc ảnh cần xem lại"
            for image in database.list_post_images(path, post_id):
                if image["kind"] == "title_card":
                    continue
                image_path = media.post_image_path(path, image, post_id)
                allowed, reason = llm.check_post(f"{body}\n\nBình luận đầu tiên: {comment}", image_path.read_bytes())
                if allowed:
                    approved += 1
                else:
                    last_reason = reason or last_reason
                    rejected.append(image)
            if approved and all(image["kind"] != "upload" for image in rejected):
                for image in rejected:
                    database.remove_post_image(path, post_id, image["id"])
                database.finish_automation_job(path, article_id, "ready", post_id)
                prepared += 1
                continue
            database.block_automation_draft(path, post_id, last_reason)
            database.finish_automation_job(path, article_id, "blocked", post_id, last_reason)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"[:500]
            if post_id is not None:
                database.block_automation_draft(path, post_id, message)
            database.finish_automation_job(path, article_id, "failed", post_id, message)
            logging.exception("Automatic preparation failed for article %s", article_id)
    return prepared


def next_slot(now: datetime, reserved: list[str], posting_times: tuple[str, ...]) -> str | None:
    occupied = {datetime.fromisoformat(value).astimezone(BANGKOK).replace(second=0, microsecond=0)
                for value in reserved}
    local_day = now.astimezone(BANGKOK).date()
    for day_offset in range(14):
        day = local_day + timedelta(days=day_offset)
        for posting_time in posting_times:
            hour, minute = map(int, posting_time.split(":"))
            slot = datetime.combine(day, time(hour, minute), BANGKOK)
            if slot <= now.astimezone(BANGKOK) + timedelta(minutes=5):
                continue
            if any(abs((slot - value).total_seconds()) < 30 * 60 for value in occupied):
                continue
            return slot.astimezone(timezone.utc).isoformat()
    return None


def schedule_ready(path: Path, now: datetime) -> int:
    if not page_ready():
        return 0
    posting_times = database.get_posting_settings(path)["times"]
    scheduled = 0
    reserved = database.reserved_post_times(path, now.isoformat())
    for job in database.ready_automation_jobs(path):
        if now - datetime.fromisoformat(job["claimed_at"]) > MAX_ARTICLE_AGE:
            database.finish_automation_job(path, job["article_id"], "failed", job["post_id"],
                                           "Bài đã quá 48 giờ trước khi kết nối Facebook Page")
            continue
        if job["post_status"] == "scheduled":
            database.finish_automation_job(path, job["article_id"], "scheduled", job["post_id"])
            continue
        if job["post_status"] != "draft":
            database.finish_automation_job(path, job["article_id"], "failed", job["post_id"],
                                           "Bản nháp đã đổi trạng thái")
            continue
        try:
            media.publishable_post_image_paths(path, job["post_id"])
        except media.MissingImageError as exc:
            database.finish_automation_job(path, job["article_id"], "blocked", job["post_id"], str(exc))
            continue
        slot = next_slot(now, reserved, posting_times)
        if slot is None:
            break
        database.schedule_post(path, job["post_id"], slot)
        database.finish_automation_job(path, job["article_id"], "scheduled", job["post_id"])
        reserved.append(slot)
        scheduled += 1
    return scheduled


def run_cycle(path: Path, now: datetime | None = None) -> dict[str, int]:
    result = {"found": 0, "reviewed": 0, "prepared": 0, "scheduled": 0}
    if not enabled():
        return result
    now = now or datetime.now(timezone.utc)
    if database.claim_daily_automation_scan(path, now.isoformat()):
        daily_target = database.get_posting_settings(path)["posts_per_day"]
        result["found"], errors = discovery.scan_sources(path)
        for error in errors:
            logging.warning("Automatic source scan: %s", error)
        if hermes_research.enabled():
            try:
                found, errors = hermes_research.find_articles(path, now, daily_target)
                result["found"] += found
                result["reviewed"] += found
                for error in errors:
                    logging.warning("Hermes research: %s", error)
            except Exception as exc:
                logging.warning("Hermes research failed; keeping curated sources: %s", type(exc).__name__)
        if os.environ.get("REUP_LLM_MODEL", "").strip():
            result["reviewed"] += research.review_candidates(path, now, daily_target)["reviewed"]
    result["prepared"] = prepare_articles(path, now)
    result["scheduled"] = schedule_ready(path, now)
    return result
