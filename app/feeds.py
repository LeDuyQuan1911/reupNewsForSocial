"""Fetch RSS or Atom metadata; article bodies are not copied into the database."""

from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from http.client import HTTPConnection, HTTPSConnection
import ipaddress
import re
import socket
import ssl
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET


MAX_FEED_BYTES = 2_000_000
ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"


class FeedHTTPError(OSError):
    def __init__(self, status: int):
        self.status = status
        super().__init__(f"Nguồn trả HTTP {status}")


class FeedTargetError(ValueError):
    """The feed URL resolves to a non-public destination."""


class PinnedHTTPConnection(HTTPConnection):
    def __init__(self, hostname: str, address: str, port: int):
        super().__init__(hostname, port=port, timeout=15)
        self.address = address

    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), self.timeout)


class PinnedHTTPSConnection(HTTPSConnection):
    def __init__(self, hostname: str, address: str, port: int):
        super().__init__(hostname, port=port, timeout=15, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw_socket = socket.create_connection((self.address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw_socket, server_hostname=self.host)


class FirstImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = ""

    def handle_starttag(self, tag, attrs):
        if tag == "img" and not self.url:
            self.url = dict(attrs).get("src", "")


def image_from_html(value: str, article_url: str) -> str:
    parser = FirstImageParser()
    parser.feed(unescape(value))
    return urljoin(article_url, parser.url) if parser.url else ""


def rss_image(item: ET.Element, article_url: str) -> str:
    for tag in (f"{MEDIA}content", f"{MEDIA}thumbnail"):
        for image in item.findall(tag):
            url = image.get("url", "")
            if url and (tag.endswith("thumbnail") or image.get("medium") == "image" or image.get("type", "").startswith("image/")):
                return urljoin(article_url, url)
    for enclosure in item.findall("enclosure"):
        if enclosure.get("type", "").startswith("image/") and enclosure.get("url"):
            return urljoin(article_url, enclosure.get("url", ""))
    return image_from_html(item.findtext("description", "") or "", article_url)


def validate_feed_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return False
    try:
        port = parsed.port
    except ValueError:
        return False
    if port not in (None, 80 if parsed.scheme == "http" else 443):
        return False
    try:
        address = ipaddress.ip_address(parsed.hostname)
        return address.is_global
    except ValueError:
        return parsed.hostname.lower() != "localhost"


def public_feed_address(url: str) -> tuple[str, int]:
    if not validate_feed_url(url):
        raise ValueError("Nguồn RSS/Atom phải dùng URL HTTP/HTTPS công khai")
    parsed = urlparse(url)
    port = 443 if parsed.scheme == "https" else 80
    addresses = socket.getaddrinfo(parsed.hostname, port, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise FeedTargetError("Nguồn trỏ tới mạng riêng hoặc máy cục bộ")
    return addresses[0][4][0], port


def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(value))).strip()


def parse_feed(data: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(data)
    articles: list[dict[str, str]] = []
    if root.tag == "rss" or root.tag.endswith("}RDF"):
        items = root.findall("./channel/item") or root.findall("./item")
        for item in items:
            title = plain_text(item.findtext("title", ""))
            url = (item.findtext("link", "") or "").strip()
            summary = plain_text(item.findtext("description", ""))[:600]
            image_url = rss_image(item, url)
            published = (item.findtext("pubDate", "") or "").strip()
            try:
                published = parsedate_to_datetime(published).isoformat() if published else ""
            except (TypeError, ValueError):
                published = ""
            if title and validate_feed_url(url):
                articles.append({"title": title, "url": url, "summary": summary, "published_at": published, "image_url": image_url})
    elif root.tag == f"{ATOM}feed":
        for item in root.findall(f"{ATOM}entry"):
            title = plain_text(item.findtext(f"{ATOM}title", ""))
            links = item.findall(f"{ATOM}link")
            url = next((link.get("href", "") for link in links if link.get("rel", "alternate") == "alternate"), "")
            summary = plain_text(item.findtext(f"{ATOM}summary", "") or item.findtext(f"{ATOM}content", ""))[:600]
            image_url = next((urljoin(url, link.get("href", "")) for link in links if link.get("rel") == "enclosure" and link.get("type", "").startswith("image/")), "")
            if not image_url:
                image_url = image_from_html(item.findtext(f"{ATOM}summary", "") or item.findtext(f"{ATOM}content", "") or "", url)
            published = item.findtext(f"{ATOM}published", "") or item.findtext(f"{ATOM}updated", "")
            if title and validate_feed_url(url):
                articles.append({"title": title, "url": url, "summary": summary, "published_at": published, "image_url": image_url})
    else:
        raise ValueError("Nguồn không phải RSS hoặc Atom")
    return articles


def fetch_feed(url: str) -> list[dict[str, str]]:
    current = url
    for _ in range(5):
        address, port = public_feed_address(current)
        parsed = urlparse(current)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"
        connection = (PinnedHTTPSConnection if parsed.scheme == "https" else PinnedHTTPConnection)(
            parsed.hostname, address, port
        )
        try:
            connection.request("GET", path, headers={"User-Agent": "reupNewsForSocial/0.1 (+local RSS reader)"})
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308} and response.getheader("Location"):
                current = urljoin(current, response.getheader("Location"))
                continue
            if response.status >= 400:
                raise FeedHTTPError(response.status)
            data = response.read(MAX_FEED_BYTES + 1)
        finally:
            connection.close()
        if len(data) > MAX_FEED_BYTES:
            raise ValueError("Nguồn RSS quá lớn")
        return parse_feed(data)
    raise ValueError("Nguồn RSS chuyển hướng quá nhiều lần")
