"""Collect article metadata from configured sources."""

from pathlib import Path

from . import anthropic, database, feeds, github


def scan_sources(path: Path) -> tuple[int, list[str]]:
    added = 0
    errors = []
    for source in database.list_sources(path, active_only=True):
        if source["kind"].startswith("hermes"):
            continue
        try:
            if source["kind"] == "github":
                articles = github.fetch_popular_repositories()
            elif source["kind"] == "anthropic":
                articles = anthropic.fetch_anthropic_news()
            else:
                articles = feeds.fetch_feed(source["url"])[:50]
            if not database.source_is_active(path, source["id"]):
                continue
            added += database.save_articles(path, source["id"], articles)
            database.record_source_scan(path, source["id"])
        except (OSError, ValueError) as exc:
            if isinstance(exc, feeds.FeedHTTPError):
                reason = f"HTTP {exc.status}"
            elif isinstance(exc, feeds.FeedTargetError):
                reason = str(exc)
            elif isinstance(exc, ValueError):
                reason = "Dữ liệu RSS/Atom không hợp lệ"
            else:
                reason = "Không truy cập được nguồn"
            database.record_source_scan(path, source["id"], reason)
            errors.append(f"{source['name']}: {reason}")
    return added, errors
