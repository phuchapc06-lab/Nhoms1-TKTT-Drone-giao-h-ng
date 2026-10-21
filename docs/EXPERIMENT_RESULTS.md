# BÁO CÁO KẾT QUẢ THỬ NGHIỆM ĐỐI SÁNH HIỆU NĂNG THUẬT TOÁN
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UDRP)
**Ngày tạo:** 2026-10-21 16:30:25
**Phụ trách thực nghiệm:** Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

### 1. Bảng số liệu tổng hợp đa quy mô (Multi-scale Experimental Results)

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 10 | 3 | 377.25 | 296.41 | **21.43%** | **12.21%** | **17.95%** | 0.0012 | 0.4596 |
| 20 | 6 | 517.00 | 448.03 | **13.34%** | **9.78%** | **10.90%** | 0.0006 | 1.0947 |
| 30 | 9 | 695.47 | 635.83 | **8.58%** | **7.88%** | **8.39%** | 0.0015 | 2.3218 |

### 2. Nhận xét & Đánh giá Khoa học
- **Mức độ tối ưu quãng đường:** Giải thuật Di truyền đề xuất ($A^* + GA$) giúp rút ngắn trung bình **14.45%** quãng đường bay so với Baseline Tham lam ($A^* + Greedy$).
- **Hiệu quả sử dụng năng lượng pin:** Nhờ tối ưu thứ tự giao hàng và tải trọng, mức tiêu thụ pin giảm trung bình **9.96%**, hạn chế đáng kể số lần UAV phải ghé trạm sạc.
- **Thời gian tính toán & Khả năng mở rộng:** Mặc dù thuật toán GA có thời gian tính toán lớn hơn Greedy, toàn bộ thời gian thực thi vẫn nằm trong ngưỡng vài giây (real-time planning), đáp ứng hoàn hảo yêu cầu vận hành đô thị thông minh.
