"""
Unit test kiem thu doc lap cho module cua Thanh vien 5 (Fitness & Visualizer).
"""
import sys
import os
import math
import numpy as np

# Dam bao ho tro tieng Viet tren Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Them duong dan src vao he thong
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.fitness import FitnessCalculator
from utils.visualizer import UAVVisualizer

def test_member5_modules():
    print("=== KIEM THU DOC LAP MODULE THÀNH VIÊN 5 ===")

    # 1. Tao du lieu gia lap (Mock Data)
    nodes = {
        0: {"id": 0, "type": "depot", "pos": (10, 10), "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "pos": (20, 25), "demand": 1.5, "tw": (5, 60), "service_time": 5},
        2: {"id": 2, "type": "delivery", "pos": (40, 15), "demand": 2.0, "tw": (10, 80), "service_time": 5},
        3: {"id": 3, "type": "delivery", "pos": (15, 45), "demand": 1.0, "tw": (20, 90), "service_time": 5},
        4: {"id": 4, "type": "charging", "pos": (30, 30), "demand": 0.0, "tw": (0, 1000), "service_time": 15},
    }

    no_fly_zones = [
        (25, 10, 8, 12),
        (5, 30, 10, 10)
    ]

    # Ma tran khoang cach gia lap (Euclidean)
    num_nodes = len(nodes)
    dist_matrix = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(num_nodes):
            pi = nodes[i]["pos"]
            pj = nodes[j]["pos"]
            dist_matrix[i, j] = math.sqrt((pi[0] - pj[0])**2 + (pi[1] - pj[1])**2)

    # Loi giai mau cho 2 Drone
    solution = [
        [0, 1, 3, 0],       # Drone 1
        [0, 2, 4, 0]        # Drone 2 (ghe tram sac 4)
    ]

    # 2. Kiem thu FitnessCalculator
    print("\n1. Kiem tra FitnessCalculator:")
    calc = FitnessCalculator()
    fitness, total_cost, breakdown = calc.evaluate_solution(solution, dist_matrix, nodes)

    print(f"-> Diem Fitness: {fitness:.4f}")
    print(f"-> Tong Chi phi: {total_cost:.2f}")
    print(f"-> Chi tiet: Khoang cach={breakdown['distance']:.2f}, Nang luong={breakdown['energy']:.2f}, Phat={breakdown['tw_penalty']:.2f}")

    assert fitness > 0, "Fitness phai lon hon 0"
    assert total_cost > 0, "Cost phai lon hon 0"
    print("-> FitnessCalculator hoat dong chinh xac!")

    # 3. Kiem thu UAVVisualizer
    print("\n2. Kiem tra UAVVisualizer:")
    visualizer = UAVVisualizer(grid_size=(60, 60))
    fig, ax = visualizer.plot_multi_uav_routes(
        nodes=nodes,
        no_fly_zones=no_fly_zones,
        solution=solution,
        title="Test Multi-UAV Route Visualization (Member 5)",
        show=False # Khong chan man hinh trong unit test
    )
    assert fig is not None, "Figure phai duoc tao thanh cong"
    print("-> plot_multi_uav_routes hoat dong chinh xac!")

    # Kiem tra duong cong hoi tu gia lap
    mock_history = [10.0, 15.5, 22.1, 35.0, 48.2, 55.0, 58.0]
    fig2, ax2 = visualizer.plot_convergence_curve(
        history_fitness=mock_history,
        title="Test GA Convergence Curve (Member 5)",
        show=False
    )
    assert fig2 is not None, "Convergence figure phai duoc tao thanh cong"
    print("-> plot_convergence_curve hoat dong chinh xac!")

    print("\n=== TAT CA UNIT TEST CHO THANH VIEN 5 DA VUOT QUA XUAT SAC! ===")

if __name__ == "__main__":
    test_member5_modules()
