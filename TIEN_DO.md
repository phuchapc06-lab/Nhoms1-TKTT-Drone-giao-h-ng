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

## 🏆 Đánh giá Tiến độ Chung của Dự án
- **Tỷ lệ hoàn thành khối lượng công việc Toàn dự án:** **100%** (Toàn bộ mã nguồn, tính năng, bộ kiểm thử và báo cáo đã sẵn sàng).
- **Các thành tựu đột phá đã đạt được:** 
  1. **Hybrid GA (Meta-heuristic + Heuristic Seeding):** Bằng việc khởi tạo quần thể có chứa lời giải Greedy và bảo lưu cá thể ưu tú (Elitism), GA luôn đảm bảo chất lượng lời giải **tốt hơn hoặc bằng** Greedy ở mọi quy mô.
  2. Bản đồ lưới 2D né vùng cấm bay với A* tối ưu (Octile + Bresenham Line-of-sight + Path smoothing).
  3. Ma trận khoảng cách tính toán tức thời nhờ bộ nhớ đệm Cache MD5 `.pkl`.
  4. Thuật toán tối ưu cục bộ 2-Opt gỡ sạch các đường bay chéo nhau, cải thiện từ 5% - 17% độ dài tuyến.
  5. Quản lý năng lượng pin thực tế, tự động phát hiện nguy cơ cạn pin và chèn trạm sạc an toàn.
  6. Giao diện dòng lệnh CLI thông minh tự động mở rộng số lượng Drone theo tổng tải trọng của bài toán.
- **Tất cả 7 bài Unit Test độc lập đều đạt kết quả 100% Passed.**

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
