# Kế hoạch

## Đã xong

- [x] Nối lập dàn ý và sinh ảnh dự phòng với model văn bản/ảnh trên 9Router localhost; cấu hình model ảnh riêng, thử tạo ảnh thật và thay ảnh bản nháp #1 bằng kết quả 9Router.

- [x] Thay ảnh AI trừu tượng của bản nháp OpenAI–NASK bằng ảnh có tên hai tổ chức và ba bước nghiên cứu nhìn thấy ngay; ghi tiêu chí điểm nhấn cho ảnh tạo mới.

- [x] Ưu tiên ảnh thật trong bài báo hoặc README repo, thử ảnh khác khi ảnh đầu không dùng được, rồi mới chụp repo; bổ sung kiểm tra mức độ liên quan của ảnh trước khi đăng.

- [x] Bỏ quy tắc icon đầu mỗi dòng và phần tự chèn icon; để LLM chọn cách dùng phù hợp từng bài.

- [x] Thay ảnh thẻ chữ của bản nháp OpenAI–NASK bằng ảnh minh họa AI; chặn tự lên lịch và gửi bài chỉ có ảnh thẻ tạm.

- [x] Từng thử đặt icon ở đầu mỗi dòng bản nháp AI; đã thay bằng quyền quyết định cách dùng icon cho LLM.

- [x] Làm mới giọng viết bài AI với cách mở bài đa dạng, icon thay đổi theo bài và không áp số lượng cố định.

- [x] Bổ sung icon và hashtag cho các bản nháp AI tạo sau này; giữ bài đã đăng nguyên trạng.

- [x] Ưu tiên trang kết nối Facebook Page và thêm script nhập kín, kiểm tra Page token dạng chỉ đọc trên Windows.

- [x] Thêm trang Facebook để quản lý danh sách nhóm đích dự kiến đăng; phân biệt rõ cấu hình đích với chức năng đăng nhóm chưa có.

- [x] Thêm script setup Hermes có thể chạy lại từ repo trên Windows, pin bản đã thử và cấu hình 9Router qua biến môi trường.
- [x] Đưa snapshot đầy đủ source Hermes v0.22.5 vào `vendor/hermes-agent/` để có thể đọc code ngay trong repo.

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
- [x] Tìm video nhúng phù hợp trong bài báo, thêm chỉ dẫn vào bản nháp và gửi liên kết ở bình luận sau khi bài Page đăng thành công; giữ trạng thái riêng để tránh bình luận trùng.
- [x] Chặn đăng tin có tiêu đề tương tự bài đã đăng trong 14 ngày gần đây.
- [x] Review độc lập bản đầu và xử lý lỗi retry có thể đăng trùng sau timeout.
- [x] Thêm ảnh từ bài báo, ảnh chụp repo hoặc ảnh thẻ tiêu đề; xem trước và chuẩn bị gửi ảnh cùng bài Page.
- [x] Tách giao diện thành trang tổng quan, bài báo, bài đăng, nguồn thông tin và tài khoản/kết nối.
- [x] Thêm trang luồng đăng thể hiện nguồn, bài báo, kênh Facebook Page và giờ hẹn/đã đăng.
- [x] Thêm tiến trình quét nguồn theo giờ, tự chuẩn bị tối đa 6 bài/ngày và xếp giờ đăng khi có Page.
- [x] Thử viết lại một bài và tạo ảnh AI, lên lịch thử nghiệm có cờ chặn gửi Facebook.
- [x] Hỗ trợ 1–10 ảnh cho bài đăng, kiểm duyệt từng ảnh và gửi nhiều ảnh trong một bài Facebook Page.
- [x] Làm mới bố cục dashboard, luồng đăng và trang biên tập để dễ đọc trên desktop và điện thoại.
- [x] Rút gọn trang Tổng quan, bỏ danh sách bài báo/bài đăng để tập trung vào số liệu vận hành.
- [x] Chuyển Tổng quan thành dashboard 7/30 ngày với số tin, bài tạo, bài tự động đạt và bài đã đăng từng ngày; bỏ khối dịch vụ.
- [x] Chuyển bảng theo ngày sang một hàng tiêu đề cột chung, bỏ nhãn lặp trong từng dòng.
- [x] Bổ sung ba feed chính thức về AI và nghiên cứu công nghệ vào nguồn mặc định.
- [x] Sắp lại trang Luồng đăng thành bảng dễ quét trên desktop và mục gọn trên điện thoại, nêu rõ trạng thái và thao tác.
- [x] Đồng bộ thiết kế toàn bộ dashboard, danh sách, trang chi tiết và tài khoản theo hai skill frontend-design và web-design-guidelines; kiểm tra ở desktop và điện thoại.
- [x] Làm lại giao diện bằng bảng màu xanh mực/xanh dương và font Bahnschrift cục bộ, giữ menu đủ mục trên điện thoại.
- [x] Chuyển header và điều hướng từ mảng xanh đậm sang nền sáng, đồng bộ với vùng nội dung; giữ dấu chọn xanh dương trên desktop và điện thoại.
- [x] Thêm lọc/tìm hàng đợi bài đăng, cảnh báo bài cần xử lý và trạng thái kết nối trước khi đặt lịch thật.
- [x] Thêm lọc bài báo theo tiến độ chưa chọn viết/đã tạo bài đăng.
- [x] Cho tạm dừng/bật lại nguồn mà giữ dữ liệu cũ; hiển thị lần quét và lỗi của từng nguồn.
- [x] Kiểm tra và cố định địa chỉ IP công khai khi tải RSS/Atom, kể cả sau chuyển hướng.
- [x] Đánh giá theo lô tiêu đề/tóm tắt tin mới bằng model văn bản, lưu lý do chọn và phân bố nguồn trong sáu vị trí đầu; có thứ tự dự phòng khi model lỗi.
- [x] Cho đối chiếu thủ công bài ở `publishing` quá 45 phút, hiển thị trong nhóm Cần xử lý và tránh tự gửi lại.

## Tiếp theo

- [ ] Chốt các điểm còn mở trong `SPEC.md`: mẫu giọng văn bổ sung, quy tắc kiểm duyệt, cách đăng vào trang cá nhân/nhóm.
- [ ] Bổ sung nhận diện trùng nội dung khi tiêu đề khác nhau.
- [ ] Nâng bước đánh giá metadata thành nghiên cứu có kiểm chứng toàn văn và độ tin cậy nguồn.
- [ ] Kiểm tra viết bài và kiểm duyệt với 9Router/model thật; chọn giọng văn và ngôn ngữ đầu ra.
- [ ] Kiểm tra đăng thật lên Facebook Page bằng quyền và token của chủ dự án.
- [ ] Kiểm chứng giải pháp đăng tự động lên trang cá nhân và nhóm bằng phiên trình duyệt của chủ dự án.
- [ ] Build runtime vendored và bật Git hook cục bộ khi quyền cho phép; kiểm tra một commit thực tế.
- [ ] Chọn plugin cần bật cho dự án thực tế.

Chỉ thêm MCP, skill, agent chuyên biệt hoặc script tự động khi có nhu cầu rõ ràng.
