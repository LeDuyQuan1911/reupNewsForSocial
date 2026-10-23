"""Read Anthropic's public sitemap and article metadata."""

from html.parser import HTMLParser
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


SITEMAP = "https://www.anthropic.com/sitemap.xml"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        values = dict(attrs)
        key = values.get("property", "")
        if key in {"og:title", "og:description", "og:image", "article:published_time"}:
            self.metadata[key] = values.get("content", "")


def recent_news_urls(data: bytes, limit: int = 15) -> list[str]:
    root = ET.fromstring(data)
    urls = []
    for entry in root.findall(f"{SITEMAP_NS}url"):
        url = entry.findtext(f"{SITEMAP_NS}loc", "")
        modified = entry.findtext(f"{SITEMAP_NS}lastmod", "")
        if url.startswith("https://www.anthropic.com/news/"):
            urls.append((modified, url))
    return [url for _, url in sorted(urls, reverse=True)[:limit]]


def request_public_page(url: str, max_bytes: int = 1_000_000) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; reupNewsForSocial/0.1)"})
    with urlopen(request, timeout=15) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Trang quá lớn")
    return data


def fetch_anthropic_news() -> list[dict[str, str]]:
    urls = recent_news_urls(request_public_page(SITEMAP))
    articles = []
    for url in urls:
        parser = MetadataParser()
        parser.feed(request_public_page(url).decode("utf-8", "replace"))
        metadata = parser.metadata
        title = metadata.get("og:title", "").strip()
        if title:
            articles.append({
                "title": title,
                "url": url,
                "summary": metadata.get("og:description", "").strip()[:600],
                "published_at": metadata.get("article:published_time", ""),
                "image_url": metadata.get("og:image", ""),
            })
    return articles
