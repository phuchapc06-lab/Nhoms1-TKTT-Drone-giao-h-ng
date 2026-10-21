"""
Module Quản lý Năng lượng Pin và Tự động Chèn Trạm sạc (Energy & Battery Manager).
Phụ trách: Thành viên 3 (Energy Manager & Constraints).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import math
from typing import List, Dict, Tuple, Any, Optional

class EnergyManager:
    """
    Quản lý tiêu hao năng lượng pin của đội bay UAV theo tải trọng hàng hóa,
    kiểm tra ngưỡng an toàn và lập trình tự động chèn trạm sạc vào lộ trình.
    """
    def __init__(
        self,
        battery_capacity: float = 300.0,       # Dung lượng pin tối đa của Drone (Wh)
        base_consumption: float = 1.0,         # Tiêu hao cơ sở khi bay không tải (Wh / km)
        payload_factor: float = 0.15,          # Hệ số tiêu hao thêm trên mỗi kg hàng hóa (Wh / km / kg)
        min_battery_threshold: float = 0.15,   # Ngưỡng pin an toàn (15% dung lượng) cần ghé trạm sạc
        charging_rate: float = 20.0,           # Tốc độ sạc pin (Wh / phút)
        charging_time: float = 5.0,            # Thời gian sạc mặc định tại trạm (phút)
        min_battery_ratio: Optional[float] = None
    ):
        if min_battery_ratio is not None:
            min_battery_threshold = min_battery_ratio

        if not math.isfinite(battery_capacity) or battery_capacity <= 0:
            raise ValueError("battery_capacity must be a positive finite number")
        if not math.isfinite(min_battery_threshold) or not (0 <= min_battery_threshold < 1):
            raise ValueError("min_battery_threshold must be in [0, 1)")
        if not math.isfinite(charging_time) or charging_time < 0:
            raise ValueError("charging_time must be a non-negative finite number")

        self.battery_capacity = float(battery_capacity)
        self.base_consumption = float(base_consumption)
        self.payload_factor = float(payload_factor)
        self.min_battery_threshold = float(min_battery_threshold)
        self.min_battery_ratio = self.min_battery_threshold
        self.min_safe_battery = self.battery_capacity * self.min_battery_threshold
        self.charging_rate = float(charging_rate)
        self.charging_time = float(charging_time)

    def get_charging_time(self, node: Dict[str, Any]) -> float:
        """
        Lấy thời gian phục vụ sạc tại trạm từ cấu hình node, hoặc lấy giá trị mặc định.
        """
        duration = float(node.get("service_time", self.charging_time))
        if not math.isfinite(duration) or duration < 0:
            return self.charging_time
        return duration

    def calculate_segment_energy(self, distance: float, cargo_weight: float) -> float:
        """
        Tính năng lượng tiêu thụ cho một chặng bay:
        E = distance * (base_consumption + payload_factor * cargo_weight)
        """
        rate = self.base_consumption + self.payload_factor * max(0.0, cargo_weight)
        return distance * rate

    def calculate_route_energy(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]]
    ) -> Tuple[float, bool]:
        """
        Tính tổng năng lượng tiêu thụ của một tuyến bay và kiểm tra tính khả thi của Pin.
        Chữ ký hàm tuân thủ 100% yêu cầu của FitnessCalculator:
        Trả về: (total_energy, is_feasible)
        """
        if not route or len(route) <= 2:
            return 0.0, True

        # Tính tải trọng ban đầu của chuyến bay
        current_cargo = 0.0
        for nid in route:
            node = nodes.get(nid, {})
            if node.get("type") == "delivery":
                current_cargo += node.get("demand", 0.0)

        current_battery = self.battery_capacity
        total_energy = 0.0
        is_feasible = True

        for i in range(len(route) - 1):
            u = route[i]
            v = route[i + 1]

            dist = dist_matrix[u][v] if isinstance(dist_matrix, list) else dist_matrix[u, v]
            if math.isinf(dist):
                return float("inf"), False

            seg_energy = self.calculate_segment_energy(dist, current_cargo)
            total_energy += seg_energy
            current_battery -= seg_energy

            # Nếu pin bị cạn kiệt dưới 0
            if current_battery < 0:
                is_feasible = False

            # Giảm tải trọng sau khi giao hàng xong tại v
            node_v = nodes.get(v, {})
            if node_v.get("type") == "delivery":
                current_cargo -= node_v.get("demand", 0.0)
            elif node_v.get("type") in ["charging", "depot"]:
                # Nạp đầy pin tại trạm sạc hoặc trạm gốc
                current_battery = self.battery_capacity

        return total_energy, is_feasible

    def repair_route_with_charging(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]]
    ) -> Tuple[List[int], float, bool]:
        """
        Thuật toán tham lam tự động chèn trạm sạc vào tuyến đường khi phát hiện pin sắp cạn:
        Nếu chặng bay tiếp theo làm pin < min_safe_battery:
        Tìm trạm sạc gần nhất có thể tiếp cận an toàn và chèn vào lộ trình.
        """
        if not route or len(route) <= 2:
            return route[:], 0.0, True

        charging_stations = [k for k, v in nodes.items() if v.get("type") == "charging"]
        if not charging_stations:
            # Không có trạm sạc trên bản đồ -> giữ nguyên và kiểm tra khả thi
            tot_e, feas = self.calculate_route_energy(route, dist_matrix, nodes)
            return route[:], tot_e, feas

        current_cargo = sum(nodes.get(nid, {}).get("demand", 0.0) for nid in route if nodes.get(nid, {}).get("type") == "delivery")
        current_battery = self.battery_capacity
        repaired_route = [route[0]]
        total_energy = 0.0
        is_feasible = True

        idx = 0
        while idx < len(route) - 1:
            u = repaired_route[-1]
            v = route[idx + 1]

            dist_uv = dist_matrix[u][v] if isinstance(dist_matrix, list) else dist_matrix[u, v]
            seg_energy = self.calculate_segment_energy(dist_uv, current_cargo)

            # Nếu bay thẳng đến v mà pin vẫn trên ngưỡng an toàn: bay thẳng
            if current_battery - seg_energy >= self.min_safe_battery:
                current_battery -= seg_energy
                total_energy += seg_energy
                repaired_route.append(v)
                if nodes.get(v, {}).get("type") == "delivery":
                    current_cargo -= nodes[v].get("demand", 0.0)
                elif nodes.get(v, {}).get("type") in ["charging", "depot"]:
                    current_battery = self.battery_capacity
                idx += 1
            else:
                # Cần chèn trạm sạc giữa u và v!
                best_cs = None
                best_detour = float("inf")

                for cs in charging_stations:
                    dist_u_cs = dist_matrix[u][cs] if isinstance(dist_matrix, list) else dist_matrix[u, cs]
                    energy_to_cs = self.calculate_segment_energy(dist_u_cs, current_cargo)

                    # Kiểm tra xem có đủ pin bay tới trạm sạc cs không
                    if current_battery >= energy_to_cs:
                        dist_cs_v = dist_matrix[cs][v] if isinstance(dist_matrix, list) else dist_matrix[cs, v]
                        detour = dist_u_cs + dist_cs_v - dist_uv
                        if detour < best_detour:
                            best_detour = detour
                            best_cs = cs

                # Đang đứng ở trạm sạc (pin vừa nạp đầy) mà vẫn không đủ pin bay tới v -> chèn thêm trạm nào
                # cũng vô ích. Trước đây best_cs chính là u (đường vòng = 0) nên bị chèn lại mãi -> vòng lặp vô hạn.
                if best_cs is not None and best_cs != u:
                    # Chèn trạm sạc vào lộ trình
                    dist_to_cs = dist_matrix[u][best_cs] if isinstance(dist_matrix, list) else dist_matrix[u, best_cs]
                    e_to_cs = self.calculate_segment_energy(dist_to_cs, current_cargo)
                    current_battery = self.battery_capacity # Nạp đầy pin tại trạm
                    total_energy += e_to_cs
                    repaired_route.append(best_cs)
                    # Sau khi sạc tại best_cs, tiếp tục xét bay từ best_cs đến v
                else:
                    # Không trạm sạc nào khả thi -> đành bay tiếp và đánh dấu không khả thi
                    current_battery -= seg_energy
                    total_energy += seg_energy
                    repaired_route.append(v)
                    is_feasible = False
                    idx += 1

        return repaired_route, total_energy, is_feasible

    def insert_charging_stations(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]]
    ) -> Tuple[List[int], bool]:
        """
        Giao diện đồng bộ với Module TV3: Trả về lộ trình đã chèn trạm sạc và cờ hợp lệ.
        """
        repaired, _, is_feasible = self.repair_route_with_charging(route, dist_matrix, nodes)
        return repaired, is_feasible
