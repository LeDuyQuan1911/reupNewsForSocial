# Hướng dẫn cho coding agent

## Khi bắt đầu một nhiệm vụ

1. Đọc `README.md`, `MAP.md`, `SPEC.md` và phần liên quan của `PLAN.md`.
2. Đọc `project.plugins.json`; chỉ đọc và áp dụng `plugins/<id>/INSTRUCTIONS.md` của các plugin đang bật. Nếu cấu hình sai, báo lỗi trước khi triển khai.
3. Nếu nhiệm vụ phụ thuộc vào quyết định đã có, đọc `contexte/` trước khi sửa code.
4. Kiểm tra trạng thái Git và file hiện có. Không giả định repo đã có ứng dụng, test hay công cụ build.
5. Nếu thiếu thông tin cốt lõi trong `SPEC.md`, hỏi đúng phần thiếu. Có thể làm các phần độc lập trong lúc chờ.

## Nhật ký bắt buộc

- Với mỗi yêu cầu liên quan đến repo, tạo một file riêng theo `docs/worklog/README.md` khi bắt đầu. Áp dụng cả cho khảo sát, review, sửa code và thay đổi tài liệu; không phụ thuộc plugin `documentation`.
- Ghi yêu cầu/phạm vi trước khi làm. Trước khi bàn giao, điền thay đổi hoặc phát hiện, lý do/quyết định, kiểm chứng, giới hạn và bước tiếp theo. Nếu không có mục nào, ghi rõ "Không có"; không để mẫu trống.
- Nếu có nhiều agent, mỗi agent chỉ sửa worklog của nhiệm vụ mình. Ghi đường dẫn worklog trong phần bàn giao.
- Không ghi secrets hay dữ liệu riêng tư vào worklog.
- Chạy `node scripts/check-worklog.mjs <tên-file.md>` trước khi bàn giao. Nếu môi trường không có Node, đối chiếu thủ công với mẫu trong `docs/worklog/README.md` và báo rõ.

## Cách làm việc

- Chỉ tạo file hoặc thư mục khi có mục đích cụ thể. Giữ thay đổi nhỏ, dễ review.
- Dùng source và test thực tế làm căn cứ; không ghi tài liệu như thể tính năng chưa xây đã tồn tại.
- Không ghi đè thay đổi của người dùng. Không xóa dữ liệu hoặc sửa lịch sử Git khi chưa được yêu cầu rõ.
- Không đưa mật khẩu, token, API key hoặc nội dung `.env` vào code, log, tài liệu hay commit. Dùng biến môi trường; chỉ thêm `.env.example` khi biết tên biến thực sự cần dùng, với giá trị giả.
- Chạy kiểm tra phù hợp với thay đổi. Nếu chưa có test/build, nói rõ đã kiểm tra bằng cách nào và còn gì chưa kiểm chứng.
- Khi thay đổi cấu trúc file hoặc đường đi chính, cập nhật `MAP.md`. Khi chốt quyết định kỹ thuật quan trọng, ghi vào `contexte/decisions.md`. Khi thay đổi phạm vi/yêu cầu, cập nhật `SPEC.md`; khi hoàn thành bước, cập nhật `PLAN.md`. Trong phiên làm việc song song, tuân theo quyền sở hữu tài liệu chung trong `MULTI_AGENT.md`.
- Trước khi dùng công cụ bên ngoài, MCP, phụ thuộc mới hoặc quyền truy cập mới, nêu mục đích và phạm vi cần thiết. Không tự thêm cấu hình chỉ để đủ bộ khung.

## Git và làm việc song song

- Khi Codex, Antigravity hoặc Claude cùng làm việc, áp dụng `MULTI_AGENT.md`. Mỗi nhiệm vụ độc lập dùng branch/worktree riêng; nêu rõ nhiệm vụ và phạm vi file của từng agent.
- Trước khi commit hoặc push, xem diff, chạy kiểm tra liên quan và rà soát secrets. Review trước khi merge; worktree không tự giải quyết xung đột.
- Khi plugin `independent-review` bật, không tự review thay cho reviewer độc lập đối với thay đổi code dự kiến merge vào `main`. Dùng quy trình tại `reviews/README.md`.
- Không push, tạo PR, merge hoặc đổi trạng thái remote nếu nhiệm vụ hiện tại chưa yêu cầu.
- Chỉ chủ repo `LeDuyQuan1911` quyết định merge vào `main`. Agent khác có thể tạo PR khi được giao, nhưng không tự merge; agent chỉ thực hiện merge khi chủ repo yêu cầu rõ đối với PR cụ thể. Xem `governance/README.md`.

## Khi bàn giao

Tóm tắt file đã đổi, lý do, kết quả kiểm tra, giới hạn còn lại, bước tiếp theo và đường dẫn worklog.

## Ngữ cảnh biên tập cho Hermes trong repo này

- Nguồn đang vận hành: RSS/Atom và bài chính thức từ hãng công nghệ, cùng repo GitHub mới nổi. Reddit và Threads là nguồn có thể thêm sau, chưa được quét tự động.
- Số bài tự động mỗi ngày và các giờ đăng Facebook Page do chủ dự án đặt trong trang Tài khoản; mặc định 6 bài ở các giờ đã lưu. Đăng nhóm/trang cá nhân để sau. Không tự gửi bài chưa được duyệt nội dung và từng ảnh; tránh tin trùng và giữ URL nguồn gốc.
- Bài đăng viết bằng tiếng Việt cho cộng đồng IT: mở bằng chi tiết đáng chú ý có căn cứ, giải thích điểm mới và giá trị thực tế bằng đoạn ngắn. Dùng **ít nhất một icon/emoji có ý nghĩa**, nhưng để model tự chọn số lượng, vị trí và biểu tượng; không áp mẫu mỗi dòng một icon. Thêm 2–5 hashtag liên quan. Không sao chép câu chữ hoặc bịa dữ kiện.
- Mỗi bài có ít nhất một ảnh nhận diện ngay chủ thể: ưu tiên ảnh bài gốc, demo/screenshot/README của repo, rồi ảnh chụp repo. Ảnh AI chỉ là dự phòng khi không có ảnh thật, phải có chi tiết bám sát nguồn; thẻ tiêu đề chung chung không đủ điều kiện đăng.
- Nếu nguồn có video liên quan và kiểm chứng được URL, bài báo có thể hẹn video dưới bình luận; chỉ bình luận link sau khi bài Page đăng thành công.
- Khi viết bản nháp, dashboard gọi Hermes như tác giả qua model 9Router. Mỗi lượt soạn nạp `docs/editorial-brief.md` và dữ kiện nguồn. Hermes cron điều phối quét/chuẩn bị/lịch đăng qua runner của repo; các giới hạn và bước duyệt trước đăng vẫn ở code ứng dụng. Các bước AI khác dùng model 9Router trực tiếp. Key và Page token chỉ nằm trong biến môi trường, không đưa vào file hoặc câu trả lời.
