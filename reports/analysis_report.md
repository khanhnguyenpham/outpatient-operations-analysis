# Báo cáo phân tích vận hành khám ngoại trú

## Tóm tắt điều hành

Phân tích sử dụng 6.500 lịch hẹn ngoại trú mô phỏng từ tháng 01/2025 đến tháng 10/2026. Đây là đồ án năng lực cá nhân, không phải đánh giá về một bệnh viện thật.

Tín hiệu vận hành rõ nhất nằm ở **thời gian chờ**, không phải khác biệt vắng hẹn giữa các chuyên khoa. Tim mạch có thời gian chờ trung vị 35,9 phút và P90 50,5 phút, cao nhất trong sáu chuyên khoa. Ba lát cắt ổn định đứng đầu là Tim mạch lúc 09:00, 10:00 và 14:00, với P90 từ 54,1 đến 56,7 phút. Đây là các vị trí nên kiểm tra trước về dồn lượt đến, phòng khám và cấu hình lịch hẹn.

Phân rã theo công đoạn cho thấy phần chờ từ lúc vào phòng đến khi bắt đầu khám là thành phần lớn nhất tại Tim mạch: trung bình 20,8 trên tổng 35,6 phút. Ba khung giờ Tim mạch vẫn đứng đầu khi thay ngưỡng cỡ mẫu từ 30 lên 50 và 70 lượt, vì vậy kết luận ưu tiên không phụ thuộc riêng vào ngưỡng chính 50 lượt.

Tỷ lệ vắng hẹn chung là 13,79%. Nhóm có ghi nhận nhắc hẹn là 12,42%, so với 18,66% ở nhóm không ghi nhận, chênh lệch 6,24 điểm phần trăm. Không được xem đây là tác động nhân quả vì khả năng gửi nhắc hẹn trong dữ liệu mô phỏng có liên quan đến số ngày đặt trước.

## Phạm vi và phương pháp

- **Đơn vị dữ liệu:** một dòng tương ứng một lịch hẹn ngoại trú.
- **Mẫu số vắng hẹn:** lượt hoàn thành cộng lượt vắng; loại trừ lịch đã hủy.
- **Tập tính thời gian chờ:** chỉ gồm lượt khám hoàn thành.
- **Thống kê thời gian:** dùng trung vị và P90 để không che khuất đuôi phân phối.
- **Phân rã quy trình:** tổng chờ bằng tiếp nhận, chờ vào phòng và chờ bắt đầu khám.
- **Ngưỡng lát cắt:** chỉ xếp hạng chuyên khoa – khung giờ có ít nhất 50 lượt hoàn thành.
- **Độ nhạy:** so sánh thứ hạng ở ngưỡng 30, 50 và 70 lượt hoàn thành.
- **Kiểm soát thống kê:** dùng biểu đồ p với giới hạn ba sigma cho tỷ lệ vắng theo tháng.
- **Lưu trữ:** dữ liệu nguồn được nạp vào SQLite theo mô hình sao và cung cấp qua view báo cáo.

Quy trình kiểm tra mã định danh, ngày, danh mục, biến nhị phân, quy tắc thời gian chờ và tính nhất quán giữa trạng thái với nhãn vắng hẹn. Kết quả đối soát là 6.500 dòng nguồn, 6.500 dòng bảng sự kiện, 6.500 dòng view báo cáo và không có khóa ngoại mồ côi.

## Phát hiện chính

### 1. Tim mạch là điểm cần ưu tiên về thời gian chờ

| Chuyên khoa | Lượt hoàn thành | Chờ trung vị | Chờ P90 | Tỷ lệ vắng |
|---|---:|---:|---:|---:|
| Tim mạch | 885 | 35,9 phút | 50,5 phút | 13,74% |
| Chấn thương chỉnh hình | 727 | 32,2 phút | 45,8 phút | 13,35% |
| Nội tiết | 362 | 29,4 phút | 43,7 phút | 14,01% |
| Nội tổng quát | 1.608 | 27,7 phút | 42,6 phút | 13,78% |
| Mắt | 559 | 22,7 phút | 37,1 phút | 14,00% |
| Nhi | 1.154 | 21,1 phút | 35,8 phút | 13,94% |

Tỷ lệ vắng hẹn giữa các chuyên khoa khá gần nhau, trong khi phân phối thời gian chờ khác biệt rõ. Vì vậy, rà soát hàng đợi theo từng chuyên khoa có tính mục tiêu hơn một biện pháp điểm danh áp dụng giống nhau cho toàn hệ thống.

### 2. Ba khung giờ Tim mạch đứng đầu bảng áp lực

| Chuyên khoa và giờ | Lượt hoàn thành | Chờ trung bình | Chờ P90 |
|---|---:|---:|---:|
| Tim mạch 09:00 | 129 | 41,9 phút | 56,7 phút |
| Tim mạch 10:00 | 112 | 40,4 phút | 55,1 phút |
| Tim mạch 14:00 | 93 | 40,9 phút | 54,1 phút |
| Chấn thương chỉnh hình 10:00 | 95 | 36,6 phút | 52,2 phút |
| Chấn thương chỉnh hình 14:00 | 89 | 37,2 phút | 52,2 phút |

Xếp hạng này chỉ ra đúng chuyên khoa và cửa sổ lịch hẹn nên dễ hành động hơn trung bình theo cả ngày. Tuy nhiên, nó chưa xác định nguyên nhân gốc.

### 3. Chờ bắt đầu khám là thành phần lớn nhất tại Tim mạch

| Chuyên khoa | Tiếp nhận | Chờ vào phòng | Chờ bắt đầu khám | Tổng chờ trung bình |
|---|---:|---:|---:|---:|
| Tim mạch | 7,0 phút | 7,8 phút | 20,8 phút | 35,6 phút |
| Chấn thương chỉnh hình | 6,8 phút | 8,6 phút | 16,1 phút | 31,6 phút |
| Nội tiết | 7,4 phút | 8,1 phút | 13,6 phút | 29,1 phút |
| Nội tổng quát | 6,8 phút | 7,3 phút | 13,5 phút | 27,5 phút |
| Mắt | 5,8 phút | 5,9 phút | 11,0 phút | 22,7 phút |
| Nhi | 5,3 phút | 5,8 phút | 10,2 phút | 21,3 phút |

Thành phần chờ bắt đầu khám chiếm khoảng 58% tổng thời gian chờ trung bình của Tim mạch. Với dữ liệu thật, đây là lý do để kiểm tra lịch bác sĩ, thời lượng ca trước và thời điểm sẵn sàng của phòng; chưa phải bằng chứng thiếu nhân sự.

### 4. Kết luận ưu tiên bền vững với ba ngưỡng cỡ mẫu

| Ngưỡng tối thiểu | Hạng 1 | Hạng 2 | Hạng 3 |
|---:|---|---|---|
| 30 lượt | Tim mạch 09:00 | Tim mạch 10:00 | Tim mạch 14:00 |
| 50 lượt | Tim mạch 09:00 | Tim mạch 10:00 | Tim mạch 14:00 |
| 70 lượt | Tim mạch 09:00 | Tim mạch 10:00 | Tim mạch 14:00 |

Thứ hạng không thay đổi khi tăng ngưỡng từ 30 lên 70 lượt. Điều này không loại bỏ thiên lệch của dữ liệu mô phỏng, nhưng cho thấy khuyến nghị không được tạo ra chỉ bởi một lựa chọn ngưỡng thuận tiện.

### 5. Ghi nhận nhắc hẹn có liên hệ với tỷ lệ vắng thấp hơn

| Trạng thái nhắc hẹn | Lịch đủ điều kiện | Tỷ lệ vắng | Khoảng Wilson 95% |
|---|---:|---:|---:|
| Không ghi nhận | 1.345 | 18,66% | 16,67%–20,83% |
| Đã gửi | 4.797 | 12,42% | 11,52%–13,39% |

Khoảng tin cậy cho thấy khác biệt rõ trong bộ dữ liệu tạo sinh, nhưng đây vẫn là so sánh quan sát. Với dữ liệu thật, cần điều chỉnh theo số ngày đặt trước và các yếu tố lựa chọn khác, hoặc tốt hơn là triển khai thử nghiệm có nhóm đối chứng.

### 6. Biến động vắng hẹn theo tháng nằm trong giới hạn kiểm soát

Tỷ lệ vắng theo tháng dao động từ 9,66% đến 18,55%. Biểu đồ p sử dụng tỷ lệ chung 13,79% và giới hạn ba sigma thay đổi theo số lịch đủ điều kiện mỗi tháng. Không có tháng nào vượt giới hạn trên hoặc dưới. Vì vậy, biến động quan sát được phù hợp với nhiễu nguyên nhân chung trong bộ dữ liệu mô phỏng; không nên phản ứng với từng tháng riêng lẻ nếu chưa có bằng chứng vận hành bổ sung.

## Đề xuất hành động

1. Kiểm tra mẫu lịch của Tim mạch vào 09:00, 10:00 và 14:00 trước khi điều chỉnh nhân sự toàn khoa.
2. Đối chiếu timestamp thực tế ở ba công đoạn và kiểm tra chờ bắt đầu khám tại Tim mạch trước khi kết luận nguyên nhân.
3. Kiểm tra điều kiện nhận nhắc hẹn và tỷ lệ gửi thất bại; không dùng chênh lệch hiện tại như mức tác động nhân quả.
4. Bổ sung giới hạn kiểm soát và nhật ký sự kiện vào báo cáo tháng để phân biệt biến động ngẫu nhiên với thay đổi vận hành.
5. Chỉ tính lại bằng dữ liệu thật sau khi thống nhất định nghĩa với bộ phận tiếp nhận và vận hành lâm sàng.

## Giới hạn

- Mọi bản ghi đều là dữ liệu mô phỏng; kết quả không dùng để bố trí nhân sự hay liên hệ bệnh nhân.
- Quy luật được chủ động đưa vào bộ sinh dữ liệu, nên việc tìm thấy chúng không chứng minh hiệu quả trên dữ liệu thật.
- Ba công đoạn chờ được mô phỏng để minh họa cách định vị nút thắt; với dữ liệu thật cần xác nhận timestamp và trình tự sự kiện.
- Không có kết quả lâm sàng, lịch nhân sự hoặc công suất phòng.
- Việc gửi nhắc hẹn không được phân nhóm ngẫu nhiên.
