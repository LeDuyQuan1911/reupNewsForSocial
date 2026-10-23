"""Collect article metadata from configured sources."""

from pathlib import Path

from . import anthropic, database, feeds, github


def scan_sources(path: Path) -> tuple[int, list[str]]:
    added = 0
    errors = []
    for source in database.list_sources(path):
        try:
            if source["kind"] == "github":
                articles = github.fetch_popular_repositories()
            elif source["kind"] == "anthropic":
                articles = anthropic.fetch_anthropic_news()
            else:
                articles = feeds.fetch_feed(source["url"])[:50]
            added += database.save_articles(path, source["id"], articles)
        except (OSError, ValueError) as exc:
            errors.append(f"{source['name']}: {exc}")
    return added, errors
