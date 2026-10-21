# TIẾN ĐỘ THỰC HIỆN ĐỀ TÀI: UAV DELIVERY ROUTING PROBLEM (UDRP)
## Nhóm 1 - Môn Phân tích & Thiết kế Thuật toán

---

## 🎯 Tổng quan Tiến độ Sprint 1 Tuần (7 Ngày)
- **Mục tiêu:** Xây dựng hệ thống hoàn chỉnh giải bài toán Định tuyến Đội bay UAV giao hàng trong đô thị né vùng cấm bay, quản lý pin và tối ưu hóa đa mục tiêu.
- **Trạng thái:** **HOÀN THÀNH 100% TOÀN DỰ ÁN (SẴN SÀNG CHO TUẦN LÀM VIỆC MỚI)**.

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
  5. **Hệ thống Kiểm thử Hồi quy 10/10 Suites:** Chuẩn hóa toàn bộ 10 bài Unit Test và Integration Test độc lập bao quát đầy đủ 6 thành viên, chạy tự động qua `python src/main.py --test` và `python tests/run_all_tests.py` đạt kết quả **100% Passed**.
  6. **Tự động hóa CI/CD:** Thiết lập workflow GitHub Actions `.github/workflows/python-tests.yml` tự động kiểm thử trên Python 3.10, 3.11, 3.12.
  7. **Sẵn sàng cho Tuần làm việc Mới:** Toàn bộ mã nguồn, dữ liệu, tài liệu và test đã hoàn thiện 100% sạch sẽ và đồng bộ!

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
