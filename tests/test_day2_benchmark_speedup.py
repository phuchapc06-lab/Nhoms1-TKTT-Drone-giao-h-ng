"""
Bộ kiểm thử độc lập cho nhiệm vụ Thứ Năm (Ngày 2 - 22/10/2026):
- Chạy Thực nghiệm Đối sánh Đa quy mô Toàn diện (Multi-Scale Benchmark).
- Đo đạc Đa chiều: Quãng đường, Năng lượng, Tỷ lệ đúng giờ (On-time Rate), Thời gian tính toán.
- Đo đạc Tốc độ Tăng tốc Song song hóa (Speedup) và Trực quan hóa Biểu đồ Nghiên cứu.
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import pandas as pd

# Đảm bảo console Windows in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.benchmark_evaluator import BenchmarkEvaluator
from utils.visualizer import UAVVisualizer


def test_evaluate_scale_metrics():
    print("\n[TEST 1] Kiểm tra Thu thập Đầy đủ 4 Chỉ số Thực nghiệm (evaluate_scale):")
    evaluator = BenchmarkEvaluator(seed=42)
    res = evaluator.evaluate_scale(num_delivery=6, num_drones=2, ga_generations=20, ga_pop_size=20)

    # 1. Quãng đường
    assert "greedy_dist" in res and "ga_dist" in res, "Phải có số liệu quãng đường"
    assert "dist_saved_pct" in res, "Phải có tỷ lệ tiết kiệm quãng đường"

    # 2. Năng lượng
    assert "greedy_energy" in res and "ga_energy" in res, "Phải có số liệu năng lượng"
    assert "energy_saved_pct" in res, "Phải có tỷ lệ tiết kiệm năng lượng"

    # 3. Tỷ lệ đúng giờ (On-time Rate)
    assert "greedy_ontime_rate" in res and "ga_ontime_rate" in res, "Phải có tỷ lệ giao đúng giờ"
    assert 0.0 <= res["ga_ontime_rate"] <= 100.0, "Tỷ lệ đúng giờ phải nằm trong [0, 100]"

    # 4. Thời gian tính toán
    assert "greedy_time_s" in res and "ga_time_s" in res, "Phải có thời gian tính toán"

    # 5. An toàn pin
    assert "battery_safe" in res and res["battery_safe"] is True, "Pin phải luôn an toàn không cạn kiệt"

    print(f"  -> Quãng đường: GA={res['ga_dist']}km vs Greedy={res['greedy_dist']}km (Tiết kiệm: {res['dist_saved_pct']}%)")
    print(f"  -> Năng lượng:  GA={res['ga_energy']}Wh vs Greedy={res['greedy_energy']}Wh (Tiết kiệm: {res['energy_saved_pct']}%)")
    print(f"  -> Đúng giờ:    GA={res['ga_ontime_rate']}% vs Greedy={res['greedy_ontime_rate']}%")
    print(f"  -> Thời gian:   GA={res['ga_time_s']}s vs Greedy={res['greedy_time_s']}s")
    print("  -> Thu thập 4 chỉ số cốt lõi: PASSED")


def test_run_speedup_benchmark():
    print("\n[TEST 2] Kiểm tra Đo đạc Hệ số Tăng tốc Song song hóa (run_speedup_benchmark):")
    evaluator = BenchmarkEvaluator(seed=42)
    speedup_res = evaluator.run_speedup_benchmark(scale=10, workers_list=[1, 2])

    assert "workers" in speedup_res, "Kết quả phải chứa danh sách workers"
    assert "speedups" in speedup_res, "Kết quả phải chứa hệ số speedups"
    assert "times_sec" in speedup_res, "Kết quả phải chứa times_sec"
    assert speedup_res["speedups"]["S_1"] == 1.0, "S_1 với 1 luồng phải bằng 1.0"
    assert os.path.exists(speedup_res["chart_path"]), f"File biểu đồ {speedup_res['chart_path']} phải tồn tại"

    print(f"  -> Speedup S_1: {speedup_res['speedups']['S_1']}x, S_2: {speedup_res['speedups']['S_2']}x")
    print(f"  -> Biểu đồ Speedup tạo thành công tại: {speedup_res['chart_path']}: PASSED")


def test_visualizer_plot_speedup():
    print("\n[TEST 3] Kiểm tra Module Trực quan hóa Biểu đồ Speedup (plot_speedup_analysis):")
    visualizer = UAVVisualizer()
    mock_workers = [1, 2, 4]
    mock_speedups = [1.0, 1.85, 3.42]
    mock_times = [0.1200, 0.0650, 0.0350]
    out_img = "docs/figures/test_speedup_mock.png"

    fig, axes = visualizer.plot_speedup_analysis(
        workers=mock_workers,
        speedups=mock_speedups,
        times=mock_times,
        title="Test Speedup Analysis Chart",
        save_path=out_img,
        show=False
    )

    assert fig is not None, "Figure phải được khởi tạo thành công"
    assert os.path.exists(out_img), "Ảnh biểu đồ speedup phải được lưu thành công"
    if os.path.exists(out_img):
        os.remove(out_img) # Dọn file test tạm
    print("  -> plot_speedup_analysis hoạt động chính xác: PASSED")


def test_multi_scale_benchmark_e2e():
    print("\n[TEST 4] Kiểm tra Toàn trình Thực nghiệm Đa quy mô & Xuất Báo cáo Khoa học:")
    evaluator = BenchmarkEvaluator(seed=42)
    df = evaluator.run_multi_scale_benchmark(scales=[6, 10], include_speedup=True)

    assert isinstance(df, pd.DataFrame), "Kết quả trả về phải là DataFrame"
    assert len(df) == 2, "DataFrame phải có 2 dòng tương ứng 2 quy mô"

    csv_path = "data/processed/benchmark_comparison_results.csv"
    md_path = "docs/EXPERIMENT_RESULTS.md"
    bars_path = "docs/figures/comparison_bars.png"
    scal_path = "docs/figures/scalability_analysis.png"
    spd_path = "docs/figures/speedup_analysis.png"

    assert os.path.exists(csv_path), "File CSV kết quả phải tồn tại"
    assert os.path.exists(md_path), "File báo cáo Markdown phải tồn tại"
    assert os.path.exists(bars_path), "Biểu đồ cột comparison_bars phải tồn tại"
    assert os.path.exists(scal_path), "Biểu đồ scalability_analysis phải tồn tại"
    assert os.path.exists(spd_path), "Biểu đồ speedup_analysis phải tồn tại"

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Đúng giờ GA (%)" in content, "Báo cáo phải chứa cột Đúng giờ"
    assert "Tăng tốc Song song hóa" in content, "Báo cáo phải chứa mục Speedup"
    assert "Đánh giá An toàn Pin" in content, "Báo cáo phải chứa mục Pin"

    print("  -> Đã xác nhận đầy đủ 5 sản phẩm đầu ra (CSV, MD, 3 biểu đồ PNG): PASSED")


def main():
    print("=" * 80)
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ THỨ NĂM (NGÀY 2) - THÀNH VIÊN 5   ")
    print("  Chức năng: Thực nghiệm Đa quy mô, Đo đạc 4 Chỉ số & Biểu đồ Speedup  ")
    print("=" * 80)

    test_evaluate_scale_metrics()
    test_run_speedup_benchmark()
    test_visualizer_plot_speedup()
    test_multi_scale_benchmark_e2e()

    print("\n" + "=" * 80)
    print("  🎉 TẤT CẢ KIỂM THỬ THỨ NĂM (NGÀY 2) ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!  ")
    print("=" * 80)


if __name__ == "__main__":
    main()
