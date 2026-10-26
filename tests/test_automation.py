import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app import automation, database


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.path = Path(self.directory.name) / "news.sqlite3"
        database.initialize(self.path)
        database.add_source(self.path, "Test RSS", "https://example.com/rss")
        self.source_id = database.list_sources(self.path)[0]["id"]
        self.now = datetime.now(timezone.utc)
        ranking = patch("app.research.llm.chat", return_value='{"picks":[]}')
        ranking.start()
        self.addCleanup(ranking.stop)

    def tearDown(self):
        self.directory.cleanup()

    def articles(self, prefix: str, amount: int) -> list[dict]:
        subjects = ("Satellite imagery gains a new editor", "Database engine reduces memory usage",
                    "Robotics kit learns to sort packages", "Compiler release changes build diagnostics",
                    "Browser update adds private tabs", "Chip design improves battery efficiency",
                    "Cloud storage project reaches stable release")
        return [
            {"title": f"{prefix}: {subjects[index]}",
             "url": f"https://example.com/{prefix}/{index}",
             "summary": "A new software release", "published_at": self.now.isoformat()}
            for index in range(amount)
        ]

    def prepare_image(self, path: Path, post_id: int) -> Path:
        image = path.parent / "media" / f"post-{post_id}.jpg"
        image.parent.mkdir(exist_ok=True)
        Image.new("RGB", (16, 16), "green").save(image, "JPEG")
        database.attach_image(path, post_id, image.name, "https://example.com/image.jpg")
        return image

    def test_scans_and_prepares_six_new_articles_without_page(self):
        database.save_articles(self.path, self.source_id, self.articles("old", 1))
        with database.connect(self.path) as db:
            old = (self.now - timedelta(days=3)).isoformat()
            db.execute("UPDATE articles SET published_at = ?, discovered_at = ? WHERE id = 1", (old, old))

        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("new", 7)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan) as scanner, \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")):
            result = automation.run_cycle(self.path, self.now)
            again = automation.run_cycle(self.path, self.now)

        self.assertEqual(result, {"found": 7, "reviewed": 7, "prepared": 6, "scheduled": 0})
        self.assertEqual(again, {"found": 0, "reviewed": 0, "prepared": 0, "scheduled": 0})
        scanner.assert_called_once()
        self.assertEqual(database.count_posts(self.path), 6)
        self.assertIsNone(database.get_post_for_article(self.path, 1))
        self.assertEqual(database.automation_status(self.path)["counts"].get("ready"), 6)

        with patch.dict(os.environ, {**settings, "REUP_FACEBOOK_PAGE_ID": "page",
                                          "REUP_FACEBOOK_PAGE_TOKEN": "test-only",
                                          "REUP_META_GRAPH_VERSION": "v99.0"}, clear=True):
            self.assertEqual(automation.schedule_ready(self.path, self.now), 6)
        self.assertEqual(database.automation_status(self.path)["counts"].get("scheduled"), 6)
        self.assertEqual(len(database.reserved_post_times(self.path, self.now.isoformat())), 6)

    def test_rejected_image_blocks_automatic_schedule(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("rejected", 1)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision", "REUP_FACEBOOK_PAGE_ID": "page",
                    "REUP_FACEBOOK_PAGE_TOKEN": "test-only", "REUP_META_GRAPH_VERSION": "v99.0"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(False, "Needs review")):
            result = automation.run_cycle(self.path, self.now)

        self.assertEqual(result["scheduled"], 0)
        self.assertEqual(database.list_posts(self.path)[0]["status"], "blocked")
        self.assertEqual(database.automation_status(self.path)["counts"].get("blocked"), 1)

    def test_title_only_image_stays_as_draft_and_is_not_scheduled(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("title-only", 1)), []

        def prepare_title_card(path, post_id):
            image = self.prepare_image(path, post_id)
            database.attach_image(path, post_id, image.name, "", "title_card")
            return image

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision", "REUP_FACEBOOK_PAGE_ID": "page",
                    "REUP_FACEBOOK_PAGE_TOKEN": "test-only", "REUP_META_GRAPH_VERSION": "v99.0"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=prepare_title_card), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")) as check_post:
            result = automation.run_cycle(self.path, self.now)

        post = database.list_posts(self.path)[0]
        self.assertEqual(result["scheduled"], 0)
        self.assertEqual(post["status"], "blocked")
        self.assertEqual(database.automation_status(self.path)["counts"].get("blocked"), 1)
        check_post.assert_not_called()

    def test_transient_generation_error_retries_existing_draft(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("retry", 1)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", side_effect=[TimeoutError("temporary"), "Draft with source"]), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")), \
             patch("app.automation.logging.exception"):
            first = automation.run_cycle(self.path, self.now)
            second = automation.run_cycle(self.path, self.now + timedelta(minutes=6))

        self.assertEqual(first["prepared"], 0)
        self.assertEqual(second["prepared"], 1)
        self.assertEqual(database.count_posts(self.path), 1)
        self.assertEqual(database.automation_status(self.path)["counts"].get("ready"), 1)

    def test_blocked_article_does_not_use_daily_ready_slot(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("candidate", 7)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision"}
        verdicts = [(False, "Needs review")] + [(True, "OK")] * 6
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", side_effect=verdicts):
            result = automation.run_cycle(self.path, self.now)

        self.assertEqual(result["prepared"], 6)
        self.assertEqual(database.automation_status(self.path)["counts"].get("blocked"), 1)

    def test_paused_source_does_not_prepare_saved_articles(self):
        database.save_articles(self.path, self.source_id, self.articles("paused", 1))
        database.claim_automation_scan(self.path, self.now.isoformat(), automation.SCAN_INTERVAL_SECONDS)
        database.set_source_active(self.path, self.source_id, False)
        settings = {"REUP_LLM_MODEL": "test-text", "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")):
            self.assertEqual(automation.prepare_articles(self.path, self.now), 0)
            database.set_source_active(self.path, self.source_id, True)
            self.assertEqual(automation.prepare_articles(self.path, self.now), 1)


if __name__ == "__main__":
    unittest.main()
