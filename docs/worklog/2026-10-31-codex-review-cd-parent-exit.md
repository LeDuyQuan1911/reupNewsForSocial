# Review CD khi dashboard launcher tự thoát

- Ngày: 2026-10-31
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Review độc lập diff từ `2d02824daa848a703d2be2dba451cac2134fc0eb` đến `488a82b7b7732a62f4cb639bdd79872b647b54af`, tập trung vào dừng dashboard trong CD, PID tái sử dụng, bảo vệ tiến trình ngoài dashboard và khả năng phục hồi. Không sửa implementation.

## Thực hiện
Đã đọc yêu cầu review, quy trình, diff và luồng dừng dashboard/rollback trong worktree reviewer riêng. Lượt đầu ghi hai phát hiện P2 vào `reviews/reports/cd-parent-exit.md`: CIM trả rỗng khiến launcher còn sống bị bỏ qua; xác minh `CreationDate` tách khỏi lệnh dừng bằng PID nên vẫn có cửa sổ PID tái sử dụng. Lượt đối chiếu head `4f332e92` rút lại cả hai phát hiện dựa trên thay đổi source và test mới. Không sửa implementation.

## Quyết định
Đánh giá trên source và test thực tế, không đọc worklog hoặc giải thích của tác giả trong lượt độc lập. Chỉ ghi lỗi có điều kiện kích hoạt và bằng chứng cụ thể.

## Kiểm chứng
Lượt đầu: hai lệnh unittest theo yêu cầu đều đạt (mỗi lệnh 1 test). Mô phỏng PowerShell dùng định nghĩa hàm thật xác nhận lỗi cũ. Lượt đối chiếu: test dashboard đạt 3/3, test cú pháp PowerShell 5 đạt 1/1 trên head `4f332e92`. Chưa chạy trên server thật.

## Còn lại
Không có phát hiện còn mở. Chưa kiểm tra CD thực tế trên server hoặc đường rollback bằng tiến trình thật; chủ repo quyết định merge.
