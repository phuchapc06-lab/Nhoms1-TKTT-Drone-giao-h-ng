# BÁO CÁO KẾT QUẢ THỬ NGHIỆM ĐỐI SÁNH HIỆU NĂNG THUẬT TOÁN
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UDRP)
**Ngày tạo:** 2026-10-21 16:45:16
**Phụ trách thực nghiệm:** Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

### 1. Bảng số liệu tổng hợp đa quy mô (Multi-scale Experimental Results)

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Đúng giờ Greedy (%) | Đúng giờ GA (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 6 | 3 | 328.09 | 283.32 | **13.65%** | **14.42%** | 83.3% | 100.0% | **18.66%** | 0.0011 | 0.2396 |
| 12 | 4 | 362.67 | 302.18 | **16.68%** | **14.89%** | 91.7% | 100.0% | **19.37%** | 0.0002 | 0.5513 |

### 2. Nhận xét & Đánh giá Khoa học
- **Mức độ tối ưu quãng đường:** Giải thuật Di truyền đề xuất ($A^* + GA$) giúp rút ngắn trung bình **15.16%** quãng đường bay so với Baseline Tham lam ($A^* + Greedy$).
- **Hiệu quả sử dụng năng lượng pin:** Nhờ tối ưu thứ tự giao hàng và tải trọng, mức tiêu thụ pin giảm trung bình **14.66%**, hạn chế đáng kể số lần UAV phải ghé trạm sạc.
- **Tỷ lệ giao hàng đúng giờ (Time Windows):** Thuật toán GA đạt tỷ lệ giao đúng hẹn trung bình **100.0%**, giảm thiểu các khoản phạt vi phạm khung giờ giao hàng của khách hàng.
- **Thời gian tính toán & Khả năng mở rộng:** Mặc dù thuật toán GA có thời gian tính toán lớn hơn Greedy, toàn bộ thời gian thực thi vẫn nằm trong ngưỡng vài giây (real-time planning), đáp ứng hoàn hảo yêu cầu vận hành đô thị thông minh.
