# Yêu cầu review: schedule-ready-early

- Base commit: 5babbc7cb288c39b5c382977e5b23c3dc48de377
- Head commit hoặc PR: 6cf7b8a5c5e1062abfc275f37a16043bf2d0dfc0 (vòng độc lập); 490d99f439372f30323f0192d094261bfa9cae33 (sau đối chiếu)
- Phạm vi file:
  - PLAN.md
  - app/automation.py
  - contexte/decisions.md
  - docs/worklog/2026-10-31-codex-schedule-ready-early.md
  - tests/test_automation.py
- Tiêu chí chấp nhận: Khi lượt tự động chuẩn bị nhiều bài, mỗi bài đạt kiểm tra nội dung, ảnh và bình luận được xếp vào khung còn trống trước khi bắt đầu chuẩn bị bài kế tiếp. Bài bị chặn hoặc thiếu điều kiện không được hẹn. Tổng `scheduled` của lượt phản ánh số bài mới hẹn; lượt chạy thật không đặt giờ đã qua nếu bước chuẩn bị kéo dài. Không đăng Facebook trực tiếp trong bước này.
- Lệnh kiểm tra khả dụng: `python -m unittest discover -s tests -p test_automation.py -v`; `git diff 5babbc7cb288c39b5c382977e5b23c3dc48de377...490d99f439372f30323f0192d094261bfa9cae33 -- app/automation.py app/database.py tests/test_automation.py`
- Ngoài phạm vi: Thay đổi quyền Meta, Facebook API, lịch 19 bài/ngày và quy trình CD trên server.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
