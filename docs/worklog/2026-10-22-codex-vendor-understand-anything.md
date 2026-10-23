# Đưa Understand Anything vào repo

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: bị chặn

## Yêu cầu và phạm vi
Đưa source Understand Anything vào repo để dùng cùng một phiên bản mà không phải tải lại plugin bên ngoài; cho phép tạo/làm mới graph khi cần đọc map. Sau commit có thay đổi, đánh dấu graph cũ và làm mới ở lần dùng tiếp theo theo lựa chọn của người dùng.

## Thực hiện
Đã chép 374 file được Git theo dõi từ upstream vào `vendor/understand-anything/` (plugin và MIT license), thêm provenance `UPSTREAM.md`. Tạo plugin quy trình `codebase-graph`, `.understandignore`, `.githooks/post-commit`, `.gitattributes` giữ LF cho hook trên Windows, các script setup/trạng thái/đánh dấu stale và tài liệu sử dụng. Cập nhật README, MAP, SPEC, PLAN, quyết định dự án, manifest plugin và `.gitignore`. Hook ghi `stale.json` trong thư mục graph; agent chạy skill vendored khi cần graph. Review độc lập phát hiện script bỏ qua đường dẫn legacy; đã sửa cả hai script và tài liệu, reviewer xác nhận không còn phát hiện mở.

## Quyết định
Chọn vendor source thay vì submodule để bản source nằm trong clone repo. Người dùng chọn đánh dấu cũ sau commit và làm mới khi dùng, vì cập nhật ngữ nghĩa có thể cần LLM. Graph giữ cục bộ trong `.ua/`, hoặc `.understand-anything/` với dữ liệu cũ; source vendored tự bị loại khỏi phân tích để tránh graph phình lớn.

## Kiểm chứng
Đối chiếu hash của 374 file vendored với checkout upstream: khớp. `node scripts/plugins.mjs check` đạt (7 plugin, 2 bật); `node --check` cho hai script mới đạt; `node scripts/mark-graph-stale.mjs` ghi đúng HEAD và danh sách 6 file của commit hiện tại; `node scripts/graph-status.mjs` báo MISSING khi chưa có graph. Fixture legacy `.understand-anything/` báo CURRENT và ghi stale đúng thư mục, sau đó đã dọn; reviewer độc lập xác nhận P2 đã sửa. Commit kiểm thử `6642293` kích hoạt post-commit hook thực, marker có đúng HEAD và hai path thay đổi; hook được lưu với mode `100755`. PowerShell 5.1 parse script setup và báo core chưa build. `git diff --check` cho file đã theo dõi đạt; diff vendored giữ nguyên hai dòng whitespace của upstream. `pnpm install --offline --frozen-lockfile` thất bại vì sandbox từ chối tạo symlink vào pnpm store ngoài workspace; thử store trong workspace tiếp tục thiếu metadata offline cho `@babel/compat-data`.

## Còn lại
Chưa build được runtime vendored vì sandbox thiếu gói offline; chưa tạo graph baseline. Đã bật `core.hooksPath=.githooks` cho checkout này sau khi xác nhận không có hook cũ. Hai worklog không theo dõi của nhiệm vụ khác trong checkout này được giữ nguyên. Không push hoặc merge lên `main` trong nhiệm vụ này.
