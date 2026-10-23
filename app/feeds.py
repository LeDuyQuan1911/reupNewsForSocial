"""Fetch RSS or Atom metadata; article bodies are not copied into the database."""

from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


MAX_FEED_BYTES = 2_000_000
ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"


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
    if not validate_feed_url(url):
        raise ValueError("URL nguồn phải dùng HTTP hoặc HTTPS")
    request = Request(url, headers={"User-Agent": "reupNewsForSocial/0.1 (+local RSS reader)"})
    with urlopen(request, timeout=15) as response:
        data = response.read(MAX_FEED_BYTES + 1)
    if len(data) > MAX_FEED_BYTES:
        raise ValueError("Nguồn RSS quá lớn")
    return parse_feed(data)
