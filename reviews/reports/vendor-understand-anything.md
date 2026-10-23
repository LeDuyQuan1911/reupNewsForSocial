# Báo cáo review: vendor-understand-anything

- Reviewer: Codex (reviewer độc lập)
- Ngày: 2026-10-22
- Base / head: 1bbbc7d14855ab85ae74dddb3fe10487a82a2f9e / working tree chưa commit
- Vòng: độc lập; đã đối chiếu bản sửa
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: `SPEC.md`, manifest/plugin, `.gitignore`, `.understandignore`, `.githooks/post-commit`, ba script mới, tài liệu sử dụng và source vendored liên quan đến thư mục graph. Không đọc worklog tác giả hay giải thích của tác giả trước kết luận này.
- Lệnh đã chạy và kết quả: `node scripts/graph-status.mjs` trả `MISSING` khi repo chưa có graph; `node --check` cho hai script Node đạt; `node scripts/plugins.mjs check` đạt (7 plugin, 2 bật); `git diff --check` không thấy lỗi; `git check-ignore -v` xác nhận `.ua/`, `.understand-anything/`, `node_modules/` và `dist/` được bỏ qua. Sau bản sửa, fixture legacy trong checkout hiện tại cho `CURRENT`; `mark-graph-stale.mjs` ghi marker vào đúng thư mục legacy với head khớp. Đã dọn fixture.
- Phần chưa kiểm chứng: code mới chưa commit nên `git diff` thường không hiển thị file untracked; đã đọc trực tiếp các file đó. Không chạy setup cài dependencies hoặc tạo graph thật vì sẽ ghi vào repo và gọi LLM. Probe bằng Git repo tạm ban đầu bị sandbox từ chối ghi Git metadata; phép kiểm tra sau sửa dùng checkout hiện tại.

## Phát hiện

### P2 — Kiểm tra trạng thái bỏ qua graph ở thư mục legacy

- Vị trí: `scripts/graph-status.mjs:23` và `scripts/mark-graph-stale.mjs:23`
- Điều kiện kích hoạt / cách tái hiện: checkout đã có graph trong `.understand-anything/` từ phiên bản cũ; đây là đường dẫn mà source vendored tiếp tục đọc và ghi khi thư mục đó tồn tại. Chạy `node scripts/graph-status.mjs` trước khi dùng graph, rồi commit một thay đổi.
- Kết quả thực tế: `graph-status.mjs` chỉ đọc `.ua/` nên báo `MISSING` dù graph và `meta.json` legacy tồn tại; hook ghi `stale.json` vào `.ua/` tách rời graph. Sau khi skill cập nhật graph trong `.understand-anything/`, lệnh trạng thái vẫn không thể báo `CURRENT`.
- Kết quả mong đợi: script trạng thái và hook chọn cùng thư mục dữ liệu mà skill vendored chọn, để phát hiện graph cũ và xác nhận cập nhật hoàn tất.
- Bằng chứng: `packages/core/src/persistence/index.ts:21` chọn `.understand-anything/` nếu tồn tại; `skills/understand/SKILL.md` mục 1.7 cũng dùng quy tắc đó. Hai script mới cố định `.ua/`.
- Độ chắc chắn: cao về sai lệch đường dẫn; chưa chạy probe end-to-end do sandbox không cho tạo Git repo tạm.
- Hướng sửa gợi ý (nếu có): dùng cùng quy tắc chọn thư mục như source vendored cho cả hai script, và kiểm tra bằng fixture legacy.

## Đối chiếu sau phản hồi tác giả

Hai script hiện chọn `.understand-anything/` nếu thư mục này tồn tại, khớp `resolveUaDirName` của source vendored. Tôi đã tạo fixture legacy tạm trong checkout hiện tại: `graph-status.mjs` báo `CURRENT` khi `meta.json` khớp HEAD; `mark-graph-stale.mjs` ghi `stale.json` trong legacy với head đúng. Fixture đã được xóa. Phát hiện P2 **đã sửa trong working tree hiện tại**.

## Kết luận cho chủ repo

Không còn phát hiện mở trong phạm vi kiểm tra của working tree. Cần đưa bản sửa vào commit dự kiến tích hợp; setup và cập nhật graph thật chưa được kiểm chứng. Reviewer không quyết định merge.
