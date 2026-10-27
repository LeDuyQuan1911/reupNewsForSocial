# Làm rõ tự triển khai sau khi merge vào main

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích liệu CI kiểm tra PR rồi merge vào `main` có thể khiến máy server tự tải bản code mới để chạy hay không; chưa triển khai.

## Thực hiện
Đối chiếu tài liệu GitHub về PR test merge, required checks và workflow sau push vào `main`; phân biệt thiết kế tự triển khai theo commit `main` với thiết kế cần tạo Release riêng. Không thay đổi source, workflow hoặc máy server.

## Quyết định
Đề xuất đúng luồng người dùng muốn: CI PR phải xanh và là điều kiện merge; sau merge, CI xác nhận commit `main` mới; máy server chỉ kéo đúng SHA đã qua CI rồi kiểm tra/khởi động. Release riêng là tùy chọn, không bắt buộc.

## Kiểm chứng
Đã xác minh khái niệm PR merge ref, push main và required checks bằng tài liệu chính thức GitHub. Không chạy test vì không đổi code.

## Còn lại
Chưa cài pipeline. Khi triển khai cần chốt máy đích, chính sách cập nhật, bảo toàn dữ liệu và bảo đảm chỉ máy server chạy lịch Hermes.
