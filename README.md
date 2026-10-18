# UAV Delivery Routing Problem (UDRP)
## Hệ thống Tối ưu hóa Định tuyến Đội bay UAV Giao hàng Đô thị Thông minh

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
- Python 3.9+
- Cài đặt thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

### 5.2. Chạy thử nghiệm đối sánh trực tiếp (CLI)
```bash
# 1. So sánh trực quan trên kịch bản chuẩn 10 điểm (Có đồ họa hiển thị)
python src/main.py --benchmark data/raw/benchmark_10.json --compare

# 2. Chế độ chạy nhanh không bật popup cửa sổ đồ thị (Batch run)
python src/main.py --benchmark data/raw/benchmark_10.json --compare --no-plot

# 3. Thử nghiệm trên quy mô trung bình (50 điểm giao hàng, tự động bố trí 14 UAV)
python src/main.py --benchmark data/raw/benchmark_50.json --generations 50 --compare --no-plot

# 4. Tự động chạy Suite thực nghiệm đa quy mô và cập nhật báo cáo khoa học
python src/main.py --evaluate-all
```

### 5.3. Chạy kiểm thử tự động toàn diện (Unit & Integration Tests - 100% Passed)
```bash
python tests/test_distance_matrix.py   # Test A* tối ưu & MD5 Cache (TV2) - Passed 100%
python tests/test_ga.py                # Test GA Core Engine & Tuning (TV1) - Passed 100%
python tests/test_member5.py           # Test Fitness & Visualizer (TV5) - Passed 100%
python tests/test_day2_pipeline.py     # Test Pipeline E2E & Validator (TV5) - Passed 100%
python tests/test_day3_evaluator.py    # Test Benchmark Evaluator (TV5) - Passed 100%
python tests/test_day4_integration.py  # Test Cột mốc Tích hợp Toàn diện (TV5) - Passed 100%
python tests/test_day5_integration.py  # Test Hybrid GA Seeding & Dynamic Fleet (TV5) - Passed 100%
```

---

## 📂 6. CẤU TRÚC THƯ MỤC DỰ ÁN

```
uav-routing-project/
├── data/
│   ├── raw/                           # Các bộ dữ liệu chuẩn (benchmark_10, 50, 100, 500.json)
│   └── processed/                     # Dữ liệu xuất thực nghiệm (CSV) và cache khoảng cách (.pkl)
├── docs/
│   ├── figures/                       # Hình ảnh trực quan hóa bản đồ tuyến bay và đồ thị hội tụ
│   ├── EXPERIMENT_RESULTS.md          # Báo cáo thực nghiệm khoa học đa quy mô
│   ├── GA_TUNING_RESULTS.md           # Báo cáo tinh chỉnh siêu tham số giải thuật di truyền
│   ├── Mathematical_Model.md          # Mô hình hóa toán học chính thức của bài toán
│   ├── NGUYEN_PHUC_HA_CONTRIBUTION.md # Báo cáo chi tiết minh chứng đóng góp cá nhân của Tech Lead
│   └── TV1_CONTRIBUTION.md            # Báo cáo đóng góp cá nhân của Thành viên 1
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
├── tests/                             # Hệ thống 7 bộ Unit Test độc lập kiểm định chất lượng (100% Passed)
├── TIEN_DO.md                         # Bảng theo dõi tiến độ tổng thể của toàn dự án
├── requirements.txt                   # Danh mục thư viện Python phụ thuộc
└── README.md                          # Tài liệu hướng dẫn chính thức của dự án (File này)
```

---

## 🏆 7. KẾT LUẬN & NGHIỆM THU DỰ ÁN

- **Trạng thái Sprint 1 tuần:** **Hoàn thành 100%** đúng tiến độ đề ra vào **Chủ Nhật (18/10/2026)**.
- Toàn bộ 6 module của 6 thành viên đã được ghép nối hoàn chỉnh, kiểm thử tự động toàn diện và nghiệm thu đạt chuẩn chất lượng nghiên cứu khoa học.
- Đầy đủ báo cáo khoa học, bảng số liệu thực nghiệm đối sánh, biểu đồ phân tích và mã nguồn sạch sẽ trên GitHub.
