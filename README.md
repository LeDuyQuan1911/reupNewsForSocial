# reupNewsForSocial

Hệ thống dự kiến thu thập và tổng hợp thông tin từ trang báo, GitHub và X, viết lại theo phong cách của chủ dự án rồi đăng lên mạng xã hội. Repo dùng khung làm việc từ [setupSourceVibeCode](https://github.com/LeDuyQuan1911/setupSourceVibeCode). Bước đầu đã có dashboard cục bộ để đọc RSS/Atom; phạm vi còn lại nằm trong [SPEC.md](SPEC.md).

## Chạy dashboard hiện tại

Yêu cầu Python 3.12+. Tại thư mục repo:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

Mở `http://127.0.0.1:5000`. Dữ liệu lưu tại `data/reup.sqlite3` và không được commit. Dashboard có sẵn RSS của OpenAI, Google AI, NVIDIA Technical Blog, AWS Machine Learning Blog và Microsoft Research; tin Anthropic từ sitemap chính thức; cùng repo GitHub mới nổi trong 30 ngày qua theo số sao. Có thể thêm nguồn RSS/Atom khác. Nút “Tìm báo / repo mới” quét ngay các nguồn đang bật, lấy tối đa 50 bài từ mỗi RSS và loại trùng theo URL.

## Cài Hermes khi chuyển repo sang máy Windows khác

Repo lưu **toàn bộ snapshot source Hermes** trong [`vendor/hermes-agent/`](vendor/hermes-agent/) tại commit `bf0203a794a07aac3ff764972ab9087baa4e4f4e` (bản v0.22.5 đã thử), gồm giấy phép MIT của upstream. Script setup dùng installer trong thư mục vendor; installer vẫn lấy đúng commit upstream để dựng runtime riêng tại `%LOCALAPPDATA%\hermes`. Cần Git, PowerShell, internet để tải các phụ thuộc/runtime, và 9Router chạy tại localhost. Cache, phiên làm việc và secrets của Hermes không được đưa vào Git.

Đặt `REUP_LLM_MODEL` thành model ID có trong 9Router và `REUP_LLM_API_KEY` trong biến môi trường **User** trên máy mới. Có thể đặt thêm `REUP_LLM_BASE_URL`; mặc định là `http://127.0.0.1:20128/v1`. Không đưa key vào repo hay dòng lệnh lưu trong lịch sử shell. Sau đó mở terminal mới tại repo và chạy:

```powershell
.\scripts\setup-hermes.ps1
.\scripts\setup-hermes.ps1 -TestConnection  # tùy chọn: gọi model với câu thử ngắn
.\scripts\start-hermes.ps1               # mở Hermes tại repo và nạp AGENTS.md
```

Script kiểm tra SHA-256 của installer vendored trước khi chạy. Nếu máy đã cài Hermes ở commit khác, script dừng để tránh ghi đè cài đặt dùng chung. Cấu hình chỉ lưu **tên** biến môi trường chứa key. `start-hermes.ps1` mở phiên tương tác mới tại repo để Hermes tự nạp `AGENTS.md`. Dashboard gọi Hermes ở chế độ một lượt khi cần viết bài và truyền trực tiếp [`docs/editorial-brief.md`](docs/editorial-brief.md) cùng dữ kiện nguồn; không cần giữ phiên tương tác mở. Cài lịch Hermes riêng bằng `scripts/install-hermes-automation.ps1` như bên dưới. Snapshot upstream có hơn 20.000 file và làm repo nặng thêm khoảng 222 MB nội dung; khi nâng phiên bản cần thay toàn bộ snapshot, pin và kiểm tra lại.

Giao diện gồm các trang: **Tổng quan** (`/`, dashboard hoạt động theo 7 hoặc 30 ngày), **Bài báo** (`/articles`, có tìm kiếm/lọc nguồn và phân trang), **Luồng đăng** (`/workflow`), **Bài đăng** (`/posts`, có phân trang), **Nguồn thông tin** (`/sources`), **Facebook** (`/facebook`, chọn nhóm đích) và **Tài khoản & kết nối** (`/account`). Dashboard đếm tin phát hiện, bản nháp tạo, bài tự động chuẩn bị đạt và bài đã đăng theo ngày giờ Bangkok; ngày không có hoạt động vẫn hiện số 0. Trang Luồng đăng hiển thị từng bài báo cùng nguồn, trạng thái, kênh Facebook Page, giờ hẹn/đã đăng và thao tác tiếp theo trong một bảng; trên điện thoại mỗi bài thành một mục gọn. Mặc định trang hiển thị bài đã chọn đăng, có nút xem toàn bộ bài báo kể cả mục chưa tạo nháp. Bài chưa có lịch được ghi rõ. Kênh đang hỗ trợ là Facebook Page, chưa có lựa chọn Page hoặc kênh riêng cho từng bài. Trang tài khoản chỉ hiển thị trạng thái biến môi trường đã cấu hình, không hiển thị giá trị bí mật hoặc xác nhận kết nối hoạt động. Trang chi tiết bài báo dùng `/articles/<id>`; trang biên tập bài đăng dùng `/posts/<id>`.

Trang Bài báo lọc được tin chưa chọn viết hoặc đã có bài đăng, bên cạnh từ khóa và nguồn. Trang Bài đăng có bộ lọc Tất cả, Cần xử lý, Bản nháp, Đã lên lịch và Đã đăng; tìm theo tiêu đề/nội dung, giữ bộ lọc khi phân trang. Dashboard dẫn tới nhóm cần xử lý. Trang Nguồn thông tin cho tạm dừng/bật lại từng nguồn mà không xóa tin cũ, hiển thị lần quét gần nhất và lỗi quét; nguồn tạm dừng không được quét. Giao diện biên tập cảnh báo khi có nội dung chưa lưu. Lịch thử nghiệm vẫn dùng được khi chưa kết nối, còn lịch đăng thật và nút đăng ngay cần đủ cấu hình Page và model viết/duyệt ảnh.

URL RSS/Atom có thể dùng HTTP hoặc HTTPS trên cổng mặc định và phải trỏ tới địa chỉ công khai. Lúc quét, hệ thống kiểm tra địa chỉ DNS, cố định IP kết nối và kiểm tra lại từng lần chuyển hướng; feed trỏ tới máy cục bộ/mạng riêng bị từ chối. Tạm dừng nguồn cũng ngừng chọn tin chưa chuẩn bị từ nguồn đó cho luồng tự động; bài đã có lịch không tự bị hủy.

Từ một mục đã tìm thấy, chọn “Tạo bản nháp” để biên tập, viết lại bằng LLM, lên lịch hoặc đăng ngay lên Facebook Page. Khi viết lại, ứng dụng thử đọc trích đoạn bài gốc hoặc README GitHub (giới hạn độ dài); nếu trang không cho đọc, bài chỉ dựa trên tiêu đề và tóm tắt. Khi tạo bản nháp, hệ thống ưu tiên tối đa ba ảnh JPEG khác nhau trong `data/media/`: với bài báo, thử ảnh feed rồi nhiều ảnh trong trang nguồn; với repo GitHub, ưu tiên ảnh demo/screenshot sản phẩm trong README, thêm ảnh chụp repo bằng Chrome headless khi tư liệu ít. URL và dữ liệu ảnh trùng được bỏ qua. Nếu không lấy được ảnh thật, ứng dụng thử sinh ảnh qua 9Router; khi bước đó không khả dụng, thẻ tiêu đề chỉ dùng xem trước và bài phải chờ ảnh phù hợp. Trang biên tập cho xem trước, thêm ảnh từ nguồn (hoặc chụp thêm repo), chọn tải nhiều ảnh từ máy cùng lúc và bỏ từng ảnh; mỗi bài hỗ trợ tối đa 10 ảnh và không thể bỏ ảnh cuối cùng. Một ảnh được gửi qua Page `/photos`; nhiều ảnh được tải lên ở trạng thái chưa xuất bản rồi gắn vào một bài qua `/feed`. Ảnh được lưu riêng cho từng bản nháp và không đưa vào Git.

Khi nguồn chỉ có một ảnh thật, hệ thống tự thử tạo ảnh thứ hai với góc nhìn bổ sung bằng model ảnh 9Router, không yêu cầu bạn tải ảnh lên. Nếu nguồn không có ảnh, hệ thống thử tạo hai ảnh khác nhau. Ảnh sinh ra phải dựa trên tiêu đề/tóm tắt nguồn và được model nhìn ảnh kiểm duyệt trước khi xếp lịch hoặc đăng. Bản nháp cũ còn một ảnh được thử bổ sung tự động khi bạn lên lịch hoặc đăng ngay; bài đã lên lịch/đã đăng không bị đổi ảnh. Nếu model ảnh lỗi hoặc hai kết quả trùng nhau, bài có thể còn một ảnh hợp lệ.

Nút “Hermes viết lại” và bước tự tạo bài gọi **Hermes CLI** với model 9Router đã cấu hình; Hermes là tác giả của toàn bộ nội dung bản nháp. Mỗi lượt gọi nhận hướng dẫn biên tập và dữ kiện nguồn qua stdin, chạy riêng và chỉ trả bài viết để dashboard lưu. Bản nháp mới cần ít nhất một emoji phù hợp do Hermes chọn; nếu lượt đầu bỏ sót, dashboard yêu cầu Hermes viết lại một lần và báo lỗi nếu vẫn thiếu, giữ nội dung đã lưu. Hermes được gợi ý dùng nhiều icon có ý nghĩa khi nội dung có nhiều điểm cần nhấn; số lượng và vị trí thay đổi theo bài, không theo mẫu cố định. Hermes cũng thử viết bình luận đầu tiên trong một lượt riêng; nếu lỗi, hệ thống dùng liên kết nguồn làm bình luận dự phòng để bạn sửa. Các bước chọn tin, tạo/duyệt ảnh và kiểm duyệt trước đăng vẫn gọi model 9Router tương ứng trực tiếp. Có thể đặt `REUP_HERMES_BIN` nếu chương trình Hermes ở đường dẫn khác mặc định.

Việc đăng đòi hỏi LLM có khả năng xem ảnh kiểm duyệt cả nội dung và từng ảnh trước; khi không có cấu hình, một ảnh bị mất hoặc LLM trả kết quả không hợp lệ, bài sẽ không được gửi. Tin có tiêu đề rất giống bài đã đăng trong 14 ngày gần đây cũng bị chặn. Khi Hermes nhận quyền điều phối, cron của Hermes đánh thức quy trình mỗi phút, kể cả khi dashboard đóng; nếu máy tắt, bài quá giờ được xử lý sau khi Hermes gateway chạy lại. Nếu không xác nhận được kết quả từ Facebook, bài ở trạng thái “Cần đối chiếu” và không được gửi lại cho đến khi bạn kiểm tra Page, rồi đánh dấu đã đăng hoặc chưa đăng trên dashboard. Nếu tiến trình dừng giữa lúc gửi, bài vẫn ở trạng thái `publishing` và cần kiểm tra thủ công trong cơ sở dữ liệu.

Các biến môi trường cần dùng được liệt kê trong [.env.example](.env.example). Cấu hình chúng trong PowerShell trước khi chạy; file `.env.example` chỉ là mẫu và không tự được nạp. `REUP_LLM_BASE_URL` mặc định là endpoint 9Router cục bộ `http://127.0.0.1:20128/v1`; cần đặt `REUP_LLM_MODEL` để viết bài và `REUP_LLM_VISION_MODEL` cho model hỗ trợ ảnh để duyệt trước khi đăng. Bước gọi LLM có thể thử dùng model viết bài khi thiếu model vision, nhưng luồng tự động và thao tác đặt lịch/đăng thật trên web yêu cầu cấu hình vision riêng để tránh lỗi muộn; model chỉ đọc văn bản vẫn sẽ bị chặn ở bước kiểm duyệt. Để đăng lên Page cần `REUP_FACEBOOK_PAGE_ID`, phiên bản Graph API trong `REUP_META_GRAPH_VERSION` và một trong hai cách xác thực: `REUP_FACEBOOK_SYSTEM_USER_TOKEN` khi `REUP_FACEBOOK_AUTH_MODE=system_user`, hoặc `REUP_FACEBOOK_PAGE_TOKEN` khi `REUP_FACEBOOK_AUTH_MODE=page_token`. Không đưa token thật vào repo.

Nếu không lấy được ảnh thật từ bài báo hoặc repo, ứng dụng dùng model văn bản 9Router lập dàn ý ảnh từ tiêu đề/tóm tắt, rồi gọi model tạo ảnh qua `POST /v1/images/generations` trên localhost. Đặt `REUP_LLM_IMAGE_MODEL` bằng một ID thuộc danh sách `GET /v1/models/image` của 9Router; model viết bài/nhìn ảnh như `ag/gemini-3.8-flash-low` không tự sinh ảnh. Ảnh được lưu và qua model nhìn ảnh kiểm tra lại trước khi đăng. Nếu thiếu model ảnh hoặc router lỗi, bài giữ ảnh thẻ tạm và không tự đăng. 9Router chạy trên máy cá nhân nhưng có thể chuyển yêu cầu tới nhà cung cấp model bên ngoài; điều này không đồng nghĩa model chạy hoàn toàn offline trên máy.

Với bài báo có video nhúng rõ ràng, bước tự động kiểm tra video trong trang nguồn và nhờ model 9Router chọn link liên quan; bản nháp được thêm dòng “Video ở dưới phần bình luận.”. Trang biên tập cũng có nút tìm video và ô sửa/dán URL. Sau khi Facebook xác nhận bài đã đăng, ứng dụng gửi link video thành bình luận của chính bài Page. Nếu phản hồi bình luận không rõ, bài xuất hiện trong **Cần xử lý**; kiểm tra bình luận trên Page rồi xác nhận đã có link hoặc cho gửi khi chắc chắn chưa có, tránh trùng. Tính năng chỉ gửi liên kết video, không tải lên hay đăng lại tệp video; quyền bình luận của Page token còn cần kiểm chứng bằng bài thật.

Mỗi bản nháp có ô **Bình luận đầu tiên**. Bài đăng thật cần nội dung bình luận; sau khi Facebook trả ID bài đăng, hệ thống gửi bình luận qua Page và lưu ID/trạng thái riêng. Nội dung bình luận được kiểm duyệt cùng bài và ảnh. Nếu Meta không xác nhận kết quả bình luận, hệ thống dừng gửi lại và yêu cầu đối chiếu trên Page. Bài có video có thể có thêm bình luận chứa URL video. Quyền đăng bình luận bằng System User vẫn cần thử với một bài thật có kiểm soát.

Đặt `REUP_AUTO_ENABLED=1` trong biến môi trường User để bật luồng tự động. Hermes chạy job mỗi phút để xử lý bài đến giờ; ứng dụng chỉ **tìm bài mới tự động một lần trong mỗi ngày Bangkok**. Tại trang **Tài khoản**, đặt 1–24 bài tự động/ngày và nhập đúng một giờ đăng cho mỗi bài, cách nhau ít nhất 30 phút. Mặc định là 6 bài tại **07:00, 10:00, 13:00, 16:00, 19:00, 22:00**. Chỉ xét tin được phát hiện và đăng trong 48 giờ gần đây, kể cả tin đã lưu trước khi bật tự động nếu chưa có bản nháp. Bài được tạo bản nháp, chuẩn bị ảnh, Hermes viết nội dung và model 9Router kiểm duyệt cả nội dung lẫn ảnh. Lỗi chuẩn bị tạm thời được thử lại tối đa 3 lần, cách nhau ít nhất 5 phút; bài bị kiểm duyệt từ chối được giữ lại để xem và không tự đăng. Khi đủ cấu hình Facebook Page, bài đạt được xếp vào các giờ đã chọn và được kiểm duyệt lần nữa trước khi gửi. Nếu chưa có Page ID/token, bài đạt nằm ở trạng thái bản nháp chờ kết nối; bài quá 48 giờ không được tự xếp lịch sau này. Lưu cấu hình mới không đổi các bài đã lên lịch. Nút “Tìm báo / repo mới” trên Tổng quan, Bài báo hoặc Tài khoản quét thủ công bất cứ lúc nào; thao tác này không chiếm lượt quét tự động trong ngày.

Lượt tìm tự động của ngày mới bắt đầu từ **00:00 giờ Bangkok** khi Hermes đang hoạt động. Nếu máy tắt hoặc job bận lúc nửa đêm, Hermes chạy bù ở lượt kế tiếp. Hermes chọn và chuẩn bị tối đa số bài đã đặt cho ngày đó; hệ thống có thể lưu nhiều tin thô hơn để xếp hạng và thay tin không đạt kiểm duyệt. Số bài đạt thực tế có thể ít hơn mục tiêu khi thiếu tin phù hợp hoặc model/nguồn gặp lỗi.

### Hermes vận hành độc lập

Sau khi cài Hermes và đặt biến môi trường User, chạy một lần tại repo:

```powershell
.\scripts\install-hermes-automation.ps1
hermes cron status
hermes cron list
```

Script chép một runner nhỏ vào thư mục script riêng của Hermes, tạo job cron **mỗi phút** và cho Hermes gateway tự chạy khi đăng nhập Windows. Hermes cron gọi các hàm thu thập, chọn tin, chuẩn bị ảnh, viết nháp, kiểm duyệt, xếp lịch và xử lý bài đến giờ; các giới hạn và trạng thái chống gửi trùng vẫn do code ứng dụng bảo vệ. Job không gọi LLM ở những phút không có bài cần viết, nên không tốn token cho mỗi nhịp kiểm tra. Tệp `data/hermes-automation.enabled` ngăn dashboard khởi động thêm scheduler thứ hai. Xem các lượt chạy bằng `hermes cron runs <job-id>`; ID nằm trong `data/hermes-cron-job-id.txt`. Chuyển repo sang máy khác thì cài 9Router, Hermes, cấu hình biến User rồi chạy lại script này tại vị trí repo mới. Không chép token hoặc dữ liệu phiên Hermes qua Git.

Mở [trang Hermes](http://127.0.0.1:5000/hermes) khi dashboard đang chạy để xem gateway, job và các lượt chạy gần đây; chạy một lượt, tạm dừng hoặc tiếp tục lịch. Giao diện xuất hiện trước, sau đó tải trạng thái Hermes và bật các nút điều khiển khi đã xác nhận job. Trang này cũng cho đặt số bài/ngày, chọn từng giờ Bangkok bằng đồng hồ của trình duyệt và quét báo/repo theo yêu cầu. Nút chạy một lượt có thể xử lý bài đến giờ để đăng lên Page nếu đã đủ điều kiện; tạm dừng sẽ ngừng cả việc xử lý bài đến giờ cho đến khi tiếp tục. Website chỉ điều khiển job có ID và thư mục làm việc khớp repo hiện tại.

[Trang Facebook](http://127.0.0.1:5000/facebook) hiện Page ID, nguồn xác thực đang chọn và tải tên Page từ Meta Graph API bằng token trên máy. Script cấu hình lưu tên Page đã xác minh cùng ID vào biến môi trường User để có thể nhận ra Page khi token về sau hết hạn; giao diện ghi rõ khi tên chỉ là bản đã lưu. Phép kiểm tra chỉ xác nhận quyền đọc Page; muốn xác nhận quyền đăng cần thử một bài. Token không được hiển thị.

Trên Windows, `scripts/start-local-services.ps1` có thể được gọi khi đăng nhập để khởi động 9Router và dashboard nếu chúng chưa chạy. Khi repo đã giao lịch cho Hermes, script đợi 9Router phản hồi rồi bảo đảm Hermes gateway đang chạy trước khi mở dashboard. Script lấy biến môi trường của người dùng và chỉ mở hai cổng web trên localhost. Trên máy hiện tại, tác vụ Task Scheduler `reupNewsForSocial-local` đã được đăng ký ở chế độ đăng nhập người dùng. Máy cần bật và đăng nhập Windows để Hermes/9Router chạy; khi máy tắt, không thể tự quét hoặc gửi bài đúng giờ. Nếu gateway dừng giữa phiên, chạy lại script để khôi phục; bài quá giờ có thể được xử lý ngay khi gateway chạy lại.

Hiện chỉ có adapter đăng Facebook Page. Luồng trang cá nhân, nhóm và LinkedIn chưa được tích hợp. Bản nháp mới có thể dùng trích đoạn bài gốc/README, nhưng chưa kiểm chứng toàn văn hoặc đối chiếu nhiều nguồn và chưa học giọng văn cá nhân. Reddit và Threads chưa được quét tự động.

Kiểm tra cục bộ: `python -m unittest discover -s tests -v`.

`.github/workflows/ci.yml` chạy cùng bộ test trên máy Windows tạm khi có PR vào `main` hoặc commit mới trên `main`. CI không nạp token thật, tắt tự động đăng và dùng dữ liệu SQLite tạm của test; kết quả CI chưa xác nhận 9Router/Hermes/Meta trên máy server. Bộ script trong [`scripts/cd/`](scripts/cd/) đã chuẩn bị cho máy Windows tự kéo **đúng SHA có CI push xanh** mỗi 5 phút, sao lưu DB và phục hồi khi triển khai lỗi. Xem [hướng dẫn CI/CD](docs/deployment.md) để bật required check trên GitHub và cài Scheduled Task trên máy server sau này; script trong repo chưa tự kích hoạt trên máy khác.

## Chọn nhóm Facebook dự kiến đăng

Trang **Facebook** (`/facebook`) lưu tên/URL nhóm dự kiến đăng, cho chọn hoặc tạm dừng từng nhóm và xóa nhóm nhập nhầm. Đây là cấu hình đích để chuẩn bị tích hợp; ứng dụng chưa đăng vào nhóm và không dùng danh sách này khi chạy lịch. Trạng thái kết nối Facebook Page cũng xuất hiện trên trang này.

## Kết nối Facebook Page để đăng tự động

### System User cho lịch tự động

Trong [Meta Business Settings](https://business.facebook.com/settings/), chọn đúng Business Portfolio, mở **Người dùng hệ thống** và tạo/chọn System User. Gán App `CreatePost` và Page cần đăng cho System User; cấp quyền tạo nội dung trên Page. Tạo System User token với `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`; nếu ứng dụng gửi liên kết video trong bình luận, cấp thêm `pages_manage_engagement`. Các quyền có thể chỉ hiện khi App đã được cấp quyền tương ứng. Chọn thời hạn token phù hợp và tự kiểm tra hạn/khả năng thu hồi; không mặc định token tồn tại vĩnh viễn.

Mở PowerShell tại repo và chạy `scripts/configure-facebook-system-user.ps1`. Script lấy Page ID và phiên bản Graph API đã lưu trên máy (hoặc hỏi nếu chưa có), hỏi System User token bằng đầu vào ẩn, lấy Page token của đúng Page bằng `/me/accounts` và xác minh tên/ID Page trước khi lưu **System User token** vào biến môi trường User của Windows. Không truyền token qua tham số dòng lệnh hoặc chat. Chạy `scripts/configure-facebook-system-user.ps1 -Check` để kiểm tra lại. Khi chọn chế độ này, dashboard và Hermes tự lấy Page token từ System User lúc cần; Page token cũ không được dùng làm dự phòng. Khởi động lại dashboard; Hermes runner nạp lại biến User ở mỗi lượt. Kiểm tra đọc Page **chưa xác nhận quyền đăng**; thử một bài có kiểm soát trước khi để lịch tự chạy.

### Page token cá nhân (đường cấu hình cũ)

Ứng dụng chỉ cần **Page ID**, **Page access token** có quyền phù hợp và phiên bản Graph API; không yêu cầu App ID hoặc App Secret, cũng không bắt buộc tạo Meta App *mới* nếu đã có Page token hợp lệ từ một App/tích hợp khác. Nếu chưa có token, cách chủ động là dùng Meta App đang có hoặc [tạo App](https://developers.facebook.com/apps/), rồi mở [Graph API Explorer](https://developers.facebook.com/tools/explorer/) để cấp quyền Page. Dùng User access token gọi `/me/accounts?fields=id,name,access_token,tasks`, chọn đúng Page và lấy ID/token; [bộ ví dụ Pages API của Meta](https://www.postman.com/meta/facebook/documentation/r56bjfd/facebook-api) mô tả luồng này. Giữ token trên máy, không đưa vào chat hay Git.

Mở PowerShell ở repo và chạy `scripts/configure-facebook-page.ps1`. Script hỏi Page ID, phiên bản Graph API và Page token bằng đầu vào ẩn; gọi `GET /<page-id>?fields=id,name` để xác minh đúng Page trước khi lưu cấu hình vào môi trường User của Windows. Nếu Graph API Explorer không hiện kết quả `/me/accounts`, chạy `scripts/configure-facebook-page.ps1 -FromUserToken`, sao chép **User access token** ở cột phải và dán vào lời nhắc nhập ẩn. Script dùng Page ID/phiên bản API đã lưu (hoặc hỏi nếu chưa có), lấy Page token trực tiếp qua `GET /<page-id>?fields=id,name,access_token`, kiểm tra Page rồi lưu; User token chỉ dùng trong lần chạy đó. Không dán token vào chat hoặc dòng lệnh. Chạy lại với `-Check` để kiểm tra cấu hình đã lưu. Phép kiểm tra đọc này **chưa chứng minh quyền đăng**; xem các bài đang chờ, khởi động lại dashboard rồi thử một bài có kiểm soát trước khi để lịch tự chạy. Dashboard đang dùng `REUP_AUTO_ENABLED=1` sẽ tự xếp lịch bài đạt sau khi có cấu hình Page.

## Bắt đầu

1. Chốt các điểm còn mở trong [SPEC.md](SPEC.md).
2. Yêu cầu agent đọc [AGENTS.md](AGENTS.md), [MAP.md](MAP.md) và SPEC.md, rồi đề xuất một bước nhỏ trong [PLAN.md](PLAN.md).
3. Sau mỗi thay đổi, yêu cầu agent chạy kiểm tra phù hợp và cập nhật bản đồ/tài liệu nếu cấu trúc hoặc quyết định thay đổi.

**Mỗi nhiệm vụ liên quan đến repo phải có nhật ký riêng** trong [docs/worklog/](docs/worklog/README.md), ghi yêu cầu, việc đã làm, quyết định, kiểm chứng và phần còn lại. Quy tắc này áp dụng dù plugin `documentation` tắt.

## Bật plugin theo nhu cầu

```powershell
node scripts/plugins.mjs list
node scripts/plugins.mjs enable prototype
node scripts/plugins.mjs enable ci-cd
node scripts/plugins.mjs disable ci-cd
node scripts/plugins.mjs check
```

`project.plugins.json` là danh sách plugin đang bật. Mỗi agent đọc file này qua `AGENTS.md` và chỉ áp dụng hướng dẫn của plugin bật. Xem [danh mục plugin](plugins/README.md). Đây là plugin quy trình trong repo, không phải plugin cài vào Codex, Antigravity hay Claude Code.

Plugin `independent-review` hiện được bật: agent khác review code trong phiên riêng theo [quy trình và mẫu báo cáo](reviews/README.md) trước khi chủ repo quyết định merge.

Understand Anything được lưu tại `vendor/understand-anything/` và dùng qua plugin `codebase-graph`. Xem [cách build runtime và làm mới graph khi cần](docs/understand-anything.md). Hook sau commit chỉ đánh dấu graph cũ; agent cập nhật graph trước lần dùng tiếp theo.

## Các file chính

- `AGENTS.md`: quy tắc chung cho coding agent, được Codex sử dụng.
- `CLAUDE.md`: điểm vào tương ứng cho Claude Code.
- `MAP.md`: bản đồ file và nơi cần tìm thông tin.
- `SPEC.md`: mục tiêu, ràng buộc và câu hỏi cần chốt.
- `PLAN.md`: trạng thái và các bước triển khai.
- `MULTI_AGENT.md`: cách chia việc giữa Codex, Antigravity và Claude Code bằng worktree.
- `project.plugins.json` và `plugins/`: plugin quy trình có thể bật/tắt cho dự án.
- `docs/worklog/`: nhật ký bắt buộc cho từng nhiệm vụ của mỗi agent.
- `governance/`: quy tắc GitHub để chỉ chủ repo merge vào `main`.
- `reviews/`: yêu cầu và báo cáo review code độc lập.
- `vendor/understand-anything/`: source Understand Anything đã cố định phiên bản.
- `contexte/`: quyết định và kiến thức dự án.
- `livrables/`: sản phẩm đầu ra không phải source code.

Khung này dựa trên [bài viết về Claude Code Harness 3 tầng](https://www.facebook.com/photo.php?fbid=1460250176064963&set=a.101224068634254&type=3). Git đã được khởi tạo và có remote `origin` của `reupNewsForSocial`. Chưa có cấu hình MCP, secrets hay quy trình triển khai.
