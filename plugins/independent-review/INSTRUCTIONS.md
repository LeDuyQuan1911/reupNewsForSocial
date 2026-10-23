# Plugin: Independent code review

Khi plugin này bật, mỗi thay đổi code dự kiến merge vào `main` phải có một lượt review độc lập theo [quy trình review](../../reviews/README.md). Agent review khác agent viết code và làm việc trong phiên ngữ cảnh riêng.

- Người điều phối chuẩn bị yêu cầu review trung tính theo mẫu, gồm base/head, phạm vi và tiêu chí chấp nhận; không đưa kết luận hoặc lời giải thích của tác giả vào lượt đầu.
- Reviewer chỉ đọc code và chạy kiểm tra, không sửa implementation trong lượt review. Ghi phát hiện có bằng chứng theo mẫu báo cáo.
- Sau báo cáo đầu tiên, tác giả được trả lời và reviewer có thể cập nhật kết luận khi có chứng cứ mới.
- Chủ repo xem code, kết quả kiểm tra và report để quyết định merge. Reviewer không tự merge.

Review không bảo đảm loại bỏ mọi thiên vị. Quy trình này giảm ảnh hưởng của danh tính, lời giải thích ban đầu và nhận xét trước đó bằng cách tách ngữ cảnh và yêu cầu dẫn chứng cụ thể.
