# Tiếp tục chuyển Facebook sang System User

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: bị chặn

## Yêu cầu và phạm vi
Tiếp tục cấu hình Meta System User cho Page đã chọn và xác minh ứng dụng trên máy. Không lưu token trong repo hoặc nhật ký.

## Thực hiện
Đã kiểm tra repo và biến môi trường User: chế độ System User và token chưa được cấu hình; Page ID vẫn là Page đã chọn. Trên Meta Developers, xác định App CreatePost có ID `1843338676664642`. Đã mở biểu mẫu thêm App vào Business Portfolio và nhập ID; thao tác gửi bị dừng bởi phím Escape của người dùng nên chưa xác nhận App đã được thêm.

## Quyết định
Giữ nguyên cấu hình Page hiện hành cho đến khi có token System User thật và phép kiểm tra Page thành công. Không ghi token vào repo, tài liệu hoặc log.

## Kiểm chứng
Quan sát trực tiếp Meta Developers xác nhận tên và ID App. Kiểm tra biến môi trường User chỉ đọc tên biến và trạng thái có/không, không in token. Chưa kiểm chứng Graph API System User vì token chưa tồn tại.

## Còn lại
Người dùng đã dừng computer-use bằng phím Escape; không thao tác Meta tiếp trong lượt này. Cần thêm App CreatePost vào Portfolio, tạo System User, gán App/Page, tạo token, chạy script cấu hình và kiểm tra đăng. Không commit/push/merge.
