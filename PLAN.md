# Kế hoạch

## Đã xong

- [x] Kiểm tra trạng thái repo hiện tại.
- [x] Tạo điểm vào và bản đồ ngữ cảnh cho Codex/Claude Code.
- [x] Đặt quy tắc bảo vệ secrets và cập nhật tài liệu.
- [x] Thêm quy trình chung cho Codex, Antigravity và Claude Code.
- [x] Tạo cơ chế plugin bật/tắt và bộ 5 plugin quy trình khởi đầu.
- [x] Bắt buộc ghi worklog riêng cho từng nhiệm vụ của mọi agent.
- [x] Áp dụng ruleset GitHub chỉ cho chủ repo merge PR vào `main`.
- [x] Bật plugin review độc lập và tạo mẫu yêu cầu/báo cáo review.
- [x] Đưa source Understand Anything vào repo và tạo lệnh đánh dấu/kiểm tra graph.
- [x] Đưa khung `setupSourceVibeCode` vào repo `reupNewsForSocial` và ghi mục tiêu sản phẩm ban đầu.
- [x] Dựng dashboard Flask/SQLite để nhập RSS/Atom, tìm bài và loại trùng URL.
- [x] Thêm nguồn Anthropic từ sitemap chính thức và repo GitHub nổi bật qua Search API.
- [x] Tạo bản nháp, lên lịch/đăng ngay và adapter Facebook Page có bước kiểm duyệt LLM trước khi gửi.
- [x] Chặn đăng tin có tiêu đề tương tự bài đã đăng trong 14 ngày gần đây.

## Tiếp theo

- [ ] Chốt các điểm còn mở trong `SPEC.md`: giọng văn, ngôn ngữ, quy tắc kiểm duyệt, cách đăng vào trang cá nhân/nhóm.
- [ ] Xếp hạng bài và bổ sung nhận diện trùng nội dung khác tiêu đề.
- [ ] Kiểm tra viết bài và kiểm duyệt với 9Router/model thật; chọn giọng văn và ngôn ngữ đầu ra.
- [ ] Kiểm tra đăng thật lên Facebook Page bằng quyền và token của chủ dự án.
- [ ] Kiểm chứng giải pháp đăng tự động lên trang cá nhân và nhóm bằng phiên trình duyệt của chủ dự án.
- [ ] Build runtime vendored và bật Git hook cục bộ khi quyền cho phép; kiểm tra một commit thực tế.
- [ ] Chọn plugin cần bật cho dự án thực tế.
- [ ] Chốt phạm vi bản đầu, stack và tiêu chí hoàn thành.
- [ ] Thiết kế cấu trúc source theo nhu cầu thực tế; cập nhật `MAP.md`.
- [ ] Xây một lát chức năng nhỏ, chạy kiểm tra và ghi kết quả.

Chỉ thêm MCP, skill, agent chuyên biệt hoặc script tự động khi có nhu cầu rõ ràng.
