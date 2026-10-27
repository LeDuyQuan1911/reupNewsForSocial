# Mô tả quy trình CI/CD chuẩn cho dự án

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích chi tiết quy trình từ sửa code, PR, CI, merge đến máy server tự cập nhật, kiểm tra và khôi phục; chỉ khảo sát và hướng dẫn, chưa triển khai CD.

## Thực hiện
Đã đọc README/MAP/SPEC/PLAN, plugin bật, quy trình review, `governance/github-main-ruleset.json` và `.github/workflows/ci.yml`. Đối chiếu tài liệu chính thức GitHub về bản merge thử của PR, required checks/nhánh cập nhật, workflow push `main` và cách bảo vệ nhánh. Xây mô tả chi tiết luồng đề xuất gồm PR → CI → review → merge → CI trên SHA thật của `main` → máy server tự kéo SHA đủ điều kiện → backup/kiểm tra/khởi động → giám sát và rollback.

## Quyết định
Không thay đổi cấu hình hoặc quyền GitHub trong yêu cầu giải thích. Dùng `main` làm nguồn triển khai được đề xuất, nhưng chỉ lấy commit cụ thể khi CI của chính SHA đó thành công; không yêu cầu tạo Release riêng. Giữ máy server làm nơi chạy lịch duy nhất và giữ dữ liệu, secrets tách khỏi code.

## Kiểm chứng
Đã kiểm tra workflow có trigger PR và push `main`; ruleset JSON hiện yêu cầu PR nhưng chưa có required status checks. Chưa chạy test vì không thay code.

## Còn lại
Cần triển khai required check/strict update, cơ chế poll/deploy, kiểm tra sau triển khai, backup/rollback và cấu hình máy đích. Workflow CI còn uncommitted trong working tree; chưa xác nhận chạy trên GitHub. Dữ liệu SQLite/ảnh và token vẫn nằm trên từng máy, nên việc di chuyển ban đầu cần kế hoạch riêng.
