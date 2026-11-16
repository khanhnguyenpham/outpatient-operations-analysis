# Từ điển dữ liệu

## Dữ liệu nguồn và view báo cáo

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `appointment_id` | chuỗi | Mã lịch hẹn mô phỏng, duy nhất |
| `patient_id` | chuỗi | Mã người bệnh mô phỏng đã băm; không đại diện người thật |
| `appointment_date` | ngày | Ngày hẹn theo lịch địa phương |
| `department` | danh mục | Chuyên khoa ngoại trú |
| `appointment_hour` | số nguyên | Giờ hẹn, từ 07 đến 16 |
| `weekday_name` | danh mục | Tên thứ do thư viện ngày giờ sinh ra; dashboard chuyển sang tiếng Việt |
| `lead_days` | số nguyên | Số ngày từ lúc đặt đến ngày hẹn |
| `prior_no_shows` | số nguyên | Số lần vắng trước đó trong dữ liệu mô phỏng |
| `reminder_sent` | nhị phân | 1 nếu ghi nhận đã gửi nhắc hẹn, ngược lại là 0 |
| `outside_city` | nhị phân | 1 nếu thuộc nhóm mô phỏng ở ngoài thành phố |
| `status` | danh mục | `Hoàn thành`, `Vắng hẹn` hoặc `Đã hủy` |
| `no_show` | nhị phân | 1 khi và chỉ khi trạng thái là `Vắng hẹn` |
| `checkin_wait_minutes` | số thập phân/rỗng | Số phút từ lúc đến nơi đến khi hoàn tất tiếp nhận |
| `room_wait_minutes` | số thập phân/rỗng | Số phút từ hoàn tất tiếp nhận đến khi vào phòng khám |
| `clinician_wait_minutes` | số thập phân/rỗng | Số phút từ khi vào phòng đến khi bắt đầu được phục vụ |
| `wait_minutes` | số thập phân/rỗng | Số phút từ đến nơi đến bắt đầu phục vụ; chỉ có ở lượt hoàn thành |

## Các bảng trong kho dữ liệu

- `fact_appointment`: một dòng cho mỗi lịch hẹn, chứa số đo, trạng thái và khóa chiều.
- `dim_date`: thuộc tính lịch của từng ngày hẹn.
- `dim_department`: khóa số nguyên ổn định và tên chuyên khoa.
- `appointments`: view dành cho phân tích, nối bảng sự kiện với hai bảng chiều.

Mô hình không chứa họ tên, số điện thoại, địa chỉ, bệnh án hoặc chẩn đoán vì các trường này không cần thiết cho câu hỏi vận hành.
