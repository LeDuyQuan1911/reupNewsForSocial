# Kết nối model 9Router

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng cung cấp endpoint và khóa API 9Router cục bộ, muốn dùng model nhẹ cho ứng dụng.

## Thực hiện
Kiểm tra danh mục 9Router và thử các model nhẹ. Các model miễn phí được liệt kê nhưng không dùng được qua giao thức hiện tại hoặc đã ngừng. Chọn `ag/gemini-3.8-flash-low` vì phản hồi được cả văn bản và ảnh. Sửa `app/llm.py` để gửi `stream: false`, nhận JSON như code đang xử lý; 9Router trả SSE nếu thiếu trường này. Lưu endpoint, tên model văn bản/ảnh và khóa API vào biến môi trường Windows của người dùng (không ghi giá trị khóa ở đây). Khởi động lại dashboard để nạp cấu hình.

## Quyết định
Chọn cùng một model Flash nhẹ cho viết bài và kiểm duyệt ảnh sau khi xác nhận capability vision và thử hàm tích hợp thật. Không ghi khóa API vào repo hoặc worklog.

## Kiểm chứng
Gọi thật `llm.chat` nhận nội dung văn bản; `llm.check_post` với ảnh JPEG mẫu trả verdict parse được. Dashboard lắng nghe ở `127.0.0.1:5000`, trang `/account` trả HTTP 200; 9Router lắng nghe ở `127.0.0.1:20128`. Bốn biến môi trường người dùng đều hiện diện, chỉ kiểm tra trạng thái có/không. `python -m unittest discover -s tests -q`: 20 test đạt.

## Còn lại
Chưa có token Facebook Page để kiểm tra đăng bài thật. Model và kết nối upstream 9Router có thể thay đổi trạng thái về sau. Khi khởi động lại 9Router cần chạy lại CLI nếu chưa thiết lập tự khởi động cùng Windows.
