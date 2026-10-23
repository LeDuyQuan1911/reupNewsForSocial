import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL DEFAULT 'rss',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL DEFAULT '',
    image_url TEXT,
    published_at TEXT,
    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_articles_discovered ON articles(discovered_at DESC, id DESC);
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL UNIQUE REFERENCES articles(id),
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    scheduled_at TEXT,
    published_at TEXT,
    platform_post_id TEXT,
    last_error TEXT,
    image_file TEXT,
    image_source_url TEXT,
    image_kind TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_posts_schedule ON posts(status, scheduled_at);
"""

STARTER_SOURCES = (
    ("OpenAI News", "https://openai.com/news/rss.xml", "rss"),
    ("Google AI", "https://blog.google/technology/ai/rss/", "rss"),
    ("Anthropic News", "https://www.anthropic.com/news", "anthropic"),
    ("GitHub nổi bật 30 ngày", "https://github.com/trending", "github"),
)


@contextmanager
def connect(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: Path) -> None:
    with connect(path) as db:
        db.executescript(SCHEMA)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(sources)")}
        if "kind" not in columns:
            db.execute("ALTER TABLE sources ADD COLUMN kind TEXT NOT NULL DEFAULT 'rss'")
        article_columns = {row["name"] for row in db.execute("PRAGMA table_info(articles)")}
        if "image_url" not in article_columns:
            db.execute("ALTER TABLE articles ADD COLUMN image_url TEXT")
        post_columns = {row["name"] for row in db.execute("PRAGMA table_info(posts)")}
        if "image_file" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN image_file TEXT")
        if "image_source_url" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN image_source_url TEXT")
        if "image_kind" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN image_kind TEXT")


def add_source(path: Path, name: str, url: str) -> None:
    with connect(path) as db:
        db.execute("INSERT INTO sources (name, url) VALUES (?, ?)", (name, url))


def add_starter_sources(path: Path) -> None:
    with connect(path) as db:
        db.executemany("INSERT OR IGNORE INTO sources (name, url, kind) VALUES (?, ?, ?)", STARTER_SOURCES)


def list_sources(path: Path) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute("SELECT id, name, url, kind FROM sources ORDER BY name").fetchall()


def list_articles(path: Path, limit: int = 100) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute(
            """SELECT articles.*, sources.name AS source_name
               FROM articles JOIN sources ON sources.id = articles.source_id
               ORDER BY articles.discovered_at DESC, articles.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()


def save_articles(path: Path, source_id: int, articles: list[dict[str, str]]) -> int:
    with connect(path) as db:
        rows = [{**article, "source_id": source_id, "image_url": article.get("image_url", "")} for article in articles]
        before = db.total_changes
        db.executemany(
            """INSERT OR IGNORE INTO articles (source_id, title, url, summary, published_at, image_url)
               VALUES (:source_id, :title, :url, :summary, :published_at, :image_url)""",
            rows,
        )
        added = db.total_changes - before
        db.executemany(
            """UPDATE articles SET image_url = :image_url WHERE url = :url
               AND (image_url IS NULL OR image_url = '') AND :image_url != ''""",
            rows,
        )
        return added


def get_article(path: Path, article_id: int):
    with connect(path) as db:
        return db.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()


def make_draft(path: Path, article_id: int) -> int:
    with connect(path) as db:
        article = db.execute("SELECT title, url FROM articles WHERE id = ?", (article_id,)).fetchone()
        if article is None:
            raise ValueError("Bài gốc không tồn tại")
        body = f"{article['title']}\n\nNguồn: {article['url']}"
        db.execute("INSERT OR IGNORE INTO posts (article_id, body) VALUES (?, ?)", (article_id, body))
        return db.execute("SELECT id FROM posts WHERE article_id = ?", (article_id,)).fetchone()["id"]


def list_posts(path: Path, limit: int = 50):
    with connect(path) as db:
        return db.execute(
            """SELECT posts.*, articles.title AS article_title, articles.url AS article_url
               FROM posts JOIN articles ON articles.id = posts.article_id
               ORDER BY posts.created_at DESC, posts.id DESC LIMIT ?""", (limit,)
        ).fetchall()


def get_post(path: Path, post_id: int):
    with connect(path) as db:
        return db.execute(
            """SELECT posts.*, articles.title AS article_title, articles.url AS article_url,
                      articles.summary AS article_summary, articles.image_url AS article_image_url,
                      sources.kind AS source_kind, sources.name AS source_name
               FROM posts JOIN articles ON articles.id = posts.article_id
               JOIN sources ON sources.id = articles.source_id WHERE posts.id = ?""", (post_id,)
        ).fetchone()


def attach_image(path: Path, post_id: int, image_file: str, source_url: str, kind: str = "source") -> None:
    if kind not in {"source", "screenshot", "title_card"}:
        raise ValueError("Loại ảnh không hợp lệ")
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET image_file = ?, image_source_url = ?, image_kind = ? WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (image_file, source_url, kind, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Không thể thay ảnh của bài đã lên lịch hoặc đã đăng")


def recent_published_titles(path: Path, since_iso: str, exclude_post_id: int) -> list[str]:
    with connect(path) as db:
        return [row["title"] for row in db.execute(
            """SELECT articles.title FROM posts JOIN articles ON articles.id = posts.article_id
               WHERE posts.status = 'published' AND posts.published_at >= ? AND posts.id != ?""",
            (since_iso, exclude_post_id),
        )]


def update_draft(path: Path, post_id: int, body: str) -> None:
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET body = ?, status = 'draft', scheduled_at = NULL, last_error = NULL WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (body, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Không thể sửa bài đã lên lịch hoặc đã đăng")


def schedule_post(path: Path, post_id: int, scheduled_at: str) -> None:
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET status = 'scheduled', scheduled_at = ?, last_error = NULL WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (scheduled_at, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Bài không ở trạng thái có thể lên lịch")


def unschedule_post(path: Path, post_id: int) -> None:
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET status = 'draft', scheduled_at = NULL WHERE id = ? AND status = 'scheduled'",
            (post_id,),
        ).rowcount
        if not changed:
            raise ValueError("Bài không có lịch cần hủy")


def claim_post(path: Path, post_id: int) -> bool:
    with connect(path) as db:
        return bool(db.execute(
            """UPDATE posts SET status = 'publishing' WHERE id = ? AND
               status IN ('draft', 'scheduled', 'blocked', 'failed')""",
            (post_id,),
        ).rowcount)


def claim_due_posts(path: Path, now_iso: str) -> list[int]:
    with connect(path) as db:
        ids = [row["id"] for row in db.execute(
            "SELECT id FROM posts WHERE status = 'scheduled' AND scheduled_at <= ? ORDER BY scheduled_at LIMIT 20",
            (now_iso,),
        )]
        claimed = []
        for post_id in ids:
            if db.execute("UPDATE posts SET status = 'publishing' WHERE id = ? AND status = 'scheduled'", (post_id,)).rowcount:
                claimed.append(post_id)
        return claimed


def finish_post(path: Path, post_id: int, status: str, error: str | None = None, platform_post_id: str | None = None, published_at: str | None = None) -> None:
    if status not in {"published", "blocked", "failed", "uncertain"}:
        raise ValueError("Trạng thái không hợp lệ")
    with connect(path) as db:
        db.execute(
            """UPDATE posts SET status = ?, last_error = ?, platform_post_id = ?, published_at = ?
               WHERE id = ? AND status = 'publishing'""",
            (status, error, platform_post_id, published_at, post_id),
        )


def resolve_uncertain_post(path: Path, post_id: int, was_published: bool) -> None:
    with connect(path) as db:
        if was_published:
            changed = db.execute(
                "UPDATE posts SET status = 'published', published_at = ?, last_error = NULL WHERE id = ? AND status = 'uncertain'",
                (datetime.now(timezone.utc).isoformat(), post_id),
            ).rowcount
        else:
            changed = db.execute(
                "UPDATE posts SET status = 'draft', scheduled_at = NULL, last_error = NULL WHERE id = ? AND status = 'uncertain'",
                (post_id,),
            ).rowcount
        if not changed:
            raise ValueError("Bài không ở trạng thái cần đối chiếu")
