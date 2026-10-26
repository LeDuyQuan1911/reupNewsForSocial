# Giải thích agent local đăng vào nhóm qua trình duyệt

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng làm rõ muốn tự host LLM như Hermes trên máy, đến giờ agent dùng máy/trình duyệt của họ lấy bài đã chuẩn bị và đăng vào nhóm Facebook. Giải thích tính khả thi và cách ghép với ứng dụng hiện tại; không triển khai hoặc gửi bài.

## Thực hiện
Kiểm tra `app/automation.py`, `app/queue.py`, `app/database.py` và `run.py`. Ứng dụng có lịch, nội dung, ảnh và trạng thái cho bài đăng Page; chưa có đích nhóm, adapter trình duyệt hoặc bộ xác nhận kết quả đăng nhóm.

## Quyết định
Có thể thiết kế agent local dùng phiên Facebook đã đăng nhập để thao tác giao diện nhóm. LLM xử lý lựa chọn/nội dung; thao tác đăng cần bộ điều khiển trình duyệt, trạng thái đăng theo từng nhóm, kiểm chứng URL/kết quả và chặn thử lại khi chưa rõ kết quả. Bắt đầu bằng chế độ chuẩn bị/duyệt trước khi bật gửi tự động.

## Kiểm chứng
Đối chiếu source thực tế, không đăng lên Facebook hay đọc cookie/tài khoản. Chạy kiểm tra worklog trước bàn giao.

## Còn lại
Chưa xác định nhóm đích, quyền thành viên, mức tự động hay hành vi Facebook trên tài khoản người dùng. Cần kiểm thử từng nhóm bằng phiên người dùng; giao diện, kiểm duyệt nhóm và chính sách nền tảng có thể thay đổi.
