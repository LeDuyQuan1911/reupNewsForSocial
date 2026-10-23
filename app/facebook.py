"""Publish text to a Facebook Page through Meta's Graph API."""

import json
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PageConfigurationError(ValueError):
    """The Page request cannot be attempted with the current settings."""


def publish_page(body: str) -> str:
    page_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("REUP_FACEBOOK_PAGE_TOKEN", "").strip()
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    if not page_id or not token or not re.fullmatch(r"v\d+\.\d+", version):
        raise PageConfigurationError("Cần REUP_FACEBOOK_PAGE_ID, REUP_FACEBOOK_PAGE_TOKEN và REUP_META_GRAPH_VERSION")
    request = Request(
        f"https://graph.facebook.com/{version}/{page_id}/feed",
        data=urlencode({"message": body, "access_token": token}).encode("utf-8"),
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    post_id = result.get("id")
    if not isinstance(post_id, str) or not post_id:
        raise ValueError("Facebook không trả ID bài đăng")
    return post_id
