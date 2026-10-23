# Báo cáo review: <task-id>

- Reviewer: <agent>
- Ngày: YYYY-MM-DD
- Base / head: <SHA> / <SHA>
- Vòng: độc lập | đối chiếu
- Trạng thái: đang review | hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem:
- Lệnh đã chạy và kết quả:
- Phần chưa kiểm chứng:

## Phát hiện

Với mỗi phát hiện, dùng cấu trúc:

### <P0 | P1 | P2 | P3> — <tiêu đề ngắn>

- Vị trí: `path/to/file:line`
- Điều kiện kích hoạt / cách tái hiện:
- Kết quả thực tế:
- Kết quả mong đợi:
- Bằng chứng:
- Độ chắc chắn: cao | vừa | thấp
- Hướng sửa gợi ý (nếu có):

Nếu không có phát hiện, ghi `Không có phát hiện sau phạm vi kiểm tra nêu trên.`

## Đối chiếu sau phản hồi tác giả

Ghi phần này sau lượt độc lập: phát hiện nào được xác nhận, sửa, rút lại hoặc còn bất đồng, kèm lý do dựa trên bằng chứng. Nếu chưa có lượt đối chiếu, ghi `Chưa thực hiện.`

## Kết luận cho chủ repo

Tóm tắt rủi ro còn lại. Reviewer không quyết định merge.
