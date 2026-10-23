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
    test_only INTEGER NOT NULL DEFAULT 0,
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
        had_post_images = db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'post_images'").fetchone() is not None
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
        if "test_only" not in post_columns:
            db.execute("ALTER TABLE posts ADD COLUMN test_only INTEGER NOT NULL DEFAULT 0")
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


def add_source(path: Path, name: str, url: str) -> None:
    with connect(path) as db:
        db.execute("INSERT INTO sources (name, url) VALUES (?, ?)", (name, url))


def add_starter_sources(path: Path) -> None:
    with connect(path) as db:
        db.executemany("INSERT OR IGNORE INTO sources (name, url, kind) VALUES (?, ?, ?)", STARTER_SOURCES)


def list_sources(path: Path) -> list[sqlite3.Row]:
    with connect(path) as db:
        return db.execute("SELECT id, name, url, kind FROM sources ORDER BY name").fetchall()


def article_filter(source_id: int | None, search: str) -> tuple[str, list]:
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
    return (f"WHERE {' AND '.join(filters)}" if filters else ""), parameters


def list_articles(path: Path, limit: int = 100, source_id: int | None = None,
                  search: str = "", offset: int = 0) -> list[sqlite3.Row]:
    with connect(path) as db:
        where, parameters = article_filter(source_id, search)
        return db.execute(
            f"""SELECT articles.*, sources.name AS source_name
               FROM articles JOIN sources ON sources.id = articles.source_id
               {where} ORDER BY articles.discovered_at DESC, articles.id DESC LIMIT ? OFFSET ?""",
            (*parameters, limit, offset),
        ).fetchall()


def count_articles(path: Path, source_id: int | None = None, search: str = "") -> int:
    with connect(path) as db:
        where, parameters = article_filter(source_id, search)
        return db.execute(f"SELECT COUNT(*) FROM articles {where}", parameters).fetchone()[0]


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
            "sources": db.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
            "articles": db.execute("SELECT COUNT(*) FROM articles").fetchone()[0],
        }
        for row in db.execute("SELECT status, COUNT(*) AS total FROM posts GROUP BY status"):
            counts[row["status"]] = row["total"]
        return counts


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


def make_automation_draft(path: Path, article_id: int) -> int:
    with connect(path) as db:
        article = db.execute("SELECT title, url FROM articles WHERE id = ?", (article_id,)).fetchone()
        if article is None:
            raise ValueError("Bài gốc không tồn tại")
        body = f"{article['title']}\n\nNguồn: {article['url']}"
        cursor = db.execute(
            "INSERT OR IGNORE INTO posts (article_id, body) VALUES (?, ?)", (article_id, body)
        )
        if cursor.rowcount != 1:
            raise ValueError("Bài đã được tạo thủ công")
        return cursor.lastrowid


def list_posts(path: Path, limit: int = 50, offset: int = 0):
    with connect(path) as db:
        return db.execute(
            """SELECT posts.*, articles.title AS article_title, articles.url AS article_url
               FROM posts JOIN articles ON articles.id = posts.article_id
               ORDER BY posts.created_at DESC, posts.id DESC LIMIT ? OFFSET ?""", (limit, offset)
        ).fetchall()


def count_posts(path: Path) -> int:
    with connect(path) as db:
        return db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]


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
    if kind not in {"source", "screenshot", "title_card", "ai_generated", "upload"}:
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
    if kind not in {"source", "screenshot", "title_card", "ai_generated", "upload"}:
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
        changed = db.execute(
            "UPDATE posts SET body = ?, status = 'draft', scheduled_at = NULL, last_error = NULL WHERE id = ? AND status IN ('draft', 'blocked', 'failed')",
            (body, post_id),
        ).rowcount
        if not changed:
            raise ValueError("Không thể sửa bài đã lên lịch hoặc đã đăng")


def schedule_post(path: Path, post_id: int, scheduled_at: str, test_only: bool = False) -> None:
    with connect(path) as db:
        if not db.execute("SELECT 1 FROM post_images WHERE post_id = ? LIMIT 1", (post_id,)).fetchone():
            raise ValueError("Bài đăng phải có ít nhất một ảnh trước khi lên lịch")
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
            """UPDATE posts SET status = 'publishing' WHERE id = ? AND
               status IN ('draft', 'scheduled', 'blocked', 'failed') AND test_only = 0
               AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)""",
            (post_id,),
        ).rowcount)


def claim_due_posts(path: Path, now_iso: str) -> list[int]:
    with connect(path) as db:
        ids = [row["id"] for row in db.execute(
            """SELECT id FROM posts WHERE status = 'scheduled' AND test_only = 0 AND scheduled_at <= ?
               AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)
               ORDER BY scheduled_at LIMIT 20""",
            (now_iso,),
        )]
        claimed = []
        for post_id in ids:
            if db.execute("""UPDATE posts SET status = 'publishing' WHERE id = ? AND status = 'scheduled' AND test_only = 0
                             AND EXISTS (SELECT 1 FROM post_images WHERE post_images.post_id = posts.id)""", (post_id,)).rowcount:
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
               WHERE automation_jobs.attempts < 3 AND automation_jobs.claimed_at >= ?
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
               LEFT JOIN posts ON posts.article_id = articles.id
               LEFT JOIN automation_jobs ON automation_jobs.article_id = articles.id
               WHERE articles.id > ? AND posts.id IS NULL AND automation_jobs.article_id IS NULL
                 AND datetime(articles.discovered_at) >= datetime(?)
                 AND (articles.published_at IS NULL OR articles.published_at = ''
                      OR datetime(articles.published_at) >= datetime(?))
               ORDER BY COALESCE(datetime(articles.published_at), datetime(articles.discovered_at)) DESC,
                        articles.id DESC LIMIT 1""",
            (state["baseline_article_id"], cutoff_iso, cutoff_iso),
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
               WHERE automation_jobs.status = 'ready' ORDER BY automation_jobs.claimed_at LIMIT 20"""
        ).fetchall()


def reserved_post_times(path: Path, after_iso: str) -> list[str]:
    with connect(path) as db:
        return [row["scheduled_at"] for row in db.execute(
            "SELECT scheduled_at FROM posts WHERE scheduled_at >= ? AND test_only = 0 AND status IN ('scheduled', 'publishing', 'published')",
            (after_iso,),
        )]


def automation_status(path: Path) -> dict:
    with connect(path) as db:
        state = db.execute("SELECT last_scan_at FROM automation_state WHERE id = 1").fetchone()
        counts = {row["status"]: row["total"] for row in db.execute(
            "SELECT status, COUNT(*) AS total FROM automation_jobs GROUP BY status"
        )}
        return {"last_scan_at": state["last_scan_at"] if state else None, "counts": counts}
