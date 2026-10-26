"""Find a relevant public video explicitly embedded in an article."""

import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs

from . import llm, media


VIDEO_NOTICE = "🎬 Video ở dưới phần bình luận."


class VideoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.candidates: list[tuple[str, str]] = []
        self.in_video = False
        self.page_title = ""
        self.link_url = ""
        self.link_text = ""

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta" and (values.get("property") or values.get("name")) == "og:title":
            self.page_title = values.get("content", "")[:160]
        elif tag == "meta" and (values.get("property") or values.get("name")) in {
            "og:video", "og:video:url", "og:video:secure_url", "twitter:player"
        }:
            self.candidates.append((values.get("content", ""), ""))
        elif tag == "video":
            self.in_video = True
            if values.get("src"):
                self.candidates.append((values["src"], values.get("title", "")))
        elif tag == "source" and self.in_video and values.get("src") and values.get("type", "video/").startswith("video/"):
            self.candidates.append((values["src"], ""))
        elif tag == "iframe" and values.get("src"):
            host = (urlparse(values["src"]).hostname or "").lower()
            if host in {"youtube.com", "www.youtube.com", "youtube-nocookie.com", "www.youtube-nocookie.com",
                        "youtu.be", "www.youtu.be", "player.vimeo.com", "vimeo.com", "www.vimeo.com"}:
                self.candidates.append((values["src"], values.get("title", "")))
        elif tag == "a" and values.get("href"):
            self.link_url = values["href"]
            self.link_text = ""

    def handle_data(self, data):
        if self.link_url:
            self.link_text += data[:160]

    def handle_endtag(self, tag):
        if tag == "video":
            self.in_video = False
        elif tag == "a" and self.link_url:
            target = urlparse(self.link_url)
            host = (target.hostname or "").lower()
            if host in {"youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be",
                        "vimeo.com", "www.vimeo.com"} or target.path.lower().endswith((".mp4", ".webm")):
                self.candidates.append((self.link_url, self.link_text.strip()))
            self.link_url = ""
            self.link_text = ""


def public_video_url(candidate: str, article_url: str) -> str:
    if not candidate.strip():
        return ""
    url = urljoin(article_url, candidate.strip())
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or parsed.username or parsed.password:
        return ""
    if host in {"www.youtube.com", "youtube.com", "www.youtube-nocookie.com", "youtube-nocookie.com"}:
        match = re.fullmatch(r"/(?:embed|shorts)/([A-Za-z0-9_-]{11})", parsed.path)
        video_id = match.group(1) if match else (parse_qs(parsed.query).get("v", [""])[0] if parsed.path == "/watch" else "")
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return f"https://www.youtube.com/watch?v={video_id}"
        return ""
    if host in {"youtu.be", "www.youtu.be"} and re.fullmatch(r"/[A-Za-z0-9_-]{11}", parsed.path):
        return f"https://www.youtube.com/watch?v={parsed.path[1:]}"
    if host in {"player.vimeo.com", "vimeo.com", "www.vimeo.com"}:
        match = re.fullmatch(r"/(?:video/)?(\d+)", parsed.path)
        return f"https://vimeo.com/{match.group(1)}" if match else ""
    if host == (urlparse(article_url).hostname or "").lower() or parsed.path.lower().endswith((".mp4", ".webm")):
        try:
            media.validate_public_url(url)
        except (OSError, ValueError):
            return ""
        return url
    return ""


def find_relevant_video(article_url: str, title: str, summary: str) -> str:
    """Return one verified candidate, or empty when the article gives insufficient evidence."""
    raw, final_url = media.fetch_public_bytes(article_url, media.MAX_PAGE_BYTES)
    parser = VideoParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    candidates = []
    for source_url, video_title in parser.candidates:
        url = public_video_url(source_url, final_url)
        if url and url not in [item["url"] for item in candidates]:
            candidates.append({"url": url, "title": (video_title or parser.page_title)[:160]})
        if len(candidates) >= 5:
            break
    if not candidates:
        return ""
    system = (
        "Bạn chọn video thật sự liên quan và đáng xem kèm bài báo công nghệ. "
        "Chỉ dùng dữ liệu đã cho; bỏ qua link theo dõi kênh, quảng cáo, video giới thiệu chung. "
        "Nếu tiêu đề video mơ hồ hoặc không chắc đúng chủ đề, chọn use=false. "
        'Trả duy nhất JSON {"use": true hoặc false, "index": số thứ tự từ 0, "reason": "ngắn"}.'
    )
    answer = llm.chat(system, json.dumps({"article_title": title[:300], "article_summary": summary[:800],
                                           "videos": candidates}, ensure_ascii=False), 180)
    match = re.search(r"\{.*\}", answer, flags=re.DOTALL)
    if not match:
        return ""
    decision = json.loads(match.group())
    index = decision.get("index")
    return candidates[index]["url"] if decision.get("use") is True and type(index) is int and 0 <= index < len(candidates) else ""


def with_video_notice(body: str, video_url: str) -> str:
    if not video_url and VIDEO_NOTICE not in body:
        return body
    text = body.replace(VIDEO_NOTICE, "").strip()
    if not video_url:
        return text
    source = re.search(r"(?m)^Nguồn:\s+https?://\S+\s*$", text)
    if source:
        return f"{text[:source.start()].rstrip()}\n\n{VIDEO_NOTICE}\n\n{text[source.start():].lstrip()}"
    return f"{text}\n\n{VIDEO_NOTICE}"
