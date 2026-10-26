# Giải thích thao tác trình duyệt theo bước cố định

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích cách chạy thao tác cố định để đăng nhóm và liệu đó có phải thao tác thủ công của người dùng.

## Thực hiện
Đối chiếu scheduler trong `run.py`, bộ đăng Page trong `app/queue.py` và bộ lưu nhóm đích trong `app/facebook_groups.py`. Không chạy trình duyệt Facebook, không gửi bài và không sửa code.

## Quyết định
Phân biệt người dùng đăng nhập/chọn quyền ban đầu với script tự thao tác khi đến giờ. Bước cố định là tự động hóa UI, không cần LLM quyết định mỗi cú nhấp, nhưng vẫn cần dừng khi phiên hết hạn, xác thực bổ sung hoặc giao diện thay đổi.

## Kiểm chứng
Source xác nhận tiến trình lịch hiện gọi `process_due_posts` và chỉ có đường gửi Page; nhóm mới chỉ được lưu URL, chưa có worker đăng nhóm.

## Còn lại
Cần một nhóm thử, danh tính đăng và phiên đăng nhập do người dùng tự tạo để xây và đo một luồng trình duyệt an toàn. Chưa chứng minh Facebook chấp nhận thao tác tự động trên nhóm.
