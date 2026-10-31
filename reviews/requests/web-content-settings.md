# Yêu cầu review: web-content-settings

- Base commit: f01b0c7be70767546d6b869f430e3d9ed17e67b8
- Head commit hoặc PR: 47b93e1b80e113f572af2e89320639224a2fe5af
- Phạm vi file:
  - PLAN.md
  - README.md
  - SPEC.md
  - app/automation.py
  - app/database.py
  - app/hermes_research.py
  - app/hermes_writer.py
  - app/llm.py
  - app/static/site-redesign.css
  - app/templates/base.html
  - app/templates/hermes.html
  - app/web.py
  - contexte/decisions.md
  - docs/editorial-brief.md
  - docs/worklog/2026-11-01-codex-web-editable-settings.md
  - tests/test_app.py
  - tests/test_automation.py
  - tests/test_hermes_research.py
  - tests/test_hermes_writer.py
- Tiêu chí chấp nhận: `SPEC.md` yêu cầu trang Hermes cho sửa giới hạn 25–30 ứng viên, phong cách viết bài/bình luận và ưu tiên tìm tin; lưu trong SQLite; lượt web và automation mới dùng giá trị đã lưu. Điều kiện nguồn gốc, kiểm duyệt, ảnh và giờ đăng còn hiệu lực. Giá trị bí mật không hiện trong form. Cấu hình cũ cần được khởi tạo an toàn.
- Lệnh kiểm tra khả dụng: `$env:REUP_FACEBOOK_AUTH_MODE='page_token'; $env:REUP_HERMES_DISCOVERY_ENABLED='0'; python -m unittest discover -s tests -q`.
- Ngoài phạm vi: bài đã viết/lên lịch không tự đổi; không thay cấu hình token/secret hoặc kiểm tra bằng Facebook thật.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
