# Giải thích CI sau merge và rollback

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Làm rõ liệu CI lần hai thất bại có tự chạy lại commit cũ hay không.

## Thực hiện
Đối chiếu workflow `.github/workflows/ci.yml` và quy trình đã mô tả trong tài liệu đính kèm. Workflow chỉ chạy test khi có push lên `main`, không có bước triển khai hoặc rollback.

## Quyết định
Phân biệt ba trạng thái: commit trên `main`, phiên bản server đang chạy, và kết quả CI. CI đỏ không đảo Git; cơ chế triển khai dự kiến sẽ giữ server ở commit cũ. Rollback chỉ cần khi đã chuyển sang bản mới rồi kiểm tra sau triển khai thất bại.

## Kiểm chứng
Đọc lại cấu hình workflow trong lượt trước; chạy `node scripts/check-worklog.mjs` trước khi bàn giao.

## Còn lại
Cơ chế tự triển khai và rollback trên server chưa được xây, nên hiện tại CI đỏ chỉ báo lỗi.
