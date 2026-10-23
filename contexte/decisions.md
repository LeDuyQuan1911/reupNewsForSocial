# Quyết định dự án

Ghi mỗi quyết định quan trọng theo mẫu dưới đây.

### 2026-10-23 — Bắt đầu bằng dashboard cục bộ

- Bối cảnh: chủ dự án muốn tìm bài báo, xem trên dashboard và về sau đăng theo lịch hoặc đăng ngay; bản đầu chạy trên máy cá nhân.
- Quyết định: dùng Flask và SQLite cho lát chức năng đầu; đọc RSS/Atom từ nguồn có feed, lưu metadata và URL gốc, loại trùng theo URL.
- Lý do: ít thành phần cần vận hành trên máy cá nhân, đủ để kiểm chứng luồng nhập nguồn → tìm bài → hiển thị trước khi nối LLM và Facebook.
- Hệ quả / khi nào xem lại: cần thiết kế thêm lịch đăng và xử lý tiến trình nền; nguồn không có RSS (như Anthropic) và repo GitHub sẽ có adapter riêng. Chưa chọn cơ chế đăng trang cá nhân/nhóm.

### 2026-10-23 — Ảnh cho mỗi bài đăng

- Bối cảnh: chủ dự án muốn bài đăng có ảnh từ bài báo hoặc ảnh chụp repo.
- Quyết định: lưu một JPEG riêng cho mỗi bản nháp; ưu tiên ảnh nguồn, dùng Chrome headless chụp repo GitHub, và tạo ảnh thẻ tiêu đề khi nguồn chặn truy cập. Gửi ảnh kèm caption qua Facebook Page Photos API.
- Lý do: ảnh đã lưu cục bộ giúp xem trước và giữ nguyên nội dung khi bài chờ lịch; ảnh dự phòng bảo đảm không đăng bài chỉ có chữ khi nguồn ảnh không khả dụng.
- Hệ quả / khi nào xem lại: cần Chrome để chụp repo; chưa kiểm thử Photos API với token Page thật. Ảnh nguồn có thể thay đổi hoặc bị chặn, và người dùng cần kiểm tra ảnh trước khi đăng.

### 2026-10-22 — Merge main bằng PR thông thường

- Bối cảnh: ruleset `Restrict updates` khiến PR hiện nút bypass; chủ repo muốn merge bằng nút thường mà vẫn là người duy nhất quyết định.
- Quyết định: giữ yêu cầu PR, chặn xóa/force push; bỏ `Restrict updates` và bypass actor. Chỉ chủ repo có quyền Write/Admin, người khác gửi PR từ fork công khai.
- Lý do: với repo thuộc tài khoản cá nhân, collaborator có quyền Write và có thể merge PR. Giới hạn quyền Write duy trì quyền merge độc quyền mà không cần bypass.
- Hệ quả / khi nào xem lại: người đóng góp không push branch trực tiếp vào repo gốc. Mời thêm collaborator sẽ thay đổi quyền merge; cần xem lại cấu hình nếu chuyển repo sang organization.

### 2026-10-22 — Lưu Understand Anything trong repo

- Bối cảnh: chủ repo muốn mọi agent dùng cùng source mà không phải clone plugin riêng; sau commit có thay đổi graph cần được làm mới khi dùng.
- Quyết định: vendor `understand-anything-plugin/` ở commit upstream cố định. Hook sau commit chỉ ghi `stale.json` trong thư mục graph (`.ua/`, hoặc `.understand-anything/` nếu đã tồn tại); agent kiểm tra commit hash và cập nhật graph khi cần. Graph giữ cục bộ.
- Lý do: source có thể review và dùng chung; quá trình cập nhật có thể cần LLM nên không chạy âm thầm trong Git hook. Cách này hoạt động với Codex, Antigravity và Claude qua quy tắc repo.
- Hệ quả / khi nào xem lại: dependencies và hook phải được thiết lập một lần trên mỗi clone vì Git không tự kích hoạt hook từ source. Khi có source ứng dụng, tạo graph baseline và kiểm tra incremental; nếu muốn chia sẻ graph, rà soát dữ liệu trước khi đổi `.gitignore`.

## Mẫu

### YYYY-MM-DD — Tên quyết định

- Bối cảnh:
- Quyết định:
- Lý do:
- Hệ quả / khi nào xem lại:
