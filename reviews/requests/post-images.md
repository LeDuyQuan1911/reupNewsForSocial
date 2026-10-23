# Yêu cầu review: post-images

- Base commit: `5819b4e074af8ecc7eaf5319c5193adf6fbeb2dd`
- Head commit: `721cbf38e6f22c20b669fe702f48da9a22fb4ca5`
- Phạm vi file: diff base/head, tập trung `app/media.py`, `app/feeds.py`, `app/database.py`, `app/llm.py`, `app/facebook.py`, `app/queue.py`, `app/web.py`, template ảnh và tests.
- Tiêu chí chấp nhận: `SPEC.md` yêu cầu bài có ảnh từ nguồn báo hoặc ảnh chụp repo, dự phòng khi nguồn chặn, xem trước, kiểm duyệt ảnh/văn bản, gửi JPEG và caption lên Facebook Page, giữ an toàn khi lỗi.
- Lệnh kiểm tra khả dụng: `python -m unittest discover -s tests -v`, `python -m compileall -q app run.py`, `node scripts/check-worklog.mjs 2026-10-23-codex-post-images.md`.
- Ngoài phạm vi: đăng ảnh thật lên Page khi chưa có token, đăng trang cá nhân/nhóm/LinkedIn, mã upstream trong `vendor/`.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
