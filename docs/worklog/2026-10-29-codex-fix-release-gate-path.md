# Sửa release gate nhận CI push trên main

- Ngày: 2026-10-29
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Máy server từ chối mở dashboard vì `release_gate.py` không nhận CI push xanh cho commit `main`; sửa điều kiện đối chiếu workflow mà vẫn giữ yêu cầu đúng SHA/branch/event và CI thành công.

## Thực hiện
So sánh phản hồi API của run CI push trên `main` với điều kiện trong `scripts/cd/release_gate.py`; xác nhận API trả path không có `@refs`. Cập nhật điều kiện path và unit test cho cả hai dạng, không đổi điều kiện SHA/branch/event/status. Ghi quyết định và cập nhật PLAN.

## Quyết định
Chấp nhận đúng `.github/workflows/ci.yml` hoặc cùng đường dẫn có hậu tố `@`; từ chối tên workflow khác. Không cho server bỏ qua CI khi gate lỗi.

## Kiểm chứng
Ba unit test release gate qua; gọi gate với commit `904c26f4` đã qua CI trả `CI passed`; toàn bộ 111 unit test và dashboard smoke check qua; `git diff --check` sạch.

## Còn lại
Cần mở PR, CI/review, merge theo quyết định chủ repo, server kéo commit mới rồi chạy lại `update-server.ps1 -StartOnly`. Facebook token vẫn trống và tự động đăng vẫn tắt.
