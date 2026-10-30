# Tổng hợp bộ test và lệnh kiểm thử – UDRP (Nhóm 1)

**Cập nhật:** 31/10/2026 · **Người tổng hợp:** Nguyễn Hải Anh (TV1) · **Mã nguồn:** nhánh `develop` (`676c972`)

Tài liệu này gom toàn bộ test case và các lệnh chạy test của chương trình vào một chỗ. Nó thay cho `docs/HUONG_DAN_CHAY_TEST.txt` (bản cũ chỉ nêu 3 / 14 bộ test và dùng đường dẫn trên máy cá nhân).

## 1. Tóm tắt

| Chỉ số | Giá trị |
| :--- | :--- |
| Số bộ test (file `tests/test_*.py`) | **14** (đều nằm trong `tests/run_all_tests.py`) |
| Số hàm test / số test case | **61** hàm test, **67** test case (một số hàm gồm nhiều mục `[TEST n]`) |
| Kết quả chạy ngày 31/10/2026 | **14 / 14 bộ PASS (100%)**, tổng 49.8 s, không bộ nào rơi vào thuật toán dự phòng |
| Môi trường đã chạy | Windows 11, Python 3.14.7 (venv của nhóm) |
| Kiểm thử tự động trên GitHub | GitHub Actions (`.github/workflows/python-tests.yml`), Python 3.10 / 3.11 / 3.12, mỗi lần push lên `main` / `develop` và mỗi PR |

## 2. Chuẩn bị môi trường (PowerShell)

```powershell
cd "<thư mục chứa repo>\Nhoms1-TKTT-Drone-giao-h-ng"
..\venv\Scripts\Activate.ps1            # bật môi trường ảo (nếu dùng venv)
pip install -r requirements.txt          # chỉ cần lần đầu
$env:MPLBACKEND = "Agg"                  # tùy chọn: không mở cửa sổ hình khi chạy test
```

- Tắt chế độ không mở hình: `Remove-Item Env:MPLBACKEND`.
- Mọi lệnh dưới đây chạy từ **thư mục gốc của repo**.

## 3. Các lệnh chạy test

### 3.1. Chạy toàn bộ (khuyên dùng)

| Lệnh | Tác dụng | Thời gian |
| :--- | :--- | :---: |
| `python tests/run_all_tests.py` | Chạy lần lượt 14 bộ test, in bảng tổng kết PASS/FAIL và thời gian từng bộ | ~50 s |
| `python src/main.py --test` | Giống lệnh trên (gọi `run_all_tests.main()`) | ~50 s |

Kết quả mong đợi ở dòng cuối: `TỔNG KẾT: 14/14 SUITES PASSED (100.0%)`.

### 3.2. Chạy từng bộ

| Lệnh | Bộ test | Cách in kết quả |
| :--- | :--- | :--- |
| `python tests/test_distance_matrix.py` | TV2 – A* và ma trận khoảng cách | `-> <tên test>: PASSED`, cuối: `9/9 UNIT TEST ... VƯỢT QUA` |
| `python tests/test_ga.py` | TV1 – Giải thuật Di truyền | 12 mục đánh số, cuối: `TAT CA UNIT TEST ... DA VUOT QUA` |
| `python -m unittest -v tests.test_energy_manager` | TV3 – Năng lượng và trạm sạc | `Ran 7 tests ... OK` |
| `python -m unittest -v tests.test_benchmark_generator` | TV4 – Sinh dữ liệu benchmark | `Ran 2 tests ... OK` |
| `python tests/test_member5.py` | TV5 – Hàm chi phí và vẽ hình | 2 mục đánh số |
| `python -m unittest -v tests.test_greedy_baseline` | TV6 – Greedy và 2-Opt | `Ran 5 tests ... OK` |
| `python tests/test_day2_pipeline.py` | Tích hợp: pipeline và bộ kiểm tra ràng buộc | `[TEST 1]`, `[TEST 2]` |
| `python tests/test_day3_evaluator.py` | Tích hợp: đánh giá đa quy mô | `[TEST 1]`–`[TEST 3]` |
| `python tests/test_day4_integration.py` | Tích hợp toàn hệ thống | `[TEST 1]`–`[TEST 4]` |
| `python tests/test_day5_integration.py` | Khởi tạo GA từ Greedy, số Drone theo tải | `[TEST 1]`–`[TEST 3]` |
| `python tests/test_day1_parallel_ontime.py` | Song song hóa ma trận, tỷ lệ đúng giờ | `[TEST 1]`–`[TEST 4]` |
| `python tests/test_day2_benchmark_speedup.py` | Thực nghiệm đa quy mô, đo tăng tốc | `[TEST 1]`–`[TEST 4]` |
| `python tests/test_day3_complexity_correctness.py` | Kiểm chứng 5 định lý đúng đắn | `[TEST 1]`–`[TEST 5]` |
| `python -m unittest -v tests.test_day4_tong_ket` | Tổng kết hệ thống | `Ran 5 tests ... OK` |

Các bộ viết bằng `unittest` cũng chạy được bằng `python tests/<file>.py` (in `Ran n tests ... OK`); thêm `-m unittest -v` để thấy tên từng test case.

### 3.3. Kiểm tra chương trình chính (CLI)

| Lệnh | Tác dụng | Kết quả kiểm tra ngày 31/10 |
| :--- | :--- | :--- |
| `python src/main.py --compare --benchmark 10 --no-plot --save-dir data/processed/demo` | Chạy cả Greedy và GA trên bộ 10 điểm, in bảng so sánh | Greedy 749.02, GA 706.50 (rẻ hơn 5.7%), cả hai hợp lệ, ~8 s |
| `python src/main.py --algorithm ga --benchmark 10 --no-plot --save-dir data/processed/demo` | Chạy riêng GA, lưu bản đồ tuyến bay và đường hội tụ | Cost 706.5 |
| `python src/main.py --algorithm greedy --benchmark 10 --no-plot --save-dir data/processed/demo` | Chạy riêng Greedy | Cost 749.02 |
| `python src/main.py --benchmark 10 --no-plot --parallel --speedup --save-dir data/processed/demo` | Lệnh GitHub Actions dùng để kiểm tra CLI: chạy song song và đo tăng tốc của ma trận A* | Thoát mã 0, ~13 s |
| `python src/main.py --evaluate-all` | Thực nghiệm đa quy mô, xuất `docs/EXPERIMENT_RESULTS.md` và biểu đồ | Ghi đè file được git theo dõi |

- Bỏ `--no-plot` để mở cửa sổ hình.
- `--save-dir` mặc định là `docs/figures` (được git theo dõi); khi chạy thử nên dùng `data/processed/demo` (bị git bỏ qua).
- Ở bộ 10 điểm, `--speedup` cho S₂ ≈ S₄ ≈ 0.03×: ma trận chỉ có 14 điểm nên thời gian khởi động tiến trình lớn hơn thời gian tính. Song song hóa chỉ có lợi ở dữ liệu lớn (mục 3.4).

### 3.4. Lệnh thực nghiệm (không phải unit test, chạy lâu)

| Lệnh | Tác dụng | Thời gian |
| :--- | :--- | :---: |
| `python src/utils/ga_tuning.py compare --scales 10 --seeds 5 --pop-size 100 --mutation-rate 0.5 --generations 2000` | So sánh Greedy với các biến thể GA qua đúng pipeline | ~1 phút |
| `python src/utils/ga_tuning.py compare --scales 50 100 --seeds 5 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8` | Như trên, 50 và 100 điểm, GA chấm điểm trên 8 tiến trình | ~8 phút |
| `python src/utils/ga_tuning.py compare --scales 500 --seeds 3 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8 --only-proposed` | 500 điểm, chỉ GA đề xuất | ~10 phút |
| `python src/utils/ga_tuning.py speedup --scales 10 50 100 500 --workers 1 2 4 8 --generations 200 --repeats 3` | Đo tăng tốc của GA song song, ghi `data/processed/ga_speedup_results.csv` | ~25 phút |
| `python src/utils/ga_tuning.py plot-speedup` | Vẽ lại `docs/figures/ga_speedup.png` từ CSV | vài giây |

Kết quả các lệnh này đã ghi trong `docs/GA_TUNING_RESULTS.md` (mục 10 và 13).

### 3.5. Lưu ý khi chạy

- **Bộ test ghi đè file đang được git theo dõi:** `docs/EXPERIMENT_RESULTS.md`, `docs/figures/*.png`, `data/processed/benchmark_comparison_results.csv`. Nếu không định commit các file này, chạy xong thì khôi phục:
  ```powershell
  git checkout -- docs data/processed
  ```
- **Kiểm tra đúng là module thật đã chạy:** pipeline bọc GA, Greedy và 2-Opt trong `try/except`. Nếu output có dòng `[Pipeline] Chạy fallback GA` hoặc `[Pipeline] Bỏ qua 2-Opt do lỗi` thì module thật đã lỗi, kết quả không còn giá trị.
- **Windows:** các test song song (`test_ga.py` mục 12, `test_distance_matrix.py`, `test_day1_parallel_ontime.py`) khởi động tiến trình con mất khoảng 0.6 s mỗi tiến trình; đó là lý do các bộ này chậm hơn dù dữ liệu nhỏ.

## 4. Danh sách 14 bộ test

Thứ tự theo `tests/run_all_tests.py`; thời gian là lần chạy ngày 31/10/2026.

| STT | File | Phụ trách | Kiểu | Số test case | Dữ liệu dùng | Thời gian | Kết quả |
| :---: | :--- | :--- | :---: | :---: | :--- | ---: | :---: |
| 1 | `test_distance_matrix.py` | TV2 Ngọc Linh | script | 9 | Lưới 50×50 tự dựng, 4 điểm | 2.27 s | PASS |
| 2 | `test_ga.py` | TV1 Nguyễn Hải Anh | script | 12 | 8 khách + 1 trạm sạc, ma trận Euclid, K = 3 | 5.77 s | PASS |
| 3 | `test_energy_manager.py` | TV3 Đỗ Đông Hải | unittest | 7 | Depot + 1 khách + 2 trạm sạc, ma trận 4×4 | 0.25 s | PASS |
| 4 | `test_benchmark_generator.py` | TV4 Gia Phong | unittest | 2 | 4 file `benchmark_{10,50,100,500}.json` + bộ sinh | 0.53 s | PASS |
| 5 | `test_member5.py` | TV5 Nguyễn Phúc Hà | script | 2 | Lời giải giả lập nhỏ | 0.84 s | PASS |
| 6 | `test_greedy_baseline.py` | TV6 Phạm Nhật Quang | unittest | 5 | Depot + 4 khách + 1 trạm sạc | 0.26 s | PASS |
| 7 | `test_day2_pipeline.py` | Tích hợp (TV5) | script | 2 | Dữ liệu tổng hợp 6 khách, 2 trạm sạc, lưới 40×40 | 6.88 s | PASS |
| 8 | `test_day3_evaluator.py` | Tích hợp (TV5) | script | 3 | Bộ sinh 10 điểm; đánh giá 6 và 12 điểm | 7.94 s | PASS |
| 9 | `test_day4_integration.py` | Tích hợp (TV1+TV2+TV3+TV6) | script | 4 | Tuyến dựng tay + `benchmark_10.json` | 8.00 s | PASS |
| 10 | `test_day5_integration.py` | Tối ưu (TV5) | script | 3 | `benchmark_10.json`, `benchmark_50.json` | 0.88 s | PASS |
| 11 | `test_day1_parallel_ontime.py` | TV5 | script | 4 | Tuyến 2 khách tự dựng; tổng hợp 6 khách | 3.96 s | PASS |
| 12 | `test_day2_benchmark_speedup.py` | TV5 | script | 4 | Đánh giá 6 và 10 điểm | 8.33 s | PASS |
| 13 | `test_day3_complexity_correctness.py` | TV5 (+TV3 cập nhật test 4) | script | 5 | 100 lần lai/đột biến ngẫu nhiên, 50 tuyến 2-Opt, tổng hợp 10 khách | 1.08 s | PASS |
| 14 | `test_day4_tong_ket.py` | TV5 | unittest | 5 | File trong `docs/`, CSV kết quả, tổng hợp 6 khách | 2.79 s | PASS |
| | **Tổng** | | | **67** | | **49.81 s** | **14/14** |

## 5. Chi tiết từng test case

Cột "Kiểm tra" tóm tắt các câu `assert` trong code, tức kết quả mong đợi để test được tính là PASS.

### 5.1. `test_distance_matrix.py` – A* và ma trận khoảng cách (TV2)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| DM-01 | `test_straight_line_without_obstacle` | Không có vùng cấm: A* từ (0,0) tới (30,40) cho đúng 50.0 |
| DM-02 | `test_detour_around_nfz_is_longer` | Có vùng cấm chắn giữa: đường đi vòng hữu hạn và dài hơn đường thẳng |
| DM-03 | `test_boundary_is_inclusive` | `build_grid` tính cả biên vùng cấm: ô (10,10), (15,15) bị chặn, (16,16) không |
| DM-04 | `test_unreachable_returns_inf` | Điểm không tới được: khoảng cách `inf`, không có đường đi |
| DM-05 | `test_matrix_properties` | Ma trận 4×4, đường chéo bằng 0, đối xứng, có lưu đường bay chi tiết |
| DM-06 | `test_cache_is_reused` | Gọi lại với cùng dữ liệu: đọc cache (< 0.5 s), kết quả trùng |
| DM-07 | `test_parallel_equals_sequential` | Tính song song cho ma trận và đường bay trùng tính tuần tự |
| DM-08 | `test_parallel_flag_compat` | Giao diện `parallel` / `num_workers` của `main.py`, `pipeline.py` vẫn chạy, kết quả trùng |
| DM-09 | `test_stats_recorded` | Thống kê lần tính: 6 cặp điểm = số cặp đường thẳng + số cặp chạy A* |

### 5.2. `test_ga.py` – Giải thuật Di truyền (TV1)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| GA-01 | `test_init_and_validation` | Chỉ lấy điểm giao hàng vào nhiễm sắc thể (bỏ depot, trạm sạc); K = 3 → vách ngăn −1, −2; báo lỗi khi không có khách hoặc tham số sai |
| GA-02 | `test_decode` | Giải mã đúng 4 ví dụ tính tay, kể cả vách ngăn liền nhau / ở đầu / ở cuối (bỏ tuyến rỗng) |
| GA-03 | `test_random_population` | Quần thể 60 cá thể đa dạng; mỗi cá thể là hoán vị hợp lệ, không chứa trạm sạc; mỗi khách được giao đúng 1 lần; ≤ K tuyến bắt đầu và kết thúc ở depot; cùng seed cho cùng quần thể |
| GA-04 | `test_evaluate` | Chi phí trùng `FitnessCalculator` của TV5; F = 1000 / (chi phí có phạt + 1); hệ số phạt 1 cho đúng fitness gốc; đánh giá lại dùng cache |
| GA-05 | `test_tournament_select` | Chọn đúng cá thể tốt nhất trong nhóm; trung bình cá thể được chọn tốt hơn trung bình quần thể |
| GA-06 | `test_order_crossover` | OX cho đúng kết quả ví dụ tính tay; điểm cắt phủ toàn bộ thì con = cha 1; 200 lần lai luôn ra hoán vị hợp lệ |
| GA-07 | `test_swap_mutation` | Đột biến đổi đúng 2 vị trí, giữ tính hợp lệ, trả về bản sao (không sửa cha); xác suất 0 thì không đổi |
| GA-08 | `test_evolve` | `history` dài đúng số thế hệ và không giảm; chi phí tốt nhất ≤ cá thể tốt nhất ban đầu; hết quá tải; chi phí khớp TV5; K = 1 chạy được |
| GA-09 | `test_seed_reproducible` | Cùng seed cho cùng lời giải và cùng `history` |
| GA-10 | `test_encode_and_initial_solutions` | `encode` là chiều ngược của `decode`; lời giải có sẵn nằm ở cá thể đầu; GA không tệ hơn lời giải khởi tạo; báo lỗi với lời giải sai |
| GA-11 | `test_energy_manager_with_charging` | Có EnergyManager: chấm điểm tuyến sau khi chèn trạm sạc; không bị treo khi đứng ở trạm sạc mà vẫn không tới được điểm kế (tuyến bị đánh dấu không khả thi) |
| GA-12 | `test_parallel_matches_sequential` | Cùng seed, chạy song song cho lời giải, `history`, chi phí trùng chạy tuần tự (có và không có EnergyManager); `num_workers = 0` báo lỗi |

### 5.3. `test_energy_manager.py` – Năng lượng và trạm sạc (TV3)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| EM-01 | `test_energy_consumption_with_payload` | Chặng 10 km: rỗng tốn 10 Wh, chở 2 kg tốn 13 Wh (năng lượng tăng theo tải) |
| EM-02 | `test_route_feasibility_check` | Tính được năng lượng của tuyến vượt dung lượng pin |
| EM-03 | `test_insert_charging_stations` | Tuyến thiếu pin được chèn trạm sạc, vẫn bắt đầu và kết thúc ở depot, trở thành khả thi |
| EM-04 | `test_depot_used_as_final_charge_stop_is_not_duplicated` | Khi depot là điểm sạc cho chặng cuối: không lặp depot (`[0, 1, 0]`), năng lượng 96 Wh |
| EM-05 | `test_rejects_invalid_battery_configuration` | Dung lượng ≤ 0 hoặc ngưỡng ngoài [0, 1) → `ValueError` |
| EM-06 | `test_station_service_time` | Thời gian sạc lấy từ trạm (20 phút), thiếu thông tin thì dùng mặc định 12 phút |
| EM-07 | `test_detailed_energy_breakdown_and_charging_time` | Chi tiết từng chặng: năng lượng, tải, loại điểm, thời gian sạc đúng; chế độ không chi tiết cho cùng tổng năng lượng |

### 5.4. `test_benchmark_generator.py` – Sinh dữ liệu (TV4)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| BG-01 | `test_all_benchmarks_exist_and_valid` | Đủ 4 file 10/50/100/500 điểm; số khách, trạm sạc, vùng cấm đúng; depot id 0, demand 0; khách có demand > 0; vùng cấm có `bounds` 4 số |
| BG-02 | `test_benchmark_generator_class` | `generate(15 khách, 3 trạm sạc, 4 vùng cấm)` cho đúng số lượng, có depot "0" |

### 5.5. `test_member5.py` – Hàm chi phí và vẽ hình (TV5)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| M5-01 | `FitnessCalculator` | Fitness > 0 và chi phí > 0 với lời giải mẫu |
| M5-02 | `UAVVisualizer` | Vẽ được bản đồ tuyến bay và đường hội tụ (figure khác `None`) |

### 5.6. `test_greedy_baseline.py` – Greedy và 2-Opt (TV6)

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| GR-01 | `test_greedy_router_solve` | 2 tuyến, phục vụ đủ 4 khách mỗi khách 1 lần, tuyến bắt đầu và kết thúc ở depot |
| GR-02 | `test_two_opt_route_uncrossing` | 2-Opt gỡ đường chéo: quãng đường giảm về đúng 40.0 |
| GR-03 | `test_apply_2opt_to_solution` | Áp dụng cho cả đội bay; tuyến 1 khách giữ nguyên |
| GR-04 | `test_apply_2opt_with_route_cost_guard` | Có `route_cost`: chỉ giữ kết quả 2-Opt khi chi phí tuyến không tăng |
| GR-05 | `test_greedy_integration_with_energy_and_fitness` | Greedy → 2-Opt → chèn trạm sạc → chấm điểm chạy liền mạch, có `distance`, `energy` |

### 5.7. `test_day2_pipeline.py` – Pipeline và bộ kiểm tra ràng buộc

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| P2-01 | `DataContractValidator` | Dữ liệu đúng được chấp nhận; thiếu depot bị bắt lỗi; lời giải trùng / thiếu khách bị bắt lỗi; **tuyến cạn pin bị bắt lỗi** (2 lỗi), không truyền EnergyManager thì không xét pin |
| P2-02 | `UAVRoutingPipeline` E2E | Dữ liệu tổng hợp 9 nút; ma trận 9×9; lời giải Greedy và GA đều hợp lệ; xuất được file hình |

### 5.8. `test_day3_evaluator.py` – Đánh giá đa quy mô

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| E3-01 | `BenchmarkGenerator` | Dữ liệu 10 điểm sinh ra đạt Data Contract |
| E3-02 | `BenchmarkEvaluator` | Đánh giá 2 quy mô (6, 12 điểm), có cột quãng đường và % tiết kiệm quãng đường, năng lượng |
| E3-03 | Xuất báo cáo, biểu đồ | Các file báo cáo và hình tồn tại, không rỗng |

### 5.9. `test_day4_integration.py` – Tích hợp toàn hệ thống

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| I4-01 | `test_energy_manager` | Năng lượng chặng đúng công thức; tuyến 160 km với pin 100 Wh không khả thi; sau khi sửa có trạm sạc 3, giữ đủ điểm giao |
| I4-02 | `test_local_search_2opt` | 2-Opt giảm quãng đường về 40.0 |
| I4-03 | `test_greedy_router` | Lời giải Greedy hợp lệ, đúng 2 tuyến cho 2 Drone |
| I4-04 | `test_day4_pipeline_integration` | Nạp `benchmark_10.json`; pipeline có EnergyManager; Greedy và GA đều hợp lệ, năng lượng ≥ 0, chi phí > 0; có file hình |

### 5.10. `test_day5_integration.py` – Khởi tạo GA từ Greedy, số Drone theo tải

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| I5-01 | Khởi tạo GA từ Greedy | Trên `benchmark_10.json`: chi phí GA ≤ chi phí Greedy |
| I5-02 | Số Drone theo tổng tải | `benchmark_50.json`: số Drone tối thiểu tính ra ≥ 14 |
| I5-03 | Hồi quy lỗi lặp vô hạn ở trạm sạc | Tuyến không tới được bị đánh dấu không khả thi; trạm sạc không bị chèn lặp |

### 5.11. `test_day1_parallel_ontime.py` – Song song hóa ma trận, tỷ lệ đúng giờ

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| D1-01 | `test_ontime_delivery_rate` | 2 khách giao trong khung giờ → 100%; 1 khách trễ → 50% và có phạt trễ giờ |
| D1-02 | `test_parallel_distance_matrix` | Ma trận song song trùng tuần tự (sai số 1e-5) |
| D1-03 | `test_speedup_measurement` | Kết quả đo tăng tốc có `times_sec`, `speedup`, S₁ = 1.0 |
| D1-04 | `test_pipeline_integration_with_parallel_and_ontime` | Pipeline chạy song song, kết quả có tỷ lệ đúng giờ trong [0, 100], đủ 6 đơn |

### 5.12. `test_day2_benchmark_speedup.py` – Thực nghiệm đa quy mô, đo tăng tốc

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| D2-01 | `test_evaluate_scale_metrics` | Đủ 4 chỉ số: quãng đường, năng lượng, đúng giờ, thời gian; cờ an toàn pin |
| D2-02 | `test_run_speedup_benchmark` | Kết quả đo có danh sách tiến trình, hệ số tăng tốc, S₁ = 1.0, có file biểu đồ |
| D2-03 | `test_visualizer_plot_speedup` | Vẽ và lưu được biểu đồ tăng tốc |
| D2-04 | `test_multi_scale_benchmark_e2e` | Chạy 2 quy mô (6, 10): có CSV, báo cáo Markdown (cột đúng giờ, mục tăng tốc, mục pin), 3 biểu đồ |

### 5.13. `test_day3_complexity_correctness.py` – Kiểm chứng 5 định lý

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| C3-01 | Định lý 2 – toán tử GA | 100 lần lai OX và 100 lần đột biến: con giữ đúng tập gen, đủ khách, không trùng |
| C3-02 | Định lý 1 – A* | Đường bay né vùng cấm [20, 40]², dài hơn đường thẳng, không điểm nào nằm trong vùng cấm |
| C3-03 | Định lý 3 – 2-Opt | 50 tuyến ngẫu nhiên: quãng đường không tăng, giữ depot ở hai đầu, không mất / thêm điểm |
| C3-04 | Định lý 4 – chèn trạm sạc | Thuật toán dừng, chèn trạm sạc 4, tuyến sau khi sửa khả thi về pin |
| C3-05 | Định lý 5 – khởi tạo GA từ Greedy | Dữ liệu tổng hợp 10 khách: chi phí GA ≤ Greedy, fitness GA ≥ Greedy |

### 5.14. `test_day4_tong_ket.py` – Tổng kết hệ thống

| ID | Test case | Kiểm tra |
| :--- | :--- | :--- |
| T4-01 | `test_01_tat_ca_bieu_do_ton_tai` | Đủ 7 biểu đồ trong `docs/figures/`, mỗi file > 10 KB |
| T4-02 | `test_02_ve_bieu_do_on_time_rate` | Vẽ và lưu được biểu đồ tỷ lệ đúng giờ |
| T4-03 | `test_03_tinh_nhat_quan_du_lieu_csv` | CSV kết quả đủ cột; đúng giờ của GA ≥ Greedy; mọi lời giải an toàn pin |
| T4-04 | `test_04_tai_lieu_tong_ket_va_phan_tich` | Các tài liệu tổng kết và phân tích tồn tại, đủ nội dung |
| T4-05 | `test_05_chay_tich_hop_pipeline_va_song_song` | Pipeline song song cho kết quả có tỷ lệ đúng giờ trong [0, 100]; lời giải hợp lệ theo bộ kiểm tra (có xét pin) |

## 6. Kết quả chạy ngày 31/10/2026

Lệnh `python tests/run_all_tests.py` trên nhánh `develop` (`676c972`):

```text
1    | TV2: A* Octile & Distance Matrix Cache                | PASS | 2.27s
2    | TV1: GA Core Engine & Hyperparameter Tuning           | PASS | 5.77s
3    | TV3: Energy Manager & Charging Stations               | PASS | 0.25s
4    | TV4: Multi-Scale Benchmark Generator                  | PASS | 0.53s
5    | TV5: Multi-Objective Fitness & Visualizer             | PASS | 0.84s
6    | TV6: Baseline Greedy & 2-Opt Local Search             | PASS | 0.26s
7    | E2E Pipeline Integration & Data Contract Validator    | PASS | 6.88s
8    | Multi-Scale Benchmark Evaluator & Visual Charts       | PASS | 7.94s
9    | Full System Integration (TV1 + TV2 + TV3 + TV6)       | PASS | 8.00s
10   | Hybrid GA Seeding & Dynamic Fleet Sizing              | PASS | 0.88s
11   | TV5: Parallel Distance Matrix & On-time Delivery Rate | PASS | 3.96s
12   | TV5: Multi-Scale Benchmark & Speedup Analysis         | PASS | 8.33s
13   | TV5: Mathematical Correctness & Complexity Proofs     | PASS | 1.08s
14   | TV5: System Verification & Final Defense Wrap-up      | PASS | 2.79s
TỔNG KẾT: 14/14 SUITES PASSED (100.0%) - Tổng thời gian: 49.81s
```

Chạy riêng: `test_distance_matrix.py` 9/9, `test_ga.py` 12/12, `unittest` của TV3 / TV4 / TV6 / tổng kết lần lượt 7 / 2 / 5 / 5 test OK.
