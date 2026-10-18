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
  - `validate_benchmark_data()`: Tự động kiểm tra cấu trúc dữ liệu JSON đầu vào (kích thước grid, tọa độ no-fly zones, tính hợp lệ của Depot 0, loại node, demand, time window).
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
- **Class chính:** `BenchmarkGenerator`
- **Nội dung thực hiện:**
  - Sinh và lưu sẵn 3 bộ dữ liệu chuẩn trong thư mục `data/raw/`:
    - `benchmark_10.json`: 10 điểm giao hàng, 3 trạm sạc, 5 vùng cấm bay.
    - `benchmark_50.json`: 50 điểm giao hàng, 6 trạm sạc, 12 vùng cấm bay.
    - `benchmark_100.json`: 100 điểm giao hàng, 10 trạm sạc, 20 vùng cấm bay.

---

### 9. Giao diện Thực thi Dòng lệnh Đa Năng (Main CLI Entrypoint)
- **File mã nguồn:** `src/main.py`
- **Nội dung thực hiện:**
  - Hỗ trợ đầy đủ các cờ CLI:
    - `--algorithm [ga|greedy]`: Chạy đơn lẻ từng thuật toán.
    - `--benchmark [10|50|100|path.json]`: Chọn kịch bản quy mô.
    - `--compare`: Chế độ chạy so sánh trực tiếp.
    - `--evaluate-all`: Chạy toàn bộ suite thực nghiệm đa quy mô và xuất báo cáo.
    - `--no-plot`, `--save-dir`, `--seed`.

---

### 10. Cột mốc Tích hợp Hệ thống Toàn diện Ngày 4 (Full System Integration Milestone)
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

### 11. Cột mốc Tối ưu & Tinh chỉnh Nâng cao Ngày 5 (Advanced GA Tuning & Dynamic Scaling)
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

### 12. Cột mốc Nghiệm thu Toàn dự án & Tổng kết Sprint 1 Tuần (Chủ Nhật - 18/10/2026)
- **Files liên quan:**
  - `README.md` (Tài liệu tổng quan dự án toàn diện, kiến trúc hệ thống, hướng dẫn chạy CLI)
  - `TIEN_DO.md` (Báo cáo tiến độ hoàn thành 100% Sprint 1 tuần của nhóm)
  - `docs/EXPERIMENT_RESULTS.md` (Báo cáo thực nghiệm đối sánh đa quy mô hoàn chỉnh)
  - `data/raw/benchmark_500.json` (Bộ dữ liệu quy mô siêu lớn 500 khách hàng)
  - `src/utils/benchmark_evaluator.py` (Mở rộng đánh giá tự động đa quy mô, tích hợp sửa đường bay trạm sạc & tối ưu 2-Opt)
  - Review & Merge hoàn tất đóng góp từ nhánh `origin/feature/tv1-contribution`
- **Nội dung thực hiện:**
  - **Nghiệm thu thực nghiệm đối sánh đa quy mô tự động (Multi-scale Benchmark Consolidation):**
    - Hoàn thiện và chạy nghiệm thu chuỗi kịch bản đánh giá quy mô đa dạng: 10, 20, 30, 50, 100 và mở rộng 500 điểm (`python src/main.py --evaluate-all`).
    - Nâng cấp `benchmark_evaluator.py` để quy trình đối sánh chạy liên hoàn với đầy đủ cơ chế tối ưu cục bộ 2-Opt và tự động chèn trạm sạc bảo vệ pin cho cả GA và Greedy Router.
    - Cập nhật tự động bảng tổng hợp chỉ số định lượng `data/processed/benchmark_comparison_results.csv`, biểu đồ trực quan hóa so sánh cột `docs/figures/comparison_bars.png` và biểu đồ phân tích khả năng mở rộng `docs/figures/scalability_analysis.png`.
  - **Hợp nhất mã nguồn và đồng bộ đóng góp toàn nhóm:**
    - Rà soát và fast-forward merge thành công nhánh `feature/tv1-contribution` (tài liệu `TV1_CONTRIBUTION.md`, chuẩn hóa docstrings toán tử di truyền GA và vá siêu tham số `ga_tuning.py`).
    - Đồng bộ bộ dữ liệu kịch bản siêu lớn 500 điểm `data/raw/benchmark_500.json` từ nhánh `feature/tv4-benchmark-data` vào hệ thống, đảm bảo tuân thủ 100% Data Contract của dự án.
  - **Đại tu và hoàn thiện tài liệu dự án chuẩn mực (`README.md`):**
    - Viết lại toàn bộ `README.md` theo chuẩn tài liệu nghiên cứu chuyên nghiệp: Sơ đồ kiến trúc luồng dữ liệu (Mermaid Flowchart), bảng phân công trách nhiệm 6 thành viên, cơ sở lý thuyết toán học (Haversine + NFZ A*, GA Chromosome + OX + Swap, Energy Non-linear + Charging Repair, 2-Opt Local Search), bảng kết quả thực nghiệm tổng hợp và hướng dẫn chi tiết toàn bộ các cờ lệnh CLI.
  - **Đóng gói và bảo đảm chất lượng tổng thể (Quality Assurance & Audit):**
    - Kiểm thử tự động hồi quy 7/7 test suites độc lập, xác nhận toàn bộ hệ sinh thái phần mềm hoạt động trơn tru 100% không phát sinh lỗi.
    - Đóng gói nghiệm thu toàn bộ Sprint 1 Tuần, đồng bộ toàn diện trên 3 nhánh `nguyen-phuc-ha`, `develop`, và `main`.

---

### 13. Kiểm thử Tự động Toàn diện (Unit Testing & Validation)
- **Danh mục 7 file test độc lập:**
  - `tests/test_distance_matrix.py`: Kiểm thử A* tối ưu, tính đối xứng và MD5 Cache (TV2).
  - `tests/test_ga.py`: Kiểm thử GA Core, toán tử OX, Swap, Tuning và Seeding (TV1).
  - `tests/test_member5.py`: Kiểm thử độc lập Fitness & Visualizer (TV5).
  - `tests/test_day2_pipeline.py`: Kiểm thử Pipeline tích hợp E2E & Validator (TV5).
  - `tests/test_day3_evaluator.py`: Kiểm thử BenchmarkEvaluator, Bar Charts & Scalability (TV5).
  - `tests/test_day4_integration.py`: Kiểm thử Cột mốc tích hợp Hệ thống Ngày 4 (TV5).
  - `tests/test_day5_integration.py`: Kiểm thử Cột mốc Tinh chỉnh & Tối ưu Nâng cao Ngày 5 (TV5).
- **Kết quả kiểm thử:** **100% Passed**.

---

## 📂 DANH MỤC CÁC FILE ĐÃ TẠO VÀ ĐÓNG GÓP
| STT | Tên File | Chức năng | Trạng thái |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `src/algorithms/fitness.py` | Lập trình Hàm mục tiêu đa ràng buộc & Fitness function cho GA | Hoàn thành |
| 2 | `src/utils/visualizer.py` | Lập trình trực quan hóa bản đồ đa UAV, biểu đồ hội tụ, biểu đồ cột & scalability | Hoàn thành |
| 3 | `src/utils/validator.py` | Bộ kiểm định chuẩn Data Contract và tính hợp lệ của Solution | Hoàn thành |
| 4 | `src/pipeline.py` | Khung điều phối tích hợp hệ thống End-to-End, Hybrid GA & đối sánh | Hoàn thành |
| 5 | `src/utils/benchmark_evaluator.py` | Module đo đạc chỉ số khoa học, đối sánh đa quy mô và xuất báo cáo | Hoàn thành |
| 6 | `src/utils/benchmark_generator.py` | Trình sinh các bộ dữ liệu thử nghiệm chuẩn 10, 50, 100 điểm vào `data/raw/` | Hoàn thành |
| 7 | `src/main.py` | Giao diện điều khiển chính của chương trình qua CLI, tự động tính số Drone | Hoàn thành |
| 8 | `src/algorithms/energy_manager.py` | Module quản lý pin, tiêu hao tải trọng và tự động chèn trạm sạc | Hoàn thành |
| 9 | `src/algorithms/local_search.py` | Module tối ưu cục bộ 2-Opt gỡ giao cắt đường bay đa UAV | Hoàn thành |
| 10 | `src/algorithms/baseline_greedy.py` | Module thuật toán tham lam Nearest Neighbor định tuyến đối sánh | Hoàn thành |
| 11 | `tests/test_member5.py` | Unit Test độc lập cho FitnessCalculator và UAVVisualizer | Passed 100% |
| 12 | `tests/test_day2_pipeline.py` | Unit Test tích hợp toàn diện cho Pipeline và Validator | Passed 100% |
| 13 | `tests/test_day3_evaluator.py` | Unit Test cho BenchmarkEvaluator và xuất báo cáo khoa học | Passed 100% |
| 14 | `tests/test_day4_integration.py` | Unit Test kiểm thử Cột mốc Tích hợp Hệ thống Ngày 4 | Passed 100% |
| 15 | `tests/test_day5_integration.py` | Unit Test kiểm thử Cột mốc Tối ưu & Tinh chỉnh Nâng cao Ngày 5 | Passed 100% |
| 16 | `README.md` | Tài liệu dự án hoàn chỉnh, kiến trúc, phân công nhóm, kết quả thực nghiệm | Hoàn thành |
| 17 | `TIEN_DO.md` | Tài liệu quản lý tiến độ và nghiệm thu toàn dự án Sprint 1 tuần | Hoàn thành |
| 18 | `docs/EXPERIMENT_RESULTS.md` | Báo cáo khoa học kết quả thực nghiệm đối sánh đa quy mô | Hoàn thành |
| 19 | `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md` | Báo cáo chi tiết phần việc và minh chứng đóng góp cá nhân | Hoàn thành |

