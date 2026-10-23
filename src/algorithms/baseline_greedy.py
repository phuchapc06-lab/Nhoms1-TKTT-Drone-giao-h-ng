"""
Module Thuật toán Định tuyến Tham lam Baseline (Greedy Nearest Neighbor Router).
Phụ trách: Thành viên 6 (Baseline & Local Search).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import numpy as np
from typing import List, Dict, Any

class GreedyRouter:
    def __init__(
        self,
        nodes: Dict[int, Dict[str, Any]],
        dist_matrix: Any,
        num_drones: int,
        drone_capacity: float = 5.0
    ):
        self.nodes = nodes
        self.dist_matrix = dist_matrix
        self.num_drones = num_drones
        self.drone_capacity = drone_capacity

    def solve(self) -> List[List[int]]:
        """
        Tìm kiếm tuyến bay tham lam: Tại mỗi bước, Drone chọn khách hàng gần nhất
        chưa được phục vụ mà vẫn thỏa mãn giới hạn tải trọng.
        """
        deliveries = [k for k, v in self.nodes.items() if v.get("type") == "delivery"]
        unvisited = set(deliveries)
        solution = [[0] for _ in range(self.num_drones)]
        drone_loads = [0.0] * self.num_drones

        while unvisited:
            best_cand = None
            best_drone = -1
            best_dist = float("inf")

            for d_idx in range(self.num_drones):
                curr_pos = solution[d_idx][-1]
                for cand in unvisited:
                    demand = self.nodes[cand].get("demand", 0.0)
                    if drone_loads[d_idx] + demand <= self.drone_capacity:
                        dist = self.dist_matrix[curr_pos, cand]
                        if dist < best_dist:
                            best_dist = dist
                            best_cand = cand
                            best_drone = d_idx

            if best_cand is not None and best_drone != -1:
                solution[best_drone].append(best_cand)
                drone_loads[best_drone] += self.nodes[best_cand].get("demand", 0.0)
                unvisited.remove(best_cand)
            else:
                # Nếu tất cả drone đều đầy tải, gán khách vào drone có tải ít nhất
                cand = min(unvisited, key=lambda c: self.nodes[c].get("demand", 0.0))
                min_d_idx = int(np.argmin(drone_loads))
                solution[min_d_idx].append(cand)
                drone_loads[min_d_idx] += self.nodes[cand].get("demand", 0.0)
                unvisited.remove(cand)

        # Quay về trạm gốc (Depot 0)
        for r in solution:
            r.append(0)

        return solution
