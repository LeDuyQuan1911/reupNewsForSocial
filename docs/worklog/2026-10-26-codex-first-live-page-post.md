# Thử đăng ngay một bài lên Facebook Page

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng yêu cầu đăng ngay một bài thử lên Facebook Page đã cấu hình, rồi xác nhận kết quả.

## Thực hiện
Đã chọn bản nháp #19 về repo lemo-opuscar, kiểm tra nội dung tiếng Việt, nguồn GitHub và ảnh chụp repo. Lần gửi đầu bị chặn vì dashboard cũ chưa nhận biến môi trường Page; bản nháp không đổi. Đã khởi động lại đúng tiến trình dashboard, dùng route đăng ngay của ứng dụng để kiểm duyệt nội dung/ảnh và gửi một ảnh lên Page. Bài được lưu trạng thái `published` với Facebook post ID `342796135574782_122232295634324577`.

## Quyết định
Chọn một bản nháp có ảnh và nội dung hoàn chỉnh, dùng luồng đăng của ứng dụng để giữ kiểm duyệt và chống trùng lặp. Chỉ khởi động lại tiến trình dashboard đã xác định đang phục vụ repo này. Không ghi token hoặc nội dung nhạy cảm vào worklog.

## Kiểm chứng
Route ứng dụng báo đã đăng; SQLite ghi `published`, không có lỗi và có post ID. Truy vấn Graph API chỉ đọc trả cùng post ID, permalink `https://www.facebook.com/122232295706324577/posts/122232295634324577` và `is_published=true`. Không có sửa source hoặc commit.

## Còn lại
Chưa kiểm tra khả năng xem bài từ tài khoản không quản trị Page. Token đã được gửi qua chat trước đó nên cần thay bằng token nhập kín về sau.
