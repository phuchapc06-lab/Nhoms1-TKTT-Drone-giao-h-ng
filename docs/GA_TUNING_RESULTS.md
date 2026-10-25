# Tinh chỉnh & đánh giá Giải thuật Di truyền (GA)
**Phụ trách:** Thành viên 1 (GA Core Engine) · **Ngày:** 16/10/2026 · **Script:** `src/utils/ga_tuning.py`

> **Cập nhật 25/10/2026:** mục 1–9 đo trên dữ liệu benchmark ngày 16/10. Sau đó TV4 đã đổi khối lượng hàng. Số liệu trên dữ liệu hiện tại (10 / 50 / 100 / 500 điểm, có tỷ lệ đúng giờ và số tuyến thiếu pin) ở **mục 13** (số liệu chốt: EnergyManager mới của TV3, 2-Opt có kiểm tra chi phí, validator kiểm tra pin; mục 11–12 là các lần đo trước đó); Speedup song song ở **mục 10**.

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
> **Đo lại 25/10 tối** với EnergyManager mới của TV3 (`faea2f0`: Depot là điểm sạc, không lọc lại danh sách trạm sạc mỗi lần gọi). Mỗi thế hệ có EnergyManager nhanh hơn (500 điểm: 836.6 → 533.1 ms), còn tăng tốc giảm nhẹ (500 điểm: $S_4$ 2.92x → 2.84x, $S_8$ 3.80x → 3.45x) vì phần việc chia được nhẹ đi trong khi phần không chia được giữ nguyên (định luật Amdahl). Bảng dưới là số đo mới; mọi $p$ vẫn cho cùng lời giải và cùng history với chạy tuần tự.

| Quy mô (độ dài chromosome) | EnergyManager | $T_1$ (s) | ms / thế hệ ($p$ = 1) | $S_2$ | $S_4$ | $S_8$ | $E_4$ |
| :---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 điểm (12) | không | 0.33 | 1.6 | 0.34x | 0.30x | 0.22x | 7.5% |
| 10 điểm (12) | có | 0.65 | 3.3 | 0.57x | 0.57x | 0.43x | 14.3% |
| 50 điểm (64) | không | 1.70 | 8.5 | 0.92x | 1.13x | 0.89x | 28.2% |
| 50 điểm (64) | có | 4.64 | 23.2 | 1.35x | **1.90x** | **2.04x** | 47.4% |
| 100 điểm (130) | không | 3.30 | 16.5 | 1.21x | 1.60x | 1.56x | 40.0% |
| 100 điểm (130) | có | 11.46 | 57.3 | 1.58x | **2.38x** | **2.88x** | 59.6% |
| 500 điểm (649) | không | 16.77 | 83.8 | 1.49x | **1.93x** | 1.70x | 48.2% |
| 500 điểm (649) | có | 106.63 | 533.1 | 1.76x | **2.84x** | **3.45x** | 70.9% |

$S_p = T_1 / T_p$, $E_p = S_p / p$. Đậm: đạt tiêu chí của nhóm ($S \ge 1.8$).

**Phân tích:**
1. **Tăng tốc phụ thuộc chi phí chấm một cá thể.** Ở 500 điểm có EnergyManager, mỗi lần chấm tốn khoảng 5 ms (chèn trạm sạc cho 150 tuyến), nên 4 tiến trình đạt 2.84x và 8 tiến trình đạt 3.45x. Không có EnergyManager, mỗi lần chấm chỉ khoảng 1 ms, nên 4 tiến trình chỉ đạt 1.93x.
2. **Bài nhỏ chạy song song chậm hơn.** Ở 10 điểm, cả 200 thế hệ chỉ tốn 0.33–0.65 s, ít hơn thời gian khởi động Pool. Trên Windows, mỗi tiến trình con khởi động Python mới và nạp lại `pipeline` cùng matplotlib (~0.6 s; cả Pool 4 tiến trình ~2.5 s ở 500 điểm). Vì vậy nên để `num_workers=None` (tuần tự) khi N ≤ 50 và không dùng EnergyManager.
3. **Phần không song song được.** Chỉ số Karp-Flatt $e = (1/S_p - 1/p)/(1 - 1/p)$ ở 500 điểm có EnergyManager là 0.14 / 0.14 / 0.19 với p = 2 / 4 / 8 (đo với EnergyManager cũ: 0.08 / 0.12 / 0.16). Phần này gồm khởi động Pool, chọn lọc + OX + đột biến ở tiến trình chính (~7 ms / thế hệ) và chi phí gửi chromosome giữa các tiến trình. $e$ tăng theo p, một phần vì chi phí khởi động Pool tăng theo số tiến trình, một phần do nhân tiết kiệm điện (mục 4).
4. **Từ 4 lên 8 tiến trình lợi ít.** Tiến trình thứ 5 trở đi chạy trên nhân tiết kiệm điện, chậm hơn. Ở 500 điểm không có EnergyManager, 8 tiến trình còn chậm hơn 4 tiến trình.
5. **Số đo trên là cận dưới.** Pipeline mặc định chạy 2000 thế hệ, gấp 10 lần ở đây, nên chi phí khởi động Pool (cố định) chiếm tỷ lệ nhỏ hơn nhiều và tăng tốc thực tế sẽ cao hơn. Đây là suy luận, chưa đo.

**Tái lập:**
```bash
python src/utils/ga_tuning.py speedup --scales 10 50 100 500 --workers 1 2 4 8 --generations 200 --repeats 3
```
Mất khoảng 25 phút; lần đầu chạy 500 điểm cần tính ma trận A* (~50 s với 8 tiến trình, sau đó dùng cache `data/processed/distance_matrix_500.pkl`).

## 11. So sánh với Greedy trên dữ liệu hiện tại, 10–500 điểm (cập nhật 25/10/2026)
> Đo với `EnergyManager` trước commit `bb86a29` của TV3. Số liệu hiện hành ở **mục 12**. Cột "trước 2-Opt" ở mục này đếm theo cờ của `repair_route_with_charging` (tính cả tuyến chỉ xuống dưới ngưỡng 15%), khác thước đo của cột "Tuyến thiếu pin"; mục 12 đã thống nhất.

**Thiết lập:**
- Dữ liệu `data/raw/benchmark_{10,50,100,500}.json` bản trên `develop` ngày 25/10 (tổng hàng 10.5 / 61.9 / 125.7 / 623.2 kg). K = ⌈1.2 × tổng hàng / 5 kg⌉ = 3 / 15 / 31 / 150.
- Luồng đánh giá như mục 2: thuật toán → 2-Opt → chèn trạm sạc → `FitnessCalculator` → `DataContractValidator`. Không có dòng `[Pipeline] Chạy fallback GA` trong log.
- **GA đề xuất:** 100 cá thể, 2000 thế hệ, `mutation_rate=0.5`, phạt vi phạm ×100, có EnergyManager, khởi tạo từ Greedy.
- 10 điểm chạy tuần tự. 50 / 100 / 500 điểm chấm fitness trên 8 tiến trình (mục 10). Song song không đổi lời giải, chỉ đổi thời gian.
- Seed 0–4 (500 điểm: seed 0–2).
- Chạy 2 lần cùng seed: mọi cột trùng khớp, trừ thời gian (lệch tới ~30% do máy bận). Bảng dưới lấy lần 2.
- Cột mới **"Tuyến thiếu pin"**: số tuyến mà `EnergyManager` báo không bay hết được kể cả sau khi chèn trạm sạc. Validator không kiểm tra điều này, còn `FitnessCalculator` chỉ phạt 1000 cho mỗi tuyến.

| Quy mô | K | Greedy + 2-Opt | GA đề xuất (TB ± ĐLC) | Chênh lệch tổng chi phí | Đúng giờ Greedy → GA | Tuyến thiếu pin Greedy → GA | Thời gian GA (s) |
| :---: | :---: | ---: | ---: | :---: | :---: | :---: | ---: |
| 10 điểm | 3 | 749.02 | 706.50 ± 0.00 | **−5.68%** | 100.0% → 100.0% | 0 → 0 | 5.5 |
| 50 điểm | 15 | 4039.25 | 3851.10 ± 68.92 | **−4.66%** | 98.0% → 99.6% | 0 → 0 | 19.1 |
| 100 điểm | 31 | 13030.13 | 11768.55 ± 368.28 | **−9.68%** | 94.0% → 95.6% | **1 → 0** | 35.4 |
| 500 điểm | 150 | 95455.39 | 106080.99 ± 8024.58 | +11.13% | 93.8% → 92.2% | **6 → 1** | 298.3 |

Mọi lời giải đều được validator báo hợp lệ (tải trọng, mỗi khách đúng 1 lần, tuyến bắt đầu và kết thúc ở Depot).

**Thang cải tiến ở 10 / 50 / 100 điểm** (chênh lệch tổng chi phí so với Greedy, 5 seed; bảng đầy đủ in ra bởi lệnh ở cuối mục):

| Biến thể GA | 10 điểm | 50 điểm | 100 điểm |
| :--- | :---: | :---: | :---: |
| Cấu hình cũ của pipeline (80 thế hệ, 50 cá thể, phạt gốc) | −1.05% | +47.69% (3/5 hợp lệ) | +72.24% (0/5 hợp lệ) |
| Tham số tinh chỉnh | −2.31% | +4.23% | +8.84% |
| + EnergyManager | −5.68% | +4.01% | +6.86% |
| + khởi tạo từ Greedy (GA đề xuất) | **−5.68%** | **−4.66%** | **−9.68%** |

**Phân tích:**
1. **10–100 điểm:**
   - GA đề xuất rẻ hơn Greedy 4.7–9.7%, tỷ lệ đúng giờ cao hơn hoặc bằng, và không có tuyến thiếu pin. Ở 100 điểm, Greedy có 1 tuyến thiếu pin.
   - Khởi tạo từ Greedy là yếu tố quyết định ở 50 và 100 điểm. Không có nó, GA thua Greedy 4–7%.
2. **500 điểm: tổng chi phí của GA cao hơn 11.13%, nhưng Greedy vi phạm ràng buộc pin.**
   - **Greedy:** tổng chi phí 95455.39 = 29573.35 (quãng đường) + 1.5 × 39120.12 (năng lượng) + 1201.85 (trễ giờ) + **6000** (6 tuyến thiếu pin × 1000). 6 trên 150 Drone không bay hết được tuyến.
   - **Mức phạt quá nhẹ:** 1000 mỗi tuyến chỉ bằng ~1% tổng chi phí, nên Greedy vẫn "rẻ".
   - **Vì sao điểm khởi tạo không còn tác dụng:** khi chọn lọc, GA nhân phần phạt này lên 100 lần, nên chấm lời giải Greedy là 689455.39. Như vậy GA phải tự tìm từ đầu một lời giải đủ pin.
   - **GA:** trước 2-Opt, cả 3 seed đều không có tuyến thiếu pin, nhưng phải bay xa hơn 17.9% (34874 so với 29573).
   - **Không tính phạt pin:** Greedy 89455, GA 105081.
3. **2-Opt làm hỏng pin.**
   - Ở 500 điểm, lời giải GA có 0 tuyến thiếu pin trước 2-Opt và 1 tuyến sau 2-Opt, ở cả 3 seed.
   - 2-Opt (TV6) chỉ xét quãng đường, nên có thể đảo thứ tự giao khiến Drone chở nặng bay chặng xa.
   - Cũng vì chỉ xét quãng đường, 2-Opt có thể làm tăng tổng chi phí: Greedy ở 50 điểm có chi phí 4002.00 trước 2-Opt và 4039.25 sau 2-Opt.
4. **Hội tụ:**
   - Cost chọn lọc trung bình giảm trong 1/4 số thế hệ cuối: 0% / 0.55% / 1.92% / 1.21% ở 10 / 50 / 100 / 500 điểm.
   - Ở 100 và 500 điểm, GA chưa hội tụ sau 2000 thế hệ. Độ lệch chuẩn ở 500 điểm lớn (±7.6%), nên chạy thêm thế hệ sẽ còn cải thiện.
5. **Thời gian:** 500 điểm mất ~5 phút cho mỗi lần chạy GA với 8 tiến trình. Theo mục 10 ($S_8$ = 3.80), chạy tuần tự ước tính mất khoảng 19 phút (298 s × 3.80).

**Đề xuất cho nhóm (gửi TV5 / TV6, không tự sửa):**
1. `DataContractValidator` (TV5) kiểm tra thêm pin: tuyến mà `EnergyManager` báo không khả thi thì phải là không hợp lệ. Báo cáo cần có số tuyến thiếu pin.
2. Câu "100% lộ trình bay … đảm bảo mức pin an toàn" trong `BAO_CAO_TONG_KET_DE_TAI.md` §3 chỉ đúng tới 50 điểm. Ở 100 và 500 điểm, Greedy có 1 và 6 tuyến thiếu pin.
3. 2-Opt (TV6) hoặc pipeline chỉ nhận một bước đảo đoạn nếu tuyến vẫn đủ pin (hoặc tổng chi phí không tăng).

**Hạn chế:**
- 500 điểm chỉ chạy 3 seed và 2000 thế hệ.
- Thời gian chạy bị nhiễu do máy bận.
- Số Drone K chọn theo quy tắc dư 20% sức chở.

**Tái lập** (khoảng 45 phút):
```bash
python src/utils/ga_tuning.py compare --scales 10 --seeds 5 --pop-size 100 --mutation-rate 0.5 --generations 2000
python src/utils/ga_tuning.py compare --scales 50 100 --seeds 5 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8
python src/utils/ga_tuning.py compare --scales 500 --seeds 3 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8 --only-proposed
```

## 12. Chạy lại mục 11 với EnergyManager mới của TV3 (cập nhật 25/10/2026)
> Số liệu hiện hành ở **mục 13** (sau khi sửa 2-Opt và validator).

**Thay đổi so với mục 11:**
- `EnergyManager` sau commit `faea2f0` của TV3 (`develop` `0ae7a4a`): khi cần sạc, Drone có thể **ghé depot** như một trạm sạc; danh sách trạm sạc không còn lọc lại mỗi lần gọi. Ngưỡng 15% áp dụng khi bay tới điểm giao; khi tới depot / trạm sạc chỉ cần pin không âm.
- Sửa thước đo của `ga_tuning.py`: cột "trước 2-Opt" nay chèn trạm sạc rồi kiểm tra pin âm bằng `calculate_route_energy`, giống cột "Tuyến thiếu pin" và giống phép phạt của `FitnessCalculator`. Trước đây cột này dùng cờ của `repair_route_with_charging`, cờ đó còn báo cả tuyến chỉ xuống dưới 15% (vd. seed 0 ở 500 điểm: 2 tuyến về đích với 2.5% pin, không cạn).
- Dữ liệu, tham số, seed, số tiến trình giữ nguyên như mục 11. Không có dòng `[Pipeline] Chạy fallback GA` trong log.

| Quy mô | K | Greedy + 2-Opt | GA đề xuất (TB ± ĐLC) | Chênh lệch tổng chi phí | Đúng giờ Greedy → GA | Tuyến thiếu pin Greedy → GA | Thời gian GA (s) |
| :---: | :---: | ---: | ---: | :---: | :---: | :---: | ---: |
| 10 điểm | 3 | 749.02 | 706.50 ± 0.00 | **−5.68%** | 100.0% → 100.0% | 0 → 0 | 5.6 |
| 50 điểm | 15 | 4039.25 | 3806.67 ± 45.79 | **−5.76%** | 98.0% → 99.6% | 0 → 0 | 13.2 |
| 100 điểm | 31 | 12967.07 | 11742.24 ± 251.35 | **−9.45%** | 94.0% → 96.6% | **1 → 0** | 25.2 |
| 500 điểm | 150 | 95208.86 | 103140.25 ± 4089.89 | +8.33% | 93.8% → 93.3% | **6 → 0.7** | 176.1 |

Mọi lời giải đều được validator báo hợp lệ.

**Thang cải tiến** (chênh lệch tổng chi phí so với Greedy, 5 seed):

| Biến thể GA | 10 điểm | 50 điểm | 100 điểm |
| :--- | :---: | :---: | :---: |
| Cấu hình cũ của pipeline (80 thế hệ, 50 cá thể, phạt gốc) | −1.05% | +46.82% (3/5 hợp lệ) | +71.93% (0/5 hợp lệ) |
| Tham số tinh chỉnh | −2.31% | +4.23% | +8.79% |
| + EnergyManager | −5.68% | +6.78% | +8.17% |
| + khởi tạo từ Greedy (GA đề xuất) | **−5.68%** | **−5.76%** | **−9.45%** |

**So với mục 11:**
1. **10 điểm không đổi** (trùng mọi cột trừ thời gian): ở 10 điểm không tuyến nào cần ghé depot để sạc.
2. **50 / 100 điểm:** GA đề xuất vẫn rẻ hơn Greedy, mức chênh gần như cũ (−4.66% → −5.76%; −9.68% → −9.45%), độ lệch chuẩn nhỏ hơn. Greedy 100 điểm rẻ hơn một chút (13030.13 → 12967.07) nhờ được ghé depot để sạc, nhưng vẫn còn 1 tuyến thiếu pin.
3. **500 điểm:** GA vẫn đắt hơn Greedy, nhưng khoảng cách thu hẹp từ +11.13% xuống **+8.33%**, độ lệch chuẩn giảm một nửa (±8024.58 → ±4089.89). Greedy vẫn có **6 / 150 tuyến thiếu pin**: tổng chi phí 95208.86 = 29474.74 (quãng đường) + 1.5 × 39021.51 (năng lượng) + 1201.85 (trễ giờ) + 6000 (phạt pin). Lý do điểm khởi tạo Greedy mất tác dụng giữ nguyên như mục 11.
4. **2-Opt vẫn làm hỏng pin:** lời giải GA có **0 tuyến cạn pin trước 2-Opt ở cả 3 seed**; sau 2-Opt seed 0 có 2 tuyến cạn pin (pin xuống −44% và −62% của dung lượng), seed 1 và 2 không có.
5. **Hội tụ:** cost chọn lọc trung bình giảm trong 1/4 số thế hệ cuối: 0% / 0.77% / 1.57% / 0.88% ở 10 / 50 / 100 / 500 điểm; 100 và 500 điểm vẫn chưa hội tụ hẳn.
6. **Thời gian GA giảm 30–40%** ở 50 / 100 / 500 điểm (19.1 → 13.2 s, 35.4 → 25.2 s, 298.3 → 176.1 s) do `repair_route_with_charging` mới không lọc lại danh sách trạm sạc. Mục 10 đã đo lại với bản mới.

**Tái lập** (khoảng 20 phút): cùng 3 lệnh như mục 11.

## 13. Số liệu chốt: 2-Opt có kiểm tra chi phí, validator kiểm tra pin (cập nhật 25/10/2026)
**Thay đổi so với mục 12** (commit `9f7a51d`, `2024e7c`; user được nhóm cho phép sửa code TV5 / TV6):
- **2-Opt có kiểm tra chi phí:** `apply_2opt_to_solution(solution, dist, route_cost)` chỉ giữ tuyến sau 2-Opt nếu chi phí tuyến (sau khi chèn trạm sạc, gồm năng lượng, trễ giờ, phạt pin) không tăng. Pipeline và `BenchmarkEvaluator` truyền `UAVRoutingPipeline.route_cost_after_charging`. Lý do: mục 11–12 cho thấy 2-Opt (chỉ xét quãng đường) làm Greedy đắt hơn so với không chạy 2-Opt ở 50 / 100 / 500 điểm, và làm 2 tuyến GA ở 500 điểm cạn pin.
- **Validator kiểm tra pin:** tuyến mà `EnergyManager.calculate_route_energy` báo cạn pin là không hợp lệ (ràng buộc 4.2 của `Mathematical_Model.md`). Lần chạy 500 điểm dùng validator mới; ở 10 / 50 / 100 điểm cột "Hợp lệ" dưới đây tính lại từ cột "Tuyến thiếu pin" (cùng phép kiểm tra).
- GA không đổi (2-Opt và chèn trạm sạc chạy sau GA): đường hội tụ trùng mục 12.

| Quy mô | K | Greedy + 2-Opt | Hợp lệ (Greedy) | GA đề xuất (TB ± ĐLC) | Hợp lệ (GA) | Chênh lệch tổng chi phí | Đúng giờ Greedy → GA | Tuyến thiếu pin Greedy → GA | Thời gian GA (s) |
| :---: | :---: | ---: | :---: | ---: | :---: | :---: | :---: | :---: | ---: |
| 10 điểm | 3 | 749.02 | 1/1 | 706.50 ± 0.00 | 5/5 | **−5.68%** | 100.0% → 100.0% | 0 → 0 | 5.8 |
| 50 điểm | 15 | 4001.64 | 1/1 | 3796.41 ± 45.36 | 5/5 | **−5.13%** | 98.0% → 99.2% | 0 → 0 | 13.9 |
| 100 điểm | 31 | 12857.92 | **0/1** | 11683.20 ± 187.89 | 5/5 | **−9.14%** | 94.0% → 97.6% | **1 → 0** | 25.4 |
| 500 điểm | 150 | 94417.74 | **0/1** | 101722.04 ± 3169.24 | 3/3 | +7.74% | 95.0% → 94.5% | **6 → 0** | 180.3 |

**Thang cải tiến** (chênh lệch tổng chi phí so với Greedy, 5 seed):

| Biến thể GA | 10 điểm | 50 điểm | 100 điểm |
| :--- | :---: | :---: | :---: |
| Cấu hình cũ của pipeline (80 thế hệ, 50 cá thể, phạt gốc) | −1.05% | +48.17% (3/5 hợp lệ) | +70.67% (0/5 hợp lệ) |
| Tham số tinh chỉnh | −2.31% | +5.14% | +9.02% |
| + EnergyManager | −5.68% | +7.38% | +8.27% |
| + khởi tạo từ Greedy (GA đề xuất) | **−5.68%** | **−5.13%** | **−9.14%** |

**Phân tích:**
1. **Kiểm tra chi phí giúp cả hai thuật toán:** Greedy 50 / 100 / 500 điểm giảm 4039.25 → 4001.64, 12967.07 → 12857.92, 95208.86 → 94417.74; GA 500 điểm giảm 103140.25 → 101722.04 và hết tuyến cạn pin (0.7 → 0 tuyến trung bình). 10 điểm không đổi (không bước 2-Opt nào bị bỏ).
2. **10–100 điểm:** GA đề xuất rẻ hơn Greedy 5.1–9.1%, tỷ lệ đúng giờ cao hơn hoặc bằng. Ở 100 điểm, lời giải Greedy **không hợp lệ** (1 Drone cạn pin), mọi lời giải GA hợp lệ.
3. **500 điểm: chỉ GA cho lời giải hợp lệ.** Greedy rẻ hơn 7.74% nhưng 6 / 150 Drone cạn pin giữa đường (phạt 6000 trong tổng chi phí; bỏ phạt thì Greedy 88417.74). GA hợp lệ ở cả 3 seed, đổi lại bay xa hơn 15.9% (34049 so với 29370 km). GA chưa hội tụ sau 2000 thế hệ (1/4 cuối còn giảm 0.88%).
4. Kết luận "GA ≤ Greedy" chỉ nên phát biểu trên các lời giải hợp lệ: ở mọi quy mô, GA cho chi phí thấp hơn mọi lời giải Greedy hợp lệ, và ở 100 / 500 điểm Greedy không có lời giải hợp lệ.

**Tái lập** (khoảng 20 phút): cùng 3 lệnh như mục 11.
