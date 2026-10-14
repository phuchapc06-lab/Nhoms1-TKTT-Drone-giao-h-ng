"""Battery feasibility and charging-stop planning for UAV routes."""

import math
from typing import Any, Dict, List, Optional, Tuple


class EnergyManager:
    """Plan charging stops using distance, remaining payload, and battery reserve."""

    def __init__(
        self,
        battery_capacity: float = 100.0,
        min_battery_ratio: float = 0.15,
        charging_time: float = 5.0,
    ) -> None:
        if not math.isfinite(battery_capacity) or battery_capacity <= 0:
            raise ValueError("battery_capacity must be a positive finite number")
        if not math.isfinite(min_battery_ratio) or not 0 <= min_battery_ratio < 1:
            raise ValueError("min_battery_ratio must be in [0, 1)")
        if not math.isfinite(charging_time) or charging_time < 0:
            raise ValueError("charging_time must be a non-negative finite number")

        self.battery_capacity = float(battery_capacity)
        self.min_battery_ratio = float(min_battery_ratio)
        self.charging_time = float(charging_time)

    def insert_charging_stations(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]],
    ) -> Tuple[List[int], bool]:
        """Return a route with feasible charging stops and whether it is flyable.

        The input route is not mutated. Each inserted charging node contributes
        its ``service_time`` (or the manager's default charging time) when the
        returned route is evaluated by the fitness calculator.
        """
        planned_route, _, is_valid = self._plan_route(route, dist_matrix, nodes)
        return planned_route, is_valid

    def calculate_route_energy(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]],
    ) -> Tuple[float, bool]:
        """Return propulsion energy and feasibility, preserving the fitness API."""
        _, total_energy, is_valid = self._plan_route(route, dist_matrix, nodes)
        return total_energy, is_valid

    def get_charging_time(self, node: Dict[str, Any]) -> float:
        """Return a station's configured service time or the manager default."""
        return self._charging_duration(node)

    def _plan_route(
        self,
        route: List[int],
        dist_matrix: Any,
        nodes: Dict[int, Dict[str, Any]],
    ) -> Tuple[List[int], float, bool]:
        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            raise ValueError("route must start and end at depot 0")
        if any(node_id not in nodes for node_id in route):
            raise ValueError("route contains a node ID missing from nodes")

        deliveries = [node_id for node_id in route if nodes[node_id].get("type") == "delivery"]
        if len(deliveries) != len(set(deliveries)):
            raise ValueError("route must not visit a delivery node more than once")

        remaining_load = sum(self._demand(nodes[node_id]) for node_id in deliveries)
        stations = sorted(
            node_id for node_id, node in nodes.items()
            if node.get("type") == "charging"
        )
        reserve = self.battery_capacity * self.min_battery_ratio
        usable_range = self.battery_capacity - reserve
        battery = self.battery_capacity
        total_energy = 0.0
        planned_route = [route[0]]

        for target in route[1:]:
            current = planned_route[-1]
            direct_energy = self._leg_energy(current, target, remaining_load, dist_matrix)

            if direct_energy > battery - reserve:
                path = self._find_charging_path(
                    current, target, stations, remaining_load, battery - reserve,
                    usable_range, dist_matrix
                )
                if path is None:
                    return route[:], total_energy, False
            else:
                path = [target]

            for next_node in path:
                leg_energy = self._leg_energy(current, next_node, remaining_load, dist_matrix)
                if leg_energy > battery - reserve:
                    return route[:], total_energy, False
                battery -= leg_energy
                total_energy += leg_energy
                planned_route.append(next_node)
                current = next_node

                if nodes[current].get("type") == "charging":
                    battery = self.battery_capacity

            if nodes[target].get("type") == "delivery":
                remaining_load -= self._demand(nodes[target])

        return planned_route, total_energy, True

    def _find_charging_path(
        self,
        start: int,
        target: int,
        stations: List[int],
        load: float,
        first_leg_range: float,
        full_leg_range: float,
        dist_matrix: Any,
    ) -> Optional[List[int]]:
        """Find the shortest feasible sequence of charging nodes to the target."""
        candidates = [station for station in stations if station != start]
        if target not in candidates:
            candidates.append(target)

        best_distance: Dict[int, float] = {}
        previous: Dict[int, Optional[int]] = {}
        unvisited = set(candidates)

        for node_id in candidates:
            distance = self._distance(start, node_id, dist_matrix)
            energy = distance * (1.0 + 0.1 * load)
            if energy <= first_leg_range:
                best_distance[node_id] = distance
                previous[node_id] = None

        while unvisited:
            reachable = [node_id for node_id in unvisited if node_id in best_distance]
            if not reachable:
                return None
            current = min(reachable, key=best_distance.__getitem__)
            unvisited.remove(current)

            if current == target:
                path: List[int] = []
                cursor: Optional[int] = current
                while cursor is not None:
                    path.append(cursor)
                    cursor = previous[cursor]
                return list(reversed(path))

            for neighbor in unvisited:
                distance = self._distance(current, neighbor, dist_matrix)
                energy = distance * (1.0 + 0.1 * load)
                if energy > full_leg_range:
                    continue
                candidate_distance = best_distance[current] + distance
                if candidate_distance < best_distance.get(neighbor, math.inf):
                    best_distance[neighbor] = candidate_distance
                    previous[neighbor] = current

        return None

    @staticmethod
    def _demand(node: Dict[str, Any]) -> float:
        demand = float(node.get("demand", 0.0))
        if not math.isfinite(demand) or demand < 0:
            raise ValueError("node demand must be a non-negative finite number")
        return demand

    def _charging_duration(self, node: Dict[str, Any]) -> float:
        duration = float(node.get("service_time", self.charging_time))
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("charging service_time must be a non-negative finite number")
        return duration

    @staticmethod
    def _distance(start: int, end: int, dist_matrix: Any) -> float:
        try:
            distance = float(
                dist_matrix[start][end]
                if isinstance(dist_matrix, list)
                else dist_matrix[start, end]
            )
        except (IndexError, KeyError, TypeError) as exc:
            raise ValueError("dist_matrix does not contain a distance for this node pair") from exc
        if math.isnan(distance) or distance < 0:
            raise ValueError("distances must be non-negative and not NaN")
        return distance

    def _leg_energy(self, start: int, end: int, load: float, dist_matrix: Any) -> float:
        distance = self._distance(start, end, dist_matrix)
        if math.isinf(distance):
            return math.inf
        return distance * (1.0 + 0.1 * load)
