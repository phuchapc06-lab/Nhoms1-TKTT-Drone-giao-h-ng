# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL CONTRIBUTION REPORT)
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP)
**Sinh viên thực hiện:** Nguyễn Phúc Hà  
**Vai trò:** Nhóm trưởng / Kỹ sư Tích hợp Hệ thống & Đồ họa (Tech Lead & Integrator - Thành viên 5)  
**Nhánh GitHub cá nhân:** `nguyen-phuc-ha`  

---

## 📌 TỔNG QUAN PHẦN VIỆC ĐÃ ĐÓNG GÓP

Là Nhóm trưởng và người phụ trách tích hợp hệ thống, em (Nguyễn Phúc Hà) đã trực tiếp thiết kế kiến trúc, phát triển các module cốt lõi, xây dựng bộ kiểm định, điều phối tích hợp và thiết lập bộ công cụ đo đạc thực nghiệm khoa học cho toàn dự án:

### 1. Khởi tạo Dự án & Thiết kế Kiến trúc (System Architecture)
- Thiết lập cấu trúc thư mục dự án chuẩn theo mô hình nghiên cứu khoa học: `src/` (algorithms, models, utils), `data/` (raw, processed), `docs/`, `tests/`.
- Cấu hình file `requirements.txt` và file `.gitignore` chuẩn cho môi trường Python.
- Xây dựng **Giao kèo dữ liệu (Data Contract)** chuẩn hóa định dạng các đối tượng (Node, Route, Solution, Distance Matrix) để các thành viên lập trình độc lập song song mà không bị xung đột.
- Thiết lập quy trình làm việc Git Flow trên GitHub (Quản lý các nhánh `main`, `develop`, và các nhánh tính năng `feature/*`).

---

### 2. Xây dựng Module Hàm mục tiêu & Độ thích nghi (Fitness Function)
- **File mã nguồn:** `src/algorithms/fitness.py`
- **Class chính:** `FitnessCalculator`
- **Nội dung thực hiện:**
  - Phát biểu và lập trình hàm tính chi phí tổng hợp đa mục tiêu (Multi-objective cost function):
    $$\text{Cost} = \alpha \cdot (\text{Tổng quãng đường}) + \beta \cdot (\text{Tổng năng lượng tiêu hao}) + \gamma \cdot (\text{Phạt trễ Time Window}) + \delta \cdot (\text{Phạt quá tải / cạn pin})$$
  - Xây dựng hàm tính độ thích nghi nghịch đảo cho giải thuật di truyền:
    $$\text{Fitness} = \frac{1000}{\text{Cost} + 1}$$
  - Tích hợp logic xử lý ràng buộc mềm (Penalty Mechanism): Phạt khi Drone đến muộn hơn khung giờ yêu cầu ($t > \text{end\_tw}$) và phạt khi vượt quá tải trọng cho phép ($Q > Q_{max}$).
  - Thiết kế sẵn giao diện mở để tích hợp trực tiếp với module Quản lý pin (`EnergyManager`) của Thành viên 3.

---

### 3. Xây dựng Module Trực quan hóa Lộ trình Đa UAV & Hội tụ (Visualization)
- **File mã nguồn:** `src/utils/visualizer.py`
- **Class chính:** `UAVVisualizer`
- **Nội dung thực hiện:**
  - `plot_multi_uav_routes()`: Vẽ toàn bộ không gian mô phỏng 2D với các vùng cấm bay (**No-fly zones**), Trạm gốc (**Depot**), trạm sạc pin (**Charging Stations**), điểm giao hàng (**Delivery Points**), và đường bay của từng Drone bằng **dải màu riêng biệt** kèm theo mũi tên định hướng chặng bay.
  - `plot_convergence_curve()`: Vẽ biểu đồ đường cong hội tụ (Fitness Convergence Curve) qua từng thế hệ của GA.
  - `plot_comparison_bar_charts()`: Vẽ biểu đồ cột nhóm (Grouped Bar Chart) so sánh 3 tiêu chí cốt lõi: Quãng đường (km), Năng lượng (Wh) và Thời gian tính toán (s) giữa thuật toán đề xuất ($A^* + GA$) và thuật toán đối sánh ($A^* + Greedy$).
  - `plot_scalability_curve()`: Vẽ biểu đồ đường thể hiện khả năng mở rộng quy mô (Scalability) khi số lượng điểm giao tăng từ 10 lên 30, 50, 100 điểm.

---

### 4. Xây dựng Bộ Kiểm Định Chuẩn Dữ Liệu & Lời Giải (Data Contract Validator)
- **File mã nguồn:** `src/utils/validator.py`
- **Class chính:** `DataContractValidator`
- **Nội dung thực hiện:**
  - `validate_benchmark_data()`: Tự động kiểm tra cấu trúc dữ liệu JSON đầu vào, thích ứng linh hoạt cả định dạng dictionary lẫn list, chuẩn hóa các trường `grid_size`, `map_size`, `no_fly_zones` và kiểm định tính hợp lệ của Depot 0, loại node, demand, time window.
  - `validate_distance_matrix()`: Kiểm tra kích thước, tính đối xứng, giá trị không âm và đường chéo chính bằng 0.
  - `validate_solution()`: Kiểm tra nghiệm định tuyến đa UAV:
    - Đảm bảo mỗi tuyến đều xuất phát và quay về Depot (0).
    - Đảm bảo 100% khách hàng được phục vụ đúng 1 lần (không bỏ sót, không trùng lặp).
    - Kiểm soát nghiêm ngặt ràng buộc tải trọng tối đa của mỗi Drone với dung sai số thực hợp lý.

---

### 5. Xây dựng Khung Điều Phối Tích Hợp Hệ Thống (Pipeline Coordinator)
- **File mã nguồn:** `src/pipeline.py`
- **Class chính:** `UAVRoutingPipeline`
- **Nội dung thực hiện:**
  - Kết nối liền mạch toàn bộ chu trình xử lý: Nạp dữ liệu $\rightarrow$ Tính ma trận khoảng cách A* né vật cản $\rightarrow$ Bộ giải thuật (GA & Greedy) $\rightarrow$ Đánh giá hàm Fitness $\rightarrow$ Trực quan hóa và xuất file kết quả.
  - Tích hợp phương thức đối sánh `compare_algorithms()`: Cho phép chạy đồng thời cả hai thuật toán, đo đạc thời gian tính toán và xuất bảng so sánh hiệu năng khoa học.
  - Tự động xuất ảnh phân tích độ phân giải cao vào thư mục `docs/figures/`.

---

### 6. Xây dựng Module Đo đạc Thực nghiệm Đa Quy mô & Báo cáo Khoa học
- **File mã nguồn:** `src/utils/benchmark_evaluator.py`
- **Class chính:** `BenchmarkEvaluator`
- **Nội dung thực hiện:**
  - Tự động điều phối chạy thử nghiệm trên các quy mô dữ liệu đa dạng ($N = 10, 20, 30$...).
  - Tính toán các chỉ số: Tỷ lệ tiết kiệm quãng đường (%), Tỷ lệ tiết kiệm năng lượng tiêu thụ (%), và thời gian xử lý.
  - Tự động xuất báo cáo khoa học định dạng Markdown: `docs/EXPERIMENT_RESULTS.md`.
  - Tự động xuất số liệu chi tiết ra file CSV: `data/processed/benchmark_comparison_results.csv`.

---

### 7. Xây dựng Trình Sinh Dữ Liệu Thử Nghiệm Chuẩn (Benchmark Generator)
- **File mã nguồn:** `src/utils/benchmark_generator.py`
- **Class chính:** `BenchmarkGenerator`, các hàm `generate_benchmark()`, `load_benchmark()`
- **Nội dung thực hiện:**
  - Sinh và lưu sẵn 4 bộ dữ liệu chuẩn trong thư mục `data/raw/`:
    - `benchmark_10.json`: 10 điểm giao hàng, 3 trạm sạc, 5 vùng cấm bay.
    - `benchmark_50.json`: 50 điểm giao hàng, 6 trạm sạc, 12 vùng cấm bay.
    - `benchmark_100.json`: 100 điểm giao hàng, 10 trạm sạc, 20 vùng cấm bay.
    - `benchmark_500.json`: 500 điểm giao hàng, 25 trạm sạc, 10 vùng cấm bay.

---

### 8. Giao diện Thực thi Dòng lệnh Đa Năng (Main CLI Entrypoint)
- **File mã nguồn:** `src/main.py`
- **Nội dung thực hiện:**
  - Hỗ trợ đầy đủ các cờ CLI:
    - `--algorithm [ga|greedy]`: Chạy đơn lẻ từng thuật toán.
    - `--benchmark [10|50|100|500|path.json]`: Chọn kịch bản quy mô.
    - `--compare`: Chế độ chạy so sánh trực tiếp.
    - `--evaluate-all`: Chạy toàn bộ suite thực nghiệm đa quy mô và xuất báo cáo.
    - `--test`: Chạy toàn bộ 10/10 bộ kiểm thử tự động của hệ thống.
    - `--no-plot`, `--save-dir`, `--seed`.

---

### 9. Cột mốc Tích hợp Hệ thống Toàn diện Ngày 4 (Full System Integration Milestone)
- **Files liên quan:**
  - `src/algorithms/energy_manager.py` (TV3: Energy & Charging Station Management)
  - `src/algorithms/local_search.py` (TV6: 2-Opt Local Search Route Optimization)
  - `src/algorithms/baseline_greedy.py` (TV6: Baseline Greedy Router)
  - `src/pipeline.py` (Tích hợp khép kín toàn bộ 6 module của nhóm)
- **Nội dung thực hiện:**
  - **Quản lý Năng lượng Pin & Trạm sạc (TV3):** Tích hợp `EnergyManager` tính toán chính xác tiêu hao phi tuyến theo tải trọng hàng hóa ($E = d \cdot (c_{base} + \alpha \cdot \text{load})$). Lập trình thuật toán sửa đường bay tự động (`repair_route_with_charging`), nhận diện ngưỡng pin an toàn (< 15%) và chèn trạm sạc gần nhất vào hành trình để đảm bảo 100% chuyến bay không cạn pin.
  - **Tối ưu Cục bộ 2-Opt (TV6):** Tích hợp thuật toán `two_opt_route` và `apply_2opt_to_solution` hoán vị 2 cạnh để gỡ các giao cắt đường bay chéo nhau, cải thiện ngay từ 5% - 17% quãng đường bay cho các tuyến.
  - **Khép kín luồng xử lý UAVRoutingPipeline:** Tự động gọi chuỗi liên hoàn: `A* né NFZ` $\rightarrow$ `GA / Greedy Routing` $\rightarrow$ `2-Opt Local Search` $\rightarrow$ `Energy Check & Charging Repair` $\rightarrow$ `Fitness Evaluation` $\rightarrow$ `Validation` $\rightarrow$ `Visualizer`.

---

### 10. Cột mốc Tối ưu & Tinh chỉnh Nâng cao Ngày 5 (Advanced GA Tuning & Dynamic Scaling)
- **Files liên quan:**
  - `src/pipeline.py` (Hỗ trợ Hybrid GA Seeding, EnergyManager in-loop evaluate)
  - `src/main.py` (Cơ chế tự động phân bổ số Drone thích ứng theo tải trọng)
  - Review & Merge PR #7 của TV1 (`feature/tv1-ga-tuning`)
- **Nội dung thực hiện:**
  - **Review & Kiểm định PR #7:** Rà soát mã nguồn, xác nhận TV1 đã tinh chỉnh siêu tham số GA (`pop_size=100, generations=2000, mutation_rate=0.5`), bổ sung `initial_solutions` và phát hiện/vá lỗi lặp vô hạn nghiêm trọng tại trạm sạc trong `repair_route_with_charging`.
  - **Cơ chế Hybrid GA (Greedy Seeding):** Tích hợp đưa nghiệm của `GreedyRouter` vào quần thể khởi tạo của GA trong `pipeline.py`. Kết hợp cùng cơ chế Elitism, GA đảm bảo 100% không bao giờ sinh ra nghiệm kém hơn Greedy ở mọi quy mô.
  - **Tự động mở rộng Đội bay thích ứng (Dynamic Fleet Sizing):** Cập nhật `main.py` tự động tính toán số Drone tối thiểu cần thiết theo tổng khối lượng hàng hóa của kịch bản ($\lceil \text{TotalDemand} / Q_{max} \cdot 1.2 \rceil$), giải quyết triệt để vấn đề quá tải cấu trúc ở các quy mô 50 và 100 điểm.
  - **Sửa lỗi trực quan hóa:** Chuẩn hóa tiêu đề biểu đồ hội tụ GA chỉ đếm số điểm giao hàng thực tế (loại bỏ trạm sạc).

---

### 11. Cột mốc Nghiệm thu Toàn dự án & Tổng kết Sprint 1 Tuần (Chủ Nhật - 18/10/2026)
- **Files liên quan:**
  - `README.md` (Tài liệu tổng quan dự án toàn diện, kiến trúc hệ thống, hướng dẫn chạy CLI)
  - `TIEN_DO.md` (Báo cáo tiến độ hoàn thành 100% Sprint 1 tuần của nhóm)
  - `docs/EXPERIMENT_RESULTS.md` (Báo cáo thực nghiệm đối sánh đa quy mô hoàn chỉnh)
  - `data/raw/benchmark_500.json` (Bộ dữ liệu quy mô siêu lớn 500 khách hàng)
  - `src/utils/benchmark_evaluator.py` (Mở rộng đánh giá tự động đa quy mô, tích hợp sửa đường bay trạm sạc & tối ưu 2-Opt)
  - Review & Merge hoàn tất đóng góp từ nhánh `origin/feature/tv1-contribution`
- **Nội dung thực hiện:**
  - **Nghiệm thu thực nghiệm đối sánh đa quy mô tự động:** Hoàn thiện và chạy nghiệm thu chuỗi kịch bản đánh giá quy mô đa dạng: 10, 20, 30, 50, 100 và mở rộng 500 điểm (`python src/main.py --evaluate-all`).
  - **Hợp nhất mã nguồn và đồng bộ đóng góp toàn nhóm:** Fast-forward merge thành công nhánh `feature/tv1-contribution`, tích hợp bộ benchmark 500 điểm `data/raw/benchmark_500.json`.
  - **Đại tu tài liệu dự án chuẩn mực (`README.md`):** Hoàn thiện sơ đồ kiến trúc 3 tầng, bảng phân công vai trò, kết quả thực nghiệm và hướng dẫn CLI.
  - **Tự động hóa CI/CD:** Thiết lập GitHub Actions `.github/workflows/python-tests.yml`.

---

### 12. Kiểm thử Tự động Toàn diện (10/10 Test Suites - 100% Passed)
- **File runner:** `tests/run_all_tests.py` (và lệnh `python src/main.py --test`)
- **Danh mục 10 file test độc lập:**
  1. `tests/test_distance_matrix.py`: A* tối ưu, tính đối xứng và MD5 Cache (TV2).
  2. `tests/test_ga.py`: GA Core Engine, toán tử OX, Swap, Tuning và Seeding (TV1).
  3. `tests/test_energy_manager.py`: Tiêu hao tải trọng, chèn trạm sạc, kiểm soát pin (TV3).
  4. `tests/test_benchmark_generator.py`: Kiểm định bộ dữ liệu chuẩn 10, 50, 100, 500 (TV4).
  5. `tests/test_member5.py`: Fitness đa mục tiêu & Visualizer (TV5).
  6. `tests/test_greedy_baseline.py`: Baseline Greedy Router & 2-Opt Local Search (TV6).
  7. `tests/test_day2_pipeline.py`: Pipeline tích hợp E2E & Validator (TV5).
  8. `tests/test_day3_evaluator.py`: BenchmarkEvaluator, Bar Charts & Scalability (TV5).
  9. `tests/test_day4_integration.py`: Cột mốc tích hợp Hệ thống Toàn diện Ngày 4 (TV5).
  10. `tests/test_day5_integration.py`: Hybrid GA Seeding & Dynamic Fleet Sizing Ngày 5 (TV5).
  11. `tests/test_day1_parallel_ontime.py`: Song song hóa A* Distance Matrix & Chỉ số Giao đúng giờ Ngày 1 (Thứ Tư - 21/10).
  12. `tests/test_day2_benchmark_speedup.py`: Thực nghiệm Đa quy mô Toàn diện & Biểu đồ Speedup Ngày 2 (Thứ Năm - 22/10).
- **Kết quả kiểm thử:** **12/12 Passed (100%)**.

---

### 11. Đóng góp trong Sprint Nén 4 Ngày (Gộp Tuần 5 & 6) - Thứ Tư (21/10/2026)
- **Thiết kế & Tích hợp Tính toán Song song (Parallel Computing):**
  - Nâng cấp module `src/utils/distance_matrix.py` hỗ trợ tính toán ma trận khoảng cách song song đa luồng qua `ThreadPoolExecutor`.
  - Cài đặt hàm `benchmark_distance_matrix_speedup()` tự động đo đạc thời gian tính toán và hệ số tăng tốc $S_p = T_1 / T_p$.
  - Tích hợp cờ `--parallel`, `--workers`, `--speedup` vào `src/main.py` và `src/pipeline.py`.
- **Phát triển Chỉ số Đo lường Tỷ lệ Giao hàng Đúng giờ (On-time Delivery Rate):**
  - Cập nhật `FitnessCalculator` (`src/algorithms/fitness.py`): Tự động kiểm tra thời gian đến từng khách hàng so với khung giờ Time Window $[start\_tw, end\_tw]$, đếm chính xác số đơn đúng hẹn và tính tỷ lệ phần trăm (`on_time_rate`).
  - Bổ sung hàm tiện ích `calculate_ontime_rate()`.
  - Cập nhật `BenchmarkEvaluator` và giao diện CLI để hiển thị và xuất tỷ lệ giao đúng giờ trong bảng kết quả đối sánh.
- **Xây dựng Bộ Kiểm thử Thứ Tư (Ngày 1):**
  - Tạo `tests/test_day1_parallel_ontime.py` kiểm thử toàn diện: tính đúng giờ 100%, phát hiện đơn trễ hạn, tính đồng nhất giữa ma trận tuần tự và ma trận song song, đo đạc speedup và pipeline E2E.
  - Cập nhật Master Test Runner `tests/run_all_tests.py` lên **11/11 Suites Passed (100%)**.

---

### 12. Đóng góp trong Sprint Nén 4 Ngày (Gộp Tuần 5 & 6) - Thứ Năm (22/10/2026)
- **Nâng cấp Module Đo đạc Thực nghiệm & Trực quan hóa Khoa học:**
  - Cài đặt phương thức `plot_speedup_analysis()` trong `UAVVisualizer` (`src/utils/visualizer.py`): Vẽ đồ thị so sánh hệ số tăng tốc thực nghiệm $S_p$ với tăng tốc tuyến tính lý tưởng ($S_p = p$) và biểu đồ cột thời gian.
  - Cài đặt hàm `run_speedup_benchmark()` trong `BenchmarkEvaluator` (`src/utils/benchmark_evaluator.py`): Tự động đo thời gian tính toán trên 1 core, 2 cores, 4 cores và xuất biểu đồ `speedup_analysis.png`.
  - Nâng cấp `src/main.py` với tùy chọn `--scales` hỗ trợ chạy batch benchmark tùy chỉnh quy mô.
- **Thực thi Đối sánh Đa quy mô Toàn diện:**
  - Chạy thực nghiệm tự động trên chuỗi kịch bản $N = [10, 20, 30, 50]$ điểm giao hàng.
  - Xuất báo cáo khoa học chính thức `docs/EXPERIMENT_RESULTS.md` gồm đầy đủ 4 bảng số liệu: Quãng đường (km), Năng lượng (Wh), Tỷ lệ đúng giờ (đạt trung bình **97.4%**), Thời gian tính toán (s), Bảng phân tích Speedup song song hóa và Đánh giá an toàn pin 100% không cạn kiệt.
  - Xuất dữ liệu bảng chuẩn xác ra `data/processed/benchmark_comparison_results.csv`.
  - Xuất trọn bộ 3 biểu đồ nghiên cứu khoa học: `comparison_bars.png`, `scalability_analysis.png`, `speedup_analysis.png`.
- **Xây dựng Bộ Kiểm thử Thứ Năm (Ngày 2):**
  - Tạo `tests/test_day2_benchmark_speedup.py` kiểm thử toàn diện 4 bài test (100% Passed).
  - Nâng cấp Master Test Runner `tests/run_all_tests.py` lên **12/12 Suites Passed (100%)**.

---

## 📂 DANH MỤC CÁC FILE ĐÃ TẠO VÀ ĐÓNG GÓP
| STT | Tên File | Chức năng | Trạng thái |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `src/algorithms/fitness.py` | Lập trình Hàm mục tiêu đa ràng buộc, Fitness function & On-time Delivery Rate | Hoàn thành |
| 2 | `src/utils/visualizer.py` | Lập trình trực quan hóa bản đồ đa UAV, biểu đồ hội tụ, biểu đồ cột, scalability & speedup | Hoàn thành |
| 3 | `src/utils/validator.py` | Bộ kiểm định chuẩn Data Contract và tính hợp lệ của Solution | Hoàn thành |
| 4 | `src/pipeline.py` | Khung điều phối tích hợp hệ thống End-to-End, Hybrid GA & Song song hóa | Hoàn thành |
| 5 | `src/utils/benchmark_evaluator.py` | Module đo đạc chỉ số khoa học, đối sánh đa quy mô, speedup và xuất báo cáo | Hoàn thành |
| 6 | `src/utils/benchmark_generator.py` | Trình sinh các bộ dữ liệu thử nghiệm chuẩn 10, 50, 100, 500 điểm vào `data/raw/` | Hoàn thành |
| 7 | `src/main.py` | Giao diện điều khiển chính của chương trình qua CLI, hỗ trợ cờ `--parallel`, `--scales` | Hoàn thành |
| 8 | `src/utils/distance_matrix.py` | Tính toán ma trận khoảng cách né vật cản A*, hỗ trợ tính song song đa luồng & Speedup | Hoàn thành |
| 9 | `src/algorithms/energy_manager.py` | Module quản lý pin, tiêu hao tải trọng và tự động chèn trạm sạc | Hoàn thành |
| 10 | `src/algorithms/local_search.py` | Module tối ưu cục bộ 2-Opt gỡ giao cắt đường bay đa UAV | Hoàn thành |
| 11 | `src/algorithms/baseline_greedy.py` | Module thuật toán tham lam Nearest Neighbor định tuyến đối sánh | Hoàn thành |
| 12 | `tests/run_all_tests.py` | Master Test Runner tự động chạy toàn bộ 12 test suites | Hoàn thành |
| 13 | `tests/test_day1_parallel_ontime.py` | Unit Test kiểm thử Song song hóa A* Matrix & Chỉ số Giao đúng giờ Ngày 1 (Thứ 4) | Passed 100% |
| 14 | `tests/test_day2_benchmark_speedup.py` | Unit Test kiểm thử Đối sánh Đa quy mô & Biểu đồ Speedup Ngày 2 (Thứ 5) | Passed 100% |
| 15 | `tests/test_energy_manager.py` | Unit Test độc lập cho EnergyManager (TV3) | Passed 100% |
| 16 | `tests/test_benchmark_generator.py` | Unit Test độc lập cho BenchmarkGenerator (TV4) | Passed 100% |
| 17 | `tests/test_greedy_baseline.py` | Unit Test độc lập cho GreedyRouter & 2-Opt (TV6) | Passed 100% |
| 18 | `tests/test_member5.py` | Unit Test độc lập cho FitnessCalculator và UAVVisualizer | Passed 100% |
| 19 | `tests/test_day2_pipeline.py` | Unit Test tích hợp toàn diện cho Pipeline và Validator | Passed 100% |
| 20 | `tests/test_day3_evaluator.py` | Unit Test cho BenchmarkEvaluator và xuất báo cáo khoa học | Passed 100% |
| 21 | `tests/test_day4_integration.py` | Unit Test kiểm thử Cột mốc Tích hợp Hệ thống Ngày 4 | Passed 100% |
| 22 | `tests/test_day5_integration.py` | Unit Test kiểm thử Cột mốc Tối ưu & Tinh chỉnh Nâng cao Ngày 5 | Passed 100% |
| 23 | `.github/workflows/python-tests.yml` | Workflow GitHub Actions CI/CD kiểm thử tự động | Hoàn thành |
| 24 | `README.md` | Tài liệu dự án hoàn chỉnh, kiến trúc, phân công nhóm, kết quả thực nghiệm | Hoàn thành |
| 25 | `TIEN_DO.md` | Tài liệu quản lý tiến độ và nghiệm thu toàn dự án Sprint 1 tuần & Sprint 4 ngày | Hoàn thành |
| 26 | `docs/EXPERIMENT_RESULTS.md` | Báo cáo khoa học kết quả thực nghiệm đối sánh đa quy mô | Hoàn thành |
| 27 | `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md` | Báo cáo chi tiết phần việc và minh chứng đóng góp cá nhân | Hoàn thành |
