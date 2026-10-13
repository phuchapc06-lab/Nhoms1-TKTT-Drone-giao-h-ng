# CLAUDE.md

Bài tập lớn môn Phân tích & Thiết kế Thuật toán (NEU) — **UAV Delivery Routing Problem (UDRP)**: định tuyến đa Drone giao hàng, né vùng cấm bay (A*), ràng buộc tải trọng / pin / khung giờ, tối ưu bằng Genetic Algorithm và so sánh với baseline Greedy + 2-Opt. Nhóm 6 người làm song song, mỗi người một module; nhóm trưởng (TV5) tích hợp.

## Lệnh thường dùng

Chạy từ thư mục gốc repo. Môi trường ảo nằm ở `../venv` (Python 3.14, đã cài đủ `requirements.txt`).

```bash
../venv/Scripts/python.exe -m pip install -r requirements.txt   # cài lần đầu
../venv/Scripts/python.exe src/main.py                          # demo A* (mở cửa sổ matplotlib)
MPLBACKEND=Agg ../venv/Scripts/python.exe tests/test_member5.py # test không bật cửa sổ
MPLBACKEND=Agg ../venv/Scripts/python.exe tests/test_ga.py      # test GA (~2s), lưu hình demo vào data/processed/
```

- Test là script thường (có hàm `test_*` nên cũng chạy được bằng pytest, nhưng pytest không có trong `requirements.txt`). Mỗi file test tự thêm `src/` vào `sys.path`.
- Import trong code dùng dạng `from utils.x import ...`, `from algorithms.x import ...` (gốc là `src/`), không dùng `src.` prefix.
- Windows console: in tiếng Việt có thể lỗi encoding → đầu script test gọi `sys.stdout.reconfigure(encoding='utf-8')` như `tests/test_member5.py`.

## Cấu trúc & trạng thái module

| Module | File | Chủ | Trạng thái |
|---|---|---|---|
| Sinh dữ liệu cũ | `src/utils/data_generator.py` (`UDRPDataGenerator`) | — | Có, nhưng chỉ sinh tọa độ tuple, chưa có demand/tw, chưa theo Data Contract |
| A* baseline | `src/models/baseline_astar.py` (`astar`) | — | Có (heapq, 8 hướng, Euclid) |
| Fitness | `src/algorithms/fitness.py` (`FitnessCalculator`) | TV5 | Xong |
| Visualizer | `src/utils/visualizer.py` (`UAVVisualizer`) | TV5 | Xong |
| GA | `src/algorithms/genetic_algorithm.py` (`GeneticAlgorithm`) | TV1 | Chạy được trên dữ liệu giả (nhánh `feature/tv1-ga-core`); chờ tích hợp dữ liệu thật |
| A* tối ưu + ma trận | `src/models/optimized_astar.py`, `src/utils/distance_matrix.py` | TV2 | Chưa có |
| Pin / trạm sạc | `src/algorithms/energy_manager.py` (`EnergyManager`) | TV3 | Chưa có |
| Benchmark | `src/utils/benchmark_generator.py`, `data/raw/benchmark_*.json` | TV4 | Chưa có |
| Greedy + 2-Opt | `src/algorithms/baseline_greedy.py` (`GreedyRouter`), `src/algorithms/local_search.py` (`two_opt_route`) | TV6 | Chưa có |
| Pipeline | `src/main.py` | TV5 | Mới chỉ demo 1 đường A*, chưa ghép GA/fitness/visualizer |

Kế hoạch phân công của nhóm nằm trong file `KE_HOACH_PHAN_CONG_NHOM_6_NGUOI.txt` (không có trong repo).

## Data Contract (bắt buộc giữ nguyên để ghép code)

```python
nodes = {                       # dict: id -> node  (FitnessCalculator & Visualizer nhận dạng này)
    0: {"id": 0, "type": "depot",    "pos": (x, y), "demand": 0.0, "tw": (t_min, t_max), "service_time": 0},
    1: {"id": 1, "type": "delivery", "pos": (x, y), "demand": 2.0, "tw": (5, 60),       "service_time": 5},
    # id 0 = depot, 1..N = khách hàng, N+1.. = trạm sạc ("charging")
}
dist_matrix   # numpy 2D (hoặc list), dist_matrix[i][j] = khoảng cách A* đã né NFZ
solution = [[0, 1, 4, 0], [0, 2, 5, 3, 0]]   # mỗi list = 1 Drone, bắt đầu & kết thúc ở depot 0
no_fly_zones = [(x, y, w, h), ...]          # hình chữ nhật, biên tính bao gồm (<=)
detailed_paths = {(i, j): [(x, y), ...]}    # tùy chọn, cho Visualizer vẽ đường né vật cản
```

Đơn vị thời gian: phút. `FitnessCalculator.drone_speed` = đơn vị lưới / phút (mặc định 10).

## Giao diện giữa các module

- `GeneticAlgorithm(nodes, dist_matrix, num_drones, energy_manager=None, pop_size=80, generations=300, mutation_rate=0.2, seed=None, ...).evolve() -> (best_solution, best_fitness, history)`; sau khi chạy có thêm `best_cost`, `best_breakdown`, `runtime`. Chromosome = hoán vị khách hàng + K-1 vách ngăn số âm; chỉ node `type == "delivery"` được đưa vào chromosome.

- `FitnessCalculator.evaluate_solution(solution, dist_matrix, nodes, energy_manager=None) -> (fitness, total_cost, breakdown)`; `fitness = 1000 / (cost + 1)`, càng cao càng tốt.
- Nếu truyền `energy_manager`, fitness gọi **`energy_manager.calculate_route_energy(route, dist_matrix, nodes) -> (total_energy, is_feasible)`**. TV3 phải cài đúng chữ ký này; `is_feasible=False` bị phạt `delta`.
- Không có `energy_manager` → fitness ước lượng `E = tổng quãng đường * (1 + 0.1 * tổng tải)`.
- `UAVVisualizer.plot_multi_uav_routes(nodes, no_fly_zones, solution, detailed_paths=None, save_path=None, show=True)` và `plot_convergence_curve(history_fitness, ...)` — GA cần trả về lịch sử best fitness theo thế hệ.

## Lưu ý / điểm dễ sai

- `calculate_route_cost` cộng demand của **cả tuyến** để kiểm tra tải trọng — nếu một route quay về depot giữa chừng (`[0,1,0,2,0]`) thì tải vẫn bị cộng dồn. Nên tách mỗi chuyến thành một route riêng.
- `docs/Mathematical_Model.md` dùng `β` cho phạt trễ giờ, còn code dùng `β` cho năng lượng và `γ` cho phạt trễ — khi viết báo cáo theo ký hiệu trong code.
- `UDRPDataGenerator` có thể đặt điểm giao/trạm sạc **bên trong vùng cấm bay** → `astar` trả `None`. Code tính ma trận phải xử lý trường hợp không tới được (vd. `inf`).
- `UDRPDataGenerator` gọi `np.random.seed` toàn cục — ảnh hưởng mọi random khác cùng tiến trình.
- `data/raw/*` và `data/processed/*` bị `.gitignore` (trừ `.gitkeep`) — file benchmark/cache muốn commit phải `git add -f`.

## Quy trình Git

- `main`: bản chính thức; `develop`: nhánh tích hợp. Nhánh cá nhân tạo từ `develop`: `feature/tvX-<ten-nhiem-vu>`, PR vào `develop`, TV5 duyệt.
- Commit message dạng `feat(module): mô tả`.
- Hiện `main` đi trước `origin/develop` 1 commit (file `docs/NGUYEN_PHUC_HA_CONTRIBUTION.md`).
