import os
import unittest
from src.utils.benchmark_generator import generate_benchmark, load_benchmark


class TestBenchmarkGenerator(unittest.TestCase):
    def setUp(self):
        self.expected_files = {
            10: ("data/raw/benchmark_10.json", 2, 2),
            50: ("data/raw/benchmark_50.json", 5, 4),
            100: ("data/raw/benchmark_100.json", 10, 6),
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
            self.assertTrue(1.0 <= customer["demand"] <= 5.0)
            self.assertIsInstance(customer["pos"], tuple)
            self.assertIsInstance(customer["tw"], tuple)

            # Kiểm tra định dạng Vùng cấm bay
            zone = data["no_fly_zones"][0]
            self.assertIsInstance(zone["bounds"], tuple)
            self.assertEqual(len(zone["bounds"]), 4)


if __name__ == "__main__":
    unittest.main()