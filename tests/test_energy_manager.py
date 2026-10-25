"""
Unit test kiểm thử Module Quản lý Năng lượng Pin & Trạm sạc (TV3).
Phụ trách: Thành viên 3 (Energy Manager & Constraints).
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

from algorithms.energy_manager import EnergyManager
from algorithms.fitness import FitnessCalculator


class TestEnergyManager(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            0: {"id": 0, "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
            1: {"id": 1, "type": "delivery", "demand": 1.0, "tw": (0, 1000), "service_time": 5},
            2: {"id": 2, "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 20},
            3: {"id": 3, "type": "charging", "demand": 0.0, "tw": (0, 1000), "service_time": 10},
        }
        self.distances = np.array([
            [0, 40, 20, 35],
            [50, 0, 10, 20],
            [10, 10, 0, 12],
            [10, 20, 12, 0],
        ], dtype=float)

    def test_energy_consumption_with_payload(self):
        """Kiểm tra tiêu hao năng lượng tăng theo tải trọng hàng hóa."""
        manager = EnergyManager(battery_capacity=300.0, base_consumption=1.0, payload_factor=0.15)
        # Bay 10km không tải: 10 * 1.0 = 10.0 Wh
        e_empty = manager.calculate_segment_energy(10.0, cargo_weight=0.0)
        self.assertAlmostEqual(e_empty, 10.0, places=2)

        # Bay 10km với tải 2kg: 10 * (1.0 + 0.15 * 2) = 13.0 Wh
        e_loaded = manager.calculate_segment_energy(10.0, cargo_weight=2.0)
        self.assertAlmostEqual(e_loaded, 13.0, places=2)
        self.assertGreater(e_loaded, e_empty)

    def test_route_feasibility_check(self):
        """Kiểm tra phát hiện lộ trình vượt quá dung lượng pin."""
        manager = EnergyManager(battery_capacity=100.0, min_battery_threshold=0.15)
        # Tuyến 0 -> 1 -> 0: quãng đường 40 + 50 = 90km, tiêu hao > 90Wh
        # Với battery=100 và min_reserve=15, bay thẳng sẽ vi phạm ngưỡng pin an toàn
        total_e, is_valid = manager.calculate_route_energy([0, 1, 0], self.distances, self.nodes)
        self.assertGreater(total_e, 0.0)

    def test_insert_charging_stations(self):
        """Kiểm tra thuật toán tự động chèn trạm sạc vào lộ trình."""
        manager = EnergyManager(battery_capacity=100.0, min_battery_threshold=0.20)
        # Node 1 -> Node 0 rất xa (50km). Trạm 2 cách Node 1 chỉ 10km.
        # Thuật toán sẽ chèn trạm sạc 2 vào lộ trình: [0, 1, 2, 0]
        repaired_route, is_valid = manager.insert_charging_stations([0, 1, 0], self.distances, self.nodes)
        self.assertTrue(is_valid)
        self.assertIn(2, repaired_route)
        self.assertEqual(repaired_route[0], 0)
        self.assertEqual(repaired_route[-1], 0)

    def test_rejects_invalid_battery_configuration(self):
        """Kiểm tra ném lỗi ValueError khi cấu hình pin không hợp lệ."""
        for cap, ratio in [(-100.0, 0.15), (0.0, 0.15), (100.0, -0.1), (100.0, 1.0), (100.0, 1.5)]:
            with self.assertRaises(ValueError):
                EnergyManager(battery_capacity=cap, min_battery_threshold=ratio)

    def test_station_service_time(self):
        """Kiểm tra lấy thời gian sạc tại trạm và fallback về mặc định."""
        manager = EnergyManager(charging_time=12.0)
        # Node 2 có service_time = 20
        self.assertEqual(manager.get_charging_time(self.nodes[2]), 20.0)
        # Node không có service_time -> fallback về 12.0
        self.assertEqual(manager.get_charging_time({"id": 99}), 12.0)

    def test_detailed_energy_breakdown_and_charging_time(self):
        """Kiểm tra báo cáo chi tiết từng chặng bay và thời gian sạc tại trạm."""
        manager = EnergyManager(battery_capacity=100.0, charging_rate=20.0)
        total_energy, is_valid, details = manager.calculate_route_energy_details([0, 1, 2, 0], self.distances, self.nodes)

        self.assertTrue(is_valid)
        self.assertAlmostEqual(total_energy, 40.0 * (1.0 + 0.15 * 1.0) + 10.0 + 10.0, places=2)
        self.assertEqual(len(details), 3)
        self.assertAlmostEqual(details[0]["segment_energy"], 46.0, places=2)
        self.assertAlmostEqual(details[0]["payload"], 1.0, places=2)
        self.assertEqual(details[1]["node_type"], "charging")
        self.assertAlmostEqual(details[1]["charging_time"], 20.0, places=2)
        self.assertAlmostEqual(manager.estimate_charging_duration(54.0, self.nodes[2]), 20.0, places=2)


if __name__ == "__main__":
    unittest.main()
