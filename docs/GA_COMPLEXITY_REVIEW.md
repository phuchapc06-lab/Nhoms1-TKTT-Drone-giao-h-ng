# Rà soát phần GA trong `COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md`
**Người rà soát:** Thành viên 1 (GA Core Engine) · **Ngày:** 25/10/2026 · **Gửi:** TV5 (chủ file), TV3 (mục 6)

File `docs/COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md` là của TV5. Tài liệu này **chỉ đề xuất**, không sửa file gốc. Mỗi đề xuất có căn cứ: dòng code hoặc số đo tái lập được.

> **Cập nhật 25/10/2026: ĐÃ ÁP DỤNG** vào `COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md` (TV5 cho phép TV1 sửa). Hai điểm đã thay đổi so với nội dung dưới đây: (1) TV3 đã bỏ bước lọc trạm sạc theo $M$ nút (`bb86a29`), nên số hạng $K \cdot M$ không còn, độ phức tạp có EnergyManager gọn thành $O(G \cdot P \cdot (L \cdot C + \log P))$, và bảng mục 3 (đo với EnergyManager cũ) được thay bằng số đo mới; (2) 2-Opt nay chỉ giữ bước đảo không làm tăng chi phí tuyến và validator kiểm tra cạn pin, nên phản ví dụ của Định lý 5 dùng số liệu `GA_TUNING_RESULTS.md` mục 13. Phần dưới giữ nguyên làm lịch sử.

Ký hiệu như file gốc, thêm:
- $L = N + K - 1$: độ dài chromosome.
- $\lambda$: hệ số nhân phạt khi chọn lọc (`constraint_penalty_factor`, mặc định 100).

## 1. Tóm tắt

| # | Vị trí trong file gốc | Vấn đề | Mức độ |
| :---: | :--- | :--- | :---: |
| 1 | II.2a, II.5 | Mỗi lần đánh giá được tính là $O(N+K)$. Điều này chỉ đúng khi **không** có EnergyManager, trong khi pipeline luôn truyền EnergyManager cho GA (từ `7a24f57`) và GA chèn trạm sạc trước khi chấm điểm. Thiếu số hạng $O(K \cdot M + L \cdot C)$. | Quan trọng |
| 2 | II.2a | Chưa có độ phức tạp của bản GA song song (`num_workers`). | Bổ sung |
| 3 | III, Định lý 5 | Phát biểu $\text{Cost}(S_{GA}) \le \text{Cost}(S_{greedy})$ quá mạnh: chỉ đúng theo **thước đo chọn lọc của GA, trước 2-Opt**. Thực nghiệm 500 điểm là phản ví dụ. | Quan trọng |
| 4 | IV.1 | Cột "Lý thuyết GA" thực chất là tỷ số thời gian **đo được** (1.1446 / 0.4854 = 2.36 ≈ "2.3"; 2.4002 / 0.4854 = 4.94 ≈ "4.8"), nên phép "đối chiếu" bị vòng lặp. | Quan trọng |
| 5 | II.2a, II.2b, Định lý 2 | Ba chỗ nhỏ: Swap là $O(L)$ chứ không $O(1)$ (code sao chép chromosome); cache là $O(P \cdot L)$ chứ không $O(P)$; `decode` bỏ tuyến rỗng nên có $\le K$ tuyến, không phải đúng $K$. | Nhỏ |
| 6 | II (sơ đồ), II.5 (Pha 5), Định lý 4 | "100% khả thi / không cạn pin" sai từ 100 điểm: lời giải Greedy có 1 (100 điểm) và 6 (500 điểm) tuyến mà EnergyManager báo không khả thi kể cả sau khi chèn trạm sạc (`GA_TUNING_RESULTS.md` mục 11). Ngoài ra, chặng tới trạm sạc được chèn chỉ bảo đảm pin $\ge 0$, không phải $\ge 15\%$. | Quan trọng (TV3/TV5) |

## 2. Đề xuất thay thế mục II.2: độ phức tạp của GA

**Chi phí đánh giá một cá thể** (`_evaluate_chromosome` trong `genetic_algorithm.py`):

| Bước | Không có EnergyManager | Có EnergyManager |
| :--- | :---: | :---: |
| Giải mã chromosome thành tuyến | $O(L)$ | $O(L)$ |
| Chèn trạm sạc cho từng tuyến (`repair_route_with_charging`) | — | $O(K \cdot M + L \cdot C)$ |
| Chấm điểm (`evaluate_solution`, gồm năng lượng và khung giờ) | $O(L)$ | $O(L)$ |
| **Tổng** $T_{ind}$ | $O(L)$ | $O(K \cdot M + L \cdot C)$ |

Giải thích số hạng $O(K \cdot M + L \cdot C)$:
- **$K \cdot M$:** mỗi lần gọi, `repair_route_with_charging` duyệt toàn bộ $M$ nút để lọc danh sách trạm sạc (`energy_manager.py` dòng 125), và hàm được gọi cho cả $K$ tuyến.
- **$L \cdot C$:** với mỗi chặng thiếu pin, hàm duyệt $C$ trạm sạc (dòng 160).

**Chi phí các toán tử mỗi thế hệ:**
- Elitism (sắp xếp): $O(P \log P)$.
- Tournament: $O(P \cdot k_{tour})$.
- OX: $O(L)$ mỗi con.
- Swap: $O(L)$ mỗi con, vì sao chép chromosome để không sửa cha.
- Cache theo `tuple(chromosome)`: $O(L)$ mỗi cá thể.

Tổng chi phí toán tử: $T_{ops} = O(P \cdot (L + \log P))$.

**Tổng thời gian (tuần tự):**
$$T_{GA} = O\big(G \cdot P \cdot (L + \log P)\big) \quad \text{(không EnergyManager)}, \qquad T_{GA} = O\big(G \cdot P \cdot (K \cdot M + L \cdot C + \log P)\big) \quad \text{(có EnergyManager)}$$
Mỗi thế hệ chỉ đánh giá những cá thể chưa có trong cache (elite và bản sao không phải tính lại), nên đây là cận trên.

**Bản song song với $p$ tiến trình** (`GeneticAlgorithm(num_workers=p)`): chỉ phần đánh giá được chia, còn chọn lọc, lai ghép, đột biến vẫn chạy ở tiến trình chính.
$$T_{GA}(p) = O\Big(T_{pool}(p) + G \cdot \big(\tfrac{P \cdot T_{ind}}{p} + T_{ops} + T_{ipc}\big)\Big), \qquad T_{ipc} = O(P \cdot L), \qquad T_{pool}(p) = O(p \cdot M^2)$$
- $T_{ipc}$: gửi chromosome đi và nhận kết quả về.
- $T_{pool}$: mỗi tiến trình nhận một bản ma trận $D$ khi khởi động, cộng thời gian khởi động tiến trình. Trên Windows khoảng 0.6 s mỗi tiến trình.

Theo định luật Amdahl, tăng tốc bị chặn bởi phần không chia được:
$$S_p \le \frac{T_{ind} + T_{ops}/P}{T_{ind}/p + (T_{ops} + T_{ipc})/P}$$
Do đó GA song song chỉ có lợi khi $T_{ind}$ lớn (có EnergyManager, quy mô lớn).

**Bộ nhớ:**
- Quần thể và cache: $O(P \cdot L)$.
- Bản song song: thêm $O(p \cdot M^2)$ cho bản sao ma trận ở mỗi tiến trình.

## 3. Đề xuất thay thế bảng IV.1: đối chiếu lý thuyết với thực nghiệm

Số đo từ `data/processed/ga_speedup_results.csv`:
- Lệnh `ga_tuning.py speedup`, 1 tiến trình, $P = 100$, 200 thế hệ.
- Dữ liệu `benchmark_{10,50,100,500}.json`.
- Cột "quét trạm sạc" đo riêng: thời gian dòng 125 của `energy_manager.py` × số cá thể.

| N | $L$ | $K$ | $C$ | $M$ | ms / thế hệ (không EM) | **÷ L** | ms / thế hệ (có EM) | Phần tăng do EM | trong đó quét trạm sạc | **(Phần tăng − quét) ÷ (L·C)** |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 12 | 3 | 3 | 14 | 1.73 | 0.144 | 3.42 | 1.7 | 0.2 | 0.041 |
| 50 | 64 | 15 | 6 | 57 | 8.53 | 0.133 | 25.17 | 16.6 | 3.5 | 0.034 |
| 100 | 130 | 31 | 10 | 111 | 16.87 | 0.130 | 68.19 | 51.3 | 12.4 | 0.030 |
| 500 | 649 | 150 | 25 | 526 | 85.41 | 0.132 | 836.59 | 751.2 | 285.5 | 0.029 |

**Đọc bảng:**
- Không có EnergyManager, thời gian mỗi thế hệ chia cho $L$ gần như **không đổi** (0.13–0.14 ms) dù $L$ tăng 54 lần. Điều này khớp với $O(P \cdot L)$ mỗi thế hệ.
- Có EnergyManager, phần tăng thêm (sau khi trừ phần quét $K \cdot M$) chia cho $L \cdot C$ cũng gần **không đổi** (0.029–0.041 ms) dù $L \cdot C$ tăng 450 lần. Điều này khớp với số hạng $O(L \cdot C)$.
- Phần quét danh sách trạm sạc ($O(K \cdot M)$) chiếm 38% phần tăng thêm ở 500 điểm (285.5 / 751.2).

## 4. Đề xuất thay thế Định lý 5

> **Phát biểu (sửa).** Gọi $R(S)$ là lời giải $S$ sau khi chèn trạm sạc (nếu GA có EnergyManager), $\text{Pen}(S) \ge 0$ là phần phạt vi phạm (quá tải, thiếu pin) trong `breakdown["cap_penalty"]`, và
> $$\text{Cost}_\lambda(S) = \text{Cost}(R(S)) + (\lambda - 1)\cdot \text{Pen}(R(S)), \qquad F(S) = \frac{1000}{\text{Cost}_\lambda(S) + 1}$$
> là thước đo GA dùng để chọn lọc. Nếu lời giải Greedy $S_{greedy}$ (có $\le K$ tuyến) được đưa vào quần thể ban đầu và Elitism giữ $E \ge 1$ cá thể, thì lời giải GA trả về $S_{GA}$, **trước bước 2-Opt của pipeline**, thỏa:
> $$\text{Cost}_\lambda(S_{GA}) \le \text{Cost}_\lambda(S_{greedy})$$
> **Hệ quả.** Nếu $\text{Pen}(R(S_{greedy})) = 0$ thì $\text{Cost}(R(S_{GA})) \le \text{Cost}(R(S_{greedy}))$, vì $\lambda \ge 1$ và $\text{Pen} \ge 0$.

**Chứng minh:** giữ nguyên lập luận hiện tại (elitism làm best fitness không giảm), thay Fitness bằng $F$. Code còn lưu riêng lời giải tốt nhất từ đầu đến giờ (`best_eval` trong `evolve`), nên dãy best fitness không giảm kể cả khi $E = 0$.

**Định lý cũ không bảo đảm được hai điều:**
1. **Sau 2-Opt.** 2-Opt chỉ giảm quãng đường (Định lý 3), không giảm tổng chi phí, nên có thể tăng năng lượng, trễ giờ, hoặc làm tuyến thiếu pin. Đo được:
   - Greedy ở 50 điểm có chi phí 4002.00 trước 2-Opt, 4039.25 sau 2-Opt.
   - GA ở 500 điểm có 0 tuyến thiếu pin trước 2-Opt, 1 tuyến sau 2-Opt (cả 3 seed).
2. **Khi Greedy vi phạm ràng buộc.** $\lambda$ khuếch đại phạt nên $\text{Cost}_\lambda(S_{greedy})$ rất lớn, và bất đẳng thức không nói gì về $\text{Cost}$ gốc.
   - **Phản ví dụ, 500 điểm:** Greedy có 6 tuyến thiếu pin. $\text{Cost}_\lambda(S_{greedy}) = 95455.39 + 99 \times 6000 = 689455.39$.
   - Chi phí cuối của GA là 106080.99 ± 8024.58, **lớn hơn** của Greedy (95455.39). Xem `GA_TUNING_RESULTS.md` mục 11.

## 5. Các sửa nhỏ
1. **II.2a, Swap Mutation:** "$O(1)$ mỗi cá thể" → "$O(L)$ mỗi cá thể (sao chép chromosome để không sửa cha; phép hoán đổi là $O(1)$)". Tổng không đổi vì OX đã là $O(P \cdot L)$.
2. **II.2b:** "Cache đánh giá thế hệ: $O(P)$" → "$O(P \cdot L)$ (khóa là `tuple(chromosome)`)".
3. **Định lý 2, ý 3:** "tách thành $K$ danh sách con" → "tách thành tối đa $K$ danh sách con; danh sách rỗng (hai vách ngăn liền nhau) bị bỏ, nên số tuyến $\le K$". Kết luận của định lý không đổi.
4. **II.5, dòng Pha 3:** cập nhật theo mục 2 ở trên. Dòng tổng thể thêm số hạng $G \cdot P \cdot (K \cdot M + L \cdot C)$ khi có EnergyManager.

## 6. Ngoài phần GA (để TV3 / TV5 quyết định)
1. **Định lý 4 và các câu "100% khả thi / không cạn pin":**
   - **Tuyến không khả thi:** khi không trạm sạc nào tới được, `repair_route_with_charging` vẫn bay tiếp và đặt `is_feasible = False` (`energy_manager.py` dòng 187). Tuyến đó thật sự thiếu pin. Thực nghiệm có 1 tuyến (Greedy, 100 điểm) và 6 tuyến (Greedy, 500 điểm).
   - **Ngay cả với tuyến khả thi:**
     - Chặng bay thẳng được kiểm tra pin còn lại $\ge B_{safe}$ (dòng 146).
     - Chặng tới trạm sạc được chèn chỉ kiểm tra `current_battery >= energy_to_cs` (dòng 165). Nghĩa là khi hạ cánh ở trạm sạc, pin chỉ được bảo đảm $\ge 0$, không phải $\ge B_{safe}$.
   - **Đề xuất phát biểu lại:** "Với mọi tuyến được đánh dấu khả thi, pin khi tới điểm giao hàng và Depot $\ge B_{safe}$; khi tới trạm sạc được chèn, pin $\ge 0$". Hoặc TV3 sửa dòng 165 thành `current_battery - energy_to_cs >= self.min_safe_battery` để giữ đúng phát biểu cũ.
2. **Hiệu năng `repair_route_with_charging` (TV3):** danh sách trạm sạc được lọc lại từ $M$ nút ở mỗi lần gọi (dòng 125). Tính một lần rồi dùng lại sẽ bỏ được số hạng $O(K \cdot M)$. Ở 500 điểm, phần này chiếm khoảng 40% thời gian chèn trạm sạc (đo: 2.855 / 7.113 ms mỗi cá thể).

## 7. Tái lập số liệu
```bash
python src/utils/ga_tuning.py speedup --scales 10 50 100 500 --workers 1 --generations 200 --repeats 3
python src/utils/ga_tuning.py compare --scales 500 --seeds 3 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8 --only-proposed
```
