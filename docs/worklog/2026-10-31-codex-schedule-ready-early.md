# Xếp lịch bài đạt kiểm tra ngay trong lượt Hermes

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Server có nhiều bài tự động đã đạt kiểm tra nhưng chưa có lịch vì lượt Hermes vẫn đang viết các bài tiếp theo. Sửa luồng để xếp lịch ngay khi từng bài sẵn sàng, giữ giới hạn ảnh/bình luận và lịch đã đặt.

## Thực hiện
Trong worktree `codex/schedule-ready-early`, sửa `app/automation.py` để gọi xếp lịch sau từng bài đạt kiểm tra và dùng giờ hiện tại khi chạy thật. Giữ lượt xếp lịch cuối để xử lý bài `ready` còn tồn. Thêm `database.scheduled_post_ids` để đếm bài mới hẹn theo trạng thái thực trong DB, kể cả khi cập nhật job lỗi tạm thời rồi phục hồi. Thêm test hồi quy trong `tests/test_automation.py` cho thứ tự xếp lịch và trường hợp lỗi tạm thời. Cập nhật `PLAN.md` và `contexte/decisions.md`.

## Quyết định
Không đổi điều kiện đăng, ảnh hoặc bình luận. Nếu xếp lịch sớm lỗi, ghi log và thử lại ở cuối lượt. Triển khai code mới qua CI/CD sau khi được chủ repo quyết định merge; các bài đã được hẹn trên server dùng hàm hiện có.

## Kiểm chứng
`python -m unittest discover -s tests -p test_automation.py -v`: 16 bài test qua, gồm hai test mới. `git diff --check`: qua ở commit đầu. Đã thử chạy toàn bộ suite cục bộ nhưng các test khác cần nhiều thời gian/truy cập mạng và lượt này bị ngắt; CI Windows sẽ kiểm tra toàn bộ khi có PR. Review độc lập vòng đầu tìm được lỗi đếm thiếu khi job status lỗi tạm thời; đã bổ sung cách đếm theo DB và test tái hiện, chờ đối chiếu vòng hai.

## Còn lại
Bản chạy trên server cần cập nhật qua quy trình CI/CD sau khi được chủ repo phê duyệt merge. Chưa kiểm tra lượt Hermes thực tế với code mới trên server.
