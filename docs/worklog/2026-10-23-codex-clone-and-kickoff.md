# Clone và khởi động dự án

- Ngày: 2026-10-23
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Clone `LeDuyQuan1911/setupSourceVibeCode`, dùng khung trong repo `reupNewsForSocial` và bắt đầu xác định sản phẩm.

## Thực hiện
Đã clone repository, đọc hướng dẫn, bản đồ, đặc tả, kế hoạch và hai plugin đang bật. Sau khi người dùng xác nhận nơi phát triển, đã chép bộ khung vào repo `reupNewsForSocial`, kiểm tra đủ các file được Git theo dõi rồi dọn bản clone lồng bên trong. Đã tạo dashboard Flask/SQLite: thêm nguồn RSS/Atom, tìm bài, lưu metadata, loại trùng URL và hiển thị bài kèm liên kết gốc. Nguồn OpenAI, Google AI, Anthropic và GitHub được thêm sẵn. Đã thêm bản nháp, viết lại và kiểm duyệt LLM, lên lịch/đăng ngay lên Facebook Page, chặn tin giống bài đã đăng trong 14 ngày. Đã cập nhật `README.md`, `MAP.md`, `SPEC.md`, `PLAN.md` và nhật ký quyết định.

Review độc lập phát hiện nguy cơ đăng trùng khi Facebook đã nhận bài nhưng phản hồi bị mất, cùng lỗi test trên checkout sạch. Đã sửa bằng trạng thái `uncertain`, yêu cầu đối chiếu Page trước khi thử lại, và dùng thư mục tạm trong `tests/`.

## Quyết định
Giữ repo `reupNewsForSocial` và remote hiện có làm nơi phát triển. Chọn Flask + SQLite cho bản chạy cục bộ. Lấy metadata từ RSS/Atom thay vì sao chép toàn văn. Chưa chọn cơ chế đăng Facebook trang cá nhân/nhóm vì API chính thức không hỗ trợ tương ứng.

## Kiểm chứng
Đã so sánh mọi file được Git theo dõi trong clone với bản sao ở repo đích: không thiếu file. `node scripts/plugins.mjs check` báo cấu hình hợp lệ với 7 plugin, 2 đang bật. `python -m unittest discover -s tests -v`: 7 bài kiểm tra thành công, gồm chặn bài trùng, không gửi bài bị kiểm duyệt chặn và giữ trạng thái cần đối chiếu khi mất phản hồi Facebook. Flask test client trả HTTP 200 cho dashboard và trang biên tập. Đã đọc thử RSS OpenAI và Google AI qua mạng, parser nhận lần lượt 1316 và 20 mục tại thời điểm kiểm tra; GitHub Search API trả 20 repo; sitemap và metadata Anthropic trả 15 bài. Browser trong phiên này không truy cập được localhost để kiểm tra bố cục trực quan.

## Còn lại
Đã xem một bài mẫu trên trang Hỏi Dân it và dùng nét viết làm hướng dẫn ban đầu. Người dùng muốn để phần đăng nhập/kết nối Facebook sau. Cần cấu hình 9Router/model thật, quyền và token Page của chủ dự án để kiểm tra đăng thật; chưa có cơ chế đăng tự động trang cá nhân/nhóm và LinkedIn. Bộ kiểm duyệt LLM là bước lọc sơ bộ, không chứng nhận nội dung chắc chắn phù hợp mọi quy tắc nền tảng. Bài viết chưa đọc toàn văn nguồn và chưa kiểm tra bố cục bằng browser cục bộ.
