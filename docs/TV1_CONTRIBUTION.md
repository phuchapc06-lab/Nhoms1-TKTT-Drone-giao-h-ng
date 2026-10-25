# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL CONTRIBUTION REPORT)
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP)
**Sinh viên thực hiện:** Nguyễn Hải Anh  
**Vai trò:** Thành viên 1 — Lập trình Giải thuật Di truyền (GA Core Engine)  
**Tài khoản GitHub:** `Sieqhart262`  
**Pull Request:** #3 (`feature/tv1-ga-core`), #7 (`feature/tv1-ga-tuning`) và #8 (`feature/tv1-contribution`) đã được Nhóm trưởng (TV5) review và merge; tuần 5–6: #11 (`feature/tv1-ga-parallel`) và #12 (`feature/tv1-bao-cao-n20-50`)  

---

## 📌 TỔNG QUAN PHẦN VIỆC ĐÃ ĐÓNG GÓP

Là thành viên phụ trách Giải thuật Di truyền, em (Nguyễn Hải Anh) đã thiết kế và lập trình toàn bộ module GA tìm cách chia đơn hàng và thứ tự giao hàng cho đội K Drone: biểu diễn nhiễm sắc thể, toán tử di truyền, vòng lặp tiến hóa và bộ kiểm thử. Sau mốc tích hợp Ngày 4, em kiểm chứng GA trong pipeline của nhóm, rồi tinh chỉnh tham số và cải tiến thuật toán qua thực nghiệm trên 3 quy mô dữ liệu.

**Kết quả chính** (tổng chi phí theo `FitnessCalculator` của TV5, thấp hơn là tốt hơn; GA lấy trung bình 5 seed):

| Quy mô | Greedy + 2-Opt (TV6) | GA trước tinh chỉnh | GA sau tinh chỉnh |
| :---: | ---: | ---: | ---: |
| 10 điểm giao (K = 3) | 758.74 | 763.98 (kém 0.69%) | **712.08 (tốt hơn 6.15%)** |
| 50 điểm giao (K = 14) | 4177.60 | 5667.97 (kém 35.68%, 1/5 lời giải không hợp lệ) | **3810.39 (tốt hơn 8.79%)** |
| 100 điểm giao (K = 29) | 11471.35 | 21816.01 (kém 90.18%, 4/5 lời giải không hợp lệ) | **11230.08 (tốt hơn 2.10%)** |

Mọi lời giải của GA sau tinh chỉnh đều hợp lệ (5/5 ở cả 3 quy mô). Từ commit `7a24f57` (Ngày 5), pipeline chính của nhóm chạy GA theo đúng cấu hình này.

> **Cập nhật tuần 5–6 (25/10/2026):** bảng trên đo trên dữ liệu benchmark ngày 16/10. Sau khi TV4 đổi khối lượng hàng, em chạy lại trên 10 / 50 / 100 / 500 điểm: GA đề xuất rẻ hơn Greedy **5.68% / 4.66% / 9.68%** ở 10 / 50 / 100 điểm. Ở 500 điểm, GA đắt hơn 11.13% nhưng lời giải Greedy có 6/150 tuyến thiếu pin. Em cũng song song hóa GA, đạt tăng tốc **3.80 lần** với 8 tiến trình ở 500 điểm. Chi tiết ở mục 10.

---

### 1. Thiết kế Biểu diễn Nhiễm sắc thể (Chromosome Encoding & Decoding)
- **File mã nguồn:** `src/algorithms/genetic_algorithm.py`
- **Class chính:** `GeneticAlgorithm` (các hàm `decode()`, `encode()`, `_random_chromosome()`, `_init_population()`)
- **Nội dung thực hiện:**
  - Chromosome là một hoán vị gồm N mã khách hàng xen K − 1 **vách ngăn** mang số âm $-1, -2, \dots, -(K-1)$, độ dài $L = N + K - 1$. Mỗi đoạn nằm giữa hai vách ngăn là tuyến bay của một Drone. Mã khách hàng là số dương (Depot là 0) nên vách ngăn không bao giờ trùng với khách. Ví dụ với K = 3:
    `[3, 1, -1, 5, 2, -2, 4]` → `[[0, 3, 1, 0], [0, 5, 2, 0], [0, 4, 0]]`
  - **Lý do chọn cách mã hóa này:** mọi hoán vị đều giải mã ra một lời giải đúng Data Contract: mỗi khách được giao đúng 1 lần, không quá K tuyến, mọi tuyến xuất phát và quay về Depot 0. Nhờ vậy GA dùng nguyên được các toán tử hoán vị chuẩn (OX, Swap) mà không cần bước sửa lời giải. Các vách ngăn là những số âm khác nhau nên OX coi chúng như gen bình thường và không bao giờ sinh gen trùng.
  - Hai vách ngăn liền nhau, hoặc vách ngăn ở đầu hay cuối dãy, tạo ra tuyến rỗng và bị bỏ qua. Vì vậy GA tự quyết định số Drone thực sự cần bay (không quá K).
  - Chỉ điểm giao hàng (`type == "delivery"`) nằm trong chromosome. Depot và trạm sạc bị loại ra; trạm sạc do `EnergyManager` của TV3 chèn vào sau. Tải trọng không được mã hóa trực tiếp: quá tải là ràng buộc mềm, bị hàm fitness phạt (mục 3).
  - `encode()` là chiều ngược của `decode()`: bỏ qua Depot và trạm sạc trong tuyến, kiểm tra lời giải không quá K tuyến và giao mỗi khách đúng 1 lần. Hàm này cho phép đưa lời giải Greedy của TV6 vào quần thể ban đầu (mục 7).
  - **Kích thước không gian tìm kiếm:** có $(N+K-1)!\,/\,(K-1)!$ chromosome khác nhau (không tính việc đổi nhãn các vách ngăn), tức khoảng $2.4 \times 10^{8}$ với 10 điểm, $3.2 \times 10^{77}$ với 50 điểm và $1.3 \times 10^{186}$ với 100 điểm. Không thể duyệt toàn bộ, nên cần một meta-heuristic như GA.

---

### 2. Cài đặt các Toán tử Di truyền (Genetic Operators)
- **Hàm chính:** `_tournament_select()`, `_order_crossover()`, `_swap_mutation()`
- **Nội dung thực hiện:**
  - **Chọn lọc Tournament** (`tournament_size = 3`): lấy ngẫu nhiên 3 cá thể khác nhau, giữ cá thể có fitness cao nhất.
  - **Lai ghép thứ tự (Order Crossover - OX)**, xác suất `crossover_rate = 0.9`: chép nguyên đoạn $[a, b]$ của cha 1 sang con; các vị trí còn lại điền gen của cha 2 theo thứ tự xuất hiện, bắt đầu từ vị trí $b + 1$ và vòng lại đầu dãy, bỏ qua gen đã có. Con luôn là hoán vị hợp lệ, không trùng hay thiếu đơn hàng và vách ngăn. Ví dụ với đoạn từ vị trí 3 đến 6 (đánh số từ 0): `[1,2,3,4,5,6,7,8,9]` × `[9,3,7,8,2,6,5,1,4]` → `[3,8,2,4,5,6,7,1,9]`.
  - **Đột biến hoán đổi (Swap Mutation)**, xác suất `mutation_rate`: đổi chỗ 2 gen ngẫu nhiên và trả về bản sao mới (không sửa cá thể cha). Với cách mã hóa vách ngăn, một phép Swap có thể đổi thứ tự giao trong một tuyến, đổi khách giữa hai tuyến, hoặc dời vách ngăn để chuyển khách sang tuyến khác.
  - **Elitism** (`elitism = 2`): 2 cá thể tốt nhất được giữ nguyên sang thế hệ sau, nên lời giải tốt nhất không bao giờ bị mất.

---

### 3. Đánh giá Độ thích nghi & Vòng lặp Tiến hóa (Fitness Evaluation & Evolution Loop)
- **Hàm chính:** `_evaluate()`, `_next_generation()`, `evolve()`
- **Nội dung thực hiện:**
  - **Đánh giá một cá thể:** giải mã chromosome → nếu có `EnergyManager` thì chèn trạm sạc vào từng tuyến bằng `repair_route_with_charging` (TV3) → tính chi phí bằng `FitnessCalculator.evaluate_solution` (TV5). Khi chọn lọc, phần phạt vi phạm ràng buộc cứng (quá tải, cạn pin) được nhân thêm hệ số $\lambda$ = `constraint_penalty_factor` (mặc định 100):
    $$\text{Fitness}_{GA} = \frac{1000}{\text{Cost} + (\lambda - 1) \cdot \text{Phạt}_{\text{quá tải, cạn pin}} + 1}$$
    Với lời giải hợp lệ, hoặc khi $\lambda = 1$, công thức này trùng đúng fitness $1000 / (\text{Cost} + 1)$ của TV5. Chi phí trả về (`best_cost`, `best_breakdown`) vẫn là số gốc của TV5 để báo cáo.
  - **Bộ nhớ đệm (cache)** theo `tuple(chromosome)`: cá thể ưu tú và các bản sao không bị tính lại. Cache chỉ giữ quần thể hiện tại nên bộ nhớ không tăng theo số thế hệ.
  - **Vòng lặp tiến hóa** `evolve()` (mã giả bên dưới) trả về `(best_solution, best_fitness, history)`, sau khi chạy có thêm `best_cost`, `best_breakdown` và `runtime`. `history` là fitness tốt nhất tính đến từng thế hệ (không giảm nhờ elitism), dùng trực tiếp cho `UAVVisualizer.plot_convergence_curve` của TV5.
  - **Tái lập được:** GA dùng bộ sinh số ngẫu nhiên riêng `random.Random(seed)`, không gọi `random.seed` hay `np.random.seed` toàn cục, nên không ảnh hưởng và không bị ảnh hưởng bởi module khác. Cùng seed cho cùng kết quả.
  - Kiểm tra tham số đầu vào (K ≥ 1, `pop_size` ≥ 2, các xác suất nằm trong [0, 1], ...) và báo lỗi rõ ràng.

```text
evolve():
    P ← lời giải có sẵn (nếu có) + cá thể ngẫu nhiên cho đủ pop_size
    với mỗi thế hệ g = 1..G:
        nếu g > 1: P ← THẾ_HỆ_MỚI(P)
        đánh giá mọi cá thể của P (dùng cache); cập nhật lời giải tốt nhất; ghi fitness tốt nhất vào history
    trả về (lời giải tốt nhất, fitness của nó, history)

THẾ_HỆ_MỚI(P):
    P' ← 2 cá thể tốt nhất của P                                  # elitism
    trong khi |P'| < pop_size:
        cha1, cha2 ← TOURNAMENT(P), TOURNAMENT(P)
        con ← OX(cha1, cha2) với xác suất 0.9, ngược lại con ← bản sao cha1
        thêm SWAP(con) vào P'
    trả về P'
```

---

### 4. Phân tích Độ phức tạp (Complexity Analysis)
Ký hiệu: N là số điểm giao hàng, K là số Drone, $L = N + K - 1$ là độ dài chromosome, P là kích thước quần thể, G là số thế hệ, C là số trạm sạc. Ma trận khoảng cách đã được TV2 tính trước nên mỗi lần tra khoảng cách tốn O(1).

| Thao tác | Độ phức tạp | Giải thích |
| :--- | :---: | :--- |
| `decode()`, `encode()` | O(L) | Duyệt chromosome một lần |
| Đánh giá 1 cá thể, không có EnergyManager | O(N + K) | Tổng số chặng bay của mọi tuyến không quá N + K, mỗi chặng tra ma trận O(1) |
| Đánh giá 1 cá thể, có EnergyManager | O((N + K) · C) | Thêm bước chèn trạm sạc: chặng nào thiếu pin thì xét cả C trạm sạc (trường hợp xấu nhất: mọi chặng) |
| Tournament | O(t) | t = 3 cá thể |
| OX | O(L) | Chép đoạn và điền một lượt từ cha 2; kiểm tra gen đã dùng bằng `set` trong O(1) |
| Swap | O(L) | Đổi chỗ O(1), tạo bản sao O(L) |
| Chọn cá thể ưu tú | O(P log P) | Sắp xếp quần thể theo fitness |
| **Một thế hệ** | **O(P · L + P log P)** | P lần chọn lọc, lai ghép, đột biến và đánh giá (có EnergyManager: O(P · L · C + P log P)) |
| **Toàn bộ GA** | **O(G · P · (L + log P))** | Vì K < N, và thực tế bước sắp xếp rẻ hơn nhiều so với P lần đánh giá, nên xấp xỉ **O(G · P · N)** |

- **Bộ nhớ:** O(P · L) cho quần thể và cache, chưa kể ma trận khoảng cách $O(M^2)$ của TV2 (M là tổng số node).
- **So với duyệt toàn bộ:** với mặc định P = 100, G = 2000, GA đánh giá không quá $P \cdot G = 2 \times 10^5$ cá thể, trong khi không gian tìm kiếm ở 100 điểm có khoảng $10^{186}$ chromosome.

**Kiểm chứng bằng đo thời gian thực tế** (P = 100, 200 thế hệ, lấy lần nhanh nhất trong 3 seed; đo ngày 18/10/2026):

| Quy mô | L | C | Thời gian / thế hệ, không EnergyManager | Thời gian / thế hệ, có EnergyManager |
| :---: | :---: | :---: | ---: | ---: |
| 10 điểm (K = 3) | 12 | 3 | 1.53 ms | 2.82 ms |
| 50 điểm (K = 14) | 63 | 6 | 7.19 ms | 22.27 ms |
| 100 điểm (K = 29) | 128 | 10 | 13.85 ms | 62.29 ms |

- Từ 50 lên 100 điểm, L tăng ×2.03 và thời gian mỗi thế hệ (không EnergyManager) tăng ×1.93: đúng bậc tuyến tính theo L.
- Có EnergyManager, thời gian tăng nhanh hơn (×2.80) vì số trạm sạc C cũng tăng từ 6 lên 10, khớp với số hạng O((N + K) · C).
- Ở 10 điểm, quần thể hội tụ nhanh nên nhiều cá thể trùng nhau: chỉ 53% lượt đánh giá phải tính thật, phần còn lại lấy từ cache. Ở 50 và 100 điểm, con số này là 90%.

---

### 5. Kiểm thử Tự động & Kiểm chứng Tính đúng (Unit Testing & Verification)
- **File test:** `tests/test_ga.py`, gồm 11 bài test trên dữ liệu giả lập (8 điểm giao hàng, 1 trạm sạc, ma trận khoảng cách Euclid):

| # | Bài test | Nội dung kiểm tra |
| :---: | :--- | :--- |
| 1 | `test_init_and_validation` | Chỉ lấy điểm giao hàng, tạo đúng K − 1 vách ngăn, báo lỗi khi tham số sai |
| 2 | `test_decode` | Giải mã đúng; bỏ tuyến rỗng khi vách ngăn ở đầu, cuối hoặc liền nhau |
| 3 | `test_random_population` | Cá thể ngẫu nhiên hợp lệ, không chứa trạm sạc, tái lập được theo seed |
| 4 | `test_evaluate` | Chi phí khớp `FitnessCalculator` của TV5; hệ số phạt; cache |
| 5 | `test_tournament_select` | Tournament ưu tiên cá thể tốt |
| 6 | `test_order_crossover` | Ví dụ OX chuẩn; 200 lần lai ngẫu nhiên luôn ra hoán vị hợp lệ |
| 7 | `test_swap_mutation` | Đổi đúng 2 vị trí, không sửa cá thể cha |
| 8 | `test_evolve` | Mỗi khách đúng 1 lần, không quá K tuyến, `history` không giảm, hết quá tải, kết nối được Visualizer; trường hợp K = 1 |
| 9 | `test_seed_reproducible` | Cùng seed cho cùng lời giải và `history` |
| 10 | `test_encode_and_initial_solutions` | `encode()` ngược với `decode()`; GA khởi tạo từ lời giải có sẵn không bao giờ tệ hơn lời giải đó |
| 11 | `test_energy_manager_with_charging` | Chấm điểm sau khi chèn trạm sạc; kiểm thử hồi quy lỗi lặp vô hạn của `repair_route_with_charging` (mục 9) |

- **Kết quả kiểm thử:** **11/11 Passed** (khoảng 5 giây).
- **Kiểm chứng bằng lời giải tối ưu thật:** trên dữ liệu giả lập (8 khách, K = 3), em duyệt toàn bộ 1 814 400 lời giải và xác định tối ưu thật có cost **792.80**. So sánh GA với con số này, em phát hiện GA **hội tụ sớm**: với tham số ban đầu (80 cá thể, 300 thế hệ, `mutation_rate = 0.2`), chỉ 16/20 seed đạt tối ưu, có seed kẹt ở 839.25 (kém 5.9%) ngay từ thế hệ 4–11; tăng `mutation_rate` lên 0.8 thì đạt 20/20. Với tham số mặc định cuối cùng (100 cá thể, 2000 thế hệ, `mutation_rate = 0.5`), GA đạt tối ưu ở **19/20 seed**, seed còn lại kém tối ưu 3.2%.
- **Trường hợp biên kiểm tra khi tích hợp:**
  - Cặp điểm không tới được (`dist = inf`): GA không crash, nhưng chỉ cần 1 ô `inf` là mọi lời giải có fitness 0 và GA tìm kiếm như ngẫu nhiên. Em đã báo nhóm; hiện dữ liệu benchmark không có cặp nào không tới được và pipeline thay `inf` bằng khoảng cách Euclid × 2.
  - Trạm sạc không bao giờ nằm trong chromosome.
  - K = 1 (không có vách ngăn) vẫn chạy đúng.

---

### 6. Kiểm chứng Tích hợp Hệ thống Ngày 4 (Integration Milestone Verification)
- TV5 ghép `GeneticAlgorithm` vào `src/pipeline.py`. Em chạy lại toàn bộ test trên `develop` và kiểm tra log không có dòng `[Pipeline] Chạy fallback GA`, vì pipeline sẽ âm thầm chạy bản GA dự phòng nếu module GA thật bị lỗi.
- Trên `benchmark_10.json`, GA có cost 734.91, tốt hơn Greedy (758.74) 3.1%; cả hai đều đã qua 2-Opt và chèn trạm sạc.
- Em phát hiện 3 vấn đề, dùng làm đầu vào cho giai đoạn tinh chỉnh:
  - `run_experiment` cố định 80 thế hệ × 50 cá thể; đường hội tụ trên benchmark 10 đứng yên từ thế hệ 23.
  - `solve_ga` không truyền `EnergyManager`, nên GA tối ưu theo năng lượng ước lượng $d \cdot (1 + 0.1 \cdot \text{tổng tải của tuyến})$, trong khi kết quả cuối được chấm theo mô hình của TV3 $d \cdot (1 + 0.15 \cdot \text{tải hiện tại})$, với tải giảm dần sau mỗi điểm giao.
  - Tiêu đề đường hội tụ đếm cả trạm sạc ("13 điểm" thay vì 10).

---

### 7. Tinh chỉnh Tham số & Cải tiến Thuật toán (Parameter Tuning & Algorithm Improvements)
- **File mã nguồn:** `src/utils/ga_tuning.py` (script thực nghiệm), `src/algorithms/genetic_algorithm.py`
- **Báo cáo chi tiết:** `docs/GA_TUNING_RESULTS.md`
- **Nội dung thực hiện:**
  - **Script thực nghiệm** có 2 lệnh: `sweep` quét `pop_size` × `mutation_rate` × số thế hệ (10 seed mỗi cấu hình); `compare` chạy Greedy và các biến thể GA qua **đúng** `run_experiment` của pipeline (thuật toán → 2-Opt → chèn trạm sạc → chấm điểm → validator). Script kiểm tra pipeline thật sự dùng `GreedyRouter` của TV6 (không rơi vào bản dự phòng) và cố định cấu hình "GA cũ" để so sánh trước/sau một cách trung thực.
  - **Chọn số Drone:** mô hình cho mỗi Drone bay 1 chuyến với tải tối đa 5 kg. Benchmark 50 và 100 có 56.4 kg và 117.5 kg hàng nên 3 Drone mặc định không thể chở hết. Em chọn $K = \lceil 1.2 \times \text{tổng khối lượng hàng} / 5 \rceil$, tức K = 3 / 14 / 29 (dư 20% sức chở).
  - **Quét tham số** cho thấy hai vấn đề ngược nhau: bài 10 điểm **hội tụ sớm** (`mutation_rate = 0.8` đạt kết quả tốt nhất ở 10/10 seed, 0.2 chỉ 4–7/10), còn bài 50 điểm **chưa hội tụ** sau 500 thế hệ (0.2 tốt nhất, 0.8 kém nhất). Khi tăng lên 2000 thế hệ và khởi tạo từ Greedy, `mutation_rate = 0.5` cho kết quả tốt nhất ở 50 điểm (3976.60 ± 68.10) và đạt tốt nhất 10/10 seed ở 10 điểm (0.2 chỉ 1/10). Vì vậy em chọn tham số mặc định mới: `pop_size = 100`, `generations = 2000`, `mutation_rate = 0.5`.
  - **Các cải tiến thuật toán**, mỗi cải tiến một commit. Khi tắt (`initial_solutions=None`, `constraint_penalty_factor=1`), GA cho kết quả y hệt bản cũ:

| Cải tiến | Vấn đề được giải quyết | Commit |
| :--- | :--- | :---: |
| Khởi tạo quần thể từ lời giải Greedy (`encode()` + tham số `initial_solutions`) | Ở bài lớn, GA khởi tạo ngẫu nhiên không kịp đuổi kịp Greedy. Ở 50 điểm (1000 thế hệ, `mutation_rate = 0.2`), cost giảm từ 4222 ± 176 xuống 4002 ± 32 | `29a49fe` |
| Tham số mặc định mới (100 cá thể, 2000 thế hệ, `mutation_rate = 0.5`) | Cấu hình cũ quá ít thế hệ và dễ hội tụ sớm | `29a49fe` |
| Nhân phần phạt vi phạm ràng buộc với λ = 100 khi chọn lọc | Mức phạt quá tải gốc (1000 cho mỗi kg) quá nhẹ so với cost cỡ 10⁴, nên GA trả về lời giải quá tải 0.02–0.39 kg và validator báo không hợp lệ | `9987897` |
| Chấm điểm tuyến **sau** khi chèn trạm sạc (khi có EnergyManager) | Tuyến cần ghé trạm sạc bị phạt như cạn pin, dù pipeline sẽ chèn trạm sạc sau GA | `e61e77f` |

- **Quá trình cải tiến ở quy mô 100 điểm** cho thấy vì sao phải lặp lại vòng "đo → tìm nguyên nhân → sửa":
  1. Lần so sánh đầu tiên, GA đầy đủ tốt hơn Greedy 1.80%, nhưng chỉ 2/5 lời giải hợp lệ (quá tải nhẹ).
  2. Sau khi thêm hệ số phạt: 5/5 lời giải hợp lệ, nhưng GA lại kém Greedy 0.46%.
  3. Giả thuyết ban đầu là do bước 2-Opt, nhưng số đo bác bỏ giả thuyết này. Đo tiếp thì thấy lời giải Greedy có 2/29 tuyến cần ghé trạm sạc, mà thước đo của GA lại phạt mọi tuyến như vậy như cạn pin. GA bị ép tìm tuyến không cần sạc, khắt khe hơn cách chấm điểm cuối cùng.
  4. Sau khi GA chấm điểm tuyến đã chèn trạm sạc: **tốt hơn Greedy 2.10%, 5/5 lời giải hợp lệ**.

---

### 8. Kết quả Thực nghiệm (Experimental Results)
- **Thiết lập:** dữ liệu `benchmark_{10,50,100}.json` sinh bằng bộ sinh của TV4 (seed 100); ma trận khoảng cách A* của TV2; K = 3 / 14 / 29; Greedy tất định chạy 1 lần, GA chạy 5 seed (0–4). Mọi thuật toán đi qua cùng một luồng: thuật toán → 2-Opt (TV6) → chèn trạm sạc (TV3) → `FitnessCalculator` có `EnergyManager` (TV5) → `DataContractValidator` (TV5).
- **GA đề xuất** = tham số tinh chỉnh + phạt vi phạm ×100 + chấm điểm có EnergyManager (sau khi chèn trạm sạc) + khởi tạo từ Greedy.

| Quy mô | Thuật toán | Quãng đường | Năng lượng | Phạt trễ giờ | Tổng chi phí | Hợp lệ | Thời gian (s) |
| :---: | :--- | ---: | ---: | ---: | ---: | :---: | ---: |
| 10 điểm | Greedy + 2-Opt | 262.09 | 331.10 | 0.00 | 758.74 | 1/1 | 0.001 |
| 10 điểm | GA đề xuất | 247.48 ± 0.00 | 309.73 ± 0.00 | 0.00 | **712.08 ± 0.00** | 5/5 | 6.0 |
| 50 điểm | Greedy + 2-Opt | 1367.26 | 1728.98 | 216.88 | 4177.60 | 1/1 | 0.003 |
| 50 điểm | GA đề xuất | 1277.71 ± 29.91 | 1655.22 ± 29.41 | 49.86 ± 55.98 | **3810.39 ± 54.38** | 5/5 | 45 |
| 100 điểm | Greedy + 2-Opt | 3767.92 | 4935.06 | 300.84 | 11471.35 | 1/1 | 0.025 |
| 100 điểm | GA đề xuất | 3728.92 ± 29.08 | 4868.30 ± 40.80 | 198.71 ± 142.12 | **11230.08 ± 199.12** | 5/5 | 137 |

**Đóng góp của từng cải tiến** (chênh lệch tổng chi phí so với Greedy + 2-Opt, âm là GA tốt hơn; mỗi dòng thêm đúng một thay đổi so với dòng trên):

| Biến thể GA | 10 điểm | 50 điểm | 100 điểm |
| :--- | ---: | ---: | ---: |
| GA cũ (50 cá thể, 80 thế hệ, `mutation_rate = 0.2`, phạt gốc) | +0.69% | +35.68% | +90.18% |
| + tham số tinh chỉnh, phạt vi phạm ×100 | −2.74% | −0.98% | +26.09% |
| + EnergyManager | −6.15% | −3.08% | +20.98% |
| + khởi tạo từ Greedy (**GA đề xuất**) | **−6.15%** | **−8.79%** | **−2.10%** |

- **Nhận xét:**
  1. Cấu hình cũ của pipeline không đủ cho bài lớn: 80 thế hệ × 50 cá thể quá ít, và mức phạt quá tải gốc quá nhẹ nên có lời giải không hợp lệ (1/5 ở 50 điểm, 4/5 ở 100 điểm).
  2. Năng lượng thật phụ thuộc **thứ tự giao** (tải giảm dần sau mỗi điểm). Khi được chấm bằng đúng mô hình của TV3, GA học cách giao gói nặng trước: ở 10 điểm, năng lượng giảm từ 325.03 xuống 309.73 Wh.
  3. Khởi tạo từ Greedy là yếu tố quyết định ở bài lớn. Nhờ elitism, theo thước đo của GA, lời giải tốt nhất không bao giờ tệ hơn lời giải Greedy ban đầu; độ lệch chuẩn cũng giảm mạnh (100 điểm: ± 647.71 → ± 199.12).
  4. Cái giá là thời gian chạy: vài giây ở 10 điểm, khoảng 45 giây ở 50 điểm và khoảng 2 phút ở 100 điểm, so với dưới 0.03 giây của Greedy. Thời gian ở 100 điểm bị nhiễu do máy chạy song song tác vụ khác; theo phép đo riêng ở mục 4 (62.29 ms/thế hệ × 2000 thế hệ), GA mất khoảng 125 giây.
- **Hạn chế:** ở 100 điểm GA chỉ tốt hơn Greedy 2.10% (độ lệch chuẩn khoảng 1.8%); mỗi cấu hình chỉ chạy 5 seed; tham số được quét trước khi có các bản sửa ở mục 7; mô hình chưa cho một Drone bay nhiều chuyến.
- **Hướng phát triển:** đưa tìm kiếm cục bộ (2-Opt) vào bên trong vòng lặp GA (Memetic Algorithm), tăng số thế hệ cho bài lớn, và hỗ trợ một Drone bay nhiều chuyến.

---

### 9. Phát hiện Lỗi Liên Module & Đề xuất cho Nhóm (Cross-module Bug Reports & Proposals)
Với code của thành viên khác, em không sửa âm thầm: em gửi đề xuất kèm số liệu và cách tái hiện, và khi buộc phải sửa thì tách thành commit riêng.

| Vấn đề phát hiện | Module (phụ trách) | Cách xử lý | Trạng thái |
| :--- | :--- | :--- | :--- |
| `repair_route_with_charging` lặp vô hạn (dẫn tới `MemoryError`) khi Drone đứng ở trạm sạc với pin đầy mà vẫn không bay tới được điểm kế: hàm chèn lại chính trạm đó mãi. Ở benchmark 100, 27/1000 cặp (trạm sạc → khách) có thể gây lỗi khi chở 5 kg | `energy_manager.py` (TV3) | Phát hiện khi viết test 11. Sửa tối thiểu: không chèn trạm sạc trùng điểm hiện tại, đánh dấu tuyến không khả thi. Commit riêng `8360f14`, có test hồi quy | Đã merge; TV5 bổ sung test hồi quy trong `tests/test_day5_integration.py` |
| Mức phạt quá tải 1000 / kg quá nhẹ ở quy mô lớn | `fitness.py` (TV5) | Không sửa code TV5; xử lý trong GA bằng `constraint_penalty_factor` | Đã merge (`9987897`) |
| `solve_ga` không truyền `EnergyManager`; `run_experiment` cố định 80 thế hệ × 50 cá thể | `pipeline.py` (TV5) | Đề xuất kèm số liệu đo trước/sau (`docs/GA_TUNING_RESULTS.md`, mục 8) | TV5 đã áp dụng, kèm khởi tạo từ Greedy (`7a24f57`) |
| `main.py` mặc định 3 Drone, không chở nổi benchmark 50 và 100 | `main.py` (TV5) | Đề xuất chọn K theo tổng khối lượng hàng | TV5 đã áp dụng (`7a24f57`) |
| Tiêu đề đường hội tụ đếm cả trạm sạc | `pipeline.py` (TV5) | Báo lỗi | TV5 đã sửa (`7a24f57`) |
| Một ô `inf` trong ma trận làm mọi fitness bằng 0 | Dữ liệu và ma trận khoảng cách (TV2, TV4) | Báo nhóm | Benchmark hiện không có cặp nào không tới được; pipeline thay `inf` bằng Euclid × 2 |
| Cờ `--parallel` của `main.py` không có tác dụng với GA | `pipeline.py` (TV5) | TV5 đồng ý cho sửa: `solve_ga` nhận `num_workers` (`c1da04c`) | PR #11 |
| Bảng §3 của `BAO_CAO_TONG_KET_DE_TAI.md`: dòng N = 20/30/50 không có nguồn, số Drone K sai công thức của `benchmark_evaluator.py` | Báo cáo tổng kết (TV5) | Chạy lại bằng `BenchmarkEvaluator.evaluate_scale`; TV5 đồng ý sửa (`fb6b6d4`) | PR #12 |
| Lời giải Greedy ở 100 / 500 điểm có 1 / 6 tuyến thiếu pin kể cả sau khi chèn trạm sạc, nhưng validator vẫn báo hợp lệ; phạt 1000 / tuyến quá nhẹ | `validator.py`, `fitness.py` (TV5) | Thêm cột "Tuyến thiếu pin" vào thực nghiệm; validator kiểm tra tuyến cạn pin (`2024e7c`) | Đã sửa (được nhóm cho phép) |
| 2-Opt làm tuyến đủ pin thành thiếu pin (GA ở 500 điểm, seed 0: 0 tuyến trước, 2 tuyến sau 2-Opt) và làm tăng tổng chi phí | `local_search.py` (TV6), `pipeline.py` (TV5) | Đo trước và sau 2-Opt; 2-Opt chỉ nhận bước đảo không làm tăng chi phí tuyến (`9f7a51d`) | Đã sửa (được nhóm cho phép) |
| Độ phức tạp GA thiếu số hạng EnergyManager; Định lý 5 phát biểu quá mạnh; bảng mục IV lấy tỷ số thời gian đo làm cột lý thuyết | `COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md` (TV5) | Rà soát, đề xuất thay thế kèm số đo (`docs/GA_COMPLEXITY_REVIEW.md`) | Chờ TV5 phản hồi |
| Định lý 4: chặng tới trạm sạc được chèn chỉ bảo đảm pin ≥ 0; danh sách trạm sạc được lọc lại ở mỗi lần gọi (~40% thời gian chèn trạm sạc ở 500 điểm) | `energy_manager.py` (TV3) | Đề xuất trong `docs/GA_COMPLEXITY_REVIEW.md` mục 6 | Chờ TV3 phản hồi |

---

### 10. Tuần 5–6: Song song hóa GA, thực nghiệm 10–500 điểm, phân tích độ phức tạp (Weeks 5–6)
- **Song song hóa đánh giá thích nghi** (`GeneticAlgorithm(num_workers=p)`):
  - Nhóm tiến trình (`multiprocessing.Pool`) được tạo một lần mỗi lần chạy, dữ liệu bài toán gửi một lần qua `initializer`.
  - Mỗi thế hệ chỉ gửi các cá thể chưa có trong cache.
  - Mọi bước ngẫu nhiên vẫn ở tiến trình chính, nên cùng seed thì kết quả **trùng hoàn toàn** với chạy tuần tự. Test 12 trong `tests/test_ga.py` kiểm tra điều này.
  - Pipeline: cờ `--parallel / --workers` nay áp dụng cho cả GA.
- **Đo tăng tốc** (lệnh `ga_tuning.py speedup`, 100 cá thể × 200 thế hệ, có EnergyManager): $S_4$ = 1.90 / 2.38 / 2.84 ở 50 / 100 / 500 điểm, $S_8$ = 3.45 ở 500 điểm (đo lại với EnergyManager mới của TV3; bản cũ: $S_4$ = 2.00 / 2.60 / 2.92, $S_8$ = 3.80); đạt tiêu chí 1.8 lần của nhóm từ 50 điểm. Bài 10 điểm chạy song song chậm hơn vì khởi động tiến trình (~0.6 s mỗi tiến trình trên Windows) lâu hơn cả thời gian tính. Biểu đồ: `docs/figures/ga_speedup.png`; chi tiết: `GA_TUNING_RESULTS.md` mục 10.
- **Thực nghiệm trên dữ liệu mới** (`GA_TUNING_RESULTS.md` mục 11, chạy lại ở mục 12 với EnergyManager mới của TV3 — Drone được ghé depot để sạc, và ở mục 13 sau khi sửa 2-Opt / validator; `compare` có thêm cột đúng giờ và tuyến thiếu pin; chạy 2 lần cùng seed, trùng mọi cột trừ thời gian). Số dưới đây theo mục 13 (số chốt):

| Quy mô | Greedy + 2-Opt | GA đề xuất | Chênh lệch | Đúng giờ Greedy → GA | Tuyến thiếu pin Greedy → GA | Hợp lệ Greedy / GA |
| :---: | ---: | ---: | :---: | :---: | :---: | :---: |
| 10 điểm (K = 3) | 749.02 | 706.50 ± 0.00 | **−5.68%** | 100.0% → 100.0% | 0 → 0 | 1/1 / 5/5 |
| 50 điểm (K = 15) | 4001.64 | 3796.41 ± 45.36 | **−5.13%** | 98.0% → 99.2% | 0 → 0 | 1/1 / 5/5 |
| 100 điểm (K = 31) | 12857.92 | 11683.20 ± 187.89 | **−9.14%** | 94.0% → 97.6% | 1 → 0 | **0/1** / 5/5 |
| 500 điểm (K = 150) | 94417.74 | 101722.04 ± 3169.24 | +7.74% | 95.0% → 94.5% | 6 → 0 | **0/1** / 3/3 |

- **Giải thích 500 điểm:** Greedy rẻ hơn vì 6/150 Drone không đủ pin bay hết tuyến mà chỉ bị phạt 1000 mỗi tuyến; với validator mới, lời giải đó không hợp lệ. GA nhân phạt ×100 nên tìm lời giải đủ pin cho mọi Drone, đổi lại bay xa hơn 15.9%. GA ở 500 điểm chưa hội tụ sau 2000 thế hệ.
- **Sửa 2-Opt và validator** (được nhóm cho phép): 2-Opt chỉ nhận bước đảo không làm tăng chi phí tuyến (trước đó 2-Opt làm Greedy đắt hơn so với không chạy 2-Opt, và làm 2 tuyến GA ở 500 điểm cạn pin); validator báo không hợp lệ khi có tuyến cạn pin.
- **Phân tích độ phức tạp** (`docs/GA_COMPLEXITY_REVIEW.md`): với EnergyManager, mỗi lần đánh giá tốn $O(K \cdot M + L \cdot C)$, nên $T_{GA} = O(G \cdot P \cdot (K \cdot M + L \cdot C + \log P))$; không có EnergyManager là $O(G \cdot P \cdot (L + \log P))$. Đối chiếu số đo: thời gian mỗi thế hệ chia cho $L$ gần như không đổi (0.13–0.14 ms) dù $L$ tăng 54 lần. Viết lại phát biểu Định lý 5 cho chính xác (chỉ đúng theo thước đo chọn lọc, trước 2-Opt) kèm phản ví dụ 500 điểm.
- **Báo cáo và slide phần GA:** file Word (8 trang) và slide (12 trang, có ghi chú người nói), nộp theo hướng dẫn của TV5.

---

## 💡 BÀI HỌC RÚT RA
1. **Code chạy đúng chưa chắc thuật toán tốt.** Cần đáp án tham chiếu (duyệt toàn bộ ở bài nhỏ) và chạy nhiều seed mới thấy được hội tụ sớm.
2. **Kết quả đẹp mà vi phạm ràng buộc thì không có giá trị.** Luôn xem cột "Hợp lệ" chứ không chỉ nhìn cost, và sửa từ gốc (hệ số phạt) thay vì lọc bỏ lời giải xấu.
3. **Giả thuyết phải được đo.** Ở 100 điểm, giả thuyết "do 2-Opt" bị số liệu bác bỏ; nguyên nhân thật nằm ở cách chấm điểm tuyến cần sạc.
4. **Thước đo khi tối ưu phải khớp thước đo khi chấm điểm cuối.** Hai lần GA tối ưu lệch mục tiêu (năng lượng ước lượng, tuyến chưa chèn trạm sạc) đều làm kết quả kém đi rõ rệt.
5. **Một con số xấu phải được giải thích trước khi kết luận.** Ở 500 điểm, GA "thua" Greedy 11%; truy đến cùng thì thấy Greedy vi phạm ràng buộc pin mà thước đo chung gần như không phạt, và bảng so sánh cần thêm cột tuyến thiếu pin.
6. **Song song hóa chỉ có lợi khi phần việc đủ nặng.** Đo trên nhiều quy mô mới thấy: bài nhỏ chạy song song còn chậm hơn, bài lớn có EnergyManager mới đạt tăng tốc cao.

---

## 📂 DANH MỤC CÁC FILE ĐÃ TẠO VÀ ĐÓNG GÓP
| STT | Tên File | Chức năng | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | `src/algorithms/genetic_algorithm.py` | Class `GeneticAlgorithm`: mã hóa và giải mã, toán tử di truyền, vòng lặp tiến hóa, khởi tạo từ Greedy, hệ số phạt, chấm điểm có EnergyManager, đánh giá song song (`num_workers`) | Hoàn thành |
| 2 | `tests/test_ga.py` | 12 unit test cho module GA (test 12: song song cho kết quả trùng tuần tự) | Passed 100% |
| 3 | `src/utils/ga_tuning.py` | Script thực nghiệm: quét tham số (`sweep`), so sánh với Greedy qua pipeline (`compare`, có cột đúng giờ và tuyến thiếu pin), đo tăng tốc (`speedup`), vẽ biểu đồ tăng tốc (`plot-speedup`) | Hoàn thành |
| 4 | `docs/GA_TUNING_RESULTS.md` | Báo cáo tinh chỉnh tham số, tăng tốc song song (mục 10) và so sánh 10–500 điểm trên dữ liệu mới (mục 11, chạy lại với EnergyManager mới ở mục 12) | Hoàn thành |
| 5 | `src/algorithms/energy_manager.py` (file của TV3) | Sửa lỗi lặp vô hạn trong `repair_route_with_charging` | Hoàn thành |
| 6 | `docs/TV1_CONTRIBUTION.md` | Báo cáo chi tiết phần việc và minh chứng đóng góp cá nhân | Hoàn thành |
| 7 | `src/pipeline.py` (file của TV5, đã được đồng ý) | `solve_ga` nhận `num_workers`; `run_experiment(parallel=True)` truyền xuống GA | Hoàn thành |
| 8 | `docs/GA_COMPLEXITY_REVIEW.md` | Rà soát phần GA trong tài liệu độ phức tạp của nhóm, đề xuất kèm số đo | Chờ TV5 phản hồi |
| 9 | `data/processed/ga_speedup_results.csv`, `docs/figures/ga_speedup.png` | Số liệu và biểu đồ tăng tốc song song | Hoàn thành |
| 10 | `docs/BAO_CAO_TONG_KET_DE_TAI.md` (file của TV5, đã được đồng ý), `data/processed/benchmark_comparison_results.csv` | Chạy lại và sửa 3 dòng N = 20/30/50 của bảng §3 | PR #12 |

## 🔖 CÁC COMMIT CHÍNH
| Commit | Ngày | Nội dung | Pull Request |
| :---: | :---: | :--- | :---: |
| `034b6d2` | 13/10/2026 | Chromosome, `decode()`, quần thể ngẫu nhiên, đánh giá có cache | #3 |
| `e6e1e33` | 13/10/2026 | Tournament, Order Crossover, Swap Mutation | #3 |
| `8c8bac6` | 13/10/2026 | `evolve()`, elitism, lịch sử hội tụ | #3 |
| `29a49fe` | 16/10/2026 | `encode()`, khởi tạo quần thể từ lời giải có sẵn, tham số mặc định mới | #7 |
| `9987897` | 16/10/2026 | Hệ số phạt vi phạm ràng buộc khi chọn lọc | #7 |
| `8360f14` | 16/10/2026 | Sửa vòng lặp vô hạn trong `energy_manager.py` (code của TV3) | #7 |
| `e61e77f` | 16/10/2026 | Chấm điểm tuyến sau khi chèn trạm sạc | #7 |
| `aa7deaa` | 16/10/2026 | Script `ga_tuning.py` và báo cáo `GA_TUNING_RESULTS.md` | #7 |
| `a0ca6d6` | 25/10/2026 | Đánh giá thích nghi song song (`num_workers`) và test 12 | #11 |
| `c1da04c` | 25/10/2026 | Pipeline: cờ `parallel / num_workers` áp dụng cho GA | #11 |
| `7785f5a` | 25/10/2026 | Lệnh `speedup` và kết quả tăng tốc 10–500 điểm | #11 |
| `f96282f` | 25/10/2026 | `compare` có cột đúng giờ, tuyến thiếu pin; kết quả 10–500 điểm | #11 |
| `97d92bb` | 25/10/2026 | Rà soát phần GA trong tài liệu độ phức tạp của nhóm | #11 |
| `fb6b6d4` | 25/10/2026 | Chạy lại số liệu N = 20/30/50 của bảng §3 báo cáo tổng kết | #12 |
