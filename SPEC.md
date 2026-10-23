# Yêu cầu dự án

Trạng thái: **đang phát triển từng bước**. Stack cục bộ đã chọn; một số quyết định nội dung và kết nối Facebook còn mở.

## 5 câu hỏi khởi đầu

1. **Đã trả lời một phần:** hệ thống có thể là workflow hoặc agent, tìm và đọc thông tin từ các website báo, repo GitHub đang được quan tâm và bài viết trên X; tổng hợp, chuyển thành phong cách viết của chủ dự án và đăng lên Facebook, LinkedIn cùng các kênh khác về sau.
2. **Đã trả lời một phần:** chủ dự án muốn hệ thống tự động đăng. Trước khi đăng, hệ thống cần phát hiện bài không phù hợp, ví dụ nội dung bạo lực; có thể dùng LLM để duyệt. Quy tắc xử lý khi bài bị chặn và các thao tác thủ công chưa được chốt.
3. **Đã trả lời một phần:** bản đầu tìm các bài báo, hiển thị trên dashboard, đăng theo lịch và có nút đăng ngay. Nguồn báo cụ thể, kênh đăng và tiêu chí kiểm chứng đăng thành công chưa được chốt.
4. **Đã trả lời:** chạy trên máy cá nhân trước, để agent đề xuất stack, ưu tiên Facebook. Stack bước đầu: Flask + SQLite + RSS/Atom.
5. **Đã trả lời một phần:** cần tự động đăng lên Facebook Page, trang cá nhân và nhóm. Ưu tiên bài từ Anthropic, OpenAI/Codex, Google/Gemini và repo GitHub nổi bật; tránh đăng lặp gần nhau. Nội dung phải phù hợp quy tắc Facebook và LinkedIn. Muốn dùng LLM chi phí thấp, đang cân nhắc 9Router. Chưa có bài mẫu giọng văn, ngôn ngữ đầu ra, ngân sách cụ thể hoặc quy tắc xử lý khi kiểm duyệt không chắc chắn.

## Yêu cầu đã xác nhận

- Repo phải có ngữ cảnh và quy tắc để coding agent đọc trước khi vibe code.
- Source Understand Anything nằm trong repo và dùng chung cho các agent; commit có thay đổi đánh dấu graph cũ, agent làm mới graph khi cần dùng.
- Dùng khung `setupSourceVibeCode` trong repo `reupNewsForSocial`.
- Mục tiêu sản phẩm ở câu 1 là thu thập thông tin từ báo, GitHub và X; tổng hợp, viết theo phong cách cá nhân và đăng lên Facebook, LinkedIn. Cách vận hành và phạm vi bản đầu chưa được chốt.
- Hệ thống cần tự động đăng sau khi qua bước phát hiện nội dung không phù hợp; người dùng đang cân nhắc dùng LLM cho bước duyệt.
- Bản đầu có dashboard hiển thị các bài báo tìm được, hỗ trợ đăng theo lịch và đăng ngay.
- Bản đầu chạy trên máy cá nhân; cần đăng tự động lên Page, trang cá nhân và nhóm. LinkedIn là kênh dự kiến sau Facebook.
- Nguồn ưu tiên gồm tin chính thức từ các hãng AI lớn và repo GitHub nổi bật. Cần chống đăng lặp trong thời gian ngắn.
- Tham chiếu giọng viết: trang Facebook [Hỏi Dân it Offical](https://www.facebook.com/askITwithERIC), đặc biệt [bài mẫu về bản vá bảo mật](https://www.facebook.com/photo?fbid=1748385257291798&set=a.553695503427452). Đặc điểm: mở đầu gây chú ý, đoạn ngắn, chút hài hước của dân IT, nêu chi tiết kỹ thuật và việc người đọc nên làm. Không sao chép câu chữ và không tự thêm dữ kiện ngoài nguồn.
- Bài đăng cần có ảnh: ưu tiên tải ảnh đại diện từ bài báo, tự chụp trang repo GitHub khi là tin về repo, và cho xem trước trên dashboard trước khi gửi lên Facebook. Nếu không truy cập được ảnh nguồn, tạo ảnh thẻ tiêu đề từ dữ kiện đã có.
- Ảnh cũng phải đi qua bước kiểm duyệt bằng model nhìn ảnh trước khi đăng; nếu bước này lỗi hoặc không chắc chắn, hệ thống không gửi lên Facebook.

## Giới hạn kỹ thuật đang xác minh

- Meta có API đăng lên Page. API đăng tự động lên trang cá nhân đã bị loại bỏ và Groups API đã ngừng hỗ trợ; khả năng dùng trình duyệt để tự động hóa trang cá nhân/nhóm cần kiểm chứng riêng và có thể bị thay đổi bởi giao diện hoặc chính sách của Meta.
- Dashboard hiện tại đọc metadata RSS/Atom từ OpenAI và Google AI, sitemap Anthropic và repo GitHub mới tạo có nhiều sao. Danh sách GitHub là kết quả Search API, không phải bảng Trending chính thức.
- Đã có bản nháp, viết lại và kiểm duyệt qua endpoint LLM tương thích OpenAI, lên lịch/đăng ngay lên Facebook Page, cùng chặn tiêu đề tương tự bài đã đăng trong 14 ngày. Chưa kiểm tra với LLM và Page token thật; chưa có adapter cho trang cá nhân/nhóm hoặc LinkedIn. Bài được viết lại từ tiêu đề/tóm tắt feed, chưa đọc toàn văn.

Khi nhận câu trả lời, thay phần câu hỏi bằng yêu cầu cụ thể, tiêu chí chấp nhận và những gì nằm ngoài phạm vi bản đầu tiên. Không lưu secrets tại đây.
