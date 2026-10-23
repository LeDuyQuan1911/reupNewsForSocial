# Bản đồ dự án

Trạng thái: khung làm việc cho agent và dashboard đọc RSS/Atom cục bộ.

| Vị trí | Vai trò |
| --- | --- |
| `README.md` | Cách bắt đầu và tổng quan repo |
| `AGENTS.md` | Quy tắc làm việc cho coding agent |
| `CLAUDE.md` | Điểm vào cho Claude Code |
| `SPEC.md` | Yêu cầu và câu hỏi cần xác định |
| `PLAN.md` | Các bước triển khai và trạng thái |
| `MULTI_AGENT.md` | Cách chia nhiệm vụ và dùng worktree cho nhiều agent |
| `project.plugins.json` | Danh sách plugin quy trình đang bật |
| `plugins/<id>/plugin.json` | Tên và mô tả của từng plugin |
| `plugins/<id>/INSTRUCTIONS.md` | Quy trình chỉ áp dụng khi plugin được bật |
| `scripts/plugins.mjs` | Lệnh liệt kê, bật/tắt và kiểm tra plugin |
| `vendor/understand-anything/understand-anything-plugin/` | Source skill, dashboard và core của Understand Anything |
| `docs/understand-anything.md` | Cách build runtime và cập nhật graph khi cần |
| `scripts/setup-understand-anything.ps1` | Build runtime và bật hook cục bộ trên Windows |
| `.githooks/post-commit` | Đánh dấu graph cũ sau commit có thay đổi |
| `scripts/mark-graph-stale.mjs` | Ghi dấu stale theo commit và file đã đổi |
| `scripts/graph-status.mjs` | Kiểm tra graph khớp commit hiện tại hay chưa |
| `docs/worklog/README.md` | Quy ước ghi nhật ký bắt buộc |
| `docs/worklog/<date>-<agent>-<task>.md` | Kết quả và kiểm chứng của từng nhiệm vụ |
| `scripts/check-worklog.mjs` | Kiểm tra cấu trúc và độ hoàn tất của worklog |
| `governance/github-main-ruleset.json` | Cấu hình ruleset GitHub cho quyền merge vào `main` |
| `governance/README.md` | Quy trình PR và giới hạn quyền merge |
| `reviews/README.md` | Quy trình review hai lượt để giảm thiên vị |
| `reviews/templates/REQUEST.md` | Mẫu giao việc trung tính cho reviewer |
| `reviews/templates/REPORT.md` | Mẫu báo cáo có bằng chứng và kết quả kiểm tra |
| `scripts/review-brief.mjs` | Tạo yêu cầu review từ hai Git ref mà không kèm danh tính tác giả |
| `contexte/decisions.md` | Nhật ký quyết định dự án |
| `livrables/README.md` | Quy ước lưu sản phẩm đầu ra |
| `.gitignore` | Loại trừ secrets và file sinh ra cục bộ |
| `run.py` | Chạy dashboard Flask trên `127.0.0.1:5000` |
| `app/web.py` | Route dashboard, thêm nguồn và tìm bài |
| `app/feeds.py` | Đọc và chuẩn hóa RSS/Atom |
| `app/anthropic.py` | Đọc sitemap chính thức của Anthropic và metadata bài viết |
| `app/github.py` | Tìm repo mới nổi qua GitHub Search API |
| `app/llm.py` | Viết bản nháp và kiểm duyệt văn bản/ảnh qua endpoint chat tương thích OpenAI |
| `app/facebook.py` | Đăng lên Facebook Page qua Graph API |
| `app/media.py` | Tìm ảnh bài báo, chụp repo, tạo ảnh dự phòng và lưu JPEG cục bộ |
| `app/queue.py` | Xử lý bài đến lịch, trạng thái đăng và lỗi |
| `app/database.py` | Schema SQLite, nguồn tin và bài báo |
| `app/templates/`, `app/static/style.css` | Giao diện dashboard và biên tập |
| `.env.example` | Tên biến môi trường cho LLM và Facebook Page |
| `tests/test_app.py` | Kiểm tra parser, chống trùng và route cơ bản |
| `data/reup.sqlite3` | Dữ liệu cục bộ, được Git bỏ qua |

Luồng hiện tại: người dùng bấm “Tìm bài mới” → `app/web.py` gọi adapter RSS/Atom, Anthropic hoặc GitHub → mục được lưu theo URL duy nhất trong SQLite → dashboard hiển thị tối đa 100 mục mới được tìm thấy. Từ một mục, người dùng tạo bản nháp → `app/media.py` tải ảnh bài báo, chụp repo hoặc tạo ảnh thẻ tiêu đề và lưu trong `data/media/` → người dùng xem trước, sửa nội dung hoặc gọi LLM viết lại → lên lịch hoặc đăng ngay → LLM có khả năng xem ảnh kiểm duyệt cả caption và ảnh → `app/facebook.py` gửi ảnh và nội dung lên Page → cập nhật trạng thái. Chạy `python run.py`; kiểm tra `python -m unittest discover -s tests -v`.
