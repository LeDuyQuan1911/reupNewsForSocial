# Xếp lịch bài đạt kiểm tra ngay trong lượt Hermes

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Server có nhiều bài tự động đã đạt kiểm tra nhưng chưa có lịch vì lượt Hermes vẫn đang viết các bài tiếp theo. Sửa luồng để xếp lịch ngay khi từng bài sẵn sàng, giữ giới hạn ảnh/bình luận và lịch đã đặt.

## Thực hiện
Trong worktree `codex/schedule-ready-early`, sửa `app/automation.py` để gọi xếp lịch sau từng bài đạt kiểm tra, cộng đúng số bài đã hẹn trong kết quả lượt và dùng giờ hiện tại khi chạy thật. Giữ lượt xếp lịch cuối để xử lý bài `ready` còn tồn. Thêm test hồi quy trong `tests/test_automation.py` để kiểm tra bài đầu đã có lịch trước khi bắt đầu viết bài thứ hai. Cập nhật `PLAN.md` và `contexte/decisions.md`.

## Quyết định
Không đổi điều kiện đăng, ảnh hoặc bình luận. Nếu xếp lịch sớm lỗi, ghi log và thử lại ở cuối lượt. Triển khai code mới qua CI/CD sau khi được chủ repo quyết định merge; các bài đã được hẹn trên server dùng hàm hiện có.

## Kiểm chứng
`python -m unittest discover -s tests -p test_automation.py -v`: 15 bài test qua, gồm test mới. `git diff --check`: qua. Đã thử chạy toàn bộ suite cục bộ nhưng các test khác cần nhiều thời gian/truy cập mạng và lượt này bị ngắt; CI Windows sẽ kiểm tra toàn bộ khi có PR.

## Còn lại
Bản chạy trên server cần cập nhật qua quy trình CI/CD sau khi được chủ repo phê duyệt merge. Chưa kiểm tra lượt Hermes thực tế với code mới trên server.
