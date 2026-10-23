"""Fetch RSS or Atom metadata; article bodies are not copied into the database."""

from email.utils import parsedate_to_datetime
from html import unescape
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


MAX_FEED_BYTES = 2_000_000
ATOM = "{http://www.w3.org/2005/Atom}"


def validate_feed_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


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
            published = (item.findtext("pubDate", "") or "").strip()
            try:
                published = parsedate_to_datetime(published).isoformat() if published else ""
            except (TypeError, ValueError):
                published = ""
            if title and validate_feed_url(url):
                articles.append({"title": title, "url": url, "summary": summary, "published_at": published})
    elif root.tag == f"{ATOM}feed":
        for item in root.findall(f"{ATOM}entry"):
            title = plain_text(item.findtext(f"{ATOM}title", ""))
            links = item.findall(f"{ATOM}link")
            url = next((link.get("href", "") for link in links if link.get("rel", "alternate") == "alternate"), "")
            summary = plain_text(item.findtext(f"{ATOM}summary", "") or item.findtext(f"{ATOM}content", ""))[:600]
            published = item.findtext(f"{ATOM}published", "") or item.findtext(f"{ATOM}updated", "")
            if title and validate_feed_url(url):
                articles.append({"title": title, "url": url, "summary": summary, "published_at": published})
    else:
        raise ValueError("Nguồn không phải RSS hoặc Atom")
    return articles


def fetch_feed(url: str) -> list[dict[str, str]]:
    if not validate_feed_url(url):
        raise ValueError("URL nguồn phải dùng HTTP hoặc HTTPS")
    request = Request(url, headers={"User-Agent": "reupNewsForSocial/0.1 (+local RSS reader)"})
    with urlopen(request, timeout=15) as response:
        data = response.read(MAX_FEED_BYTES + 1)
    if len(data) > MAX_FEED_BYTES:
        raise ValueError("Nguồn RSS quá lớn")
    return parse_feed(data)
