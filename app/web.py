import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from . import anthropic, database, feeds, github, llm, queue


BANGKOK = ZoneInfo("Asia/Bangkok")


def create_app(database_path: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("REUP_SECRET_KEY") or secrets.token_hex(32)
    app.config["DATABASE_PATH"] = database_path or Path("data/reup.sqlite3")
    database.initialize(app.config["DATABASE_PATH"])
    if database_path is None:
        database.add_starter_sources(app.config["DATABASE_PATH"])

    @app.before_request
    def protect_forms():
        token = session.setdefault("csrf_token", secrets.token_hex(24))
        if request.method == "POST" and not secrets.compare_digest(request.form.get("csrf_token", ""), token):
            abort(403)

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": session["csrf_token"]}

    @app.template_filter("bangkok_time")
    def bangkok_time(value):
        if not value:
            return ""
        return datetime.fromisoformat(value).astimezone(BANGKOK).strftime("%d/%m/%Y %H:%M")

    @app.get("/")
    def dashboard():
        posts = database.list_posts(app.config["DATABASE_PATH"])
        return render_template(
            "dashboard.html",
            sources=database.list_sources(app.config["DATABASE_PATH"]),
            articles=database.list_articles(app.config["DATABASE_PATH"]),
            posts=posts,
            posted_articles={post["article_id"] for post in posts},
        )

    @app.post("/sources")
    def add_source():
        name = request.form.get("name", "").strip()
        url = request.form.get("url", "").strip()
        if not name or not feeds.validate_feed_url(url):
            flash("Nhập tên và URL RSS/Atom hợp lệ.", "error")
        else:
            try:
                database.add_source(app.config["DATABASE_PATH"], name, url)
                flash("Đã thêm nguồn tin.", "success")
            except sqlite3.IntegrityError:
                flash("Nguồn tin này đã tồn tại.", "error")
        return redirect(url_for("dashboard"))

    @app.post("/discover")
    def discover():
        added = 0
        errors = []
        for source in database.list_sources(app.config["DATABASE_PATH"]):
            try:
                if source["kind"] == "github":
                    articles = github.fetch_popular_repositories()
                elif source["kind"] == "anthropic":
                    articles = anthropic.fetch_anthropic_news()
                else:
                    articles = feeds.fetch_feed(source["url"])[:50]
                added += database.save_articles(app.config["DATABASE_PATH"], source["id"], articles)
            except (OSError, ValueError) as exc:
                errors.append(f"{source['name']}: {exc}")
        flash(f"Đã tìm thấy {added} bài mới.", "success")
        for error in errors:
            flash(error, "error")
        return redirect(url_for("dashboard"))

    @app.post("/articles/<int:article_id>/draft")
    def draft_article(article_id):
        try:
            database.make_draft(app.config["DATABASE_PATH"], article_id)
            flash("Đã tạo bản nháp. Hãy kiểm tra nội dung trước khi lên lịch.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("dashboard"))

    @app.get("/posts/<int:post_id>")
    def edit_post(post_id):
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if post is None:
            abort(404)
        return render_template("post.html", post=post)

    @app.post("/posts/<int:post_id>/save")
    def save_post(post_id):
        body = request.form.get("body", "").strip()
        if not body:
            flash("Bài đăng không được để trống.", "error")
        else:
            try:
                database.update_draft(app.config["DATABASE_PATH"], post_id, body)
                flash("Đã lưu bản nháp.", "success")
            except ValueError as exc:
                flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/generate")
    def generate_post(post_id):
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if post is None:
            abort(404)
        if post["status"] not in {"draft", "blocked", "failed"}:
            flash("Không thể viết lại bài đã lên lịch hoặc đã đăng.", "error")
            return redirect(url_for("edit_post", post_id=post_id))
        try:
            body = llm.write_draft(post["article_title"], post["article_summary"], post["article_url"])
            database.update_draft(app.config["DATABASE_PATH"], post_id, body)
            flash("Đã tạo nội dung bằng LLM. Hãy đọc lại trước khi đăng.", "success")
        except Exception as exc:
            flash(f"Không tạo được bài: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/schedule")
    def schedule_post(post_id):
        try:
            local_time = datetime.fromisoformat(request.form.get("scheduled_at", ""))
            if local_time.tzinfo is not None:
                raise ValueError("Nhập giờ địa phương không kèm múi giờ")
            utc_time = local_time.replace(tzinfo=BANGKOK).astimezone(timezone.utc)
            if utc_time <= datetime.now(timezone.utc):
                raise ValueError("Giờ đăng phải ở tương lai")
            database.schedule_post(app.config["DATABASE_PATH"], post_id, utc_time.isoformat())
            flash("Đã lên lịch đăng lên Facebook Page.", "success")
        except ValueError as exc:
            flash(f"Không lên lịch được: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/unschedule")
    def unschedule_post(post_id):
        try:
            database.unschedule_post(app.config["DATABASE_PATH"], post_id)
            flash("Đã hủy lịch; bài trở lại bản nháp.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/publish")
    def publish_now(post_id):
        if not database.claim_post(app.config["DATABASE_PATH"], post_id):
            flash("Bài không ở trạng thái có thể đăng.", "error")
        else:
            queue.process_claimed_post(app.config["DATABASE_PATH"], post_id)
            post = database.get_post(app.config["DATABASE_PATH"], post_id)
            if post["status"] == "published":
                flash("Đã đăng lên Facebook Page.", "success")
            else:
                flash(f"Chưa đăng: {post['last_error'] or post['status']}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    return app
