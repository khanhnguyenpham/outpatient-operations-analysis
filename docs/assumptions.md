# Sổ đăng ký giả định

| Mã | Giả định mô phỏng | Lý do | Rủi ro khi dùng dữ liệu thật | Cách kiểm tra trong thực tế |
|---|---|---|---|---|
| A01 | Một dòng tương ứng một lịch hẹn | Xác định rõ grain của bảng sự kiện | Trùng lịch hoặc đổi lịch có thể tạo nhiều dòng | Đối chiếu quy tắc mã lịch với hệ thống nguồn |
| A02 | Lịch đã hủy không nằm trong mẫu số vắng hẹn | Hủy và vắng là hai hành vi khác nhau | Quy trình hủy muộn có thể được ghi nhận không nhất quán | Thống nhất định nghĩa với bộ phận tiếp nhận |
| A03 | Thời gian chờ chỉ có ở lượt hoàn thành | Không suy diễn thời gian cho lượt không phục vụ | Một số lượt rời đi giữa chừng có thể bị thiếu trạng thái | Bổ sung trạng thái rời hàng đợi và kiểm tra timestamp |
| A04 | Tổng chờ bằng ba công đoạn | Cho phép định vị nút thắt | Timestamp thực tế có thể chồng lấn hoặc thiếu | Đối soát thứ tự sự kiện và sai lệch tổng thời gian |
| A05 | Gửi nhắc hẹn liên quan đến số ngày đặt trước | Tạo tình huống có yếu tố gây nhiễu | So sánh thô có thể phóng đại hiệu quả nhắc hẹn | Điều chỉnh theo lead time hoặc thử nghiệm có đối chứng |
| A06 | Ngưỡng chính là 50 lượt hoàn thành | Hạn chế xếp hạng từ mẫu quá nhỏ | Ngưỡng tùy ý có thể thay đổi thứ hạng | Báo cáo độ nhạy ở ngưỡng 30, 50 và 70 |

Các giả định này mô tả cách xây dựng đồ án, không phải nhận định về một bệnh viện thật.
