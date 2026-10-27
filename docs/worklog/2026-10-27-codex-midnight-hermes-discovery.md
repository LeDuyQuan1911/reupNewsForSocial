# Hermes tìm bài lúc nửa đêm

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Cho Hermes tìm bài một lần vào 00:00 giờ Bangkok mỗi ngày và chuẩn bị số bài tương ứng với cấu hình số bài đăng trong ngày. Giữ bộ đăng bài theo giờ đã hẹn.

## Thực hiện
Giữ Hermes cron mỗi phút để xử lý bài đến giờ; `app/automation.py` chỉ gọi quét và xếp hạng ở lượt đầu tiên của ngày Bangkok. Truyền `posts_per_day` cho `app/research.py` làm số tin AI ưu tiên tối đa; luồng chuẩn bị hiện giới hạn số bản nháp đạt theo ngày. `app/templates/hermes.html` nêu mốc 00:00 và chạy bù. Cập nhật README, SPEC, PLAN, quyết định kỹ thuật và thêm ca kiểm tra trong `tests/test_automation.py`. Khởi động lại dashboard để hiển thị thay đổi.

## Quyết định
24:00 được hiểu là 00:00 của ngày mới tại Bangkok. Tiếp tục dùng một job mỗi phút để không lỡ giờ đăng; lượt đầu tiên sau nửa đêm thực hiện tìm tin. Lưu nhiều metadata nguồn hơn mục tiêu để thay tin không đạt, nhưng số bài chuẩn bị đạt không vượt `posts_per_day`.

## Kiểm chứng
`python -m unittest discover -s tests`: 92 ca đạt. Sau ca bổ sung về chạy bù, `python -m unittest discover -s tests -p test_automation.py`: 13 ca đạt. Trang `/hermes` trả HTTP 200 và hiện mốc 00:00 cùng mục tiêu 12 bài hiện tại. Hermes gateway/job đang chạy và lượt quét thực tế hôm nay ghi lúc 00:00:53 Bangkok. `git diff --check` đạt.

## Còn lại
Không thể bảo đảm đủ 12 bài nếu thiếu tin phù hợp, nguồn/model lỗi hoặc kiểm duyệt từ chối. Lượt quét đã nhận mà dừng giữa chừng chưa tự thử quét lại trong cùng ngày; có thể bấm quét thủ công. Chưa chờ đến nửa đêm tiếp theo để quan sát lượt chạy thật sau thay đổi.
