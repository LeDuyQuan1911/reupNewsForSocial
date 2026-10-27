# Thiết lập sandbox CI cho PR

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thiết lập môi trường kiểm tra tách biệt cho code mới trước khi triển khai lên máy chạy server. Phạm vi hiện tại là CI trên GitHub-hosted Windows runner; chưa chuyển dịch vụ, lịch đăng hoặc token.

## Thực hiện
Đã thêm `.github/workflows/ci.yml`: PR vào `main` và push lên `main` chạy Python 3.12 trên GitHub-hosted Windows runner, quyền `contents: read`, không giữ credential của checkout, tắt tự động hóa và để trống các biến token/model. Test dùng SQLite tạm và mock thao tác đăng. Cập nhật README, MAP, SPEC, PLAN và quyết định kỹ thuật để ghi rõ phạm vi CI.

## Quyết định
Runner tạm của GitHub được chọn thay vì máy server vì repo công khai; không cấp secret cho code PR. Cố định `REUP_FACEBOOK_AUTH_MODE=page_token` trong job vì test hiện giả định mặc định này và máy phát triển đang dùng System User. CI chỉ kiểm tra code, chưa có CD/staging server.

## Kiểm chứng
Kiểm tra YAML bằng PyYAML đạt; `git diff --check` đạt. Chạy 92 test với cấu hình CI giả lập: lần đầu 5 lỗi do kế thừa chế độ xác thực System User từ máy, sau khi cố định `page_token` chạy lại 92/92 đạt. Chưa thể xác nhận workflow GitHub chạy thật vì chưa commit/push theo yêu cầu hiện tại.

## Còn lại
Một số test vẫn thử đọc trang nguồn công khai và ghi warning khi SSL không xác minh được; không dùng token thật. Chưa cấu hình required status check trên GitHub nên CI chưa chặn merge; cần làm sau khi workflow chạy lần đầu. Chưa có bước kiểm tra và triển khai trên máy server.
