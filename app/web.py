import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for

from . import automation, database, discovery, feeds, llm, media, queue


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
        return render_template(
            "dashboard.html",
            counts=database.overview_counts(app.config["DATABASE_PATH"]),
            articles=database.list_articles(app.config["DATABASE_PATH"], limit=6),
            posts=database.list_posts(app.config["DATABASE_PATH"], limit=6),
        )

    @app.get("/articles")
    def articles_page():
        source_value = request.args.get("source", "")
        source_id = int(source_value) if source_value.isdecimal() else None
        search = request.args.get("q", "").strip()[:100]
        page_size = 25
        total = database.count_articles(app.config["DATABASE_PATH"], source_id, search)
        page_value = request.args.get("page", "1")
        requested_page = int(page_value) if page_value.isdecimal() and len(page_value) <= 10 else 1
        page = min(max(1, requested_page), max(1, (total + page_size - 1) // page_size))
        articles = database.list_articles(app.config["DATABASE_PATH"], limit=page_size,
                                          source_id=source_id, search=search, offset=(page - 1) * page_size)
        return render_template(
            "articles.html",
            articles=articles,
            sources=database.list_sources(app.config["DATABASE_PATH"]),
            posted_articles=database.drafted_article_ids(app.config["DATABASE_PATH"],
                                                         [article["id"] for article in articles]),
            selected_source=source_id,
            search=search,
            page=page,
            total=total,
            page_size=page_size,
        )

    @app.get("/articles/<int:article_id>")
    def article_detail(article_id):
        article = database.get_article(app.config["DATABASE_PATH"], article_id)
        if article is None:
            abort(404)
        post = database.get_post_for_article(app.config["DATABASE_PATH"], article_id)
        source = next((item for item in database.list_sources(app.config["DATABASE_PATH"])
                       if item["id"] == article["source_id"]), None)
        return render_template("article.html", article=article, source=source, post=post)

    @app.get("/sources")
    def sources_page():
        return render_template("sources.html", sources=database.list_sources(app.config["DATABASE_PATH"]))

    @app.get("/posts")
    def posts_page():
        page_size = 25
        total = database.count_posts(app.config["DATABASE_PATH"])
        page_value = request.args.get("page", "1")
        requested_page = int(page_value) if page_value.isdecimal() and len(page_value) <= 10 else 1
        page = min(max(1, requested_page), max(1, (total + page_size - 1) // page_size))
        return render_template("posts.html", posts=database.list_posts(
            app.config["DATABASE_PATH"], limit=page_size, offset=(page - 1) * page_size
        ), page=page, total=total, page_size=page_size)

    @app.get("/workflow")
    def workflow_page():
        page_size = 25
        selected_view = "all" if request.args.get("view") == "all" else "posts"
        article_total = database.count_articles(app.config["DATABASE_PATH"])
        post_total = database.count_posts(app.config["DATABASE_PATH"])
        total = article_total if selected_view == "all" else post_total
        page_value = request.args.get("page", "1")
        requested_page = int(page_value) if page_value.isdecimal() and len(page_value) <= 10 else 1
        page = min(max(1, requested_page), max(1, (total + page_size - 1) // page_size))
        workflows = database.list_publication_workflows(
            app.config["DATABASE_PATH"], limit=page_size, offset=(page - 1) * page_size,
            with_post_only=selected_view == "posts"
        )
        return render_template("workflow.html", workflows=workflows, page=page,
                               total=total, page_size=page_size, selected_view=selected_view,
                               article_total=article_total, post_total=post_total)

    @app.get("/account")
    def account_page():
        return render_template("account.html", automation_status=database.automation_status(app.config["DATABASE_PATH"]),
                               automation_enabled=automation.enabled(), connections={
            "page": bool(os.environ.get("REUP_FACEBOOK_PAGE_ID") and os.environ.get("REUP_FACEBOOK_PAGE_TOKEN")),
            "llm": bool(os.environ.get("REUP_LLM_MODEL")),
            "vision": bool(os.environ.get("REUP_LLM_VISION_MODEL")),
        })

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
        return redirect(url_for("sources_page"))

    @app.post("/discover")
    def discover():
        added, errors = discovery.scan_sources(app.config["DATABASE_PATH"])
        flash(f"Đã tìm thấy {added} bài mới.", "success")
        for error in errors:
            flash(error, "error")
        return redirect(url_for("articles_page"))

    @app.post("/articles/<int:article_id>/draft")
    def draft_article(article_id):
        try:
            post_id = database.make_draft(app.config["DATABASE_PATH"], article_id)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("articles_page"))
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if not database.list_post_images(app.config["DATABASE_PATH"], post_id):
            try:
                media.prepare_post_image(app.config["DATABASE_PATH"], post_id)
                flash("Đã tạo bản nháp và lưu ảnh minh họa.", "success")
            except Exception as exc:
                flash(f"Đã tạo bản nháp nhưng chưa lấy được ảnh: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.get("/posts/<int:post_id>")
    def edit_post(post_id):
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if post is None:
            abort(404)
        images = database.list_post_images(app.config["DATABASE_PATH"], post_id)
        try:
            media.post_image_paths(app.config["DATABASE_PATH"], post_id)
            has_image = True
        except media.MissingImageError:
            has_image = False
        return render_template("post.html", post=post, images=images, has_image=has_image)

    @app.get("/posts/<int:post_id>/image")
    def post_image(post_id):
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if post is None:
            abort(404)
        try:
            image_path = media.post_image_path(app.config["DATABASE_PATH"], post)
        except media.MissingImageError:
            abort(404)
        return send_file(image_path.resolve(), mimetype="image/jpeg", max_age=0)

    @app.get("/posts/<int:post_id>/images/<int:image_id>")
    def post_image_item(post_id, image_id):
        image = database.get_post_image(app.config["DATABASE_PATH"], post_id, image_id)
        if image is None:
            abort(404)
        try:
            image_path = media.post_image_path(app.config["DATABASE_PATH"], image, post_id)
        except media.MissingImageError:
            abort(404)
        return send_file(image_path.resolve(), mimetype="image/jpeg", max_age=0)

    @app.post("/posts/<int:post_id>/image/refresh")
    def refresh_post_image(post_id):
        try:
            media.prepare_post_image(app.config["DATABASE_PATH"], post_id, append=True)
            flash("Đã thêm ảnh từ nguồn vào bài viết.", "success")
        except Exception as exc:
            flash(f"Không lấy được ảnh: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/images/upload")
    def upload_post_image(post_id):
        file = request.files.get("image")
        try:
            if not file or not file.filename:
                raise ValueError("Chọn một ảnh để tải lên")
            raw = file.stream.read(media.MAX_IMAGE_BYTES + 1)
            media.save_uploaded_post_image(app.config["DATABASE_PATH"], post_id, raw)
            flash("Đã thêm ảnh vào bài viết.", "success")
        except (ValueError, OSError) as exc:
            flash(f"Không thêm được ảnh: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/images/<int:image_id>/remove")
    def remove_post_image(post_id, image_id):
        try:
            database.remove_post_image(app.config["DATABASE_PATH"], post_id, image_id)
            flash("Đã bỏ ảnh khỏi bài viết.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

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
            media.post_image_paths(app.config["DATABASE_PATH"], post_id)
            local_time = datetime.fromisoformat(request.form.get("scheduled_at", ""))
            if local_time.tzinfo is not None:
                raise ValueError("Nhập giờ địa phương không kèm múi giờ")
            utc_time = local_time.replace(tzinfo=BANGKOK).astimezone(timezone.utc)
            if utc_time <= datetime.now(timezone.utc):
                raise ValueError("Giờ đăng phải ở tương lai")
            test_only = request.form.get("test_only") == "yes"
            database.schedule_post(app.config["DATABASE_PATH"], post_id, utc_time.isoformat(), test_only=test_only)
            flash("Đã lên lịch thử nghiệm; bài sẽ không được gửi lên Facebook." if test_only else "Đã lên lịch đăng lên Facebook Page.", "success")
        except (ValueError, media.MissingImageError) as exc:
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

    @app.post("/posts/<int:post_id>/resolve")
    def resolve_post(post_id):
        if request.form.get("checked_page") != "yes":
            flash("Hãy kiểm tra Page trước khi xác nhận kết quả.", "error")
            return redirect(url_for("edit_post", post_id=post_id))
        outcome = request.form.get("outcome")
        if outcome not in {"published", "not_published"}:
            abort(400)
        try:
            database.resolve_uncertain_post(app.config["DATABASE_PATH"], post_id, outcome == "published")
            flash("Đã cập nhật trạng thái sau khi đối chiếu trên Page.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    return app
