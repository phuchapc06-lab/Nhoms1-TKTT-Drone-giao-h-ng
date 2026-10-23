"""
Bộ kiểm thử độc lập cho nhiệm vụ Thứ Sáu (Ngày 3 - 23/10/2026):
- Kiểm chứng thực nghiệm các Định lý Toán học & Tính đúng đắn của Thuật toán:
  1. Định lý 1: Tính tối ưu và né vật cản của A* Heuristic.
  2. Định lý 2: Tính bất biến bảo toàn lời giải hợp lệ của toán tử GA (OX và Swap).
  3. Định lý 3: Tính đơn điệu không tăng quãng đường của 2-Opt (d_new <= d_old).
  4. Định lý 4: Tính dừng và an toàn pin (E_battery >= 15%) của EnergyManager.
  5. Định lý 5: Tính không suy giảm của Hybrid GA Seeding (Cost_GA <= Cost_Greedy).
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import math
import random
import numpy as np

# Đảm bảo console Windows in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.local_search import two_opt_route, apply_2opt_to_solution
from algorithms.energy_manager import EnergyManager
from algorithms.fitness import FitnessCalculator
from models.optimized_astar import build_grid, astar
from pipeline import UAVRoutingPipeline


def test_ga_operators_invariance():
    print("\n[TEST 1] Kiểm chứng Định lý 2: Tính Bất biến Bảo toàn Lời giải Hợp lệ của GA:")
    num_deliveries = 20
    num_drones = 4
    nodes = {
        0: {"id": 0, "pos": (10, 10), "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0}
    }
    for i in range(1, num_deliveries + 1):
        nodes[i] = {"id": i, "pos": (i * 2, i * 2), "type": "delivery", "demand": 1.0, "tw": (10, 100), "service_time": 5}

    dist_matrix = np.zeros((num_deliveries + 1, num_deliveries + 1))
    ga = GeneticAlgorithm(nodes=nodes, dist_matrix=dist_matrix, num_drones=num_drones, seed=42)

    customer_set = set(range(1, num_deliveries + 1))
    expected_separators = set(range(-1, -num_drones, -1))
    expected_gene_set = customer_set | expected_separators

    # 1. Kiểm thử 100 lần phép lai ghép Order Crossover (OX)
    for trial in range(100):
        parent1 = ga._init_population()[0]
        parent2 = ga._init_population()[1]

        # Cắt ngẫu nhiên
        cut1, cut2 = sorted(random.sample(range(len(parent1)), 2))
        child = ga._order_crossover(parent1, parent2, cut=(cut1, cut2))

        assert len(child) == len(parent1), f"Trial {trial}: Chiều dài con {len(child)} phải bằng cha {len(parent1)}"
        assert set(child) == expected_gene_set, f"Trial {trial}: Con không bảo toàn đúng tập gen!"
        child_customers = [g for g in child if g > 0]
        assert len(child_customers) == num_deliveries, f"Trial {trial}: Số khách hàng {len(child_customers)} != {num_deliveries}"
        assert set(child_customers) == customer_set, f"Trial {trial}: Trùng hoặc thiếu khách hàng!"

    print("  -> Kiểm thử 100 phép lai ghép OX: 100% bảo toàn hoán vị hợp lệ (PASSED)")

    # 2. Kiểm thử 100 phép đột biến Swap Mutation
    for trial in range(100):
        chrom = ga._init_population()[0]
        mutant = ga._swap_mutation(chrom)
        assert len(mutant) == len(chrom), f"Trial {trial}: Chiều dài đột biến phải giữ nguyên"
        assert set(mutant) == expected_gene_set, f"Trial {trial}: Đột biến làm mất/trùng gen!"

    print("  -> Kiểm thử 100 phép đột biến Swap: 100% bảo toàn tập gen (PASSED)")


def test_astar_obstacle_avoidance_and_metric():
    print("\n[TEST 2] Kiểm chứng Định lý 1: Tính Tối ưu & Không giao cắt Vùng cấm bay của A*:")
    grid_size = (60, 60)
    # Vùng cấm bay chắn ngang giữa (10, 30) và (50, 30)
    no_fly_zones = [(20, 20, 20, 20)] # Hình chữ nhật từ x=20..40, y=20..40
    grid = build_grid(grid_size[0], grid_size[1], no_fly_zones)

    start = (10, 30) # Bên trái NFZ
    goal = (50, 30)  # Bên phải NFZ

    dist, path = astar(grid, start, goal)
    assert path is not None, "A* phải tìm thấy đường đi vòng qua NFZ"
    assert dist > 0, "Khoảng cách phải dương"

    # Kiểm tra không có bất kỳ điểm nào trên path nằm trong vùng cấm bay
    for (px, py) in path:
        assert not (20 <= px <= 40 and 20 <= py <= 40), f"Điểm ({px}, {py}) trên đường bay vi phạm NFZ!"

    # Đường vòng phải dài hơn đường thẳng Euclidean (40.0)
    straight_dist = math.dist(start, goal)
    assert dist > straight_dist, f"Đường bay né vật cản ({dist:.2f}) phải dài hơn đường thẳng ({straight_dist:.2f})"
    print(f"  -> Đường bay A* ({dist:.2f}) né hoàn toàn NFZ [20, 40] x [20, 40]: PASSED")


def test_2opt_monotonic_decrease():
    print("\n[TEST 3] Kiểm chứng Định lý 3: Tính Đơn điệu Không Tăng Quãng đường của 2-Opt:")
    # Tạo ma trận khoảng cách Euclidean ngẫu nhiên cho 8 điểm
    pts = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(8)]
    n = len(pts)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_mat[i, j] = math.dist(pts[i], pts[j])

    def calc_dist(route):
        return sum(dist_mat[route[i], route[i+1]] for i in range(len(route)-1))

    # Kiểm thử 50 tuyến đường ngẫu nhiên
    for trial in range(50):
        # Tuyến đường bắt đầu và kết thúc tại 0
        inner = list(range(1, n))
        random.shuffle(inner)
        initial_route = [0] + inner + [0]

        d_before = calc_dist(initial_route)
        optimized_route = two_opt_route(initial_route, dist_mat)
        d_after = calc_dist(optimized_route)

        assert d_after <= d_before + 1e-6, f"Trial {trial}: 2-Opt làm tăng quãng đường! Trước: {d_before}, Sau: {d_after}"
        assert optimized_route[0] == 0 and optimized_route[-1] == 0, "Tuyến đường phải bắt đầu và kết thúc tại 0"
        assert set(optimized_route) == set(initial_route), "2-Opt không được làm mất hoặc thêm đỉnh!"

    print("  -> Kiểm thử 50 trường hợp 2-Opt: 100% đơn điệu giảm hoặc bằng (d_after <= d_before): PASSED")


def test_energy_manager_termination_and_safety():
    print("\n[TEST 4] Kiểm chứng Định lý 4: Tính Dừng & Tính An toàn Pin (>= 15%):")
    nodes = {
        0: {"id": 0, "pos": (0, 0), "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "pos": (60, 0), "type": "delivery", "demand": 1.0, "tw": (10, 100), "service_time": 5},
        2: {"id": 2, "pos": (120, 0), "type": "delivery", "demand": 1.0, "tw": (20, 150), "service_time": 5},
        3: {"id": 3, "pos": (60, 10), "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 15},
    }
    num_nodes = len(nodes)
    dist_mat = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(num_nodes):
            dist_mat[i, j] = math.dist(nodes[i]["pos"], nodes[j]["pos"])

    em = EnergyManager(battery_capacity=300.0, min_battery_threshold=0.15)
    # Tuyến đường [0, 1, 2, 0] có tổng khoảng cách 60 + 60 + 120 = 240km, tiêu hao > 255Wh (vượt pin an toàn)
    long_route = [0, 1, 2, 0]

    repaired_route, is_feasible, energy_used = em.repair_route_with_charging(long_route, dist_mat, nodes)

    # 1. Thuật toán dừng và tìm được trạm sạc
    assert repaired_route is not None, "Thuật toán phải dừng và trả về tuyến đường"
    assert len(repaired_route) > len(long_route), "Phải chèn thêm trạm sạc vào tuyến"
    assert 3 in repaired_route, "Trạm sạc 3 phải xuất hiện trong tuyến đường"

    # 2. Kiểm tra an toàn pin
    total_energy, feasible_energy = em.calculate_route_energy(repaired_route, dist_mat, nodes)
    assert feasible_energy is True, "Tuyến đường sau khi chèn trạm sạc phải an toàn pin (Feasible)"
    print(f"  -> Tuyến gốc: {long_route} -> Tuyến đã chèn trạm sạc: {repaired_route} (An toàn pin: PASSED)")


def test_hybrid_ga_seeding_superiority():
    print("\n[TEST 5] Kiểm chứng Định lý 5: Tính Không Suy giảm của Hybrid GA Seeding:")
    pipeline = UAVRoutingPipeline(grid_size=(40, 40), num_drones=3, seed=42)
    pipeline.generate_synthetic_data(num_delivery=10, num_charging=2, num_no_fly=4)
    pipeline.compute_distance_matrix(use_astar=True, parallel=False)

    # Chạy Greedy
    res_greedy = pipeline.run_experiment(algorithm="greedy", save_figure_dir=None, show_plot=False)

    # Chạy GA có mồi Greedy (Seeding)
    res_ga = pipeline.run_experiment(
        algorithm="ga",
        save_figure_dir=None,
        show_plot=False,
        generations=80,
        pop_size=40,
        seed_greedy=True
    )

    # Định lý 5 khẳng định Cost(GA) <= Cost(Greedy) + dung sai epsilon
    assert res_ga["total_cost"] <= res_greedy["total_cost"] + 1e-4, (
        f"Cost GA ({res_ga['total_cost']}) không được lớn hơn Greedy ({res_greedy['total_cost']})!"
    )
    assert res_ga["fitness"] >= res_greedy["fitness"] - 1e-4, "Fitness GA phải >= Fitness Greedy!"
    print(f"  -> Chi phí Greedy Baseline: {res_greedy['total_cost']:.2f}")
    print(f"  -> Chi phí Hybrid GA:       {res_ga['total_cost']:.2f} (Tiết kiệm: {res_greedy['total_cost'] - res_ga['total_cost']:.2f})")
    print("  -> Tính không suy giảm Cost(GA) <= Cost(Greedy): PASSED")


def main():
    print("=" * 80)
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ THỨ SÁU (NGÀY 3) - THÀNH VIÊN 5   ")
    print("  Chức năng: Chứng minh Tính đúng đắn, Tính dừng & Bất biến Thuật toán ")
    print("=" * 80)

    test_ga_operators_invariance()
    test_astar_obstacle_avoidance_and_metric()
    test_2opt_monotonic_decrease()
    test_energy_manager_termination_and_safety()
    test_hybrid_ga_seeding_superiority()

    print("\n" + "=" * 80)
    print("  🎉 TẤT CẢ KIỂM THỬ THỨ SÁU (NGÀY 3) ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!  ")
    print("=" * 80)


if __name__ == "__main__":
    main()
