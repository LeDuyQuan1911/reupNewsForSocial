# Giải thích CI trước và sau merge

- Ngày: 2026-10-27
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Xác nhận cách hiểu của chủ dự án về bước 1–4: CI trên PR và lần chạy CI sau khi merge vào `main`.

## Thực hiện
Đã đối chiếu đoạn giải thích được gửi, `.github/workflows/ci.yml`, `SPEC.md`, `README.md` và tài liệu GitHub về sự kiện `pull_request`/`push`. Workflow hiện khai báo CI cho PR vào `main` và push lên `main`.

## Quyết định
Giải thích rõ: khi PR còn mở, CI trên PR có thể chạy nhưng chưa có CI của commit mới trên `main`; lần chạy thứ hai chỉ phát sinh sau khi thực sự merge, vì lúc đó mới có push lên `main`. CI sau merge không phải điều kiện quyết định merge; nó kiểm tra commit thực tế sau merge.

## Kiểm chứng
Đã đọc cấu hình workflow và đối chiếu tài liệu GitHub Actions. Chạy `node scripts/check-worklog.mjs` trước khi bàn giao.

## Còn lại
Workflow hiện là file chưa theo dõi trong checkout này; chưa có bằng chứng workflow đã chạy trên GitHub. Chưa có tác vụ tự triển khai server.
