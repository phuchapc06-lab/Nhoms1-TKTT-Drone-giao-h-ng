# Tinh chỉnh & đánh giá Giải thuật Di truyền (GA)
**Phụ trách:** Thành viên 1 (GA Core Engine) · **Ngày:** 16/10/2026 · **Script:** `src/utils/ga_tuning.py`

## 1. Kết luận chính
| Quy mô | Greedy + 2-Opt | GA trước tinh chỉnh (cấu hình cũ của pipeline) | GA sau tinh chỉnh (đề xuất) |
| :---: | ---: | ---: | ---: |
| 10 điểm | 758.74 | 763.98 ± 22.17 (**kém** Greedy 0.69%) | **712.08 ± 0.00 (tốt hơn 6.15%)** |
| 50 điểm | 4177.60 | 5667.97 ± 269.25 (kém 35.68%, 1/5 lời giải không hợp lệ) | **3810.39 ± 54.38 (tốt hơn 8.79%)** |
| 100 điểm | 11471.35 | 21816.01 ± 1124.28 (kém 90.18%, 4/5 không hợp lệ) | **11230.08 ± 199.12 (tốt hơn 2.10%)** |

Tổng chi phí theo `FitnessCalculator` của TV5 (có `EnergyManager`), thấp hơn là tốt hơn; GA chạy 5 seed, giá trị = trung bình ± độ lệch chuẩn.
Mọi lời giải của GA đề xuất đều hợp lệ (5/5 ở cả 3 quy mô).

**GA đề xuất** = tham số tinh chỉnh (`pop_size=100, mutation_rate=0.5, generations=2000`) + phạt vi phạm ràng buộc ×100 khi chọn lọc + chấm điểm có `EnergyManager` (sau khi chèn trạm sạc) + khởi tạo quần thể từ lời giải Greedy.

## 2. Thiết lập thực nghiệm
- **Dữ liệu:** `data/raw/benchmark_{10,50,100}.json` sinh bằng `src/utils/benchmark_generator.py` (TV4, seed 100). Ma trận khoảng cách A* của TV2 (không có cặp nào không tới được).
- **Số Drone K:** mô hình hiện tại cho mỗi Drone bay **1 chuyến**, tải tối đa 5 kg. Tổng hàng: 11.2 / 56.4 / 117.5 kg, nên 3 Drone (mặc định của `main.py`) không đủ chở benchmark 50 và 100. Chọn K = ⌈1.2 × tổng hàng / 5 kg⌉ = **3 / 14 / 29** (dư 20% sức chở).
- **Luồng đánh giá:** mọi thuật toán chạy qua đúng `UAVRoutingPipeline.run_experiment` của TV5: thuật toán → 2-Opt (TV6) → chèn trạm sạc (TV3) → `FitnessCalculator.evaluate_solution(..., energy_manager)` → `DataContractValidator`. Script kiểm tra pipeline dùng đúng `GreedyRouter` của TV6 (không rơi vào bản dự phòng).
- **Ngẫu nhiên:** Greedy tất định (1 lần chạy); GA chạy seed 0–4.
- **Thời gian:** Python thuần, 1 luồng. Ở benchmark 100, thời gian dao động lớn (± 30–50 s) vì máy chạy song song tác vụ khác; chỉ nên đọc như bậc độ lớn.

## 3. Quét tham số
Chạy bằng `ga_tuning.py sweep`, 10 seed mỗi cấu hình, đo cost tốt nhất theo thước đo nội bộ của GA (chưa 2-Opt / chèn trạm sạc, chưa có `EnergyManager`, phạt gốc của TV5).

**Benchmark 10 điểm** (500 thế hệ; cost tốt nhất biết được 761.55):

| mutation_rate | pop 50 | pop 80 | pop 100 |
| :---: | :---: | :---: | :---: |
| 0.2 | 5/10 đạt tốt nhất (TB 787.22) | 7/10 (784.48) | 4/10 (794.82) |
| 0.5 | 8/10 (769.51) | 9/10 (770.45) | 9/10 (765.53) |
| 0.8 | **10/10 (761.55)** | 9/10 (765.53) | 9/10 (763.28) |

→ Bài nhỏ **hội tụ sớm**: đột biến cao giúp thoát điểm kẹt.

**Benchmark 50 điểm** (pop 100; Greedy = 4452.10 theo cùng thước đo):

| Cấu hình | 500 thế hệ | 1000 thế hệ | 2000 thế hệ |
| :--- | ---: | ---: | ---: |
| Khởi tạo ngẫu nhiên, mutation 0.2 | 4330.91 ± 174.45 | 4222.32 ± 176.19 | 4159.48 ± 172.05 |
| Khởi tạo ngẫu nhiên, mutation 0.5 | 4993.53 ± 161.60 | 4364.41 ± 105.75 | 4116.09 ± 96.96 |
| Khởi tạo từ Greedy, mutation 0.2 | 4017.25 ± 49.75 | 4002.31 ± 31.63 | 3983.65 ± 47.31 |
| Khởi tạo từ Greedy, mutation 0.5 | 4191.07 ± 58.23 | 4107.10 ± 75.75 | **3976.60 ± 68.10** |
| Khởi tạo từ Greedy, mutation 0.8 | - | - | 4092.21 ± 89.81 |

→ Bài lớn **chưa hội tụ** sau 500 thế hệ (đột biến cao làm chậm thêm). Khởi tạo từ Greedy vừa tốt hơn ~5% vừa ổn định hơn nhiều (độ lệch chuẩn ~170 → ~50).
→ Chọn `pop_size=100, mutation_rate=0.5, generations=2000` + khởi tạo từ Greedy: tốt nhất ở benchmark 50, và ở benchmark 10 (khởi tạo từ Greedy) đạt tốt nhất 10/10 seed, trong khi mutation 0.2 chỉ 1/10.

## 4. So sánh đầy đủ qua pipeline
Mỗi dòng GA thêm đúng một thay đổi so với dòng trên. Chạy bằng `ga_tuning.py compare`.

**Benchmark 10 điểm (K = 3)**

| Thuật toán | Quãng đường | Năng lượng | Phạt trễ giờ | Tổng chi phí | Hợp lệ | Thời gian (s) |
| :--- | ---: | ---: | ---: | ---: | :---: | ---: |
| Greedy + 2-Opt | 262.09 | 331.10 | 0.00 | 758.74 | 1/1 | 0.001 |
| GA cũ (80 thế hệ, 50 cá thể, mutation 0.2, phạt gốc) | 260.43 ± 7.73 | 335.71 ± 10.43 | 0.00 | 763.98 ± 22.17 | 5/5 | 0.045 |
| GA tinh chỉnh (100 cá thể, 2000 thế hệ, mutation 0.5, phạt ×100) | 250.40 ± 6.53 | 325.03 ± 9.35 | 0.00 | 737.95 ± 19.14 | 5/5 | 3.0 |
| + EnergyManager | 247.48 ± 0.00 | 309.73 ± 0.00 | 0.00 | 712.08 ± 0.00 | 5/5 | 6.0 |
| + khởi tạo từ Greedy (**đề xuất**) | 247.48 ± 0.00 | 309.73 ± 0.00 | 0.00 | **712.08 ± 0.00** | 5/5 | 6.0 |

**Benchmark 50 điểm (K = 14)**

| Thuật toán | Quãng đường | Năng lượng | Phạt trễ giờ | Tổng chi phí | Hợp lệ | Thời gian (s) |
| :--- | ---: | ---: | ---: | ---: | :---: | ---: |
| Greedy + 2-Opt | 1367.26 | 1728.98 | 216.88 | 4177.60 | 1/1 | 0.003 |
| GA cũ | 1865.75 ± 78.50 | 2451.76 ± 85.70 | 108.57 ± 64.06 | 5667.97 ± 269.25 | 4/5 | 0.20 |
| GA tinh chỉnh | 1380.02 ± 45.57 | 1818.64 ± 62.22 | 28.84 ± 26.27 | 4136.81 ± 105.55 | 5/5 | 14 |
| + EnergyManager | 1360.96 ± 55.27 | 1771.85 ± 58.42 | 30.33 ± 41.71 | 4049.07 ± 157.75 | 5/5 | 45 |
| + khởi tạo từ Greedy (**đề xuất**) | 1277.71 ± 29.91 | 1655.22 ± 29.41 | 49.86 ± 55.98 | **3810.39 ± 54.38** | 5/5 | 45 |

**Benchmark 100 điểm (K = 29)**

| Thuật toán | Quãng đường | Năng lượng | Phạt trễ giờ | Tổng chi phí | Hợp lệ | Thời gian (s) |
| :--- | ---: | ---: | ---: | ---: | :---: | ---: |
| Greedy + 2-Opt | 3767.92 | 4935.06 | 300.84 | 11471.35 | 1/1 | 0.025 |
| GA cũ | 6342.42 ± 180.41 | 8356.99 ± 312.36 | 1140.11 ± 345.77 | 21816.01 ± 1124.28 | 1/5 | 0.44 |
| GA tinh chỉnh | 4560.76 ± 223.40 | 5994.10 ± 341.90 | 312.51 ± 301.75 | 14464.42 ± 1197.55 | 5/5 | 64 |
| + EnergyManager | 4665.03 ± 210.42 | 6020.20 ± 213.44 | 183.13 ± 166.01 | 13878.46 ± 647.71 | 5/5 | 191 |
| + khởi tạo từ Greedy (**đề xuất**) | 3728.92 ± 29.08 | 4868.30 ± 40.80 | 198.71 ± 142.12 | **11230.08 ± 199.12** | 5/5 | 137 |

**Chênh lệch tổng chi phí so với Greedy + 2-Opt** (âm = GA tốt hơn):

| Biến thể GA | 10 điểm | 50 điểm | 100 điểm |
| :--- | ---: | ---: | ---: |
| GA cũ | +0.69% | +35.68% | +90.18% |
| GA tinh chỉnh | −2.74% | −0.98% | +26.09% |
| + EnergyManager | −6.15% | −3.08% | +20.98% |
| + khởi tạo từ Greedy | **−6.15%** | **−8.79%** | **−2.10%** |

## 5. Phân tích
1. **Cấu hình cũ của pipeline không đủ:** 80 thế hệ × 50 cá thể quá ít cho bài lớn, và phạt quá tải gốc (1000 / kg) quá nhẹ so với cost ~10⁴ nên GA trả lời giải quá tải nhẹ (validator báo không hợp lệ).
2. **Tinh chỉnh tham số** đủ cho bài nhỏ, nhưng ở 100 điểm GA khởi tạo ngẫu nhiên không kịp đuổi kịp Greedy trong 2000 thế hệ.
3. **EnergyManager:** năng lượng thật phụ thuộc **thứ tự giao** (tải giảm dần sau mỗi điểm), còn công thức ước lượng mặc định của fitness thì không. Khi GA được chấm bằng đúng mô hình của TV3, nó học giao gói nặng trước (benchmark 10: năng lượng 325 → 310 Wh).
4. **Khởi tạo từ Greedy** là yếu tố quyết định ở bài lớn: GA bắt đầu từ một lời giải tốt và (nhờ elitism) không bao giờ tệ hơn nó theo thước đo của GA; độ lệch chuẩn giảm mạnh (benchmark 100: ± 648 → ± 199).
5. **Cái giá:** thời gian chạy từ < 1 giây lên vài giây (10 điểm), ~45 giây (50 điểm) và ~2 phút (100 điểm).

## 6. Lỗi phát hiện & đã sửa trong quá trình thực nghiệm
| Vấn đề | Ảnh hưởng | Sửa (commit) |
| :--- | :--- | :--- |
| Phạt quá tải của fitness quá nhẹ ở quy mô lớn | Lời giải GA quá tải 0.02–0.39 kg, không hợp lệ | GA nhân phần phạt vi phạm ×100 khi chọn lọc; cost báo cáo giữ nguyên của TV5 (`9987897`) |
| GA chấm điểm tuyến **chưa** chèn trạm sạc, trong khi pipeline chèn sau GA | Ở benchmark 100, tuyến cần ghé trạm sạc bị phạt như cạn pin → GA chỉ ngang Greedy (+0.46%) | Có EnergyManager thì GA chấm điểm sau khi gọi `repair_route_with_charging` (`e61e77f`) → −2.10% |
| `EnergyManager.repair_route_with_charging` lặp vô hạn khi đứng ở trạm sạc pin đầy mà vẫn không tới được điểm kế | Treo / `MemoryError`; với cấu hình thật, 27/1000 cặp (trạm sạc → khách) ở benchmark 100 có thể gây lỗi khi chở 5 kg | Không chèn trạm sạc trùng điểm hiện tại, đánh dấu tuyến không khả thi (`8360f14`, file của TV3) |

## 7. Hạn chế
- Ở 100 điểm, GA chỉ tốt hơn Greedy 2.10% (độ lệch chuẩn ± 1.8%), cần nhiều thế hệ hơn hoặc thêm tìm kiếm cục bộ trong vòng lặp GA.
- Mỗi cấu hình chỉ 5 seed (quét tham số 10 seed); thời gian chạy ở benchmark 100 bị nhiễu do máy bận.
- Quét tham số dùng thước đo cũ của GA (chưa EnergyManager, phạt gốc); tham số được chọn trước khi có các bản sửa ở mục 6.
- Số Drone K được chọn theo quy tắc dư 20% sức chở; mô hình chưa hỗ trợ một Drone bay nhiều chuyến.

## 8. Đề xuất cho pipeline (`src/pipeline.py`, TV5)
1. `solve_ga` truyền `energy_manager=self.energy_manager` và `initial_solutions=[GreedyRouter(...).solve()]` cho `GeneticAlgorithm`.
2. `run_experiment` không cố định `generations=80, pop_size=50`; dùng mặc định mới của GA (100 cá thể, 2000 thế hệ) hoặc nhận từ tham số.
3. `main.py --benchmark 50/100` cần số Drone đủ chở (14 / 29), không dùng 3 mặc định.
4. Lỗi nhỏ: tiêu đề đường cong hội tụ dùng `len(nodes) - 1` nên đếm cả trạm sạc ("13 điểm" với benchmark 10).

## 9. Tái lập kết quả
```bash
python src/utils/benchmark_generator.py
python src/utils/ga_tuning.py sweep --scales 10 50 --seeds 10
python src/utils/ga_tuning.py sweep --scales 50 --pop-sizes 100 --mutation-rates 0.2 0.5 0.8 --generations 500 1000 2000 --seed-greedy
python src/utils/ga_tuning.py compare --scales 10 50 100 --seeds 5 --pop-size 100 --mutation-rate 0.5 --generations 2000
```
Lệnh `compare` mất khoảng 1 giờ trên máy thường (phần lớn ở benchmark 100).

## 10. Song song hóa đánh giá fitness (cập nhật 25/10/2026)
**Thiết kế** (`GeneticAlgorithm(num_workers=p)`): mỗi thế hệ, các cá thể chưa có trong cache (đã bỏ trùng) được chấm điểm trên `p` tiến trình (`multiprocessing.Pool`). Pool tạo một lần cho mỗi lần `evolve()`; dữ liệu bài toán (`nodes`, ma trận, `FitnessCalculator`, `EnergyManager`) gửi một lần qua `initializer`. Chọn lọc, lai ghép, đột biến vẫn chạy ở tiến trình chính, nên cùng seed thì mọi `p` cho **cùng lời giải và cùng history** (script kiểm tra điều này ở mọi dòng bên dưới).

**Thiết lập:**
- Dữ liệu `data/raw/benchmark_{10,50,100,500}.json` bản trên `develop` ngày 25/10. Khối lượng hàng đã đổi so với mục 2, nên K = 3 / 15 / 31 / 150.
- GA 100 cá thể × 200 thế hệ, seed 0. Mỗi cấu hình chạy 3 lần, lấy lần nhanh nhất.
- $T_p$ = `ga.runtime`, **gồm cả thời gian khởi động Pool**.
- Máy: Intel Core i5-13500H (4 nhân hiệu năng cao + 8 nhân tiết kiệm điện, 16 luồng), Windows 11, Python 3.14.
- Số liệu gốc: `data/processed/ga_speedup_results.csv`.

| Quy mô (độ dài chromosome) | EnergyManager | $T_1$ (s) | ms / thế hệ ($p$ = 1) | $S_2$ | $S_4$ | $S_8$ | $E_4$ |
| :---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 điểm (12) | không | 0.35 | 1.7 | 0.36x | 0.32x | 0.22x | 7.9% |
| 10 điểm (12) | có | 0.68 | 3.4 | 0.57x | 0.58x | 0.44x | 14.5% |
| 50 điểm (64) | không | 1.71 | 8.5 | 0.95x | 1.14x | 0.99x | 28.5% |
| 50 điểm (64) | có | 5.03 | 25.2 | 1.41x | **2.00x** | 2.13x | 50.0% |
| 100 điểm (130) | không | 3.37 | 16.9 | 1.23x | 1.64x | 1.50x | 41.0% |
| 100 điểm (130) | có | 13.64 | 68.2 | 1.66x | **2.60x** | 3.17x | 64.9% |
| 500 điểm (649) | không | 17.08 | 85.4 | 1.54x | **2.00x** | 1.72x | 50.0% |
| 500 điểm (649) | có | 167.32 | 836.6 | **1.85x** | **2.92x** | **3.80x** | 72.9% |

$S_p = T_1 / T_p$, $E_p = S_p / p$. Đậm: đạt tiêu chí của nhóm ($S \ge 1.8$).

**Phân tích:**
1. **Tăng tốc phụ thuộc chi phí chấm một cá thể.** Ở 500 điểm có EnergyManager, mỗi lần chấm tốn khoảng 8 ms (chèn trạm sạc cho 150 tuyến), nên 4 tiến trình đạt 2.92x và 8 tiến trình đạt 3.80x. Không có EnergyManager, mỗi lần chấm chỉ khoảng 1 ms, nên 4 tiến trình chỉ đạt 2.00x.
2. **Bài nhỏ chạy song song chậm hơn.** Ở 10 điểm, cả 200 thế hệ chỉ tốn 0.35–0.68 s, ít hơn thời gian khởi động Pool. Trên Windows, mỗi tiến trình con khởi động Python mới và nạp lại `pipeline` cùng matplotlib (~0.6 s; cả Pool 4 tiến trình ~2.5 s ở 500 điểm). Vì vậy nên để `num_workers=None` (tuần tự) khi N ≤ 50 và không dùng EnergyManager.
3. **Phần không song song được.** Chỉ số Karp-Flatt $e = (1/S_p - 1/p)/(1 - 1/p)$ ở 500 điểm có EnergyManager là 0.08 / 0.12 / 0.16 với p = 2 / 4 / 8. Phần này gồm khởi động Pool, chọn lọc + OX + đột biến ở tiến trình chính (~7 ms / thế hệ) và chi phí gửi chromosome giữa các tiến trình. $e$ tăng theo p, một phần vì chi phí khởi động Pool tăng theo số tiến trình, một phần do nhân tiết kiệm điện (mục 4).
4. **Từ 4 lên 8 tiến trình lợi ít.** Tiến trình thứ 5 trở đi chạy trên nhân tiết kiệm điện, chậm hơn. Ở 500 điểm không có EnergyManager, 8 tiến trình còn chậm hơn 4 tiến trình.
5. **Số đo trên là cận dưới.** Pipeline mặc định chạy 2000 thế hệ, gấp 10 lần ở đây, nên chi phí khởi động Pool (cố định) chiếm tỷ lệ nhỏ hơn nhiều và tăng tốc thực tế sẽ cao hơn. Đây là suy luận, chưa đo.

**Tái lập:**
```bash
python src/utils/ga_tuning.py speedup --scales 10 50 100 500 --workers 1 2 4 8 --generations 200 --repeats 3
```
Mất khoảng 25 phút; lần đầu chạy 500 điểm cần tính ma trận A* (~50 s với 8 tiến trình, sau đó dùng cache `data/processed/distance_matrix_500.pkl`).
