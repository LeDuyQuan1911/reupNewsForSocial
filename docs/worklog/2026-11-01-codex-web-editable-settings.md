# Thiết lập nội dung và tự động hóa trên web

- Ngày: 2026-11-01
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Đưa các thiết lập do chủ dự án quyết định, gồm phong cách viết và các lựa chọn vận hành tự động, lên giao diện web để xem và sửa. Không đưa bí mật kết nối lên giao diện.

## Thực hiện
Thêm bảng `content_settings` với giới hạn ứng viên, phong cách viết và ưu tiên tìm tin; đưa form lên trang Hermes. Nối giá trị đã lưu vào cả tìm tin Hermes, viết nháp và bình luận từ web/automation; áp giới hạn ứng viên cho việc claim và quét bù. Cập nhật brief biên tập để phong cách lưu trên web được ưu tiên, cùng README, SPEC, PLAN và quyết định kỹ thuật. Giữ nguyên form số bài/ngày và giờ đăng đã có.

## Quyết định
SQLite là nguồn cấu hình chung cho dashboard và Hermes runner trên cùng máy; thay đổi chỉ áp dụng cho lượt mới. Các cổng kiểm tra tính chính xác, URL nguồn, ảnh và kiểm duyệt nằm trong code và brief cố định, không chuyển thành lựa chọn có thể tắt trên web. Giá trị kết nối bí mật không xuất hiện trên form.

## Kiểm chứng
`python -m unittest discover -s tests -q` với `REUP_FACEBOOK_AUTH_MODE=page_token`, `REUP_HERMES_DISCOVERY_ENABLED=0`: 132 test đạt. `git diff --check`: sạch. Test trực tiếp xác nhận form lưu/từ chối giá trị sai, prompt Hermes nhận phong cách/ưu tiên mới và giới hạn 25 ứng viên được áp dụng.

## Còn lại
Chưa thử với Hermes/9Router thật hoặc đăng Facebook thật. Bài đã soạn/lên lịch không tự viết lại. Cần review độc lập trước khi merge vào main.
