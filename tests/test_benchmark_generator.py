"""
Unit test kiểm thử Module Sinh Dữ liệu Thực nghiệm Đa quy mô (TV4).
Phụ trách: Thành viên 4 (Benchmark Data & Scenarios).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import unittest

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.benchmark_generator import generate_benchmark, load_benchmark, BenchmarkGenerator


class TestBenchmarkGenerator(unittest.TestCase):
    def setUp(self):
        self.expected_files = {
            10: ("data/raw/benchmark_10.json", 3, 5),
            50: ("data/raw/benchmark_50.json", 6, 12),
            100: ("data/raw/benchmark_100.json", 10, 20),
            500: ("data/raw/benchmark_500.json", 25, 10),
        }
        # Đảm bảo các file đều tồn tại trước khi test
        for n_cust, (path, n_chg, n_nfz) in self.expected_files.items():
            if not os.path.exists(path):
                generate_benchmark(n_cust, n_chg, n_nfz, path)

    def test_all_benchmarks_exist_and_valid(self):
        """Kiểm tra đủ 4 bộ dữ liệu 10, 50, 100, 500 điểm theo Data Contract."""
        for n_cust, (path, n_chg, n_nfz) in self.expected_files.items():
            self.assertTrue(os.path.exists(path), f"Thiếu file {path}")
            data = load_benchmark(path)

            # Kiểm tra các khóa chính
            self.assertEqual(data["num_customers"], n_cust)
            self.assertEqual(data["num_charging"], n_chg)
            self.assertEqual(len(data["no_fly_zones"]), n_nfz)

            nodes = data["nodes"]
            # Tổng số node = 1 Depot + N Khách hàng + M Trạm sạc
            self.assertEqual(len(nodes), 1 + n_cust + n_chg)

            # Kiểm tra định dạng Depot (ID = 0)
            depot = nodes[0]
            self.assertEqual(depot["id"], 0)
            self.assertEqual(depot["type"], "depot")
            self.assertEqual(depot["demand"], 0.0)
            self.assertIsInstance(depot["pos"], tuple)
            self.assertIsInstance(depot["tw"], tuple)

            # Kiểm tra định dạng Khách hàng đầu tiên (ID = 1)
            customer = nodes[1]
            self.assertEqual(customer["id"], 1)
            self.assertEqual(customer["type"], "delivery")
            self.assertTrue(customer["demand"] > 0)
            self.assertIsInstance(customer["pos"], tuple)
            self.assertIsInstance(customer["tw"], tuple)

            # Kiểm tra định dạng Vùng cấm bay
            zone = data["no_fly_zones"][0]
            self.assertIn("bounds", zone)
            self.assertIsInstance(zone["bounds"], tuple)
            self.assertEqual(len(zone["bounds"]), 4)

    def test_benchmark_generator_class(self):
        """Kiểm tra phương thức generate của class BenchmarkGenerator."""
        gen = BenchmarkGenerator(seed=99)
        data = gen.generate(num_delivery=15, num_charging=3, num_no_fly=4, grid_size=(70, 70))
        self.assertEqual(data["num_customers"], 15)
        self.assertEqual(data["num_charging"], 3)
        self.assertEqual(len(data["no_fly_zones"]), 4)
        self.assertIn("0", data["nodes"])
        self.assertEqual(data["nodes"]["0"]["type"], "depot")


if __name__ == "__main__":
    unittest.main()
