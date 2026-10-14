# BÁO CÁO KẾT QUẢ THỬ NGHIỆM ĐỐI SÁNH HIỆU NĂNG THUẬT TOÁN
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UDRP)
**Ngày tạo:** 2026-10-14 15:27:46
**Phụ trách thực nghiệm:** Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

### 1. Bảng số liệu tổng hợp đa quy mô (Multi-scale Experimental Results)

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 6 | 3 | 279.14 | 237.50 | **14.92%** | **16.04%** | **23.33%** | 0.0001 | 0.1145 |
| 12 | 4 | 340.90 | 318.11 | **6.68%** | **9.06%** | **6.38%** | 0.0001 | 0.1462 |

### 2. Nhận xét & Đánh giá Khoa học
- **Mức độ tối ưu quãng đường:** Giải thuật Di truyền đề xuất ($A^* + GA$) giúp rút ngắn trung bình **10.80%** quãng đường bay so với Baseline Tham lam ($A^* + Greedy$).
- **Hiệu quả sử dụng năng lượng pin:** Nhờ tối ưu thứ tự giao hàng và tải trọng, mức tiêu thụ pin giảm trung bình **12.55%**, hạn chế đáng kể số lần UAV phải ghé trạm sạc.
- **Thời gian tính toán & Khả năng mở rộng:** Mặc dù thuật toán GA có thời gian tính toán lớn hơn Greedy, toàn bộ thời gian thực thi vẫn nằm trong ngưỡng vài giây (real-time planning), đáp ứng hoàn hảo yêu cầu vận hành đô thị thông minh.
