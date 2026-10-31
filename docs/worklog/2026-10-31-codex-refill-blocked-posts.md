# Tự bù bài bị chặn để đạt mục tiêu ngày

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Khi bài tự động bị chặn, tiếp tục tìm và chuẩn bị bài thay thế để lấp các khung còn lại trong mục tiêu 19 bài/ngày, nhưng chỉ đăng bài đạt kiểm duyệt, đúng giờ cấu hình và tránh gửi trùng.

## Thực hiện
Sửa `app/database.py` để bài đã xếp lịch nhưng bị chặn không chiếm suất, thêm trạng thái và giới hạn quét bù trong ngày, kể cả migration SQLite cũ. Sửa `app/automation.py` để quét RSS/GitHub và Hermes bổ sung khi còn giờ cấu hình nhưng hết ứng viên đã lưu; chuẩn bị/xếp lịch bài thay thế và chuẩn bị riêng mốc 00:00 ngày kế tiếp sau giờ cuối hôm trước. Thêm test tương ứng trong `tests/test_automation.py`; cập nhật `SPEC.md`, `README.md`, `PLAN.md` và `contexte/decisions.md`. Không sửa dữ liệu server, secrets hoặc lịch người dùng.

## Quyết định
Giữ các giờ do chủ dự án đặt; không thêm giờ bù ngoài cấu hình. Quét bổ sung đầu tiên sau ít nhất 5 phút, các lượt sau cách ít nhất 30 phút, tối đa 48 lượt/ngày để tránh Hermes gọi lặp mỗi phút. Bài bị chặn ở giờ đã qua chỉ có thể thay ở giờ cấu hình còn lại. Mốc 00:00 phải được chuẩn bị từ tối hôm trước vì quét bắt đầu đúng 00:00 không thể kịp xếp bài cho chính mốc đó.

## Kiểm chứng
`python -m unittest discover -s tests -p test_automation.py -q`: 23 test đạt, gồm migration, bài bị chặn lúc chuẩn bị/đăng, bù vào giờ cấu hình, giữ chỗ 00:00, không lấy bản nháp cũ cho ngày mới và khôi phục job sau khi bài đã có lịch/đã đăng. `git diff --check`: không có lỗi khoảng trắng. Bộ `unittest discover -s tests -q` chạy hơn một phút không kết thúc ở môi trường cục bộ nên đã dừng; chưa có kết quả toàn bộ suite. Reviewer độc lập đã tìm trường hợp bản nháp `ready` tràn sang ngày sau; bản sửa và vòng đối chiếu được xác nhận trong `C:\Users\PC\Desktop\reupNewsForSocial-refill-review\reviews\reports\refill-blocked-independent.md`, không còn phát hiện đã xác nhận.

## Còn lại
Không thể bảo đảm đủ 19 bài nếu không có đủ nguồn/ảnh đạt kiểm duyệt, model lỗi hoặc giờ cấu hình đã qua; riêng bài bị chặn đúng lúc đăng không thể quay lại giờ đó. Chưa thử bằng Hermes/9Router/Facebook thật hoặc trên server. Chưa tạo PR, push, merge hoặc triển khai server vì nhiệm vụ chưa yêu cầu thay đổi remote.
