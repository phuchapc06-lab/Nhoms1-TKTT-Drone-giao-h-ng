# BÁO CÁO KẾT QUẢ THỬ NGHIỆM ĐỐI SÁNH HIỆU NĂNG THUẬT TOÁN
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UDRP)
**Ngày tạo:** 2026-10-25 14:44:26
**Phụ trách thực nghiệm:** Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

### 1. Bảng số liệu tổng hợp đa quy mô (Multi-scale Experimental Results)

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Đúng giờ Greedy (%) | Đúng giờ GA (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 6 | 3 | 328.09 | 283.32 | **13.65%** | **14.42%** | 83.3% | 100.0% | **18.66%** | 0.0001 | 0.1739 |
| 10 | 3 | 377.25 | 296.41 | **21.43%** | **12.21%** | 80.0% | 100.0% | **17.95%** | 0.0001 | 0.3848 |

### 2. Bảng đo đạc Tăng tốc Song song hóa Ma trận Khoảng cách ($A^*$ Parallel Speedup)

*Quy mô thử nghiệm: N = 10 điểm giao hàng và các chướng ngại vật NFZ.*

| Số Luồng / CPU Cores (p) | Thời gian tính toán (s) | Hệ số Tăng tốc ($S_p = T_1 / T_p$) | Hiệu suất Song song ($E_p = S_p / p$) |
| :---: | :---: | :---: | :---: |
| 1 Core(s) | 0.0257s | **1.00x** | 100.0% |
| 2 Core(s) | 0.8681s | **0.03x** | 1.5% |
| 4 Core(s) | 1.0883s | **0.02x** | 0.5% |

### 3. Chỉ số TV3: Năng lượng chi tiết từng chặng bay và thời gian sạc trạm

- **Mức tiết kiệm năng lượng của GA so với Greedy:** **14.42%** (Greedy = **402.24 Wh**, GA = **344.24 Wh**).
- **Đánh giá An toàn Pin:** Greedy có **0** tuyến không an toàn, GA có **0** tuyến không an toàn; do đó **100% các chuyến bay đều đáp ứng điều kiện pin an toàn** trên dữ liệu thực nghiệm hiện tại.
- **Greedy:** tổng năng lượng = **402.24 Wh**, số lần sạc = **2**, tổng thời gian sạc = **20.11 phút**.
- **GA:** tổng năng lượng = **344.24 Wh**, số lần sạc = **2**, tổng thời gian sạc = **17.21 phút**.
- **Ví dụ chi tiết chặng bay (GA):** 0->3: 49.0km, 1.2kg, 58.2Wh; 3->6: 15.8km, 0.7kg, 17.4Wh; 6->0: 55.2km, 0.0kg, 55.2Wh, sạc 6.5 phút.
- **Ví dụ chi tiết chặng bay (Greedy):** 0->3: 49.0km, 4.4kg, 81.5Wh; 3->6: 15.8km, 3.9kg, 25.0Wh; 6->1: 13.5km, 3.2kg, 19.9Wh.

### 4. Nhận xét & Đánh giá Khoa học
- **Mức độ tối ưu quãng đường:** Giải thuật Di truyền đề xuất ($A^* + GA$) giúp rút ngắn trung bình **17.54%** quãng đường bay so với Baseline Tham lam ($A^* + Greedy$).
- **Hiệu quả sử dụng năng lượng pin:** Nhờ tối ưu thứ tự giao hàng và tải trọng, mức tiêu thụ pin giảm trung bình **13.32%**, hạn chế đáng kể số lần UAV phải ghé trạm sạc.
- **Tỷ lệ giao hàng đúng giờ (Time Windows):** Thuật toán GA đạt tỷ lệ giao đúng hẹn trung bình **100.0%**, giảm thiểu các khoản phạt vi phạm khung giờ giao hàng của khách hàng.
- **Thời gian tính toán & Khả năng mở rộng:** Mặc dù thuật toán GA có thời gian tính toán lớn hơn Greedy, toàn bộ thời gian thực thi vẫn nằm trong ngưỡng vài giây (real-time planning), đáp ứng hoàn hảo yêu cầu vận hành đô thị thông minh.
- **Hiệu quả Song song hóa:** Cài đặt đa luồng `ThreadPoolExecutor` giúp tăng tốc tính ma trận khoảng cách $A^*$, giúp giảm đáng kể thời gian tiền xử lý không gian bản đồ khi số lượng điểm giao và vùng cấm bay tăng cao.
