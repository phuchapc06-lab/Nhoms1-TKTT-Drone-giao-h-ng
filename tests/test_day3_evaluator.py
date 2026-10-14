"""
Unit test kiểm thử tự động cho phần việc Ngày 3 của Thành viên 5 (Tech Lead):
- Benchmark Data Generator
- Benchmark Evaluator & Metrics Suite
- Biểu đồ Bar Chart so sánh đa thuật toán & Đồ thị Scalability
- Xuất báo cáo khoa học EXPERIMENT_RESULTS.md và file CSV
"""
import sys
import os

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validator import DataContractValidator
from utils.benchmark_generator import BenchmarkGenerator
from utils.benchmark_evaluator import BenchmarkEvaluator

def test_day3():
    print("==================================================================")
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ NGÀY 3 - THÀNH VIÊN 5 (TECH LEAD) ")
    print("==================================================================")

    # 1. Kiểm thử BenchmarkGenerator
    print("\n[TEST 1] Kiểm tra BenchmarkGenerator:")
    gen = BenchmarkGenerator(seed=99)
    bench_data = gen.generate(num_delivery=10, num_charging=3, num_no_fly=5, grid_size=(60, 60))

    validator = DataContractValidator()
    is_valid, errors = validator.validate_benchmark_data(bench_data)
    assert is_valid, f"Dữ liệu benchmark sinh ra vi phạm Data Contract: {errors}"
    print(f"  -> Dữ liệu benchmark 10 điểm hợp lệ: PASSED")

    # 2. Kiểm thử BenchmarkEvaluator
    print("\n[TEST 2] Kiểm tra BenchmarkEvaluator & Multi-scale Suite:")
    evaluator = BenchmarkEvaluator(
        save_figures_dir="docs/figures",
        results_dir="docs",
        csv_dir="data/processed",
        seed=42
    )

    # Chạy thử 2 quy mô nhỏ để kiểm tra tính toán metrics và xuất báo cáo
    df = evaluator.run_multi_scale_benchmark(scales=[6, 12])

    assert len(df) == 2, "Phải có kết quả cho 2 quy mô thử nghiệm"
    assert "dist_saved_pct" in df.columns, "Phải tính được % quãng đường tiết kiệm"
    assert "energy_saved_pct" in df.columns, "Phải tính được % năng lượng tiết kiệm"
    assert "greedy_dist" in df.columns and "ga_dist" in df.columns
    print("  -> Tính toán các chỉ số thực nghiệm đa quy mô: PASSED")

    # 3. Kiểm tra các file kết quả xuất ra
    print("\n[TEST 3] Kiểm tra xuất các file báo cáo & biểu đồ:")
    expected_files = [
        "docs/EXPERIMENT_RESULTS.md",
        "data/processed/benchmark_comparison_results.csv",
        "docs/figures/comparison_bars.png",
        "docs/figures/scalability_analysis.png"
    ]

    for ef in expected_files:
        assert os.path.exists(ef), f"Thiếu file kết quả: {ef}"
        size_bytes = os.path.getsize(ef)
        assert size_bytes > 0, f"File {ef} bị rỗng (0 bytes)"
        print(f"  -> Đã tạo thành công {ef} ({size_bytes} bytes): PASSED")

    print("\n==================================================================")
    print("  🎉 TẤT CẢ KIỂM THỬ NGÀY 3 ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!   ")
    print("==================================================================")

if __name__ == "__main__":
    test_day3()
