"""
Bộ kiểm thử tổng kết hệ thống (Ngày Thứ Bảy - 24/10/2026)
Phụ trách: Nguyễn Phúc Hà (Tech Lead - Thành viên 5)

Nội dung kiểm thử:
1. Kiểm tra sự tồn tại và tính hợp lệ của toàn bộ 7 biểu đồ khoa học trong docs/figures/.
2. Kiểm tra hàm vẽ biểu đồ tỷ lệ giao hàng đúng giờ (plot_ontime_rate_comparison).
3. Kiểm tra tính nhất quán của bảng số liệu thực nghiệm CSV.
4. Kiểm tra sự đầy đủ của tài liệu báo cáo tổng kết và phân tích độ phức tạp.
5. Kiểm tra chạy tích hợp E2E Pipeline kết hợp tính song song và đo tỷ lệ đúng giờ.
"""

import os
import sys
import unittest
import pandas as pd

# Thiết lập sys.path hỗ trợ cả chạy trực tiếp và chạy qua runner
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(project_root, "src")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from utils.visualizer import UAVVisualizer
from pipeline import UAVRoutingPipeline
from utils.validator import DataContractValidator


class TestDay4TongKet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = project_root
        cls.figures_dir = os.path.join(cls.root_dir, "docs", "figures")
        cls.docs_dir = os.path.join(cls.root_dir, "docs")
        cls.csv_path = os.path.join(cls.root_dir, "data", "processed", "benchmark_comparison_results.csv")

    def test_01_tat_ca_bieu_do_ton_tai(self):
        """Kiểm tra đầy đủ 7 file biểu đồ khoa học trong docs/figures/."""
        required_figures = [
            "comparison_bars.png",
            "scalability_analysis.png",
            "speedup_analysis.png",
            "ontime_rate_comparison.png",
            "route_ga.png",
            "route_greedy.png",
            "convergence_ga.png"
        ]
        for fig_name in required_figures:
            fig_path = os.path.join(self.figures_dir, fig_name)
            self.assertTrue(os.path.exists(fig_path), f"Thiếu file biểu đồ: {fig_name}")
            self.assertGreater(os.path.getsize(fig_path), 10000, f"File {fig_name} có kích thước không hợp lệ.")

    def test_02_ve_bieu_do_on_time_rate(self):
        """Kiểm tra phương thức plot_ontime_rate_comparison trong UAVVisualizer."""
        viz = UAVVisualizer()
        test_scales = [10, 20, 30]
        test_greedy = [80.0, 75.0, 70.0]
        test_ga = [100.0, 95.0, 93.3]
        test_out = os.path.join(self.figures_dir, "test_ontime_temp.png")

        try:
            fig, ax = viz.plot_ontime_rate_comparison(
                scales=test_scales,
                greedy_rates=test_greedy,
                ga_rates=test_ga,
                title="Kiểm thử vẽ biểu đồ On-time Rate",
                save_path=test_out,
                show=False
            )
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
            self.assertTrue(os.path.exists(test_out))
            self.assertGreater(os.path.getsize(test_out), 5000)
        finally:
            if os.path.exists(test_out):
                os.remove(test_out)

    def test_03_tinh_nhat_quan_du_lieu_csv(self):
        """Kiểm tra file CSV kết quả đối sánh thực nghiệm chứa đầy đủ các trường cốt lõi."""
        self.assertTrue(os.path.exists(self.csv_path), "Thiếu file CSV kết quả thực nghiệm.")
        df = pd.read_csv(self.csv_path)

        expected_columns = [
            "scale_n", "greedy_dist", "ga_dist", "greedy_energy", "ga_energy",
            "greedy_ontime_rate", "ga_ontime_rate", "battery_safe"
        ]
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Thiếu cột {col} trong CSV kết quả.")

        for _, row in df.iterrows():
            self.assertGreaterEqual(row["ga_ontime_rate"], row["greedy_ontime_rate"],
                                    "Tỷ lệ đúng giờ của GA cần lớn hơn hoặc bằng Greedy.")
            self.assertTrue(bool(row["battery_safe"]), "Tất cả các lời giải phải đảm bảo an toàn pin.")

    def test_04_tai_lieu_tong_ket_va_phan_tich(self):
        """Kiểm tra sự đầy đủ của các tài liệu tổng kết và phân tích."""
        key_docs = [
            os.path.join(self.docs_dir, "BAO_CAO_TONG_KET_DE_TAI.md"),
            os.path.join(self.docs_dir, "COMPLEXITY_AND_CORRECTNESS_ANALYSIS.md"),
            os.path.join(self.docs_dir, "EXPERIMENT_RESULTS.md"),
            os.path.join(self.docs_dir, "NGUYEN_PHUC_HA_CONTRIBUTION.md"),
            os.path.join(self.root_dir, "TIEN_DO.md"),
            os.path.join(self.root_dir, "README.md")
        ]
        for doc in key_docs:
            self.assertTrue(os.path.exists(doc), f"Thiếu tài liệu: {doc}")
            self.assertGreater(os.path.getsize(doc), 1500, f"File {doc} chưa đủ nội dung.")

    def test_05_chay_tich_hop_pipeline_va_song_song(self):
        """Kiểm tra chạy Pipeline toàn trình có kích hoạt song song và đo tỷ lệ đúng giờ."""
        pipeline = UAVRoutingPipeline(grid_size=(40, 40), num_drones=2, seed=42)
        pipeline.generate_synthetic_data(num_delivery=6, num_charging=2, num_no_fly=2)

        pipeline.compute_distance_matrix(use_astar=True, parallel=True, num_workers=2)
        self.assertIsNotNone(pipeline.dist_matrix)

        res = pipeline.run_experiment(
            algorithm="ga",
            save_figure_dir=None,
            generations=15,
            pop_size=10
        )

        self.assertIn("solution", res)
        self.assertIn("total_cost", res)
        self.assertIn("on_time_rate", res)
        self.assertGreaterEqual(res["on_time_rate"], 0.0)
        self.assertLessEqual(res["on_time_rate"], 100.0)
        self.assertTrue(res["is_valid"])

        validator = DataContractValidator()
        self.assertTrue(validator.validate_solution(res["solution"], pipeline.nodes))


if __name__ == "__main__":
    unittest.main()
