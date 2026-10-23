"""Publish one or several JPEG photos with a caption to a Facebook Page."""

import json
import os
import re
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from uuid import uuid4


class PageConfigurationError(ValueError):
    """The Page request cannot be attempted with the current settings."""


def photo_request_body(body: str, image: bytes, token: str, boundary: str,
                       published: bool = True) -> bytes:
    parts = []
    fields = [("access_token", token)]
    if published:
        fields.append(("caption", body))
    else:
        fields.append(("published", "false"))
    for name, value in fields:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8")
        )
    parts.extend((
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"post.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n".encode(),
        image,
        f"\r\n--{boundary}--\r\n".encode(),
    ))
    return b"".join(parts)


def feed_request_body(body: str, photo_ids: list[str], token: str) -> bytes:
    fields = [("message", body), ("access_token", token)]
    fields.extend((f"attached_media[{index}]", json.dumps({"media_fbid": photo_id}))
                  for index, photo_id in enumerate(photo_ids))
    return urlencode(fields).encode("utf-8")


def publish_page(body: str, image: bytes | list[bytes]) -> str:
    page_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("REUP_FACEBOOK_PAGE_TOKEN", "").strip()
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    if not page_id or not token or not re.fullmatch(r"v\d+\.\d+", version):
        raise PageConfigurationError("Cần REUP_FACEBOOK_PAGE_ID, REUP_FACEBOOK_PAGE_TOKEN và REUP_META_GRAPH_VERSION")
    images = [image] if isinstance(image, bytes) else image
    if not 1 <= len(images) <= 10:
        raise ValueError("Bài đăng phải có từ 1 đến 10 ảnh")
    if any(not data.startswith(b"\xff\xd8\xff") or len(data) > 10_000_000 for data in images):
        raise ValueError("Ảnh JPEG không hợp lệ hoặc quá 10 MB")
    photo_ids = []
    for data in images:
        boundary = f"reup-{uuid4().hex}"
        request = Request(
            f"https://graph.facebook.com/{version}/{page_id}/photos",
            data=photo_request_body(body, data, token, boundary, published=len(images) == 1),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        photo_id = result.get("id")
        if not isinstance(photo_id, str) or not photo_id:
            raise ValueError("Facebook không trả ID ảnh")
        photo_ids.append(photo_id)
        if len(images) == 1:
            post_id = result.get("post_id") or photo_id
    if len(images) > 1:
        request = Request(
            f"https://graph.facebook.com/{version}/{page_id}/feed",
            data=feed_request_body(body, photo_ids, token),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        post_id = result.get("id")
    if not isinstance(post_id, str) or not post_id:
        raise ValueError("Facebook không trả ID bài đăng")
    return post_id
