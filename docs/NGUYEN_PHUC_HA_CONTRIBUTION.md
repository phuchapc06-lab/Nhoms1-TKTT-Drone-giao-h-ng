# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL CONTRIBUTION REPORT)
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP)
**Sinh viên thực hiện:** Nguyễn Phúc Hà  
**Vai trò:** Nhóm trưởng / Kỹ sư Tích hợp Hệ thống & Đồ họa (Tech Lead & Integrator - Thành viên 5)  
**Nhánh GitHub cá nhân:** `nguyen-phuc-ha`  

---

## 📌 TỔNG QUAN PHẦN VIỆC ĐÃ ĐÓNG GÓP

Là Nhóm trưởng và người phụ trách tích hợp hệ thống, em (Nguyễn Phúc Hà) đã đảm nhận các phần việc cốt lõi sau:

### 1. Khởi tạo Dự án & Thiết kế Kiến trúc (System Architecture)
- Thiết lập cấu trúc thư mục dự án chuẩn theo mô hình nghiên cứu khoa học: `src/` (algorithms, models, utils), `data/` (raw, processed), `docs/`, `tests/`.
- Cấu hình file `requirements.txt` và file `.gitignore` chuẩn cho môi trường Python.
- Xây dựng **Giao kèo dữ liệu (Data Contract)** chuẩn hóa định dạng các đối tượng (Node, Route, Solution, Distance Matrix) để 5 thành viên có thể lập trình độc lập song song mà không bị xung đột.
- Thiết lập quy trình làm việc Git Flow trên GitHub (Quản lý các nhánh `main`, `develop`, và các nhánh tính năng `feature/*`).

---

### 2. Xây dựng Module Hàm mục tiêu & Độ thích nghi (Fitness Function)
- **File mã nguồn:** `src/algorithms/fitness.py`
- **Class chính:** `FitnessCalculator`
- **Nội dung thực hiện:**
  - Phát biểu và lập trình hàm tính chi phí tổng hợp đa mục tiêu (Multi-objective cost function):
    $$\text{Cost} = \alpha \cdot (\text{Tổng quãng đường}) + \beta \cdot (\text{Tổng năng lượng tiêu hao}) + \gamma \cdot (\text{Phạt trễ Time Window}) + \delta \cdot (\text{Phạt quá tải / cạn pin})$$
  - Xây dựng hàm tính độ thích nghi nghịch đảo cho giải thuật di truyền:
    $$\text{Fitness} = \frac{1000}{\text{Cost} + 1}$$
  - Tích hợp logic xử lý ràng buộc mềm (Penalty Mechanism): Phạt khi Drone đến muộn hơn khung giờ yêu cầu ($t > \text{end\_tw}$) và phạt khi vượt quá tải trọng cho phép ($Q > Q_{max}$).
  - Thiết kế sẵn giao diện mở để tích hợp trực tiếp với module Quản lý pin (`EnergyManager`) của Thành viên 3.

---

### 3. Xây dựng Module Trực quan hóa Lộ trình Đa UAV & Hội tụ (Visualization)
- **File mã nguồn:** `src/utils/visualizer.py`
- **Class chính:** `UAVVisualizer`
- **Nội dung thực hiện:**
  - `plot_multi_uav_routes()`: Vẽ toàn bộ không gian mô phỏng 2D với:
    - Các vùng cấm bay (**No-fly zones**) được hiển thị dạng hình khối viền đỏ, nền đỏ nhạt với hoa văn gạch chéo.
    - Trạm gốc (**Depot**) đánh dấu bằng biểu tượng ngôi sao vàng viền đen nổi bật.
    - Các trạm sạc pin (**Charging Stations**) đánh dấu bằng tam giác xanh lá.
    - Điểm giao hàng (**Delivery Points**) đánh dấu chấm tròn xanh dương kèm số ID.
    - Vẽ đường bay của từng Drone bằng **dải màu riêng biệt** (UAV 1 màu xanh dương, UAV 2 màu cam, UAV 3 màu xanh lá...), kèm theo mũi tên định hướng chặng bay.
  - `plot_convergence_curve()`: Vẽ biểu đồ đường cong hội tụ (Fitness Convergence Curve) qua từng thế hệ, phục vụ cho việc đánh giá tốc độ tối ưu hóa của thuật toán trong báo cáo khoa học.

---

### 4. Kiểm thử Độc lập (Unit Testing & Validation)
- **File mã nguồn:** `tests/test_member5.py`
- Đã xây dựng kịch bản kiểm thử giả lập với 5 điểm, 2 vùng cấm bay và 2 Drone.
- Kết quả kiểm thử: **100% Passed**, không có lỗi ngoại lệ (runtime exception), đồ thị được tạo và kết xuất chính xác.

---

## 📂 DANH MỤC CÁC FILE ĐÃ TẠO VÀ ĐÓNG GÓP
| STT | Tên File | Chức năng |
| :---: | :--- | :--- |
| 1 | `src/algorithms/fitness.py` | Lập trình Hàm mục tiêu đa ràng buộc & Fitness function cho GA |
| 2 | `src/utils/visualizer.py` | Lập trình trực quan hóa bản đồ đa UAV và biểu đồ hội tụ GA |
| 3 | `tests/test_member5.py` | Kịch bản Unit Test tự động kiểm tra tính đúng đắn của code |
| 4 | `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md` | Báo cáo chi tiết phần việc và minh chứng đóng góp cá nhân |
