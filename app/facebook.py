"""Publish one or several JPEG photos with a caption to a Facebook Page."""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from uuid import uuid4


class PageConfigurationError(ValueError):
    """The Page request cannot be attempted with the current settings."""


def auth_mode() -> str:
    return os.environ.get("REUP_FACEBOOK_AUTH_MODE", "page_token").strip() or "page_token"


def page_token(page_id: str, version: str) -> str:
    """Resolve the selected Page token from the configured credential."""
    mode = auth_mode()
    if mode not in {"page_token", "system_user"}:
        raise PageConfigurationError("Chế độ xác thực Facebook không hợp lệ.")
    if mode == "page_token":
        token = os.environ.get("REUP_FACEBOOK_PAGE_TOKEN", "").strip()
        if not token:
            raise PageConfigurationError("Chưa có Page access token.")
        return token

    system_token = os.environ.get("REUP_FACEBOOK_SYSTEM_USER_TOKEN", "").strip()
    if not system_token:
        raise PageConfigurationError("Chưa có System User token.")
    cursor = ""
    for _ in range(10):
        query = {"fields": "id,name,access_token,tasks", "limit": "100"}
        if cursor:
            query["after"] = cursor
        request = Request(
            f"https://graph.facebook.com/{version}/me/accounts?{urlencode(query)}",
            headers={"Authorization": f"Bearer {system_token}"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=8) as response:
                data = json.load(response)
        except (HTTPError, URLError, OSError, ValueError) as exc:
            raise PageConfigurationError(
                "Không lấy được Page token bằng System User. Kiểm tra hạn token, quyền App và Page đã gán."
            ) from exc
        if not isinstance(data, dict) or not isinstance(data.get("data"), list):
            raise PageConfigurationError("Meta trả danh sách Page không hợp lệ cho System User.")
        for page in data["data"]:
            if isinstance(page, dict) and str(page.get("id", "")) == page_id:
                token = page.get("access_token")
                if not isinstance(token, str) or not token.strip():
                    raise PageConfigurationError("System User không nhận được Page token cho Page đã chọn.")
                return token.strip()
        cursors = data.get("paging", {}).get("cursors", {}) if isinstance(data.get("paging"), dict) else {}
        next_cursor = cursors.get("after") if isinstance(cursors, dict) else None
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
    raise PageConfigurationError("Page đã chọn không nằm trong các Page được gán cho System User.")


def page_identity() -> dict:
    """Read the configured Page name without returning or logging the token."""
    page_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    result = {"page_id": page_id if re.fullmatch(r"\d+", page_id) else "",
              "name": "", "verified": False, "error": ""}
    if not page_id or not version:
        result["error"] = "Chưa đủ thông số Facebook Page."
        return result
    if not result["page_id"] or not re.fullmatch(r"v\d+\.\d+", version):
        result["error"] = "Page ID hoặc phiên bản Graph API không hợp lệ."
        return result
    try:
        token = page_token(page_id, version)
    except PageConfigurationError as exc:
        result["error"] = str(exc)
        return result
    request = Request(f"https://graph.facebook.com/{version}/{page_id}?fields=id,name",
                      headers={"Authorization": f"Bearer {token}"}, method="GET")
    try:
        with urlopen(request, timeout=8) as response:
            data = json.load(response)
    except HTTPError as exc:
        try:
            details = json.loads(exc.read(8192))
            graph_error = details.get("error", {}) if isinstance(details, dict) else {}
            if not isinstance(graph_error, dict):
                graph_error = {}
        except (OSError, ValueError):
            graph_error = {}
        if graph_error.get("code") == 190 and graph_error.get("error_subcode") == 463:
            result["error"] = "Token Facebook đã hết hạn; hãy cấu hình lại kết nối."
        elif exc.code in {401, 403}:
            result["error"] = "Meta từ chối token hoặc quyền đọc Page; hãy kiểm tra và cấu hình lại token."
        else:
            result["error"] = "Meta không trả thông tin Page; hãy kiểm tra Page ID và phiên bản API."
        return result
    except (URLError, OSError, ValueError):
        result["error"] = "Không kết nối được với Meta để xác minh Page."
        return result
    if not isinstance(data, dict) or str(data.get("id", "")) != page_id or not isinstance(data.get("name"), str) or not data["name"].strip():
        result["error"] = "Token không trả về đúng Page đã cấu hình."
        return result
    result["name"] = data["name"].strip()[:200]
    result["verified"] = True
    return result


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
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    if not re.fullmatch(r"\d+", page_id) or not re.fullmatch(r"v\d+\.\d+", version):
        raise PageConfigurationError("Cần Page ID và phiên bản Graph API hợp lệ")
    token = page_token(page_id, version)
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


def comment_page(post_id: str, message: str) -> str:
    """Comment on a confirmed Page post; callers persist the result separately."""
    page_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
    version = os.environ.get("REUP_META_GRAPH_VERSION", "").strip()
    if not re.fullmatch(r"\d+", page_id) or not re.fullmatch(r"v\d+\.\d+", version):
        raise PageConfigurationError("Cần Page ID và phiên bản Graph API để bình luận")
    if not re.fullmatch(r"[A-Za-z0-9_]+", post_id) or not 1 <= len(message.strip()) <= 2000:
        raise ValueError("ID bài đăng hoặc nội dung bình luận không hợp lệ")
    token = page_token(page_id, version)
    request = Request(
        f"https://graph.facebook.com/{version}/{post_id}/comments",
        data=urlencode({"message": message.strip()}).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    comment_id = result.get("id")
    if not isinstance(comment_id, str) or not comment_id:
        raise ValueError("Facebook không trả ID bình luận")
    return comment_id


def comment_video(post_id: str, video_url: str) -> str:
    if not video_url.startswith("https://"):
        raise ValueError("URL video không hợp lệ")
    return comment_page(post_id, video_url)
