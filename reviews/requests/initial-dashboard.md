# Yêu cầu review: initial-dashboard

- Base commit: `5c78369fcead12bd1356073d80b7a22b0e5b2efd`
- Head commit: `61e1753`
- Phạm vi file: toàn bộ diff; tập trung `app/`, `run.py`, `tests/`, tài liệu cấu hình và các script nhập từ template. Phần `vendor/` là mã upstream.
- Tiêu chí chấp nhận: `SPEC.md`, đặc biệt thu thập tin, tránh trùng, tạo bài, duyệt nội dung, lịch đăng, đăng ngay lên Facebook Page. Đối chiếu các giới hạn được nêu trong `README.md`.
- Lệnh kiểm tra khả dụng: `python -m unittest discover -s tests -v`, `node scripts/plugins.mjs check`, `node scripts/check-worklog.mjs 2026-10-23-codex-clone-and-kickoff.md`.
- Ngoài phạm vi: đăng tự động lên trang cá nhân và nhóm Facebook; đăng LinkedIn; kiểm thử với token Facebook thật.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
