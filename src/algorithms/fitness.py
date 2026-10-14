"""
Module đánh giá hàm mục tiêu và độ thích nghi (Fitness Function) cho giải thuật di truyền (GA).
Phụ trách: Thành viên 5 (Nhóm trưởng / Tech Lead & Integrator).
"""
from typing import List, Dict, Tuple, Any, Optional

class FitnessCalculator:
    def __init__(
        self,
        alpha: float = 1.0,         # Trọng số chi phí khoảng cách
        beta: float = 1.5,          # Trọng số chi phí năng lượng tiêu thụ
        gamma: float = 5.0,         # Hệ số phạt vi phạm khung giờ (Time Window penalty)
        delta: float = 1000.0,      # Hệ số phạt vi phạm nghiêm trọng (cạn pin, quá tải Drone)
        drone_speed: float = 10.0,  # Vận tốc bay trung bình (đơn vị khoảng cách / phút)
        drone_capacity: float = 5.0 # Tải trọng tối đa mỗi Drone (kg)
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.drone_speed = drone_speed
        self.drone_capacity = drone_capacity

    def calculate_route_cost(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes_dict: Dict[int, Dict[str, Any]],
        energy_manager: Optional[Any] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Tính toán chi phí cho 1 tuyến đường của 1 UAV.
        Route ví dụ: [0, 3, 5, 0] (bắt đầu và kết thúc tại Depot 0).
        """
        if not route or len(route) <= 2:
            return 0.0, {"distance": 0.0, "energy": 0.0, "tw_penalty": 0.0, "cap_penalty": 0.0}

        evaluated_route = route
        if energy_manager and hasattr(energy_manager, "insert_charging_stations"):
            evaluated_route, _ = energy_manager.insert_charging_stations(
                route, dist_matrix, nodes_dict
            )

        total_distance = 0.0
        current_time = 0.0
        tw_penalty = 0.0
        cargo_load = 0.0
        cap_penalty = 0.0

        # 1. Tính tổng khối lượng hàng ban đầu cần giao
        for node_id in evaluated_route:
            if node_id in nodes_dict:
                cargo_load += nodes_dict[node_id].get("demand", 0.0)

        # Phạt nếu vượt quá tải trọng cho phép
        if cargo_load > self.drone_capacity:
            cap_penalty += (cargo_load - self.drone_capacity) * self.delta

        # 2. Duyệt từng chặng trong tuyến để tính khoảng cách và thời gian
        for i in range(len(evaluated_route) - 1):
            u = evaluated_route[i]
            v = evaluated_route[i + 1]

            dist = dist_matrix[u][v] if isinstance(dist_matrix, list) else dist_matrix[u, v]
            total_distance += dist

            # Thời gian bay đến v
            flight_time = dist / self.drone_speed if self.drone_speed > 0 else dist
            current_time += flight_time

            node_v = nodes_dict.get(v, {})
            tw = node_v.get("tw", (0.0, float("inf")))
            start_tw, end_tw = tw[0], tw[1]

            # Đến sớm -> phải chờ đến start_tw
            if current_time < start_tw:
                current_time = start_tw
            # Đến muộn -> phạt trễ hạn
            elif current_time > end_tw:
                lateness = current_time - end_tw
                tw_penalty += lateness * self.gamma

            # Thời gian phục vụ (giao hàng hoặc sạc)
            service_time = node_v.get("service_time", 0.0)
            if (
                energy_manager
                and node_v.get("type") == "charging"
                and hasattr(energy_manager, "get_charging_time")
            ):
                service_time = energy_manager.get_charging_time(node_v)
            current_time += service_time

        # 3. Tính năng lượng tiêu thụ (nếu TV3 đã kết nối EnergyManager, hoặc dùng ước lượng)
        total_energy = 0.0
        if energy_manager and hasattr(energy_manager, "calculate_route_energy"):
            total_energy, is_feasible = energy_manager.calculate_route_energy(
                evaluated_route, dist_matrix, nodes_dict
            )
            if not is_feasible:
                cap_penalty += self.delta
        else:
            # Mô hình năng lượng ước lượng: E = d * (1 + 0.1 * cargo)
            total_energy = total_distance * (1.0 + 0.1 * min(cargo_load, self.drone_capacity))

        route_cost = (
            self.alpha * total_distance
            + self.beta * total_energy
            + tw_penalty
            + cap_penalty
        )

        breakdown = {
            "distance": total_distance,
            "energy": total_energy,
            "tw_penalty": tw_penalty,
            "cap_penalty": cap_penalty
        }

        return route_cost, breakdown

    def evaluate_solution(
        self,
        solution: List[List[int]],
        dist_matrix: Any,
        nodes_dict: Dict[int, Dict[str, Any]],
        energy_manager: Optional[Any] = None
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Đánh giá toàn bộ lời giải gồm K tuyến bay của K Drone.
        Trả về:
            - fitness: Điểm thích nghi (càng cao càng tốt)
            - total_cost: Tổng chi phí (càng thấp càng tốt)
            - breakdown: Chi tiết các thành phần chi phí
        """
        total_cost = 0.0
        total_breakdown = {
            "distance": 0.0,
            "energy": 0.0,
            "tw_penalty": 0.0,
            "cap_penalty": 0.0
        }

        for route in solution:
            route_cost, breakdown = self.calculate_route_cost(route, dist_matrix, nodes_dict, energy_manager)
            total_cost += route_cost
            for k in total_breakdown:
                total_breakdown[k] += breakdown[k]

        # Hàm tính fitness nghịch đảo: Fitness = 1000 / (Cost + 1)
        fitness = 1000.0 / (total_cost + 1.0)
        return fitness, total_cost, total_breakdown
