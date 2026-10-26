# Token cho tự đăng một nhóm

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Ước lượng định tính số token tăng thêm khi tự đăng một bài vào một nhóm Facebook.

## Thực hiện
Đọc `app/automation.py`, `app/queue.py`, `app/research.py` và `app/llm.py` để tách lượt gọi AI chuẩn bị bài với lượt điều khiển trình duyệt dự kiến. Không gọi model hay Facebook; không sửa code.

## Quyết định
Không đưa con số token cố định vì chưa có adapter đăng nhóm hoặc đo bằng phiên thật. Nếu dùng thao tác trình duyệt theo kịch bản cố định, một nhóm không cần thêm lượt gọi LLM; nếu để Hermes tự nhìn và quyết định từng bước, token tăng theo số nhóm và số bước/ảnh chụp.

## Kiểm chứng
Source xác nhận đánh giá tin theo lô, viết một bản nháp và kiểm duyệt từng ảnh ở lúc chuẩn bị; khi đăng Page hiện tại kiểm duyệt lại từng ảnh. Chưa có lời gọi AI nào cho đích nhóm vì chưa có adapter nhóm.

## Còn lại
Cần thử một nhóm với phiên đăng nhập thật và ghi usage từ 9Router/Hermes để đo token cụ thể trước khi nhân ra nhiều nhóm. Không có kiểm chứng chi phí tiền vì giá model phụ thuộc 9Router và có thể thay đổi.
