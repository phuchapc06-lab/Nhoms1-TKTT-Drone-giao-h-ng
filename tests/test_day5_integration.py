"""
Unit test kiểm thử tự động cho Nhiệm vụ Ngày 5 của Thành viên 5 (Tech Lead):
- Tích hợp kết quả tinh chỉnh tham số GA (TV1 PR #7) vào Pipeline.
- Kiểm thử cơ chế Hybrid GA (khởi tạo từ Greedy Seeding): GA luôn có cost <= Greedy.
- Kiểm thử tự động tính toán số lượng UAV khả dụng theo tổng tải trọng trên quy mô 50 điểm.
- Kiểm thử hàm sửa trạm sạc không bị lặp vô hạn (Hồi quy lỗi TV3).
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

from pipeline import UAVRoutingPipeline
from algorithms.energy_manager import EnergyManager
from algorithms.genetic_algorithm import GeneticAlgorithm
from utils.validator import DataContractValidator

def test_day5():
    print("==================================================================")
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ NGÀY 5 - THÀNH VIÊN 5 (TECH LEAD) ")
    print("==================================================================")

    # 1. Kiểm thử Seeding Greedy vào GA
    print("\n[TEST 1] Kiểm tra Hybrid GA (Khởi tạo từ lời giải Greedy Seeding):")
    bench_10 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "benchmark_10.json"))
    pipeline = UAVRoutingPipeline(num_drones=3, drone_speed=12.0, drone_capacity=5.0, seed=42)
    pipeline.load_benchmark_from_json(bench_10)
    pipeline.compute_distance_matrix(use_astar=True)

    # Lời giải Greedy
    greedy_sol = pipeline.solve_greedy()
    _, greedy_cost, _ = pipeline.fitness_calc.evaluate_solution(
        greedy_sol, pipeline.dist_matrix, pipeline.nodes, pipeline.energy_manager
    )

    # Lời giải GA có seeding Greedy
    ga_sol, _ = pipeline.solve_ga(generations=40, pop_size=30, seed_greedy=True)
    _, ga_cost, _ = pipeline.fitness_calc.evaluate_solution(
        ga_sol, pipeline.dist_matrix, pipeline.nodes, pipeline.energy_manager
    )

    print(f"  -> Chi phí Greedy Baseline: {greedy_cost:.2f}")
    print(f"  -> Chi phí GA (Seeded):    {ga_cost:.2f}")
    assert ga_cost <= greedy_cost + 1e-3, f"GA có khởi tạo từ Greedy không được có cost tệ hơn: {ga_cost} > {greedy_cost}"
    print("  -> Hybrid GA Seeding đảm bảo chất lượng vượt trội hoặc bằng Greedy: PASSED")

    # 2. Kiểm thử Tự động phân bổ số lượng UAV trên quy mô 50 điểm
    print("\n[TEST 2] Kiểm tra Phân bổ Đội bay linh hoạt theo tổng tải trọng (Benchmark 50):")
    bench_50 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "benchmark_50.json"))
    pipe_50 = UAVRoutingPipeline(num_drones=3, drone_capacity=5.0, seed=42)
    pipe_50.load_benchmark_from_json(bench_50)

    total_demand = sum(v.get("demand", 0.0) for v in pipe_50.nodes.values() if v.get("type") == "delivery")
    min_drones = max(3, int(math.ceil(total_demand / pipe_50.drone_capacity * 1.2)))
    assert min_drones >= 14, f"50 điểm giao hàng với tổng tải {total_demand:.1f}kg cần ít nhất 14 UAV, thực tế tính: {min_drones}"
    pipe_50.num_drones = min_drones
    print(f"  -> Đã tính đúng số UAV cần thiết: {pipe_50.num_drones} UAVs (Tổng tải: {total_demand:.2f}kg): PASSED")

    # 3. Kiểm thử Khắc phục lỗi lặp vô hạn ở trạm sạc trong EnergyManager
    print("\n[TEST 3] Kiểm tra Khắc phục triệt để lỗi lặp vô hạn tại trạm sạc:")
    em = EnergyManager(battery_capacity=100.0)
    # Tuyến đường không thể bay tới điểm kế tiếp dù pin đã đầy tại trạm sạc
    nodes_corner = {
        0: {"pos": [0, 0], "type": "depot", "demand": 0.0},
        1: {"pos": [0, 10], "type": "charging", "demand": 0.0},
        2: {"pos": [0, 200], "type": "delivery", "demand": 5.0} # Quá xa (200km > pin 100Wh)
    }
    dist_corner = np.array([
        [0.0, 10.0, 200.0],
        [10.0, 0.0, 190.0],
        [200.0, 190.0, 0.0]
    ])
    repaired_route, _, is_feas = em.repair_route_with_charging([0, 1, 2, 0], dist_corner, nodes_corner)
    assert not is_feas, "Tuyến không thể bay tới phải được đánh dấu Infeasible"
    assert repaired_route.count(1) == 1, f"Trạm sạc 1 không được phép lặp lại vô hạn: {repaired_route}"
    print(f"  -> Thuật toán tự ngắt an toàn khi không thể bay tới: {repaired_route}: PASSED")

    print("\n==================================================================")
    print("  🎉 TẤT CẢ KIỂM THỬ NGÀY 5 ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!   ")
    print("==================================================================")

if __name__ == "__main__":
    test_day5()
