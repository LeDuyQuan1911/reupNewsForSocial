import re
import unittest
from unittest.mock import patch

from app import llm


class DraftStyleTests(unittest.TestCase):
    def test_rewrites_text_without_icons_and_adds_missing_hashtags(self):
        source = "https://example.com/story"
        raw = "Tin mới đáng chú ý.\n\nCó ba điểm kỹ thuật.\n\nNgười đọc có thể xem nguồn.\n\nNguồn: " + source
        revised = "💡 Tin mới đáng chú ý.\n\nCó ba điểm kỹ thuật.\n\nNgười đọc có thể xem nguồn.\n\nNguồn: " + source
        with patch("app.hermes_writer.write_with_hermes", side_effect=[raw, revised]) as writer:
            draft = llm.write_draft("Tin mới", "Tóm tắt", source)
        self.assertEqual(writer.call_count, 2)
        self.assertRegex(draft, r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
        self.assertGreaterEqual(len(re.findall(r"(?<!\w)#[A-Za-z][A-Za-z0-9_]*", draft)), 2)
        self.assertTrue(draft.endswith("Nguồn: " + source))
        self.assertEqual(draft.count(source), 1)

    def test_keeps_existing_style_without_extra_fallback(self):
        source = "https://example.com/story"
        raw = "📰 Mở đầu\n\n🔎 Chi tiết\n\n💡 Ứng dụng\n\n#AI #CongNghe #GitHub\n\nNguồn: " + source
        with patch("app.hermes_writer.write_with_hermes", return_value=raw):
            draft = llm.write_draft("Tin mới", "Tóm tắt", source)
        self.assertEqual(draft, raw)

    def test_leaves_model_chosen_icon_placement_unchanged(self):
        source = "https://example.com/story"
        raw = "Một thông tin đáng chú ý 👀\n\nChi tiết kỹ thuật có căn cứ.\n\n🔎 Xem thêm ở nguồn.\n\n#AI #GitHub"
        with patch("app.hermes_writer.write_with_hermes", return_value=raw):
            draft = llm.write_draft("Tin mới", "Tóm tắt", source)
        self.assertEqual(draft, f"{raw}\n\nNguồn: {source}")

    def test_prompt_leaves_icon_choice_to_model(self):
        source = "https://example.com/story"
        with patch("app.hermes_writer.write_with_hermes", return_value="💡 Nội dung.\n\n#AI #GitHub") as writer:
            llm.write_draft("Tin mới", "Tóm tắt", source)
        self.assertIn("Tiêu đề: Tin mới", writer.call_args.args[0])
        brief = __import__("app.hermes_writer", fromlist=["EDITORIAL_BRIEF"]).EDITORIAL_BRIEF.read_text(encoding="utf-8")
        self.assertIn("Chính bạn chọn loại, số lượng và vị trí", brief)
        self.assertIn("Không áp công thức một icon đầu mỗi dòng", brief)


if __name__ == "__main__":
    unittest.main()
