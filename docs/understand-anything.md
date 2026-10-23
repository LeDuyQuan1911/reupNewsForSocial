# Understand Anything trong repo

Source plugin đã có tại `vendor/understand-anything/understand-anything-plugin/`, cố định theo [UPSTREAM.md](../vendor/understand-anything/UPSTREAM.md). Mọi agent dùng cùng source trong repo; không cần clone plugin vào thư mục cá nhân. Node.js >= 22 và pnpm >= 10 vẫn cần để cài dependencies từ lockfile, build core một lần trên mỗi máy. Dependencies và output build bị Git bỏ qua.

## Chuẩn bị trên Windows

```powershell
& .\scripts\setup-understand-anything.ps1
& .\scripts\setup-understand-anything.ps1 -Check
```

Script build core nếu chưa có và bật hook Git `post-commit` cho checkout này. Git không tự cài hook từ repository khi clone, nên bước bật hook là bắt buộc một lần. Nếu checkout đã có `core.hooksPath` hoặc `post-commit` riêng, script dừng để bạn gộp hook thủ công, không ghi đè. Trên macOS/Linux, chạy `pnpm install --frozen-lockfile` và `pnpm --filter @understand-anything/core build` trong thư mục plugin, rồi `git config --local core.hooksPath .githooks` sau khi kiểm tra hook hiện có.

## Khi cần đọc graph

`MAP.md` là bản đồ thủ công, luôn đọc trực tiếp. Graph Understand Anything chỉ được tạo hoặc làm mới khi một agent cần dùng:

1. Chạy `node scripts/graph-status.mjs` ở checkout cần phân tích.
2. Nếu trạng thái `MISSING` hoặc `STALE`, đặt `CLAUDE_PLUGIN_ROOT` thành đường dẫn tuyệt đối tới `vendor/understand-anything/understand-anything-plugin`. Trong worktree, đặt thêm `UNDERSTAND_NO_WORKTREE_REDIRECT=1` để output ở đúng worktree.
3. Đọc `vendor/understand-anything/understand-anything-plugin/skills/understand/SKILL.md` và thực hiện `/understand --language vi --no-auto-update` bằng agent đang dùng. Với Codex, có thể yêu cầu bằng lời: “Dùng skill understand vendored trong repo để cập nhật graph”.
4. Chạy lại `node scripts/graph-status.mjs`. Chỉ dùng graph sau khi lệnh báo `CURRENT`; nếu còn cũ, xem source trực tiếp và ghi giới hạn.

Ví dụ thiết lập biến môi trường trong PowerShell cho phiên agent:

```powershell
$env:CLAUDE_PLUGIN_ROOT = (Resolve-Path .\vendor\understand-anything\understand-anything-plugin).Path
$env:UNDERSTAND_NO_WORKTREE_REDIRECT = '1'
```

## Sau commit

`.githooks/post-commit` chạy `scripts/mark-graph-stale.mjs`. Nếu commit đổi file được theo dõi, script ghi `stale.json` trong thư mục graph của checkout hiện tại. Hook không gọi LLM và không chặn commit nếu đánh dấu lỗi. Khi agent cần graph lần sau, so sánh `meta.json` với `HEAD` qua `graph-status.mjs` rồi chạy cập nhật incremental. Graph và dấu stale nằm trong `.ua/` với dự án mới, hoặc `.understand-anything/` nếu thư mục dữ liệu cũ đã tồn tại; cả hai đều không commit lên Git.

Nếu commit tạo qua công cụ không chạy Git hook, `graph-status.mjs` vẫn phát hiện graph cũ bằng commit hash. Khi chưa có graph, lần đầu phân tích toàn repo có thể tốn nhiều token. `--no-auto-update` giữ hook LLM của upstream tắt; quy trình repo chỉ làm mới khi cần đọc graph. Đồ thị là nguồn hỗ trợ tìm code, không thay thế diff/source/test trong review.
