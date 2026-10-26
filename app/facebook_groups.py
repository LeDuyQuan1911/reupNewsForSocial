"""Validate Facebook Group destinations without visiting the supplied URL."""

import re
from urllib.parse import urlsplit


GROUP_PATH = re.compile(r"/groups/([A-Za-z0-9._-]+)/?")
GROUP_HOSTS = {"facebook.com", "www.facebook.com", "m.facebook.com", "web.facebook.com"}


def normalize_group_url(value: str) -> str | None:
    if len(value) > 500:
        return None
    try:
        parsed = urlsplit(value.strip())
        if (parsed.scheme != "https" or parsed.hostname not in GROUP_HOSTS
                or parsed.username or parsed.password or parsed.port):
            return None
    except ValueError:
        return None
    match = GROUP_PATH.fullmatch(parsed.path)
    if not match:
        return None
    return f"https://www.facebook.com/groups/{match.group(1)}"
