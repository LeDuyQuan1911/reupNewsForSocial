import tempfile
import unittest
import re
import os
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image

from app import anthropic, database, facebook, feeds, github, llm, media, queue
from app.web import create_app


RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>AI &amp; tools</title><link>https://example.com/one</link>
<description><![CDATA[<p>A brief <b>summary</b>.</p>]]></description>
<pubDate>Fri, 23 Oct 2026 09:00:00 GMT</pubDate></item>
</channel></rss>"""


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.db_path = Path(self.directory.name) / "test.sqlite3"
        self.client = create_app(self.db_path).test_client()
        page = self.client.get("/").data.decode()
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)

    def tearDown(self):
        self.directory.cleanup()

    def attach_test_image(self, post_id):
        image_path = self.db_path.parent / "media" / f"post-{post_id}.jpg"
        image_path.parent.mkdir(exist_ok=True)
        Image.new("RGB", (64, 32), "green").save(image_path, "JPEG")
        database.attach_image(self.db_path, post_id, image_path.name, "https://example.com/image.jpg")
        return image_path

    def test_rss_parsing_and_deduplication(self):
        articles = feeds.parse_feed(RSS)
        self.assertEqual(articles[0]["title"], "AI & tools")
        self.assertEqual(articles[0]["summary"], "A brief summary .")
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        self.assertEqual(database.save_articles(self.db_path, source_id, articles), 1)
        self.assertEqual(database.save_articles(self.db_path, source_id, articles), 0)
        self.assertEqual(len(database.list_articles(self.db_path)), 1)

    def test_dashboard_and_source_validation(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.post("/sources", data={"name": "bad", "url": "https://example.com"}).status_code, 403)
        self.client.post("/sources", data={"csrf_token": self.csrf, "name": "bad", "url": "file:///etc/passwd"})
        self.assertEqual(len(database.list_sources(self.db_path)), 0)
        self.client.post("/sources", data={"csrf_token": self.csrf, "name": "Example", "url": "https://example.com/rss"})
        self.assertEqual(len(database.list_sources(self.db_path)), 1)

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

    def test_missing_image_prevents_publish(self):
        database.add_source(self.db_path, "Example", "https://example.com/rss")
        source_id = database.list_sources(self.db_path)[0]["id"]
        database.save_articles(self.db_path, source_id, feeds.parse_feed(RSS))
        post_id = database.make_draft(self.db_path, database.list_articles(self.db_path)[0]["id"])
        database.claim_post(self.db_path, post_id)
        with patch("app.queue.llm.check_post") as reviewer, patch("app.queue.facebook.publish_page") as publisher:
            queue.process_claimed_post(self.db_path, post_id)
            reviewer.assert_not_called()
            publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, post_id)["status"], "failed")

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
        with patch("app.media.fetch_public_bytes", side_effect=ValueError("source unavailable")):
            replacement = media.prepare_post_image(self.db_path, post_id)
        self.assertNotEqual(path, replacement)
        self.assertEqual(path.read_bytes(), first_bytes)
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "title_card")
        with Image.open(replacement) as image:
            self.assertEqual(image.size, (1200, 630))

    def test_vision_review_includes_image_and_fails_closed(self):
        image_path = self.db_path.parent / "photo.jpg"
        Image.new("RGB", (640, 320), "red").save(image_path, "JPEG")
        with patch.dict(os.environ, {"REUP_LLM_VISION_MODEL": "vision-test"}), patch(
            "app.llm.request_chat", return_value='{"allowed": false, "reason": "Ảnh không phù hợp"}'
        ) as request_chat:
            self.assertEqual(llm.check_post("Text", image_path.read_bytes()), (False, "Ảnh không phù hợp"))
        messages = request_chat.call_args.args[1]
        self.assertEqual(request_chat.call_args.args[0], "vision-test")
        self.assertTrue(messages[1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,"))

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
        with patch("app.media.screenshot_repository", return_value=output.getvalue()) as screenshot:
            media.prepare_post_image(self.db_path, post_id)
        screenshot.assert_called_once_with("https://github.com/owner/project")
        self.assertEqual(database.get_post(self.db_path, post_id)["image_kind"], "screenshot")

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


if __name__ == "__main__":
    unittest.main()
