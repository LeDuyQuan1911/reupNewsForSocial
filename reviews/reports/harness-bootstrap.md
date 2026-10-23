# Báo cáo review: harness-bootstrap

- Reviewer: Codex (reviewer độc lập)
- Ngày: 2026-10-22
- Base / head: d4d15b3a5dcce8964ad83deac64a0d2a4a851189 / 9c9b8bad70fd3a19632c211e1d2e3327f9d8bd44
- Vòng: độc lập; đã đối chiếu bản sửa chưa commit
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff `main...HEAD`, `SPEC.md`, hướng dẫn agent và review, cấu hình plugin/ruleset, ba script Node; không đọc worklog, commit message hay giải thích của tác giả trước kết luận này.
- Lệnh đã chạy và kết quả: `node scripts/plugins.mjs check` thành công (6 plugin, 1 bật); `node scripts/plugins.mjs list` đúng cấu hình; `node --check` cho ba script thành công; `git diff --check main...HEAD` thành công; `node scripts/review-brief.mjs main HEAD harness-bootstrap --dry-run` cho SHA và danh sách file đúng. Ở lượt độc lập, probe worklog CRLF thất bại; sau bản sửa chưa commit, probe CRLF và LF đều thành công (exit 0).
- Phần chưa kiểm chứng: chưa thử bật/tắt plugin vì sẽ đổi manifest; chưa xác minh ruleset hiện hành trên GitHub hoặc quyền của tài khoản collaborator; chưa có source ứng dụng hay test sản phẩm.

## Phát hiện

### P2 — Worklog dùng CRLF bị từ chối dù đủ mục

- Vị trí: `scripts/check-worklog.mjs:29`
- Điều kiện kích hoạt / cách tái hiện: tạo worklog hợp lệ với line ending CRLF, phổ biến khi chỉnh Markdown trên Windows; chạy `node scripts/check-worklog.mjs <tên-file.md>`.
- Kết quả thực tế: script báo mục `Yêu cầu và phạm vi` chưa có nội dung, thoát mã 1. Probe `2026-10-22-codex-crlf-probe.md` có đủ năm heading và nội dung; đã xóa probe sau khi kiểm tra.
- Kết quả mong đợi: file hợp lệ được chấp nhận bất kể LF hay CRLF để agent có thể hoàn thành lệnh kiểm tra bắt buộc.
- Bằng chứng: biến `marker` ở dòng 29 nối heading với `\n`, trong khi file CRLF chứa `\r\n`; `indexOf(marker)` trả -1. Probe trả `mục "Yêu cầu và phạm vi" chưa có nội dung`, exit 1.
- Độ chắc chắn: cao
- Hướng sửa gợi ý (nếu có): chuẩn hóa line ending trước khi tách heading hoặc dùng biểu thức chấp nhận cả CRLF.

## Đối chiếu sau phản hồi tác giả

Bản sửa chưa commit tại `scripts/check-worklog.mjs:21` chuẩn hóa `\r\n` và `\r` thành `\n` trước khi tìm heading. Tôi đã đọc diff của đúng dòng sửa, chạy lại probe với cùng cấu trúc worklog bằng CRLF và LF: cả hai được chấp nhận (exit 0); `node --check scripts/check-worklog.mjs` đạt. Phát hiện P2 được **xác nhận đã sửa trong working tree hiện tại**. Commit head ghi ở đầu report vẫn chứa lỗi; cần đưa bản sửa vào commit được review trước khi tích hợp.

## Kết luận cho chủ repo

Không còn phát hiện đang mở trong bản working tree đã đối chiếu. Bản sửa CRLF chưa nằm trong head commit của report; điều phối viên cần bảo đảm commit dự kiến tích hợp chứa dòng sửa và kiểm tra lại trên ref đó. Reviewer không quyết định merge.
