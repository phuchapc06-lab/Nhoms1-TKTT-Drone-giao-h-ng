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

### 8. Giao diện Thực thi Dòng lệnh Đa Năng (Main CLI Entrypoint)
- **File mã nguồn:** `src/main.py`
- **Nội dung thực hiện:**
  - Hỗ trợ đầy đủ các cờ CLI:
    - `--algorithm [ga|greedy]`: Chạy đơn lẻ từng thuật toán.
    - `--benchmark [10|50|100|path.json]`: Chọn kịch bản quy mô.
    - `--compare`: Chế độ chạy so sánh trực tiếp.
    - `--evaluate-all`: Chạy toàn bộ suite thực nghiệm đa quy mô và xuất báo cáo.
    - `--no-plot`, `--save-dir`, `--seed`.

---

### 9. Kiểm thử Tự động Toàn diện (Unit Testing & Validation)
- **Danh mục file test:**
  - `tests/test_member5.py`: Kiểm thử độc lập Fitness & Visualizer.
  - `tests/test_day2_pipeline.py`: Kiểm thử Pipeline tích hợp E2E & Validator.
  - `tests/test_day3_evaluator.py`: Kiểm thử BenchmarkEvaluator, Bar Charts, Scalability & xuất file báo cáo.
- **Kết quả kiểm thử:** **100% Passed**.

---

## 📂 DANH MỤC CÁC FILE ĐÃ TẠO VÀ ĐÓNG GÓP
| STT | Tên File | Chức năng | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | `src/algorithms/fitness.py` | Lập trình Hàm mục tiêu đa ràng buộc & Fitness function cho GA | Hoàn thành |
| 2 | `src/utils/visualizer.py` | Lập trình trực quan hóa bản đồ đa UAV, biểu đồ hội tụ, biểu đồ cột & scalability | Hoàn thành |
| 3 | `src/utils/validator.py` | Bộ kiểm định chuẩn Data Contract và tính hợp lệ của Solution | Hoàn thành |
| 4 | `src/pipeline.py` | Khung điều phối tích hợp hệ thống End-to-End và đối sánh thuật toán | Hoàn thành |
| 5 | `src/utils/benchmark_evaluator.py` | Module đo đạc chỉ số khoa học, đối sánh đa quy mô và xuất báo cáo | Hoàn thành |
| 6 | `src/utils/benchmark_generator.py` | Trình sinh các bộ dữ liệu thử nghiệm chuẩn 10, 50, 100 điểm vào `data/raw/` | Hoàn thành |
| 7 | `src/main.py` | Giao diện điều khiển chính của chương trình qua dòng lệnh CLI | Hoàn thành |
| 8 | `tests/test_member5.py` | Unit Test độc lập cho FitnessCalculator và UAVVisualizer | Passed 100% |
| 9 | `tests/test_day2_pipeline.py` | Unit Test tích hợp toàn diện cho Pipeline và Validator | Passed 100% |
| 10 | `tests/test_day3_evaluator.py` | Unit Test cho BenchmarkEvaluator và xuất báo cáo khoa học | Passed 100% |
| 11 | `docs/EXPERIMENT_RESULTS.md` | Báo cáo khoa học kết quả thực nghiệm đa quy mô | Hoàn thành |
| 12 | `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md` | Báo cáo chi tiết phần việc và minh chứng đóng góp cá nhân | Hoàn thành |
