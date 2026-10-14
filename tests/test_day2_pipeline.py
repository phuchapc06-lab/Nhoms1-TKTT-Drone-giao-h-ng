"""
Unit test kiem thu toan dien cho Ngay 2 cua Thanh vien 5 (Pipeline & Validator).
"""
import sys
import os
import shutil

import numpy as np

# Dam bao in tieng Viet UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Them src vao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validator import DataContractValidator
from pipeline import UAVRoutingPipeline

def test_day2():
    print("==================================================================")
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ NGÀY 2 - THÀNH VIÊN 5 (TECH LEAD) ")
    print("==================================================================")

    # -------------------------------------------------------------
    # 1. KIEM THU DATA CONTRACT VALIDATOR
    # -------------------------------------------------------------
    print("\n[TEST 1] Kiem tra DataContractValidator:")
    validator = DataContractValidator()

    # 1.1 Du lieu hop le
    valid_data = {
        "grid_size": (50, 50),
        "no_fly_zones": [(10, 10, 5, 5)],
        "nodes": {
            0: {"id": 0, "type": "depot", "pos": (5, 5), "demand": 0.0, "tw": (0, 100)},
            1: {"id": 1, "type": "delivery", "pos": (15, 20), "demand": 2.0, "tw": (10, 50)},
            2: {"id": 2, "type": "charging", "pos": (30, 30), "demand": 0.0, "tw": (0, 100)}
        }
    }
    is_ok, errs = validator.validate_benchmark_data(valid_data)
    assert is_ok, f"Du lieu hop le nhung bi bao loi: {errs}"
    print("  -> Validate benchmark hop le: PASSED")

    # 1.2 Du lieu thieu Depot (0)
    invalid_data = {
        "grid_size": (50, 50),
        "no_fly_zones": [],
        "nodes": {
            1: {"id": 1, "type": "delivery", "pos": (15, 20), "demand": 2.0}
        }
    }
    is_ok, errs = validator.validate_benchmark_data(invalid_data)
    assert not is_ok, "Phai phat hien loi thieu Depot"
    print(f"  -> Bat dung loi thieu Depot: PASSED ({errs[0]})")

    # 1.3 Kiem tra validate solution
    nodes_test = {
        0: {"id": 0, "type": "depot", "demand": 0.0},
        1: {"id": 1, "type": "delivery", "demand": 1.5},
        2: {"id": 2, "type": "delivery", "demand": 2.0},
    }
    good_sol = [[0, 1, 0], [0, 2, 0]]
    is_sol_ok, s_errs = validator.validate_solution(good_sol, nodes_test, drone_capacity=5.0)
    assert is_sol_ok, f"Solution hop le nhung bi loi: {s_errs}"
    print("  -> Validate solution hop le: PASSED")

    # Solution bi trung diem va bo sot diem
    bad_sol = [[0, 1, 1, 0]] # Thieu diem 2, trung diem 1
    is_bad_ok, b_errs = validator.validate_solution(bad_sol, nodes_test, drone_capacity=5.0)
    assert not is_bad_ok, "Phai bat duoc loi trung diem va bo sot"
    print(f"  -> Bat dung loi trung diem / bo sot khach: PASSED (Phat hien {len(b_errs)} loi)")

    # -------------------------------------------------------------
    # 2. KIEM THU INTEGRATION PIPELINE
    # -------------------------------------------------------------
    print("\n[TEST 2] Kiem tra UAVRoutingPipeline E2E:")
    test_fig_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "figures"))
    os.makedirs(test_fig_dir, exist_ok=True)

    pipeline = UAVRoutingPipeline(
        grid_size=(40, 40),
        num_drones=3,
        drone_capacity=5.0,
        seed=123
    )

    # 2.1 Sinh du lieu
    pipeline.generate_synthetic_data(num_delivery=6, num_charging=2, num_no_fly=3)
    assert len(pipeline.nodes) == 9 # 1 depot + 6 delivery + 2 charging
    print("  -> Khoi tao & sinh du lieu hop le: PASSED")

    # 2.2 Tinh ma tran khoang cach
    pipeline.compute_distance_matrix(use_astar=True)
    assert pipeline.dist_matrix.shape == (9, 9)
    print("  -> Tinh ma tran khoang cach A* (9x9): PASSED")

    # 2.3 Chay thuat toan Greedy
    res_greedy = pipeline.run_experiment(algorithm="greedy", save_figure_dir=test_fig_dir, show_plot=False)
    assert res_greedy["is_valid"], f"Greedy solution bi vi pham rang buoc: {res_greedy['errors']}"
    print(f"  -> Chay Greedy Baseline thanh cong (Cost: {res_greedy['total_cost']}): PASSED")

    # 2.4 Chay thuat toan GA
    res_ga = pipeline.run_experiment(algorithm="ga", save_figure_dir=test_fig_dir, show_plot=False)
    assert res_ga["is_valid"], f"GA solution bi vi pham rang buoc: {res_ga['errors']}"
    print(f"  -> Chay GA Meta-heuristic thanh cong (Cost: {res_ga['total_cost']}): PASSED")

    # 2.5 Kiem tra file anh xuat ra dia
    expected_files = [
        os.path.join(test_fig_dir, "route_greedy.png"),
        os.path.join(test_fig_dir, "route_ga.png"),
        os.path.join(test_fig_dir, "convergence_ga.png")
    ]
    for ef in expected_files:
        assert os.path.exists(ef), f"Khong tim thay file anh xuat ra: {ef}"
    print("  -> Kiem tra xuat file anh ban do & hoi tu: PASSED")

    print("\n==================================================================")
    print("  🎉 TẤT CẢ KIỂM THỬ NGÀY 2 ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!   ")
    print("==================================================================")

def test_pipeline_inserts_charging_stops():
    pipeline = UAVRoutingPipeline(num_drones=1, drone_capacity=5.0)
    pipeline.nodes = {
        0: {"id": 0, "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
        2: {"id": 2, "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 15},
    }
    pipeline.dist_matrix = np.array([
        [0.0, 50.0, 20.0],
        [60.0, 0.0, 20.0],
        [20.0, 20.0, 0.0],
    ])

    result = pipeline.run_experiment(
        algorithm="greedy", save_figure_dir=None, show_plot=False
    )

    assert result["is_valid"], result["errors"]
    assert result["solution"] == [[0, 1, 2, 0]]
    assert result["distance"] == 90.0
    assert result["energy"] == 95.0

def test_pipeline_is_valid_when_at_least_one_delivery_route_is_energy_feasible():
    pipeline = UAVRoutingPipeline(num_drones=2, drone_capacity=5.0)
    pipeline.nodes = {
        0: {"id": 0, "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
        2: {"id": 2, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
    }
    pipeline.dist_matrix = np.array([
        [0.0, 10.0, 200.0],
        [10.0, 0.0, 10.0],
        [200.0, 10.0, 0.0],
    ])

    routes, is_valid, errors = pipeline._insert_charging_stops(
        [[0, 1, 0], [0, 2, 0]]
    )

    assert routes == [[0, 1, 0], [0, 2, 0]]
    assert is_valid
    assert len(errors) == 1
    assert "Drone #2" in errors[0]

def test_pipeline_is_invalid_when_all_delivery_routes_are_energy_infeasible():
    pipeline = UAVRoutingPipeline(num_drones=2, drone_capacity=5.0)
    pipeline.nodes = {
        0: {"id": 0, "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
        2: {"id": 2, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
    }
    pipeline.dist_matrix = np.array([
        [0.0, 200.0, 200.0],
        [200.0, 0.0, 200.0],
        [200.0, 200.0, 0.0],
    ])

    _, is_valid, errors = pipeline._insert_charging_stops(
        [[0, 1, 0], [0, 2, 0]]
    )

    assert not is_valid
    assert len(errors) == 2

if __name__ == "__main__":
    test_pipeline_inserts_charging_stops()
    test_pipeline_is_valid_when_at_least_one_delivery_route_is_energy_feasible()
    test_pipeline_is_invalid_when_all_delivery_routes_are_energy_infeasible()
    test_day2()
