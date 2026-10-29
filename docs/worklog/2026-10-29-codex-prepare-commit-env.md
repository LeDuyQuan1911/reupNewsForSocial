# Chuẩn bị commit thay đổi cấu hình .env

- Ngày: 2026-10-29
- Agent: Codex
- Trạng thái: bị chặn

## Yêu cầu và phạm vi
Xử lý thay đổi nạp `.env`, rà soát thay đổi chờ commit trên nhánh hiện tại và tạo commit an toàn, không đưa secret hoặc dữ liệu tạm vào Git.

## Thực hiện
Rà soát nhánh và các file thay đổi. Sửa `run.py` để chỉ nạp `.env` khi chạy server, tránh import lúc thu thập test làm lộ cấu hình máy vào CI test. Giữ `.env` ngoài Git; không chạm vào dữ liệu test tạm. Chuẩn bị danh sách code, test và tài liệu để commit.

## Quyết định
Giữ các thay đổi code trước đó trên nhánh `codex/hermes-web-research` và không đưa `.env` hoặc thư mục `tests/tmp*` vào commit. Không xóa `.git/index.lock` vì thao tác xóa lock đã bị automatic approval review từ chối trước đó; không dùng đường vòng để sửa index.

## Kiểm chứng
109 unit test qua với cấu hình CI giả; dashboard smoke check qua; `py_compile` và parser PowerShell qua; `git diff --check` không báo lỗi whitespace; quét 46 file ứng viên không thấy token/key hiện hành hoặc mẫu giống secret. `git check-ignore .env` xác nhận file cấu hình không vào Git. `.git/index.lock` là file rỗng có dấu thời gian từ 2026-10-28; không thấy tiến trình Git đang chạy. Lệnh `git add` trả `fatal: Unable to create .../.git/index.lock: File exists`.

## Còn lại
Chưa tạo được commit do `.git/index.lock` đang chặn việc ghi index; cần người dùng xử lý lock trong checkout này, sau đó stage đúng file và commit. Không push, PR hoặc merge trong yêu cầu này.
