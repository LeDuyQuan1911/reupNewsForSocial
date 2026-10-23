"""Prepare a local JPEG for each post from its article or GitHub repository."""

from html.parser import HTMLParser
from http.client import HTTPSConnection
from io import BytesIO
import ipaddress
from pathlib import Path
import re
import socket
import ssl
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont, ImageOps
from playwright.sync_api import sync_playwright

from . import database


MAX_PAGE_BYTES = 1_500_000
MAX_IMAGE_BYTES = 8_000_000
MAX_IMAGE_PIXELS = 20_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class MissingImageError(ValueError):
    """A post cannot be published until its image is ready."""


class PinnedHTTPSConnection(HTTPSConnection):
    def __init__(self, hostname: str, address: str):
        super().__init__(hostname, port=443, timeout=20, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        socket_connection = socket.create_connection((self.address, 443), self.timeout)
        self.sock = self._context.wrap_socket(socket_connection, server_hostname=self.host)


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Ảnh hoặc trang nguồn phải dùng URL HTTPS công khai")
    if parsed.port not in (None, 443):
        raise ValueError("URL nguồn dùng cổng không được hỗ trợ")
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError("URL nguồn không được trỏ đến mạng riêng hoặc máy cục bộ")
    return addresses[0][4][0]


def fetch_public_bytes(url: str, limit: int) -> tuple[bytes, str]:
    current = url
    for _ in range(5):
        address = validate_public_url(current)
        parsed = urlparse(current)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"
        connection = PinnedHTTPSConnection(parsed.hostname, address)
        try:
            connection.request("GET", path, headers={"User-Agent": "Mozilla/5.0 (compatible; reupNewsForSocial/0.2)"})
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308} and response.getheader("Location"):
                current = urljoin(current, response.getheader("Location"))
                continue
            if response.status >= 400:
                raise ValueError(f"Nguồn trả HTTP {response.status}")
            data = response.read(limit + 1)
        finally:
            connection.close()
        if len(data) > limit:
            raise ValueError("Ảnh hoặc trang nguồn quá lớn")
        return data, current
    raise ValueError("Nguồn chuyển hướng quá nhiều lần")


class ImageMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.first_image = ""

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            if key in {"og:image", "twitter:image"} and values.get("content"):
                self.metadata[key] = values["content"]
        elif tag == "img" and not self.first_image:
            self.first_image = values.get("src", "")


def find_article_image(article_url: str) -> str:
    data, final_url = fetch_public_bytes(article_url, MAX_PAGE_BYTES)
    parser = ImageMetadataParser()
    parser.feed(data.decode("utf-8", errors="replace"))
    candidate = parser.metadata.get("og:image") or parser.metadata.get("twitter:image") or parser.first_image
    if not candidate:
        raise MissingImageError("Bài gốc không có ảnh có thể lấy được")
    return urljoin(final_url, candidate)


def screenshot_repository(url: str) -> bytes:
    if not re.fullmatch(r"https://github\.com/[^/?#]+/[^/?#]+/?", url):
        raise ValueError("URL repo GitHub không hợp lệ")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True, timeout=15_000)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
            response = page.goto(url, wait_until="domcontentloaded", timeout=25_000)
            if response is None or response.status >= 400:
                raise ValueError("Không mở được trang repo để chụp ảnh")
            page.locator("body").wait_for(timeout=10_000)
            return page.screenshot(type="png", full_page=False, timeout=15_000)
        finally:
            browser.close()


def normalized_jpeg(raw: bytes) -> bytes:
    with Image.open(BytesIO(raw)) as original:
        if original.width * original.height > MAX_IMAGE_PIXELS:
            raise ValueError("Ảnh nguồn quá lớn")
        if original.width < 320 or original.height < 180:
            raise ValueError("Ảnh nguồn quá nhỏ để đăng")
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((1600, 1600))
        output = BytesIO()
        image.save(output, format="JPEG", quality=86, optimize=True)
        return output.getvalue()


def title_card(title: str, source: str, article_url: str) -> bytes:
    canvas = Image.new("RGB", (1200, 630), "#123729")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((56, 54, 1144, 576), radius=32, fill="#184b36")
    draw.rectangle((57, 54, 68, 576), fill="#73d19a")
    font_path = Path("C:/Windows/Fonts/segoeui.ttf")
    try:
        heading_font = ImageFont.truetype(str(font_path), 55)
        label_font = ImageFont.truetype(str(font_path), 25)
    except OSError:
        heading_font = ImageFont.load_default(size=55)
        label_font = ImageFont.load_default(size=25)
    draw.text((105, 97), source.upper()[:55], fill="#a6edbf", font=label_font)
    words = title.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=heading_font)[2] > 950:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for index, line in enumerate(lines[:5]):
        if index == 4 and len(lines) > 5:
            line = line.rstrip(" .") + "…"
        draw.text((105, 170 + index * 70), line, fill="#ffffff", font=heading_font)
    domain = urlparse(article_url).hostname or ""
    draw.text((105, 530), domain, fill="#a6edbf", font=label_font)
    output = BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()


def post_image_path(database_path: Path, post) -> Path:
    image_file = post["image_file"] or ""
    if not re.fullmatch(rf"post-{post['id']}(?:-[0-9a-f]{{32}})?\.jpg", image_file):
        raise MissingImageError("Bài chưa có ảnh được chuẩn bị")
    path = database_path.parent / "media" / image_file
    if not path.is_file():
        raise MissingImageError("File ảnh của bài không còn trên máy; hãy lấy lại ảnh")
    return path


def prepare_post_image(database_path: Path, post_id: int) -> Path:
    post = database.get_post(database_path, post_id)
    if post is None:
        raise ValueError("Bản nháp không tồn tại")
    if post["status"] not in {"draft", "blocked", "failed"}:
        raise ValueError("Không thể thay ảnh của bài đã lên lịch hoặc đã đăng")
    if post["source_kind"] == "github":
        try:
            image = normalized_jpeg(screenshot_repository(post["article_url"]))
            kind = "screenshot"
        except Exception:
            image = normalized_jpeg(title_card(post["article_title"], post["source_name"], post["article_url"]))
            kind = "title_card"
        source_url = post["article_url"]
    else:
        source_url = post["article_url"]
        try:
            candidate = post["article_image_url"] or find_article_image(post["article_url"])
            source_url = urljoin(post["article_url"], candidate)
            raw, source_url = fetch_public_bytes(source_url, MAX_IMAGE_BYTES)
            image = normalized_jpeg(raw)
            kind = "source"
        except Exception:
            source_url = post["article_url"]
            image = normalized_jpeg(title_card(post["article_title"], post["source_name"], source_url))
            kind = "title_card"
    media_dir = database_path.parent / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"post-{post_id}-{uuid4().hex}.jpg"
    target = media_dir / file_name
    target.write_bytes(image)
    try:
        database.attach_image(database_path, post_id, file_name, source_url, kind)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target
