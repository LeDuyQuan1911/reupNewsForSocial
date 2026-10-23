# Commit thay đổi cục bộ

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng yêu cầu commit các thay đổi hiện có trong repo. Chỉ tạo commit cục bộ trên branch hiện tại; không push, tạo PR hoặc merge.

## Thực hiện
Rà các file đã sửa và file mới trên branch `codex/initial-dashboard`: luồng tự động, trang workflow, lịch thử nghiệm không đăng, ảnh nhiều tấm cho bài đăng, tài liệu và các worklog trước. Chuẩn bị một commit cục bộ chứa toàn bộ thay đổi không bị Git bỏ qua.

## Quyết định
Gộp các thay đổi liên tiếp của cùng ứng dụng vào một commit vì chúng đã được triển khai và kiểm thử cùng nhau. Giữ cơ sở dữ liệu, ảnh cục bộ và biến môi trường ngoài Git. Không push hoặc merge theo đúng phạm vi yêu cầu.

## Kiểm chứng
`node scripts/plugins.mjs check`: hợp lệ. `python -m unittest discover -s tests -v`: 30/30 đạt. `git diff --check`: đạt. Kiểm tra 39 file thay đổi bằng mẫu token/key/private key: không phát hiện. `git check-ignore` xác nhận cơ sở dữ liệu và ảnh cục bộ được bỏ qua. `node scripts/check-worklog.mjs --all`: các nhật ký trước hợp lệ; nhật ký này được kiểm tra riêng trước commit.

## Còn lại
Chưa kiểm thử gửi nhiều ảnh lên Facebook Page thật vì thiếu Page ID/token. Plugin `independent-review` yêu cầu reviewer khác trước khi thay đổi code được merge vào `main`; commit cục bộ chưa phải merge.
