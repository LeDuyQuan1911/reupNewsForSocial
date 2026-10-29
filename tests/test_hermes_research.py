import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app import database, hermes_research


class HermesResearchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.path = Path(self.directory.name) / "research.sqlite3"
        database.initialize(self.path)
        self.now = datetime(2026, 10, 28, 0, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.directory.cleanup()

    def test_web_only_hermes_turn_saves_verified_original_and_reason(self):
        url = "https://new-vendor.example/news/product-launch"
        output = json.dumps({"articles": [{"url": url, "reason": "Sản phẩm mới có thông số cụ thể"}]})
        html = ("<html><head><meta property='og:title' content='New product launch for developers'>"
                "<meta property='og:description' content='A new toolkit with specific developer features.'>"
                "<meta property='article:published_time' content='2026-10-27T22:00:00Z'>"
                "</head></html>").encode()
        settings = {"REUP_HERMES_DISCOVERY_ENABLED": "1", "REUP_LLM_MODEL": "test-model",
                    "REUP_LLM_API_KEY": "test-secret"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.hermes_research.hermes_executable", return_value="hermes"), \
             patch("app.hermes_research.subprocess.run", return_value=subprocess.CompletedProcess([], 1, output, "")) as run, \
             patch("app.hermes_research.media.fetch_public_bytes", return_value=(html, url)):
            count, errors = hermes_research.find_articles(self.path, self.now, 2)
        self.assertEqual((count, errors), (1, []))
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--toolsets") + 1], "web")
        self.assertIn("--ignore-rules", command)
        self.assertIn("nhiều ảnh thật", run.call_args.kwargs["input"])
        self.assertNotIn("test-secret", run.call_args.kwargs["input"])
        article = database.list_articles(self.path)[0]
        self.assertEqual(article["url"], url)
        self.assertEqual(article["research_method"], "hermes")
        self.assertEqual(article["source_name"], "new-vendor.example")

    def test_rejects_old_or_unverifiable_page_even_if_hermes_recommends_it(self):
        url = "https://vendor.example/news/old-story"
        output = json.dumps({"articles": [{"url": url, "reason": "Có vẻ là tin mới rất đáng đọc"}]})
        html = ("<meta property='og:title' content='Old technology announcement'>"
                "<meta property='og:description' content='A detailed old technology announcement.'>"
                "<meta property='article:published_time' content='2026-10-01T12:00:00Z'>").encode()
        with patch.dict(os.environ, {"REUP_HERMES_DISCOVERY_ENABLED": "1", "REUP_LLM_MODEL": "test",
                                          "REUP_LLM_API_KEY": "test"}, clear=True), \
             patch("app.hermes_research.hermes_executable", return_value="hermes"), \
             patch("app.hermes_research.subprocess.run", return_value=subprocess.CompletedProcess([], 0, output, "")), \
             patch("app.hermes_research.media.fetch_public_bytes", return_value=(html, url)):
            count, errors = hermes_research.find_articles(self.path, self.now, 1)
        self.assertEqual(count, 0)
        self.assertEqual(len(errors), 1)
        self.assertEqual(database.count_articles(self.path), 0)

    def test_accepts_article_date_from_structured_data(self):
        url = "https://other-vendor.example/blog/launch"
        html = ("<meta property='og:title' content='Developer platform launch'>"
                "<meta property='og:description' content='The platform has a new feature for developers.'>"
                "<script type='application/ld+json'>"
                '{"@type":"NewsArticle","datePublished":"2026-10-27T20:00:00Z"}'
                "</script>").encode()
        with patch("app.hermes_research.media.fetch_public_bytes", return_value=(html, url)):
            article = hermes_research._verify_page(url, self.now)
        self.assertEqual(article["published_at"], "2026-10-27T20:00:00+00:00")

    def test_parses_quiet_cli_session_prefix_before_json(self):
        raw = ('session_id: local-' + 'a' * 64
               + '{"articles":[{"url":"https://vendor.example/news/new",'
                 '"reason":"Một tính năng mới hữu ích"}]}')
        self.assertEqual(len(hermes_research._proposals(raw, 2)), 1)

    def test_long_reason_is_bounded_after_valid_json(self):
        raw = json.dumps({"articles": [{"url": "https://vendor.example/news/new",
                                       "reason": "Tin công nghệ đáng chú ý. " * 30}]})
        self.assertEqual(len(hermes_research._proposals(raw, 1)[0]["reason"]), 240)

    def test_paused_domain_blocks_new_hermes_articles(self):
        database.add_source(self.path, "Vendor", "https://vendor.example/feed")
        source_id = database.list_sources(self.path)[0]["id"]
        database.set_source_active(self.path, source_id, False)
        article = {"url": "https://vendor.example/news/new", "title": "A new software release",
                   "summary": "This release adds useful features for developers.",
                   "published_at": self.now.isoformat(), "image_url": ""}
        with self.assertRaisesRegex(ValueError, "tạm dừng"):
            database.save_hermes_article(self.path, article, False)

    def test_github_repo_is_saved_with_repo_media_kind(self):
        url = "https://github.com/example/new-tool"
        info = {"html_url": url, "full_name": "example/new-tool", "fork": False,
                "archived": False, "description": "A useful new developer tool with examples",
                "created_at": (self.now - timedelta(hours=3)).isoformat()}
        with patch("app.hermes_research.media.fetch_public_bytes", return_value=(json.dumps(info).encode(),
                                                                           "https://api.github.com/repos/example/new-tool")):
            article = hermes_research._verify_repo(url, self.now)
        database.save_hermes_article(self.path, article, True)
        with database.connect(self.path) as db:
            kind = db.execute("SELECT kind FROM sources").fetchone()[0]
        self.assertEqual(kind, "hermes_github")


if __name__ == "__main__":
    unittest.main()
