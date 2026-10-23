# Giải thích cách merge không bypass

- Ngày: 2026-10-22
- Agent: Codex
- Trạng thái: hoàn tất

## Yêu cầu và phạm vi
Giải thích điều gì xảy ra nếu không dùng nút bypass trên PR #2 và cách để chủ repo merge bằng nút thường mà vẫn kiểm soát quyền merge.

## Thực hiện
Đối chiếu ruleset hiện tại với tài liệu chính thức của GitHub về `Restrict updates`, bypass và quyền repository. Không thay đổi cấu hình GitHub.

## Quyết định
Không tự sửa ruleset hoặc quyền thành viên khi người dùng chỉ hỏi phương án.

## Kiểm chứng
Ruleset #25650325 đang bật trên `main`, có `update` và bypass actor `LeDuyQuan1911` ở chế độ `pull_request`. Tài liệu GitHub xác nhận `Restrict updates` chỉ cho actor có quyền bypass cập nhật nhánh; tùy chọn giới hạn push theo người dùng trong branch protection chỉ dành cho repository của organization.

## Còn lại
Nếu muốn bỏ bypass, chủ repo cần quyết định mô hình quyền: chỉ mình có quyền Write để người khác gửi PR từ fork, hoặc giữ quyền Write cho thành viên và chấp nhận họ có thể merge khi đủ điều kiện. Chưa thay đổi gì trên remote.
