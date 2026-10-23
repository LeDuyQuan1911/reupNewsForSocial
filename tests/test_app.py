import tempfile
import unittest
import re
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from app import anthropic, database, feeds, github, queue
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
        self.assertEqual(self.client.get(f"/posts/{post['id']}").status_code, 200)
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        database.schedule_post(self.db_path, post["id"], future)
        database.unschedule_post(self.db_path, post["id"])
        self.assertEqual(database.get_post(self.db_path, post["id"])["status"], "draft")
        database.schedule_post(self.db_path, post["id"], future)
        self.assertEqual(queue.process_due_posts(self.db_path), 0)
        self.assertTrue(database.claim_post(self.db_path, post["id"]))
        with patch("app.queue.llm.check_content", return_value=(False, "Cần xem lại")), patch("app.queue.facebook.publish_page") as publisher:
            queue.process_claimed_post(self.db_path, post["id"])
            publisher.assert_not_called()
        self.assertEqual(database.get_post(self.db_path, post["id"])["status"], "blocked")
        with patch("app.queue.llm.check_content", return_value=(True, "Đạt")), patch("app.queue.facebook.publish_page", return_value="123_456"):
            self.assertTrue(database.claim_post(self.db_path, post["id"]))
            queue.process_claimed_post(self.db_path, post["id"])
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
        with patch("app.queue.llm.check_content") as reviewer, patch("app.queue.facebook.publish_page") as publisher:
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
        self.assertTrue(database.claim_post(self.db_path, post_id))
        with patch("app.queue.llm.check_content", return_value=(True, "Đạt")), patch(
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


if __name__ == "__main__":
    unittest.main()
