# Nhoms1-TKTT-Drone-giao-h-ng
# UAV Delivery Routing Problem (UDRP)

## 📌 Tổng quan Dự án (Project Overview)
Dự án tập trung vào việc thiết kế, phân tích và triển khai các thuật toán tối ưu hóa định tuyến cho đội bay UAV (Drone) phục vụ giao hàng trong đô thị thông minh. Bài toán đòi hỏi sự cân bằng giữa:
- Năng lượng tiêu thụ (Dung lượng pin)
- Tải trọng tối đa của Drone
- Thời gian giao hàng (Time Windows)
- Tránh các khu vực cấm bay (No-fly zones)

## 🏗️ Kiến trúc thuật toán (Architecture)
1. **Mô hình hóa:** Không gian 2D/3D bằng Đồ thị lưới (Grid Graph).
2. **Tìm đường đi ngắn nhất (Pathfinding):** Thuật toán A* (A-Star) tránh vật cản và vùng cấm bay.
3. **Định tuyến & Phân bổ (Routing & Assignment):** Sử dụng Genetic Algorithm (GA) để tối ưu hóa thứ tự các điểm giao hàng cho từng UAV, tính đến trạm sạc khi hết pin.

## 📂 Cấu trúc thư mục (Directory Structure)
```
uav-routing-project/
├── data/
│   ├── raw/                 # Dữ liệu thô (tọa độ điểm giao, no-fly zones, trạm sạc)
│   └── processed/           # Dữ liệu đã qua tiền xử lý
├── docs/                    # Báo cáo, slide thuyết trình, tài liệu tham khảo
├── src/                     # Mã nguồn chính
│   ├── algorithms/          # Chứa các thuật toán Heuristic (GA, ACO)
│   ├── models/              # Chứa Baseline (A* / Dijkstra) và định nghĩa Class
│   ├── utils/               # Các hàm hỗ trợ (vẽ biểu đồ, sinh dữ liệu ngẫu nhiên)
│   └── main.py              # File thực thi chính
├── tests/                   # Các kịch bản kiểm thử thuật toán
├── requirements.txt         # Các thư viện Python cần thiết
└── README.md                # Tài liệu hướng dẫn (File này)
```

## 🚀 Hướng dẫn cài đặt (Installation)
1. Cài đặt Python 3.9+
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## 🗓️ Lộ trình thực hiện (Roadmap)
- [ ] **Tuần 1:** Nghiên cứu & Mô hình hóa bài toán thành đồ thị Grid Graph. Sinh tập dữ liệu thử nghiệm.
- [ ] **Tuần 2:** Lập Baseline bằng thuật toán A*/Dijkstra né vật cản. Xây dựng hàm mục tiêu toán học.
- [ ] **Tuần 3:** Thiết kế Giải thuật Genetic Algorithm (GA) để tối ưu thứ tự giao hàng.
- [ ] **Tuần 4:** Tích hợp ràng buộc pin, tải trọng, vùng cấm bay. Tự động chèn điểm sạc.
- [ ] **Tuần 5:** Thực nghiệm, đo đạc chỉ số (Thời gian, Năng lượng tiêu thụ).
- [ ] **Tuần 6:** Phân tích độ phức tạp, biểu đồ so sánh.
- [ ] **Tuần 7:** Đóng gói, viết báo cáo & chuẩn bị slide.
