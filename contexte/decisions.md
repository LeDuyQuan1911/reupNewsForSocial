# Quyết định dự án

Ghi mỗi quyết định quan trọng theo mẫu dưới đây.

### 2026-10-26 — Link video trong bình luận Page

- Bối cảnh: chủ dự án muốn chỉ dẫn video trong bài và đặt link dưới bình luận khi bài báo có video hay.
- Quyết định: chỉ chọn video nhúng trực tiếp trong trang bài báo hoặc YouTube/Vimeo được nhúng, dùng model 9Router đánh giá tính liên quan từ metadata. Lưu URL theo bản nháp, thêm dòng chỉ dẫn vào nội dung. Sau khi Facebook xác nhận bài đăng, gửi link thành bình luận Page và lưu trạng thái bình luận độc lập.
- Lý do: tránh chỉ dẫn tới video không tồn tại; tách lỗi bình luận khỏi trạng thái bài để không đăng trùng bài. Phản hồi bình luận không rõ phải đối chiếu, không tự retry.
- Hệ quả / khi nào xem lại: chưa đánh giá trực tiếp hình/âm thanh trong video và chưa kiểm chứng quyền bình luận với Page token thật; một số player riêng không có metadata nhúng sẽ cần dán URL thủ công.

### 2026-10-26 — Đánh giá metadata trước khi viết và đối chiếu bài kẹt

- Bối cảnh: chọn tin thuần theo thời gian dễ lấy nhiều bài từ cùng một nguồn; bài ở `publishing` có thể kẹt nếu tiến trình dừng giữa lúc gửi.
- Quyết định: đánh giá tối đa 30 tiêu đề/tóm tắt mới trong một lời gọi model văn bản, lưu điểm/lý do và phân bố nguồn trong sáu vị trí đầu. Kết quả không hợp lệ chuyển sang thứ tự dự phòng theo độ mới/nguồn. Bài `publishing` quá 45 phút chỉ chuyển sang `uncertain` bằng thao tác thủ công; người dùng kiểm tra Page rồi xác nhận kết quả, không tự gửi lại.
- Lý do: giới hạn số lời gọi model, cho thấy căn cứ chọn tin, và tránh tự tạo bài trùng khi phản hồi từ Facebook bị mất.
- Hệ quả / khi nào xem lại: chưa đọc/xác minh toàn văn hoặc đo độ tin cậy nguồn; quyết định đối chiếu vẫn phụ thuộc kiểm tra Page của người dùng. Khi có cơ chế tra cứu ID bài trên Meta, có thể giảm thao tác thủ công.

### 2026-10-26 — Quan sát và điều khiển nguồn tin trong giao diện

- Bối cảnh: nguồn lỗi khi quét tự động chỉ xuất hiện trong log, còn người dùng không thể tạm dừng một nguồn gây nhiễu mà vẫn giữ tin cũ.
- Quyết định: thêm cờ `active` và lần quét/lỗi gần nhất vào bảng `sources`; chỉ quét và chọn bài mới từ nguồn đang bật, không xóa bài báo hay hủy lịch cũ khi tạm dừng. Lỗi hiển thị bằng mô tả chung hoặc mã HTTP để không lộ thông tin riêng trong ngoại lệ. URL RSS/Atom được kiểm tra IP công khai và cố định kết nối, bao gồm từng lần chuyển hướng.
- Lý do: người dùng có thể xác định nguồn hỏng và điều chỉnh đầu vào của luồng tự động ngay trên web.
- Hệ quả / khi nào xem lại: chưa có thao tác sửa URL nguồn; khi cần đổi URL, cần thiết kế cách giữ hoặc chuyển quan hệ với các bài báo cũ.

### 2026-10-26 — Hàng đợi bài đăng và điều kiện xuất bản thật

- Bối cảnh: bản nháp, lịch và lỗi trộn trong một danh sách; khi chưa có Page/model, lịch thật vẫn đặt được nhưng chỉ thất bại khi tới giờ.
- Quyết định: lọc/tìm hàng đợi bằng query URL; nhóm `action` gồm bài blocked, failed, uncertain. Chặn đặt lịch thật/đăng ngay khi thiếu Page hoặc model viết và duyệt ảnh, vẫn cho lịch thử nghiệm. Giao diện mới dùng Bahnschrift cục bộ cùng bảng màu xanh mực/xanh dương, không phụ thuộc font mạng.
- Lý do: người dùng thấy việc cần làm và biết trước điều kiện xuất bản thay vì nhận lỗi muộn.
- Hệ quả / khi nào xem lại: trạng thái `publishing` bị kẹt sau khi tiến trình dừng vẫn cần quy trình đối chiếu an toàn riêng trước khi cho thao tác khôi phục trên web.

### 2026-10-25 — Đếm hoạt động dashboard theo ngày Bangkok

- Bối cảnh: chủ dự án muốn biết mỗi ngày hệ thống tìm và chuẩn bị bao nhiêu bài, thay khối dịch vụ trên Tổng quan.
- Quyết định: nhóm mốc thời gian lưu dạng UTC sang ngày Asia/Bangkok; hiển thị cả ngày không hoạt động trong 7 hoặc 30 ngày. “Bài viết tạo” đếm bản nháp thủ công và tự động theo giờ tạo; “Tự động đạt” đếm job hiện ở trạng thái ready/scheduled theo ngày bắt đầu; “Đã đăng” đếm bài có trạng thái published theo giờ đăng thực tế.
- Lý do: các chỉ số phản ánh các giai đoạn khác nhau, tránh hiểu nhầm bài đã tạo hoặc chuẩn bị đạt là bài đã gửi lên Facebook.
- Hệ quả / khi nào xem lại: chỉ số tự động của một ngày cũ có thể thay đổi nếu trạng thái job được chỉnh về sau; nếu cần lịch sử bất biến, bổ sung mốc hoàn tất cho từng job.

### 2026-10-23 — Nhiều ảnh cho một bài đăng

- Bối cảnh: chủ dự án muốn nhiều ảnh trong một bài, tối thiểu một ảnh, kể cả ảnh chụp repo GitHub.
- Quyết định: thêm bảng `post_images` và tự chuyển ảnh đơn hiện có khi nâng cấp. Giữ các cột ảnh cũ làm ảnh đầu để tương thích. Bản nháp nhận tối đa 10 ảnh, không được bỏ ảnh cuối; lịch và thao tác đăng đòi ít nhất một ảnh. Kiểm duyệt từng ảnh; với nhiều ảnh, tải ảnh chưa xuất bản rồi tạo một bài Page qua `attached_media`.
- Lý do: giữ dữ liệu cũ và đảm bảo toàn bộ ảnh gắn với bài đăng được kiểm tra trước khi gửi.
- Hệ quả / khi nào xem lại: chưa kiểm tra lời gọi nhiều ảnh với Page token thật; lỗi khi đang tải ảnh được giữ ở trạng thái cần đối chiếu để tránh gửi trùng.

### 2026-10-23 — Lịch thử nghiệm không đăng

- Bối cảnh: cần xem trước một bài viết lại bằng AI cùng ảnh minh họa và giờ hẹn, nhưng chưa gửi lên Facebook.
- Quyết định: lưu cờ `test_only` trên bài đăng; hàng đợi và thao tác đăng ngay đều bỏ qua bài mang cờ này. Giao diện phân biệt lịch thử nghiệm với lịch đăng thật; hủy lịch xóa cờ.
- Lý do: bảo đảm bài thử vẫn an toàn khi sau này bổ sung Page ID/token hoặc tới giờ hẹn.
- Hệ quả / khi nào xem lại: lịch thử nghiệm không chiếm khung đăng tự động; cần hủy lịch rồi đặt lịch thật nếu muốn xuất bản.

### 2026-10-23 — Tự động hóa tối đa sáu bài mỗi ngày

- Bối cảnh: chủ dự án muốn luồng tìm, viết và đăng không cần thao tác từng bài; hiện chưa có Page ID/token.
- Quyết định: tiến trình nền quét nguồn mỗi giờ, chuẩn bị tối đa sáu bài đạt mỗi ngày theo giờ Bangkok, chỉ xét tin được phát hiện và đăng trong 48 giờ gần đây, kể cả tin đã lưu trước khi bật nếu chưa có bản nháp. Tạo ảnh, viết và kiểm duyệt trước khi xếp vào sáu khung giờ ban ngày; chỉ xếp lịch khi có cấu hình Page. Bài lỗi/bị chặn giữ lại và không tự gửi; lỗi tạm thời thử lại tối đa ba lần, sau đó có thể chọn bài khác để bù khung còn trống.
- Lý do: giới hạn lượng bài và độ cũ, tránh tự đăng nội dung chưa qua kiểm duyệt hoặc từ nguồn lỗi; giữ nguyên bài thủ công và cơ chế chống đăng trùng hiện tại.
- Hệ quả / khi nào xem lại: tiến trình chỉ chạy khi `run.py` và 9Router còn hoạt động. Chưa kiểm chứng gửi thật lên Facebook Page; cần Page ID/token và kiểm tra quyền API trước khi sử dụng ngoài máy.

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

### 2026-10-26 — Vendor source và setup Hermes có thể mang theo repo

- Bối cảnh: Hermes trước đây được cài riêng trên máy, nên clone repo sang máy khác không có bước dựng lại rõ ràng.
- Quyết định: lưu snapshot đầy đủ source Hermes ở `vendor/hermes-agent/`, bao gồm license MIT và installer; script PowerShell kiểm tra SHA-256 installer, cài đúng commit upstream vào máy và cấu hình provider custom qua biến môi trường.
- Lý do: người dùng muốn xem và mang mã nguồn open source cùng repo, đồng thời dựng lại bản đã kiểm thử mà không commit runtime, dữ liệu cá nhân hoặc API key.
- Hệ quả / khi nào xem lại: repo tăng khoảng 222 MB nội dung và hơn 20.000 file; clone/review nặng hơn. Máy mới vẫn cần Git, internet cho dependencies, 9Router và key riêng. Khi nâng Hermes phải cập nhật snapshot, pin/checksum và thử lại.

### 2026-10-26 — Lưu nhóm Facebook đích trước khi tích hợp đăng nhóm

- Bối cảnh: người dùng muốn chọn nhóm nào cần đăng từ dashboard, trong khi ứng dụng mới có adapter Facebook Page.
- Quyết định: lưu tên/URL và trạng thái chọn nhóm trong SQLite; trang Facebook cho thêm, tạm dừng và xóa. Danh sách này chưa nối vào hàng đợi hay Hermes.
- Lý do: cho phép chuẩn bị đích đăng và tránh hiển thị sai rằng chọn nhóm đồng nghĩa bài sẽ được gửi.
- Hệ quả / khi nào xem lại: cần thiết kế riêng cơ chế đăng nhóm, danh tính đăng, xác nhận quyền và xử lý lỗi trước khi dùng danh sách này để xuất bản.

## Mẫu
### 2026-10-26 — Kết nối Page theo từng bước trước khi tự đăng

- Bối cảnh: người dùng đã có Facebook Page nhưng chưa có Meta App và Page access token; tiến trình tự động đang bật nhưng chưa đủ thông số gửi Page.
- Quyết định: chấp nhận Page token hợp lệ bất kể người dùng có tạo App mới hay dùng App/tích hợp phù hợp sẵn có; hướng dẫn luồng tự lấy token qua Meta App là một lựa chọn. Script PowerShell nhập kín, kiểm tra `GET /<page-id>?fields=id,name` trước khi lưu vào biến môi trường User. Giao diện Facebook ưu tiên Page; phần nhóm vẫn là cấu hình đích tương lai.
- Lý do: giữ secret khỏi repo/chat và tránh nhầm phép kiểm tra thông số với quyền đăng thật.
- Hệ quả / khi nào xem lại: người dùng vẫn phải tạo App và cấp quyền; sau đó cần thử một bài thật có kiểm soát. Kiểm tra đọc không xác nhận quyền xuất bản hoặc hạn token.

### 2026-10-26 — Ảnh thẻ tiêu đề chỉ dùng trong bản nháp

- Bối cảnh: ảnh thẻ chữ tự tạo khi không lấy được ảnh nguồn quá đơn điệu để thu hút người đọc.
- Quyết định: vẫn lưu ảnh này để bản nháp luôn có ảnh xem trước, nhưng yêu cầu ít nhất một ảnh khác trước khi tự lên lịch hoặc gửi lên Facebook Page.
- Lý do: kiểm tra nội dung ảnh bằng model không bảo đảm chất lượng thị giác; tránh tự đăng một ảnh đã biết là kém phù hợp.
- Hệ quả / khi nào xem lại: các bài không có ảnh nguồn cần được bổ sung ảnh thủ công hoặc một dịch vụ tạo ảnh tự động có cấu hình riêng.

### 2026-10-26 — Ảnh bài đăng phải bám sát nguồn

- Bối cảnh: ảnh minh họa chung chung không giúp người đọc hiểu bài và có thể gợi sai nội dung.
- Quyết định: thử nhiều ảnh từ trang báo; với repo, lấy ảnh đủ lớn trong README trước khi chụp trang repo. Bước duyệt ảnh bằng LLM kiểm tra cả mức độ liên quan với nội dung bài. Ảnh AI được tạo thủ công phải mô tả thông tin hoặc quy trình có căn cứ trong nguồn.
- Lý do: ảnh lấy từ nguồn hoặc quy trình được nguồn mô tả giúp bài đăng cụ thể và đáng tin hơn.
- Hệ quả / khi nào xem lại: nếu nguồn không có ảnh và không thể chụp repo, ứng dụng thử model ảnh 9Router theo quyết định sau; nếu bước đó lỗi, bài giữ ảnh tạm và không được đăng thật.

### 2026-10-26 — Sinh ảnh qua model ảnh riêng của 9Router

- Bối cảnh: chủ dự án muốn toàn bộ bước AI về ảnh do ứng dụng cục bộ gọi qua 9Router, không dùng công cụ tạo ảnh của phiên chat.
- Quyết định: dùng model văn bản 9Router lập dàn ý ngắn từ tiêu đề/tóm tắt, gọi model loại `image` qua `/v1/images/generations` trên localhost, rồi dùng model nhìn ảnh 9Router duyệt trước khi đăng. Tên model ảnh lưu trong biến môi trường User `REUP_LLM_IMAGE_MODEL`; nếu không thể sinh ảnh, giữ thẻ tạm và chặn đăng thật theo quy tắc hiện có.
- Lý do: tách khả năng viết/nhìn ảnh khỏi khả năng sinh ảnh và giữ toàn bộ lời gọi AI trong luồng ứng dụng qua router do người dùng cấu hình.
- Hệ quả / khi nào xem lại: 9Router có thể định tuyến đến nhà cung cấp từ xa; không cam kết suy luận offline. Tạo ảnh tốn tài nguyên/model quota; cần theo dõi chất lượng, chi phí và quyền truy cập model khi vận hành.

## Mẫu

### YYYY-MM-DD — Tên quyết định

- Bối cảnh:
- Quyết định:
- Lý do:
- Hệ quả / khi nào xem lại:
