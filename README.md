# reupNewsForSocial

Hệ thống dự kiến thu thập và tổng hợp thông tin từ trang báo, GitHub và X, viết lại theo phong cách của chủ dự án rồi đăng lên mạng xã hội. Repo dùng khung làm việc từ [setupSourceVibeCode](https://github.com/LeDuyQuan1911/setupSourceVibeCode). Bước đầu đã có dashboard cục bộ để đọc RSS/Atom; phạm vi còn lại nằm trong [SPEC.md](SPEC.md).

## Chạy dashboard hiện tại

Yêu cầu Python 3.12+. Tại thư mục repo:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

Mở `http://127.0.0.1:5000`. Dữ liệu lưu tại `data/reup.sqlite3` và không được commit. Dashboard có sẵn RSS của OpenAI, Google AI, NVIDIA Technical Blog, AWS Machine Learning Blog và Microsoft Research; tin Anthropic từ sitemap chính thức; cùng repo GitHub mới nổi trong 30 ngày qua theo số sao. Có thể thêm nguồn RSS/Atom khác. Nút “Tìm bài mới” lấy tối đa 50 bài từ mỗi RSS và loại trùng theo URL.

## Cài Hermes khi chuyển repo sang máy Windows khác

Repo lưu **toàn bộ snapshot source Hermes** trong [`vendor/hermes-agent/`](vendor/hermes-agent/) tại commit `bf0203a794a07aac3ff764972ab9087baa4e4f4e` (bản v0.22.5 đã thử), gồm giấy phép MIT của upstream. Script setup dùng installer trong thư mục vendor; installer vẫn lấy đúng commit upstream để dựng runtime riêng tại `%LOCALAPPDATA%\hermes`. Cần Git, PowerShell, internet để tải các phụ thuộc/runtime, và 9Router chạy tại localhost. Cache, phiên làm việc và secrets của Hermes không được đưa vào Git.

Đặt `REUP_LLM_MODEL` thành model ID có trong 9Router và `REUP_LLM_API_KEY` trong biến môi trường **User** trên máy mới. Có thể đặt thêm `REUP_LLM_BASE_URL`; mặc định là `http://127.0.0.1:20128/v1`. Không đưa key vào repo hay dòng lệnh lưu trong lịch sử shell. Sau đó mở terminal mới tại repo và chạy:

```powershell
.\scripts\setup-hermes.ps1
.\scripts\setup-hermes.ps1 -TestConnection  # tùy chọn: gọi model với câu thử ngắn
hermes
```

Script kiểm tra SHA-256 của installer vendored trước khi chạy. Nếu máy đã cài Hermes ở commit khác, script dừng để tránh ghi đè cài đặt dùng chung. Cấu hình chỉ lưu **tên** biến môi trường chứa key. Hermes và dashboard hiện là hai chương trình riêng; script này không bật lịch Hermes hoặc cấp quyền đăng Facebook. Snapshot upstream có hơn 20.000 file và làm repo nặng thêm khoảng 222 MB nội dung; khi nâng phiên bản cần thay toàn bộ snapshot, pin và kiểm tra lại.

Giao diện gồm các trang: **Tổng quan** (`/`, dashboard hoạt động theo 7 hoặc 30 ngày), **Bài báo** (`/articles`, có tìm kiếm/lọc nguồn và phân trang), **Luồng đăng** (`/workflow`), **Bài đăng** (`/posts`, có phân trang), **Nguồn thông tin** (`/sources`), **Facebook** (`/facebook`, chọn nhóm đích) và **Tài khoản & kết nối** (`/account`). Dashboard đếm tin phát hiện, bản nháp tạo, bài tự động chuẩn bị đạt và bài đã đăng theo ngày giờ Bangkok; ngày không có hoạt động vẫn hiện số 0. Trang Luồng đăng hiển thị từng bài báo cùng nguồn, trạng thái, kênh Facebook Page, giờ hẹn/đã đăng và thao tác tiếp theo trong một bảng; trên điện thoại mỗi bài thành một mục gọn. Mặc định trang hiển thị bài đã chọn đăng, có nút xem toàn bộ bài báo kể cả mục chưa tạo nháp. Bài chưa có lịch được ghi rõ. Kênh đang hỗ trợ là Facebook Page, chưa có lựa chọn Page hoặc kênh riêng cho từng bài. Trang tài khoản chỉ hiển thị trạng thái biến môi trường đã cấu hình, không hiển thị giá trị bí mật hoặc xác nhận kết nối hoạt động. Trang chi tiết bài báo dùng `/articles/<id>`; trang biên tập bài đăng dùng `/posts/<id>`.

Trang Bài báo lọc được tin chưa chọn viết hoặc đã có bài đăng, bên cạnh từ khóa và nguồn. Trang Bài đăng có bộ lọc Tất cả, Cần xử lý, Bản nháp, Đã lên lịch và Đã đăng; tìm theo tiêu đề/nội dung, giữ bộ lọc khi phân trang. Dashboard dẫn tới nhóm cần xử lý. Trang Nguồn thông tin cho tạm dừng/bật lại từng nguồn mà không xóa tin cũ, hiển thị lần quét gần nhất và lỗi quét; nguồn tạm dừng không được quét. Giao diện biên tập cảnh báo khi có nội dung chưa lưu. Lịch thử nghiệm vẫn dùng được khi chưa kết nối, còn lịch đăng thật và nút đăng ngay cần đủ cấu hình Page và model viết/duyệt ảnh.

URL RSS/Atom có thể dùng HTTP hoặc HTTPS trên cổng mặc định và phải trỏ tới địa chỉ công khai. Lúc quét, hệ thống kiểm tra địa chỉ DNS, cố định IP kết nối và kiểm tra lại từng lần chuyển hướng; feed trỏ tới máy cục bộ/mạng riêng bị từ chối. Tạm dừng nguồn cũng ngừng chọn tin chưa chuẩn bị từ nguồn đó cho luồng tự động; bài đã có lịch không tự bị hủy.

Từ một mục đã tìm thấy, chọn “Tạo bản nháp” để biên tập, viết lại bằng LLM, lên lịch hoặc đăng ngay lên Facebook Page. Khi tạo bản nháp, hệ thống lưu ảnh JPEG đầu tiên trong `data/media/`: với bài báo, thử ảnh feed và nhiều ảnh trong trang nguồn; với repo GitHub, ưu tiên ảnh đủ lớn trong README, sau đó chụp repo bằng Chrome headless. Nếu không lấy được ảnh thật, ứng dụng thử sinh ảnh qua 9Router; khi bước đó không khả dụng, thẻ tiêu đề chỉ dùng xem trước và bài phải chờ ảnh phù hợp. Trang biên tập cho xem trước, thêm ảnh từ nguồn (hoặc chụp thêm repo), tải ảnh từ máy và bỏ từng ảnh; mỗi bài hỗ trợ tối đa 10 ảnh và không thể bỏ ảnh cuối cùng. Một ảnh được gửi qua Page `/photos`; nhiều ảnh được tải lên ở trạng thái chưa xuất bản rồi gắn vào một bài qua `/feed`. Ảnh được lưu riêng cho từng bản nháp và không đưa vào Git.

Việc đăng đòi hỏi LLM có khả năng xem ảnh kiểm duyệt cả nội dung và từng ảnh trước; khi không có cấu hình, một ảnh bị mất hoặc LLM trả kết quả không hợp lệ, bài sẽ không được gửi. Tin có tiêu đề rất giống bài đã đăng trong 14 ngày gần đây cũng bị chặn. Lịch chạy khi `run.py` còn hoạt động và quét mỗi 30 giây; nếu máy tắt, bài quá giờ được xử lý sau khi ứng dụng chạy lại. Nếu không xác nhận được kết quả từ Facebook, bài ở trạng thái “Cần đối chiếu” và không được gửi lại cho đến khi bạn kiểm tra Page, rồi đánh dấu đã đăng hoặc chưa đăng trên dashboard. Nếu tiến trình dừng giữa lúc gửi, bài vẫn ở trạng thái `publishing` và cần kiểm tra thủ công trong cơ sở dữ liệu.

Các biến môi trường cần dùng được liệt kê trong [.env.example](.env.example). Cấu hình chúng trong PowerShell trước khi chạy; file `.env.example` chỉ là mẫu và không tự được nạp. `REUP_LLM_BASE_URL` mặc định là endpoint 9Router cục bộ `http://127.0.0.1:20128/v1`; cần đặt `REUP_LLM_MODEL` để viết bài và `REUP_LLM_VISION_MODEL` cho model hỗ trợ ảnh để duyệt trước khi đăng. Bước gọi LLM có thể thử dùng model viết bài khi thiếu model vision, nhưng luồng tự động và thao tác đặt lịch/đăng thật trên web yêu cầu cấu hình vision riêng để tránh lỗi muộn; model chỉ đọc văn bản vẫn sẽ bị chặn ở bước kiểm duyệt. Để đăng lên Page cần `REUP_FACEBOOK_PAGE_ID`, `REUP_FACEBOOK_PAGE_TOKEN` và phiên bản Graph API trong `REUP_META_GRAPH_VERSION`. Không đưa token thật vào repo.

Nếu không lấy được ảnh thật từ bài báo hoặc repo, ứng dụng dùng model văn bản 9Router lập dàn ý ảnh từ tiêu đề/tóm tắt, rồi gọi model tạo ảnh qua `POST /v1/images/generations` trên localhost. Đặt `REUP_LLM_IMAGE_MODEL` bằng một ID thuộc danh sách `GET /v1/models/image` của 9Router; model viết bài/nhìn ảnh như `ag/gemini-3.8-flash-low` không tự sinh ảnh. Ảnh được lưu và qua model nhìn ảnh kiểm tra lại trước khi đăng. Nếu thiếu model ảnh hoặc router lỗi, bài giữ ảnh thẻ tạm và không tự đăng. 9Router chạy trên máy cá nhân nhưng có thể chuyển yêu cầu tới nhà cung cấp model bên ngoài; điều này không đồng nghĩa model chạy hoàn toàn offline trên máy.

Với bài báo có video nhúng rõ ràng, bước tự động kiểm tra video trong trang nguồn và nhờ model 9Router chọn link liên quan; bản nháp được thêm dòng “Video ở dưới phần bình luận.”. Trang biên tập cũng có nút tìm video và ô sửa/dán URL. Sau khi Facebook xác nhận bài đã đăng, ứng dụng gửi link video thành bình luận của chính bài Page. Nếu phản hồi bình luận không rõ, bài xuất hiện trong **Cần xử lý**; kiểm tra bình luận trên Page rồi xác nhận đã có link hoặc cho gửi khi chắc chắn chưa có, tránh trùng. Tính năng chỉ gửi liên kết video, không tải lên hay đăng lại tệp video; quyền bình luận của Page token còn cần kiểm chứng bằng bài thật.

Đặt `REUP_AUTO_ENABLED=1` trước khi chạy để bật luồng tự động. Khi `run.py` còn chạy, hệ thống quét nguồn mỗi giờ và chuẩn bị tối đa **6 bài đạt/ngày** (giờ Bangkok), chỉ xét tin được phát hiện và đăng trong 48 giờ gần đây, kể cả tin đã lưu trước khi bật tự động nếu chưa có bản nháp. Bài được tạo bản nháp, chuẩn bị ảnh, viết bằng LLM và kiểm duyệt cả nội dung lẫn ảnh. Lỗi chuẩn bị tạm thời được thử lại tối đa 3 lần, cách nhau ít nhất 5 phút; bài bị kiểm duyệt từ chối được giữ lại để xem và không tự đăng. Khi đủ cấu hình Facebook Page, bài đạt được xếp vào các khung **07:00, 10:00, 13:00, 16:00, 19:00, 22:00** giờ Bangkok và được kiểm duyệt lần nữa trước khi gửi. Nếu chưa có Page ID/token, bài đạt nằm ở trạng thái bản nháp chờ kết nối; bài quá 48 giờ không được tự xếp lịch sau này. Trang **Tài khoản & kết nối** hiển thị lần quét và số bài đang chờ. Việc quét thủ công bằng nút “Tìm bài mới” vẫn dùng được, và không làm thay đổi bài đã tạo bản nháp thủ công.

Trên Windows, `scripts/start-local-services.ps1` có thể được gọi khi đăng nhập để khởi động 9Router và dashboard nếu chúng chưa chạy. Script lấy biến môi trường của người dùng và chỉ mở hai cổng trên localhost. Trên máy hiện tại, tác vụ Task Scheduler `reupNewsForSocial-local` đã được đăng ký ở chế độ đăng nhập người dùng. Máy cần bật và đăng nhập Windows để quy trình chạy; khi máy tắt, không thể tự quét hoặc gửi bài đúng giờ.

Hiện chỉ có adapter đăng Facebook Page. Luồng trang cá nhân, nhóm và LinkedIn chưa được tích hợp. Chưa thử gửi ảnh lên Page thật vì chưa có token của chủ dự án. Bài viết LLM chỉ dựa trên tiêu đề/tóm tắt feed và link nguồn; chưa đọc toàn văn bài báo và chưa học giọng văn cá nhân.

Kiểm tra cục bộ: `python -m unittest discover -s tests -v`.

## Chọn nhóm Facebook dự kiến đăng

Trang **Facebook** (`/facebook`) lưu tên/URL nhóm dự kiến đăng, cho chọn hoặc tạm dừng từng nhóm và xóa nhóm nhập nhầm. Đây là cấu hình đích để chuẩn bị tích hợp; ứng dụng chưa đăng vào nhóm và không dùng danh sách này khi chạy lịch. Trạng thái kết nối Facebook Page cũng xuất hiện trên trang này.

## Kết nối Facebook Page để đăng tự động

Ứng dụng chỉ cần **Page ID**, **Page access token** có quyền phù hợp và phiên bản Graph API; không yêu cầu App ID hoặc App Secret, cũng không bắt buộc tạo Meta App *mới* nếu đã có Page token hợp lệ từ một App/tích hợp khác. Nếu chưa có token, cách chủ động là dùng Meta App đang có hoặc [tạo App](https://developers.facebook.com/apps/), rồi mở [Graph API Explorer](https://developers.facebook.com/tools/explorer/) để cấp quyền Page. Dùng User access token gọi `/me/accounts?fields=id,name,access_token,tasks`, chọn đúng Page và lấy ID/token; [bộ ví dụ Pages API của Meta](https://www.postman.com/meta/facebook/documentation/r56bjfd/facebook-api) mô tả luồng này. Giữ token trên máy, không đưa vào chat hay Git.

Mở PowerShell ở repo và chạy `scripts/configure-facebook-page.ps1`. Script hỏi Page ID, phiên bản Graph API và token bằng đầu vào ẩn; chỉ gọi `GET /<page-id>?fields=id,name` để xác minh đúng Page trước khi lưu ba biến vào môi trường User của Windows. Chạy lại với `-Check` để kiểm tra cấu hình đã lưu. Phép kiểm tra đọc này **chưa chứng minh quyền đăng**; xem các bài đang chờ, khởi động lại dashboard rồi thử một bài có kiểm soát trước khi để lịch tự chạy. Dashboard đang dùng `REUP_AUTO_ENABLED=1` sẽ tự xếp lịch bài đạt sau khi có cấu hình Page.

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
