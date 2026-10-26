# Khả năng tự tìm tin và đăng bằng LLM local

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích liệu một LLM chạy trên máy có thể đến giờ tự tìm tin, viết và đăng bài, đặc biệt trong bối cảnh Facebook Page và nhóm. Đây là câu hỏi về kiến trúc hiện có; không yêu cầu thay đổi code hoặc gửi bài.

## Thực hiện
Đối chiếu `app/automation.py`, `app/queue.py`, `run.py` và cấu hình hiện tại. Chu kỳ đã quét nguồn theo giờ, đánh giá tin, viết và kiểm duyệt bằng model, chuẩn bị tối đa 6 bài/ngày; có sáu khung đăng giờ Bangkok. Bộ gửi Page chạy riêng và cần Page token/quyền. Nhóm chưa có adapter API.

## Quyết định
Trình bày LLM local là thành phần chọn/viết/duyệt; bộ lịch và quyền kênh đăng là hai phần độc lập. Không coi LLM local là cách vượt quyền API đăng nhóm.

## Kiểm chứng
Kiểm tra các hàm `run_cycle`, `schedule_ready`, `process_due_posts` và `process_claimed_post` trong source; không gọi Meta hoặc đăng bài thật.

## Còn lại
Chưa có Page token nên chưa kiểm chứng đăng thật. Đăng nhóm cần luồng thủ công hoặc nghiên cứu thao tác trình duyệt riêng; chưa thể bảo đảm tự động hoàn toàn qua API chính thức.
