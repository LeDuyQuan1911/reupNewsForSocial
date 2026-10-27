# Phân biệt 9Router và LLM chạy local

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Người dùng hỏi vì sao API key của 9Router có thể xử lý trên máy và làm rõ mong muốn dùng LLM tự host. Giải thích kiến trúc hiện có; không thay đổi code hay cấu hình.

## Thực hiện
Đối chiếu `app/llm.py`, `.env.example` và `run.py`. Ứng dụng gửi yêu cầu tới `REUP_LLM_BASE_URL` mặc định là cổng 9Router localhost; nơi model thật chạy phụ thuộc backend mà 9Router định tuyến. Bộ lịch và trình duyệt có thể chạy trên máy độc lập với nơi model suy luận.

## Quyết định
Nêu rõ 9Router localhost không đồng nghĩa suy luận local. Nếu cần dữ liệu và suy luận giữ trên máy, phải chạy model server local và trỏ ứng dụng tới endpoint đó (hoặc cấu hình router trỏ về nó), kiểm tra riêng model nhìn ảnh. Không đọc hoặc ghi API key thật.

## Kiểm chứng
Đọc source và tên biến cấu hình; không gọi endpoint hoặc kiểm tra secrets. Chạy kiểm tra worklog.

## Còn lại
Chưa biết model Hermes, phần cứng và endpoint người dùng định triển khai; chưa chứng minh model hiện được 9Router định tuyến là local hay cloud.
