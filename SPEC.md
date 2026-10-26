# Yêu cầu dự án

Trạng thái: **đang phát triển từng bước**. Stack cục bộ đã chọn; một số quyết định nội dung và kết nối Facebook còn mở.

## 5 câu hỏi khởi đầu

1. **Đã trả lời một phần:** hệ thống có thể là workflow hoặc agent, tìm và đọc thông tin từ các website báo, repo GitHub đang được quan tâm và bài viết trên X; tổng hợp, chuyển thành phong cách viết của chủ dự án và đăng lên Facebook, LinkedIn cùng các kênh khác về sau.
2. **Đã trả lời một phần:** chủ dự án muốn hệ thống tự động đăng. Trước khi đăng, hệ thống cần phát hiện bài không phù hợp, ví dụ nội dung bạo lực; có thể dùng LLM để duyệt. Quy tắc xử lý khi bài bị chặn và các thao tác thủ công chưa được chốt.
3. **Đã trả lời một phần:** bản đầu tìm các bài báo, hiển thị trên dashboard, đăng theo lịch và có nút đăng ngay. Nguồn báo cụ thể, kênh đăng và tiêu chí kiểm chứng đăng thành công chưa được chốt.
4. **Đã trả lời:** chạy trên máy cá nhân trước, để agent đề xuất stack, ưu tiên Facebook. Stack bước đầu: Flask + SQLite + RSS/Atom.
5. **Đã trả lời một phần:** cần tự động đăng lên Facebook Page, trang cá nhân và nhóm. Ưu tiên bài từ Anthropic, OpenAI/Codex, Google/Gemini và repo GitHub nổi bật; tránh đăng lặp gần nhau. Nội dung phải phù hợp quy tắc Facebook và LinkedIn. Muốn dùng LLM chi phí thấp, đang cân nhắc 9Router. Chưa có bài mẫu giọng văn, ngôn ngữ đầu ra, ngân sách cụ thể hoặc quy tắc xử lý khi kiểm duyệt không chắc chắn.

## Yêu cầu đã xác nhận

- Với bài báo có video nhúng liên quan và đáng xem, bản nháp cần báo video ở dưới bình luận; sau khi bài Facebook Page đăng thành công, tự bình luận liên kết video. Không thêm lời hứa video khi không tìm được link đủ tin cậy. Nếu kết quả gửi bình luận không rõ, không gửi lại mù để tránh trùng.

- Ưu tiên đăng tự động Facebook Page; đăng nhóm để sau. Người dùng có Page nhưng chưa có Page token. Ứng dụng chấp nhận Page token hợp lệ từ App/tích hợp phù hợp và không bắt buộc tạo App mới; cần chỉ rõ cách lấy, kiểm tra Page cục bộ mà không đưa secret vào repo.

- Có trang Facebook riêng để lưu tên/URL các nhóm dự kiến đăng, chọn/tạm dừng/xóa nhóm và xem trạng thái kết nối Page. Chọn nhóm chưa kích hoạt đăng vào nhóm; adapter và cách đăng cần triển khai riêng.

- Repo giữ snapshot đầy đủ mã nguồn open source Hermes đã thử và có lệnh Windows để cài lại, cấu hình 9Router khi chuyển máy; API key, runtime và dữ liệu phiên Hermes ở ngoài Git.

- Repo phải có ngữ cảnh và quy tắc để coding agent đọc trước khi vibe code.
- Source Understand Anything nằm trong repo và dùng chung cho các agent; commit có thay đổi đánh dấu graph cũ, agent làm mới graph khi cần dùng.
- Dùng khung `setupSourceVibeCode` trong repo `reupNewsForSocial`.
- Mục tiêu sản phẩm ở câu 1 là thu thập thông tin từ báo, GitHub và X; tổng hợp, viết theo phong cách cá nhân và đăng lên Facebook, LinkedIn. Cách vận hành và phạm vi bản đầu chưa được chốt.
- Hệ thống cần tự động đăng sau khi qua bước phát hiện nội dung không phù hợp; người dùng đang cân nhắc dùng LLM cho bước duyệt.
- Bản đầu có dashboard hiển thị các bài báo tìm được, hỗ trợ đăng theo lịch và đăng ngay.
- Bản đầu chạy trên máy cá nhân; cần đăng tự động lên Page, trang cá nhân và nhóm. LinkedIn là kênh dự kiến sau Facebook.
- Nguồn ưu tiên gồm tin chính thức từ các hãng AI lớn và repo GitHub nổi bật. Cần chống đăng lặp trong thời gian ngắn.
- Mở rộng nguồn chính thức với NVIDIA Technical Blog, AWS Machine Learning Blog và Microsoft Research. Các nguồn được quét định kỳ cùng nguồn hiện có; bước nghiên cứu/đánh giá mức độ đáng chú ý bằng AI cần thiết kế riêng vì quét RSS chưa phải tuyển chọn biên tập.
- Tham chiếu giọng viết: trang Facebook [Hỏi Dân it Offical](https://www.facebook.com/askITwithERIC), đặc biệt [bài mẫu về bản vá bảo mật](https://www.facebook.com/photo?fbid=1748385257291798&set=a.553695503427452). Đặc điểm: mở đầu gây chú ý, đoạn ngắn, chút hài hước của dân IT, nêu chi tiết kỹ thuật và việc người đọc nên làm. Không sao chép câu chữ và không tự thêm dữ kiện ngoài nguồn.
- Bản nháp viết mới bằng AI có mở đầu cụ thể, các ý ngắn nêu điểm mới và giá trị với người đọc. LLM tự quyết định có dùng icon hay không, chọn số lượng, vị trí và biểu tượng theo nội dung; không áp quy tắc mỗi dòng một icon hoặc tự chèn icon sau khi model viết. Có 2–5 hashtag liên quan trước liên kết nguồn; nếu model bỏ sót hashtag, ứng dụng bổ sung hashtag dự phòng. Các bài đã viết hoặc đã đăng trước đó không tự thay đổi.
- Bài đăng cần có ảnh bám sát nội dung: thử ảnh từ feed và các ảnh trong bài báo; với repo GitHub, ưu tiên ảnh đủ lớn được dẫn trong README rồi mới chụp trang repo. Nếu không lấy được tư liệu, chỉ tạo ảnh thẻ tiêu đề làm ảnh tạm trong bản nháp.
- Ảnh thẻ chỉ có tiêu đề được xem là ảnh tạm để biên tập, không đủ điều kiện tự động lên lịch hoặc đăng thật. Cần ít nhất một ảnh nguồn, ảnh trong README repo, ảnh chụp repo, ảnh tải lên hoặc ảnh minh họa AI phù hợp với bài trước khi đăng. Ảnh AI cần có điểm nhấn nhận ra ngay khi lướt: tên chủ thể/sản phẩm hoặc nội dung chính của bài, kèm hình thể hiện chi tiết hay luồng xử lý thực sự được nguồn mô tả. Chỉ dùng tên người khi bài nguồn nhắc tới họ; không dùng hình gợi sai sự kiện, địa điểm hay hình trang trí chung chung. Model nhìn ảnh cần từ chối ảnh không liên quan hoặc không chắc chắn.
- Mọi bước AI của ứng dụng liên quan đến ảnh (lập dàn ý ảnh, sinh ảnh khi nguồn không có ảnh, duyệt ảnh trước đăng) gọi các model đã cấu hình qua 9Router trên localhost. Tải ảnh nguồn, chụp repo, đổi định dạng và lưu file là thao tác cục bộ thông thường. Model văn bản/nhìn ảnh không được giả định có khả năng sinh ảnh; sinh ảnh cần model riêng thuộc nhóm `image` của 9Router. Khi model ảnh thiếu hoặc trả kết quả lỗi, chỉ giữ ảnh tạm và không tự đăng bài đó.
- Một bài đăng có thể chứa nhiều ảnh (tối đa 10 cho Facebook Page), thêm từ nguồn, ảnh chụp repo GitHub hoặc tải lên từ máy. Không cho xóa ảnh cuối cùng; bài không có ảnh hợp lệ không được lên lịch hoặc gửi. Mọi ảnh đều phải qua kiểm duyệt trước khi gửi.
- Giao diện cục bộ cần các trang riêng cho tổng quan, tài khoản/kết nối, nguồn thông tin và bài báo; bài đăng và biên tập có trang riêng để danh sách tin không bị gộp vào một màn hình.
- Giao diện cần một luồng trực quan nối nguồn tin → bài báo → kênh đăng → thời điểm dự kiến/thực tế. Bài chưa có nháp hoặc chưa có lịch phải hiển thị trạng thái tương ứng; không thể hiện kênh chưa tích hợp như thể đã có thể đăng.
- Trang Luồng đăng cần ưu tiên tiêu đề bài, nguồn, trạng thái và thao tác tiếp theo; tên cột chỉ xuất hiện một lần trên desktop, còn điện thoại hiển thị từng bài gọn và vẫn giữ đủ thông tin.
- Giao diện phải dễ đọc và thao tác trên desktop lẫn điện thoại: luồng đăng gọn, trạng thái và bước tiếp theo rõ ràng; trang biên tập ưu tiên nội dung bài viết, cho xem toàn bộ nội dung của bài đã lên lịch và phân biệt lịch thử nghiệm với lịch đăng thật.
- Các trang Tổng quan, Bài báo, Luồng đăng, Bài đăng, Nguồn thông tin và Tài khoản dùng chung hệ thống điều hướng, màu sắc, khoảng cách, biểu mẫu và trạng thái. Trên điện thoại phải nhìn thấy đủ mục điều hướng; các trang có liên kết bỏ qua điều hướng để dùng bằng bàn phím.
- Header và thanh điều hướng dùng nền sáng đồng bộ với vùng nội dung; chỉ dùng xanh dương làm điểm nhấn cho thương hiệu và mục đang chọn, tránh mảng xanh đậm chiếm nhiều diện tích.
- Người dùng có thể tạm dừng/bật lại từng nguồn mà vẫn giữ bài báo và bài đăng cũ; trang nguồn cho biết lần quét gần nhất và lỗi quét nếu có. Nguồn tạm dừng không được quét thủ công hoặc tự động.
- URL RSS/Atom do người dùng thêm chỉ được tải từ địa chỉ công khai trên cổng HTTP/HTTPS mặc định; từng lần chuyển hướng cũng phải được kiểm tra để không gọi tới máy cục bộ hoặc mạng riêng.
- Trang Bài đăng cho lọc theo bản nháp, lịch đăng, đã đăng và bài cần xử lý; tìm theo tiêu đề/nội dung và giữ bộ lọc trong URL/phân trang. Dashboard dẫn thẳng tới bài cần xử lý.
- Trang Bài báo cho lọc tin chưa chọn viết hoặc đã có bài đăng, kết hợp với từ khóa/nguồn và giữ bộ lọc khi phân trang.
- Lịch đăng thật và nút đăng ngay chỉ khả dụng khi đã có đủ cấu hình Facebook Page và model viết/duyệt ảnh; lịch thử nghiệm vẫn dùng được khi chưa kết nối. Giao diện biên tập cảnh báo khi rời trang với nội dung chưa lưu hoặc viết lại bằng AI làm thay thế bản nháp.
- Trang Tổng quan là dashboard hoạt động theo từng ngày giờ Bangkok, xem được 7 hoặc 30 ngày. Mỗi ngày có số tin phát hiện, bài viết tạo, bài tự động chuẩn bị đạt và bài đã đăng; ngày không có hoạt động vẫn hiện số 0. Không lặp danh sách tiêu đề bài báo/bài đăng hay khối dịch vụ kết nối trên dashboard.
- Bảng hoạt động theo ngày có một hàng tiêu đề cột chung; các dòng ngày chỉ hiển thị ngày và giá trị, kể cả khi xem trên điện thoại.
- Có thể lên lịch thử nghiệm cho một bài đã viết lại và có ảnh AI. Bài thử hiển thị giờ hẹn nhưng không được bộ chạy lịch hoặc nút đăng ngay gửi lên Facebook.
- Ảnh cũng phải đi qua bước kiểm duyệt bằng model nhìn ảnh trước khi đăng; nếu bước này lỗi hoặc không chắc chắn, hệ thống không gửi lên Facebook.
- Luồng tìm tin, viết bài và xếp lịch cần chạy tự động trên máy cá nhân, tối đa 6 bài/ngày. Người dùng chưa có Page ID/token nên phần gửi thật chỉ có thể hoạt động sau khi kết nối Page.
- Trước khi tạo bản nháp tự động, model văn bản đánh giá một lô tin mới từ tiêu đề/tóm tắt RSS, lưu thứ tự ưu tiên và lý do; nguồn tin được phân bố trong sáu vị trí đầu. Nếu model lỗi hoặc trả kết quả không hợp lệ, hệ thống dùng thứ tự theo độ mới và phân bố nguồn. Trang Bài báo cho xem kết quả và phân biệt đánh giá AI với dự phòng. Điểm này không chứng nhận đã đọc hoặc xác minh toàn văn.
- Bài kẹt ở `publishing` hơn 45 phút xuất hiện trong nhóm Cần xử lý; người dùng chuyển sang trạng thái cần đối chiếu, kiểm tra Facebook Page rồi xác nhận đã đăng hoặc chưa đăng. Hệ thống không tự thử gửi lại trong tình huống không rõ kết quả.

## Giới hạn kỹ thuật đang xác minh

- Meta có API đăng lên Page. API đăng tự động lên trang cá nhân đã bị loại bỏ và Groups API đã ngừng hỗ trợ; khả năng dùng trình duyệt để tự động hóa trang cá nhân/nhóm cần kiểm chứng riêng và có thể bị thay đổi bởi giao diện hoặc chính sách của Meta.
- Dashboard hiện tại đọc metadata RSS/Atom từ OpenAI và Google AI, sitemap Anthropic và repo GitHub mới tạo có nhiều sao. Danh sách GitHub là kết quả Search API, không phải bảng Trending chính thức.
- Đã có bản nháp, viết lại và kiểm duyệt qua endpoint LLM tương thích OpenAI, lên lịch/đăng ngay lên Facebook Page, cùng chặn tiêu đề tương tự bài đã đăng trong 14 ngày. Chưa kiểm tra với LLM và Page token thật; chưa có adapter cho trang cá nhân/nhóm hoặc LinkedIn. Bài được viết lại từ tiêu đề/tóm tắt feed, chưa đọc toàn văn.

Khi nhận câu trả lời, thay phần câu hỏi bằng yêu cầu cụ thể, tiêu chí chấp nhận và những gì nằm ngoài phạm vi bản đầu tiên. Không lưu secrets tại đây.
