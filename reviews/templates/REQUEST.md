# Yêu cầu review: <task-id>

- Base commit: <SHA>
- Head commit hoặc PR: <SHA hoặc URL>
- Phạm vi file: <đường dẫn liên quan>
- Tiêu chí chấp nhận: <dẫn đến SPEC.md hoặc ghi hành vi cụ thể>
- Lệnh kiểm tra khả dụng: <lệnh đã xác minh, hoặc "chưa có">
- Ngoài phạm vi: <nếu có>

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
