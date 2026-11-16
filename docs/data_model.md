# Mô hình dữ liệu

Kho SQLite sử dụng mô hình sao nhỏ thay vì phân tích trực tiếp trên tệp CSV.

```text
dim_date ───────────┐
                    ├── fact_appointment ── appointments (view báo cáo)
dim_department ─────┘
```

`fact_appointment` lưu một dòng cho mỗi lịch hẹn và tham chiếu đến chiều ngày, chiều chuyên khoa. View `appointments` trả lại tên trường dễ đọc để các truy vấn nghiệp vụ không phải lặp lại câu lệnh nối bảng.

Ở mỗi lần chạy, quy trình kiểm tra:

1. số dòng nguồn bằng số dòng bảng sự kiện;
2. số dòng view báo cáo bằng số dòng nguồn;
3. không có khóa ngày hoặc chuyên khoa mồ côi;
4. các ràng buộc giờ hẹn, biến nhị phân, trạng thái và giá trị không âm được SQLite thực thi.

Mô hình được giữ có chủ đích ở quy mô nhỏ. Không xây dựng chiều người bệnh vì đồ án chỉ dùng mã mô phỏng và câu hỏi nghiệp vụ không cần thuộc tính cá nhân.
