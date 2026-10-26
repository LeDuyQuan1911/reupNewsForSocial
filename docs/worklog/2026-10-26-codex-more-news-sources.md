# Bổ sung nguồn tin và kiểm tra nghiên cứu hằng ngày

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tìm nguồn AI/công nghệ phù hợp để mở rộng thu thập tin; kiểm tra khả năng hệ thống tự tìm bài mới hằng ngày và hoàn thiện phần cần thiết. Không đăng bài lên mạng xã hội.

## Thực hiện
Kiểm tra `app/automation.py`: ứng dụng đã quét nguồn mỗi giờ khi bật tự động và server còn chạy. Xác minh trực tiếp các feed chính thức của NVIDIA Technical Blog, AWS Machine Learning Blog và Microsoft Research; thêm ba nguồn vào `app/database.py`, cập nhật `README.md`, `SPEC.md`, `PLAN.md` và kiểm tra tính lặp an toàn trong `tests/test_app.py`. Khởi động lại server, nạp nguồn vào SQLite hiện có và quét thử: 20 bài AWS, 10 bài Microsoft Research, 50 bài NVIDIA được thêm. Tạo automation Codex `research-tin-ai-m-i-ng-y` chạy hằng ngày lúc 08:00 để nghiên cứu và báo cáo tối đa sáu bài mới đáng xem; không tạo hay đăng bài.

## Quyết định
Giữ bước quét RSS của ứng dụng để thu thập tự động; dùng lượt research hằng ngày riêng để chọn lọc và giải thích bài đáng chú ý. Không dùng feed Microsoft AI cũ vì trả HTTP 410. Chưa đưa đánh giá AI vào pipeline tạo bản nháp tự động; đã ghi bước đó trong `PLAN.md`.

## Kiểm chứng
Thử feed bằng `app.feeds.fetch_feed`: cả ba hợp lệ và có bài mới. `python -m unittest discover -s tests -v`: 32/32 đạt. `git diff --check`: đạt. `/sources` trả HTTP 200 và hiển thị cả ba nguồn. Quét thử lưu thành công 80 bài.

## Còn lại
Lượt research hằng ngày chưa chạy lần đầu. Server và Codex app cần hoạt động để các cơ chế cục bộ chạy; pipeline tạo bản nháp hiện chọn bài theo điều kiện hiện có, chưa có bước AI xếp hạng mức đáng đăng.
