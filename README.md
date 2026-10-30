# UAV Delivery Routing Problem (UDRP)
## Hệ thống Tối ưu hóa Định tuyến Đội bay UAV Giao hàng Đô thị Thông minh

[![Python CI - UAV Routing Tests](https://github.com/phuchapc06-lab/Nhoms1-TKTT-Drone-giao-h-ng/actions/workflows/python-tests.yml/badge.svg)](https://github.com/phuchapc06-lab/Nhoms1-TKTT-Drone-giao-h-ng/actions)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Tests](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen)
![Status](https://img.shields.io/badge/status-production%20ready-success)

> **Đồ án môn học:** Phân tích & Thiết kế Thuật toán — Trường Đại học Kinh tế Quốc dân (NEU)  
> **Nhóm thực hiện:** Nhóm 1  
> **Trưởng nhóm / Kỹ sư Tích hợp Hệ thống (Tech Lead):** Nguyễn Phúc Hà (Thành viên 5)  
> **Kho lưu trữ GitHub:** [https://github.com/phuchapc06-lab/Nhoms1-TKTT-Drone-giao-h-ng](https://github.com/phuchapc06-lab/Nhoms1-TKTT-Drone-giao-h-ng)

---

## 📌 1. TỔNG QUAN ĐỀ TÀI

Dự án giải quyết bài toán định tuyến đa phương tiện bay không người lái (**UAV Delivery Routing Problem - UDRP**), một bài toán tối ưu tổ hợp thuộc lớp **NP-hard** trong logistics đô thị thông minh. Mục tiêu là lập lộ trình bay phục vụ tập khách hàng sao cho **tổng chi phí là nhỏ nhất**, đồng thời thỏa mãn đồng thời các ràng buộc kỹ thuật khắt khe trong thực tế:

1. **Vật cản không gian:** Lượn vòng an toàn qua các **Vùng cấm bay (No-Fly Zones - NFZs)** như nhà cao tầng, khu quân sự.
2. **Năng lượng pin hữu hạn:** Dung lượng pin giới hạn, tự động ghé **Trạm sạc (Charging Stations)** khi pin xuống dưới ngưỡng an toàn 15%.
3. **Tiêu hao năng lượng phi tuyến:** Điện năng tiêu hao tính theo cả quãng đường và khối lượng hàng chuyên chở thực tế ($E = d \cdot (c_{base} + \alpha \cdot \text{payload})$).
4. **Tải trọng tối đa:** Mỗi Drone chỉ chở tối đa $Q_{max} = 5.0\text{ kg}$.
5. **Khung giờ giao hàng (Time Windows):** Phạt vi phạm nếu giao hàng trễ so với yêu cầu của khách hàng.

---

## 🏗️ 2. KIẾN TRÚC HỆ THỐNG 3 TẦNG (SYSTEM ARCHITECTURE)

Hệ thống được thiết kế theo mô hình tích hợp toàn trình khép kín (**End-to-End Pipeline**):

```
       [ Dữ liệu JSON Benchmark (10, 50, 100, 500 điểm) ]
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │ TẦNG 1: TÍNH TOÁN HÌNH HỌC KHÔNG GIAN     │
        │ - Thuật toán A* tối ưu (Octile Heuristic) │ (Thành viên 2)
        │ - Bước nhảy Tầm nhìn thẳng (Line-of-Sight)│
        │ - Bộ nhớ đệm Ma trận khoảng cách MD5 Cache│
        └─────────────────────┬─────────────────────┘
                              │ Ma trận khoảng cách né NFZ
                              ▼
        ┌───────────────────────────────────────────┐
        │ TẦNG 2: BỘ GIẢI THUẬT TỐI ƯU TỔ HỢP       │
        │ - Hybrid Genetic Algorithm (GA Core)      │ (Thành viên 1)
        │ - Khởi tạo từ Greedy Seeding              │ (Thành viên 6 / 1)
        │ - Tối ưu cục bộ 2-Opt (Local Search)      │ (Thành viên 6)
        └─────────────────────┬─────────────────────┘
                              │ Tuyến bay sơ bộ
                              ▼
        ┌───────────────────────────────────────────┐
        │ TẦNG 3: KIỂM ĐỊNH RÀNG BUỘC & ĐIỀU PHỐI   │
        │ - Quản lý Pin & Tự động chèn Trạm sạc     │ (Thành viên 3)
        │ - Hàm mục tiêu đa tiêu chí (Fitness)      │ (Thành viên 5)
        │ - Bộ kiểm định hợp đồng dữ liệu Validator │ (Thành viên 5)
        │ - Trực quan hóa bản đồ đa UAV & Hội tụ    │ (Thành viên 5)
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
        [ Bản đồ đường bay | Đồ thị hội tụ | Báo cáo Markdown & CSV ]
```

---

## 👥 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN (TEAM ROLES)

| Ký hiệu | Thành viên | Vai trò | Phân công chuyên môn chính |
| :---: | :--- | :--- | :--- |
| **TV1** | Thành viên 1 | Lập trình viên GA Core | Lõi giải thuật Di truyền (GA), Toán tử OX, Đột biến Swap, Tinh chỉnh siêu tham số |
| **TV2** | Thành viên 2 | Lập trình viên Pathfinding | Thuật toán A* né vùng cấm bay, Line-of-sight, Làm mượt đường bay, Bộ đệm MD5 Cache |
| **TV3** | Thành viên 3 | Kỹ sư Ràng buộc & Năng lượng | Mô hình tiêu hao pin theo tải trọng, thuật toán tự động chèn trạm sạc |
| **TV4** | Thành viên 4 | Kỹ sư Dữ liệu & Benchmark | Sinh tập dữ liệu đa quy mô (10, 50, 100, 500 điểm), chuẩn hóa Khung giờ giao hàng |
| **TV5** | **Nguyễn Phúc Hà** | **Nhóm trưởng (Tech Lead)** | **Hàm mục tiêu Fitness, Bộ kiểm định Data Contract, Khung điều phối Pipeline E2E, Bộ đo đạc thực nghiệm Evaluator, Trực quan hóa Visualizer, Quản lý Git** |
| **TV6** | Thành viên 6 | Lập trình viên Baseline | Thuật toán Tham lam (Greedy Baseline Router) & Thuật toán Tối ưu cục bộ 2-Opt |

---

## 📊 4. KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH (EXPERIMENTAL RESULTS)

Số liệu thực nghiệm đo đạc thực tế trên hệ thống (trích xuất tự động từ [`docs/EXPERIMENT_RESULTS.md`](docs/EXPERIMENT_RESULTS.md)):

| Quy mô (N) | Số Drone (K) | Quãng đường Greedy (km) | Quãng đường GA (km) | Tiết kiệm Quãng đường (%) | Tiết kiệm Năng lượng (%) | Tiết kiệm Chi phí (%) | Thời gian Greedy (s) | Thời gian GA (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10 điểm** | 3 | 377.25 km | **296.41 km** | **-21.43%** | **-12.21%** | **-17.95%** | 0.0036 s | 0.4589 s |
| **20 điểm** | 6 | 517.00 km | **448.03 km** | **-13.34%** | **-9.78%** | **-10.90%** | 0.0005 s | 1.0874 s |
| **30 điểm** | 9 | 695.47 km | **635.83 km** | **-8.58%** | **-7.88%** | **-8.39%** | 0.0015 s | 2.1758 s |
| **50 điểm** | 14 | 1367.26 km | **1277.71 km** | **-6.55%** | **-4.27%** | **-8.79%** | 0.0070 s | 1.9526 s |

> **Kết luận khoa học:**
> - Giải thuật đề xuất ($A^* + GA + \text{2-Opt}$) rút ngắn trung bình **12.47%** quãng đường bay và tiết kiệm **8.53%** năng lượng tiêu thụ so với Greedy Baseline.
> - Cơ chế **Hybrid GA Seeding** đảm bảo lời giải của GA không bao giờ kém hơn Greedy ở bất kỳ quy mô nào.
> - Thời gian tính toán nằm trong ngưỡng vài giây, hoàn toàn đáp ứng khả năng điều phối thời gian thực trong logistics đô thị.

---

## 🚀 5. HƯỚNG DẪN CÀI ĐẶT & THỰC THI (QUICK START)

### 5.1. Yêu cầu môi trường
- Python 3.9+ (hỗ trợ 3.10, 3.11, 3.12)
- Cài đặt thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

### 5.2. Chạy thử nghiệm đối sánh trực tiếp (CLI)
```bash
# 1. So sánh trực quan trên kịch bản chuẩn 10 điểm (Có đồ họa hiển thị)
python src/main.py --benchmark 10 --compare

# 2. Chế độ chạy nhanh không bật popup cửa sổ đồ thị (Batch run)
python src/main.py --benchmark 10 --compare --no-plot

# 3. Chạy với chế độ tính toán song song đa luồng (Parallel Computing) & đo hệ số tăng tốc Speedup
python src/main.py --benchmark 50 --compare --parallel --speedup --no-plot

# 4. Thử nghiệm trên quy mô trung bình (50 điểm giao hàng, tự động tính số UAV)
python src/main.py --benchmark 50 --compare --no-plot

# 5. Thử nghiệm quy mô lớn 100 và 500 điểm
python src/main.py --benchmark 100 --algorithm ga --parallel --no-plot
python src/main.py --benchmark 500 --algorithm greedy --no-plot

# 6. Tự động chạy Suite thực nghiệm đa quy mô và cập nhật báo cáo khoa học
python src/main.py --evaluate-all
```

### 5.3. Chạy kiểm thử tự động toàn diện (14/14 Test Suites - 100% Passed)
```bash
# Lệnh nhanh nhất: Kích hoạt toàn bộ 13 bộ kiểm thử qua CLI chính
python src/main.py --test

# Hoặc chạy trực tiếp qua Master Test Runner:
python tests/run_all_tests.py

# Hoặc chạy kiểm thử từng module chuyên biệt:
python tests/test_distance_matrix.py       # TV2: A* Octile & MD5 Cache
python tests/test_ga.py                    # TV1: GA Core Engine & Tuning
python tests/test_energy_manager.py         # TV3: Energy Manager & Charging
python tests/test_benchmark_generator.py   # TV4: Multi-Scale Benchmark Generator
python tests/test_member5.py               # TV5: Multi-Objective Fitness & Visualizer
python tests/test_greedy_baseline.py       # TV6: Baseline Greedy & 2-Opt Local Search
python tests/test_day2_pipeline.py         # Tích hợp: E2E Pipeline & Data Validator
python tests/test_day3_evaluator.py        # Tích hợp: Multi-Scale Evaluator
python tests/test_day4_integration.py      # Tích hợp: Full System (TV1+TV2+TV3+TV6)
python tests/test_day5_integration.py      # Tối ưu: Hybrid GA Seeding & Dynamic Fleet
python tests/test_day1_parallel_ontime.py  # Ngày 1: Song song hóa A* Matrix & On-time Delivery Rate
python tests/test_day2_benchmark_speedup.py # Ngày 2: Thực nghiệm Đa quy mô & Biểu đồ Speedup
python tests/test_day3_complexity_correctness.py # Ngày 3: Chứng minh Toán học & Tính đúng đắn
python tests/test_day4_tong_ket.py               # Ngày 4: Kiểm thử tổng kết & trực quan hóa On-time rate
```

---

## 📂 6. CẤU TRÚC THƯ MỤC DỰ ÁN

Tài liệu tổng hợp về cấu trúc, luồng xử lý và các đầu ra dữ liệu có tại [docs/DU_LIEU_CHUONG_TRINH.md](docs/DU_LIEU_CHUONG_TRINH.md).

```
uav-routing-project/
├── .github/
│   └── workflows/
│       └── python-tests.yml           # CI/CD tự động kiểm thử toàn diện trên GitHub Actions
├── data/
│   ├── raw/                           # Các bộ dữ liệu chuẩn (benchmark_10, 50, 100, 500.json)
│   └── processed/                     # Dữ liệu xuất thực nghiệm (CSV) và cache khoảng cách (.pkl)
├── docs/
│   ├── figures/                       # Hình ảnh trực quan hóa bản đồ tuyến bay và đồ thị hội tụ
│   ├── EXPERIMENT_RESULTS.md          # Báo cáo thực nghiệm khoa học đa quy mô
│   ├── GA_TUNING_RESULTS.md           # Báo cáo tinh chỉnh siêu tham số giải thuật di truyền
│   ├── Mathematical_Model.md          # Mô hình hóa toán học chính thức của bài toán
│   ├── DU_LIEU_CHUONG_TRINH.md        # Tổng hợp cấu trúc, luồng xử lý và đầu ra dữ liệu chương trình
│   ├── NGUYEN_PHUC_HA_CONTRIBUTION.md # Báo cáo chi tiết minh chứng đóng góp cá nhân của Tech Lead
│   ├── TV1_CONTRIBUTION.md            # Báo cáo đóng góp cá nhân của Thành viên 1
│   └── TV3_CONTRIBUTION.md            # Báo cáo đóng góp cá nhân của Thành viên 3 (Năng lượng & Pin)
├── src/
│   ├── algorithms/
│   │   ├── genetic_algorithm.py       # Giải thuật Di truyền (GA Core Engine - TV1)
│   │   ├── fitness.py                 # Hàm mục tiêu đa tiêu chuẩn & Fitness Calculator (TV5)
│   │   ├── energy_manager.py          # Quản lý pin & Tự động chèn trạm sạc (TV3)
│   │   ├── local_search.py            # Thuật toán tối ưu cục bộ 2-Opt (TV6)
│   │   └── baseline_greedy.py         # Thuật toán tham lam đối chuẩn Nearest Neighbor (TV6)
│   ├── models/
│   │   └── optimized_astar.py         # Thuật toán A* tối ưu né vùng cấm bay (TV2)
│   ├── utils/
│   │   ├── distance_matrix.py         # Tính ma trận khoảng cách có bộ đệm Cache MD5 (TV2)
│   │   ├── validator.py               # Bộ kiểm định chuẩn Data Contract & tính hợp lệ Solution (TV5)
│   │   ├── visualizer.py              # Bộ công cụ vẽ bản đồ đa UAV và đồ thị hội tụ (TV5)
│   │   ├── benchmark_generator.py     # Trình sinh dữ liệu thử nghiệm chuẩn (TV4/TV5)
│   │   ├── benchmark_evaluator.py     # Bộ đo đạc thực nghiệm khoa học đa quy mô (TV5)
│   │   └── ga_tuning.py               # Script quét siêu tham số GA tự động (TV1)
│   ├── pipeline.py                    # Khung điều phối tích hợp hệ thống toàn trình End-to-End (TV5)
│   └── main.py                        # Điểm khởi chạy chính của chương trình qua dòng lệnh CLI (TV5)
├── tests/                             # Hệ thống 10 bộ Unit & Integration Tests (100% Passed)
│   ├── run_all_tests.py               # Master Test Runner chạy toàn bộ 10 suites
│   ├── test_distance_matrix.py        # Unit Test TV2
│   ├── test_ga.py                     # Unit Test TV1
│   ├── test_energy_manager.py         # Unit Test TV3
│   ├── test_benchmark_generator.py    # Unit Test TV4
│   ├── test_member5.py                # Unit Test TV5
│   ├── test_greedy_baseline.py        # Unit Test TV6
│   ├── test_day2_pipeline.py          # Integration Test Ngày 2
│   ├── test_day3_evaluator.py         # Integration Test Ngày 3
│   ├── test_day4_integration.py       # Integration Test Ngày 4
│   └── test_day5_integration.py       # Integration Test Ngày 5
├── TIEN_DO.md                         # Bảng theo dõi tiến độ tổng thể của toàn dự án
├── requirements.txt                   # Danh mục thư viện Python phụ thuộc
└── README.md                          # Tài liệu hướng dẫn chính thức của dự án (File này)
```

---

## 📌 7. TIẾN ĐỘ THỰC HIỆN

- Hệ thống đã ghép nối hoàn chỉnh các module: tìm đường tránh vật cản A*, giải thuật di truyền GA, quản lý pin và trạm sạc, thuật toán tham lam đối sánh và tối ưu cục bộ 2-Opt.
- Tiến độ tuần này (cập nhật đến Thứ Bảy - 24/10/2026):
  - Tối ưu tính toán song song ma trận khoảng cách $A^*$ và kiểm tra khung giờ giao hàng (Time Windows).
  - Chạy thực nghiệm đối sánh trên các tập dữ liệu đa quy mô, ghi nhận số liệu và xuất bộ biểu đồ phân tích.
  - Hoàn thành báo cáo phân tích độ phức tạp thuật toán và các chứng minh toán học (`docs/COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md`).
  - Bổ sung biểu đồ tỷ lệ giao hàng đúng giờ (`docs/figures/ontime_rate_comparison.png`) và báo cáo tổng kết đề tài (`docs/BAO_CAO_TONG_KET_DE_TAI.md`).
  - Toàn bộ 14 bộ kiểm thử độc lập đều đã chạy đạt (`python tests/run_all_tests.py` hoặc `python src/main.py --test`).
