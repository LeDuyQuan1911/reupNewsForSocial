# Quyết định dự án

Ghi mỗi quyết định quan trọng theo mẫu dưới đây.

### 2026-10-27 — Sandbox CI tách khỏi máy đăng bài

- Bối cảnh: chủ dự án muốn kiểm tra PR trước khi máy khác tự nhận code từ `main`; repo hiện chưa có workflow CI và đang dùng Windows cho Hermes/9Router.
- Quyết định: chạy bộ test Python bằng GitHub-hosted Windows runner trên PR và push vào `main`, giới hạn quyền workflow ở mức đọc; job dùng cấu hình giả, tắt tự động đăng và không nhận token Page/9Router. Không dùng máy server làm runner cho PR.
- Lý do: kiểm tra gần hệ điều hành đích mà không cho code PR truy cập dữ liệu hoặc quyền đăng của máy server.
- Hệ quả / khi nào xem lại: test giả lập chưa xác nhận kết nối thật hay quyền Meta; cần thêm bước kiểm tra trên máy đích và cấu hình required status check trước khi xem CI là cổng bắt buộc để merge.

### 2026-10-27 — Khởi động Hermes cùng dịch vụ cục bộ

- Bối cảnh: trang Hermes báo không kết nối CLI khi gateway đã dừng dù dashboard còn mở; lệnh mở dịch vụ trước đó chỉ kiểm tra 9Router và dashboard.
- Quyết định: khi marker giao lịch cho Hermes tồn tại, script khởi động dịch vụ đợi 9Router phản hồi rồi gọi `hermes gateway ensure` trước khi mở dashboard. Nếu gateway không sẵn sàng, báo lỗi thay vì coi hệ thống tự động đang hoạt động.
- Lý do: gateway cần chạy để cron xử lý bài theo lịch, và model cục bộ cần sẵn sàng trước khi job chạy bù.
- Hệ quả / khi nào xem lại: gateway dừng giữa phiên vẫn cần cơ chế giám sát riêng; script được gọi lúc đăng nhập hoặc khi người dùng chủ động mở lại dịch vụ.

### 2026-10-27 — Lượt Hermes tìm bài cho ngày mới

- Bối cảnh: người dùng muốn Hermes tìm bài vào 24:00 một lần và số bài tương ứng lịch đăng ngày đó; job hiện chạy mỗi phút và đã giới hạn một lần quét theo ngày Bangkok.
- Quyết định: hiểu 24:00 là 00:00 của ngày mới tại Bangkok. Giữ job phút để đăng đúng giờ; lượt quét đầu tiên từ 00:00 nhận mục tiêu `posts_per_day` của ngày đó, model xếp hạng tối đa mục tiêu này, và luồng chuẩn bị giới hạn số bài đạt trong ngày. Khi máy tắt hoặc job bận lúc 00:00, lượt tiếp theo chạy bù. Nút quét thủ công không chiếm lượt tự động.
- Lý do: một job Hermes duy nhất duy trì lịch đăng theo phút và tự phục hồi khi bỏ lỡ nửa đêm; thu thập nhiều metadata hơn mục tiêu giúp thay ứng viên không đạt kiểm duyệt.
- Hệ quả / khi nào xem lại: số bài đạt có thể thấp hơn mục tiêu khi nguồn/model lỗi hoặc thiếu tin phù hợp; một lượt quét đã được nhận mà lỗi giữa chừng sẽ không tự quét lại trong cùng ngày.

### 2026-10-27 — Tự tạo ảnh bổ sung khi nguồn thiếu ảnh

- Bối cảnh: ưu tiên nhiều ảnh nguồn vẫn để bài chỉ có một ảnh khi báo/repo cung cấp ít tư liệu; người dùng không muốn tự thêm ảnh.
- Quyết định: sau khi ưu tiên ảnh thật và ảnh chụp repo, thử tạo ảnh bổ sung có góc nhìn khác qua model ảnh 9Router khi chỉ còn một ảnh. Khi không có ảnh thật, thử tạo hai ảnh khác nhau. Bỏ ảnh sinh trùng dữ liệu; mỗi ảnh vẫn phải qua model nhìn ảnh trước khi tự xếp lịch/đăng. Bản nháp cũ còn một ảnh được thử bổ sung khi chuẩn bị đăng, không tự thay bài đã lên lịch hoặc đã đăng.
- Lý do: hệ thống tự hoàn thiện bộ ảnh mà vẫn dùng tư liệu nguồn trước và tránh ảnh minh họa không có căn cứ.
- Hệ quả / khi nào xem lại: một bài có thể vẫn chỉ có một ảnh nếu model tạo ảnh lỗi, trả cùng ảnh hoặc ảnh bổ sung bị kiểm duyệt từ chối; không trì hoãn bài hợp lệ vô hạn chỉ để đạt số lượng ảnh.

### 2026-10-27 — Ưu tiên nhiều ảnh thật cho bản nháp

- Bối cảnh: bài đăng hỗ trợ tối đa 10 ảnh nhưng bước tạo nháp chỉ lưu ảnh đầu tiên; người dùng muốn ưu tiên nhiều ảnh trong một bài.
- Quyết định: khi tạo nháp, thử tối đa ba ảnh khác nhau từ feed/trang báo hoặc README repo; repo ít ảnh thử thêm ảnh chụp trang repo. Bỏ qua URL và dữ liệu ảnh trùng, không tạo thêm ảnh AI chỉ để đủ ba. Ảnh thẻ tiêu đề tạm không được gửi kèm ảnh thật. Khi tự chuẩn bị, ảnh không qua kiểm duyệt được loại nếu còn ít nhất một ảnh đạt; kiểm duyệt lại toàn bộ ảnh còn lại trước khi gửi.
- Lý do: tăng lượng tư liệu hữu ích mà vẫn giữ bài nguồn chỉ có một ảnh hợp lệ hoạt động bình thường và tránh đăng ảnh trùng hoặc trang trí.
- Hệ quả / khi nào xem lại: tải nhiều ảnh làm bước chuẩn bị chậm hơn và mỗi ảnh cần một lượt duyệt bằng model. Nếu nguồn chỉ có một ảnh dùng được, bài vẫn chỉ có một ảnh; người dùng có thể thêm ảnh khác trước khi lên lịch.

### 2026-10-27 — Bình luận đầu tiên cho bài Facebook Page

- Bối cảnh: bài đã có 1–10 ảnh và bình luận video khi tìm thấy video, nhưng bài thông thường chưa có bình luận; chủ dự án muốn mỗi bài có ít nhất một bình luận.
- Quyết định: tạo bình luận đầu tiên cùng bản nháp, để Hermes thử viết dựa trên tiêu đề/tóm tắt và nội dung bài; khi Hermes không khả dụng, dùng liên kết nguồn làm nội dung dự phòng có thể sửa. Chặn lịch đăng thật khi bình luận trống, kiểm duyệt bình luận cùng văn bản và ảnh, chỉ gửi sau khi Meta xác nhận bài đã đăng. Lưu trạng thái/ID bình luận riêng và không tự gửi lại khi kết quả không rõ. Giữ bình luận video riêng.
- Lý do: có bình luận cho cả bài không có video, đồng thời tránh bình luận trùng sau timeout hoặc phản hồi Meta không chắc chắn.
- Hệ quả / khi nào xem lại: bình luận nguồn dự phòng có thể kém hấp dẫn, nên người dùng nên đọc và sửa trước khi đăng; cần thử quyền bình luận trên Page thật. Bài đã đăng trước thay đổi này không tự được thêm bình luận.

### 2026-10-27 — Xác thực System User cho đăng Page tự động

- Bối cảnh: Page token lấy từ phiên User trước đã hết hạn; người dùng muốn chuyển sang System User để Hermes chạy lâu dài.
- Quyết định: lưu System User token trong biến môi trường User trên máy, chọn chế độ xác thực riêng; mỗi lần cần gửi bài hoặc bình luận, lấy Page token cho Page ID đã cấu hình qua `/me/accounts`. Nếu không lấy được token hoặc Page không được gán, dừng gửi thay vì dùng Page token cũ. Script cấu hình xác minh tên/ID Page trước khi bật chế độ.
- Lý do: quyền của System User gắn với App/Page trong Business Portfolio và không phụ thuộc phiên token cá nhân cũ; tách rõ token gốc với Page token dùng để xuất bản.
- Hệ quả / khi nào xem lại: System User quyền Employee đã được gán App CreatePost và Page Duy Quân AppleWatch với quyền nội dung/bình luận; token hiện có hạn 60 ngày. Đã xác minh tên/ID Page và Meta trả task `CREATE_CONTENT`, `MODERATE`; vẫn cần thử một bài thật có kiểm soát vì kiểm tra đọc và task chưa chứng minh yêu cầu đăng ảnh sẽ thành công. Token có thể hết hạn hoặc bị thu hồi, cần theo dõi thời hạn và gia hạn khi cần.

### 2026-10-26 — Hiển thị Page đã lưu và xác minh hiện tại riêng biệt

- Bối cảnh: trang Facebook chỉ báo có thông số, không cho biết Page nào; token hiện có thể hết hạn dù Page ID vẫn được cấu hình.
- Quyết định: hiển thị Page ID và tên đã lưu gắn với đúng ID; gọi Meta Graph API ở nền để xác minh lại tên/ID, rồi hiện trạng thái quyền đọc. Token và danh tính tài khoản cá nhân cấp quyền không được hiển thị. Khi Meta từ chối token, vẫn cho thấy tên đã lưu nhưng đánh dấu chưa xác minh lại.
- Lý do: người dùng nhận ra đích đăng mà không hiểu nhầm cấu hình có sẵn là kết nối còn hoạt động.
- Hệ quả / khi nào xem lại: tên đã lưu có thể cũ nếu Page được đổi tên; lần xác minh thành công sẽ hiện tên hiện tại. Quyền đăng vẫn cần thử bằng một bài riêng.

### 2026-10-26 — Lịch đăng cấu hình được và quét tự động một lần/ngày

- Bối cảnh: mức sáu bài và các khung giờ cố định nằm trong code, Hermes quét nguồn mỗi giờ; chủ dự án muốn chỉnh từ giao diện và chỉ quét tự động một lần mỗi ngày.
- Quyết định: lưu số bài tự động (1–24) và đúng một giờ Bangkok cho từng bài trong SQLite; giờ trùng hoặc cách nhau dưới 30 phút bị từ chối. Hermes cron vẫn thức mỗi phút để xử lý bài đến giờ, nhưng `automation_state` chỉ cho một lượt tìm nguồn trong mỗi ngày Bangkok. Nút tìm báo/repo thủ công không chiếm lượt quét tự động. Cấu hình mới không dời các bài đã xếp lịch.
- Lý do: giờ đăng và mức bài được điều chỉnh mà không sửa code/khởi động lại Hermes; lượt quét thủ công giải quyết nhu cầu tin mới đột xuất.
- Hệ quả / khi nào xem lại: nguồn lỗi trong lần quét ngày đó không tự thử lại trước ngày sau; người dùng có thể bấm quét thủ công. Bài đăng thủ công không tính vào mức tự động.

### 2026-10-26 — Hermes sở hữu lịch vận hành

- Bối cảnh: Hermes đã viết nội dung, nhưng hai thread của `run.py` vẫn quyết định khi nào tìm bài và đăng; đóng dashboard sẽ dừng tự động.
- Quyết định: dùng Hermes cron mỗi phút để gọi runner Python của repo trong chế độ `no-agent`. Runner đọc biến môi trường User, xử lý bài đến giờ và chu trình quét/chuẩn bị; khi marker `data/hermes-automation.enabled` tồn tại, dashboard không tạo thread tự động. Hermes gateway tự khởi động khi đăng nhập Windows. Hermes CLI riêng tiếp tục viết từng bản nháp; model 9Router và code ứng dụng thực hiện các bước ảnh/kiểm duyệt/đăng. Website có trang Hermes đọc trạng thái và điều khiển job qua CLI với tập lệnh cố định; trước mọi thao tác xác nhận ID, script và workdir khớp repo để tránh điều khiển job khác.
- Lý do: Hermes có thể vận hành khi Codex và dashboard đều đóng, không tiêu tốn token cho mỗi lần kiểm tra phút. Các kiểm tra ảnh, giới hạn 6 bài/ngày và trạng thái chống gửi trùng không phụ thuộc vào độ ổn định của một prompt agent.
- Hệ quả / khi nào xem lại: máy và 9Router vẫn phải chạy; lịch sẽ ngừng nếu Hermes gateway không chạy. Chuyển repo qua máy khác cần chạy lại installer lịch để trỏ đúng thư mục. Nếu muốn Hermes tự nghiên cứu/ra quyết định sâu hơn thay code cố định, cần thiết kế đầu ra có cấu trúc và cổng kiểm chứng riêng.

### 2026-10-26 — Hermes là tác giả bản nháp

- Bối cảnh: dashboard trước đây gọi 9Router trực tiếp khi viết bài, còn Hermes chỉ chạy trong terminal riêng nên chưa hề viết các bài của dashboard.
- Quyết định: cả thao tác viết lại và bước tự động đều gọi Hermes CLI một lượt. Mỗi lời gọi gửi `docs/editorial-brief.md` và dữ kiện nguồn qua stdin; Hermes dùng model 9Router đã cấu hình. Dashboard chỉ kiểm tra emoji/hashtag, URL nguồn và lưu bản nháp; nếu Hermes lỗi thì giữ nội dung cũ, không dùng lời gọi model trực tiếp để thay thế.
- Lý do: bảo đảm người viết là Hermes và ngữ cảnh biên tập đi cùng từng bài, kể cả khi phiên terminal Hermes không mở.
- Hệ quả / khi nào xem lại: mỗi bài khởi tạo một tiến trình Hermes nên chậm hơn một lời gọi API đơn; cần theo dõi thời gian và chất lượng thực tế. Chọn tin, ảnh và kiểm duyệt vẫn dùng 9Router trực tiếp.

### 2026-10-26 — Icon do LLM chọn và context Hermes theo workspace

- Bối cảnh: prompt chỉ cho phép dùng emoji nên bản nháp #25 được lưu mà không có icon; Hermes đã dùng model 9Router nhưng cần nhận rõ yêu cầu biên tập của dự án.
- Quyết định: yêu cầu ít nhất một emoji có ý nghĩa, cho LLM tự quyết định số lượng/vị trí; nếu thiếu, gọi model viết lại một lần và chỉ lưu khi đạt. `AGENTS.md` chứa tóm tắt yêu cầu sản phẩm, còn `scripts/start-hermes.ps1` khởi động Hermes tại repo để nạp context này. Không đặt API key hay Page token trong repo.
- Lý do: bảo đảm đầu ra đáp ứng yêu cầu mà không chèn icon máy móc; context Hermes gắn với đúng dự án và không ảnh hưởng dự án khác.
- Hệ quả / khi nào xem lại: model có thể vẫn chọn icon kém phù hợp về thẩm mỹ; cần xem bản nháp thực tế. Hermes và dashboard dùng cùng endpoint/model nhưng là hai chương trình riêng.

### 2026-10-26 — Viết từ trích đoạn nguồn và chọn ảnh demo repo

- Bối cảnh: bản nháp chỉ dựa vào tiêu đề/tóm tắt, trong khi mẫu người dùng chọn thường nêu chi tiết sản phẩm và dùng ảnh chụp repo hoặc demo thật.
- Quyết định: khi viết bài mới, đọc trích đoạn giới hạn từ bài gốc hoặc README GitHub qua cơ chế tải URL công khai; nếu nguồn không đọc được, dùng metadata và nói rõ giới hạn trong prompt. Ưu tiên ảnh demo/screenshot có trong README trước ảnh trang trí; nếu không lấy được ảnh thì dùng đường dự phòng hiện có. Chưa quét Reddit/Threads.
- Lý do: bản nháp có thêm dữ kiện cụ thể và ảnh nhận diện được chủ thể mà không cần sao chép phong cách hay ảnh của trang mẫu.
- Hệ quả / khi nào xem lại: trang chặn truy cập vẫn chỉ cho metadata; trích đoạn chưa thay thế việc kiểm chứng sự thật hoặc quyền dùng ảnh. Cần mở rộng bộ adapter riêng khi thêm diễn đàn.

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

### 2026-10-27 — Máy chủ tự kéo đúng commit đã qua CI

- Bối cảnh: máy phát triển tạo PR và merge vào `main`; máy Windows khác chỉ chạy dịch vụ, chưa sẵn sàng để cài ngay.
- Quyết định: giữ CI trên runner Windows tạm. Server dùng Scheduled Task của tài khoản sở hữu Hermes để poll `main` mỗi 5 phút, yêu cầu workflow `push` thành công cho đúng SHA. Trước checkout, tạm dừng cron và đợi lượt Hermes kết thúc; backup SQLite, kiểm tra ứng dụng với DB tạm rồi HTTP, phục hồi nếu lỗi trước khi tiếp tục cron. Không tự triển khai PR hoặc commit CI đỏ.
- Lý do: server không cần mở cổng SSH cho GitHub, không nhận token trong CI và không sửa dữ liệu cục bộ khi cập nhật code.
- Hệ quả / khi nào xem lại: phải bật required check trên GitHub sau khi workflow chạy lần đầu và cài task trên server; dữ liệu/ảnh vẫn cần backup độc lập, sự cố sau khi đã gửi Page phải đối chiếu thủ công.

### 2026-10-27 — Không phục hồi DB sau khi Hermes có thể đã chạy lại

- Bối cảnh: review độc lập phát hiện dashboard có thể nhận thao tác đăng bài giữa health check và bước hoàn tất cập nhật; rollback từ bản sao cũ sẽ làm mất trạng thái Page đã đăng.
- Quyết định: giữ dashboard trong chế độ bảo trì khi có `data/deployment-paused`, chỉ cho `/healthz` phản hồi. Bắt đầu thử `hermes cron resume` là ranh giới sau đó không tự phục hồi DB; nếu lỗi, giữ bảo trì để chủ dự án đối chiếu trạng thái thực tế.
- Lý do: trạng thái đăng bài sau thời điểm đó có thể đã đổi trên Facebook; ghi đè DB cũ tạo nguy cơ đăng trùng.
- Hệ quả / khi nào xem lại: cần thao tác phục hồi thủ công nếu lỗi sau ranh giới này; kiểm chứng end-to-end trên server Windows khi cài máy.

### 2026-10-28 — Hermes chủ động tìm tin ngoài nguồn cấu hình

- Bối cảnh: luồng cũ chỉ quét nguồn cố định rồi model xếp hạng metadata; chủ dự án muốn Hermes tự tìm thêm tin và nhận đủ ngữ cảnh biên tập.
- Quyết định: giữ cron `--no-agent` để xử lý lịch theo phút, nhưng ở lượt tìm hằng ngày gọi riêng Hermes với toolset `web`, brief nghiên cứu, giới hạn số vòng công cụ và timeout cục bộ. Hermes trả JSON URL gốc và lý do chọn; ứng dụng kiểm tra lại URL HTTPS công khai, tiêu đề, tóm tắt, ngày công bố trong 48 giờ rồi mới lưu. Bài từ Hermes giữ phương pháp đánh giá riêng; nguồn cũ tiếp tục chạy khi Hermes lỗi. Bật bằng biến môi trường User `REUP_HERMES_DISCOVERY_ENABLED=1`.
- Lý do: Hermes có thể nghiên cứu rộng hơn mà không giao quyền sửa file, chạy terminal hoặc trực tiếp đăng Page trong lượt tìm. Kiểm tra độc lập giảm rủi ro link bịa, tin cũ hoặc nguồn bị tạm dừng.
- Hệ quả / khi nào xem lại: phụ thuộc web search backend của Hermes và khả năng tool calling của model 9Router; trang thiếu metadata ngày sẽ không được nhận. Chưa đối chiếu toàn văn qua nhiều nguồn.

### 2026-10-31 — Xếp lịch ngay khi từng bài tự động sẵn sàng

- Bối cảnh: lượt Hermes chuẩn bị nhiều bài liên tiếp; bài đã đạt kiểm tra vẫn chưa có lịch cho đến khi toàn bộ lượt kết thúc, có thể bỏ lỡ giờ đăng đầu tiên.
- Quyết định: sau mỗi bài đạt kiểm tra, thử xếp lịch ngay vào khung còn trống. Nếu bước này lỗi, giữ bài ở trạng thái sẵn sàng và thử lại cuối lượt. Dùng đồng hồ hiện tại khi chạy thật để không đặt lịch vào một giờ đã qua trong lượt dài. Đếm ID bài có automation job trong DB trước/sau lượt để số liệu vẫn đúng khi đồng bộ job lỗi tạm thời rồi được phục hồi, không tính bài người dùng tự hẹn.
- Lý do: bài đã sẵn sàng không bị giữ lại bởi bài kế tiếp đang viết hoặc xử lý ảnh; vẫn giữ kiểm tra ảnh, bình luận và Page trước khi hẹn.
- Hệ quả: lượt chuẩn bị có thêm các thao tác SQLite ngắn sau mỗi bài; cần kiểm tra CI và triển khai lên server qua CD sau khi chủ repo merge.

# Cấu hình runtime theo máy

### 2026-10-29 — PID launcher và tiến trình con dashboard trên Windows

- Bối cảnh: `Start-Process` với Python trong `.venv` trả PID launcher, còn cổng Flask 5000 do tiến trình Python con giữ. Updater cũ yêu cầu PID trùng tuyệt đối nên báo health lỗi dù `/healthz` trả OK.
- Quyết định: chấp nhận listener thuộc launcher hoặc tiến trình Python con trực tiếp có command line `run.py`; trước khi dừng, xác minh launcher nằm trong `.venv` và listener thuộc nhóm này. Dừng con trước launcher; kéo dài thời gian chờ health lên 60 lần.
- Lý do: hỗ trợ cơ chế Python venv trên Windows mà vẫn không dừng tiến trình không thuộc dashboard do updater quản lý.
- Hệ quả: cần kiểm chứng triển khai thực tế trên server sau khi CI/merge; updater không thay đổi các dữ liệu `.env` hoặc SQLite ngoài quy trình backup hiện có.

### 2026-10-29 — Nhận diện workflow CI theo GitHub API

- Bối cảnh: GitHub API trên commit `main` trả `path=.github/workflows/ci.yml` không có hậu tố `@refs/...`; release gate cũ từ chối CI đã xanh nên server không mở dashboard.
- Quyết định: chỉ nhận đúng `.github/workflows/ci.yml` hoặc cùng đường dẫn có hậu tố `@...`, đồng thời giữ nguyên điều kiện SHA, branch `main`, event `push`, lượt chạy mới nhất và kết quả success.
- Lý do: cho phép hai dạng đường dẫn API mà không nhận workflow khác hoặc bỏ qua CI.
- Hệ quả: kiểm tra cả hai dạng bằng unit test; server vẫn phải chờ commit sửa gate được merge và CI push thành công.

### 2026-10-29 — PowerShell 5.1 cần UTF-8 BOM cho script tiếng Việt

- Bối cảnh: máy server chỉ có Windows PowerShell 5.1; `install-hermes-automation.ps1` chứa tiếng Việt UTF-8 không BOM nên parser đọc sai và dừng trước khi cài cron.
- Quyết định: thêm UTF-8 BOM cho các script `.ps1` có tiếng Việt chưa có BOM; CI Windows gọi parser của `powershell.exe` cho toàn bộ script để bắt lỗi tương tự.
- Lý do: không cần cài PowerShell 7 trên server và không thay nội dung lệnh vận hành.
- Hệ quả: file nguồn có BOM; khi sửa những script này cần giữ BOM để tương thích PowerShell 5.1.

### 2026-10-29 — Ưu tiên `.env` cục bộ

- Bối cảnh: chuyển hệ thống sang Windows server bằng các biến môi trường User gây khó thao tác và dễ lệch cấu hình giữa hai máy.
- Quyết định: dashboard và Hermes runner đọc `.env` ở gốc repo; script PowerShell nạp biến User cũ trước rồi để `.env` ghi đè trong tiến trình. Chỉ chấp nhận khóa `REUP_*` theo cú pháp `KEY=VALUE`; file không được commit.
- Lý do: mỗi máy có thể giữ key/token riêng và cập nhật bằng một file cục bộ mà không cần chỉnh Windows User environment.
- Hệ quả: khi sửa `.env` cần khởi động lại dashboard/gateway để các tiến trình đang chạy nhận giá trị mới. Script cấu hình Facebook cũ vẫn có thể ghi User environment; nếu `.env` đã đặt biến tương ứng thì giá trị trong file được dùng khi chạy.
