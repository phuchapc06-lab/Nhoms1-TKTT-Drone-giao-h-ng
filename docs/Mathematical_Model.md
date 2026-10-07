# Mô hình Toán học: Bài toán Định tuyến UAV (UDRP)

## 1. Phát biểu bài toán (Problem Statement)
Bài toán tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP) yêu cầu phân bổ các tuyến bay từ trạm gốc (Depot) đến một tập hợp các điểm giao hàng (Delivery points) sao cho đáp ứng các yêu cầu về giới hạn pin, tải trọng, và né tránh khu vực cấm bay (No-fly zones).

## 2. Biến quyết định (Decision Variables)
- $x_{ijk} \in \{0, 1\}$: Biến nhị phân bằng `1` nếu UAV $k$ bay thẳng từ điểm $i$ đến điểm $j$, ngược lại bằng `0`.
- $t_i$: Biến liên tục thể hiện thời điểm UAV đến điểm $i$.
- $E_i$: Lượng pin còn lại của UAV khi đến điểm $i$.

## 3. Hàm mục tiêu (Objective Function)
Mục tiêu là tối thiểu hóa tổng chi phí hoạt động, bao gồm thời gian di chuyển, chi phí năng lượng tiêu thụ, và khoản phạt nếu giao trễ giờ (Time Windows).

$$ \text{Minimize} \quad Z = \alpha \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} d_{ij} x_{ijk} + \beta \sum_{i \in V} \max(0, t_i - L_i) $$

Trong đó:
- $V = \{0, 1, 2, ..., n, n+1\}$: Tập hợp các đỉnh, bao gồm Depot (0), các điểm giao hàng và các điểm sạc.
- $K$: Tập hợp các UAV.
- $d_{ij}$: Chi phí khoảng cách/thời gian bay thực tế từ $i$ đến $j$ (Được tính toán bởi thuật toán **A*** để tự động né tránh vùng cấm bay).
- $L_i$: Thời hạn giao hàng muộn nhất tại $i$.
- $\alpha, \beta$: Trọng số cân bằng giữa chi phí năng lượng và chi phí thời gian.

## 4. Các Ràng buộc (Constraints)
**4.1. Ràng buộc luồng giao hàng (Flow conservation):**
Mỗi điểm giao hàng chỉ được phục vụ đúng 1 lần bởi 1 UAV.
$$ \sum_{k \in K} \sum_{j \in V} x_{ijk} = 1 \quad \forall i \in \text{Delivery Points} $$

**4.2. Ràng buộc năng lượng pin (Energy constraint):**
Năng lượng tiêu thụ tỷ lệ thuận với khoảng cách bay và tải trọng mang theo. Pin của Drone không bao giờ được phép giảm xuống dưới mức an toàn $E_{min}$.
$$ E_j \le E_i - e(d_{ij}, w_j) \quad \text{nếu } x_{ijk} = 1 $$
Nếu UAV ghé trạm sạc, $E_j = E_{max}$.

**4.3. Ràng buộc vùng cấm bay (No-fly zone constraint):**
Đường đi thực tế giữa $i$ và $j$ không phải là đường thẳng Euclidean mà là đường đi ngắn nhất $A^*(i, j)$ trên đồ thị lưới không giao cắt với không gian của tập hợp $NFZ$ (No-fly zones).
$$ A^*(i, j) \cap NFZ = \emptyset \quad \forall i, j \text{ nếu } x_{ijk} = 1 $$
