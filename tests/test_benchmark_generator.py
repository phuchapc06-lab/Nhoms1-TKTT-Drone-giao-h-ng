import csv
import os
import unittest
from src.utils.benchmark_generator import (
    export_comparison_csv,
    generate_benchmark,
    load_benchmark,
)


class TestBenchmarkGenerator(unittest.TestCase):
    def setUp(self):
        self.expected_files = {
            10: ("data/raw/benchmark_10.json", 2, 2),
            50: ("data/raw/benchmark_50.json", 5, 4),
            100: ("data/raw/benchmark_100.json", 10, 6),
            500: ("data/raw/benchmark_500.json", 25, 10),
        }
        for n_cust, (path, n_chg, n_nfz) in self.expected_files.items():
            generate_benchmark(n_cust, n_chg, n_nfz, path, tw_mode="mixed")

        self.csv_path = "data/processed/benchmark_comparison_results.csv"
        export_comparison_csv(output_csv=self.csv_path)

    def test_all_benchmarks_and_time_windows(self):
        """Kiểm tra đủ 4 bộ dữ liệu 10, 50, 100, 500 điểm và Time Windows đa dạng."""
        for n_cust, (path, n_chg, n_nfz) in self.expected_files.items():
            self.assertTrue(os.path.exists(path), f"Thiếu file {path}")
            data = load_benchmark(path)

            self.assertEqual(data["num_customers"], n_cust)
            self.assertEqual(data["num_charging"], n_chg)
            self.assertEqual(len(data["no_fly_zones"]), n_nfz)

            nodes = data["nodes"]
            self.assertEqual(len(nodes), 1 + n_cust + n_chg)

            # Kiểm tra có cả Time Windows chặt chẽ (tight) và nới lỏng (relaxed)
            tw_types = {
                node.get("tw_type")
                for node in nodes
                if node["type"] == "delivery"
            }
            self.assertIn("tight", tw_types)
            self.assertIn("relaxed", tw_types)

    def test_comparison_csv_exported(self):
        """Kiểm tra file CSV tổng hợp thực nghiệm tồn tại và đủ cột."""
        self.assertTrue(os.path.exists(self.csv_path))
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertGreaterEqual(len(reader), 8)
            self.assertIn("ontime_delivery_rate_pct", reader[0])
            self.assertIn("speedup_factor", reader[0])


if __name__ == "__main__":
    unittest.main()