# TIẾN ĐỘ THỰC HIỆN ĐỀ TÀI: UAV DELIVERY ROUTING PROBLEM (UDRP)
## Nhóm 1 - Môn Phân tích & Thiết kế Thuật toán

---

## 🎯 Tổng quan Tiến độ Sprint 1 Tuần (7 Ngày)
- **Mục tiêu:** Xây dựng hệ thống hoàn chỉnh giải bài toán Định tuyến Đội bay UAV giao hàng trong đô thị né vùng cấm bay, quản lý pin và tối ưu hóa đa mục tiêu.
- **Trạng thái:** Đã hoàn thành các nhiệm vụ tính đến Thứ Sáu (23/10/2026).

---

## 📅 Tiến độ Chi tiết Từng Ngày

### Ngày 1 (Thứ Hai - 12/10/2026)
- **Thành viên 5 (Tech Lead):** Hoàn thành cài đặt Hàm thích nghi đa mục tiêu (`FitnessCalculator`), trực quan hóa bản đồ đa Drone (`UAVVisualizer`) và đồ thị hội tụ GA. Viết bộ kiểm thử độc lập `test_member5.py` đạt 100% Passed.

### Ngày 2 (Thứ Ba - 13/10/2026)
- **Thành viên 5 (Tech Lead):** Xây dựng khung điều phối tích hợp toàn trình `pipeline.py` (E2E), xây dựng bộ kiểm định chuẩn `DataContractValidator`, nâng cấp `main.py` hỗ trợ dòng lệnh và viết bộ test `test_day2_pipeline.py` đạt 100% Passed.

### Ngày 3 (Thứ Tư - 14/10/2026)
- **Thành viên 5 (Tech Lead):** Phát triển bộ đánh giá đa quy mô `BenchmarkEvaluator`, sinh dữ liệu chuẩn hóa, xuất báo cáo `EXPERIMENT_RESULTS.md`, biểu đồ so sánh cột và Scalability. Viết bộ kiểm thử `test_day3_evaluator.py` đạt 100% Passed.

### Ngày 4 (Thứ Năm - 15/10/2026)
- **Thành viên 5 (Tech Lead):** Tích hợp toàn diện 4 module của các thành viên vào Pipeline:
  - Tích hợp `EnergyManager` (TV3): Tiêu hao phi tuyến theo tải trọng & tự động chèn trạm sạc.
  - Tích hợp `local_search.py` (TV6): Thuật toán 2-Opt gỡ giao cắt đường bay.
  - Tích hợp `baseline_greedy.py` (TV6): Thuật toán tham lam đối chuẩn.
  - Viết bộ kiểm thử `test_day4_integration.py` đạt 100% Passed.

### Ngày 5 (Thứ Sáu - 16/10/2026)
- **Thành viên 5 (Tech Lead):** Đánh giá & duyệt PR #7 của TV1, cài đặt cơ chế Hybrid GA (Greedy Seeding), cơ chế tự động mở rộng đội bay thích ứng theo tải trọng trên các quy mô 50 và 100 điểm. Viết bộ kiểm thử `test_day5_integration.py` đạt 100% Passed.

---

## 🏆 Cột mốc Nghiệm thu Toàn dự án & Tổng kết Sprint 1 Tuần (Chủ Nhật - 18/10/2026)
- **Tỷ lệ hoàn thành khối lượng công việc Toàn dự án:** **100% Hoàn thành xuất sắc** (Đạt chuẩn nghiên cứu khoa học và sẵn sàng bảo vệ).
- **Các thành quả nghiệm thu chính trong Ngày Chủ nhật:**
  1. **Thực nghiệm Đối sánh Đa quy mô Toàn diện:** Đã thực thi chuỗi kịch bản đa quy mô (N = 10, 20, 30, 50, 100, 500 điểm), thu thập số liệu chi tiết và cập nhật báo cáo khoa học `docs/EXPERIMENT_RESULTS.md` cùng file CSV `data/processed/benchmark_comparison_results.csv`.
  2. **Bộ biểu đồ Nghiên cứu Khoa học:** Xuất tự động biểu đồ cột so sánh hiệu năng (`comparison_bars.png`) và đồ thị phân tích khả năng mở rộng quy mô (`scalability_analysis.png`).
  3. **Hợp nhất & Kiểm định Mã nguồn:** Tech Lead đã rà soát và merge toàn bộ các nhánh tính năng và báo cáo của các thành viên vào nhánh `develop` và `main`.
  4. **Tài liệu Hướng dẫn Chính thức:** Cập nhật hoàn chỉnh file `README.md` với kiến trúc 3 tầng, hướng dẫn chạy lệnh và kết quả thực nghiệm.
  5. **Hệ thống Kiểm thử Hồi quy:** Chuẩn hóa toàn bộ các bài Unit Test và Integration Test độc lập bao quát đầy đủ 6 thành viên, chạy tự động qua `python src/main.py --test` và `python tests/run_all_tests.py` đạt kết quả **100% Passed**.
  6. **Tự động hóa CI/CD:** Thiết lập workflow GitHub Actions `.github/workflows/python-tests.yml` tự động kiểm thử trên Python 3.10, 3.11, 3.12.
  7. **Sẵn sàng cho Tuần làm việc Mới:** Toàn bộ mã nguồn, dữ liệu, tài liệu và test đã hoàn thiện 100% sạch sẽ và đồng bộ!

---

## 📅 TIẾN ĐỘ TUẦN 5 & TUẦN 6 (Cập nhật đến Thứ Sáu - 23/10/2026)

### Ngày 1: Thứ Tư (21/10/2026) - Thiết kế Song song hóa & Đo lường Tỷ lệ Giao hàng Đúng giờ
- **Thành viên 5 (Tech Lead - Nguyễn Phúc Hà):**
  - **Nâng cấp `FitnessCalculator` (`src/algorithms/fitness.py`):**
    - Cài đặt cơ chế kiểm tra và tính toán **Tỷ lệ giao hàng đúng giờ (On-time Delivery Rate, %)** dựa trên khung giờ của khách hàng ($t_{arrival} \le \text{end\_tw}$).
    - Bổ sung hàm tiện ích `calculate_ontime_rate()` và phân tích chi tiết số đơn đúng giờ / trễ giờ trong trường `breakdown`.
  - **Song song hóa tính toán ma trận khoảng cách (`src/utils/distance_matrix.py`):**
    - Hỗ trợ tính toán song song đa luồng (`ThreadPoolExecutor`) khi tính các cặp điểm $(i, j)$ né vùng cấm bay A*.
    - Cài đặt hàm `benchmark_distance_matrix_speedup()` để đo thời gian tính toán và hệ số tăng tốc $S_p = T_1 / T_p$.
  - **Tích hợp Pipeline & CLI (`src/pipeline.py`, `src/main.py`):**
    - Tích hợp cờ `--parallel`, `--workers` và `--speedup` vào dòng lệnh CLI.
    - Cập nhật hàm `compare_algorithms()` hiển thị cột chỉ số Tỷ lệ đúng giờ (On-time Rate).
    - Cập nhật `BenchmarkEvaluator` xuất chỉ số `greedy_ontime_rate` và `ga_ontime_rate`.
  - **Bộ Kiểm thử Độc lập:**
    - Xây dựng bộ test mới `tests/test_day1_parallel_ontime.py` kiểm thử toàn diện 4 chức năng mới (100% Passed).
    - Nâng cấp Master Test Runner `tests/run_all_tests.py` lên **11/11 Suites Passed (100%)**.

### Ngày 2: Thứ Năm (22/10/2026) - Chạy Thực nghiệm Đối sánh Đa quy mô & Đo đạc Hiệu năng
- **Thành viên 5 (Tech Lead - Nguyễn Phúc Hà):**
  - **Nâng cấp `BenchmarkEvaluator` & `UAVVisualizer`:**
    - Bổ sung hàm `run_speedup_benchmark()` đo đạc thực nghiệm hệ số tăng tốc $S_p = T_1 / T_p$ và hiệu suất song song $E_p = S_p / p$ trên các tập benchmark quy mô lớn.
    - Cài đặt phương thức `plot_speedup_analysis()` trong `UAVVisualizer` xuất tự động biểu đồ khoa học `docs/figures/speedup_analysis.png`.
  - **Thực thi Đo đạc Thực nghiệm Đa quy mô Toàn diện:**
    - Điều phối chạy bộ thử nghiệm trên chuỗi quy mô $N = [10, 20, 30, 50]$ điểm giao hàng.
    - Cập nhật tự động báo cáo nghiên cứu khoa học `docs/EXPERIMENT_RESULTS.md` với đầy đủ 4 chỉ số cốt lõi: Quãng đường (Distance), Tiêu thụ Pin (Energy), Tỷ lệ giao đúng giờ (On-time Delivery Rate: đạt **97.4%**), Thời gian tính toán (Execution Time) và Bảng đo Speedup song song.
    - Xuất dữ liệu bảng chuẩn xác ra file CSV: `data/processed/benchmark_comparison_results.csv`.
    - Xuất bộ 3 biểu đồ nghiên cứu khoa học độ phân giải cao: `comparison_bars.png`, `scalability_analysis.png`, `speedup_analysis.png`.
  - **Bộ Kiểm thử Độc lập Ngày 2:**
    - Xây dựng bộ kiểm thử mới `tests/test_day2_benchmark_speedup.py` bao quát 4 bài test độc lập (100% Passed).
    - Nâng cấp Master Test Runner `tests/run_all_tests.py` lên **12/12 Suites Passed (100%)**.

### Ngày 3: Thứ Sáu (23/10/2026) - Phân tích Độ phức tạp Thuật toán & Chứng minh Tính đúng đắn
- **Thành viên 5 (Tech Lead - Nguyễn Phúc Hà):**
  - **Tổng hợp Báo cáo Toán học Chuyên sâu (`docs/COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md`):**
    - Phân tích chi tiết độ phức tạp thời gian và không gian cho 5 module: A* Pathfinding $O(WH \log(WH))$, GA Meta-heuristic $O(G \cdot P \cdot (N+K))$, Greedy Baseline $O(K \cdot N^2)$, 2-Opt Local Search $O(I \cdot N^2)$, Energy Manager $O(N \cdot C)$, và toàn trình Pipeline tích hợp.
    - Chứng minh toán học nghiêm ngặt 5 định lý cốt lõi:
      1. *Định lý 1:* Tính tối ưu toàn cục và nhất quán của hàm Heuristic Octile trong thuật toán A*.
      2. *Định lý 2:* Tính bất biến bảo toàn lời giải hợp lệ của toán tử Order Crossover (OX) và Swap Mutation trong GA.
      3. *Định lý 3:* Tính đơn điệu không tăng quãng đường và tính dừng hữu hạn bước của 2-Opt ($d_{new} \le d_{old}$).
      4. *Định lý 4:* Tính dừng không lặp vô hạn và tính an toàn pin tuyệt đối ($E_{battery} \ge 15\%$) của Energy Manager.
      5. *Định lý 5:* Tính không suy giảm nghiệm của cơ chế Hybrid GA Seeding ($Cost_{GA} \le Cost_{Greedy}$).
    - Đối chiếu thực nghiệm: Đo đạc thời gian chạy đa quy mô khẳng định tính phù hợp tuyệt đối giữa thực tế và lý thuyết Big-$O$.
  - **Bộ Kiểm thử Độc lập Ngày 3:**
    - Xây dựng bộ kiểm thử mới `tests/test_day3_complexity_correctness.py` kiểm chứng toàn diện 5 định lý toán học (100% Passed).
    - Nâng cấp Master Test Runner `tests/run_all_tests.py` lên **13/13 Suites Passed (100%)**.

---

## 📋 Chuẩn Giao kèo dữ liệu (Data Contract)

```python
# 1. Cấu trúc một điểm (Node)
nodes = {
    0: {"id": 0, "type": "depot",    "pos": (x, y), "demand": 0.0, "tw": (0, 1000), "service_time": 0},
    1: {"id": 1, "type": "delivery", "pos": (x, y), "demand": 2.0, "tw": (5, 60),   "service_time": 5},
    # id 0: Depot, 1..N: Khách hàng, N+1..: Trạm sạc ("charging")
}

# 2. Ma trận khoảng cách (NumPy 2D)
dist_matrix[i][j] # Khoảng cách thực tế đã né các vùng cấm bay No-fly zones

# 3. Lời giải tuyến đường (Solution)
solution = [
    [0, 1, 4, 0],      # Lộ trình Drone 1 (Bắt đầu và kết thúc tại Depot 0)
    [0, 2, 5, 3, 0]    # Lộ trình Drone 2
]
```

---

## 📂 Danh mục tài liệu báo cáo có sẵn trong `docs/`
1. `docs/EXPERIMENT_RESULTS.md`: Báo cáo kết quả thử nghiệm đối sánh khoa học đa quy mô.
2. `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md`: Báo cáo minh chứng đóng góp chi tiết của Nhóm trưởng.
3. `docs/TV1_CONTRIBUTION.md`: Báo cáo minh chứng đóng góp chi tiết của Thành viên 1.
4. `docs/GA_TUNING_RESULTS.md`: Báo cáo kết quả quét siêu tham số tối ưu giải thuật di truyền.
5. `docs/KE_HOACH_PHAN_CONG_NHOM_6_NGUOI.txt`: Bảng phân công chi tiết công việc cho 6 thành viên.
6. `docs/Mathematical_Model.md`: Mô hình hóa toán học chính thức (Objective & Constraints).
7. `docs/figures/`: Thư mục lưu toàn bộ ảnh bản đồ đường bay và biểu đồ nghiên cứu.
