# Làm ảnh AI nhận ra ngay nội dung bài

- Ngày: 2026-10-26
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Thay ảnh AI trừu tượng của bản nháp OpenAI–NASK bằng ảnh có điểm nhấn về chủ thể và thông tin chính; cập nhật tiêu chí ảnh tạo mới.

## Thực hiện
Tạo ảnh editorial mới bằng công cụ imagegen: tiêu điểm chữ “OpenAI × NASK”, dòng “AI SAFETY RESEARCH” và ba bước đánh giá mô hình, tìm lỗ hổng tiềm tàng, tăng cường biện pháp bảo vệ. Chuyển thành JPEG và thay ảnh đầu của bản nháp #1 trong SQLite cục bộ. Cập nhật `SPEC.md` và `PLAN.md` để ảnh AI sau này có điểm nhấn nhận ra ngay và không gán nhân vật không có trong nguồn.

## Quyết định
Không dùng hình người sáng lập vì bài gốc không đề cập nhân vật này. Dùng tên hai tổ chức và nội dung hợp tác đã được nguồn nêu; ảnh là đồ họa giải thích, không trình bày như ảnh chụp sự kiện thật.

## Kiểm chứng
Xem trực quan JPEG cuối: chữ chính rõ và không sai chính tả. Flask test client trả HTTP 200 cho `/posts/1` và `/posts/1/image`; ảnh 1600×837 JPEG, bản nháp #1 có một ảnh loại `ai_generated` và vẫn ở trạng thái `draft`.

## Còn lại
Ảnh và dữ liệu bản nháp nằm trong `data/` bị Git bỏ qua; không xuất bản lên Facebook. Chưa chạy kiểm duyệt bằng model vision thật.
