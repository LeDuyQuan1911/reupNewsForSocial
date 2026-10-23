"""Bounded, restart-safe discovery and preparation for automatic Page posting."""

from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import logging
import os
import re

from . import database, discovery, llm, media, queue


BANGKOK = ZoneInfo("Asia/Bangkok")
POST_HOURS = (7, 10, 13, 16, 19, 22)
DAILY_LIMIT = 6
SCAN_INTERVAL_SECONDS = 3600
MAX_ARTICLE_AGE = timedelta(hours=48)


def enabled() -> bool:
    return os.environ.get("REUP_AUTO_ENABLED", "").strip() == "1"


def page_ready() -> bool:
    return bool(
        os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
        and os.environ.get("REUP_FACEBOOK_PAGE_TOKEN", "").strip()
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
    start, end = daily_bounds(now)
    cutoff = (now - MAX_ARTICLE_AGE).isoformat()
    prepared = 0
    attempts_this_cycle = 0
    while attempts_this_cycle < DAILY_LIMIT * 2:
        article = database.claim_automation_article(path, now.isoformat(), start, end, cutoff, DAILY_LIMIT)
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
            body = llm.write_draft(article["title"], article["summary"], article["url"])
            database.update_draft(path, post_id, body)
            for image_path in image_paths:
                allowed, reason = llm.check_post(body, image_path.read_bytes())
                if not allowed:
                    message = reason or "Nội dung hoặc ảnh cần xem lại"
                    database.block_automation_draft(path, post_id, message)
                    database.finish_automation_job(path, article_id, "blocked", post_id, message)
                    break
            else:
                database.finish_automation_job(path, article_id, "ready", post_id)
                prepared += 1
                continue
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"[:500]
            if post_id is not None:
                database.block_automation_draft(path, post_id, message)
            database.finish_automation_job(path, article_id, "failed", post_id, message)
            logging.exception("Automatic preparation failed for article %s", article_id)
    return prepared


def next_slot(now: datetime, reserved: list[str]) -> str | None:
    occupied = {datetime.fromisoformat(value).astimezone(BANGKOK).replace(second=0, microsecond=0)
                for value in reserved}
    local_day = now.astimezone(BANGKOK).date()
    for day_offset in range(14):
        day = local_day + timedelta(days=day_offset)
        for hour in POST_HOURS:
            slot = datetime.combine(day, time(hour), BANGKOK)
            if slot <= now.astimezone(BANGKOK) + timedelta(minutes=5):
                continue
            if any(abs((slot - value).total_seconds()) < 30 * 60 for value in occupied):
                continue
            return slot.astimezone(timezone.utc).isoformat()
    return None


def schedule_ready(path: Path, now: datetime) -> int:
    if not page_ready():
        return 0
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
        slot = next_slot(now, reserved)
        if slot is None:
            break
        database.schedule_post(path, job["post_id"], slot)
        database.finish_automation_job(path, job["article_id"], "scheduled", job["post_id"])
        reserved.append(slot)
        scheduled += 1
    return scheduled


def run_cycle(path: Path, now: datetime | None = None) -> dict[str, int]:
    result = {"found": 0, "prepared": 0, "scheduled": 0}
    if not enabled():
        return result
    now = now or datetime.now(timezone.utc)
    if database.claim_automation_scan(path, now.isoformat(), SCAN_INTERVAL_SECONDS):
        result["found"], errors = discovery.scan_sources(path)
        for error in errors:
            logging.warning("Automatic source scan: %s", error)
    result["prepared"] = prepare_articles(path, now)
    result["scheduled"] = schedule_ready(path, now)
    return result
