"""Bounded source excerpts for grounded draft writing."""

import base64
from html import unescape
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlparse

from .media import MAX_PAGE_BYTES, fetch_public_bytes


MAX_CONTEXT_CHARS = 6000


class ArticleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.hidden = 0
        self.current = []
        self.parts = []
        self.tag_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "footer", "aside", "form"}:
            self.hidden += 1
        if tag in {"article", "main"}:
            self.depth += 1
        if tag in {"p", "h1", "h2", "h3", "li"} and self.depth and not self.hidden:
            self.tag_depth += 1

    def handle_endtag(self, tag):
        if tag in {"p", "h1", "h2", "h3", "li"} and self.tag_depth:
            self.tag_depth -= 1
            if not self.tag_depth:
                value = re.sub(r"\s+", " ", unescape("".join(self.current))).strip()
                if len(value) >= 35 and value not in self.parts:
                    self.parts.append(value)
                self.current = []
        if tag in {"article", "main"} and self.depth:
            self.depth -= 1
        if tag in {"script", "style", "nav", "footer", "aside", "form"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if self.depth and self.tag_depth and not self.hidden:
            self.current.append(data)


def _github_readme(url: str) -> str:
    match = re.fullmatch(r"https://github\.com/([^/?#]+)/([^/?#]+)/?", url)
    if not match:
        raise ValueError("URL repo GitHub không hợp lệ")
    owner, repo = match.groups()
    raw, _ = fetch_public_bytes(f"https://api.github.com/repos/{owner}/{repo}/readme", MAX_PAGE_BYTES)
    document = json.loads(raw)
    if urlparse(document.get("download_url", "")).hostname != "raw.githubusercontent.com":
        raise ValueError("README GitHub không hợp lệ")
    encoded = re.sub(r"\s+", "", document["content"])
    markdown = base64.b64decode(encoded, validate=True).decode("utf-8", errors="replace")
    markdown = re.sub(r"!\[[^]]*]\([^)]*\)", "", markdown)
    markdown = re.sub(r"<[^>]+>", " ", markdown)
    markdown = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", markdown)
    markdown = re.sub(r"^\s*[#>*|`-]+\s*", "", markdown, flags=re.MULTILINE)
    return re.sub(r"\n{3,}", "\n\n", markdown).strip()[:MAX_CONTEXT_CHARS]


def source_excerpt(url: str, kind: str) -> str:
    """Read only public HTTPS source content; callers may fall back to feed metadata."""
    if kind == "github":
        return _github_readme(url)
    raw, _ = fetch_public_bytes(url, MAX_PAGE_BYTES)
    parser = ArticleTextParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return "\n".join(parser.parts)[:MAX_CONTEXT_CHARS]
