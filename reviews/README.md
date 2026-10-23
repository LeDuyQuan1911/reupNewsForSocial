# Review code độc lập

Áp dụng khi plugin `independent-review` bật. Mục tiêu là giúp reviewer đánh giá thay đổi dựa trên yêu cầu và hành vi thực tế, trước khi bị ảnh hưởng bởi lời giải thích của agent viết code.

## Vai trò

- **Tác giả:** viết code, tự kiểm tra, cung cấp branch hoặc PR. Không tự chấm chất lượng thay reviewer.
- **Người điều phối:** chọn base/head, điền tiêu chí chấp nhận từ `SPEC.md`, giao cho reviewer khác; giữ quyền quyết định merge cho chủ repo.
- **Reviewer:** dùng một phiên chat/ngữ cảnh riêng và checkout/worktree riêng; lượt đầu chỉ đọc, không sửa code.

## Hai lượt review

Người điều phối có thể tạo bản yêu cầu trung tính từ hai Git ref bằng:

```powershell
node scripts/review-brief.mjs main ten-branch task-id
```

Lệnh điền SHA và danh sách file thay đổi vào `reviews/requests/task-id.md`, không kèm tên hay nhận xét của tác giả. Code cần có commit ở hai ref; thay đổi chưa commit không xuất hiện trong diff. Trước khi giao reviewer, điền tiêu chí chấp nhận và lệnh kiểm tra thực tế; file có sẵn sẽ không bị ghi đè.

1. **Lượt độc lập:** reviewer nhận [mẫu yêu cầu](templates/REQUEST.md) đã điền, code tại head và diff so với base. Xem `SPEC.md`, test và vùng code liên quan. Chưa đọc worklog của tác giả, PR description, commit message, nhận xét của reviewer khác hoặc danh tính tác giả nếu có thể tránh. `git diff <base>...<head>` hiển thị thay đổi mà không cần xem metadata tác giả.
2. **Lượt đối chiếu:** sau khi reviewer lưu [báo cáo đầu tiên](templates/REPORT.md), người điều phối cung cấp giải thích và kiểm chứng của tác giả. Reviewer xác nhận, sửa hoặc rút lại phát hiện dựa trên bằng chứng mới, ghi rõ thay đổi kết luận.

Tách ngữ cảnh giúp giảm thiên vị, nhưng không tạo ẩn danh tuyệt đối: tên tác giả có thể xuất hiện trong code, lịch sử Git hoặc PR. Reviewer cần đánh giá hành vi, không suy đoán chất lượng dựa trên tên công cụ hay người viết.

## Những gì cần kiểm tra

- Hành vi so với tiêu chí chấp nhận và trường hợp biên.
- Lỗi có thể tái hiện, hồi quy, dữ liệu bị mất, quyền truy cập hoặc secrets bị lộ.
- Test có kiểm tra đúng hành vi quan trọng hay chỉ xác nhận implementation.
- Phạm vi thay đổi và tác động sang module khác.

Không tạo phát hiện chỉ để có số lượng. Với mỗi phát hiện, ghi mức độ, file và dòng, điều kiện kích hoạt, kết quả thực tế, kết quả mong đợi và độ chắc chắn. Nếu không có phát hiện, ghi rõ phạm vi đã xem, kiểm tra đã chạy và rủi ro chưa kiểm chứng. Phân biệt lỗi đã xác nhận với nghi vấn.

## Bàn giao và merge

Reviewer lưu report trong `reviews/reports/<task-id>.md` ở branch/worktree riêng và ghi worklog theo `docs/worklog/README.md`. Người điều phối cung cấp report cho tác giả để sửa hoặc phản hồi, rồi trình cả diff và report cho chủ repo. Chỉ chủ repo quyết định merge vào `main`; xem `governance/README.md`.

Nếu reviewer và tác giả bất đồng, giữ nguyên bằng chứng và nêu lựa chọn cho chủ repo. Không biến report thành biểu quyết giữa các agent.
