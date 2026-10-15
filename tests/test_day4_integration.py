"""
Unit test kiểm thử tự động cho Cột mốc Tích hợp Hệ thống Ngày 4 (System Integration Milestone):
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
Kiểm thử tích hợp toàn diện:
1. Module TV3: EnergyManager (Quản lý pin, tiêu hao năng lượng, tự động chèn trạm sạc).
2. Module TV6: 2-Opt Local Search (Gỡ giao cắt, tối ưu cục bộ) & Baseline Greedy Router.
3. Module TV1 + TV2 + TV3 + TV4 + TV5 + TV6: UAVRoutingPipeline End-to-End trên benchmark_10.json.
"""
import sys
import os
import math
import numpy as np

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validator import DataContractValidator
from algorithms.energy_manager import EnergyManager
from algorithms.local_search import two_opt_route, apply_2opt_to_solution
from algorithms.baseline_greedy import GreedyRouter
from pipeline import UAVRoutingPipeline

def test_energy_manager():
    print("\n[TEST 1] Kiểm tra EnergyManager (Module TV3 do TV5 tích hợp):")
    em = EnergyManager(
        battery_capacity=100.0,
        base_consumption=1.0,
        payload_factor=0.2,
        min_battery_threshold=0.20
    )

    # 1.1 Kiểm tra tiêu hao chặng đơn
    e_seg = em.calculate_segment_energy(distance=10.0, cargo_weight=2.0)
    expected_e = 10.0 * (1.0 + 0.2 * 2.0) # = 14.0 Wh
    assert abs(e_seg - expected_e) < 1e-4, f"Sai năng lượng tiêu hao chặng: {e_seg} != {expected_e}"
    print(f"  -> Tiêu hao chặng đơn (10km, 2kg): {e_seg:.2f} Wh == {expected_e:.2f} Wh: PASSED")

    # 1.2 Tạo kịch bản tuyến đường cần sạc pin
    # Khoảng cách Depot -> Node 1 -> Node 2 -> Depot rất xa khiến cạn pin nếu không sạc
    # Node 3 là trạm sạc nằm giữa đường
    nodes = {
        0: {"pos": [0, 0], "type": "depot", "demand": 0.0, "tw": [0, 100], "service_time": 0},
        1: {"pos": [0, 40], "type": "delivery", "demand": 1.0, "tw": [0, 100], "service_time": 2},
        2: {"pos": [0, 80], "type": "delivery", "demand": 1.0, "tw": [0, 100], "service_time": 2},
        3: {"pos": [0, 45], "type": "charging", "demand": 0.0, "tw": [0, 100], "service_time": 10}
    }
    # Ma trận khoảng cách Manhattan đơn giản
    dist_matrix = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            dist_matrix[i, j] = abs(nodes[i]["pos"][1] - nodes[j]["pos"][1])

    # Tuyến ban đầu: [0, 1, 2, 0] -> Tổng khoảng cách 40 + 40 + 80 = 160km -> tiêu hao > 160Wh > Pin 100Wh
    route_raw = [0, 1, 2, 0]
    tot_e, is_feas = em.calculate_route_energy(route_raw, dist_matrix, nodes)
    assert not is_feas, "Tuyến 160km với pin 100Wh phải bị đánh dấu Không khả thi (Infeasible)"
    print("  -> Phát hiện tuyến vượt quá giới hạn Pin: PASSED")

    # 1.3 Kiểm tra tự động sửa tuyến bằng trạm sạc: repair_route_with_charging
    repaired, repaired_energy, repaired_feas = em.repair_route_with_charging(route_raw, dist_matrix, nodes)
    assert 3 in repaired, f"Tuyến sửa bắt buộc phải chèn trạm sạc (Node 3): {repaired}"
    assert repaired[0] == 0 and repaired[-1] == 0, "Tuyến sửa phải bắt đầu và kết thúc tại Depot"
    assert 1 in repaired and 2 in repaired, "Tuyến sửa không được làm mất các điểm giao hàng"
    print(f"  -> Tự động chèn trạm sạc thành công: {route_raw} -> {repaired}: PASSED")

def test_local_search_2opt():
    print("\n[TEST 2] Kiểm tra 2-Opt Local Search (Module TV6 do TV5 tích hợp):")
    # Tạo 4 điểm hình vuông: (0,0), (0,10), (10,10), (10,0)
    # Tuyến cắt chéo hình số 8: 0 -> (0,0) -> (10,10) -> (0,10) -> (10,0) -> (0,0)
    # Tọa độ: 0: (0,0), 1: (10,10), 2: (0,10), 3: (10,0)
    # Tuyến chéo: [0, 1, 2, 3, 0]
    # Khoảng cách tuyến chéo: d(0,1)=sqrt(200)=14.14, d(1,2)=10, d(2,3)=sqrt(200)=14.14, d(3,0)=10 => Tổng ~ 48.28
    # Tuyến chuẩn (chu vi hình vuông): [0, 2, 1, 3, 0] hoặc [0, 3, 1, 2, 0] => Tổng = 10 + 10 + 10 + 10 = 40.0
    coords = {0: (0, 0), 1: (10, 10), 2: (0, 10), 3: (10, 0)}
    dist_mat = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            dist_mat[i, j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])

    crossed_route = [0, 1, 2, 3, 0]
    optimized_route = two_opt_route(crossed_route, dist_mat)

    def calc_dist(r):
        return sum(dist_mat[r[k], r[k+1]] for k in range(len(r)-1))

    dist_before = calc_dist(crossed_route)
    dist_after = calc_dist(optimized_route)

    assert dist_after < dist_before, f"2-Opt phải cải thiện quãng đường: {dist_after} < {dist_before}"
    assert abs(dist_after - 40.0) < 1e-3, f"Khoảng cách tối ưu phải là 40.0, thực tế: {dist_after}"
    print(f"  -> Gỡ giao cắt thành công: {dist_before:.2f}km -> {dist_after:.2f}km (Tiết kiệm {((dist_before-dist_after)/dist_before)*100:.1f}%): PASSED")

    # Kiểm tra áp dụng cho multi-route solution
    sol = [[0, 1, 2, 3, 0], [0, 2, 1, 3, 0]]
    opt_sol = apply_2opt_to_solution(sol, dist_mat)
    assert len(opt_sol) == 2
    print("  -> Áp dụng 2-Opt cho toàn bộ đội bay (apply_2opt_to_solution): PASSED")

def test_greedy_router():
    print("\n[TEST 3] Kiểm tra Baseline Greedy Router (Module TV6 do TV5 tích hợp):")
    nodes = {
        0: {"pos": [0, 0], "type": "depot", "demand": 0.0},
        1: {"pos": [1, 1], "type": "delivery", "demand": 2.0},
        2: {"pos": [2, 2], "type": "delivery", "demand": 2.0},
        3: {"pos": [3, 3], "type": "delivery", "demand": 2.0},
    }
    dist_mat = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            dist_mat[i, j] = math.hypot(nodes[i]["pos"][0] - nodes[j]["pos"][0], nodes[i]["pos"][1] - nodes[j]["pos"][1])

    router = GreedyRouter(nodes=nodes, dist_matrix=dist_mat, num_drones=2, drone_capacity=5.0)
    solution = router.solve()

    validator = DataContractValidator()
    is_valid, errors = validator.validate_solution(solution, nodes, drone_capacity=5.0)
    assert is_valid, f"Lời giải Greedy không hợp lệ: {errors}"
    assert len(solution) == 2, "Phải có đúng 2 tuyến cho 2 Drone"
    print(f"  -> Lời giải Greedy Baseline hợp lệ với {len(solution)} UAVs: PASSED")

def test_day4_pipeline_integration():
    print("\n[TEST 4] Kiểm tra Ghép nối Toàn diện End-to-End UAVRoutingPipeline (Cột mốc Ngày 4):")
    benchmark_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "benchmark_10.json"))
    assert os.path.exists(benchmark_file), f"Không tìm thấy file {benchmark_file}"

    # Khởi tạo Pipeline tích hợp toàn bộ các thành phần
    pipeline = UAVRoutingPipeline(
        num_drones=3,
        drone_speed=12.0,
        drone_capacity=5.0
    )
    loaded = pipeline.load_benchmark_from_json(benchmark_file)
    assert loaded, "Phải nạp thành công file benchmark_10.json"

    assert pipeline.energy_manager is not None, "EnergyManager phải được nạp vào Pipeline"
    print("  -> Khởi tạo Pipeline với đầy đủ A*, EnergyManager, 2-Opt, GA, Greedy: PASSED")

    # Tính ma trận khoảng cách tối ưu
    pipeline.compute_distance_matrix(use_astar=True)
    assert pipeline.dist_matrix is not None
    print(f"  -> Tính ma trận khoảng cách A* ({pipeline.dist_matrix.shape}): PASSED")

    output_fig_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "figures"))

    # 4.1 Chạy Greedy Baseline
    print("  -> Đang thực thi thuật toán Baseline Greedy (kèm 2-Opt & Energy check)...")
    res_greedy = pipeline.run_experiment(algorithm="greedy", save_figure_dir=output_fig_dir, show_plot=False)
    assert res_greedy["is_valid"], f"Greedy vi phạm Data Contract: {res_greedy['errors']}"
    assert res_greedy["energy"] >= 0
    assert res_greedy["total_cost"] > 0
    print(f"     Greedy Cost: {res_greedy['total_cost']:.2f} (Quãng đường: {res_greedy['distance']:.2f}km, Năng lượng: {res_greedy['energy']:.2f}Wh)")

    # 4.2 Chạy GA Meta-heuristic
    print("  -> Đang thực thi thuật toán GA Meta-heuristic (kèm 2-Opt & Energy check)...")
    res_ga = pipeline.run_experiment(algorithm="ga", save_figure_dir=output_fig_dir, show_plot=False)
    assert res_ga["is_valid"], f"GA vi phạm Data Contract: {res_ga['errors']}"
    assert res_ga["energy"] >= 0
    assert res_ga["total_cost"] > 0
    print(f"     GA Cost: {res_ga['total_cost']:.2f} (Quãng đường: {res_ga['distance']:.2f}km, Năng lượng: {res_ga['energy']:.2f}Wh)")

    # 4.3 Kiểm tra file ảnh nghiệm thu xuất ra
    expected_fig = os.path.join(output_fig_dir, "route_ga.png")
    assert os.path.exists(expected_fig), f"Không tạo được file ảnh {expected_fig}"
    assert os.path.getsize(expected_fig) > 0, "File ảnh trực quan hóa bị rỗng"
    print(f"  -> Đã xuất trực quan hóa tuyến bay hoàn chỉnh: {expected_fig} ({os.path.getsize(expected_fig)} bytes): PASSED")

def run_all():
    print("==================================================================")
    print("  BẮT ĐẦU KIỂM THỬ CỘT MỐC TÍCH HỢP HỆ THỐNG NGÀY 4 - THÀNH VIÊN 5 ")
    print("  (Tech Lead: Ghép nối TV1 GA, TV2 A*, TV3 Pin, TV6 2-Opt & Baseline)")
    print("==================================================================")
    test_energy_manager()
    test_local_search_2opt()
    test_greedy_router()
    test_day4_pipeline_integration()
    print("\n==================================================================")
    print("  🎉 TẤT CẢ KIỂM THỬ CỘT MỐC NGÀY 4 ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ! ")
    print("==================================================================")

if __name__ == "__main__":
    run_all()
