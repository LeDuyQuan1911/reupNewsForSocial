# Chọn tin tự động và đối chiếu bài đang đăng

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Tiếp tục rà luồng xử lý của trang web, bổ sung bước chọn tin đáng viết trước khi tự chuẩn bị tối đa 6 bài/ngày và cách xử lý bài kẹt ở trạng thái `publishing` mà không tự gửi trùng. Dùng hai skill UI để thể hiện trạng thái và thao tác rõ ràng trên các trang liên quan.

## Thực hiện
Đọc code, dữ liệu SQLite cục bộ và luồng tự động. Thêm `app/research.py` để đánh giá tối đa 30 metadata tin mới trong một lời gọi model văn bản, lưu điểm/lý do trong `research_reviews`, phân bố nguồn trong sáu vị trí đầu và dùng thứ tự dự phòng khi model lỗi. Tích hợp vào `app/automation.py` trước khi tạo bản nháp; trang Bài báo có bộ lọc và giải thích điểm.

Thêm thời điểm bắt đầu gửi vào `posts`. Bài `publishing` quá 45 phút hiện trong nhóm Cần xử lý, có thao tác chuyển sang đối chiếu; chỉ xác nhận đã/chưa đăng sau khi kiểm tra Page. Cập nhật `MAP.md`, `SPEC.md`, `PLAN.md`, `contexte/decisions.md` và các test.

## Quyết định
Chỉ xếp hạng từ tiêu đề/tóm tắt feed, không trình bày như đã xác minh toàn văn. Không tự gửi lại bài có kết quả Facebook chưa rõ; thời gian 45 phút lớn hơn thời gian tối đa dự kiến cho 10 lần kiểm duyệt ảnh và 10 lần gửi ảnh theo timeout hiện tại.

## Kiểm chứng
`python -m unittest discover -s tests -q`: 41 test đạt. Kiểm tra giao diện Bài báo bằng Chromium headless ở 1365px và 390px, không tràn ngang. Sẽ chạy lại kiểm tra cuối cùng sau khi hoàn tất mọi thay đổi.

## Còn lại
Chưa thử gửi Facebook Page thật vì chưa có kết nối; đánh giá AI chưa đọc toàn văn và cần kiểm chứng với model 9Router đang dùng. Nhận diện trùng nội dung dù tiêu đề khác chưa làm.
