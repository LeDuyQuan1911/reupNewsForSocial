# Giải thích luồng server tự kéo bản phát hành

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích phương án CI/CD để máy chuyên chạy server tự lấy bản phát hành, trong khi máy hiện tại là nơi sửa code; chưa triển khai.

## Thực hiện
Đối chiếu luồng phát hành với repo hiện tại: GitHub công khai, script Windows cho dashboard/9Router/Hermes, dữ liệu SQLite và ảnh trong `data/`, bí mật trong biến môi trường User. Tham khảo tài liệu chính thức GitHub Release API, workflow release và SQLite backup để nêu các bước có thể triển khai.

## Quyết định
Mô tả thiết kế dự kiến gồm CI trước phát hành, chủ repo phát hành bản đã duyệt, máy server kiểm tra release qua kết nối đi ra, kiểm tra hash, dừng job an toàn, sao lưu dữ liệu, cập nhật code, health-check và rollback code khi lỗi. Không khởi động CD hoặc thay đổi lịch đăng trong nhiệm vụ giải thích.

## Kiểm chứng
Đã kiểm tra source vận hành và tài liệu chính thức; không chạy test do không đổi code.

## Còn lại
Chưa xây pipeline hoặc script triển khai. Cần chốt máy đích, nhịp kiểm tra bản mới và chế độ tự áp dụng hay chờ duyệt trước khi triển khai.
