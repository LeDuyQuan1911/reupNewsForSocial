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
| `vendor/hermes-agent/` | Snapshot mã nguồn Hermes v0.22.5, bao gồm license và installer upstream |
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
| `.gitattributes` | Giữ nguyên một file CRLF đặc biệt để Git tree của Hermes vendored khớp upstream |
| `.github/workflows/ci.yml` | Chạy bộ test Python trên Windows runner tạm cho PR vào `main` và commit mới trên `main`, không nạp token hoặc chạy lịch đăng |
| `scripts/cd/release_gate.py` | Kiểm tra đúng SHA `main` có workflow push CI thành công qua GitHub API |
| `scripts/cd/update-server.ps1` | Máy server Windows fetch `main`, tạm dừng Hermes, sao lưu SQLite, triển khai hoặc phục hồi phiên bản cũ |
| `scripts/cd/install-updater.ps1` | Cài Scheduled Task kiểm tra bản mới mỗi 5 phút bằng tài khoản sở hữu Hermes |
| `scripts/cd/backup_db.py`, `scripts/cd/smoke.py` | Sao lưu/phục hồi SQLite và kiểm tra ứng dụng bằng DB tạm |
| `docs/deployment.md` | Quy trình kích hoạt CI gate và cài CD trên máy server Windows |
| `docs/research-brief.md` | Ngữ cảnh và đầu ra có cấu trúc cho lượt Hermes tìm tin trên web |
| `app/hermes_research.py` | Gọi Hermes chỉ với công cụ web và xác minh URL, ngày đăng, metadata bài gốc trước khi lưu |
| `run.py` | Chạy dashboard Flask trên `127.0.0.1:5000` |
| `app/local_env.py`, `scripts/load-env.ps1` | Nạp `.env` tại repo vào tiến trình dashboard/Hermes, ưu tiên giá trị file hơn môi trường User cũ |
| `scripts/start-local-services.ps1` | Khởi động 9Router, bảo đảm Hermes gateway sẵn sàng nếu repo đã giao lịch tự động, rồi mở dashboard; dùng cho tác vụ đăng nhập Windows |
| `scripts/setup-hermes.ps1` | Dùng installer vendored để cài bản Hermes cố định trên Windows và cấu hình endpoint/model 9Router từ biến môi trường |
| `scripts/start-hermes.ps1` | Mở Hermes tại thư mục repo để tự nạp ngữ cảnh biên tập trong `AGENTS.md` |
| `scripts/install-hermes-automation.ps1` | Cài Hermes cron, gateway tự khởi động và chuyển quyền điều phối tự động từ dashboard |
| `scripts/hermes-automation-job.py` | Runner được chép vào Hermes scripts để gọi chu trình tự động và xử lý bài đến giờ |
| `docs/editorial-brief.md` | Yêu cầu giọng viết được gửi nguyên vẹn trong mỗi lượt Hermes viết nháp |
| `scripts/configure-facebook-page.ps1` | Nhập kín Page token hoặc lấy Page token bằng User token khi Graph Explorer không hiện kết quả, xác minh tên/ID Page qua Graph API rồi lưu biến môi trường User trên Windows |
| `scripts/configure-facebook-system-user.ps1` | Nhập kín System User token, tìm đúng Page qua `/me/accounts`, xác minh Page token và bật chế độ System User trong biến User Windows |
| `app/web.py` | Route tổng quan, bài báo, luồng đăng, bài đăng, nguồn, Hermes, tài khoản và thao tác xuất bản |
| `app/hermes_control.py` | Đọc trạng thái Hermes cron và chỉ điều khiển job đã xác thực thuộc repo |
| `app/templates/hermes.html` | Trang trạng thái, thao tác Hermes, lịch đăng và quét nguồn thủ công |
| `app/static/hermes-status.js` | Tải trạng thái Hermes sau khi mở trang và cập nhật nút điều khiển/lịch sử |
| `app/static/posting-times.js` | Tăng giảm các ô chọn giờ theo số bài/ngày và mở đồng hồ chọn giờ của trình duyệt |
| `app/feeds.py` | Đọc/chuẩn hóa RSS/Atom, kiểm tra địa chỉ công khai và cố định IP khi tải feed/chuyển hướng |
| `app/anthropic.py` | Đọc sitemap chính thức của Anthropic và metadata bài viết |
| `app/github.py` | Tìm repo mới nổi qua GitHub Search API |
| `app/llm.py` | Chuẩn bị dữ kiện và kiểm tra đầu ra bản nháp Hermes; các bước AI khác gọi endpoint chat 9Router |
| `app/hermes_writer.py` | Chạy Hermes một lượt để viết nội dung bài đăng theo hướng dẫn biên tập |
| `app/source_content.py` | Đọc trích đoạn bài gốc hoặc README GitHub trước khi viết bản nháp |
| `app/facebook.py` | Lấy Page token từ System User khi chọn chế độ này; xác minh, đăng ảnh/bài và bình luận qua Graph API |
| `app/static/facebook-page.js` | Tải tên và trạng thái xác minh Page sau khi trang Facebook hiển thị |
| `app/facebook_groups.py` | Kiểm tra và chuẩn hóa URL nhóm Facebook trước khi lưu |
| `app/media.py` | Tìm ảnh bài báo, chụp repo, tạo ảnh dự phòng và lưu JPEG cục bộ |
| `app/video.py` | Tìm video nhúng trong bài báo, kiểm tra URL và chọn video liên quan qua 9Router |
| `app/queue.py` | Xử lý bài đến lịch, trạng thái đăng và lỗi |
| `app/discovery.py` | Quét nguồn đang bật cho nút thủ công và tiến trình tự động, lưu trạng thái quét từng nguồn |
| `app/automation.py` | Quét nguồn một lần mỗi ngày giờ Bangkok, chuẩn bị theo mức bài/ngày đã lưu và xếp giờ đăng đã chọn |
| `app/research.py` | Đánh giá tiêu đề/tóm tắt tin mới theo lô bằng model văn bản, xếp thứ tự đa dạng nguồn và dùng thứ tự dự phòng khi model lỗi |
| `app/database.py` | Schema SQLite, cấu hình số bài/giờ đăng, nguồn tin và nhóm Facebook đích, bài báo, ảnh, hàng đợi và thống kê theo ngày Bangkok |
| `app/templates/base.html`, `app/static/style.css`, `app/static/ui-refresh.css`, `app/static/site-redesign.css` | Điều hướng chung và thiết kế bàn biên tập cho desktop, điện thoại |
| `app/static/editor.js` | Cảnh báo nội dung biên tập chưa lưu trước khi rời trang hoặc để Hermes viết lại |
| `app/templates/dashboard.html`, `articles.html`, `article.html` | Tổng quan, danh sách và chi tiết bài báo |
| `app/templates/workflow.html` | Bảng nguồn, bài báo, trạng thái, kênh, thời điểm và thao tác theo dữ liệu thật |
| `app/templates/posts.html`, `post.html` | Danh sách bài đăng và trang biên tập |
| `app/templates/sources.html`, `account.html` | Quản lý nguồn tin và trạng thái kết nối |
| `app/templates/facebook.html`, `app/static/facebook.css` | Hướng dẫn kết nối Page trước, rồi quản lý nhóm đích dự kiến |
| `.env.example` | Mẫu cấu hình cho `.env` cục bộ; `.env` được Git bỏ qua |
| `tests/test_app.py` | Kiểm tra parser, chống trùng và route cơ bản |
| `data/reup.sqlite3` | Dữ liệu cục bộ, được Git bỏ qua |

Luồng hiện tại: nút “Tìm báo / repo mới” quét ngay, còn Hermes cron gọi `scripts/hermes-automation-job.py` để quét tự động một lần trong mỗi ngày Bangkok → `app/discovery.py` → adapter RSS/Atom, Anthropic hoặc GitHub → mục được lưu theo URL duy nhất trong SQLite. Người dùng có thể chọn bài thủ công. Nếu bật tự động, `app/research.py` đánh giá theo lô metadata tin mới và phân bố nguồn → `app/automation.py` chọn số tin/ngày theo cấu hình SQLite, tạo bản nháp và ảnh, dùng `app/video.py` tìm video nhúng phù hợp, gọi Hermes viết nội dung và model 9Router duyệt từng ảnh, rồi xếp lịch theo các giờ đã chọn khi có Page. `app/queue.py` kiểm duyệt tất cả ảnh lần nữa khi đến giờ → `app/facebook.py` gửi 1–10 ảnh và nội dung trong một bài Page; nếu có video và bài đã đăng thành công, gửi tiếp link video vào bình luận và lưu trạng thái riêng. Bài ở `publishing` quá 45 phút chỉ được chuyển sang đối chiếu thủ công, không tự gửi lại. `run.py` chỉ mở dashboard khi đã có marker Hermes; nếu chưa chuyển quyền thì giữ scheduler cũ. Kiểm tra `python -m unittest discover -s tests -v`.

Trước khi Hermes viết bản nháp thủ công hoặc tự động, `app/source_content.py` thử đọc trích đoạn trang nguồn/README; khi không đọc được thì dùng metadata đã lưu. `app/hermes_writer.py` gửi dữ kiện và `docs/editorial-brief.md` vào Hermes qua stdin.
