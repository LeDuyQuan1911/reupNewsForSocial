import os
import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, send_file, session, url_for

from . import automation, database, discovery, facebook, facebook_groups, feeds, hermes_control, llm, media, queue, video


BANGKOK = ZoneInfo("Asia/Bangkok")


def create_app(database_path: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("REUP_SECRET_KEY") or secrets.token_hex(32)
    app.config["DATABASE_PATH"] = database_path or Path("data/reup.sqlite3")
    database.initialize(app.config["DATABASE_PATH"])
    if database_path is None:
        database.add_starter_sources(app.config["DATABASE_PATH"])

    @app.before_request
    def block_during_deployment():
        if request.path != "/healthz" and (app.config["DATABASE_PATH"].parent / "deployment-paused").exists():
            return "Đang cập nhật, vui lòng thử lại sau.", 503

    @app.get("/healthz")
    def healthz():
        connection = sqlite3.connect(app.config["DATABASE_PATH"])
        try:
            connection.execute("SELECT 1").fetchone()
        finally:
            connection.close()
        return {"status": "ok"}

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

    def connection_flags():
        return {
            "page": automation.page_ready(),
            "llm": bool(os.environ.get("REUP_LLM_MODEL")),
            "vision": bool(os.environ.get("REUP_LLM_VISION_MODEL")),
            "image": bool(os.environ.get("REUP_LLM_IMAGE_MODEL")),
        }

    @app.get("/")
    def dashboard():
        days = 30 if request.args.get("days") == "30" else 7
        posting_settings = database.get_posting_settings(app.config["DATABASE_PATH"])
        activity = database.daily_activity(app.config["DATABASE_PATH"], days=days)
        chart_activity = list(reversed(activity[:7]))
        return render_template(
            "dashboard.html",
            counts=database.overview_counts(app.config["DATABASE_PATH"]),
            activity=activity,
            chart_activity=chart_activity,
            chart_max=max([posting_settings["posts_per_day"], *(item["created"] for item in chart_activity)]),
            posting_settings=posting_settings,
            selected_days=days,
            automation_status=database.automation_status(app.config["DATABASE_PATH"]),
            automation_enabled=automation.enabled(),
        )

    @app.get("/articles")
    def articles_page():
        source_value = request.args.get("source", "")
        source_id = int(source_value) if source_value.isdecimal() else None
        search = request.args.get("q", "").strip()[:100]
        selected_view = request.args.get("view", "all")
        if selected_view not in {"all", "unselected", "selected", "reviewed"}:
            selected_view = "all"
        page_size = 25
        total = database.count_articles(app.config["DATABASE_PATH"], source_id, search, selected_view)
        page_value = request.args.get("page", "1")
        requested_page = int(page_value) if page_value.isdecimal() and len(page_value) <= 10 else 1
        page = min(max(1, requested_page), max(1, (total + page_size - 1) // page_size))
        articles = database.list_articles(app.config["DATABASE_PATH"], limit=page_size,
                                          source_id=source_id, search=search, offset=(page - 1) * page_size,
                                          view=selected_view)
        return render_template(
            "articles.html",
            articles=articles,
            sources=database.list_sources(app.config["DATABASE_PATH"]),
            posted_articles=database.drafted_article_ids(app.config["DATABASE_PATH"],
                                                         [article["id"] for article in articles]),
            selected_source=source_id,
            selected_view=selected_view,
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
        return render_template("article.html", article=article, source=source, post=post,
                               review=database.get_research_review(app.config["DATABASE_PATH"], article_id))

    @app.get("/sources")
    def sources_page():
        sources = database.list_sources(app.config["DATABASE_PATH"])
        return render_template("sources.html", sources=sources,
                               active_count=sum(source["active"] for source in sources))

    @app.get("/posts")
    def posts_page():
        page_size = 25
        selected_view = request.args.get("view", "all")
        if selected_view not in database.POST_VIEWS:
            selected_view = "all"
        search = request.args.get("q", "").strip()[:100]
        total = database.count_posts(app.config["DATABASE_PATH"], selected_view, search)
        page_value = request.args.get("page", "1")
        requested_page = int(page_value) if page_value.isdecimal() and len(page_value) <= 10 else 1
        page = min(max(1, requested_page), max(1, (total + page_size - 1) // page_size))
        return render_template("posts.html", posts=database.list_posts(
            app.config["DATABASE_PATH"], limit=page_size, offset=(page - 1) * page_size,
            view=selected_view, search=search
        ), page=page, total=total, page_size=page_size, selected_view=selected_view, search=search,
            view_counts={view: database.count_posts(app.config["DATABASE_PATH"], view)
                         for view in database.POST_VIEWS})

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
                               article_total=article_total, post_total=post_total,
                               page_ready=automation.page_ready())

    @app.get("/account")
    def account_page():
        data_dir = app.config["DATABASE_PATH"].parent
        posting_settings = database.get_posting_settings(app.config["DATABASE_PATH"])
        hermes_owner = (data_dir / "hermes-automation.enabled").exists()
        hermes_cycle = None
        if hermes_owner:
            try:
                hermes_cycle = json.loads((data_dir / "hermes-last-cycle.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
        return render_template("account.html", automation_status=database.automation_status(app.config["DATABASE_PATH"]),
                               automation_enabled=automation.enabled(), connections=connection_flags(),
                               facebook_auth_mode=facebook.auth_mode(),
                               hermes_owner=hermes_owner, hermes_cycle=hermes_cycle,
                               posting_settings=posting_settings)

    @app.get("/hermes")
    def hermes_page():
        root = app.config["DATABASE_PATH"].resolve().parent.parent
        cycle = None
        try:
            cycle = json.loads((root / "data" / "hermes-last-cycle.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        return render_template(
            "hermes.html", cycle=cycle,
            posting_settings=database.get_posting_settings(app.config["DATABASE_PATH"]),
            automation_status=database.automation_status(app.config["DATABASE_PATH"]),
        )

    @app.get("/hermes/status")
    def hermes_status():
        root = app.config["DATABASE_PATH"].resolve().parent.parent
        return jsonify(hermes_control.snapshot(root))

    @app.post("/hermes/<action>")
    def hermes_action(action):
        try:
            message = hermes_control.control_job(app.config["DATABASE_PATH"].resolve().parent.parent, action)
            flash(message, "success")
        except hermes_control.HermesControlError as exc:
            flash(str(exc), "error")
        return redirect(url_for("hermes_page"))

    @app.post("/account/posting-settings")
    def update_posting_settings():
        try:
            settings = database.save_posting_settings(
                app.config["DATABASE_PATH"],
                request.form.get("posts_per_day", ""),
                ", ".join(request.form.getlist("posting_times")),
            )
        except ValueError as exc:
            flash(str(exc), "error")
        else:
            flash(f"Đã lưu {settings['posts_per_day']} bài tự động/ngày. Lịch đã xếp trước đó giữ nguyên.", "success")
        return redirect(url_for("hermes_page"))

    @app.get("/facebook")
    def facebook_page():
        groups = database.list_facebook_groups(app.config["DATABASE_PATH"])
        configured_id = os.environ.get("REUP_FACEBOOK_PAGE_ID", "").strip()
        saved_name = os.environ.get("REUP_FACEBOOK_PAGE_NAME", "").strip()
        saved_id = os.environ.get("REUP_FACEBOOK_PAGE_NAME_ID", "").strip()
        return render_template("facebook.html", groups=groups,
                               selected_count=sum(group["active"] for group in groups),
                               page_ready=automation.page_ready(),
                               config_auth_mode=facebook.auth_mode(),
                               configured_page_id=configured_id if configured_id.isdecimal() else "",
                               configured_page_name=saved_name[:200] if saved_id == configured_id else "")

    @app.get("/facebook/identity")
    def facebook_identity():
        return jsonify(facebook.page_identity())

    @app.post("/facebook/groups")
    def add_facebook_group():
        name = request.form.get("name", "").strip()
        url = facebook_groups.normalize_group_url(request.form.get("url", ""))
        if not name or len(name) > 100 or url is None:
            flash("Nhập tên và URL nhóm Facebook hợp lệ dạng https://www.facebook.com/groups/...", "error")
        else:
            try:
                database.add_facebook_group(app.config["DATABASE_PATH"], name, url)
                flash("Đã thêm nhóm vào danh sách đích.", "success")
            except sqlite3.IntegrityError:
                flash("Nhóm này đã có trong danh sách.", "error")
        return redirect(url_for("facebook_page"))

    @app.post("/facebook/groups/<int:group_id>/active")
    def toggle_facebook_group(group_id):
        active = request.form.get("active")
        if active not in {"0", "1"}:
            abort(400)
        try:
            database.set_facebook_group_active(app.config["DATABASE_PATH"], group_id, active == "1")
            flash("Đã chọn nhóm." if active == "1" else "Đã tạm dừng nhóm.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("facebook_page"))

    @app.post("/facebook/groups/<int:group_id>/delete")
    def remove_facebook_group(group_id):
        try:
            database.delete_facebook_group(app.config["DATABASE_PATH"], group_id)
            flash("Đã xóa nhóm khỏi danh sách đích.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("facebook_page"))

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

    @app.post("/sources/<int:source_id>/active")
    def toggle_source(source_id):
        active = request.form.get("active")
        if active not in {"0", "1"}:
            abort(400)
        try:
            database.set_source_active(app.config["DATABASE_PATH"], source_id, active == "1")
            flash("Đã bật lại nguồn tin." if active == "1" else "Đã tạm dừng nguồn tin; bài cũ vẫn được giữ.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("sources_page"))

    @app.post("/discover")
    def discover():
        added, errors = discovery.scan_sources(app.config["DATABASE_PATH"])
        flash(f"Đã tìm thấy {added} bài báo/repo mới.", "success")
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
                image_count = len(database.list_post_images(app.config["DATABASE_PATH"], post_id))
                flash(f"Đã tạo bản nháp và lưu {image_count} ảnh minh họa.", "success")
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
        return render_template("post.html", post=post, images=images, has_image=has_image,
                               page_ready=automation.page_ready(), models_ready=automation.models_ready(),
                               can_reconcile=bool(post["publishing_started_at"] and
                                   datetime.fromisoformat(post["publishing_started_at"]) <=
                                   datetime.now(timezone.utc) - timedelta(minutes=45)))

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
        files = [file for file in request.files.getlist("images") if file.filename]
        if not files:
            files = [file for file in request.files.getlist("image") if file.filename]
        try:
            if not files:
                raise ValueError("Chọn ít nhất một ảnh để tải lên")
            remaining = 10 - len(database.list_post_images(app.config["DATABASE_PATH"], post_id))
            if len(files) > remaining:
                raise ValueError(f"Chỉ thêm được tối đa {remaining} ảnh nữa")
            prepared_images = []
            for file in files:
                raw = file.stream.read(media.MAX_IMAGE_BYTES + 1)
                if not raw or len(raw) > media.MAX_IMAGE_BYTES:
                    raise ValueError("Mỗi ảnh phải có dữ liệu và không quá 8 MB")
                prepared_images.append(media.normalized_jpeg(raw))
            for image in prepared_images:
                media.save_post_image(app.config["DATABASE_PATH"], post_id, image, "", "upload")
            flash(f"Đã thêm {len(files)} ảnh vào bài viết.", "success")
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

    @app.post("/posts/<int:post_id>/comment")
    def save_first_comment(post_id):
        try:
            database.set_first_comment(app.config["DATABASE_PATH"], post_id,
                                       request.form.get("first_comment_body", ""))
            flash("Đã lưu bình luận đầu tiên.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/comment/resolve")
    def resolve_first_comment(post_id):
        if request.form.get("checked_page") != "yes":
            flash("Hãy kiểm tra bình luận trên Facebook Page trước.", "error")
            return redirect(url_for("edit_post", post_id=post_id))
        outcome = request.form.get("outcome")
        if outcome not in {"posted", "absent"}:
            abort(400)
        try:
            database.resolve_first_comment(app.config["DATABASE_PATH"], post_id, outcome == "posted")
            if outcome == "absent":
                queue.process_first_comment(app.config["DATABASE_PATH"], post_id)
            current = database.get_post(app.config["DATABASE_PATH"], post_id)
            flash("Đã cập nhật trạng thái bình luận." if current["first_comment_status"] == "posted"
                  else "Chưa xác nhận được bình luận mới; hãy kiểm tra Page.",
                  "success" if current["first_comment_status"] == "posted" else "error")
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
            body = llm.write_draft(post["article_title"], post["article_summary"], post["article_url"], post["source_kind"])
            comment = llm.write_first_comment(post["article_title"], post["article_summary"], post["article_url"], body)
            database.update_draft(app.config["DATABASE_PATH"], post_id, body)
            database.set_first_comment(app.config["DATABASE_PATH"], post_id, comment)
            flash("Hermes đã viết bản nháp và chuẩn bị bình luận. Hãy đọc lại trước khi đăng.", "success")
        except Exception as exc:
            flash(f"Không tạo được bài: {exc}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/video/detect")
    def detect_post_video(post_id):
        post = database.get_post(app.config["DATABASE_PATH"], post_id)
        if post is None:
            abort(404)
        if post["status"] not in {"draft", "blocked", "failed"} or post["source_kind"] == "github":
            flash("Chỉ tìm video cho bản nháp bài báo.", "error")
        else:
            try:
                found = video.find_relevant_video(post["article_url"], post["article_title"], post["article_summary"] or "")
                if found:
                    database.set_post_video(app.config["DATABASE_PATH"], post_id, found)
                    flash("Đã thêm video phù hợp và dòng chỉ dẫn vào bản nháp.", "success")
                else:
                    flash("Không tìm được video đủ rõ ràng và phù hợp trong bài báo.", "error")
            except Exception as exc:
                flash(f"Không kiểm tra được video: {type(exc).__name__}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/video")
    def save_post_video(post_id):
        url = request.form.get("video_url", "").strip()
        try:
            if url:
                media.validate_public_url(url)
            database.set_post_video(app.config["DATABASE_PATH"], post_id, url)
            flash("Đã cập nhật video và nội dung bản nháp.", "success")
        except (OSError, ValueError) as exc:
            flash(f"URL video không hợp lệ: {type(exc).__name__}", "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/video/resolve")
    def resolve_post_video(post_id):
        if request.form.get("checked_page") != "yes":
            flash("Hãy kiểm tra bình luận trên Facebook Page trước.", "error")
            return redirect(url_for("edit_post", post_id=post_id))
        outcome = request.form.get("outcome")
        if outcome not in {"posted", "absent"}:
            abort(400)
        try:
            database.resolve_video_comment(app.config["DATABASE_PATH"], post_id, outcome == "posted")
            if outcome == "absent":
                queue.process_video_comment(app.config["DATABASE_PATH"], post_id)
            current = database.get_post(app.config["DATABASE_PATH"], post_id)
            flash("Đã cập nhật trạng thái bình luận video." if current["video_comment_status"] == "posted"
                  else "Chưa xác nhận được bình luận mới; hãy kiểm tra Page.",
                  "success" if current["video_comment_status"] == "posted" else "error")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    @app.post("/posts/<int:post_id>/schedule")
    def schedule_post(post_id):
        try:
            test_only = request.form.get("test_only") == "yes"
            if not test_only and not automation.page_ready():
                raise ValueError("Chưa đủ cấu hình Facebook Page. Hãy dùng lịch thử nghiệm hoặc cấu hình Page trước")
            if not test_only and not automation.models_ready():
                raise ValueError("Chưa đủ model viết bài và duyệt ảnh. Hãy dùng lịch thử nghiệm hoặc cấu hình AI trước")
            if not test_only:
                try:
                    media.ensure_multiple_images(app.config["DATABASE_PATH"], post_id)
                except media.MissingImageError:
                    pass
            if test_only:
                media.post_image_paths(app.config["DATABASE_PATH"], post_id)
            else:
                media.publishable_post_image_paths(app.config["DATABASE_PATH"], post_id)
            local_time = datetime.fromisoformat(request.form.get("scheduled_at", ""))
            if local_time.tzinfo is not None:
                raise ValueError("Nhập giờ địa phương không kèm múi giờ")
            utc_time = local_time.replace(tzinfo=BANGKOK).astimezone(timezone.utc)
            if utc_time <= datetime.now(timezone.utc):
                raise ValueError("Giờ đăng phải ở tương lai")
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
        if not automation.page_ready():
            flash("Chưa đủ cấu hình Facebook Page. Kiểm tra Tài khoản trước khi đăng.", "error")
        elif not automation.models_ready():
            flash("Chưa đủ model viết bài và duyệt ảnh. Kiểm tra Tài khoản trước khi đăng.", "error")
        else:
            try:
                media.ensure_multiple_images(app.config["DATABASE_PATH"], post_id)
            except media.MissingImageError:
                pass
            if not database.claim_post(app.config["DATABASE_PATH"], post_id):
                flash("Bài không ở trạng thái có thể đăng.", "error")
            else:
                queue.process_claimed_post(app.config["DATABASE_PATH"], post_id)
                post = database.get_post(app.config["DATABASE_PATH"], post_id)
                if post["status"] == "published" and post["first_comment_status"] == "posted":
                    flash("Đã đăng bài và bình luận đầu tiên lên Facebook Page.", "success")
                elif post["status"] == "published":
                    flash("Bài đã đăng, nhưng bình luận chưa được xác nhận. Hãy kiểm tra trên Page.", "error")
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

    @app.post("/posts/<int:post_id>/reconcile")
    def reconcile_stalled_post(post_id):
        try:
            database.mark_stalled_post_uncertain(app.config["DATABASE_PATH"], post_id)
            flash("Đã chuyển bài sang bước đối chiếu. Kiểm tra Facebook Page trước khi xác nhận kết quả.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("edit_post", post_id=post_id))

    return app
