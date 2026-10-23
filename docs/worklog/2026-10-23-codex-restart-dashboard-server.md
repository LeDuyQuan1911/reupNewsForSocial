# Chạy lại server dashboard

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Khởi động lại server cục bộ để người dùng kiểm tra thay đổi giao diện hiện tại.

## Thực hiện
Kiểm tra tiến trình server. Shell bị giới hạn không thấy listener của máy chủ; yêu cầu HTTP có quyền phù hợp phát hiện server cũ vẫn phục vụ giao diện trước đó. Dừng đúng tiến trình Python `run.py` cũ trên cổng 5000 và khởi động lại `run.py` từ checkout hiện tại dưới dạng tiến trình ẩn (PID 26956).

## Quyết định
Chạy `run.py` như cách README hướng dẫn để giữ hành vi ứng dụng hiện tại. Xác nhận trước khi chạy rằng dữ liệu cục bộ chỉ có 7 bản nháp, không có bài đã lên lịch đến hạn.

## Kiểm chứng
HTTP GET `/`, `/articles`, `/posts`, `/sources`, `/account` tại `http://127.0.0.1:5000`: cả năm trả 200 và không còn khối `page-heading`. Server mới đang lắng nghe cổng 5000.

## Còn lại
Không có. Người dùng có thể mở `http://127.0.0.1:5000` để kiểm tra.
