"""
Module Tối ưu Cục bộ 2-Opt (2-Opt Local Search Algorithm).
Phụ trách: Thành viên 6 (Baseline & Local Search).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
Chức năng:
- Gỡ các đường bay chéo nhau, tối ưu lại thứ tự giao hàng trên từng tuyến Drone.
- Rút ngắn khoảng cách di chuyển từ 5% đến 15% cho cả lời giải Greedy và GA.
"""
from typing import List, Any, Callable, Optional

def two_opt_route(route: List[int], dist_matrix: Any, max_iterations: int = 50) -> List[int]:
    """
    Áp dụng thuật toán 2-Opt cho 1 tuyến đường [0, c1, c2, ..., 0].
    Chỉ tối ưu hoán vị các điểm khách hàng ở giữa, giữ cố định Depot ở hai đầu.
    """
    if len(route) <= 3:
        return route[:]

    best_route = route[:]
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                # Các cạnh hiện tại: (u1 -> v1) và (u2 -> v2)
                u1, v1 = best_route[i - 1], best_route[i]
                u2, v2 = best_route[j], best_route[j + 1]

                current_dist = (
                    (dist_matrix[u1][v1] if isinstance(dist_matrix, list) else dist_matrix[u1, v1]) +
                    (dist_matrix[u2][v2] if isinstance(dist_matrix, list) else dist_matrix[u2, v2])
                )

                new_dist = (
                    (dist_matrix[u1][u2] if isinstance(dist_matrix, list) else dist_matrix[u1, u2]) +
                    (dist_matrix[v1][v2] if isinstance(dist_matrix, list) else dist_matrix[v1, v2])
                )

                # Nếu đảo đoạn [i:j+1] rút ngắn được quãng đường
                if new_dist < current_dist - 1e-4:
                    best_route[i:j + 1] = reversed(best_route[i:j + 1])
                    improved = True
                    break
            if improved:
                break

    return best_route

def apply_2opt_to_solution(
    solution: List[List[int]],
    dist_matrix: Any,
    route_cost: Optional[Callable[[List[int]], float]] = None
) -> List[List[int]]:
    """
    Áp dụng thuật toán 2-Opt tối ưu hóa cho toàn bộ các tuyến của đội bay UAV.
    route_cost (tùy chọn): hàm tính chi phí của 1 tuyến. Khi được truyền vào, chỉ giữ tuyến sau 2-Opt
    nếu chi phí không tăng. 2-Opt chỉ xét quãng đường nên có thể đảo thứ tự giao khiến Drone chở nặng
    bay chặng xa (tốn năng lượng hơn, trễ giờ, thậm chí cạn pin).
    """
    result = []
    for route in solution:
        new_route = two_opt_route(route, dist_matrix)
        if route_cost is not None and new_route != route and route_cost(new_route) > route_cost(route):
            new_route = route[:]
        result.append(new_route)
    return result
