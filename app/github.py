"""Find popular recently created repositories through GitHub's public Search API."""

from datetime import datetime, timedelta, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def parse_repositories(payload: dict) -> list[dict[str, str]]:
    results = []
    for repo in payload.get("items", []):
        title = repo.get("full_name", "").strip()
        url = repo.get("html_url", "")
        if not title or not url.startswith("https://github.com/"):
            continue
        description = (repo.get("description") or "").strip()
        stars = repo.get("stargazers_count", 0)
        results.append({
            "title": title,
            "url": url,
            "summary": f"{description[:500]} · {stars:,} stars" if description else f"{stars:,} stars",
            "published_at": repo.get("created_at", ""),
        })
    return results


def fetch_popular_repositories() -> list[dict[str, str]]:
    since = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    query = urlencode({"q": f"created:>={since} stars:>50", "sort": "stars", "order": "desc", "per_page": 20})
    request = Request(
        f"https://api.github.com/search/repositories?{query}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "reupNewsForSocial/0.1"},
    )
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    return parse_repositories(payload)
