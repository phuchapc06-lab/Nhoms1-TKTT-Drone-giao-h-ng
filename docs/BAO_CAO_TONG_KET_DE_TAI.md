# BÁO CÁO TỔNG KẾT ĐỀ TÀI
## HỆ THỐNG TỐI ƯU HÓA ĐỊNH TUYẾN ĐỘI BAY UAV GIAO HÀNG ĐÔ THỊ (UDRP)

> **Môn học:** Phân tích & Thiết kế Thuật toán — Trường Đại học Kinh tế Quốc dân (NEU)  
> **Nhóm thực hiện:** Nhóm 1  
> **Phụ trách Kỹ thuật & Tích hợp (Tech Lead):** Nguyễn Phúc Hà (Thành viên 5)  
> **Thời gian thực hiện:** Tháng 10/2026  

---

## 1. TỔNG QUAN ĐỀ TÀI

Dự án giải quyết bài toán định tuyến đa phương tiện bay không người lái (**UAV Delivery Routing Problem - UDRP**) trong môi trường đô thị thông minh. Mục tiêu là lập lộ trình bay phục vụ tập khách hàng sao cho tổng chi phí là nhỏ nhất, đồng thời thỏa mãn các ràng buộc thực tế:

1. **Vật cản không gian:** Bay vòng an toàn qua các Vùng cấm bay (No-Fly Zones - NFZ).
2. **Năng lượng pin hữu hạn:** Dung lượng pin giới hạn, tự động ghé trạm sạc khi mức pin xuống dưới ngưỡng an toàn (15%).
3. **Tiêu hao năng lượng phi tuyến:** Điện năng tiêu hao tính theo cả quãng đường và khối lượng hàng chuyên chở.
4. **Tải trọng giới hạn:** Mỗi drone chở tối đa tải trọng quy định ($Q_{max} = 5.0\text{ kg}$).
5. **Khung giờ giao hàng (Time Windows):** Giao hàng đúng khung giờ hẹn của khách hàng, phạt chi phí nếu giao trễ.

---

## 2. KIẾN TRÚC VÀ CÁC THÀNH PHẦN HỆ THỐNG

Hệ thống được tổ chức theo mô hình module hóa rõ ràng, phân chia trách nhiệm cho các thành viên:

```
[Dữ liệu & Kiểm chuẩn]
  ├── BenchmarkGenerator (TV4)    : Tạo dữ liệu điểm giao, vùng cấm bay, trạm sạc, khung giờ
  └── DataContractValidator (TV5) : Kiểm tra định dạng dữ liệu đầu vào và tính hợp lệ của lộ trình

[Thuật toán cốt lõi]
  ├── A* Pathfinding (TV2)         : Tìm đường ngắn nhất né vùng cấm bay (Heuristic Octile)
  ├── Parallel Distance Matrix     : Tính ma trận khoảng cách song song đa tiến trình (TV2 & TV5)
  ├── Genetic Algorithm (TV1)      : Thuật toán di truyền tối ưu hóa phân cụm và thứ tự giao hàng
  ├── Greedy Router (TV6)          : Thuật toán tham lam láng giềng gần nhất làm chuẩn đối sánh
  ├── 2-Opt Local Search (TV6)     : Tối ưu cục bộ gỡ giao cắt đường bay
  └── EnergyManager (TV3)          : Mô hình pin phi tuyến và thuật toán tự động chèn trạm sạc

[Tích hợp & Đánh giá (TV5)]
  ├── FitnessCalculator (TV5)      : Hàm mục tiêu đa tiêu chí và tính tỷ lệ giao hàng đúng giờ
  ├── Pipeline Điều phối (TV5)     : Kết nối toàn trình E2E từ dữ liệu đến kết quả
  ├── BenchmarkEvaluator (TV5)     : Đo đạc thực nghiệm đối sánh, tính tăng tốc và xuất báo cáo
  └── UAVVisualizer (TV5)          : Trực quan hóa bản đồ bay 2D, đồ thị hội tụ và các biểu đồ so sánh
```

---

## 3. KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH

Thực nghiệm được tiến hành đối sánh giữa giải thuật đề xuất ($A^* + GA$) và thuật toán chuẩn đối sánh ($A^* + Greedy$) trên các quy mô khác nhau:

| Quy mô ($N$) | Đội bay ($K$) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Tỷ lệ Đúng giờ Greedy (%) | Tỷ lệ Đúng giờ GA (%) | Tiết kiệm Chi phí (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$N = 6$** | 3 | 328.09 | 283.32 | **13.65%** | **14.42%** | 83.3% | **100.0%** | **18.66%** |
| **$N = 10$** | 3 | 377.25 | 289.53 | **23.25%** | **16.90%** | 80.0% | **100.0%** | **21.50%** |
| **$N = 20$** | 6 | 518.70 | 453.61 | **12.55%** | **8.02%** | 95.0% | **100.0%** | **10.83%** |
| **$N = 30$** | 9 | 696.97 | 618.21 | **11.30%** | **9.73%** | 96.7% | **100.0%** | **10.81%** |
| **$N = 50$** | 15 | 1469.54 | 1423.89 | **3.11%** | **3.28%** | 96.0% | **96.0%** | **3.84%** |

*Nguồn số liệu: `BenchmarkEvaluator.evaluate_scale` (`src/utils/benchmark_evaluator.py`, seed 42, số Drone $K = \max(3, \lceil N / 3.5 \rceil)$), chạy ngày 26/10 với EnergyManager sau commit `faea2f0` (depot được dùng làm điểm sạc) và 2-Opt có kiểm tra chi phí (chỉ giữ bước đảo không làm tăng chi phí tuyến), lưu tại `data/processed/benchmark_comparison_results.csv`.*

### Nhận xét:
- Về quãng đường và năng lượng, giải thuật di truyền GA giúp tiết kiệm trung bình **12.8%** quãng đường, **10.5%** điện năng tiêu thụ và **13.1%** tổng chi phí so với thuật toán Greedy trên 5 quy mô. Mức chênh lệch nhỏ dần ở quy mô lớn (chi phí tiết kiệm 18.7% - 21.5% ở $N \le 10$, khoảng 10.8% ở $N = 20, 30$, còn **3.8%** ở $N = 50$), vì cấu hình đo cho GA số thế hệ tăng chậm ($\max(120, 8N)$, tức 400 thế hệ ở $N = 50$) trong khi bài toán lớn cần nhiều thế hệ hơn để hội tụ.
- Về thời gian giao hàng, GA kiểm soát tốt khung giờ nhờ hàm phạt trong FitnessCalculator, duy trì tỷ lệ đúng giờ **96% - 100%**, bằng hoặc cao hơn Greedy (80% - 96.7%) ở mọi quy mô.
- Ở cả 5 quy mô, không lộ trình nào của hai phương pháp bị cạn pin (0 tuyến không an toàn theo `BenchmarkEvaluator.check_route_battery_safety`, kiểm tra mức pin không âm trên từng chặng). Khi chặng kế tiếp làm pin xuống dưới ngưỡng 15%, EnergyManager tự chèn trạm sạc hoặc cho Drone ghé depot để sạc.
- **Quy mô lớn (benchmark 100 và 500 điểm, `docs/GA_TUNING_RESULTS.md` mục 13; GA 2000 thế hệ, 100 cá thể):** GA rẻ hơn Greedy 9.1% ở 100 điểm; ở 500 điểm GA đắt hơn 7.7% nhưng lời giải Greedy có 1 (100 điểm) và 6 (500 điểm) Drone cạn pin giữa đường nên bị validator đánh dấu **không hợp lệ**, còn mọi lời giải GA đều hợp lệ.

---

## 4. KẾT QUẢ ĐO ĐẠC TĂNG TỐC SONG SONG HÓA

Việc tính toán ma trận khoảng cách $A^*$ trên bản đồ có vùng cấm bay là tác vụ nặng về CPU. Hệ thống hỗ trợ chạy đa tiến trình (`ProcessPoolExecutor`) để tận dụng tối đa các nhân CPU:

| Số luồng / Cores ($p$) | Thời gian tính toán ($T_p$) | Hệ số Tăng tốc ($S_p = T_1 / T_p$) | Hiệu suất Song song ($E_p = S_p / p$) |
| :---: | :---: | :---: | :---: |
| **$p = 1$ (Tuần tự)** | 0.452 s | **1.00x** | 100.0% |
| **$p = 2$** | 0.284 s | **1.59x** | 79.5% |
| **$p = 4$** | 0.232 s | **1.95x** | 48.8% |

---

## 5. TỔNG KẾT ĐỘ PHỨC TẠP THUẬT TOÁN & CHỨNG MINH TOÁN HỌC

Báo cáo chi tiết về độ phức tạp và chứng minh toán học được lưu tại [`docs/COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md`](COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md). Tóm tắt như sau:

### 5.1. Độ phức tạp Asymptotic (Thời gian & Không gian)
- **$A^*$ Pathfinding:** Thời gian $O(W \cdot H \log(W \cdot H))$, Bộ nhớ $O(W \cdot H)$.
- **Ma trận Khoảng cách Song song:** Thời gian $O\left(\frac{M^2}{p} \cdot W \cdot H \log(W \cdot H)\right)$, Bộ nhớ $O(W \cdot H + M^2)$.
- **Giải thuật Di truyền GA:** với chromosome dài $L = N + K - 1$, thời gian $O(G \cdot P \cdot (L + \log P))$ khi không có EnergyManager và $O(G \cdot P \cdot (L \cdot C + \log P))$ khi chấm điểm có chèn trạm sạc (cấu hình của pipeline); bản song song chia phần đánh giá cho $p$ tiến trình. Bộ nhớ $O(P \cdot L)$.
- **Greedy Baseline:** Thời gian $O(K \cdot N^2)$, Bộ nhớ $O(N+K)$.
- **2-Opt Local Search:** Thời gian $O(I \cdot N^2)$, Bộ nhớ $O(N)$.
- **Energy Manager:** Thời gian $O(N \cdot C)$, Bộ nhớ $O(N+C)$.

### 5.2. Các định lý toán học đã được chứng minh:
1. **Định lý 1:** Tính tối ưu toàn cục và tính nhất quán (Consistency) của hàm Heuristic Octile trong thuật toán $A^*$.
2. **Định lý 2:** Tính bất biến bảo toàn tính hợp lệ của toán tử Order Crossover (OX) và Swap Mutation trong GA (mỗi khách hàng được phục vụ đúng 1 lần).
3. **Định lý 3:** Tính đơn điệu không tăng quãng đường và tính dừng hữu hạn bước của thuật toán tối ưu cục bộ 2-Opt ($d_{new} \le d_{old}$). Quãng đường không tăng nhưng tổng chi phí có thể tăng, nên pipeline chỉ giữ bước đảo không làm tăng chi phí tuyến.
4. **Định lý 4:** Tính dừng của thuật toán tự động chèn trạm sạc (Depot cũng là điểm sạc) và tính an toàn pin có điều kiện: với tuyến được đánh dấu khả thi, pin khi tới điểm giao $\ge 15\%$, khi tới điểm sạc $\ge 0$. Tuyến không sửa được bị đánh dấu thiếu pin và bị validator loại nếu cạn pin.
5. **Định lý 5:** Tính không suy giảm nghiệm của cơ chế Hybrid GA Seeding kết hợp Elitism theo thước đo chọn lọc của GA ($\text{Cost}_\lambda(S_{GA}) \le \text{Cost}_\lambda(S_{Greedy})$, $\lambda$ là hệ số nhân phạt); khi lời giải Greedy không vi phạm ràng buộc thì $\text{Cost}_{GA} \le \text{Cost}_{Greedy}$ (Greedy trước 2-Opt).

---

## 6. DANH MỤC BIỂU ĐỒ KHOA HỌC (LƯU TẠI `docs/figures/`)

1. `comparison_bars.png`: Biểu đồ cột so sánh quãng đường, năng lượng và thời gian giữa GA và Greedy.
2. `scalability_analysis.png`: Đồ thị phân tích khả năng mở rộng khi tăng số lượng khách hàng.
3. `speedup_analysis.png`: Đồ thị hệ số tăng tốc thực nghiệm so với đường lý tưởng khi tính toán song song.
4. `ontime_rate_comparison.png`: Biểu đồ đối sánh tỷ lệ giao hàng đúng giờ theo khung thời gian.
5. `route_ga.png` & `route_greedy.png`: Bản đồ trực quan hóa đường bay 2D né vùng cấm bay (NFZ) của các thuật toán.
6. `convergence_ga.png`: Đồ thị đường cong hội tụ giá trị hàm mục tiêu của GA qua các thế hệ.

---

## 7. HƯỚNG DẪN CHẠY THỬ NGHIỆM VÀ KIỂM THỬ

### 7.1. Chạy thuật toán chính qua giao diện dòng lệnh (CLI):
```bash
# Chạy thuật toán GA trên bộ benchmark 10 điểm:
python src/main.py --algo ga --benchmark 10

# Chạy thuật toán Greedy đối sánh:
python src/main.py --algo greedy --benchmark 10

# Bật chế độ tính toán song song với 4 luồng:
python src/main.py --algo ga --benchmark 10 --parallel --workers 4

# Chạy thử nghiệm đối sánh đa quy mô tự động:
python src/main.py --evaluate-all
```

### 7.2. Chạy toàn bộ hệ thống kiểm thử:
```bash
# Cách 1: Chạy qua lệnh test của main.py
python src/main.py --test

# Cách 2: Chạy trực tiếp qua Master Test Runner
python tests/run_all_tests.py
```
Toàn bộ các bộ kiểm thử đều đã được chuẩn hóa và vượt qua kiểm tra tự động trên Python 3.10, 3.11 và 3.12.
