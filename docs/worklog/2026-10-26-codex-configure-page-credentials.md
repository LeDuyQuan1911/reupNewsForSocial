# Cấu hình thông tin kết nối Facebook Page

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng muốn cấu hình Page access token trên máy này và bảo đảm thông tin nhạy cảm không được đưa vào Git.

## Thực hiện
Đã khảo sát script cấu hình Page hiện có và vị trí lưu biến môi trường User. Token đầu thiếu quyền đăng nên không lưu. Token mới được xác minh có đủ quyền và tác vụ tạo nội dung trên Page đích; Page token tương ứng đã được lưu vào biến môi trường User của Windows. Đã khởi động 9Router và dashboard cục bộ.

## Quyết định
Chỉ lưu Page ID, phiên bản Graph API và token trong biến môi trường User của Windows sau khi kiểm tra quyền đọc đúng Page và quyền `pages_manage_posts`; không ghi giá trị nhạy cảm vào repo hoặc worklog. Không lưu token đầu thiếu quyền đăng vì có thể tạo trạng thái kết nối giả.

## Kiểm chứng
Graph API xác nhận token mới có `pages_show_list`, `pages_read_engagement`, `pages_manage_posts` và Page đích có tác vụ `CREATE_CONTENT`. Script `configure-facebook-page.ps1 -Check` xác minh lại quyền đọc Page sau khi lưu. Cổng localhost 20128 và 5000 đã lắng nghe; trang `/facebook` trả HTTP 200. `.env` và `data/` được Git bỏ qua, không tạo file chứa token trong repo và không commit. Sáu bài tự động cũ được đánh dấu quá 48 giờ; không có bài đăng thật nào đến hạn. Kiểm tra `node scripts/check-worklog.mjs 2026-10-26-codex-configure-page-credentials.md` thành công.

## Còn lại
Chưa thử xuất bản bài thật, nên quyền đăng và chế độ hiển thị công khai của App/Page chưa được xác nhận bằng một lần đăng thực tế. Các token đã gửi qua chat nên người dùng cần xoay vòng/thu hồi sau khi có cách nhập kín. Bài mới sẽ được quét và xếp lịch khi dịch vụ tiếp tục chạy; sáu bài quá hạn không tự được xếp lại.
