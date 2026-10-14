"""Tests for battery consumption and charging-stop planning."""

import os
import sys

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.energy_manager import EnergyManager
from algorithms.fitness import FitnessCalculator


def make_data():
    nodes = {
        0: {"id": 0, "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 0},
        2: {"id": 2, "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 20},
        3: {"id": 3, "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 10},
    }
    distances = np.array([
        [0, 40, 20, 35],
        [50, 0, 10, 20],
        [10, 10, 0, 12],
        [10, 20, 12, 0],
    ], dtype=float)
    return nodes, distances


def test_energy_uses_payload_weight_and_reduces_load_after_delivery():
    nodes, distances = make_data()
    manager = EnergyManager()

    energy, is_valid = manager.calculate_route_energy([0, 1, 0], distances, nodes)

    assert is_valid
    # 0 -> 1 consumes 40 * (1 + 0.1 * 1); after delivery, 1 -> 0 consumes 50.
    # The direct return would breach reserve, so station 2 is inserted instead.
    assert energy == 40 * 1.1 + 10 * 1.0 + 10 * 1.0


def test_inserts_nearest_feasible_station_and_counts_its_service_time_in_fitness():
    nodes, distances = make_data()
    nodes[0]["tw"] = (0, 10)
    manager = EnergyManager()

    planned_route, is_valid = manager.insert_charging_stations(
        [0, 1, 0], distances, nodes
    )

    assert is_valid
    assert planned_route == [0, 1, 2, 0]
    _, breakdown = FitnessCalculator().calculate_route_cost(
        [0, 1, 0], distances, nodes, manager
    )
    assert breakdown["energy"] == 64.0
    # Travel takes 6 minutes and the charging stop adds 20 minutes.
    assert breakdown["tw_penalty"] == 16 * FitnessCalculator().gamma


def test_uses_multiple_stations_when_one_leg_exceeds_safe_range():
    nodes, distances = make_data()
    nodes[4] = {"id": 4, "type": "delivery", "demand": 0.0, "tw": (0, 1000), "service_time": 0}
    distances = np.pad(distances, ((0, 1), (0, 1)), constant_values=0)
    distances[1, 4] = 90
    distances[1, 2] = 40
    distances[1, 3] = 30
    distances[2, 4] = 80
    distances[3, 4] = 70
    distances[2, 3] = distances[3, 2] = 30
    distances[4, 0] = 0
    manager = EnergyManager()

    planned_route, is_valid = manager.insert_charging_stations(
        [0, 1, 4, 0], distances, nodes
    )

    assert is_valid
    assert planned_route == [0, 1, 3, 4, 0]


def test_marks_route_invalid_when_no_charging_station_is_reachable():
    nodes, distances = make_data()
    nodes.pop(2)
    nodes.pop(3)
    distances = distances[:2, :2]
    manager = EnergyManager()

    planned_route, is_valid = manager.insert_charging_stations(
        [0, 1, 0], distances, nodes
    )

    assert not is_valid
    assert planned_route == [0, 1, 0]
    _, is_valid = manager.calculate_route_energy([0, 1, 0], distances, nodes)
    assert not is_valid


def test_rejects_invalid_battery_configuration():
    for battery_capacity, min_battery_ratio in ((0, 0.15), (100, 1), (100, -0.1)):
        try:
            EnergyManager(battery_capacity, min_battery_ratio)
            assert False, "Invalid battery configuration must raise ValueError"
        except ValueError:
            pass


def test_uses_manager_default_when_station_service_time_is_missing():
    nodes, distances = make_data()
    nodes[0]["tw"] = (0, 10)
    nodes[2].pop("service_time")
    manager = EnergyManager(charging_time=7)

    _, breakdown = FitnessCalculator().calculate_route_cost(
        [0, 1, 0], distances, nodes, manager
    )

    assert breakdown["tw_penalty"] == 3 * FitnessCalculator().gamma


if __name__ == "__main__":
    test_energy_uses_payload_weight_and_reduces_load_after_delivery()
    test_inserts_nearest_feasible_station_and_counts_its_service_time_in_fitness()
    test_uses_multiple_stations_when_one_leg_exceeds_safe_range()
    test_marks_route_invalid_when_no_charging_station_is_reachable()
    test_rejects_invalid_battery_configuration()
    test_uses_manager_default_when_station_service_time_is_missing()
    print("All EnergyManager tests passed.")
