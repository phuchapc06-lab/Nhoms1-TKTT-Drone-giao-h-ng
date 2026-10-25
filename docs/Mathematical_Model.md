# Mô hình Toán học: Bài toán Định tuyến UAV (UDRP)

> **Cập nhật 25/10/2026 (TV1, được TV5 cho phép):** sửa cho khớp code (`src/algorithms/fitness.py`, `src/algorithms/energy_manager.py`): thêm số hạng năng lượng vào hàm mục tiêu và đổi ký hiệu cho trùng code (β: năng lượng, γ: phạt trễ giờ); thêm ràng buộc tải trọng và khung giờ; ghi rõ ngưỡng pin khi tới điểm giao và khi tới điểm sạc.

## 1. Phát biểu bài toán (Problem Statement)
Bài toán tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP) yêu cầu phân bổ các tuyến bay từ trạm gốc (Depot) đến một tập hợp các điểm giao hàng (Delivery points) sao cho đáp ứng các yêu cầu về giới hạn pin, tải trọng, khung giờ giao hàng và né tránh khu vực cấm bay (No-fly zones). Mỗi Drone bay **một chuyến**: xuất phát từ Depot với toàn bộ hàng của tuyến, có thể ghé trạm sạc hoặc Depot để sạc giữa đường, và kết thúc ở Depot.

## 2. Tập hợp, tham số và biến quyết định
- $V = \{0\} \cup V_D \cup V_C$: Depot (0), tập $N$ điểm giao hàng $V_D$ và tập $C$ trạm sạc $V_C$. Tập điểm sạc $S = V_C \cup \{0\}$.
- $K$: tập các UAV; $Q_{max} = 5$ kg: tải tối đa; $B_{max} = 300$ Wh: dung lượng pin; $B_{safe} = 0.15 \cdot B_{max}$: ngưỡng an toàn.
- $q_i$: khối lượng hàng của khách $i$; $[e_i, l_i]$: khung giờ; $s_i$: thời gian phục vụ (giao hàng hoặc sạc); $v = 10$ đơn vị khoảng cách / phút: vận tốc bay.
- $d_{ij}$: độ dài đường bay thực tế từ $i$ đến $j$, tính bằng **A*** né vùng cấm bay.
- $x_{ijk} \in \{0, 1\}$: bằng `1` nếu UAV $k$ bay thẳng từ điểm $i$ đến điểm $j$.
- $t_i$: thời điểm UAV đến điểm $i$; $w_{ij}$: khối lượng hàng còn trên Drone khi bay chặng $(i, j)$; $E_i$: pin còn lại khi đến điểm $i$.

## 3. Hàm mục tiêu (Objective Function)
Tối thiểu hóa tổng chi phí: quãng đường, năng lượng tiêu thụ và phạt giao trễ giờ.

$$ \text{Minimize} \quad Z = \alpha \sum_{k \in K} \sum_{i, j \in V} d_{ij} x_{ijk} + \beta \sum_{k \in K} \sum_{i, j \in V} e_{ij}\, x_{ijk} + \gamma \sum_{i \in V} \max(0, t_i - l_i) $$

Trong đó:
- $e_{ij} = d_{ij} \cdot (1 + 0.15 \cdot w_{ij})$: năng lượng của chặng $(i, j)$, tăng theo tải đang chở (mục 4.3).
- $\alpha = 1$, $\beta = 1.5$, $\gamma = 5$ (giá trị mặc định trong `FitnessCalculator`).
- Khi cài đặt, vi phạm ràng buộc tải trọng và pin được đưa vào $Z$ dưới dạng phạt $\delta = 1000$ (mỗi kg quá tải, mỗi tuyến cạn pin) để thuật toán tìm kiếm vẫn so sánh được các lời giải vi phạm; lời giải cuối cùng phải thỏa các ràng buộc 4.1–4.3 (kiểm tra bằng `DataContractValidator`).

## 4. Các Ràng buộc (Constraints)
**4.1. Ràng buộc luồng giao hàng (Flow conservation):**
Mỗi điểm giao hàng được phục vụ đúng 1 lần bởi 1 UAV; mỗi tuyến bắt đầu và kết thúc ở Depot.
$$ \sum_{k \in K} \sum_{j \in V} x_{ijk} = 1 \quad \forall i \in V_D $$

**4.2. Ràng buộc tải trọng (Capacity):**
Tổng khối lượng hàng trên mỗi tuyến không vượt quá tải tối đa:
$$ \sum_{i \in V_D} q_i \sum_{j \in V} x_{ijk} \le Q_{max} \quad \forall k \in K $$

**4.3. Ràng buộc năng lượng pin (Energy constraint):**
Năng lượng tiêu thụ tỷ lệ thuận với khoảng cách bay và tải đang chở (tải giảm dần sau mỗi điểm giao). Nếu $x_{ijk} = 1$:
$$ E_j = E_i - d_{ij} \cdot (1 + 0.15 \cdot w_{ij}), \qquad E_0 = B_{max} $$
- Khi tới **điểm giao hàng** $j \in V_D$: $E_j \ge B_{safe}$.
- Khi tới **điểm sạc** $j \in S$ (trạm sạc hoặc Depot): $E_j \ge 0$, sau đó pin được sạc đầy, $E_j \leftarrow B_{max}$.

Trong code, `EnergyManager.repair_route_with_charging` chèn điểm sạc khi chặng kế tiếp làm pin xuống dưới $B_{safe}$; tuyến không sửa được bị đánh dấu thiếu pin. Validator chỉ kiểm tra điều kiện cứng $E_j \ge 0$ (tuyến cạn pin là không hợp lệ); ngưỡng $B_{safe}$ là biên an toàn mà bước chèn điểm sạc cố giữ, có thể không đạt khi không điểm sạc nào tới được.

**4.4. Khung giờ giao hàng (Time windows, ràng buộc mềm):**
$$ t_j = \max(t_i + s_i + d_{ij} / v,\ e_j) \quad \text{nếu } x_{ijk} = 1 $$
Đến sớm thì chờ tới $e_j$; đến muộn ($t_j > l_j$) không bị cấm nhưng bị phạt $\gamma \cdot (t_j - l_j)$ trong hàm mục tiêu.

**4.5. Ràng buộc vùng cấm bay (No-fly zone constraint):**
Đường đi thực tế giữa $i$ và $j$ không phải là đường thẳng Euclidean mà là đường đi ngắn nhất $A^*(i, j)$ trên đồ thị lưới không giao cắt với không gian của tập hợp $NFZ$ (No-fly zones).
$$ A^*(i, j) \cap NFZ = \emptyset \quad \forall i, j \text{ nếu } x_{ijk} = 1 $$
