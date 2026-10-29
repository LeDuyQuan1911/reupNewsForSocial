import base64
import tempfile
import unittest
import re
import os
import json
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import parse_qs
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

from PIL import Image

from app import anthropic, database, facebook, facebook_groups, feeds, github, llm, media, queue, research, source_content, video
from app.web import create_app


RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>AI &amp; tools</title><link>https://example.com/one</link>
<description><![CDATA[<p>A brief <b>summary</b>.</p>]]></description>
<pubDate>Fri, 23 Oct 2026 09:00:00 GMT</pubDate></item>
</channel></rss>"""
PROCESS_FIRST_COMMENT = queue.process_first_comment


class DashboardTests(unittest.TestCase):
    def setUp(self):
        image_env_patch = patch.dict(os.environ, {"REUP_LLM_IMAGE_MODEL": ""})
        image_env_patch.start()
        self.addCleanup(image_env_patch.stop)
        comment_patch = patch("app.queue.process_first_comment")
        comment_patch.start()
        self.addCleanup(comment_patch.stop)
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.db_path = Path(self.directory.name) / "test.sqlite3"
        self.client = create_app(self.db_path).test_client()
        page = self.client.get("/").data.decode()
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)

    def tearDown(self):
        self.directory.cleanup()

    def test_deployment_pause_blocks_dashboard_but_allows_health_check(self):
        marker = self.db_path.parent / "deployment-paused"
        marker.touch()
        self.assertEqual(self.client.get("/").status_code, 503)
        self.assertEqual(self.client.post("/sources/scan").status_code, 503)
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        marker.unlink()
        self.assertEqual(self.client.get("/").status_code, 200)

    def attach_test_image(self, post_id):
        image_path = self.db_path.parent / "media" / f"post-{post_id}.jpg"
        image_path.parent.mkdir(exist_ok=True)
        Image.new("RGB", (64, 32), "green").save(image_path, "JPEG")
        database.attach_image(self.db_path, post_id, image_path.name, "https://example.com/image.jpg")
        return image_path

    def test_editor_uploads_multiple_images_and_saves_comment(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        files = []
        for color in ("red", "blue"):
            buffer = BytesIO()
            Image.new("RGB", (640, 320), color).save(buffer, "PNG")
            buffer.seek(0)
            files.append((buffer, f"{color}.png"))
        response = self.client.post(f"/posts/{post_id}/images/upload",
                                    data={"csrf_token": self.csrf, "images": files},
                                    content_type="multipart/form-data")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 2)
        response = self.client.post(f"/posts/{post_id}/comment",
                                    data={"csrf_token": self.csrf, "first_comment_body": "💬 Bạn muốn thử tính năng nào?"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(database.get_post(self.db_path, post_id)["first_comment_body"],
                         "💬 Bạn muốn thử tính năng nào?")

    def test_article_video_discovery_uses_embedded_link_and_llm_selection(self):
        html = (b'<meta property="og:title" content="New AI model demo">'
                b'<iframe src="https://www.youtube.com/embed/AbCdEf12345" title="New AI model demo"></iframe>'
                b'<iframe src="https://unrelated.example.com/embed/other"></iframe>')
        with patch("app.video.media.fetch_public_bytes", return_value=(html, "https://example.com/story")), \
             patch("app.video.llm.chat", return_value='{"use":true,"index":0,"reason":"same demo"}') as picker:
            self.assertEqual(video.find_relevant_video("https://example.com/story", "New AI model demo", "Demo details"),
                             "https://www.youtube.com/watch?v=AbCdEf12345")
        self.assertIn("New AI model demo", picker.call_args.args[1])
        with patch("app.video.media.fetch_public_bytes", return_value=(html, "https://example.com/story")), \
             patch("app.video.llm.chat", return_value='{"use":false,"index":0,"reason":"unclear"}'):
            self.assertEqual(video.find_relevant_video("https://example.com/story", "Other", ""), "")

    def test_video_comment_is_sent_once_after_confirmed_publish(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        database.set_post_video(self.db_path, post_id, "https://www.youtube.com/watch?v=AbCdEf12345")
        self.assertIn(video.VIDEO_NOTICE, database.get_post(self.db_path, post_id)["body"])
        self.attach_test_image(post_id)
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", return_value=(True, "OK")), \
             patch("app.queue.facebook.publish_page", return_value="123_456"), \
             patch("app.queue.facebook.comment_video", return_value="comment-1") as commenter:
            queue.process_claimed_post(self.db_path, post_id)
            queue.process_due_posts(self.db_path)
        post = database.get_post(self.db_path, post_id)
        self.assertEqual((post["status"], post["video_comment_status"], post["video_comment_id"]),
                         ("published", "posted", "comment-1"))
        commenter.assert_called_once_with("123_456", "https://www.youtube.com/watch?v=AbCdEf12345")

    def test_first_comment_is_sent_once_after_confirmed_publish(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        database.set_first_comment(self.db_path, post_id, "💬 Bạn thấy điểm nào hữu ích nhất?")
        self.attach_test_image(post_id)
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", return_value=(True, "OK")) as review, \
             patch("app.queue.facebook.publish_page", return_value="123_456"):
            queue.process_claimed_post(self.db_path, post_id)
        self.assertIn("💬 Bạn thấy điểm nào hữu ích nhất?", review.call_args.args[0])
        self.assertEqual(database.get_post(self.db_path, post_id)["first_comment_status"], "pending")
        with patch("app.facebook.comment_page", return_value="comment-1") as commenter:
            PROCESS_FIRST_COMMENT(self.db_path, post_id)
            PROCESS_FIRST_COMMENT(self.db_path, post_id)
        commenter.assert_called_once_with("123_456", "💬 Bạn thấy điểm nào hữu ích nhất?")
        self.assertEqual(database.get_post(self.db_path, post_id)["first_comment_status"], "posted")

    def test_real_schedule_requires_first_comment(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        with database.connect(self.db_path) as db:
            db.execute("UPDATE posts SET first_comment_body = '' WHERE id = ?", (post_id,))
        with self.assertRaisesRegex(ValueError, "bình luận"):
            database.schedule_post(self.db_path, post_id, "2026-10-30T01:00:00+00:00")
        self.assertFalse(database.claim_post(self.db_path, post_id))

    def test_uncertain_first_comment_requires_page_reconciliation(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        with database.connect(self.db_path) as db:
            db.execute("UPDATE posts SET status = 'published', platform_post_id = '123_456', "
                       "first_comment_status = 'pending' WHERE id = ?", (post_id,))
        with patch("app.facebook.comment_page", side_effect=TimeoutError):
            PROCESS_FIRST_COMMENT(self.db_path, post_id)
        self.assertEqual(database.get_post(self.db_path, post_id)["first_comment_status"], "uncertain")
        self.assertIn(post_id, [row["id"] for row in database.list_posts(self.db_path, view="action")])
        self.assertNotIn(post_id, database.pending_first_comment_ids(self.db_path))
        database.resolve_first_comment(self.db_path, post_id, already_posted=False)
        with patch("app.facebook.comment_page", return_value="comment-2") as commenter:
            PROCESS_FIRST_COMMENT(self.db_path, post_id)
        commenter.assert_called_once()
        self.assertEqual(database.get_post(self.db_path, post_id)["first_comment_status"], "posted")

    def test_uncertain_video_comment_does_not_republish_or_retry(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        database.set_post_video(self.db_path, post_id, "https://www.youtube.com/watch?v=AbCdEf12345")
        self.attach_test_image(post_id)
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", return_value=(True, "OK")), \
             patch("app.queue.facebook.publish_page", return_value="123_456") as publisher, \
             patch("app.queue.facebook.comment_video", side_effect=TimeoutError) as commenter:
            queue.process_claimed_post(self.db_path, post_id)
            queue.process_due_posts(self.db_path)
        post = database.get_post(self.db_path, post_id)
        self.assertEqual((post["status"], post["video_comment_status"]), ("published", "uncertain"))
        publisher.assert_called_once()
        commenter.assert_called_once()
        self.assertEqual(database.count_posts(self.db_path, "action"), 1)
        self.client.post(f"/posts/{post_id}/video/resolve", data={"csrf_token": self.csrf, "outcome": "absent"})
        self.assertEqual(database.get_post(self.db_path, post_id)["video_comment_status"], "uncertain")
        with patch("app.queue.facebook.comment_video", return_value="comment-2") as retry:
            self.client.post(f"/posts/{post_id}/video/resolve", data={
                "csrf_token": self.csrf, "checked_page": "yes", "outcome": "absent"})
        retry.assert_called_once()
        self.assertEqual(database.get_post(self.db_path, post_id)["video_comment_status"], "posted")

    def test_facebook_comment_uses_page_token_and_video_link(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_FACEBOOK_PAGE_TOKEN": "test-token",
                    "REUP_META_GRAPH_VERSION": "v26.0"}
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen", return_value=BytesIO(b'{"id":"123_789"}')) as send:
            self.assertEqual(facebook.comment_video("123_456", "https://www.youtube.com/watch?v=AbCdEf12345"), "123_789")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://graph.facebook.com/v26.0/123_456/comments")
        self.assertEqual(parse_qs(request.data.decode())["message"], ["https://www.youtube.com/watch?v=AbCdEf12345"])
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def test_starter_sources_are_added_once_to_existing_database(self):
        database.add_starter_sources(self.db_path)
        names = {source["name"] for source in database.list_sources(self.db_path)}
        self.assertTrue({"NVIDIA Technical Blog", "AWS Machine Learning Blog", "Microsoft Research"} <= names)
        database.add_starter_sources(self.db_path)
        self.assertEqual(len(database.list_sources(self.db_path)), len(database.STARTER_SOURCES))

    def test_existing_sources_gain_scan_state_without_losing_data(self):
        old_path = self.db_path.parent / "old.sqlite3"
        with database.connect(old_path) as db:
            db.execute("CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL UNIQUE, kind TEXT NOT NULL DEFAULT 'rss', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("INSERT INTO sources (name, url) VALUES ('Existing', 'https://example.com/feed')")
        database.initialize(old_path)
        source = database.list_sources(old_path)[0]
        self.assertEqual((source["name"], source["active"]), ("Existing", 1))
        self.assertIsNone(source["last_checked_at"])
        self.assertIsNone(source["last_error"])

    def test_rss_parsing_and_deduplication(self):
        articles = feeds.parse_feed(RSS)
        self.assertEqual(articles[0]["title"], "AI & tools")
        self.assertEqual(articles[0]["summary"], "A brief summary .")
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        self.assertEqual(database.save_articles(self.db_path, source_id, articles), 1)
        self.assertEqual(database.save_articles(self.db_path, source_id, articles), 0)
        self.assertEqual(len(database.list_articles(self.db_path)), 1)

    def test_feed_fetch_rejects_private_targets_and_pins_public_address(self):
        self.assertFalse(feeds.validate_feed_url("http://127.0.0.1/feed"))
        self.assertFalse(feeds.validate_feed_url("http://example.com:8080/feed"))
        private_dns = [(None, None, None, None, ("192.168.1.8", 443))]
        with patch("app.feeds.socket.getaddrinfo", return_value=private_dns):
            with self.assertRaises(ValueError):
                feeds.fetch_feed("https://example.com/rss")
        public_dns = [(None, None, None, None, ("93.184.215.14", 443))]
        with patch("app.feeds.socket.getaddrinfo", return_value=public_dns), \
             patch("app.feeds.PinnedHTTPSConnection") as connection:
            response = connection.return_value.getresponse.return_value
            response.status = 200
            response.read.return_value = RSS
            self.assertEqual(feeds.fetch_feed("https://example.com/rss")[0]["title"], "AI & tools")
            connection.assert_called_once_with("example.com", "93.184.215.14", 443)
        with patch("app.feeds.socket.getaddrinfo", return_value=public_dns), \
             patch("app.feeds.PinnedHTTPSConnection") as connection:
            response = connection.return_value.getresponse.return_value
            response.status = 302
            response.getheader.return_value = "http://127.0.0.1/private"
            with self.assertRaises(ValueError):
                feeds.fetch_feed("https://example.com/rss")

    def test_dashboard_and_source_validation(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.post("/sources", data={"name": "bad", "url": "https://example.com"}).status_code, 403)
        self.client.post("/sources", data={"csrf_token": self.csrf, "name": "bad", "url": "file:///etc/passwd"})
        self.assertEqual(len(database.list_sources(self.db_path)), 0)
        self.client.post("/sources", data={"csrf_token": self.csrf, "name": "Example", "url": "https://example.com/rss"})
        self.assertEqual(len(database.list_sources(self.db_path)), 1)
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        overview = self.client.get("/").get_data(as_text=True)
        self.assertIn("Hoạt động từng ngày", overview)
        self.assertIn('<table class="daily-table">', overview)
        table = overview.split('<table class="daily-table">', 1)[1].split('</table>', 1)[0]
        self.assertEqual(table.count('scope="col"'), 5)
        self.assertEqual(table.count('scope="row"'), 7)
        self.assertEqual(table.count('Tin tìm thấy'), 1)
        self.assertNotIn("Dịch vụ của bạn", overview)
        self.assertNotIn("AI &amp; tools", overview)

    def test_daily_activity_uses_bangkok_dates_and_includes_empty_days(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        article_id = database.list_articles(self.db_path)[0]["id"]
        post_id = database.make_draft(self.db_path, article_id)
        with database.connect(self.db_path) as db:
            db.execute("UPDATE articles SET discovered_at = '2026-10-24 18:30:00' WHERE id = ?", (article_id,))
            db.execute("""UPDATE posts SET created_at = '2026-10-24 18:40:00',
                          published_at = '2026-10-24T19:00:00+00:00', status = 'published'
                          WHERE id = ?""", (post_id,))
            db.execute("""INSERT INTO automation_jobs (article_id, post_id, status, claimed_at)
                          VALUES (?, ?, 'scheduled', '2026-10-24T18:45:00+00:00')""",
                       (article_id, post_id))
        rows = database.daily_activity(self.db_path, now=datetime(2026, 10, 25, 12, tzinfo=timezone.utc))
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]["day"], "2026-10-25")
        self.assertEqual([rows[0][key] for key in ("discovered", "created", "automatic", "published")],
                         [1, 1, 1, 1])
        self.assertEqual([rows[1][key] for key in ("discovered", "created", "automatic", "published")],
                         [0, 0, 0, 0])
        self.assertEqual(len(database.daily_activity(self.db_path, days=30,
                                                     now=datetime(2026, 10, 25, 12, tzinfo=timezone.utc))), 30)

    def test_separate_pages_and_article_filters(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        article_id = database.list_articles(self.db_path)[0]["id"]
        for route, heading in (("/", "Tìm báo / repo mới"), ("/articles", "Bài đã tìm thấy"),
                               ("/sources", "RSS hoặc Atom"), ("/posts", "Tất cả bài đăng"),
                               ("/account", "Facebook Page"),
                               (f"/articles/{article_id}", "AI &amp; tools")):
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, route)
            self.assertIn(heading, response.data.decode(), route)
            self.assertIn('aria-label="Điều hướng chính"', response.data.decode(), route)
            if route in {"/", "/articles", "/sources", "/posts", "/account"}:
                self.assertNotIn('class="page-heading"', response.data.decode(), route)
        self.assertEqual(self.client.get("/articles/99999").status_code, 404)
        self.assertIn("AI &amp; tools", self.client.get("/articles?q=AI&source=" + str(source_id)).data.decode())
        self.assertNotIn("AI &amp; tools", self.client.get("/articles?q=missing").data.decode())
        self.assertEqual(database.count_articles(self.db_path, view="selected"), 0)
        self.assertEqual(database.count_articles(self.db_path, view="unselected"), 1)
        self.assertEqual(self.client.get("/articles?page=999999999999999999999").status_code, 200)
        self.assertEqual(self.client.get("/posts?page=999999999999999999999").status_code, 200)
        response = self.client.post("/sources", data={"csrf_token": self.csrf, "name": "Another", "url": "https://example.org/rss"})
        self.assertEqual(response.location, "/sources")

    def test_publication_workflow_shows_source_destination_and_actual_or_planned_time(self):
        database.add_source(self.db_path, "Example Feed", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [
            {"title": title, "url": f"https://example.com/{index}", "summary": "", "published_at": ""}
            for index, title in enumerate(("No draft", "Scheduled story", "Published story"))
        ])
        articles = {row["title"]: row["id"] for row in database.list_articles(self.db_path)}
        scheduled_id = database.make_draft(self.db_path, articles["Scheduled story"])
        self.attach_test_image(scheduled_id)
        database.schedule_post(self.db_path, scheduled_id, "2026-10-24T03:00:00+00:00")
        published_id = database.make_draft(self.db_path, articles["Published story"])
        self.attach_test_image(published_id)
        self.assertTrue(database.claim_post(self.db_path, published_id))
        database.finish_post(self.db_path, published_id, "published",
                             platform_post_id="page_1", published_at="2026-10-23T10:00:00+00:00")

        rows = {row["article_title"]: row for row in database.list_publication_workflows(
            self.db_path, with_post_only=False
        )}
        self.assertIsNone(rows["No draft"]["post_id"])
        self.assertEqual(rows["Scheduled story"]["post_scheduled_at"], "2026-10-24T03:00:00+00:00")
        self.assertEqual(rows["Published story"]["post_published_at"], "2026-10-23T10:00:00+00:00")
        selected_page = self.client.get("/workflow").data.decode()
        self.assertIn("Đã chọn đăng (2)", selected_page)
        self.assertNotIn("No draft", selected_page)
        self.assertEqual(selected_page.count('scope="col"'), 5)
        self.assertEqual(selected_page.count('scope="row"'), 2)
        page = self.client.get("/workflow?view=all").data.decode()
        for expected in ("Example Feed", "No draft", "Scheduled story", "Published story",
                         "Chưa chọn", "Facebook Page", "Lịch đăng", "24/10/2026 10:00",
                         "Đã đăng", "23/10/2026 17:00"):
            self.assertIn(expected, page)
        self.assertIn('href="/posts/' + str(scheduled_id) + '"', page)
        self.assertIn("Xem để tạo nháp", page)
        self.assertEqual(self.client.get("/workflow?view=all&page=999999999999999999999").status_code, 200)

    def test_literal_search_and_post_pagination(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        articles = [{"title": f"Story {index}", "url": f"https://example.com/{index}",
                     "summary": "", "published_at": ""} for index in range(27)]
        articles[0]["title"] = "100% complete"
        articles[1]["title"] = "1000 users"
        database.save_articles(self.db_path, source_id, articles)
        self.assertEqual([row["title"] for row in database.list_articles(self.db_path, search="100%")],
                         ["100% complete"])
        self.assertEqual(database.count_articles(self.db_path, search="100%"), 1)
        for article in database.list_articles(self.db_path):
            database.make_draft(self.db_path, article["id"])
        self.assertEqual(database.count_posts(self.db_path), 27)
        self.assertEqual(len(database.list_posts(self.db_path, limit=25, offset=25)), 2)
        page = self.client.get("/posts?page=2").data.decode()
        self.assertIn("Trang 2 / 2", page)
        self.assertIn("Story 26", page)
        workflow_page = self.client.get("/workflow?view=all&page=2").data.decode()
        self.assertIn("Trang 2 / 2", workflow_page)
        self.assertIn("100% complete", workflow_page)
        first_id = database.list_articles(self.db_path, search="100%")[0]["id"]
        self.assertIsNotNone(database.get_post_for_article(self.db_path, first_id))
        self.assertEqual(database.count_articles(self.db_path, view="selected"), 27)
        self.assertEqual(database.count_articles(self.db_path, view="unselected"), 0)
        self.assertEqual(self.client.get("/articles?view=selected&page=2").status_code, 200)
        self.assertIn("view=selected", self.client.get("/articles?view=selected&page=2").get_data(as_text=True))

    def test_source_can_be_paused_without_losing_articles(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        response = self.client.post(f"/sources/{source_id}/active",
                                    data={"csrf_token": self.csrf, "active": "0"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(database.list_sources(self.db_path)[0]["active"], 0)
        self.assertEqual(database.overview_counts(self.db_path)["sources"], 0)
        self.assertEqual(database.count_articles(self.db_path), 1)
        with patch("app.discovery.feeds.fetch_feed") as fetch:
            self.client.post("/discover", data={"csrf_token": self.csrf})
            fetch.assert_not_called()
        self.client.post(f"/sources/{source_id}/active", data={"csrf_token": self.csrf, "active": "1"})
        self.assertEqual(database.list_sources(self.db_path)[0]["active"], 1)
        with patch("app.discovery.feeds.fetch_feed", return_value=feeds.parse_feed(RSS)):
            self.client.post("/discover", data={"csrf_token": self.csrf})
        source = database.list_sources(self.db_path)[0]
        self.assertIsNotNone(source["last_checked_at"])
        self.assertIsNone(source["last_error"])
        with patch("app.discovery.feeds.fetch_feed", side_effect=OSError("private detail")):
            self.client.post("/discover", data={"csrf_token": self.csrf})
        source = database.list_sources(self.db_path)[0]
        self.assertEqual(source["last_error"], "Không truy cập được nguồn")
        self.assertEqual(database.overview_counts(self.db_path)["source_errors"], 1)
        self.assertNotIn("private detail", self.client.get("/sources").get_data(as_text=True))
        self.assertEqual(self.client.post(f"/sources/{source_id}/active",
                                          data={"csrf_token": self.csrf, "active": "invalid"}).status_code, 400)

    def test_facebook_group_destinations_validation_and_management(self):
        self.assertIsNone(facebook_groups.normalize_group_url("https://facebook.com.evil.test/groups/123"))
        self.assertIsNone(facebook_groups.normalize_group_url("https://www.facebook.com/groups/123/permalink/456"))
        self.assertEqual(self.client.post("/facebook/groups", data={"name": "No token",
                                  "url": "https://www.facebook.com/groups/123"}).status_code, 403)
        response = self.client.post("/facebook/groups", data={"csrf_token": self.csrf, "name": "AI Việt Nam",
                                    "url": "https://m.facebook.com/groups/123/?ref=share"})
        self.assertEqual(response.status_code, 302)
        group = database.list_facebook_groups(self.db_path)[0]
        self.assertEqual((group["name"], group["url"], group["active"]),
                         ("AI Việt Nam", "https://www.facebook.com/groups/123", 1))
        with patch.dict(os.environ, {"REUP_FACEBOOK_PAGE_TOKEN": ""}):
            page = self.client.get("/facebook").get_data(as_text=True)
        self.assertIn("Đăng nhóm chưa hoạt động", page)
        self.assertIn("AI Việt Nam", page)
        self.assertIn("Chưa kết nối", page)
        self.client.post(f"/facebook/groups/{group['id']}/active",
                         data={"csrf_token": self.csrf, "active": "0"})
        self.assertEqual(database.list_facebook_groups(self.db_path)[0]["active"], 0)
        self.assertEqual(self.client.post("/facebook/groups", data={"csrf_token": self.csrf,
                         "name": "Duplicate", "url": "https://facebook.com/groups/123/"}).status_code, 302)
        self.assertEqual(len(database.list_facebook_groups(self.db_path)), 1)
        self.client.post(f"/facebook/groups/{group['id']}/delete", data={"csrf_token": self.csrf})
        self.assertEqual(database.list_facebook_groups(self.db_path), [])

    def test_post_queue_filters_and_search_preserve_url_state(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [
            {"title": title, "url": f"https://example.com/{index}", "summary": "", "published_at": ""}
            for index, title in enumerate(("100% complete", "1000 users", "Needs review"))
        ])
        ids = {row["title"]: database.make_draft(self.db_path, row["id"])
               for row in database.list_articles(self.db_path)}
        with database.connect(self.db_path) as db:
            db.execute("UPDATE posts SET status = 'blocked', last_error = 'Review' WHERE id = ?",
                       (ids["Needs review"],))
        self.assertEqual(database.count_posts(self.db_path, view="action"), 1)
        self.assertEqual(database.count_posts(self.db_path, search="100%"), 1)
        self.assertEqual(database.list_posts(self.db_path, view="action")[0]["article_title"], "Needs review")
        page = self.client.get("/posts?view=action&q=Needs").get_data(as_text=True)
        self.assertIn("Needs review", page)
        self.assertNotIn("100% complete", page)
        self.assertIn('name="view" value="action"', page)
        self.assertIn('aria-current="page"', page)

    def test_posting_settings_form_and_manual_discovery(self):
        control = self.client.get("/hermes").get_data(as_text=True)
        self.assertIn('name="posts_per_day"', control)
        self.assertEqual(control.count('type="time" name="posting_times" value='), 6)
        self.assertIn('type="time" name="posting_times" value="07:00"', control)
        self.assertNotIn('type="text" name="posting_times"', control)
        self.assertIn('Tìm bài mới', control)
        self.client.post("/account/posting-settings", data={
            "csrf_token": self.csrf, "posts_per_day": "2", "posting_times": ["08:00", "13:15"],
        })
        self.assertEqual(database.get_posting_settings(self.db_path)["times"], ("08:00", "13:15"))
        home = self.client.get("/").get_data(as_text=True)
        self.assertIn("0 / 2", home)
        self.client.post("/account/posting-settings", data={
            "csrf_token": self.csrf, "posts_per_day": "2", "posting_times": ["08:00", "08:10"],
        })
        self.assertEqual(database.get_posting_settings(self.db_path)["times"], ("08:00", "13:15"))
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        database.claim_daily_automation_scan(self.db_path, datetime.now(timezone.utc).isoformat())
        with patch("app.web.discovery.scan_sources", return_value=(1, [])) as scan:
            response = self.client.post("/discover", data={"csrf_token": self.csrf})
        scan.assert_called_once_with(self.db_path)
        self.assertEqual(response.location, "/articles")

    def test_manual_discovery_uses_hermes_web_when_enabled(self):
        with patch.dict(os.environ, {"REUP_HERMES_DISCOVERY_ENABLED": "1"}), \
             patch("app.web.discovery.scan_sources", return_value=(1, [])) as scan, \
             patch("app.web.hermes_research.find_articles", return_value=(2, [])) as web:
            response = self.client.post("/discover", data={"csrf_token": self.csrf})
        self.assertEqual(response.location, "/articles")
        scan.assert_called_once_with(self.db_path)
        web.assert_called_once()
        self.assertEqual(web.call_args.args[2], database.get_posting_settings(self.db_path)["posts_per_day"])

    def test_hermes_controls_require_csrf_and_use_fixed_actions(self):
        with patch("app.web.hermes_control.snapshot", return_value={
            "gateway_running": True, "job_state": "active", "runs": [], "error": None,
        }) as snapshot, patch("app.web.hermes_control.control_job", return_value="Đã tạm dừng") as control:
            page = self.client.get("/hermes")
            self.assertEqual(page.status_code, 200)
            self.assertIn('action="/hermes/pause"', page.get_data(as_text=True))
            snapshot.assert_not_called()
            status = self.client.get("/hermes/status")
            self.assertEqual(status.status_code, 200)
            self.assertEqual(status.json["job_state"], "active")
            snapshot.assert_called_once()
            self.assertEqual(self.client.post("/hermes/pause").status_code, 403)
            response = self.client.post("/hermes/pause", data={"csrf_token": self.csrf})
            self.assertEqual(response.location, "/hermes")
            control.assert_called_once_with(self.db_path.resolve().parent.parent, "pause")

    def test_facebook_page_identity_shows_name_without_token(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123456", "REUP_FACEBOOK_PAGE_TOKEN": "private-test-token",
                    "REUP_META_GRAPH_VERSION": "v26.0", "REUP_FACEBOOK_PAGE_NAME": "Example Page",
                    "REUP_FACEBOOK_PAGE_NAME_ID": "123456"}
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen") as fetch:
            fetch.return_value.__enter__.return_value = BytesIO(b'{"id":"123456","name":"Example Page"}')
            page = self.client.get("/facebook").get_data(as_text=True)
            identity = self.client.get("/facebook/identity").json
        self.assertIn("Page ID: 123456", page)
        self.assertIn("Example Page", page)
        self.assertEqual(identity["name"], "Example Page")
        self.assertTrue(identity["verified"])
        self.assertNotIn("private-test-token", page)
        self.assertNotIn("private-test-token", str(identity))

        with patch.dict(os.environ, settings), patch("app.facebook.urlopen") as fetch:
            fetch.return_value.__enter__.return_value = BytesIO(b'{"id":"999","name":"Other Page"}')
            mismatch = self.client.get("/facebook/identity").json
        self.assertFalse(mismatch["verified"])
        self.assertEqual(mismatch["name"], "")
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen", side_effect=HTTPError(
            "https://graph.facebook.com/", 401, "Unauthorized", {}, None,
        )):
            expired = self.client.get("/facebook/identity").json
        self.assertFalse(expired["verified"])
        self.assertIn("token", expired["error"])
        self.assertNotIn("private-test-token", str(expired))
        graph_error = b'{"error":{"code":190,"error_subcode":463}}'
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen", side_effect=HTTPError(
            "https://graph.facebook.com/", 401, "Unauthorized", {}, BytesIO(graph_error),
        )):
            expired = self.client.get("/facebook/identity").json
        self.assertIn("hết hạn", expired["error"])

    def test_real_schedule_requires_connections_but_test_schedule_does_not(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        future = (datetime.now(timezone.utc) + timedelta(days=2)).astimezone(
            ZoneInfo("Asia/Bangkok")
        ).strftime("%Y-%m-%dT%H:%M")
        with patch.dict(os.environ, {"REUP_FACEBOOK_PAGE_ID": "", "REUP_FACEBOOK_PAGE_TOKEN": "",
                                     "REUP_META_GRAPH_VERSION": "", "REUP_LLM_MODEL": "",
                                     "REUP_LLM_VISION_MODEL": ""}):
            response = self.client.post(f"/posts/{post_id}/schedule",
                                        data={"csrf_token": self.csrf, "scheduled_at": future}, follow_redirects=True)
            self.assertIn("Chưa đủ cấu hình Facebook Page", response.get_data(as_text=True))
            self.assertEqual(database.get_post(self.db_path, post_id)["status"], "draft")
            self.client.post(f"/posts/{post_id}/schedule",
                             data={"csrf_token": self.csrf, "scheduled_at": future, "test_only": "yes"})
        post = database.get_post(self.db_path, post_id)
        self.assertEqual((post["status"], post["test_only"]), ("scheduled", 1))
        database.unschedule_post(self.db_path, post_id)
        with patch.dict(os.environ, {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_FACEBOOK_PAGE_TOKEN": "test-token",
                                     "REUP_META_GRAPH_VERSION": "v99.0", "REUP_LLM_MODEL": "test-text",
                                     "REUP_LLM_VISION_MODEL": "test-vision"}):
            self.client.post(f"/posts/{post_id}/schedule",
                             data={"csrf_token": self.csrf, "scheduled_at": future})
        post = database.get_post(self.db_path, post_id)
        self.assertEqual((post["status"], post["test_only"]), ("scheduled", 0))

    def test_github_repositories_are_normalized(self):
        articles = github.parse_repositories({"items": [
            {"full_name": "owner/project", "html_url": "https://github.com/owner/project", "description": "Example", "stargazers_count": 120, "created_at": "2026-10-01T00:00:00Z"},
            {"full_name": "bad", "html_url": "https://example.com/bad"},
        ]})
        self.assertEqual(len(articles), 1)
        self.assertIn("120 stars", articles[0]["summary"])

    def test_anthropic_sitemap_and_metadata(self):
        sitemap = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://www.anthropic.com/news/example</loc><lastmod>2026-10-23</lastmod></url></urlset>'
        self.assertEqual(anthropic.recent_news_urls(sitemap), ["https://www.anthropic.com/news/example"])
        parser = anthropic.MetadataParser()
        parser.feed('<meta property="og:title" content="Example story"><meta property="og:description" content="An update">')
        self.assertEqual(parser.metadata["og:title"], "Example story")

    def test_test_only_schedule_never_claims_or_publishes(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        database.schedule_post(self.db_path, post_id, "2020-01-01T00:00:00+00:00", test_only=True)
        with patch.object(facebook, "publish_page") as publish:
            self.assertEqual(queue.process_due_posts(self.db_path), 0)
            self.assertFalse(database.claim_post(self.db_path, post_id))
            publish.assert_not_called()
        post = database.get_post(self.db_path, post_id)
        self.assertEqual(post["status"], "scheduled")
        self.assertEqual(post["test_only"], 1)
        page = self.client.get(f"/posts/{post_id}").data.decode()
        self.assertIn("Lịch thử nghiệm · không đăng", page)
        self.assertNotIn("Đăng ngay lên Page", page)

    def test_draft_schedule_and_moderated_publish(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        article_id = database.list_articles(self.db_path)[0]["id"]
        database.make_draft(self.db_path, article_id)
        database.make_draft(self.db_path, article_id)
        post = database.list_posts(self.db_path)[0]
        image_path = self.attach_test_image(post["id"])
        self.assertEqual(self.client.get(f"/posts/{post['id']}").status_code, 200)
        image_response = self.client.get(f"/posts/{post['id']}/image")
        self.assertEqual(image_response.mimetype, "image/jpeg")
        image_response.close()
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        database.schedule_post(self.db_path, post["id"], future)
        database.unschedule_post(self.db_path, post["id"])
        self.assertEqual(database.get_post(self.db_path, post["id"])["status"], "draft")
        database.schedule_post(self.db_path, post["id"], future)
        self.assertEqual(queue.process_due_posts(self.db_path), 0)
        self.assertTrue(database.claim_post(self.db_path, post["id"]))
        with patch("app.queue.llm.check_post", return_value=(False, "Cần xem lại")), patch("app.queue.facebook.publish_page") as publisher:
            queue.process_claimed_post(self.db_path, post["id"])
            publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, post["id"])["status"], "blocked")
        with patch("app.queue.llm.check_post", return_value=(True, "Đạt")), patch("app.queue.facebook.publish_page", return_value="123_456") as publisher:
            self.assertTrue(database.claim_post(self.db_path, post["id"]))
            queue.process_claimed_post(self.db_path, post["id"])
            publisher.assert_called_once_with(post["body"], image_path.read_bytes())
        result = database.get_post(self.db_path, post["id"])
        self.assertEqual(result["status"], "published")
        self.assertEqual(result["platform_post_id"], "123_456")
        self.assertFalse(database.claim_post(self.db_path, post["id"]))

    def test_similar_news_is_blocked_before_publishing(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        articles = [
            {"title": "New AI model released", "url": "https://example.com/one", "summary": "", "published_at": ""},
            {"title": "New AI model released!", "url": "https://example.com/two", "summary": "", "published_at": ""},
        ]
        database.save_articles(self.db_path, source_id, articles)
        for article in database.list_articles(self.db_path):
            database.make_draft(self.db_path, article["id"])
        posts = database.list_posts(self.db_path)
        first, second = posts[0]["id"], posts[1]["id"]
        self.attach_test_image(first)
        self.attach_test_image(second)
        database.claim_post(self.db_path, first)
        database.finish_post(self.db_path, first, "published", platform_post_id="1", published_at=queue.now_utc())
        database.claim_post(self.db_path, second)
        with patch("app.queue.llm.check_post") as reviewer, patch("app.queue.facebook.publish_page") as publisher:
            queue.process_claimed_post(self.db_path, second)
            reviewer.assert_not_called()
            publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, second)["status"], "blocked")

    def test_uncertain_facebook_response_requires_manual_reconciliation(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        post_id = database.list_posts(self.db_path)[0]["id"]
        self.attach_test_image(post_id)
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", return_value=(True, "Đạt")), patch(
            "app.queue.facebook.publish_page", side_effect=TimeoutError("response lost")
        ):
            queue.process_claimed_post(self.db_path, post_id)
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "uncertain")
        self.assertFalse(database.claim_post(self.db_path, post_id))
        response = self.client.post(
            f"/posts/{post_id}/resolve",
            data={"csrf_token": self.csrf, "checked_page": "yes", "outcome": "published"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "published")

    def test_image_extraction_and_page_photo_payload(self):
        feed = b'''<rss xmlns:media="http://search.yahoo.com/mrss/" version="2.0"><channel><item>
        <title>Image story</title><link>https://example.com/story</link>
        <media:content url="https://cdn.example.com/cover.png" type="image/png"/>
        </item></channel></rss>'''
        self.assertEqual(feeds.parse_feed(feed)[0]["image_url"], "https://cdn.example.com/cover.png")
        parser = media.ImageMetadataParser()
        parser.feed('<meta property="og:image" content="/cover.jpg">')
        self.assertEqual(parser.metadata["og:image"], "/cover.jpg")
        image = Image.new("RGB", (640, 320), "blue")
        output = BytesIO()
        image.save(output, "PNG")
        jpeg = media.normalized_jpeg(output.getvalue())
        self.assertTrue(jpeg.startswith(b"\xff\xd8\xff"))
        payload = facebook.photo_request_body("Caption", jpeg, "test-token", "boundary")
        self.assertIn(b'name="source"; filename="post.jpg"', payload)
        self.assertIn(jpeg, payload)
        self.assertIn(b"Caption", payload)

    def test_multiple_images_can_be_added_previewed_and_reviewed(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        first = self.attach_test_image(post_id).read_bytes()
        second_buffer = BytesIO()
        Image.new("RGB", (640, 320), "blue").save(second_buffer, "JPEG")
        second = second_buffer.getvalue()
        media.save_post_image(self.db_path, post_id, second, "", "upload")
        images = database.list_post_images(self.db_path, post_id)
        self.assertEqual(len(images), 2)
        page = self.client.get(f"/posts/{post_id}").data.decode()
        self.assertIn('Ảnh của bài đăng <span class="section-count">2/10</span>', page)
        self.assertIn(f"/posts/{post_id}/images/{images[1]['id']}", page)
        image_response = self.client.get(f"/posts/{post_id}/images/{images[1]['id']}")
        self.assertEqual(image_response.data, second)
        image_response.close()
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", return_value=(True, "OK")) as reviewer, patch(
            "app.queue.facebook.publish_page", return_value="post-2"
        ) as publisher:
            queue.process_claimed_post(self.db_path, post_id)
        self.assertEqual([call.args[1] for call in reviewer.call_args_list], [first, second])
        publisher.assert_called_once_with(database.get_post(self.db_path, post_id)["body"], [first, second])

    def test_upload_and_remove_keeps_at_least_one_image(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        raw = BytesIO()
        Image.new("RGB", (640, 320), "red").save(raw, "PNG")
        response = self.client.post(f"/posts/{post_id}/images/upload", data={
            "csrf_token": self.csrf, "image": (BytesIO(raw.getvalue()), "sample.png")
        }, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        images = database.list_post_images(self.db_path, post_id)
        self.assertEqual(len(images), 2)
        self.assertEqual(images[1]["kind"], "upload")
        self.client.post(f"/posts/{post_id}/images/{images[0]['id']}/remove", data={"csrf_token": self.csrf})
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 1)
        with self.assertRaises(ValueError):
            database.remove_post_image(self.db_path, post_id, images[1]["id"])

    def test_rejected_second_image_blocks_whole_post(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        extra = BytesIO()
        Image.new("RGB", (640, 320), "blue").save(extra, "JPEG")
        media.save_post_image(self.db_path, post_id, extra.getvalue(), "", "upload")
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_post", side_effect=[(True, "OK"), (False, "Ảnh cần xem lại")]) as reviewer, patch(
            "app.queue.facebook.publish_page"
        ) as publisher:
            queue.process_claimed_post(self.db_path, post_id)
        self.assertEqual(reviewer.call_count, 2)
        publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "blocked")

    def test_existing_single_image_is_migrated(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        with database.connect(self.db_path) as db:
            db.execute("DROP TABLE post_images")
        database.initialize(self.db_path)
        images = database.list_post_images(self.db_path, post_id)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["image_file"], f"post-{post_id}.jpg")

    def test_missing_image_prevents_publish(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.assertFalse(database.claim_post(self.db_path, post_id))
        with self.assertRaises(ValueError):
            database.schedule_post(self.db_path, post_id, "2026-10-24T03:00:00+00:00")
        with patch("app.queue.llm.check_post") as reviewer, patch("app.queue.facebook.publish_page") as publisher:
            queue.process_claimed_post(self.db_path, post_id)
            reviewer.assert_not_called()
            publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "draft")

    def test_publishes_exact_image_bytes_reviewed(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        image_path = self.attach_test_image(post_id)
        original = image_path.read_bytes()
        database.claim_post(self.db_path, post_id)

        def change_image_after_review(body, image_bytes):
            self.assertEqual(image_bytes, original)
            Image.new("RGB", (64, 32), "blue").save(image_path, "JPEG")
            return True, "Đạt"

        with patch("app.queue.llm.check_post", side_effect=change_image_after_review), patch(
            "app.queue.facebook.publish_page", return_value="post-1"
        ) as publisher:
            queue.process_claimed_post(self.db_path, post_id)
        publisher.assert_called_once_with(database.get_post(self.db_path, post_id)["body"], original)

    def test_prepare_source_image_and_fallback_card(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "AI launch", "url": "https://example.com/story", "summary": "",
            "published_at": "", "image_url": "https://cdn.example.com/cover.png",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        output = BytesIO()
        Image.new("RGB", (640, 320), "blue").save(output, "PNG")
        with patch("app.media.fetch_public_bytes", return_value=(output.getvalue(), "https://cdn.example.com/cover.png")):
            path = media.prepare_post_image(self.db_path, post_id)
        self.assertTrue(path.is_file())
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "source")
        first_bytes = path.read_bytes()
        with patch.dict(os.environ, {"REUP_LLM_IMAGE_MODEL": ""}), patch("app.media.fetch_public_bytes", side_effect=ValueError("source unavailable")):
            replacement = media.prepare_post_image(self.db_path, post_id)
        self.assertNotEqual(path, replacement)
        self.assertEqual(path.read_bytes(), first_bytes)
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "title_card")
        with Image.open(replacement) as image:
            self.assertEqual(image.size, (1200, 630))

    def test_new_article_prefers_three_distinct_source_images(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "AI launch", "url": "https://example.com/story", "summary": "",
            "published_at": "", "image_url": "https://cdn.example.com/one.png",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        urls = [f"https://cdn.example.com/{name}.png" for name in ("one", "duplicate", "two", "three")]
        colors = {"one": "red", "duplicate": "red", "two": "blue", "three": "green"}

        def fetch_image(url, _limit):
            color = colors[url.rsplit("/", 1)[-1].split(".")[0]]
            output = BytesIO()
            Image.new("RGB", (640, 320), color).save(output, "PNG")
            return output.getvalue(), url

        with patch("app.media.find_article_images", return_value=urls), \
             patch("app.media.fetch_public_bytes", side_effect=fetch_image):
            media.prepare_post_image(self.db_path, post_id)
            with self.assertRaisesRegex(media.MissingImageError, "Không còn ảnh mới"):
                media.prepare_post_image(self.db_path, post_id, append=True)
        images = database.list_post_images(self.db_path, post_id)
        self.assertEqual(len(images), 3)
        self.assertEqual([row["source_url"] for row in images], [urls[0], urls[2], urls[3]])

    def test_missing_source_image_uses_9router_image_model(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "Robot walking", "url": "https://example.com/robot", "summary": "Robot learns to walk",
            "published_at": "", "image_url": "",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        output = BytesIO()
        Image.new("RGB", (800, 450), "blue").save(output, "PNG")
        companion = BytesIO()
        Image.new("RGB", (800, 450), "green").save(companion, "PNG")
        with patch.dict(os.environ, {"REUP_LLM_IMAGE_MODEL": "image-test"}), \
             patch("app.media.find_article_images", side_effect=media.MissingImageError("No image")), \
             patch("app.llm.generate_image", side_effect=[output.getvalue(), companion.getvalue()]) as generate:
            media.prepare_post_image(self.db_path, post_id)
        self.assertEqual(generate.call_count, 2)
        self.assertEqual(generate.call_args_list[1].kwargs, {"variant": 2})
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "router_generated")
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 2)

    def test_one_source_image_gets_ai_companion_automatically(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        url = "https://cdn.example.com/cover.png"
        database.save_articles(self.db_path, source_id, [{
            "title": "Robot walking", "url": "https://example.com/robot", "summary": "Robot learns to walk",
            "published_at": "", "image_url": url,
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        cover = BytesIO()
        Image.new("RGB", (800, 450), "blue").save(cover, "PNG")
        companion = BytesIO()
        Image.new("RGB", (800, 450), "green").save(companion, "PNG")
        with patch.dict(os.environ, {"REUP_LLM_IMAGE_MODEL": "image-test"}), \
             patch("app.media.find_article_images", return_value=[url]), \
             patch("app.media.fetch_public_bytes", return_value=(cover.getvalue(), url)), \
             patch("app.llm.generate_image", return_value=companion.getvalue()) as generate:
            media.prepare_post_image(self.db_path, post_id)
        images = database.list_post_images(self.db_path, post_id)
        self.assertEqual([image["kind"] for image in images], ["source", "router_generated"])
        generate.assert_called_once_with("Robot walking", "Robot learns to walk", variant=2)

    def test_existing_one_image_draft_is_topped_up_without_upload(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        companion = BytesIO()
        Image.new("RGB", (800, 450), "green").save(companion, "PNG")
        with patch.dict(os.environ, {"REUP_LLM_IMAGE_MODEL": "image-test"}), \
             patch("app.media.find_article_images", return_value=[]), \
             patch("app.llm.generate_image", return_value=companion.getvalue()) as generate:
            media.ensure_multiple_images(self.db_path, post_id)
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 2)
        generate.assert_called_once_with("AI & tools", "A brief summary .", variant=2)

    def test_9router_image_generation_uses_local_images_endpoint(self):
        output = BytesIO()
        Image.new("RGB", (640, 360), "blue").save(output, "PNG")
        result = json.dumps({"data": [{"b64_json": base64.b64encode(output.getvalue()).decode()}]}).encode()
        settings = {"REUP_LLM_BASE_URL": "http://127.0.0.1:20128/v1",
                    "REUP_LLM_IMAGE_MODEL": "image-test", "REUP_LLM_API_KEY": "test-only"}
        brief = '{"headline":"Robot","subtitle":"Walking research","steps":["Simulation","Walking"]}'
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.llm.chat", return_value=f"```json\n{brief}\n```") as planner, \
             patch("app.llm.urlopen", return_value=BytesIO(result)) as call:
            generated = llm.generate_image("Robot walking", "Robot learns to walk")
        self.assertEqual(generated, output.getvalue())
        planner.assert_called_once()
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:20128/v1/images/generations")
        self.assertEqual(json.loads(request.data)["model"], "image-test")
        self.assertEqual(json.loads(request.data)["size"], "1792x1024")
        self.assertIn("Simulation; Walking", json.loads(request.data)["prompt"])

    def test_companion_image_uses_distinct_source_grounded_prompt(self):
        output = BytesIO()
        Image.new("RGB", (640, 360), "blue").save(output, "PNG")
        result = json.dumps({"data": [{"b64_json": base64.b64encode(output.getvalue()).decode()}]}).encode()
        settings = {"REUP_LLM_BASE_URL": "http://127.0.0.1:20128/v1",
                    "REUP_LLM_IMAGE_MODEL": "image-test", "REUP_LLM_API_KEY": "test-only"}
        brief = '{"headline":"Robot","subtitle":"Walking research","steps":[]}'
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.llm.chat", return_value=brief), \
             patch("app.llm.urlopen", return_value=BytesIO(result)) as call:
            llm.generate_image("Robot walking", "Robot learns to walk", variant=2)
        prompt = json.loads(call.call_args.args[0].data)["prompt"]
        self.assertIn("companion editorial illustration", prompt)
        self.assertIn("ONE concrete source-grounded", prompt)
        self.assertNotIn("three connected panels", prompt)

    def test_image_generation_rejects_remote_router(self):
        with patch.dict(os.environ, {"REUP_LLM_BASE_URL": "https://example.com/v1",
                                       "REUP_LLM_IMAGE_MODEL": "image-test"}, clear=True):
            with self.assertRaises(ValueError):
                llm.generate_image("Robot walking", "Summary")

    def test_vision_review_includes_image_and_fails_closed(self):
        image_path = self.db_path.parent / "photo.jpg"
        Image.new("RGB", (640, 320), "red").save(image_path, "JPEG")
        with patch.dict(os.environ, {"REUP_LLM_VISION_MODEL": "vision-test"}), patch(
            "app.llm.request_chat", return_value='{"allowed": false, "reason": "Ảnh không phù hợp"}'
        ) as request_chat:
            self.assertEqual(llm.check_post("Text", image_path.read_bytes()), (False, "Ảnh không phù hợp"))
        messages = request_chat.call_args.args[1]
        self.assertEqual(request_chat.call_args.args[0], "vision-test")
        self.assertIn("Ảnh phải thể hiện trực tiếp chủ đề", messages[0]["content"])
        self.assertTrue(messages[1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,"))

    def test_vision_verdict_accepts_json_fence_but_rejects_ambiguous_text(self):
        self.assertEqual(llm.parse_verdict('```json\n{"allowed": true, "reason": "OK"}\n```'), (True, "OK"))
        with self.assertRaises(ValueError):
            llm.parse_verdict('Có thể đăng. {"allowed": true, "reason": "OK"}')

    def test_facebook_photo_endpoint_uses_image_and_caption(self):
        image_path = self.db_path.parent / "photo.jpg"
        Image.new("RGB", (32, 32), "red").save(image_path, "JPEG")
        settings = {
            "REUP_FACEBOOK_PAGE_ID": "123", "REUP_FACEBOOK_PAGE_TOKEN": "test-token",
            "REUP_META_GRAPH_VERSION": "v26.0",
        }
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen", return_value=BytesIO(b'{"id":"photo-1","post_id":"post-1"}')) as send:
            self.assertEqual(facebook.publish_page("A caption", image_path.read_bytes()), "post-1")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://graph.facebook.com/v26.0/123/photos")
        self.assertIn(b"A caption", request.data)
        self.assertIn(b'name="source"', request.data)

    def test_system_user_resolves_page_token_and_never_uses_stale_token(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_META_GRAPH_VERSION": "v26.0",
                    "REUP_FACEBOOK_AUTH_MODE": "system_user",
                    "REUP_FACEBOOK_SYSTEM_USER_TOKEN": "system-secret",
                    "REUP_FACEBOOK_PAGE_TOKEN": "stale-page-secret"}
        pages = b'{"data":[{"id":"123","name":"Example","access_token":"system-page-secret"}]}'
        with patch.dict(os.environ, settings, clear=True), patch("app.facebook.urlopen", side_effect=[
            BytesIO(pages), BytesIO(b'{"id":"photo-1","post_id":"post-1"}')
        ]) as send:
            self.assertEqual(facebook.publish_page("Caption", b"\xff\xd8\xffimage"), "post-1")
        lookup, publish = [call.args[0] for call in send.call_args_list]
        self.assertIn("/me/accounts?", lookup.full_url)
        self.assertEqual(lookup.get_header("Authorization"), "Bearer system-secret")
        self.assertEqual(publish.full_url, "https://graph.facebook.com/v26.0/123/photos")
        self.assertIn(b"system-page-secret", publish.data)
        self.assertNotIn(b"stale-page-secret", publish.data)

        with patch.dict(os.environ, settings, clear=True), patch("app.facebook.urlopen", return_value=BytesIO(b'{"data":[]}')):
            with self.assertRaises(facebook.PageConfigurationError):
                facebook.publish_page("Caption", b"\xff\xd8\xffimage")

    def test_system_user_page_identity_and_comment_use_derived_page_token(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_META_GRAPH_VERSION": "v26.0",
                    "REUP_FACEBOOK_AUTH_MODE": "system_user", "REUP_FACEBOOK_SYSTEM_USER_TOKEN": "system-secret"}
        pages = b'{"data":[{"id":"123","name":"Example","access_token":"derived-page-secret"}]}'
        with patch.dict(os.environ, settings, clear=True), patch("app.facebook.urlopen", side_effect=[
            BytesIO(pages), BytesIO(b'{"id":"123","name":"Example"}')
        ]) as send:
            identity = facebook.page_identity()
        self.assertTrue(identity["verified"])
        self.assertNotIn("derived-page-secret", str(identity))
        self.assertEqual(send.call_args_list[1].args[0].get_header("Authorization"), "Bearer derived-page-secret")

        with patch.dict(os.environ, settings, clear=True), patch("app.facebook.urlopen", side_effect=[
            BytesIO(pages), BytesIO(b'{"id":"comment-1"}')
        ]) as send:
            self.assertEqual(facebook.comment_video("123_456", "https://example.com/video"), "comment-1")
        self.assertEqual(send.call_args_list[1].args[0].get_header("Authorization"), "Bearer derived-page-secret")

    def test_system_user_page_lookup_follows_cursor_without_token_in_url(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_META_GRAPH_VERSION": "v26.0",
                    "REUP_FACEBOOK_AUTH_MODE": "system_user", "REUP_FACEBOOK_SYSTEM_USER_TOKEN": "system-secret"}
        first = b'{"data":[{"id":"999","access_token":"other"}],"paging":{"cursors":{"after":"next"}}}'
        second = b'{"data":[{"id":"123","access_token":"selected"}]}'
        with patch.dict(os.environ, settings, clear=True), patch("app.facebook.urlopen", side_effect=[
            BytesIO(first), BytesIO(second)
        ]) as send:
            self.assertEqual(facebook.page_token("123", "v26.0"), "selected")
        urls = [call.args[0].full_url for call in send.call_args_list]
        self.assertIn("after=next", urls[1])
        self.assertTrue(all("secret" not in url for url in urls))

    def test_facebook_multiple_photos_attach_to_one_feed_post(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_FACEBOOK_PAGE_TOKEN": "test-token",
                    "REUP_META_GRAPH_VERSION": "v26.0"}
        first = b"\xff\xd8\xfffirst"
        second = b"\xff\xd8\xffsecond"
        responses = [BytesIO(b'{"id":"photo-1"}'), BytesIO(b'{"id":"photo-2"}'),
                     BytesIO(b'{"id":"page_post-1"}')]
        with patch.dict(os.environ, settings), patch("app.facebook.urlopen", side_effect=responses) as send:
            self.assertEqual(facebook.publish_page("Caption", [first, second]), "page_post-1")
        requests = [call.args[0] for call in send.call_args_list]
        self.assertEqual([request.full_url.rsplit("/", 1)[-1] for request in requests],
                         ["photos", "photos", "feed"])
        self.assertTrue(all(b'name="published"\r\n\r\nfalse' in request.data for request in requests[:2]))
        self.assertIn(first, requests[0].data)
        self.assertIn(second, requests[1].data)
        form = parse_qs(requests[2].data.decode())
        self.assertEqual(form["message"], ["Caption"])
        self.assertEqual(form["attached_media[0]"], ['{"media_fbid": "photo-1"}'])
        self.assertEqual(form["attached_media[1]"], ['{"media_fbid": "photo-2"}'])

    def test_github_post_uses_repository_screenshot(self):
        with database.connect(self.db_path) as db:
            db.execute("INSERT INTO sources (name, url, kind) VALUES (?, ?, ?)", ("GitHub", "https://github.com/trending", "github"))
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "owner/project", "url": "https://github.com/owner/project", "summary": "",
            "published_at": "", "image_url": "",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        output = BytesIO()
        Image.new("RGB", (1280, 900), "green").save(output, "PNG")
        with patch("app.media.repository_image_urls", return_value=[]), patch("app.media.screenshot_repository", return_value=output.getvalue()) as screenshot:
            media.prepare_post_image(self.db_path, post_id)
            with self.assertRaisesRegex(media.MissingImageError, "Không còn ảnh mới"):
                media.prepare_post_image(self.db_path, post_id, append=True)
        self.assertEqual(screenshot.call_count, 2)
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 1)
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "screenshot")

    def test_github_post_prefers_image_in_repository_readme(self):
        with database.connect(self.db_path) as db:
            db.execute("INSERT INTO sources (name, url, kind) VALUES (?, ?, ?)", ("GitHub", "https://github.com/trending", "github"))
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "owner/project", "url": "https://github.com/owner/project", "summary": "",
            "published_at": "", "image_url": "",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        output = BytesIO()
        Image.new("RGB", (800, 450), "blue").save(output, "PNG")
        readme_image = "https://raw.githubusercontent.com/owner/project/main/demo.png"
        screenshot_image = BytesIO()
        Image.new("RGB", (1280, 900), "green").save(screenshot_image, "PNG")
        with patch("app.media.repository_image_urls", return_value=[readme_image]), \
             patch("app.media.fetch_public_bytes", return_value=(output.getvalue(), readme_image)), \
             patch("app.media.screenshot_repository", return_value=screenshot_image.getvalue()) as screenshot:
            media.prepare_post_image(self.db_path, post_id)
        post = database.get_post(self.db_path, post_id)
        self.assertEqual(post["image_kind"], "repo_asset")
        self.assertEqual(post["image_source_url"], readme_image)
        screenshot.assert_called_once()
        self.assertEqual(len(database.list_post_images(self.db_path, post_id)), 2)

    def test_repository_readme_image_urls_resolve_relative_paths_and_skip_badges(self):
        readme = "![Build](https://example.com/badge.svg)\n![Demo](assets/demo.png)\n<img src='images/flow.jpg'>"
        document = json.dumps({
            "download_url": "https://raw.githubusercontent.com/owner/project/main/README.md",
            "content": base64.b64encode(readme.encode()).decode(),
        }).encode()
        with patch("app.media.fetch_public_bytes", return_value=(document, "https://api.github.com/repos/owner/project/readme")):
            urls = media.repository_image_urls("https://github.com/owner/project")
        self.assertEqual(urls, [
            "https://raw.githubusercontent.com/owner/project/main/assets/demo.png",
            "https://raw.githubusercontent.com/owner/project/main/images/flow.jpg",
        ])

    def test_repository_images_prioritize_demo_over_decorative_cover(self):
        readme = "![Cover](assets/cover.png)\n![App screenshot](assets/app.png)\n![Logo](logo.png)"
        document = json.dumps({
            "download_url": "https://raw.githubusercontent.com/owner/project/main/README.md",
            "content": base64.b64encode(readme.encode()).decode(),
        }).encode()
        with patch("app.media.fetch_public_bytes", return_value=(document, "https://api.github.com/repos/owner/project/readme")):
            urls = media.repository_image_urls("https://github.com/owner/project")
        self.assertEqual(urls, [
            "https://raw.githubusercontent.com/owner/project/main/assets/app.png",
            "https://raw.githubusercontent.com/owner/project/main/assets/cover.png",
        ])

    def test_draft_uses_article_body_and_falls_back_when_source_unavailable(self):
        html = (b"<main><nav>Unrelated menu</nav><article>"
                b"<h1>A robot walks</h1><p>The robot walks on uneven ground using its new controller.</p>"
                b"<p>Researchers shared a video showing the robot recovering its balance.</p>"
                b"</article></main>")
        with patch("app.source_content.fetch_public_bytes", return_value=(html, "https://example.com/story")):
            excerpt = source_content.source_excerpt("https://example.com/story", "rss")
        self.assertIn("uneven ground", excerpt)
        self.assertNotIn("Unrelated menu", excerpt)
        with patch("app.source_content.source_excerpt", return_value=excerpt), patch("app.hermes_writer.write_with_hermes", return_value="Bản nháp 💡") as writer:
            llm.write_draft("Robot", "Short summary", "https://example.com/story")
        self.assertIn("uneven ground", writer.call_args.args[0])
        with patch("app.source_content.source_excerpt", side_effect=ValueError("unavailable")), patch("app.hermes_writer.write_with_hermes", return_value="Bản nháp 💡") as writer:
            llm.write_draft("Robot", "Short summary", "https://example.com/story")
        self.assertIn("chỉ dùng tiêu đề và tóm tắt", writer.call_args.args[0])

    def test_github_draft_reads_readme_without_image_markup(self):
        readme = "# Tool\n![Demo](demo.png)\nRuns a local editor and exports real files."
        document = json.dumps({
            "download_url": "https://raw.githubusercontent.com/owner/project/main/README.md",
            "content": base64.b64encode(readme.encode()).decode(),
        }).encode()
        with patch("app.source_content.fetch_public_bytes", return_value=(document, "https://api.github.com/repos/owner/project/readme")):
            excerpt = source_content.source_excerpt("https://github.com/owner/project", "github")
        self.assertIn("exports real files", excerpt)
        self.assertNotIn("demo.png", excerpt)

    def test_draft_retries_without_emoji_and_removes_duplicate_source_link(self):
        url = "https://example.com/story"
        with patch("app.source_content.source_excerpt", return_value="Grounded article detail"), patch(
            "app.hermes_writer.write_with_hermes", side_effect=["Bài đầu không có icon", f"💡 Bài viết đã có icon\n\n{url}"]
        ) as writer:
            draft = llm.write_draft("Story", "Summary", url)
        self.assertEqual(writer.call_count, 2)
        self.assertIn("💡", draft)
        self.assertEqual(draft.count(url), 1)
        with patch("app.source_content.source_excerpt", return_value=""), patch(
            "app.hermes_writer.write_with_hermes", return_value="Không có icon"
        ):
            with self.assertRaisesRegex(ValueError, "icon phù hợp"):
                llm.write_draft("Story", "Summary", url)

    def test_article_tries_other_images_after_unusable_cover(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{
            "title": "Robot walking", "url": "https://example.com/robot", "summary": "",
            "published_at": "", "image_url": "https://cdn.example.com/logo.png",
        }])
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        output = BytesIO()
        Image.new("RGB", (800, 450), "blue").save(output, "PNG")
        article_image = "https://cdn.example.com/robot.jpg"
        def fetch(url, limit):
            if url.endswith("logo.png"):
                tiny = BytesIO()
                Image.new("RGB", (80, 80), "red").save(tiny, "PNG")
                return tiny.getvalue(), url
            return output.getvalue(), url
        with patch("app.media.find_article_images", return_value=[article_image]), \
             patch("app.media.fetch_public_bytes", side_effect=fetch):
            media.prepare_post_image(self.db_path, post_id)
        self.assertEqual(database.get_post(self.db_path, post_id)["image_source_url"], article_image)

    def test_image_fetch_rejects_private_network(self):
        with self.assertRaises(ValueError):
            media.validate_public_url("https://127.0.0.1/private.jpg")

    def test_image_fetch_connects_to_vetted_ip(self):
        with patch("app.media.validate_public_url", return_value="8.8.8.8"), patch("app.media.PinnedHTTPSConnection") as pinned:
            response = pinned.return_value.getresponse.return_value
            response.status = 200
            response.read.return_value = b"image"
            self.assertEqual(media.fetch_public_bytes("https://cdn.example.com/a.jpg", 10)[0], b"image")
        pinned.assert_called_once_with("cdn.example.com", "8.8.8.8")

    def test_image_preview_with_relative_database_path(self):
        relative_db = self.db_path.relative_to(Path.cwd())
        database.add_source(relative_db, "Example", "https://example.com/rss")
        source_id = database.list_sources(relative_db)[0]["id"]
        database.save_articles(relative_db, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(relative_db, database.list_articles(relative_db)[0]["id"])
        self.attach_test_image(post_id)
        app = create_app(relative_db)
        response = app.test_client().get(f"/posts/{post_id}/image")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/jpeg")
        response.close()

    def test_research_ranks_sources_and_persists_result(self):
        now = datetime.now(timezone.utc)
        with database.connect(self.db_path) as db:
            db.execute("INSERT INTO automation_state (id, baseline_article_id) VALUES (1, 0)")
        for source_index in range(3):
            database.add_source(self.db_path, f"Source {source_index}", f"https://example.com/{source_index}")
        for source in database.list_sources(self.db_path):
            database.save_articles(self.db_path, source["id"], [
                {"title": f"News {source['id']}-{index}",
                 "url": f"https://example.com/story/{source['id']}/{index}",
                 "summary": "An engineering update", "published_at": now.isoformat(), "image_url": ""}
                for index in range(4)])
        candidates = database.list_research_candidates(self.db_path, (now - timedelta(hours=48)).isoformat())
        first_source_ids = [row["id"] for row in candidates if row["source_id"] == candidates[0]["source_id"]]
        response = {"picks": [{"id": article_id, "reason": "Tin kỹ thuật mới"}
                              for article_id in first_source_ids]}
        with patch("app.research.llm.chat", return_value=json.dumps(response)) as model:
            self.assertEqual(research.review_candidates(self.db_path, now)["reviewed"], 12)
            self.assertEqual(research.review_candidates(self.db_path, now)["reviewed"], 0)
        model.assert_called_once()
        ranked = database.list_articles(self.db_path, view="reviewed")
        self.assertEqual(len({row["source_id"] for row in ranked[:6]}), 3)
        self.assertTrue(any(row["research_method"] == "ai" for row in ranked))
        self.assertIn("Tin kỹ thuật mới", self.client.get(f"/articles/{first_source_ids[0]}").data.decode())
        day_start = now.replace(hour=0, minute=0, second=0).isoformat()
        day_end = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
        claimed_sources = []
        for _ in range(6):
            claimed = database.claim_automation_article(self.db_path, now.isoformat(), day_start,
                day_end, (now - timedelta(hours=48)).isoformat(), 6)
            claimed_sources.append(claimed["source_id"])
        self.assertEqual(sorted(claimed_sources.count(source["id"]) for source in database.list_sources(self.db_path)), [2, 2, 2])

    def test_research_falls_back_on_invalid_model_response(self):
        now = datetime.now(timezone.utc)
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, [{"title": "News", "url": "https://example.com/new",
            "summary": "Summary", "published_at": now.isoformat(), "image_url": ""}])
        with database.connect(self.db_path) as db:
            db.execute("INSERT INTO automation_state (id, baseline_article_id) VALUES (1, 0)")
        with patch("app.research.llm.chat", return_value='{"picks":[{"id":99999,"reason":"x"}]}'):
            self.assertEqual(research.review_candidates(self.db_path, now)["method"], "fallback")
        review = database.get_research_review(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.assertEqual(review["method"], "fallback")

    def test_stalled_publishing_requires_wait_and_page_reconciliation(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        self.attach_test_image(post_id)
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with self.assertRaises(ValueError):
            database.mark_stalled_post_uncertain(self.db_path, post_id)
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "publishing")
        with database.connect(self.db_path) as db:
            db.execute("UPDATE posts SET publishing_started_at = ? WHERE id = ?",
                       ((datetime.now(timezone.utc) - timedelta(minutes=46)).isoformat(), post_id))
        response = self.client.get(f"/posts/{post_id}")
        self.assertIn("Đối chiếu bài bị kẹt", response.data.decode())
        self.assertEqual(database.count_posts(self.db_path, "action"), 1)
        self.client.post(f"/posts/{post_id}/reconcile", data={"csrf_token": self.csrf})
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "uncertain")
        self.client.post(f"/posts/{post_id}/resolve", data={"csrf_token": self.csrf,
            "outcome": "not_published", "checked_page": "yes"})
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "draft")


if __name__ == "__main__":
    unittest.main()
