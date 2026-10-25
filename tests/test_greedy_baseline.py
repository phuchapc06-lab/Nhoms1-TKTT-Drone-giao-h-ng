"""
Unit test kiểm thử Module Thuật toán Đối sánh Baseline & Tối ưu Cục bộ 2-Opt (TV6).
Phụ trách: Thành viên 6 (Baseline & Local Search).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import unittest
import numpy as np

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.baseline_greedy import GreedyRouter
from algorithms.local_search import two_opt_route, apply_2opt_to_solution
from algorithms.fitness import FitnessCalculator
from algorithms.energy_manager import EnergyManager


class TestGreedyBaseline(unittest.TestCase):
    def setUp(self):
        # 1 Depot (0) + 4 Khách hàng (1..4) + 1 Trạm sạc (5)
        self.nodes = {
            0: {"id": 0, "type": "depot", "pos": [0, 0], "demand": 0.0, "tw": [0, 1000], "service_time": 0},
            1: {"id": 1, "type": "delivery", "pos": [0, 10], "demand": 1.5, "tw": [5, 50], "service_time": 5},
            2: {"id": 2, "type": "delivery", "pos": [10, 10], "demand": 1.2, "tw": [10, 60], "service_time": 5},
            3: {"id": 3, "type": "delivery", "demand": 1.8, "pos": [10, 0], "tw": [15, 70], "service_time": 5},
            4: {"id": 4, "type": "delivery", "demand": 2.0, "pos": [5, 15], "tw": [20, 80], "service_time": 5},
            5: {"id": 5, "type": "charging", "demand": 0.0, "pos": [5, 5], "tw": [0, 1000], "service_time": 15},
        }

        # Ma trận khoảng cách Euclid 6x6
        self.dist_matrix = np.zeros((6, 6))
        for i in range(6):
            for j in range(6):
                p1 = self.nodes[i]["pos"]
                p2 = self.nodes[j]["pos"]
                self.dist_matrix[i, j] = np.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def test_greedy_router_solve(self):
        """Kiểm tra GreedyRouter sinh lời giải hợp lệ cho toàn bộ khách hàng."""
        router = GreedyRouter(
            nodes=self.nodes,
            dist_matrix=self.dist_matrix,
            num_drones=2,
            drone_capacity=5.0
        )
        solution = router.solve()

        # Kiểm tra số lượng tuyến = số Drone
        self.assertEqual(len(solution), 2)

        # Kiểm tra mọi tuyến đều bắt đầu và kết thúc tại Depot 0
        for route in solution:
            self.assertEqual(route[0], 0)
            self.assertEqual(route[-1], 0)

        # Kiểm tra tất cả khách hàng (1, 2, 3, 4) đều được phục vụ
        visited = []
        for route in solution:
            visited.extend([nid for nid in route if nid in [1, 2, 3, 4]])
        self.assertEqual(set(visited), {1, 2, 3, 4})
        self.assertEqual(len(visited), 4)

    def test_two_opt_route_uncrossing(self):
        """Kiểm tra 2-Opt gỡ giao cắt đường bay và rút ngắn khoảng cách."""
        # Kịch bản 4 đỉnh hình vuông: A(0,0), B(0,10), C(10,10), D(10,0)
        # Depot là 0: (0,0). Các điểm: 1:(0,10), 2:(10,10), 3:(10,0).
        # Tuyến đường giao cắt chữ X: 0 -> 2 -> 1 -> 3 -> 0
        # Khoảng cách: d(0,2) = 14.14, d(2,1) = 10, d(1,3) = 14.14, d(3,0) = 10 -> Tổng = 48.28
        # Sau 2-Opt đảo lại: 0 -> 1 -> 2 -> 3 -> 0 -> Tổng = 10 + 10 + 10 + 10 = 40.0
        crossed_route = [0, 2, 1, 3, 0]
        optimized_route = two_opt_route(crossed_route, self.dist_matrix)

        def calc_dist(r):
            return sum(self.dist_matrix[r[i], r[i + 1]] for i in range(len(r) - 1))

        d_before = calc_dist(crossed_route)
        d_after = calc_dist(optimized_route)

        self.assertLess(d_after, d_before)
        self.assertAlmostEqual(d_after, 40.0, places=1)
        self.assertEqual(optimized_route[0], 0)
        self.assertEqual(optimized_route[-1], 0)

    def test_apply_2opt_to_solution(self):
        """Kiểm tra apply_2opt_to_solution áp dụng cho toàn bộ đội bay."""
        multi_sol = [
            [0, 2, 1, 3, 0],
            [0, 4, 0]
        ]
        improved = apply_2opt_to_solution(multi_sol, self.dist_matrix)
        self.assertEqual(len(improved), 2)
        self.assertEqual(improved[0][0], 0)
        self.assertEqual(improved[0][-1], 0)
        self.assertEqual(improved[1], [0, 4, 0])

    def test_apply_2opt_with_route_cost_guard(self):
        """route_cost: chỉ giữ kết quả 2-Opt khi chi phí tuyến không tăng (2-Opt chỉ xét quãng đường)."""
        crossed = [0, 2, 1, 3, 0]
        plain = apply_2opt_to_solution([crossed], self.dist_matrix)[0]
        self.assertNotEqual(plain, crossed)  # 2-Opt có đảo đoạn ở tuyến này

        def route_dist(r):
            return sum(self.dist_matrix[r[i], r[i + 1]] for i in range(len(r) - 1))

        # Chi phí đi theo quãng đường -> nhận kết quả 2-Opt
        self.assertEqual(apply_2opt_to_solution([crossed], self.dist_matrix, route_dist)[0], plain)
        # Chi phí tăng sau khi đảo (vd. chở nặng bay chặng xa) -> giữ tuyến cũ
        prefer_original = lambda r: 0.0 if r == crossed else 1.0
        self.assertEqual(apply_2opt_to_solution([crossed], self.dist_matrix, prefer_original)[0], crossed)

    def test_greedy_integration_with_energy_and_fitness(self):
        """Kiểm tra tích hợp Greedy với EnergyManager và FitnessCalculator."""
        router = GreedyRouter(
            nodes=self.nodes,
            dist_matrix=self.dist_matrix,
            num_drones=2,
            drone_capacity=5.0
        )
        sol = router.solve()

        # Áp dụng 2-opt
        opt_sol = apply_2opt_to_solution(sol, self.dist_matrix)

        # Chèn trạm sạc
        em = EnergyManager(battery_capacity=100.0, min_battery_threshold=0.15)
        repaired_sol = []
        for route in opt_sol:
            r, _, _ = em.repair_route_with_charging(route, self.dist_matrix, self.nodes)
            repaired_sol.append(r)

        # Đánh giá fitness
        fc = FitnessCalculator()
        fit, cost, breakdown = fc.evaluate_solution(repaired_sol, self.dist_matrix, self.nodes, em)
        self.assertGreater(fit, 0.0)
        self.assertGreater(cost, 0.0)
        self.assertIn("distance", breakdown)
        self.assertIn("energy", breakdown)


if __name__ == "__main__":
    unittest.main()
