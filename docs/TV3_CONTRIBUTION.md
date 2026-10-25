# BÁO CÁO ĐÓNG GÓP TV3 (NĂNG LƯỢNG & PIN)
## Đề tài: Tối ưu hóa định tuyến cho mạng giao vận Drone (UAV Delivery Routing Problem - UDRP)
**Vai trò:** Thành viên 3 — Kỹ sư Ràng buộc & Năng lượng  
**Phụ trách chuyên môn:** Mô hình tiêu hao pin theo tải trọng, kiểm tra ngưỡng an toàn, tự động chèn trạm sạc và bảo đảm tuyến bay không cạn pin.

---

## 📌 TỔNG QUAN PHẦN VIỆC ĐÃ ĐÓNG GÓP

TV3 chịu trách nhiệm cho lớp ràng buộc kỹ thuật quan trọng nhất của hệ thống: năng lượng pin của Drone. Mục tiêu là đảm bảo mọi tuyến bay thực tế đều được đánh giá dựa trên tiêu hao năng lượng thật, không chỉ theo quãng đường. Trong thực tế, năng lượng tiêu thụ phụ thuộc đồng thời vào khoảng cách và khối lượng hàng hóa đang chở; vì vậy, TV3 triển khai mô hình tiêu hao pin theo tải trọng, công thức kiểm tra pin an toàn và thuật toán tự động chèn trạm sạc khi pin sắp cạn.

Kết quả chính của TV3 là module `EnergyManager` nằm tại `src/algorithms/energy_manager.py`, được kết nối trực tiếp vào toàn bộ pipeline và kiểm thử với các bài kiểm tra độc lập ở `tests/test_energy_manager.py` cũng như script tích hợp `tests/test_day5_integration.py`.

---

### 1. Mô hình tiêu hao năng lượng theo tải trọng
- **File mã nguồn:** `src/algorithms/energy_manager.py`
- **Class chính:** `EnergyManager`
- **Mô hình tính toán:**

```text
E_segment = d * (c_base + alpha * payload)
```

Trong đó:
- `d`: quãng đường giữa hai điểm (km)
- `c_base`: tiêu hao cơ sở khi bay không tải (Wh/km)
- `alpha`: hệ số tăng thêm theo khối lượng hàng hóa (Wh/km/kg)
- `payload`: tải trọng đang mang trên chặng bay đó (kg)

Phương trình này phản ánh thực tế: khi Drone chở hàng nặng hơn, tiêu hao năng lượng tăng tuyến tính theo tải trọng. Điều này giúp đánh giá chính xác hơn so với mô hình chỉ dùng quãng đường.

---

### 2. Kiểm tra pin an toàn và ràng buộc kỹ thuật
TV3 xây dựng hai lớp kiểm soát:

1. `calculate_route_energy(route, dist_matrix, nodes)`  
   - Tính tổng năng lượng tiêu thụ trên toàn tuyến.
   - Giảm pin dần theo từng chặng bay.
   - Trả về `(total_energy, is_feasible)`.
   - Nếu đường bay vượt quá năng lượng pin hoặc bio pin rơi xuống dưới ngưỡng an toàn, tuyến bị đánh dấu không khả thi.

2. `min_safe_battery = battery_capacity * min_battery_threshold`  
   - Với ngưỡng mặc định `15%` (`min_battery_threshold = 0.15`).
   - Đảm bảo drone luôn giữ một lượng pin dự phòng đủ an toàn trước khi thực hiện tiếp chặng bay tiếp theo.

Điều này đáp ứng ràng buộc kỹ thuật trong tài liệu đề án: "Pin của Drone không bao giờ được phép giảm xuống dưới mức an toàn $E_{min}$".

---

### 3. Thuật toán tự động chèn trạm sạc
- **Hàm chính:** `repair_route_with_charging()`
- **Nội dung thực hiện:**
  - Duyệt từng đoạn đường từ điểm hiện tại đến điểm kế tiếp.
  - Nếu năng lượng cần bay tới điểm kế tiếp làm pin rơi xuống dưới ngưỡng an toàn thì tìm trạm sạc gần nhất có thể tiếp cận an toàn.
  - Chèn trạm sạc vào lộ trình trước khi đi tiếp.
  - Nếu không tìm được trạm nào phù hợp, đánh dấu tuyến là không khả thi và dừng xử lý.

Phương pháp này là chiến lược tối ưu tham lam trên từng bước: ưu tiên chèn trạm sạc mà tiêu hao bổ sung nhỏ nhất để bảo toàn tuyến và tránh đi vòng quá dài. Cơ chế này đã được bổ sung kiểm soát `best_cs not in repaired_route` để ngăn lặp vô hạn khi bị mắc kẹt ở cùng một trạm sạc.

Pseudo-code cơ bản:

```text
for each consecutive segment (u -> v):
    if battery_after_segment >= min_safe_battery:
        continue straight
    else:
        find charging station cs maximizing feasibility and minimizing detour
        if cs exists and cs not already in repaired_route:
            insert cs before v and recharge to full
        else:
            mark route as infeasible and terminate
```

---

### 4. Chứng minh tính dừng và tính an toàn
TV3 đóng góp phần chứng minh quan trọng cho phân tích độ phức tạp và tính đúng đắn:

#### a) Tính dừng (Termination)
Thuật toán chèn trạm sạc luôn tiến về một trong hai hướng:
- hoặc tiếp tục thêm một điểm mới vào tuyến, hoặc
- đánh dấu tuyến không khả thi và dừng.

Vì mỗi vòng lặp tăng `idx` hoặc chấm dứt tuyến, nên số lần lặp là hữu hạn. Ngoài ra, việc cấm chèn lại cùng một trạm sạc đã có trong đường đi đảm bảo không xảy ra trạng thái lặp lại vô hạn.

#### b) Bảo đảm pin luôn an toàn
Mỗi khi thực hiện một chặng bay, điều kiện kiểm tra là:

```text
battery_after_segment >= min_safe_battery
```

Nếu không thỏa mãn, thuật toán sẽ buộc chèn trạm sạc trước khi tiếp tục. Vì vậy, trên mọi điểm dừng, pin đều đảm bảo thỏa ngưỡng an toàn, đáp ứng yêu cầu kỹ thuật của hệ thống.

---

### 5. Đóng góp cho thực nghiệm và đánh giá chất lượng
TV3 cũng bổ sung các chỉ số và quy trình kiểm tra cho báo cáo nhóm:
- Tiêu hao năng lượng tổng cộng theo tuyến
- Tỷ lệ tuyến thiếu pin / không khả thi
- Đánh giá hiệu quả so với Greedy trong điều kiện pin hạn chế
- Chứng minh các tuyến đã chèn trạm sạc vẫn còn khả thi và không phá vỡ cấu trúc định tuyến

Trong các màn chạy thực nghiệm, `EnergyManager` được tích hợp vào hệ thống đánh giá và đảm bảo `GA` cũng như `Pipeline` không trả về lời giải bị thiếu pin dù có đối sánh với baseline.

---

### 6. Kiểm thử và xác thực
TV3 đã thực hiện các bài kiểm tra thực tế sau:

- `tests/test_energy_manager.py`
  - kiểm tra tiêu hao năng lượng theo tải trọng
  - kiểm tra phát hiện tuyến vi phạm pin
  - kiểm tra tự động chèn trạm sạc
  - kiểm tra cấu hình pin không hợp lệ
  - kiểm tra thời gian phục vụ trạm sạc

- `tests/test_day5_integration.py`
  - kiểm tra không xảy ra vòng lặp vô hạn khi pin không thể sửa được
  - xác nhận tuyến bị đánh dấu `infeasible` đúng cách

Các kiểm thử đều đạt kết quả 100% PASS trong quá trình tích hợp hệ thống.

---

## ✅ KẾT LUẬN

TV3 đóng vai trò là lớp ràng buộc sinh thái kỹ thuật của hệ thống UAV Delivery Routing Problem: quản lý năng lượng, đánh giá hành trình theo tải trọng thực tế và tự động chèn trạm sạc khi cần thiết. Nhờ đó, mọi lời giải tối ưu hóa sau khi đi qua `EnergyManager` đều có tính khả thi về mặt pin và đáp ứng đúng mục tiêu thực tế của đề tài.

Nội dung chính của TV3 bao gồm:
- mô hình lực lượng tiêu hao pin theo tải trọng,
- ngưỡng pin an toàn,
- thuật toán chèn trạm sạc tự động,
- kiểm tra tính dừng và bảo toàn an toàn pin,
- tích hợp kiểm thử và báo cáo kỹ thuật vào pipeline tổng thể.
