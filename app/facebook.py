"""Publish a JPEG photo and caption to a Facebook Page through Graph API."""

import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen
from uuid import uuid4


class PageConfigurationError(ValueError):
    """The Page request cannot be attempted with the current settings."""


def photo_request_body(body: str, image: bytes, token: str, boundary: str) -> bytes:
    parts = []
    for name, value in (("caption", body), ("access_token", token)):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8")
        )
    parts.extend((
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"post.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n".encode(),
        image,
        f"\r\n--{boundary}--\r\n".encode(),
    ))
    return b"".join(parts)


def publish_page(body: str, image_path: Path) -> str:
    page_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("REUP_FACEBOOK_PAGE_TOKEN", "").strip()
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    if not page_id or not token or not re.fullmatch(r"v\d+\.\d+", version):
        raise PageConfigurationError("Cần REUP_FACEBOOK_PAGE_ID, REUP_FACEBOOK_PAGE_TOKEN và REUP_META_GRAPH_VERSION")
    image = image_path.read_bytes()
    if not image.startswith(b"\xff\xd8\xff") or len(image) > 10_000_000:
        raise ValueError("Ảnh JPEG không hợp lệ hoặc quá 10 MB")
    boundary = f"reup-{uuid4().hex}"
    request = Request(
        f"https://graph.facebook.com/{version}/{page_id}/photos",
        data=photo_request_body(body, image, token, boundary),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    post_id = result.get("post_id") or result.get("id")
    if not isinstance(post_id, str) or not post_id:
        raise ValueError("Facebook không trả ID bài đăng")
    return post_id
