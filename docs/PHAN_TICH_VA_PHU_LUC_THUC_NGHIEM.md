# BÁO CÁO CHUYÊN ĐỀ THÀNH VIÊN 4 (BENCHMARK DATA & EXPERIMENTAL LOGS)
> **Người thực hiện:** Nguyễn Gia Phong   
> **Công việc:** Bộ dữ liệu đa quy mô mở rộng (Time Windows đa dạng), phân tích mật độ khách hàng và phụ lục số liệu thực nghiệm tổng hợp.

---
## THIẾT KẾ MÔ HÌNH DỮ LIỆU ĐẦU VÀO

### 1. Xây dựng chuẩn dữ liệu đầu vào (Data Contract)
Để đảm bảo tính đồng bộ cho toàn bộ pipeline của hệ thống UDRP, bộ Benchmark được chuẩn hóa nghiêm ngặt dưới định dạng JSON với các thực thể cốt lõi:
- **Cấu hình bản đồ:** Lưới không gian đa chiều, số lượng UAV, số lượng trạm sạc bổ sung.
- **Tập hợp Nodes:** Bao gồm Trạm gốc (Depot - ID 0), khách hàng (Delivery - ID $1..N$) và trạm sạc (Charging). Mỗi node quản lý trực tiếp tọa độ `pos`, khối lượng hàng `demand` và khung giờ phục vụ `tw`.
- **Vùng cấm bay (No-Fly Zones):** Các khu vực hạn chế bay được định hình bằng tọa độ hộp giới hạn (Bounding Box).

### 2. Thuật toán sinh dữ liệu mô phỏng thực tế
Việc sinh tọa độ hoàn toàn ngẫu nhiên (Uniform Distribution) không phản ánh đúng đặc thù đô thị. Do đó, dữ liệu mô phỏng được thiết kế theo **Phân bố cụm (Gaussian Clustered Distribution)**:
- Thuật toán khởi tạo các tâm điểm cụm dân cư ngẫu nhiên trên bản đồ.
- Tọa độ khách hàng được phát sinh xoay quanh các tâm cụm này bằng hàm phân bố chuẩn (Gaussian) với độ lệch chuẩn $\sigma = 10$, mô phỏng chính xác hiện tượng đơn hàng tập trung dày đặc tại các khu chung cư và tháp văn phòng.
## PHÂN TÍCH ẢNH HƯỞNG CỦA MẬT ĐỘ KHÁCH HÀNG & TIME WINDOWS LÊN ĐỘ PHỨC TẠP THUẬT TOÁN

### 1. Tác động của quy mô và mật độ khách hàng ($N \in \{10, 50, 100, 500\}$)
Trên bản đồ đô thị kích thước cố định $100 \times 100\text{ km}^2$, khi số lượng khách hàng $N$ tăng từ $10$ lên $500$ điểm theo phân bố cụm (Clustered Gaussian Distribution), mật độ điểm giao hàng $\rho = \frac{N}{\text{Area}}$ tăng gấp $50$ lần. Sự gia tăng mật độ này tác động trực tiếp đến từng pha của hệ thống:

1.1 **Giai đoạn tiền xử lý ma trận khoảng cách $A^*$:**
   - Độ phức tạp tìm đường đơn cặp của $A^*$ với Min-Heap là $O(|V| \log |V| + |E|)$.
   - Tuy nhiên, số lượng cặp điểm $(i, j)$ cần tính toán giữa Depot, $N$ khách hàng và $M$ trạm sạc tăng theo bậc hai: $\frac{(N + M + 1)(N + M)}{2} = O((N + M)^2)$.
   - Khi $N = 500, M = 25$, tổng số cặp cần tra cứu lên tới $\approx 138.075$ cặp. Do đó, việc song song hóa bằng `ProcessPoolExecutor` và lưu trữ vào bảng tra cứu $O(1)$ là bắt buộc để tránh nghẽn cổ chai tính toán.

1.2 **Giai đoạn tối ưu hóa lộ trình với giải thuật di truyền (GA):**
   - Độ phức tạp thời gian của GA là $O(G \cdot P \cdot (N + K))$, trong đó $G$ là số thế hệ, $P$ là kích thước quần thể, $N$ là số khách hàng và $K$ là số lượng UAV.
   - Khi mật độ khách hàng trong một cụm tăng cao ($N = 100, 500$), khoảng cách Euclid giữa các điểm gần nhau giảm xuống, làm xuất hiện nhiều cực trị địa phương (local optima). Để GA hội tụ tốt ở quy mô $500$ điểm, chi phí đánh giá hàm Fitness trên mỗi thế hệ tăng tuyến tính theo $(N + K)$, khiến cơ chế tính Fitness song song (`multiprocessing.Pool`) phát huy hiệu quả rõ rệt nhất (Speedup đạt $2.42\times - 2.76\times$).

1.3 **Giai đoạn đối sánh với thuật toán tham lam (Greedy Baseline) và 2-Opt:**
   - Thuật toán Greedy có độ phức tạp $O(K \cdot N^2)$ và tìm kiếm cục bộ 2-Opt có độ phức tạp $O(I \cdot N^2)$.
   - Ở mật độ thấp ($N = 10$), Greedy chạy rất nhanh ($0.18\text{s}$) nhưng dễ chọn nhầm các điểm xa cụm ở cuối hành trình. Khi mật độ tăng lên $N = 500$, chi phí $O(N^2)$ của 2-Opt khiến thời gian chạy tăng vọt lên $68.50\text{s}$ nhưng chất lượng quãng đường vẫn kém hơn GA tới $23.6\%$ do tính chất tham lam cục bộ.

### 2. Tác động của khung thời gian giao hàng (Time Windows: Tight vs. Relaxed)
- **Khung giờ chặt chẽ (`tight`, độ rộng $25 - 50$ phút):** buộc UAV phải di chuyển liên tục giữa các cụm xa nhau để kịp giờ thay vì gom đơn theo vị trí địa lý gần nhất. Điều này làm tăng tổng quãng đường bay, tăng mức tiêu hao năng lượng và kích hoạt hàm chèn trạm sạc `repair_route_with_charging` thường xuyên hơn.
- **Khung giờ nới lỏng (`relaxed`, độ rộng $120 - 250$ phút):** Cho phép thuật toán GA tối ưu hóa thứ tự thăm điểm thuần túy theo khoảng cách không gian và né vùng cấm bay (NFZ), giúp giảm số lần sạc pin và nâng tỷ lệ giao hàng đúng giờ (On-time Delivery Rate) lên mức $86.8\% - 100\%$.

---

## NỘI DUNG BÁO CÁO TỔNG KẾT & PHỤ LỤC SỐ LIỆU THỰC NGHIỆM

### 1. Thiết kế bộ dữ liệu chuẩn (Benchmark Dataset Design)
Hệ thống dữ liệu thực nghiệm được xây dựng tại `src/utils/benchmark_generator.py` và xuất ra định dạng chuẩn JSON trong `data/raw/` với các đặc tả:
- **Không gian bản đồ:** Lưới đô thị $100 \times 100\text{ km}^2$, Trạm gốc (Depot) đặt tại tâm $(50, 50)$.
- **Phân bố khách hàng:** Phân bố theo các tâm cụm dân cư (Clustered Gaussian với $\sigma = 10$), trọng lượng gói hàng ngẫu nhiên trong khoảng $[1.0, 5.0]\text{ kg}$.
- **Ràng buộc thực tế:** Tích hợp từ $2$ đến $25$ trạm sạc (Charging Stations) và từ $2$ đến $10$ vùng cấm bay hình chữ nhật (No-Fly Zones) không chồng lấn lên Depot.

### 2. Bảng tổng hợp số liệu thực nghiệm đa quy mô (`benchmark_comparison_results.csv`)

| Quy mô ($N$) | Chế độ TW | Thuật toán | Tổng quãng đường (km) | Tổng năng lượng (Wh) | Thời gian chạy (s) | Tỷ lệ đúng giờ (%) | Hệ số tăng tốc (Speedup) |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **10** | Mixed | $A^* + \text{Greedy}$ (Baseline) | 218.45 | 342.10 | 0.18 | 80.0% | $1.00\times$ |
| **10** | Mixed | $A^* + \text{GA}$ (Parallel) | **176.20** | **275.40** | 0.65 | **100.0%** | **$1.85\times$** |
| **50** | Mixed | $A^* + \text{Greedy}$ (Baseline) | 845.60 | 1320.50 | 1.42 | 72.0% | $1.00\times$ |
| **50** | Mixed | $A^* + \text{GA}$ (Parallel) | **672.15** | **1048.80** | 3.85 | **94.0%** | **$2.15\times$** |
| **100** | Mixed | $A^* + \text{Greedy}$ (Baseline) | 1590.30 | 2485.20 | 4.90 | 65.0% | $1.00\times$ |
| **100** | Mixed | $A^* + \text{GA}$ (Parallel) | **1245.80** | **1942.60** | 9.40 | **91.0%** | **$2.42\times$** |
| **500** | Mixed | $A^* + \text{Greedy}$ (Baseline) | 6820.50 | 10640.00 | 68.50 | 54.4% | $1.00\times$ |
| **500** | Mixed | $A^* + \text{GA}$ (Parallel) | **5210.40** | **8128.20** | 84.20 | **86.8%** | **$2.76\times$** |

**Nhận xét thực nghiệm cốt lõi:**
- Giải thuật đề xuất ($A^* + \text{GA}$) giúp tiết kiệm trung bình **$20.5\% - 23.6\%$ quãng đường và năng lượng tiêu thụ** so với Baseline ($A^* + \text{Greedy}$) trên mọi quy mô.
- Tỷ lệ giao hàng đúng giờ (On-time Delivery Rate) của GA duy trì ở mức cao (**$86.8\% - 100\%$**), vượt trội hoàn toàn so với Greedy (**$54.4\% - 80.0\%$**) khi mật độ đơn hàng có khung giờ hẹp tăng lên.
- Cơ chế song song hóa giúp đạt hệ số tăng tốc $S_p$ từ **$1.85\times$ đến $2.76\times$**, vượt mục tiêu nghiệm thu đề ra ($S_p \ge 1.8\times$).

---

