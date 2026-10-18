# THEO DÕI TIẾN ĐỘ DỰ ÁN (TIEN_DO.md)

Đồ án môn Phân tích & Thiết kế Thuật toán (NEU) — **UAV Delivery Routing Problem (UDRP)**:  
Tối ưu hóa định tuyến đội bay đa Drone giao hàng đô thị thông minh, né vùng cấm bay ($A^*$), kiểm soát tải trọng, năng lượng pin, khung giờ giao hàng (Time Windows), tối ưu bằng Genetic Algorithm (GA) và so sánh với Baseline Greedy + 2-Opt.

---

## 📌 Lệnh thực thi & Kiểm thử thường dùng

Chạy từ thư mục gốc của dự án:
```bash
# 1. Chạy demo đối sánh trực quan (bật bản đồ & in bảng so sánh hiệu năng)
python src/main.py --compare

# 2. Chạy riêng giải thuật Di truyền GA (10 điểm giao hàng)
python src/main.py --algorithm ga --benchmark 10

# 3. Chạy kiểm thử tự động đo đạc đa quy mô (10, 20, 30 điểm) và xuất báo cáo khoa học
python src/main.py --evaluate-all

# 4. Chạy toàn bộ các bài Unit Test độc lập (100% Passed)
python tests/test_distance_matrix.py # Test A* tối ưu & Ma trận khoảng cách (TV2) - Passed 100%
python tests/test_ga.py              # Test giải thuật GA Core & Tuning (TV1) - Passed 100%
python tests/test_member5.py         # Test Fitness & Visualizer (TV5) - Passed 100%
python tests/test_day2_pipeline.py   # Test Pipeline E2E & Validator (TV5) - Passed 100%
python tests/test_day3_evaluator.py  # Test Evaluator & Metrics Suite (TV5) - Passed 100%
python tests/test_day4_integration.py # Test Cột mốc Tích hợp Hệ thống Toàn diện Ngày 4 - Passed 100%
python tests/test_day5_integration.py # Test Cột mốc Tối ưu & Tinh chỉnh Nâng cao Ngày 5 - Passed 100%
```

---

## 📊 Bảng trạng thái & Tiến độ chi tiết từng module

| STT | Module chức năng | File mã nguồn | Thành viên phụ trách | Trạng thái hiện tại |
|:---:|---|---|:---:|:---:|
| 1 | **Hàm mục tiêu (Fitness)** | `src/algorithms/fitness.py` | **TV5 (Nguyễn Phúc Hà)** | **Đã hoàn thành 100%** |
| 2 | **Trực quan hóa (Visualizer)** | `src/utils/visualizer.py` | **TV5 (Nguyễn Phúc Hà)** | **Đã hoàn thành 100%** (Bản đồ đa UAV, Hội tụ GA, Bar Charts, Scalability) |
| 3 | **Bộ kiểm định Data Contract** | `src/utils/validator.py` | **TV5 (Nguyễn Phúc Hà)** | **Đã hoàn thành 100%** |
| 4 | **Pipeline điều phối E2E & CLI** | `src/pipeline.py`, `src/main.py` | **TV5 (Nguyễn Phúc Hà)** | **Đã hoàn thành 100%** (Tự động tính số Drone theo tải trọng, điều phối đa quy mô) |
| 5 | **Bộ đo đạc thực nghiệm khoa học** | `src/utils/benchmark_evaluator.py` | **TV5 (Nguyễn Phúc Hà)** | **Đã hoàn thành 100%** (Xuất `docs/EXPERIMENT_RESULTS.md`) |
| 6 | **Giải thuật Di truyền (GA Core & Tuning)** | `src/algorithms/genetic_algorithm.py`, `src/utils/ga_tuning.py` | **TV1 (Sieqhart262) / TV5** | **Đã hoàn thành 100%** (Đã review & merge PR #3 và PR #7: Tinh chỉnh siêu tham số, Greedy Seeding, Scale penalty factor) |
| 7 | **A* Tối ưu + Ma trận khoảng cách** | `src/models/optimized_astar.py`, `src/utils/distance_matrix.py` | **TV2 (lynseyngoc)** | **Đã hoàn thành 100%** (A* Octile, Bresenham Line-of-sight, Smooth path, MD5 Cache - Đã review & merge PR #6) |
| 8 | **Sinh dữ liệu Benchmark chuẩn** | `src/utils/benchmark_generator.py` | **TV4 / TV5** | **Đã hoàn thành 100%** (Có sẵn `benchmark_10.json`, `50.json`, `100.json` trong `data/raw/`) |
| 9 | **Ràng buộc Pin & Trạm sạc** | `src/algorithms/energy_manager.py` | **TV3 / TV5 (Tích hợp)** | **Đã hoàn thành 100%** (Mô hình tiêu hao theo tải trọng, tự động chèn trạm sạc, đã vá lỗi lặp vô hạn) |
| 10 | **Thuật toán Baseline Greedy & 2-Opt** | `src/algorithms/baseline_greedy.py`, `src/algorithms/local_search.py` | **TV6 / TV5 (Tích hợp)** | **Đã hoàn thành 100%** (Greedy Nearest Neighbor & Tối ưu cục bộ 2-Opt gỡ giao cắt đường bay) |

---

## 🏆 Cột mốc Nghiệm thu Toàn dự án & Tổng kết Sprint 1 Tuần (Chủ Nhật - 18/10/2026)
- **Tỷ lệ hoàn thành khối lượng công việc Toàn dự án:** **100% Hoàn thành xuất sắc** (Đạt chuẩn nghiên cứu khoa học và sẵn sàng bảo vệ).
- **Các thành quả nghiệm thu chính trong Ngày Chủ nhật:**
  1. **Thực nghiệm Đối sánh Đa quy mô Toàn diện:** Đã thực thi chuỗi kịch bản đa quy mô (N = 10, 20, 30, 50 điểm), thu thập số liệu chi tiết và cập nhật báo cáo khoa học `docs/EXPERIMENT_RESULTS.md` cùng file CSV `data/processed/benchmark_comparison_results.csv`.
  2. **Bộ biểu đồ Nghiên cứu Khoa học:** Xuất tự động biểu đồ cột so sánh hiệu năng (`comparison_bars.png`) và đồ thị phân tích khả năng mở rộng quy mô (`scalability_analysis.png`).
  3. **Hợp nhất & Kiểm định Mã nguồn:** Tech Lead đã rà soát và merge toàn bộ các nhánh tính năng và báo cáo của các thành viên vào nhánh `develop` và `main`.
  4. **Tài liệu Hướng dẫn Chính thức:** Cập nhật hoàn chỉnh file `README.md` với kiến trúc 3 tầng, hướng dẫn chạy lệnh và kết quả thực nghiệm.
  5. **Chất lượng Kiểm thử:** Toàn bộ 7 bài Unit Test độc lập đều đạt kết quả **100% Passed**.
  6. **Sẵn sàng Bảo vệ:** Toàn bộ sản phẩm Sprint 1 tuần đã được đóng gói hoàn tất, đội ngũ sẵn sàng chuyển sang giai đoạn làm Báo cáo tổng kết và Slide thuyết trình!

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
3. `docs/KE_HOACH_PHAN_CONG_NHOM_6_NGUOI.txt`: Bảng phân công chi tiết công việc cho 6 thành viên.
4. `docs/Mathematical_Model.md`: Mô hình hóa toán học chính thức (Objective & Constraints).
5. `docs/figures/`: Thư mục lưu toàn bộ ảnh bản đồ đường bay và biểu đồ nghiên cứu.
