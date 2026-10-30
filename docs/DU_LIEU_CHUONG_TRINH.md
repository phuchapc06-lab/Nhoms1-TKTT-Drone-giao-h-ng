# Tổng hợp tài liệu dữ liệu chương trình UDRP

## 1. Mục đích và phạm vi

Tài liệu này mô tả dữ liệu mà chương trình định tuyến UAV sử dụng: cấu trúc benchmark đầu vào, ý nghĩa các trường, cách chuẩn hóa/kiểm định, luồng xử lý và các dữ liệu kết quả được lưu. Nội dung tập trung vào dữ liệu chương trình; không trình bày bộ test case hoặc lệnh chạy test.

Tài liệu liên quan:

- [Mô hình toán học UDRP](./Mathematical_Model.md) — các ràng buộc tải trọng, pin, khung giờ và mục tiêu tối ưu.
- [README dự án](../README.md) — kiến trúc và tổng quan hệ thống.

## 2. Bản đồ dữ liệu trong dự án

| Nhóm | Vị trí | Mục đích | Định dạng |
|---|---|---|---|
| Benchmark đầu vào | `data/raw/benchmark_{10,50,100,500}.json` | Mô tả bản đồ, depot, điểm giao hàng, trạm sạc và vùng cấm bay | JSON |
| Dữ liệu sinh trong bộ nhớ | `src/utils/data_generator.py`, `src/utils/benchmark_generator.py`, `src/pipeline.py` | Tạo các kịch bản tổng hợp theo kích thước lưới và số lượng điểm | Dictionary Python |
| Ma trận khoảng cách và đường đi | `src/utils/distance_matrix.py` | Lưu khoảng cách giữa các node và đường đi chi tiết để tái sử dụng | NumPy array, dictionary; cache `.pkl` |
| Kết quả tổng hợp thực nghiệm | `data/processed/benchmark_comparison_results.csv` | So sánh chỉ số giữa Greedy và GA theo từng quy mô | CSV |
| Kết quả đo tốc độ | `data/processed/speedup_results.csv`, `data/processed/ga_speedup_results.csv` | Lưu thời gian, speedup và hiệu suất theo số worker | CSV |
| Báo cáo và biểu đồ | `docs/EXPERIMENT_RESULTS.md`, `docs/figures/` | Trình bày kết quả xử lý dữ liệu dưới dạng dễ đọc | Markdown, PNG |

`data/raw/` là dữ liệu kịch bản đầu vào; `data/processed/` chứa kết quả đã tính hoặc cache. Các file kết quả có thể được cập nhật khi chạy lại quy trình đánh giá, vì vậy số liệu trong CSV và báo cáo là kết quả tại thời điểm tạo file, không phải dữ liệu đầu vào cố định.

## 3. Khái niệm dữ liệu

| Khái niệm | Ý nghĩa |
|---|---|
| Depot | Trạm gốc để UAV xuất phát và quay về; dùng ID `0`. |
| Delivery | Điểm khách hàng cần được phục vụ một lần; có khối lượng hàng và khung giờ. |
| Charging | Trạm sạc; có thể được chèn vào tuyến để nạp pin. |
| No-fly zone (NFZ) | Vùng chữ nhật cấm bay, được dùng khi xây dựng lưới và tính đường đi. |
| Route | Danh sách ID node theo thứ tự UAV đi qua; có thể có depot và node sạc. |
| Distance matrix | Ma trận vuông `M × M`, trong đó `M` là số node và phần tử `[i, j]` là khoảng cách đi từ node `i` đến node `j`. |
| Detailed paths | Tọa độ các ô lưới tạo nên đường đi giữa từng cặp node. |

## 4. Hợp đồng dữ liệu benchmark

### 4.1. Các trường cấp cao

Benchmark JSON hiện dùng các trường sau:

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `name` | chuỗi | Tên kịch bản, ví dụ `UDRP_Benchmark_10`. |
| `map_size` | số nguyên | Kích thước bản đồ dạng một số; dùng làm phương án dự phòng khi thiếu `grid_size`. |
| `grid_size` | mảng `[width, height]` | Chiều rộng và chiều cao lưới tọa độ. Đây là trường ưu tiên khi nạp benchmark. |
| `num_customers` | số nguyên | Số điểm giao hàng dự kiến. Khi qua `load_benchmark`, giá trị này được tính lại từ `nodes`. |
| `num_charging` | số nguyên | Số trạm sạc. Khi qua `load_benchmark`, giá trị này được tính lại từ `nodes`. |
| `no_fly_zones` | mảng | Danh sách vùng cấm bay. |
| `nodes` | object hoặc mảng | Các node trong kịch bản; mỗi node phải có ID và loại hợp lệ. |

Benchmark phải có `nodes`, `no_fly_zones` và kích thước bản đồ (`grid_size` hoặc `map_size`). Cấu trúc `nodes` có thể là object với khóa là ID dạng chuỗi, hoặc mảng node có trường `id`.

### 4.2. Trường của node

| Trường | Kiểu / dạng | Ý nghĩa và quy ước |
|---|---|---|
| `id` | số nguyên | Định danh node. Depot là `0`; ID benchmark hiện tại được đánh liên tiếp. |
| `type` | chuỗi | Một trong `depot`, `delivery`, `charging`. |
| `pos` | `[x, y]` | Tọa độ node trên lưới bản đồ. |
| `demand` | số thực | Khối lượng hàng tính bằng kg; depot và trạm sạc thường là `0`. |
| `tw` | `[start, end]` | Khung giờ phục vụ, tính theo phút trong mô hình hiện tại; phải có `start <= end`. |
| `service_time` | số thực | Thời gian phục vụ node, tính theo phút. |

Quy ước của dữ liệu benchmark sinh tự động:

- Depot có `id = 0`, `demand = 0`, khung giờ `[0, 1000]` và thời gian phục vụ `0`.
- Delivery có ID bắt đầu từ `1`, nhu cầu dương, khung giờ hữu hạn và thời gian phục vụ `5` phút.
- Charging được đánh ID sau các delivery, có `demand = 0`, khung giờ `[0, 1000]` và thời gian phục vụ `15` phút.
- Sức tải UAV mặc định là `5 kg`; đây là tham số hệ thống, không phải thuộc tính từng node.

### 4.3. Vùng cấm bay

Định dạng benchmark JSON chính là mảng `[x, y, width, height]`, trong đó `(x, y)` là góc bắt đầu và `width`, `height` là kích thước hình chữ nhật. Bộ nạp dùng trong một số module cũng chấp nhận dạng object `{"id": ..., "bounds": [x_min, y_min, x_max, y_max]}` và chuẩn hóa về biên hình chữ nhật.

Khi `UAVRoutingPipeline` nạp dữ liệu, vùng dạng `[x, y, width, height]` được giữ theo quy ước kích thước. Dạng `bounds` được chuyển đổi thành `(x, y, width, height)` để xây dựng lưới.

### 4.4. Ví dụ rút gọn

```json
{
  "name": "UDRP_Benchmark_10",
  "map_size": 60,
  "grid_size": [60, 60],
  "num_customers": 1,
  "num_charging": 1,
  "no_fly_zones": [[17, 27, 5, 8]],
  "nodes": {
    "0": {
      "id": 0,
      "type": "depot",
      "pos": [30, 30],
      "demand": 0.0,
      "tw": [0.0, 1000.0],
      "service_time": 0.0
    },
    "1": {
      "id": 1,
      "type": "delivery",
      "pos": [46, 30],
      "demand": 0.8,
      "tw": [23.6, 68.4],
      "service_time": 5.0
    },
    "2": {
      "id": 2,
      "type": "charging",
      "pos": [20, 20],
      "demand": 0.0,
      "tw": [0.0, 1000.0],
      "service_time": 15.0
    }
  }
}
```

Ví dụ được rút gọn để minh họa cấu trúc, không đại diện cho số lượng node của bộ benchmark thực tế.

## 5. Nguồn tạo dữ liệu và các bộ benchmark

Có hai cách tạo dữ liệu tổng hợp trong mã nguồn:

1. `BenchmarkGenerator` trong `src/utils/benchmark_generator.py` tạo dữ liệu chuẩn hóa để lưu thành JSON. Depot được đặt giữa bản đồ; các điểm giao hàng và trạm sạc được sinh ngoài vùng cấm bay. Seed được kết hợp với số lượng delivery để tái lập kịch bản theo quy mô.
2. `UDRPDataGenerator` và `UAVRoutingPipeline.generate_synthetic_data` trong `src/utils/data_generator.py` và `src/pipeline.py` tạo dữ liệu dùng trực tiếp trong bộ nhớ. Dữ liệu node cuối cùng được pipeline bổ sung các trường theo Data Contract.

Các file benchmark hiện có trong `data/raw/`:

| File | Quy mô theo tên file |
|---|---:|
| `benchmark_10.json` | 10 điểm giao hàng |
| `benchmark_50.json` | 50 điểm giao hàng |
| `benchmark_100.json` | 100 điểm giao hàng |
| `benchmark_500.json` | 500 điểm giao hàng |

`BenchmarkGenerator` được cấu hình với kích thước lưới tăng theo quy mô. Seed giúp lặp lại dữ liệu có cùng cấu hình. Việc sinh vị trí có giới hạn số lần thử để tránh đặt node vào vùng cấm bay; vì vậy khi tùy chỉnh bản đồ quá chật, cần kiểm tra số lượng node thực tế trong file đầu ra thay vì chỉ dựa vào số lượng yêu cầu.

## 6. Kiểm định và chuẩn hóa

`DataContractValidator.validate_benchmark_data` kiểm tra cấu trúc benchmark trước khi sử dụng:

- Có kích thước bản đồ hợp lệ, `nodes` không rỗng và `no_fly_zones` là danh sách.
- Có depot ID `0`, ít nhất một delivery, và loại node thuộc nhóm cho phép.
- Mỗi node có tọa độ `pos` gồm hai phần tử; `demand` không âm.
- Nếu có `tw`, khung giờ gồm hai giá trị và thời điểm bắt đầu không sau thời điểm kết thúc.

Khi đọc benchmark, `load_benchmark` chuẩn hóa `nodes` về thứ tự ID, chuyển `pos` và `tw` sang tuple, tính lại các số đếm khách hàng/trạm sạc, và chuyển vùng cấm bay về dạng có `bounds`. Pipeline có bộ nạp riêng, chuẩn hóa node thành dictionary khóa số nguyên và giữ vùng cấm theo dạng tuple `(x, y, width, height)`.

Để dữ liệu được lập chỉ mục nhất quán trong ma trận khoảng cách, ID node cần liên tục từ `0` đến `M-1`, depot phải là `0`, và node dùng cho tính khoảng cách phải có `pos`. Bộ kiểm định ma trận xác nhận kích thước `M × M`, giá trị không âm và đường chéo chính bằng `0`. Tọa độ cũng cần nằm trong phạm vi `grid_size`, dù kiểm định benchmark hiện tại chưa xác nhận điều kiện này.

## 7. Luồng dữ liệu xử lý

1. **Nạp hoặc sinh kịch bản:** benchmark JSON được đọc thành danh sách/dictionary node nội bộ; hoặc pipeline tạo các node tổng hợp.
2. **Chuẩn hóa bản đồ:** xác định `grid_size`, node và vùng cấm bay.
3. **Tính đường đi:** tạo lưới có đánh dấu NFZ; với mỗi cặp node, dùng đường nhìn thẳng khi không vướng vật cản, nếu không thì tìm đường bằng A*. Kết quả gồm ma trận khoảng cách và các đường đi chi tiết.
4. **Tối ưu tuyến:** thuật toán nhận node, ma trận khoảng cách, số UAV và các tham số tải trọng/chi phí. Tuyến được biểu diễn bằng ID node; điểm sạc có thể được thêm vào để đáp ứng giới hạn pin.
5. **Đánh giá và xuất:** quy trình benchmark tổng hợp các chỉ số theo quy mô, lưu CSV, báo cáo Markdown và biểu đồ.

Ma trận khoảng cách được lưu cache mặc định tại `data/processed/distance_matrix.pkl`. Cache được nhận diện bằng fingerprint từ tọa độ node, vùng cấm bay và kích thước lưới; thay đổi các dữ liệu này sẽ tạo fingerprint khác. Ma trận có kích thước `M × M`, đối xứng trong cách tính hiện tại, đường chéo bằng `0`; `detailed_paths[(i, j)]` lưu dãy tọa độ của đường đi tương ứng.

## 8. Dữ liệu kết quả

### 8.1. CSV so sánh benchmark

`data/processed/benchmark_comparison_results.csv` có một dòng cho mỗi quy mô. Các cột gồm:

- Quy mô: `scale_n`, `drones_k`.
- Khoảng cách, năng lượng và chi phí của Greedy/GA: `greedy_dist`, `ga_dist`, `greedy_energy`, `ga_energy`, `greedy_cost`, `ga_cost`.
- Mức tiết kiệm tương ứng: `dist_saved_pct`, `energy_saved_pct`, `cost_saved_pct`.
- Tỷ lệ giao đúng giờ: `greedy_ontime_rate`, `ga_ontime_rate`.
- Hoạt động sạc: thời gian sạc, số lần sạc, mẫu tóm tắt chặng bay.
- An toàn pin: số tuyến không an toàn, trạng thái an toàn tổng thể và ngưỡng pin.
- Thời gian thực thi: `greedy_time_s`, `ga_time_s`.

Các trường có hậu tố `_pct` là phần trăm; thời gian thực thi dùng giây, thời gian sạc dùng phút. Những cột mô tả mẫu chặng bay là chuỗi văn bản, không phải bảng chi tiết từng chặng.

### 8.2. CSV đo tốc độ

- `speedup_results.csv`: quy mô, số node, số worker, thời gian, speedup, hiệu suất, số cặp node và tỷ lệ cặp dùng Line-of-Sight/A*.
- `ga_speedup_results.csv`: cấu hình GA, số worker, thời gian, mili giây mỗi thế hệ, speedup, hiệu suất và hệ số Karp–Flatt.

### 8.3. Các đầu ra khác

- `data/processed/distance_matrix.pkl`: cache khoảng cách và đường đi chi tiết.
- `data/processed/ga_demo_routes.png`, `data/processed/ga_demo_convergence.png`: hình minh họa tuyến và hội tụ GA.
- `docs/EXPERIMENT_RESULTS.md` cùng ảnh trong `docs/figures/`: báo cáo và biểu đồ tổng hợp kết quả.

## 9. Quy ước đơn vị và diễn giải

- Tọa độ `pos`, kích thước `grid_size` và khoảng cách là đơn vị tọa độ của bản đồ. Không có hệ số quy đổi tọa độ sang km được khai báo trong Data Contract.
- Khung giờ và `service_time` được tính bằng phút theo mô hình; vận tốc mặc định là `10` đơn vị khoảng cách/phút.
- `demand` và sức tải dùng kg. Sức tải drone mặc định là `5 kg`.
- Mô hình pin sử dụng dung lượng `300 Wh`, ngưỡng an toàn `15%`; tiêu hao tăng theo khoảng cách và tải hàng còn lại.
- Một số tên cột hoặc nội dung báo cáo dùng hậu tố “km”, nhưng dữ liệu benchmark hiện được sinh trên lưới tọa độ. Cần xác định hệ số quy đổi bản đồ trước khi diễn giải các giá trị đó là kilomet ngoài thực tế.

## 10. Các module dữ liệu liên quan

| Module | Trách nhiệm dữ liệu |
|---|---|
| `src/utils/benchmark_generator.py` | Sinh, lưu và nạp benchmark JSON; chuẩn hóa node và NFZ. |
| `src/utils/data_generator.py` | Sinh depot, điểm giao hàng, trạm sạc và vùng cấm bay tổng hợp. |
| `src/utils/validator.py` | Kiểm tra Data Contract, ma trận khoảng cách và tính hợp lệ của tuyến. |
| `src/utils/distance_matrix.py` | Tính, lưu cache và cung cấp ma trận khoảng cách/đường đi. |
| `src/pipeline.py` | Nạp dữ liệu, chuẩn hóa và điều phối các bước xử lý. |
| `src/utils/benchmark_evaluator.py` | Tổng hợp chỉ số và xuất dữ liệu đánh giá ra CSV/báo cáo/biểu đồ. |
| `docs/Mathematical_Model.md` | Định nghĩa các tham số và ràng buộc nghiệp vụ của dữ liệu. |
