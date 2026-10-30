import sqlite3
import json
import re
from contextlib import contextmanager
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL DEFAULT 'rss',
    active INTEGER NOT NULL DEFAULT 1,
    last_checked_at TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS facebook_groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
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
CREATE TABLE IF NOT EXISTS research_reviews (
    article_id INTEGER PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    reason TEXT NOT NULL,
    method TEXT NOT NULL,
    reviewed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_research_score ON research_reviews(score DESC, reviewed_at DESC);
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL UNIQUE REFERENCES articles(id),
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    scheduled_at TEXT,
    published_at TEXT,
    platform_post_id TEXT,
    last_error TEXT,
    video_url TEXT NOT NULL DEFAULT '',
    video_comment_status TEXT NOT NULL DEFAULT '',
    video_comment_id TEXT,
    video_comment_error TEXT,
    first_comment_body TEXT NOT NULL DEFAULT '',
    first_comment_status TEXT NOT NULL DEFAULT '',
    first_comment_id TEXT,
    first_comment_error TEXT,
    image_file TEXT,
    image_source_url TEXT,
    image_kind TEXT,
    test_only INTEGER NOT NULL DEFAULT 0,
    publishing_started_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_posts_schedule ON posts(status, scheduled_at);
CREATE TABLE IF NOT EXISTS post_images (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    image_file TEXT NOT NULL UNIQUE,
    source_url TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_post_images_order ON post_images(post_id, sort_order, id);
CREATE TABLE IF NOT EXISTS automation_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    baseline_article_id INTEGER NOT NULL,
    last_scan_at TEXT
);
CREATE TABLE IF NOT EXISTS automation_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    posts_per_day INTEGER NOT NULL CHECK (posts_per_day BETWEEN 1 AND 24),
    posting_times TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS automation_settings_history (
    id INTEGER PRIMARY KEY,
    changed_at TEXT NOT NULL,
    posts_per_day INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS automation_jobs (
    article_id INTEGER PRIMARY KEY REFERENCES articles(id),
    post_id INTEGER REFERENCES posts(id),
    status TEXT NOT NULL,
    error TEXT,
    claimed_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 1,
    last_attempt_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_automation_jobs_status ON automation_jobs(status, claimed_at);
"""

STARTER_SOURCES = (
    ("OpenAI News", "https://openai.com/news/rss.xml", "rss"),
    ("Google AI", "https://blog.google/technology/ai/rss/", "rss"),
    ("Anthropic News", "https://www.anthropic.com/news", "anthropic"),
    ("GitHub nổi bật 30 ngày", "https://github.com/trending", "github"),
    ("NVIDIA Technical Blog", "https://developer.nvidia.com/blog/feed/", "rss"),
    ("AWS Machine Learning Blog", "https://aws.amazon.com/blogs/machine-learning/feed/", "rss"),
    ("Microsoft Research", "https://www.microsoft.com/en-us/research/feed/", "rss"),
)

DEFAULT_POSTING_TIMES = ("07:00", "10:00", "13:00", "16:00", "19:00", "22:00")


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
        had_post_images = db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'post_images'").fetchone() is not None
        db.executescript(SCHEMA)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(sources)")}
        if "kind" not in columns:
            db.execute("ALTER TABLE sources ADD COLUMN kind TEXT NOT NULL DEFAULT 'rss'")
        if "active" not in columns:
            db.execute("ALTER TABLE sources ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
        if "last_checked_at" not in columns:
            db.execute("ALTER TABLE sources ADD COLUMN last_checked_at TEXT")
        if "last_error" not in columns:
            db.execute("ALTER TABLE sources ADD COLUMN last_error TEXT")
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
        if "test_only" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN test_only INTEGER NOT NULL DEFAULT 0")
        if "publishing_started_at" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN publishing_started_at TEXT")
            db.execute("UPDATE posts SET publishing_started_at = ? WHERE status = 'publishing'",
                       (datetime.now(timezone.utc).isoformat(),))
        for name, definition in (
            ("video_url", "TEXT NOT NULL DEFAULT ''"),
            ("video_comment_status", "TEXT NOT NULL DEFAULT ''"),
            ("video_comment_id", "TEXT"),
            ("video_comment_error", "TEXT"),
            ("first_comment_body", "TEXT NOT NULL DEFAULT ''"),
            ("first_comment_status", "TEXT NOT NULL DEFAULT ''"),
            ("first_comment_id", "TEXT"),
            ("first_comment_error", "TEXT"),
        ):
            if name not in post_columns:
                db.execute(f"ALTER TABLE posts ADD COLUMN {name} {definition}")
        db.execute("""UPDATE posts SET first_comment_body = '🔎 Đọc thêm tại nguồn: ' ||
                   (SELECT url FROM articles WHERE articles.id = posts.article_id)
                   WHERE first_comment_body = '' AND status IN ('draft', 'blocked', 'failed', 'scheduled')""")
        if not had_post_images:
            db.execute("""INSERT INTO post_images (post_id, image_file, source_url, kind, sort_order)
                          SELECT id, image_file, COALESCE(image_source_url, ''),
                                 COALESCE(image_kind, 'source'), 0
                          FROM posts WHERE image_file IS NOT NULL AND image_file != ''""")
        job_columns = {row["name"] for row in db.execute("PRAGMA table_info(automation_jobs)")}
        if "attempts" not in job_columns:
            db.execute("ALTER TABLE automation_jobs ADD COLUMN attempts INTEGER NOT NULL DEFAULT 1")
        if "last_attempt_at" not in job_columns:
            db.execute("ALTER TABLE automation_jobs ADD COLUMN last_attempt_at TEXT")
        db.execute(
            "INSERT OR IGNORE INTO automation_settings (id, posts_per_day, posting_times) VALUES (1, ?, ?)",
            (len(DEFAULT_POSTING_TIMES), json.dumps(DEFAULT_POSTING_TIMES)),
        )
        db.execute(
            "INSERT OR IGNORE INTO automation_settings_history (id, changed_at, posts_per_day) VALUES (1, ?, ?)",
            ("1970-01-01T00:00:00+00:00", len(DEFAULT_POSTING_TIMES)),
        )


def get_posting_settings(path: Path) -> dict:
    with connect(path) as db:
        row = db.execute("SELECT posts_per_day, posting_times FROM automation_settings WHERE id = 1").fetchone()
    if row is None:
        return {"posts_per_day": len(DEFAULT_POSTING_TIMES), "times": DEFAULT_POSTING_TIMES}
    return {"posts_per_day": row["posts_per_day"], "times": tuple(json.loads(row["posting_times"]))}


def save_posting_settings(path: Path, count_value: str, times_value: str) -> dict:
    if not re.fullmatch(r"\d{1,2}", count_value.strip()):
        raise ValueError("Số bài mỗi ngày phải từ 1 đến 24")
    count = int(count_value)
    if not 1 <= count <= 24:
        raise ValueError("Số bài mỗi ngày phải từ 1 đến 24")
    pieces = [piece for piece in re.split(r"[,;\s]+", times_value.strip()) if piece]
    if len(pieces) != count:
        raise ValueError(f"Cần nhập đúng {count} khung giờ, mỗi giờ cho một bài")
    minutes = []
    for piece in pieces:
        if not re.fullmatch(r"\d{1,2}:\d{2}", piece):
            raise ValueError("Giờ đăng phải có dạng HH:MM, ví dụ 07:00")
        hour, minute = map(int, piece.split(":"))
        if hour > 23 or minute > 59:
            raise ValueError("Giờ đăng phải nằm trong ngày 00:00–23:59")
        minutes.append(hour * 60 + minute)
    minutes.sort()
    gaps = [right - left for left, right in zip(minutes, minutes[1:])]
    gaps.append(minutes[0] + 1440 - minutes[-1])
    if min(gaps) < 30:
        raise ValueError("Các giờ đăng cần cách nhau ít nhất 30 phút")
    times = tuple(f"{value // 60:02d}:{value % 60:02d}" for value in minutes)
    with connect(path) as db:
        db.execute(
            "INSERT INTO automation_settings (id, posts_per_day, posting_times) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET posts_per_day = excluded.posts_per_day, posting_times = excluded.posting_times",
            (count, json.dumps(times)),
        )
        db.execute(
            "INSERT INTO automation_settings_history (changed_at, posts_per_day) VALUES (?, ?)",
            (datetime.now(timezone.utc).isoformat(), count),
        )
    return {"posts_per_day": count, "times": times}


def add_source(path: Path, name: str, url: str) -> None:
    with connect(path) as db:
        db.execute("INSERT INTO sources (name, url) VALUES (?, ?)", (name, url))


def save_hermes_article(path: Path, article: dict[str, str], is_repo: bool) -> tuple[int, bool]:
    """Store only a verified original, respecting paused sources on the same host."""
    host = (urlsplit(article["url"]).hostname or "").lower()
    if not host:
        raise ValueError("URL bài gốc không có miền")
    source_url = f"https://{host}/"
    with connect(path) as db:
        for row in db.execute("SELECT url, active FROM sources"):
            other_host = (urlsplit(row["url"]).hostname or "").lower()
            if not row["active"] and other_host.removeprefix("www.") == host.removeprefix("www."):
                raise ValueError("Nguồn này đang tạm dừng")
        db.execute("INSERT OR IGNORE INTO sources (name, url, kind) VALUES (?, ?, ?)",
                   (host, source_url, "hermes_github" if is_repo else "hermes"))
        source = db.execute("SELECT id, active FROM sources WHERE url = ?", (source_url,)).fetchone()
        if not source or not source["active"]:
            raise ValueError("Nguồn này đang tạm dừng")
        before = db.total_changes
        db.execute("""INSERT OR IGNORE INTO articles
                   (source_id, title, url, summary, published_at, image_url)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                   (source["id"], article["title"], article["url"], article["summary"],
                    article["published_at"], article.get("image_url", "")))
        created = db.total_changes > before
        article_id = db.execute("SELECT id FROM articles WHERE url = ?", (article["url"],)).fetchone()[0]
        return article_id, created


def add_facebook_group(path: Path, name: str, url: str) -> None:
    with connect(path) as db:
        db.execute("INSERT INTO facebook_groups (name, url) VALUES (?, ?)", (name, url))


def list_facebook_groups(path: Path) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute("SELECT id, name, url, active FROM facebook_groups ORDER BY active DESC, name COLLATE NOCASE").fetchall()


def set_facebook_group_active(path: Path, group_id: int, active: bool) -> None:
    with connect(path) as db:
        if db.execute("UPDATE facebook_groups SET active = ? WHERE id = ?", (int(active), group_id)).rowcount != 1:
            raise ValueError("Nhóm Facebook không tồn tại")


def delete_facebook_group(path: Path, group_id: int) -> None:
    with connect(path) as db:
        if db.execute("DELETE FROM facebook_groups WHERE id = ?", (group_id,)).rowcount != 1:
            raise ValueError("Nhóm Facebook không tồn tại")


def add_starter_sources(path: Path) -> None:
    with connect(path) as db:
        db.executemany("INSERT OR IGNORE INTO sources (name, url, kind) VALUES (?, ?, ?)", STARTER_SOURCES)


def list_sources(path: Path, active_only: bool = False) -> list[sqlite3.Row]:
    with connect(path) as db:
        where = "WHERE active = 1" if active_only else ""
        return db.execute(f"SELECT id, name, url, kind, active, last_checked_at, last_error FROM sources {where} ORDER BY active DESC, name").fetchall()


def set_source_active(path: Path, source_id: int, active: bool) -> None:
    with connect(path) as db:
        if db.execute("UPDATE sources SET active = ? WHERE id = ?", (int(active), source_id)).rowcount != 1:
            raise ValueError("Nguồn tin không tồn tại")


def source_is_active(path: Path, source_id: int) -> bool:
    with connect(path) as db:
        row = db.execute("SELECT active FROM sources WHERE id = ?", (source_id,)).fetchone()
        return bool(row and row["active"])


def record_source_scan(path: Path, source_id: int, error: str | None = None) -> None:
    with connect(path) as db:
        db.execute("UPDATE sources SET last_checked_at = ?, last_error = ? WHERE id = ?",
                   (datetime.now(timezone.utc).isoformat(), error[:200] if error else None, source_id))


def article_filter(source_id: int | None, search: str, view: str = "all") -> tuple[str, list]:
    if view not in {"all", "unselected", "selected", "reviewed"}:
        raise ValueError("Bộ lọc bài báo không hợp lệ")
    filters = []
    parameters = []
    if source_id is not None:
        filters.append("articles.source_id = ?")
        parameters.append(source_id)
    if search:
        filters.append("(articles.title LIKE ? ESCAPE '\\' OR articles.summary LIKE ? ESCAPE '\\')")
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        parameters.extend((pattern, pattern))
    if view == "reviewed":
        filters.append("research_reviews.article_id IS NOT NULL")
    elif view != "all":
        relation = "EXISTS" if view == "selected" else "NOT EXISTS"
        filters.append(f"{relation} (SELECT 1 FROM posts WHERE posts.article_id = articles.id)")
    return (f"WHERE {' AND '.join(filters)}" if filters else ""), parameters


def list_articles(path: Path, limit: int = 100, source_id: int | None = None,
                  search: str = "", offset: int = 0, view: str = "all") -> list[sqlite3.Row]:
    with connect(path) as db:
        where, parameters = article_filter(source_id, search, view)
        order = ("research_reviews.score DESC, research_reviews.reviewed_at DESC, articles.id DESC"
                 if view == "reviewed" else "articles.discovered_at DESC, articles.id DESC")
        return db.execute(
            f"""SELECT articles.*, sources.name AS source_name,
                      research_reviews.score AS research_score,
                      research_reviews.reason AS research_reason,
                      research_reviews.method AS research_method
               FROM articles JOIN sources ON sources.id = articles.source_id
               LEFT JOIN research_reviews ON research_reviews.article_id = articles.id
               {where} ORDER BY {order} LIMIT ? OFFSET ?""",
            (*parameters, limit, offset),
        ).fetchall()


def count_articles(path: Path, source_id: int | None = None, search: str = "", view: str = "all") -> int:
    with connect(path) as db:
        where, parameters = article_filter(source_id, search, view)
        return db.execute(f"SELECT COUNT(*) FROM articles LEFT JOIN research_reviews ON research_reviews.article_id = articles.id {where}", parameters).fetchone()[0]


def list_research_candidates(path: Path, cutoff_iso: str, limit: int = 30) -> list[sqlite3.Row]:
    with connect(path) as db:
        state = db.execute("SELECT baseline_article_id FROM automation_state WHERE id = 1").fetchone()
        if state is None:
            return []
        return db.execute(
            """SELECT articles.id, articles.title, articles.summary, articles.url,
                      articles.published_at, articles.discovered_at,
                      sources.id AS source_id, sources.name AS source_name
               FROM articles JOIN sources ON sources.id = articles.source_id
               LEFT JOIN posts ON posts.article_id = articles.id
               LEFT JOIN automation_jobs ON automation_jobs.article_id = articles.id
               LEFT JOIN research_reviews ON research_reviews.article_id = articles.id
               WHERE articles.id > ? AND sources.active = 1 AND posts.id IS NULL
                 AND automation_jobs.article_id IS NULL AND research_reviews.article_id IS NULL
                 AND datetime(articles.discovered_at) >= datetime(?)
                 AND (articles.published_at IS NULL OR articles.published_at = ''
                      OR datetime(articles.published_at) >= datetime(?))
               ORDER BY COALESCE(datetime(articles.published_at), datetime(articles.discovered_at)) DESC,
                        articles.id DESC LIMIT ?""",
            (state["baseline_article_id"], cutoff_iso, cutoff_iso, limit),
        ).fetchall()


def save_research_reviews(path: Path, reviews: list[dict], reviewed_at: str) -> None:
    with connect(path) as db:
        db.executemany(
            """INSERT OR REPLACE INTO research_reviews (article_id, score, reason, method, reviewed_at)
               VALUES (?, ?, ?, ?, ?)""",
            [(item["article_id"], item["score"], item["reason"], item["method"], reviewed_at)
             for item in reviews],
        )


def research_status(path: Path) -> dict:
    with connect(path) as db:
        row = db.execute("""SELECT MAX(reviewed_at) AS last_reviewed_at,
                                   COUNT(*) AS total,
                                   SUM(CASE WHEN method = 'ai' THEN 1 ELSE 0 END) AS ai_count
                            FROM research_reviews""").fetchone()
        return {"last_reviewed_at": row["last_reviewed_at"], "total": row["total"],
                "ai_count": row["ai_count"] or 0}


def list_publication_workflows(path: Path, limit: int = 25, offset: int = 0,
                               with_post_only: bool = True) -> list[sqlite3.Row]:
    with connect(path) as db:
        where = "WHERE posts.id IS NOT NULL" if with_post_only else ""
        return db.execute(
            f"""SELECT articles.id AS article_id, articles.title AS article_title,
                      sources.name AS source_name,
                      posts.id AS post_id, posts.status AS post_status,
                      posts.test_only AS post_test_only,
                      posts.scheduled_at AS post_scheduled_at,
                      posts.published_at AS post_published_at
               FROM articles
               JOIN sources ON sources.id = articles.source_id
               LEFT JOIN posts ON posts.article_id = articles.id
               {where}
               ORDER BY articles.discovered_at DESC, articles.id DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()


def drafted_article_ids(path: Path, article_ids: list[int]) -> set[int]:
    if not article_ids:
        return set()
    placeholders = ",".join("?" for _ in article_ids)
    with connect(path) as db:
        return {row[0] for row in db.execute(
            f"SELECT article_id FROM posts WHERE article_id IN ({placeholders})", article_ids
        )}


def overview_counts(path: Path) -> dict[str, int]:
    with connect(path) as db:
        counts = {
            "sources": db.execute("SELECT COUNT(*) FROM sources WHERE active = 1").fetchone()[0],
            "source_errors": db.execute("SELECT COUNT(*) FROM sources WHERE active = 1 AND last_error IS NOT NULL").fetchone()[0],
            "articles": db.execute("SELECT COUNT(*) FROM articles").fetchone()[0],
        }
        for row in db.execute("SELECT status, COUNT(*) AS total FROM posts GROUP BY status"):
            counts[row["status"]] = row["total"]
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
        counts["stalled"] = db.execute(
            "SELECT COUNT(*) FROM posts WHERE status = 'publishing' AND publishing_started_at <= ?",
            (cutoff,),
        ).fetchone()[0]
        return counts


def daily_activity(path: Path, days: int = 7, now: datetime | None = None) -> list[dict]:
    """Daily discovery and post counts in Bangkok time, including inactive days."""
    if days not in {7, 30}:
        raise ValueError("Khoảng thống kê không hợp lệ")
    today = (now or datetime.now(timezone.utc)).astimezone(ZoneInfo("Asia/Bangkok")).date()
    start = today - timedelta(days=days - 1)
    rows = {
        (start + timedelta(days=offset)).isoformat(): {
            "day": (start + timedelta(days=offset)).isoformat(),
            "label": (start + timedelta(days=offset)).strftime("%d/%m/%Y"),
            "discovered": 0,
            "created": 0,
            "automatic": 0,
            "target": len(DEFAULT_POSTING_TIMES),
            "published": 0,
        }
        for offset in range(days)
    }
    metrics = (
        ("articles", "discovered_at", "discovered", ""),
        ("posts", "created_at", "created", ""),
        ("automation_jobs", "claimed_at", "automatic", "AND status IN ('ready', 'scheduled')"),
        ("posts", "published_at", "published", "AND status = 'published'"),
    )
    with connect(path) as db:
        history = [
            (datetime.fromisoformat(item["changed_at"]), item["posts_per_day"])
            for item in db.execute("SELECT changed_at, posts_per_day FROM automation_settings_history ORDER BY changed_at")
        ]
        for item in rows.values():
            local_day = datetime.fromisoformat(item["day"]).date()
            day_end = datetime.combine(local_day + timedelta(days=1), time.min, ZoneInfo("Asia/Bangkok")).astimezone(timezone.utc)
            item["target"] = next((count for changed_at, count in reversed(history) if changed_at < day_end),
                                  len(DEFAULT_POSTING_TIMES))
        for table, column, key, condition in metrics:
            for result in db.execute(
                f"""SELECT date({column}, '+7 hours') AS day, COUNT(*) AS total
                    FROM {table}
                    WHERE date({column}, '+7 hours') BETWEEN ? AND ? {condition}
                    GROUP BY day""",
                (start.isoformat(), today.isoformat()),
            ):
                rows[result["day"]][key] = result["total"]
    return list(reversed(list(rows.values())))


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


def get_research_review(path: Path, article_id: int):
    with connect(path) as db:
        return db.execute("SELECT * FROM research_reviews WHERE article_id = ?", (article_id,)).fetchone()


def make_draft(path: Path, article_id: int) -> int:
    with connect(path) as db:
        article = db.execute("SELECT title, url FROM articles WHERE id = ?", (article_id,)).fetchone()
        if article is None:
            raise ValueError("Bài gốc không tồn tại")
        body = f"{article['title']}\n\nNguồn: {article['url']}"
        db.execute("INSERT OR IGNORE INTO posts (article_id, body, first_comment_body) VALUES (?, ?, ?)",
                   (article_id, body, f"🔎 Đọc thêm tại nguồn: {article['url']}"))
        return db.execute("SELECT id FROM posts WHERE article_id = ?", (article_id,)).fetchone()["id"]


def make_automation_draft(path: Path, article_id: int) -> int:
    with connect(path) as db:
        article = db.execute("SELECT title, url FROM articles WHERE id = ?", (article_id,)).fetchone()
        if article is None:
            raise ValueError("Bài gốc không tồn tại")
        body = f"{article['title']}\n\nNguồn: {article['url']}"
        cursor = db.execute(
            "INSERT OR IGNORE INTO posts (article_id, body, first_comment_body) VALUES (?, ?, ?)",
            (article_id, body, f"🔎 Đọc thêm tại nguồn: {article['url']}")
        )
        if cursor.rowcount != 1:
            raise ValueError("Bài đã được tạo thủ công")
        return cursor.lastrowid


POST_VIEWS = {
    "all": (),
    "action": ("blocked", "failed", "uncertain"),
    "draft": ("draft",),
    "scheduled": ("scheduled",),
    "published": ("published",),
}


def post_filter(view: str, search: str) -> tuple[str, list]:
    if view not in POST_VIEWS:
        raise ValueError("Bộ lọc bài đăng không hợp lệ")
    filters = []
    parameters = []
    statuses = POST_VIEWS[view]
    if statuses:
        clause = f"posts.status IN ({','.join('?' for _ in statuses)})"
        if view == "action":
            clause = (f"({clause} OR (posts.status = 'publishing' AND posts.publishing_started_at <= ?) "
                      "OR (posts.status = 'published' AND (posts.video_comment_status IN ('sending', 'uncertain') "
                      "OR posts.first_comment_status IN ('sending', 'uncertain'))))")
        filters.append(clause)
        parameters.extend(statuses)
        if view == "action":
            parameters.append((datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat())
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        filters.append("(articles.title LIKE ? ESCAPE '\\' OR posts.body LIKE ? ESCAPE '\\')")
        parameters.extend((f"%{escaped}%", f"%{escaped}%"))
    return (f"WHERE {' AND '.join(filters)}" if filters else ""), parameters


def list_posts(path: Path, limit: int = 50, offset: int = 0,
               view: str = "all", search: str = ""):
    with connect(path) as db:
        where, parameters = post_filter(view, search)
        order = "posts.scheduled_at ASC, posts.id DESC" if view == "scheduled" else "posts.created_at DESC, posts.id DESC"
        return db.execute(
            f"""SELECT posts.*, articles.title AS article_title, articles.url AS article_url,
                      sources.name AS source_name
               FROM posts JOIN articles ON articles.id = posts.article_id
               JOIN sources ON sources.id = articles.source_id
               {where} ORDER BY {order} LIMIT ? OFFSET ?""",
            (*parameters, limit, offset)
        ).fetchall()


def count_posts(path: Path, view: str = "all", search: str = "") -> int:
    with connect(path) as db:
        where, parameters = post_filter(view, search)
        return db.execute(f"SELECT COUNT(*) FROM posts JOIN articles ON articles.id = posts.article_id {where}", parameters).fetchone()[0]


def get_post_for_article(path: Path, article_id: int):
    with connect(path) as db:
        return db.execute("SELECT id, status FROM posts WHERE article_id = ?", (article_id,)).fetchone()


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
    if kind not in {"source", "repo_asset", "screenshot", "title_card", "ai_generated", "router_generated", "upload"}:
        raise ValueError("Loại ảnh không hợp lệ")
    with connect(path) as db:
        first = db.execute("SELECT id FROM post_images WHERE post_id = ? ORDER BY sort_order, id LIMIT 1", (post_id,)).fetchone()
        changed = db.execute(
            "UPDATE posts SET image_file = ?, image_source_url = ?, image_kind = ? WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (image_file, source_url, kind, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Không thể thay ảnh của bài đã lên lịch hoặc đã đăng")
        if first:
            db.execute("UPDATE post_images SET image_file = ?, source_url = ?, kind = ? WHERE id = ?",
                       (image_file, source_url, kind, first["id"]))
        else:
            db.execute("INSERT INTO post_images (post_id, image_file, source_url, kind, sort_order) VALUES (?, ?, ?, ?, 0)",
                       (post_id, image_file, source_url, kind))


def list_post_images(path: Path, post_id: int) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute("SELECT * FROM post_images WHERE post_id = ? ORDER BY sort_order, id", (post_id,)).fetchall()


def get_post_image(path: Path, post_id: int, image_id: int):
    with connect(path) as db:
        return db.execute("SELECT * FROM post_images WHERE id = ? AND post_id = ?", (image_id, post_id)).fetchone()


def add_post_image(path: Path, post_id: int, image_file: str, source_url: str, kind: str) -> int:
    if kind not in {"source", "repo_asset", "screenshot", "title_card", "ai_generated", "router_generated", "upload"}:
        raise ValueError("Loại ảnh không hợp lệ")
    with connect(path) as db:
        post = db.execute("SELECT status FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post is None or post["status"] not in {"draft", "blocked", "failed"}:
            raise ValueError("Không thể thêm ảnh cho bài đã lên lịch hoặc đã đăng")
        count = db.execute("SELECT COUNT(*) FROM post_images WHERE post_id = ?", (post_id,)).fetchone()[0]
        if count >= 10:
            raise ValueError("Mỗi bài tối đa 10 ảnh")
        cursor = db.execute("INSERT INTO post_images (post_id, image_file, source_url, kind, sort_order) VALUES (?, ?, ?, ?, ?)",
                            (post_id, image_file, source_url, kind, count))
        if count == 0:
            db.execute("UPDATE posts SET image_file = ?, image_source_url = ?, image_kind = ? WHERE id = ?",
                       (image_file, source_url, kind, post_id))
        return cursor.lastrowid


def remove_post_image(path: Path, post_id: int, image_id: int) -> None:
    with connect(path) as db:
        post = db.execute("SELECT status FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post is None or post["status"] not in {"draft", "blocked", "failed"}:
            raise ValueError("Không thể xóa ảnh của bài đã lên lịch hoặc đã đăng")
        images = db.execute("SELECT * FROM post_images WHERE post_id = ? ORDER BY sort_order, id", (post_id,)).fetchall()
        if len(images) <= 1:
            raise ValueError("Bài đăng phải có ít nhất một ảnh")
        if image_id not in {image["id"] for image in images}:
            raise ValueError("Ảnh không thuộc bài đăng")
        db.execute("DELETE FROM post_images WHERE id = ? AND post_id = ?", (image_id, post_id))
        first = db.execute("SELECT * FROM post_images WHERE post_id = ? ORDER BY sort_order, id LIMIT 1", (post_id,)).fetchone()
        db.execute("UPDATE posts SET image_file = ?, image_source_url = ?, image_kind = ? WHERE id = ?",
                   (first["image_file"], first["source_url"], first["kind"], post_id))


def recent_published_titles(path: Path, since_iso: str, exclude_post_id: int) -> list[str]:
    with connect(path) as db:
        return [row["title"] for row in db.execute(
            """SELECT articles.title FROM posts JOIN articles ON articles.id = posts.article_id
               WHERE posts.status = 'published' AND posts.published_at >= ? AND posts.id != ?""",
            (since_iso, exclude_post_id),
        )]


def active_post_titles(path: Path, since_iso: str, exclude_article_id: int) -> list[str]:
    with connect(path) as db:
        return [row["title"] for row in db.execute(
            """SELECT articles.title FROM posts JOIN articles ON articles.id = posts.article_id
               WHERE articles.id != ? AND ((posts.status = 'scheduled' AND posts.test_only = 0) OR
                     (posts.status = 'published' AND posts.published_at >= ?))
               UNION SELECT articles.title FROM automation_jobs
               JOIN articles ON articles.id = automation_jobs.article_id
               WHERE articles.id != ? AND automation_jobs.status IN ('processing', 'ready')""",
            (exclude_article_id, since_iso, exclude_article_id),
        )]


def update_draft(path: Path, post_id: int, body: str) -> None:
    with connect(path) as db:
        post = db.execute("SELECT video_url FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post:
            from .video import with_video_notice
            body = with_video_notice(body, post["video_url"])
        changed = db.execute(
            "UPDATE posts SET body = ?, status = 'draft', scheduled_at = NULL, last_error = NULL WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (body, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Không thể sửa bài đã lên lịch hoặc đã đăng")


def set_first_comment(path: Path, post_id: int, body: str) -> None:
    body = body.strip()
    if not 1 <= len(body) <= 2000:
        raise ValueError("Bình luận đầu tiên phải có nội dung và không quá 2.000 ký tự")
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET first_comment_body = ? WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (body, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Chỉ có thể sửa bình luận của bản nháp")


def set_post_video(path: Path, post_id: int, video_url: str) -> None:
    from .video import with_video_notice
    with connect(path) as db:
        post = db.execute("SELECT body, status FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post is None or post["status"] not in {"draft", "blocked", "failed"}:
            raise ValueError("Chỉ có thể sửa video của bản nháp")
        db.execute("UPDATE posts SET video_url = ?, body = ?, video_comment_status = '', "
                   "video_comment_id = NULL, video_comment_error = NULL WHERE id = ?",
                   (video_url, with_video_notice(post["body"], video_url), post_id))


def schedule_post(path: Path, post_id: int, scheduled_at: str, test_only: bool = False) -> None:
    with connect(path) as db:
        if not db.execute("SELECT 1 FROM post_images WHERE post_id = ? LIMIT 1", (post_id,)).fetchone():
            raise ValueError("Bài đăng phải có ít nhất một ảnh trước khi lên lịch")
        if not test_only and not db.execute(
            "SELECT 1 FROM posts WHERE id = ? AND TRIM(first_comment_body) != ''", (post_id,)
        ).fetchone():
            raise ValueError("Bài đăng thật cần ít nhất một bình luận")
        changed = db.execute(
            "UPDATE posts SET status = 'scheduled', scheduled_at = ?, test_only = ?, last_error = NULL WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (scheduled_at, int(test_only), post_id),
        ).rowcount
        if not changed:
            raise ValueError("Bài không ở trạng thái có thể lên lịch")


def unschedule_post(path: Path, post_id: int) -> None:
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET status = 'draft', scheduled_at = NULL, test_only = 0 WHERE id = ? AND status = 'scheduled'",
            (post_id,),
        ).rowcount
        if not changed:
            raise ValueError("Bài không có lịch cần hủy")


def claim_post(path: Path, post_id: int) -> bool:
    with connect(path) as db:
        return bool(db.execute(
            """UPDATE posts SET status = 'publishing', publishing_started_at = ? WHERE id = ? AND
               status IN ('draft', 'scheduled', 'blocked', 'failed') AND test_only = 0
               AND TRIM(first_comment_body) != ''
               AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)""",
            (datetime.now(timezone.utc).isoformat(), post_id,),
        ).rowcount)


def claim_due_posts(path: Path, now_iso: str) -> list[int]:
    with connect(path) as db:
        ids = [row["id"] for row in db.execute(
            """SELECT id FROM posts WHERE status = 'scheduled' AND test_only = 0 AND scheduled_at <= ?
               AND TRIM(first_comment_body) != ''
               AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)
               ORDER BY scheduled_at LIMIT 20""",
            (now_iso,),
        )]
        claimed = []
        for post_id in ids:
            if db.execute("""UPDATE posts SET status = 'publishing', publishing_started_at = ?
                             WHERE id = ? AND status = 'scheduled' AND test_only = 0
                             AND TRIM(first_comment_body) != ''
                             AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)""",
                          (now_iso, post_id,)).rowcount:
                claimed.append(post_id)
        return claimed


def finish_post(path: Path, post_id: int, status: str, error: str | None = None, platform_post_id: str | None = None, published_at: str | None = None) -> None:
    if status not in {"published", "blocked", "failed", "uncertain"}:
        raise ValueError("Trạng thái không hợp lệ")
    with connect(path) as db:
        db.execute(
            """UPDATE posts SET status = ?, last_error = ?, platform_post_id = ?, published_at = ?,
                      publishing_started_at = NULL,
                      first_comment_status = CASE WHEN ? = 'published' AND TRIM(first_comment_body) != ''
                                                  THEN 'pending' ELSE first_comment_status END,
                      video_comment_status = CASE WHEN ? = 'published' AND video_url != '' THEN 'pending' ELSE video_comment_status END
               WHERE id = ? AND status = 'publishing'""",
            (status, error, platform_post_id, published_at, status, status, post_id),
        )


def pending_first_comment_ids(path: Path) -> list[int]:
    with connect(path) as db:
        return [row["id"] for row in db.execute(
            "SELECT id FROM posts WHERE status = 'published' AND first_comment_status = 'pending' "
            "AND platform_post_id IS NOT NULL ORDER BY published_at LIMIT 20")]


def claim_first_comment(path: Path, post_id: int):
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET first_comment_status = 'sending' WHERE id = ? AND status = 'published' "
            "AND first_comment_status = 'pending' AND platform_post_id IS NOT NULL", (post_id,)
        ).rowcount
        if changed:
            return db.execute("SELECT platform_post_id, first_comment_body FROM posts WHERE id = ?", (post_id,)).fetchone()
    return None


def finish_first_comment(path: Path, post_id: int, comment_id: str | None = None, error: str | None = None) -> None:
    with connect(path) as db:
        db.execute("UPDATE posts SET first_comment_status = ?, first_comment_id = ?, first_comment_error = ? "
                   "WHERE id = ? AND status = 'published' AND first_comment_status = 'sending'",
                   ("posted" if comment_id else "uncertain", comment_id, error, post_id))


def resolve_first_comment(path: Path, post_id: int, already_posted: bool) -> None:
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET first_comment_status = ?, first_comment_error = NULL WHERE id = ? "
            "AND status = 'published' AND first_comment_status IN ('sending', 'uncertain') "
            "AND platform_post_id IS NOT NULL AND TRIM(first_comment_body) != ''",
            ("posted" if already_posted else "pending", post_id),
        ).rowcount
        if not changed:
            raise ValueError("Bình luận không ở trạng thái cần đối chiếu")


def pending_video_comment_ids(path: Path) -> list[int]:
    with connect(path) as db:
        return [row["id"] for row in db.execute(
            "SELECT id FROM posts WHERE status = 'published' AND video_comment_status = 'pending' "
            "AND platform_post_id IS NOT NULL ORDER BY published_at LIMIT 20")]


def claim_video_comment(path: Path, post_id: int):
    with connect(path) as db:
        changed = db.execute(
            "UPDATE posts SET video_comment_status = 'sending' WHERE id = ? AND status = 'published' "
            "AND video_comment_status = 'pending' AND platform_post_id IS NOT NULL", (post_id,)).rowcount
        if changed:
            return db.execute("SELECT platform_post_id, video_url FROM posts WHERE id = ?", (post_id,)).fetchone()
    return None


def finish_video_comment(path: Path, post_id: int, comment_id: str | None = None, error: str | None = None) -> None:
    with connect(path) as db:
        db.execute("UPDATE posts SET video_comment_status = ?, video_comment_id = ?, video_comment_error = ? "
                   "WHERE id = ? AND status = 'published' AND video_comment_status = 'sending'",
                   ("posted" if comment_id else "uncertain", comment_id, error, post_id))


def resolve_video_comment(path: Path, post_id: int, already_posted: bool) -> None:
    with connect(path) as db:
        status = "posted" if already_posted else "pending"
        changed = db.execute(
            "UPDATE posts SET video_comment_status = ?, video_comment_error = NULL WHERE id = ? "
            "AND status = 'published' AND video_comment_status IN ('sending', 'uncertain') "
            "AND platform_post_id IS NOT NULL AND video_url != ''", (status, post_id)).rowcount
        if not changed:
            raise ValueError("Bình luận video không ở trạng thái cần đối chiếu")


def mark_stalled_post_uncertain(path: Path, post_id: int, now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(minutes=45)).isoformat()
    with connect(path) as db:
        changed = db.execute(
            """UPDATE posts SET status = 'uncertain', publishing_started_at = NULL,
                      last_error = 'Không xác nhận được kết quả gửi. Kiểm tra Facebook Page trước khi thử lại.'
               WHERE id = ? AND status = 'publishing' AND publishing_started_at <= ?""",
            (post_id, cutoff),
        ).rowcount
        if not changed:
            raise ValueError("Bài chưa đủ 45 phút ở trạng thái đang đăng hoặc đã đổi trạng thái")


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


def claim_automation_scan(path: Path, now_iso: str, interval_seconds: int) -> bool:
    from datetime import timedelta

    with connect(path) as db:
        db.execute(
            "INSERT OR IGNORE INTO automation_state (id, baseline_article_id) "
            "VALUES (1, 0)"
        )
        last = db.execute("SELECT last_scan_at FROM automation_state WHERE id = 1").fetchone()["last_scan_at"]
        if last and datetime.fromisoformat(last) + timedelta(seconds=interval_seconds) > datetime.fromisoformat(now_iso):
            return False
        db.execute("UPDATE automation_state SET last_scan_at = ? WHERE id = 1", (now_iso,))
        return True


def claim_daily_automation_scan(path: Path, now_iso: str) -> bool:
    """Claim one automatic source search per Bangkok calendar day."""
    current_day = datetime.fromisoformat(now_iso).astimezone(ZoneInfo("Asia/Bangkok")).date()
    with connect(path) as db:
        db.execute("INSERT OR IGNORE INTO automation_state (id, baseline_article_id) VALUES (1, 0)")
        last = db.execute("SELECT last_scan_at FROM automation_state WHERE id = 1").fetchone()["last_scan_at"]
        if last and datetime.fromisoformat(last).astimezone(ZoneInfo("Asia/Bangkok")).date() >= current_day:
            return False
        db.execute("UPDATE automation_state SET last_scan_at = ? WHERE id = 1", (now_iso,))
        return True


def claim_automation_article(path: Path, now_iso: str, day_start: str, day_end: str,
                             cutoff_iso: str, daily_limit: int):
    with connect(path) as db:
        state = db.execute("SELECT baseline_article_id FROM automation_state WHERE id = 1").fetchone()
        if state is None:
            return None
        from datetime import timedelta
        retry_before = (datetime.fromisoformat(now_iso) - timedelta(minutes=5)).isoformat()
        crashed_before = (datetime.fromisoformat(now_iso) - timedelta(minutes=10)).isoformat()
        retry = db.execute(
            """SELECT articles.*, automation_jobs.post_id AS automation_post_id
               FROM automation_jobs JOIN articles ON articles.id = automation_jobs.article_id
               JOIN sources ON sources.id = articles.source_id
               WHERE automation_jobs.attempts < 3 AND automation_jobs.claimed_at >= ?
                 AND sources.active = 1
                 AND ((automation_jobs.status = 'failed' AND
                       COALESCE(automation_jobs.last_attempt_at, automation_jobs.claimed_at) <= ?)
                   OR (automation_jobs.status = 'processing' AND
                       COALESCE(automation_jobs.last_attempt_at, automation_jobs.claimed_at) <= ?))
               ORDER BY automation_jobs.claimed_at LIMIT 1""",
            (cutoff_iso, retry_before, crashed_before),
        ).fetchone()
        if retry is not None:
            db.execute(
                "UPDATE automation_jobs SET status = 'processing', attempts = attempts + 1, "
                "last_attempt_at = ?, error = NULL WHERE article_id = ?",
                (now_iso, retry["id"]),
            )
            return retry
        used = db.execute(
            """SELECT COUNT(*) FROM automation_jobs WHERE claimed_at >= ? AND claimed_at < ?
               AND (status IN ('processing', 'ready', 'scheduled') OR
                    (status = 'failed' AND attempts < 3))""",
            (day_start, day_end),
        ).fetchone()[0]
        if used >= daily_limit:
            return None
        article = db.execute(
            """SELECT articles.*, NULL AS automation_post_id FROM articles
               JOIN sources ON sources.id = articles.source_id
               LEFT JOIN posts ON posts.article_id = articles.id
               LEFT JOIN automation_jobs ON automation_jobs.article_id = articles.id
               LEFT JOIN research_reviews ON research_reviews.article_id = articles.id
               WHERE articles.id > ? AND posts.id IS NULL AND automation_jobs.article_id IS NULL
                 AND sources.active = 1
                 AND datetime(articles.discovered_at) >= datetime(?)
                 AND (articles.published_at IS NULL OR articles.published_at = ''
                      OR datetime(articles.published_at) >= datetime(?))
               ORDER BY (SELECT COUNT(*) FROM automation_jobs AS daily_jobs
                         JOIN articles AS daily_articles ON daily_articles.id = daily_jobs.article_id
                         WHERE daily_jobs.claimed_at >= ? AND daily_jobs.claimed_at < ?
                           AND daily_articles.source_id = articles.source_id
                           AND (daily_jobs.status IN ('processing', 'ready', 'scheduled') OR
                                (daily_jobs.status = 'failed' AND daily_jobs.attempts < 3))) ASC,
                        COALESCE(research_reviews.score, -1) DESC,
                        COALESCE(datetime(articles.published_at), datetime(articles.discovered_at)) DESC,
                        articles.id DESC LIMIT 1""",
            (state["baseline_article_id"], cutoff_iso, cutoff_iso, day_start, day_end),
        ).fetchone()
        if article is None:
            return None
        db.execute(
            "INSERT INTO automation_jobs (article_id, status, claimed_at, last_attempt_at) "
            "VALUES (?, 'processing', ?, ?)",
            (article["id"], now_iso, now_iso),
        )
        return article


def record_automation_post(path: Path, article_id: int, post_id: int) -> None:
    with connect(path) as db:
        db.execute(
            "UPDATE automation_jobs SET post_id = ? WHERE article_id = ? AND status = 'processing'",
            (post_id, article_id),
        )


def finish_automation_job(path: Path, article_id: int, status: str, post_id: int | None = None,
                          error: str | None = None) -> None:
    if status not in {"ready", "scheduled", "blocked", "failed"}:
        raise ValueError("Trạng thái tự động không hợp lệ")
    with connect(path) as db:
        db.execute(
            "UPDATE automation_jobs SET status = ?, post_id = COALESCE(?, post_id), error = ? WHERE article_id = ?",
            (status, post_id, error, article_id),
        )


def block_automation_draft(path: Path, post_id: int, reason: str) -> None:
    with connect(path) as db:
        db.execute(
            "UPDATE posts SET status = 'blocked', last_error = ? WHERE id = ? AND status = 'draft'",
            (reason[:500], post_id),
        )


def ready_automation_jobs(path: Path) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute(
            """SELECT automation_jobs.article_id, automation_jobs.claimed_at,
                      posts.id AS post_id, posts.status AS post_status
               FROM automation_jobs JOIN posts ON posts.id = automation_jobs.post_id
               JOIN articles ON articles.id = automation_jobs.article_id
               JOIN sources ON sources.id = articles.source_id
               WHERE automation_jobs.status = 'ready' AND sources.active = 1
               ORDER BY automation_jobs.claimed_at LIMIT 20"""
        ).fetchall()


def reserved_post_times(path: Path, after_iso: str) -> list[str]:
    with connect(path) as db:
        return [row["scheduled_at"] for row in db.execute(
            "SELECT scheduled_at FROM posts WHERE scheduled_at >= ? AND test_only = 0 AND status IN ('scheduled', 'publishing', 'published')",
            (after_iso,),
        )]


def scheduled_post_ids(path: Path) -> set[int]:
    """Snapshot real posts that have received a posting slot."""
    with connect(path) as db:
        return {row["id"] for row in db.execute(
            "SELECT id FROM posts WHERE scheduled_at IS NOT NULL AND test_only = 0 "
            "AND status IN ('scheduled', 'publishing', 'published')"
        )}


def automation_status(path: Path) -> dict:
    with connect(path) as db:
        state = db.execute("SELECT last_scan_at FROM automation_state WHERE id = 1").fetchone()
        counts = {row["status"]: row["total"] for row in db.execute(
            "SELECT status, COUNT(*) AS total FROM automation_jobs GROUP BY status"
        )}
        return {"last_scan_at": state["last_scan_at"] if state else None, "counts": counts}
