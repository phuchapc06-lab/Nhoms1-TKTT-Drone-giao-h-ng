# KẾ HOẠCH NÉN TIẾN ĐỘ 4 NGÀY (THỨ 4 - THỨ 7)
## GỘP NỘI DUNG TUẦN 5 (SONG SONG HÓA & THỰC NGHIỆM) VÀ TUẦN 6 (PHÂN TÍCH ĐỘ PHỨC TẠP & CHỨNG MINH ĐÚNG ĐẮN)
> **Đề tài:** Hệ thống Tối ưu hóa Định tuyến Đội bay UAV Giao hàng Đô thị Thông minh (UDRP)  
> **Nhóm thực hiện:** Nhóm 1 | **Nhóm trưởng (Tech Lead):** Nguyễn Phúc Hà (Thành viên 5)  
> **Thời gian thực hiện:** 4 Ngày (Thứ Tư 21/10/2026 đến Thứ Bảy 24/10/2026)

---

## 🎯 I. MỤC TIÊU VÀ PHẠM VI NÉN TIẾN ĐỘ

Kết hợp toàn bộ yêu cầu của **Tuần 5** và **Tuần 6** vào khung thời gian tăng tốc 4 ngày:
1. **Tuần 5 (Song song hóa & Thực nghiệm):**
   - Cài đặt song song hóa (Multiprocessing) cho thuật toán A* và GA.
   - Chạy thực nghiệm đối sánh đa quy mô giữa giải thuật đề xuất ($A^* + GA$) và Baseline ($A^* + Greedy$).
   - Đo đạc đầy đủ các chỉ số khoa học: Thời gian tính toán (Execution Time), Tổng năng lượng tiêu thụ (Energy), Quãng đường (Distance), Tỷ lệ giao hàng đúng giờ (On-time Delivery Rate), và Tốc độ tăng tốc khi song song hóa (Speedup).
2. **Tuần 6 (Phân tích kết quả & Chứng minh tính đúng đắn):**
   - Phân tích độ phức tạp thuật toán theo thời gian và không gian: $A^*$ với Min-Heap $O(|V| \log |V| + |E|)$, GA $O(G \cdot P \cdot (N+K))$, Greedy $O(K \cdot N^2)$, 2-Opt $O(I \cdot N^2)$.
   - Chứng minh tính đúng đắn (Correctness) và tính dừng (Termination) của toàn bộ hệ thống (đặc biệt là thuật toán tự động chèn trạm sạc không bị lặp vô hạn).
   - Vẽ hệ thống biểu đồ so sánh, phân tích khả năng mở rộng (Scalability) khi số lượng UAV và khách hàng tăng lên 50, 100, 500 điểm.

---

## 📅 II. BẢNG PHÂN BỔ CHI TIẾT THEO 4 NGÀY

### NGÀY 1 (Thứ Tư - 21/10/2026): Thiết kế Song song hóa & Bổ sung Chỉ số Thực nghiệm
- **Mục tiêu ngày:** Hoàn thiện mã nguồn song song hóa (Parallelization) cho A* và GA; bổ sung chỉ số đo lường "Tỷ lệ giao hàng đúng giờ" (On-time Delivery Rate).
- **Phân công 6 thành viên:**
  - **TV1 (GA Core):** Cài đặt đa tiến trình (`multiprocessing.Pool`) để tính song song hàm thích nghi (Fitness) cho quần thể GA nhằm giảm thời gian tiến hóa ở các quy mô 100 và 500 điểm.
  - **TV2 (A* Pathfinding):** Cài đặt song song hóa tính toán ma trận khoảng cách (`concurrent.futures.ProcessPoolExecutor`) khi tính các cặp điểm $(i, j)$ né vùng cấm bay.
  - **TV3 (Năng lượng & Pin):** Bổ sung hàm tính năng lượng tiêu thụ chi tiết từng chặng bay và đo đạc thời gian sạc tại trạm cho báo cáo thực nghiệm.
  - **TV4 (Dữ liệu Benchmark):** Kiểm tra và hoàn thiện bộ kịch bản 10, 50, 100, 500 điểm với các khung giờ Time Windows đa dạng (chặt chẽ và nới lỏng) để đo đạc tỷ lệ giao đúng giờ.
  - **TV5 (Tech Lead - Nguyễn Phúc Hà):** 
    - Nâng cấp `FitnessCalculator` và `BenchmarkEvaluator` để đo thêm chỉ số: **Tỷ lệ đơn hàng giao đúng giờ (%)** và **Hệ số tăng tốc (Speedup $S_p = T_1 / T_p$)**.
    - Tích hợp cờ lệnh song song hóa `--parallel` vào `main.py` và `pipeline.py`.
  - **TV6 (Baseline & 2-Opt):** Tối ưu hóa thuật toán Greedy Router và 2-Opt để chuẩn bị làm chuẩn đối sánh hiệu năng với bản song song của GA.

---

### NGÀY 2 (Thứ Năm - 22/10/2026): Chạy Thực nghiệm Đối sánh Đa quy mô & Đo đạc Hiệu năng
- **Mục tiêu ngày:** Chạy thực nghiệm tự động trên các quy mô 10, 50, 100, 500 điểm; thu thập số liệu đa chiều và xuất bảng kết quả thực nghiệm chuẩn xác.
- **Phân công 6 thành viên:**
  - **TV1 & TV6:** Thực thi thực nghiệm đối sánh $A^* + GA$ vs $A^* + Greedy$ trên các quy mô [10, 20, 30, 50, 100, 500 điểm]; kiểm soát hội tụ GA.
  - **TV2:** Đo đạc thời gian tính ma trận khoảng cách A* trên 1 core, 2 cores, 4 cores để ghi nhận hệ số tăng tốc Speedup.
  - **TV3:** Thống kê mức tiết kiệm năng lượng của GA so với Greedy; kiểm tra 100% các chuyến bay không bị cạn pin.
  - **TV4:** Thu thập toàn bộ log thực nghiệm, lưu trữ số liệu thô và xuất file CSV tổng hợp: `data/processed/benchmark_comparison_results.csv`.
  - **TV5 (Tech Lead - Nguyễn Phúc Hà):**
    - Điều phối chạy lệnh `python src/main.py --evaluate-all` với bộ kịch bản đa quy mô mở rộng.
    - Tự động cập nhật báo cáo khoa học `docs/EXPERIMENT_RESULTS.md` với đầy đủ 4 chỉ số: Execution Time, Total Energy, Total Distance, On-time Delivery Rate (%).

---

### NGÀY 3 (Thứ Sáu - 23/10/2026): Phân tích Độ phức tạp Thuật toán & Chứng minh Tính đúng đắn
- **Mục tiêu ngày:** Hoàn thiện cơ sở lý thuyết toán học: Phân tích độ phức tạp thời gian/không gian cho từng thành phần và chứng minh tính đúng đắn/tính dừng của toàn bộ giải pháp.
- **Phân công 6 thành viên:**
  - **TV2 (A* Pathfinding):**
    - Phân tích chi tiết độ phức tạp thuật toán A* với Min-Heap: Thời gian $O(|V| \log |V| + |E|)$, Không gian $O(|V|)$ cho đồ thị và $O(|V|^2)$ cho bảng ma trận tra cứu $O(1)$.
    - Chứng minh tính tối ưu (Admissibility & Consistency) của hàm heuristic Octile.
  - **TV1 (GA Core):**
    - Phân tích độ phức tạp GA: Thời gian $O(G \cdot P \cdot (N + K))$, Không gian $O(P \cdot (N + K))$ cho quần thể.
    - Chứng minh toán tử Order Crossover (OX) và Swap Mutation không bao giờ làm mất hoặc trùng lặp khách hàng.
  - **TV3 (Energy Manager):**
    - Chứng minh tính dừng (Termination Proof) của thuật toán tự động chèn trạm sạc `repair_route_with_charging`: Chứng minh không lặp vô hạn khi không thể bay tới node tiếp theo.
    - Chứng minh mức pin luôn thỏa mãn $E_{battery} \ge E_{safe}$ tại mọi điểm dừng.
  - **TV6 (Baseline & 2-Opt):**
    - Phân tích độ phức tạp thời gian của Greedy Baseline $O(K \cdot N^2)$ và 2-Opt Local Search $O(I \cdot N^2)$.
    - Chứng minh 2-Opt luôn đơn điệu giảm hoặc bằng quãng đường ($d_{new} \le d_{old}$).
  - **TV5 (Tech Lead - Nguyễn Phúc Hà):**
    - Tổng hợp bài toán tổng thể: Phân tích độ phức tạp của toàn bộ Pipeline tích hợp.
    - Soạn thảo và ban hành tài liệu chuyên sâu: `docs/COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md`.

---

### NGÀY 4 (Thứ Bảy - 24/10/2026): Trực quan hóa Biểu đồ Khả năng mở rộng, Báo cáo Tổng kết & Đóng gói Nghiệm thu
- **Mục tiêu ngày:** Xuất bộ biểu đồ khoa học trực quan (So sánh cột, Scalability, Speedup song song), hoàn thiện tài liệu Báo cáo Tổng kết đề tài và đóng gói sản phẩm nghiệm thu.
- **Phân công 6 thành viên:**
  - **TV5 (Tech Lead - Nguyễn Phúc Hà):**
    - Nâng cấp `UAVVisualizer` vẽ bổ sung:
      1. Biểu đồ Scalability khả năng mở rộng quy mô từ 10 đến 500 điểm (`scalability_analysis.png`).
      2. Biểu đồ tăng tốc Speedup của song song hóa (`speedup_analysis.png`).
      3. Biểu đồ tỷ lệ giao hàng đúng giờ theo khung thời gian Time Window (`ontime_rate_comparison.png`).
    - Chạy Master Test Suite (`python src/main.py --test`), xác nhận 10/10 bài test đạt 100% Passed.
    - Cập nhật `README.md`, `TIEN_DO.md`, đồng bộ và đẩy mã nguồn lên các nhánh `nguyen-phuc-ha`, `develop`, `main`.
  - **TV1, TV2, TV3, TV4, TV6:**
    - Soạn thảo nội dung chuyên đề của mình cho Báo cáo Tổng kết Đề tài (Word/LaTeX).
    - Thiết kế Slide thuyết trình bảo vệ đề tài: Sơ đồ kiến trúc, kết quả thực nghiệm đối sánh, biểu đồ phân tích và video/ảnh demo đường bay né NFZ.

---

## 👥 III. BẢNG TỔNG HỢP PHÂN CÔNG THEO TỪNG THÀNH VIÊN TRONG 4 NGÀY

| Thành viên | Thứ 4 (21/10) | Thứ 5 (22/10) | Thứ 6 (23/10) | Thứ 7 (24/10) | Sản phẩm bàn giao (Deliverables) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TV1** *(GA Core)* | Song song hóa đánh giá quần thể GA (`multiprocessing`) | Chạy đối sánh GA trên đa quy mô (10-500 điểm) | Phân tích độ phức tạp GA $O(G \cdot P \cdot (N+K))$, chứng minh OX/Elitism | Hoàn thiện diễn giải GA trong báo cáo và slide thuyết trình | Code GA song song, mục phân tích độ phức tạp GA |
| **TV2** *(A\* Precompute)* | Song song hóa tính ma trận khoảng cách A* né NFZ | Đo thời gian chạy A* tuần tự vs song song, tính Speedup | Phân tích độ phức tạp $A^*$ $O(\|V\|\log\|V\| + \|E\|)$, tính Consistent heuristic | Soạn thảo nội dung A* và Speedup cho báo cáo/slide | Code A* song song, bảng đo Speedup, phân tích A* |
| **TV3** *(Energy Manager)* | Bổ sung hàm chi tiết tiêu hao chặng & thời gian sạc | Thống kê số lần sạc pin và mức năng lượng tiết kiệm | Chứng minh tính dừng và tính an toàn của thuật toán sạc pin | Soạn nội dung quản lý pin và trạm sạc cho báo cáo/slide | Code đo năng lượng, chứng minh toán học tính dừng |
| **TV4** *(Benchmark Data)* | Kiểm định kịch bản Time Windows đa dạng (10-500 điểm) | Thu thập, làm sạch log thực nghiệm, xuất CSV tổng hợp | Phân tích ảnh hưởng của mật độ khách hàng lên độ phức tạp | Tổng hợp phụ lục số liệu thực nghiệm cho slide/báo cáo | Bộ dữ liệu mở rộng, file CSV số liệu thực nghiệm |
| **TV5** *(Tech Lead - Hà)* | **Tích hợp cờ song song hóa `--parallel`, hàm đo On-time rate** | **Điều phối chạy Batch Benchmark, cập nhật EXPERIMENT_RESULTS** | **Tổng hợp bài toán toàn cục, viết COMPLEXITY_ANALYSIS.md** | **Vẽ biểu đồ Scalability/Speedup, chạy 10/10 Tests, merge Git** | **Pipeline song song, bộ 3 biểu đồ mới, báo cáo tổng hợp** |
| **TV6** *(Baseline & 2-Opt)* | Tối ưu hóa tốc độ thuật toán Greedy Baseline & 2-Opt | Thu thập số liệu hiệu năng của Baseline đối sánh với GA | Phân tích độ phức tạp Greedy $O(K \cdot N^2)$, 2-Opt $O(I \cdot N^2)$ | Soạn nội dung phân tích đối sánh Baseline cho slide/báo cáo | Code 2-Opt tối ưu, phân tích độ phức tạp Baseline |

---

## 📌 IV. TIÊU CHÍ NGHIỆM THU CUỐI SPRINT 4 NGÀY (CHỦ NHẬT)

1. **Hiệu năng Song song hóa:** Tốc độ tính toán ma trận A* và GA trên máy đa nhân tăng tốc rõ rệt ($S_p \ge 1.8\times$ trên 4 nhân).
2. **Số liệu Thực nghiệm Đầy đủ:** Bảng số liệu đối sánh chi tiết trên cả 4 quy mô (10, 50, 100, 500 điểm) với đầy đủ 4 tiêu chí cốt lõi: Quãng đường (km), Năng lượng (Wh), Thời gian (s), Tỷ lệ giao hàng đúng giờ (%).
3. **Cơ sở Lý thuyết Vững chắc:** Có văn bản phân tích toán học chi tiết về độ phức tạp $O(|V|\log|V| + |E|)$ và chứng minh tính đúng đắn/tính dừng của hệ thống.
4. **Trực quan hóa Hoàn chỉnh:** Đầy đủ biểu đồ Scalability và so sánh hiệu năng trực quan.
5. **Chất lượng Kiểm thử:** 10/10 Unit Test & Integration Test đạt **100% Passed**.
