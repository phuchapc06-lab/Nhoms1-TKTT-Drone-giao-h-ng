# BÁO CÁO KẾT QUẢ THỬ NGHIỆM ĐỐI SÁNH HIỆU NĂNG THUẬT TOÁN
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UDRP)
**Ngày tạo:** 2026-10-22 20:12:57
**Phụ trách thực nghiệm:** Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

### 1. Bảng số liệu tổng hợp đa quy mô (Multi-scale Experimental Results)

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Đúng giờ Greedy (%) | Đúng giờ GA (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 10 | 3 | 377.25 | 296.41 | **21.43%** | **12.21%** | 80.0% | 100.0% | **17.95%** | 0.0020 | 0.5271 |
| 20 | 6 | 517.00 | 448.03 | **13.34%** | **9.78%** | 95.0% | 95.0% | **10.90%** | 0.0008 | 1.5227 |
| 30 | 9 | 695.47 | 635.83 | **8.58%** | **7.88%** | 93.3% | 96.7% | **8.39%** | 0.0024 | 3.7503 |

### 2. Nhận xét & Đánh giá Khoa học
- **Mức độ tối ưu quãng đường:** Giải thuật Di truyền đề xuất ($A^* + GA$) giúp rút ngắn trung bình **14.45%** quãng đường bay so với Baseline Tham lam ($A^* + Greedy$).
- **Hiệu quả sử dụng năng lượng pin:** Nhờ tối ưu thứ tự giao hàng và tải trọng, mức tiêu thụ pin giảm trung bình **9.96%**, hạn chế đáng kể số lần UAV phải ghé trạm sạc.
- **Tỷ lệ giao hàng đúng giờ (Time Windows):** Thuật toán GA đạt tỷ lệ giao đúng hẹn trung bình **97.2%**, giảm thiểu các khoản phạt vi phạm khung giờ giao hàng của khách hàng.
- **Thời gian tính toán & Khả năng mở rộng:** Mặc dù thuật toán GA có thời gian tính toán lớn hơn Greedy, toàn bộ thời gian thực thi vẫn nằm trong ngưỡng vài giây (real-time planning), đáp ứng hoàn hảo yêu cầu vận hành đô thị thông minh.

### 3. Chỉ số TV3: Năng lượng chi tiết từng chặng bay và thời gian sạc trạm

- **Mức tiết kiệm năng lượng của GA so với Greedy:** **12.21%** (Greedy = **446.04 Wh**, GA = **391.56 Wh**).
- **Khả năng pin an toàn:** Greedy có **0** tuyến không an toàn, GA có **0** tuyến không an toàn; do đó **100% các chuyến bay đều đáp ứng điều kiện pin an toàn** trên dữ liệu thực nghiệm hiện tại.
- **Greedy:** tổng năng lượng = **446.04 Wh**, số lần sạc = **3**, tổng thời gian sạc = **22.30 phút**.
- **GA:** tổng năng lượng = **391.56 Wh**, số lần sạc = **2**, tổng thời gian sạc = **19.58 phút**.
- **Ví dụ chi tiết chặng bay (GA):** 0->8: 41.2km, 4.6kg, 69.9Wh; 8->5: 17.0km, 4.0kg, 27.2Wh; 5->2: 20.9km, 2.7kg, 29.2Wh.
- **Ví dụ chi tiết chặng bay (Greedy):** 0->7: 10.0km, 5.0kg, 17.5Wh; 7->1: 21.2km, 4.0kg, 34.1Wh; 1->4: 20.4km, 3.2kg, 30.1Wh.
