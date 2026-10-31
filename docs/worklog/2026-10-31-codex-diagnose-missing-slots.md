# Chẩn đoán thiếu bài theo khung giờ

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tìm nguyên nhân máy server chưa đủ mục tiêu 19 bài/ngày, đã lỡ 14h và 15h, chưa thấy bài cho 21h–24h hôm nay; kiểm tra source và bằng chứng vận hành có thể truy cập.

## Thực hiện
Đọc cấu hình và source của Hermes runner, luồng quét, chuẩn bị, xếp lịch, đăng; đối chiếu worklog xác nhận trên server ngày 30–31/10. Gửi truy vấn SQLite chỉ đọc cho người dùng chạy trên server; bản đầu không chạy được vì Python hệ thống thiếu `tzdata`, và bản người dùng chạy thiếu dòng tạo `today_jobs`. Chuẩn bị lại lệnh dùng UTC+7 cố định và đủ biến. Đối chiếu kết quả SQLite server do người dùng gửi lúc khoảng 15:50 Bangkok. Truy vấn tiếp theo lấy lỗi của bài #29/#31 cũng cần sửa `Path.resolve()` trước `as_uri()`. Không sửa code hoặc dữ liệu server.

## Quyết định
Phân biệt khung chưa từng được xếp lịch với bài có lịch nhưng đăng lỗi. Kết quả server xác nhận bài 14h và 15h ở trạng thái `blocked` vì ảnh chỉ là thẻ tiêu đề; không bỏ qua kiểm duyệt ảnh để đăng bù. 24h được hiểu là 00:00 ngày kế tiếp.

## Kiểm chứng
Source xác nhận: lượt chuẩn bị chạy tuần tự và xếp lịch sau cùng trong `run_cycle`; `next_slot` bỏ giờ đã qua hoặc cách hiện tại dưới 5 phút; bài lỗi chuẩn bị có retry hữu hạn, bài bị chặn không được tự đăng; 19 là mục tiêu tối đa, không bảo đảm đủ 19. Worklog server ghi lượt quét bắt đầu 00:06 ngày 31/10, lúc 00:11 còn xử lý và chưa có lịch. `requirements.txt` có `tzdata`, nhưng Python hệ thống dùng chạy truy vấn không có gói này. SQLite server cho thấy mục tiêu 19, cấu hình 00:00 và 06:00–23:00, lượt quét 00:06, 15 automation jobs đã xếp lịch và 1 bị chặn lúc chuẩn bị do ảnh đồ họa chung; 8 bài đã đăng 06:00–13:00, 2 bài 14:00–15:00 có lịch nhưng bị chặn, 5 bài 16:00–20:00 còn chờ, không có bài 21:00–23:00. Lượt Hermes gần nhất 15:50 ghi `ok` và không chuẩn bị/xếp thêm bài. Truy vấn `posts.last_error` trên server xác nhận #29 và #31 bị model từ chối vì ảnh chỉ chứa tiêu đề/logo, không phải ảnh minh họa nhận diện chủ thể.

## Còn lại
Cần kiểm tra số tin nguồn đủ điều kiện còn lại để kết luận vì sao chỉ chuẩn bị được 16/19. Muốn đăng lại #29/#31 cần thay ảnh phù hợp, kiểm duyệt lại và chọn giờ mới; không tự gửi bài đã bị chặn. Không có shell trực tiếp đến server trong phiên này.
