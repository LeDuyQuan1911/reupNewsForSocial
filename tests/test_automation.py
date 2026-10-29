import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app import automation, database, research


class AutomationTests(unittest.TestCase):
    def test_page_ready_prefers_system_user_credential(self):
        settings = {"REUP_FACEBOOK_PAGE_ID": "123", "REUP_META_GRAPH_VERSION": "v26.0",
                    "REUP_FACEBOOK_AUTH_MODE": "system_user", "REUP_FACEBOOK_PAGE_TOKEN": "old"}
        with patch.dict(os.environ, settings, clear=True):
            self.assertFalse(automation.page_ready())
            os.environ["REUP_FACEBOOK_SYSTEM_USER_TOKEN"] = "system-secret"
            self.assertTrue(automation.page_ready())

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

        with patch.dict(os.environ, {**settings, "REUP_FACEBOOK_PAGE_ID": "123",
                                          "REUP_FACEBOOK_PAGE_TOKEN": "test-only",
                                          "REUP_META_GRAPH_VERSION": "v99.0"}, clear=True):
            self.assertEqual(automation.schedule_ready(self.path, self.now), 6)
        self.assertEqual(database.automation_status(self.path)["counts"].get("scheduled"), 6)
        self.assertEqual(len(database.reserved_post_times(self.path, self.now.isoformat())), 6)

    def test_rejected_image_blocks_automatic_schedule(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("rejected", 1)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision", "REUP_FACEBOOK_PAGE_ID": "123",
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

    def test_automatic_post_keeps_good_image_when_second_is_rejected(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("mixed-images", 1)), []

        def prepare_two(path, post_id):
            first = self.prepare_image(path, post_id)
            second = path.parent / "media" / f"post-{post_id}-{'a' * 32}.jpg"
            Image.new("RGB", (640, 320), "blue").save(second, "JPEG")
            database.add_post_image(path, post_id, second.name, "https://example.com/second.jpg", "source")
            return first

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=prepare_two), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", side_effect=[(True, "OK"), (False, "Unrelated")]):
            result = automation.run_cycle(self.path, self.now)
        self.assertEqual(result["prepared"], 1)
        post_id = database.list_posts(self.path)[0]["id"]
        self.assertEqual(len(database.list_post_images(self.path, post_id)), 1)
        self.assertEqual(database.get_post(self.path, post_id)["status"], "draft")

    def test_title_only_image_stays_as_draft_and_is_not_scheduled(self):
        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("title-only", 1)), []

        def prepare_title_card(path, post_id):
            image = self.prepare_image(path, post_id)
            database.attach_image(path, post_id, image.name, "", "title_card")
            return image

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text",
                    "REUP_LLM_VISION_MODEL": "test-vision", "REUP_FACEBOOK_PAGE_ID": "123",
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
        database.claim_daily_automation_scan(self.path, self.now.isoformat())
        database.set_source_active(self.path, self.source_id, False)
        settings = {"REUP_LLM_MODEL": "test-text", "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")):
            self.assertEqual(automation.prepare_articles(self.path, self.now), 0)
            database.set_source_active(self.path, self.source_id, True)
            self.assertEqual(automation.prepare_articles(self.path, self.now), 1)

    def test_daily_scan_uses_bangkok_calendar_day(self):
        late = datetime(2026, 10, 26, 16, 30, tzinfo=timezone.utc)
        after_midnight = late + timedelta(hours=2)
        self.assertTrue(database.claim_daily_automation_scan(self.path, late.isoformat()))
        self.assertFalse(database.claim_daily_automation_scan(self.path, (late + timedelta(minutes=20)).isoformat()))
        self.assertTrue(database.claim_daily_automation_scan(self.path, after_midnight.isoformat()))

    def test_midnight_cycle_scans_once_and_uses_daily_post_target(self):
        database.save_posting_settings(self.path, "2", "08:00, 13:15")
        midnight = datetime(2026, 10, 26, 17, 0, tzinfo=timezone.utc)
        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", return_value=(5, [])) as scan, \
             patch("app.automation.research.review_candidates", return_value={"reviewed": 5}) as review, \
             patch("app.automation.prepare_articles", return_value=2), \
             patch("app.automation.schedule_ready", return_value=0):
            first = automation.run_cycle(self.path, midnight)
            again = automation.run_cycle(self.path, midnight + timedelta(minutes=1))
            tomorrow = automation.run_cycle(self.path, midnight + timedelta(days=1))
            caught_up = automation.run_cycle(self.path, midnight + timedelta(days=2, hours=2))
        self.assertEqual(first["found"], 5)
        self.assertEqual(first["prepared"], 2)
        self.assertEqual(again["found"], 0)
        self.assertEqual(again["reviewed"], 0)
        self.assertEqual(tomorrow["found"], 5)
        self.assertEqual(caught_up["found"], 5)
        self.assertEqual(scan.call_count, 3)
        self.assertEqual(review.call_count, 3)
        self.assertTrue(all(call.args[2] == 2 for call in review.call_args_list))

    def test_daily_cycle_includes_hermes_web_results_and_keeps_curated_scan(self):
        settings = {"REUP_AUTO_ENABLED": "1", "REUP_HERMES_DISCOVERY_ENABLED": "1",
                    "REUP_LLM_MODEL": "test-text"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", return_value=(3, [])) as scan, \
             patch("app.automation.hermes_research.find_articles", return_value=(2, [])) as web, \
             patch("app.automation.research.review_candidates", return_value={"reviewed": 5}), \
             patch("app.automation.prepare_articles", return_value=0), \
             patch("app.automation.schedule_ready", return_value=0):
            result = automation.run_cycle(self.path, self.now)
        self.assertEqual(result["found"], 5)
        self.assertEqual(result["reviewed"], 7)
        scan.assert_called_once()
        web.assert_called_once()

    def test_research_picks_do_not_exceed_daily_target(self):
        candidates = [{"id": index} for index in range(1, 4)]
        raw = '{"picks": [' + ', '.join(
            f'{{"id": {index}, "reason": "useful"}}' for index in range(1, 4)
        ) + ']}'
        picked, _ = research._ordered_ids(candidates, raw, 2)
        self.assertEqual(picked, [1, 2])

    def test_custom_posting_settings_limit_and_times(self):
        settings = database.save_posting_settings(self.path, "2", "13:15, 8:00")
        self.assertEqual(settings, {"posts_per_day": 2, "times": ("08:00", "13:15")})
        self.assertEqual(database.get_posting_settings(self.path), settings)
        history = database.daily_activity(self.path, now=self.now)
        self.assertEqual(history[0]["target"], 2)
        self.assertEqual(history[1]["target"], 6)
        with self.assertRaisesRegex(ValueError, "đúng 2 khung giờ"):
            database.save_posting_settings(self.path, "2", "08:00")
        with self.assertRaisesRegex(ValueError, "30 phút"):
            database.save_posting_settings(self.path, "2", "08:00, 08:15")
        with self.assertRaisesRegex(ValueError, "30 phút"):
            database.save_posting_settings(self.path, "2", "23:50, 00:10")
        self.assertEqual(database.get_posting_settings(self.path), settings)
        now = datetime(2026, 10, 26, 0, 0, tzinfo=timezone.utc)
        first = automation.next_slot(now, [], settings["times"])
        second = automation.next_slot(now, [first], settings["times"])
        self.assertEqual(datetime.fromisoformat(first).astimezone(automation.BANGKOK).strftime("%H:%M"), "08:00")
        self.assertEqual(datetime.fromisoformat(second).astimezone(automation.BANGKOK).strftime("%H:%M"), "13:15")

    def test_custom_daily_limit_prepares_only_two_posts(self):
        database.save_posting_settings(self.path, "2", "08:00, 13:15")

        def scan(path):
            return database.save_articles(path, self.source_id, self.articles("limited", 4)), []

        settings = {"REUP_AUTO_ENABLED": "1", "REUP_LLM_MODEL": "test-text", "REUP_LLM_VISION_MODEL": "test-vision"}
        with patch.dict(os.environ, settings, clear=True), \
             patch("app.automation.discovery.scan_sources", side_effect=scan), \
             patch("app.automation.media.prepare_post_image", side_effect=self.prepare_image), \
             patch("app.automation.llm.write_draft", return_value="Draft with source"), \
             patch("app.automation.llm.check_post", return_value=(True, "OK")):
            result = automation.run_cycle(self.path, self.now)
        self.assertEqual(result["prepared"], 2)
        self.assertEqual(database.count_posts(self.path), 2)


if __name__ == "__main__":
    unittest.main()
