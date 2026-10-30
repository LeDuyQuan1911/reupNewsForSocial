# Yêu cầu review: cd-parent-exit

- Base commit: 2d02824daa848a703d2be2dba451cac2134fc0eb
- Head commit hoặc PR: 488a82b7b7732a62f4cb639bdd79872b647b54af
- Phạm vi file:
  - docs/worklog/2026-10-31-codex-fix-cd-parent-exit.md
  - scripts/cd/update-server.ps1
  - tests/test_cd_dashboard_stop.py
- Tiêu chí chấp nhận: Khi tiến trình launcher Python của dashboard tự thoát sau khi dừng tiến trình con, CD vẫn tiếp tục. Không dừng PID đã bị tái sử dụng hoặc tiến trình ngoài dashboard; nếu launcher còn sống mà không dừng được thì triển khai phải dừng. Giữ kiểm tra cổng 5000 và khả năng phục hồi hiện có.
- Lệnh kiểm tra khả dụng: `python -m unittest discover -s tests -p test_cd_dashboard_stop.py -v`; `python -m unittest discover -s tests -p test_powershell5_syntax.py -v`.
- Ngoài phạm vi: thay đổi cơ chế release gate, lịch Hermes, xử lý bài đăng và dữ liệu SQLite.

## Prompt cho reviewer

Hãy review độc lập thay đổi giữa base và head. Đọc `AGENTS.md`, plugin `independent-review`, `reviews/README.md` và yêu cầu này. Dùng phiên/ngữ cảnh riêng; ở lượt đầu chưa đọc giải thích hoặc kết luận của tác giả. Xem diff và code liên quan, kiểm tra hành vi theo tiêu chí chấp nhận. Không sửa implementation. Ghi báo cáo theo `reviews/templates/REPORT.md`, nêu bằng chứng cụ thể hoặc nói rõ không có phát hiện. Tạo worklog riêng cho nhiệm vụ review.
