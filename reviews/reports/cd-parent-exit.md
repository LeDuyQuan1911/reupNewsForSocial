# Báo cáo review: cd-parent-exit

- Reviewer: Codex
- Ngày: 2026-10-31
- Base / head: `2d02824daa848a703d2be2dba451cac2134fc0eb` / `488a82b7b7732a62f4cb639bdd79872b647b54af`
- Vòng: độc lập
- Trạng thái: hoàn tất

## Phạm vi và kiểm tra

- File/luồng đã xem: diff của `scripts/cd/update-server.ps1` và `tests/test_cd_dashboard_stop.py`; toàn bộ hàm `Stop-OwnedDashboard`, lời gọi trong luồng triển khai và rollback, kiểm tra cổng 5000; yêu cầu tại `reviews/requests/cd-parent-exit.md`. Không đọc worklog hoặc giải thích của tác giả ở lượt này.
- Lệnh đã chạy và kết quả: `python -m unittest discover -s tests -p test_cd_dashboard_stop.py -v` (1 test đạt); `python -m unittest discover -s tests -p test_powershell5_syntax.py -v` (1 test đạt). Chạy thêm mô phỏng PowerShell lấy hàm thật bằng AST: khi lần truy vấn CIM thứ hai không trả launcher còn sống, hàm trả về, xóa PID file; kiểm tra bổ sung báo lỗi `Launcher remains alive while stop returned`.
- Phần chưa kiểm chứng: không chạy CD trên server thật và không tái hiện đua PID bằng tiến trình Windows thật.

## Phát hiện

### P2 — Lỗi tra cứu CIM có thể khiến CD tiếp tục khi launcher vẫn chạy

- Vị trí: `scripts/cd/update-server.ps1:65`
- Điều kiện kích hoạt / cách tái hiện: launcher còn sống sau khi dừng con, nhưng `Get-CimInstance` tại dòng 65 trả rỗng hoặc gặp lỗi bị `-ErrorAction SilentlyContinue` che. Trong mô phỏng, lần tra cứu đầu trả launcher, lần tra cứu sau trả rỗng dù launcher vẫn sống.
- Kết quả thực tế: hàm bỏ qua `Stop-Process` của launcher, xóa `dashboard.pid`, và hoàn tất khi cổng 5000 không còn listener. Mô phỏng xác nhận PID file đã bị xóa trong khi launcher còn sống.
- Kết quả mong đợi: không thể xác nhận launcher đã thoát thì CD phải dừng, giữ đủ thông tin để xử lý/retry; không chuyển sang checkout khi launcher vẫn chạy.
- Bằng chứng: nhánh `if ($remainingParent)` tại dòng 66 coi kết quả CIM rỗng là launcher đã thoát; chỉ kiểm tra cổng ở dòng 80–81. Test mới luôn trả trạng thái CIM nhất quán nên không kiểm tra đường này.
- Độ chắc chắn: cao đối với hành vi mô phỏng; tần suất lỗi CIM trên server thật chưa xác định.
- Hướng sửa gợi ý (nếu có): phân biệt lỗi truy vấn với tiến trình đã thoát và xác nhận trạng thái launcher qua một cơ chế thứ hai trước khi cho triển khai tiếp.

### P2 — Kiểm tra CreationDate chưa gắn với lệnh dừng PID

- Vị trí: `scripts/cd/update-server.ps1:65`
- Điều kiện kích hoạt / cách tái hiện: launcher thoát và PID được hệ điều hành cấp cho tiến trình khác sau khi CIM trả về ở dòng 65 nhưng trước `Stop-Process -Id $serverPid` tại dòng 70. Tương tự, PID con có thể đổi chủ sau khi lấy danh sách ở dòng 54 và trước lệnh dừng tại dòng 61.
- Kết quả thực tế: `Stop-Process -Id` tác động đến tiến trình đang mang PID vào thời điểm gọi; kiểm tra `CreationDate` trước đó không ràng buộc lệnh dừng với cùng tiến trình. Nếu PID đổi chủ trong cửa sổ này, tiến trình ngoài dashboard có thể bị dừng.
- Kết quả mong đợi: chỉ dừng đúng đối tượng đã xác minh là dashboard; PID tái sử dụng không được dừng.
- Bằng chứng: dòng 65–70 tách riêng lần xác minh `CreationDate` và lệnh dừng bằng PID; lệnh dừng con ở dòng 61 cũng chỉ dùng PID. Test mới chỉ mô phỏng launcher biến mất ngay sau khi dừng con, chưa mô phỏng PID đổi chủ.
- Độ chắc chắn: vừa; đây là cửa sổ đua hẹp, chưa tái hiện bằng tiến trình thật.
- Hướng sửa gợi ý (nếu có): giữ handle của đúng tiến trình sau khi xác minh danh tính và dừng qua handle đó, đồng thời xử lý tương tự cho tiến trình con.

## Đối chiếu sau phản hồi tác giả

Chưa thực hiện.

## Kết luận cho chủ repo

Đường launcher tự thoát được test mới xác nhận, nhưng hai nhánh trên chưa đáp ứng trọn vẹn điều kiện dừng khi launcher còn sống và bảo vệ PID tái sử dụng. Cần tác giả xử lý hoặc chứng minh điều kiện kích hoạt không thể xảy ra trong môi trường triển khai trước khi chủ repo quyết định merge.
