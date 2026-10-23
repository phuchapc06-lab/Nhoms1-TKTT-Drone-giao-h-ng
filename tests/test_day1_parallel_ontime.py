"""
Bộ kiểm thử độc lập cho nhiệm vụ Thứ Tư (Ngày 1 - 21/10/2026):
- Song song hóa ma trận khoảng cách né vật cản A* (Parallel Distance Matrix & Speedup).
- Đo lường Tỷ lệ giao hàng đúng giờ (On-time Delivery Rate) theo khung giờ Time Windows.
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import math
import numpy as np

# Đảm bảo console Windows in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.fitness import FitnessCalculator
from utils.distance_matrix import compute_distance_matrix, benchmark_distance_matrix_speedup
from pipeline import UAVRoutingPipeline


def test_ontime_delivery_rate():
    print("\n[TEST 1] Kiểm tra Hàm đo lường Tỷ lệ Giao hàng Đúng giờ (On-time Delivery Rate):")
    calc = FitnessCalculator(drone_speed=10.0, gamma=5.0)

    # 1. Kịch bản tất cả đúng giờ (100% On-time)
    nodes_ontime = {
        0: {"id": 0, "type": "depot", "pos": (0, 0), "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "pos": (10, 0), "demand": 1.0, "tw": (1, 100), "service_time": 2}, # bay 10/10=1s -> đến lúc 1s -> đúng giờ
        2: {"id": 2, "type": "delivery", "pos": (20, 0), "demand": 1.0, "tw": (3, 100), "service_time": 2}, # bay thêm 1s -> đến lúc 4s -> đúng giờ
    }
    dist_mat = np.zeros((3, 3))
    dist_mat[0, 1] = dist_mat[1, 0] = 10.0
    dist_mat[1, 2] = dist_mat[2, 1] = 10.0
    dist_mat[0, 2] = dist_mat[2, 0] = 20.0

    solution = [[0, 1, 2, 0]]
    fitness, cost, breakdown = calc.evaluate_solution(solution, dist_mat, nodes_ontime)
    rate = calc.calculate_ontime_rate(solution, dist_mat, nodes_ontime)

    assert breakdown["on_time_deliveries"] == 2, f"Kỳ vọng 2 đơn đúng giờ, nhận {breakdown['on_time_deliveries']}"
    assert breakdown["total_deliveries"] == 2, f"Kỳ vọng tổng 2 đơn, nhận {breakdown['total_deliveries']}"
    assert breakdown["on_time_rate"] == 100.0, f"Kỳ vọng 100% đúng giờ, nhận {breakdown['on_time_rate']}"
    assert rate == 100.0, f"calculate_ontime_rate phải trả về 100.0, nhận {rate}"
    print(f"  -> Kịch bản giao hàng đúng hạn 100%: PASSED (Rate: {rate}%, On-time: {breakdown['on_time_deliveries']}/{breakdown['total_deliveries']})")

    # 2. Kịch bản có đơn trễ giờ (Khung giờ quá hẹp)
    nodes_late = {
        0: {"id": 0, "type": "depot", "pos": (0, 0), "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "pos": (10, 0), "demand": 1.0, "tw": (0.5, 0.8), "service_time": 2}, # bay 1.0s > end_tw 0.8s -> trễ!
        2: {"id": 2, "type": "delivery", "pos": (20, 0), "demand": 1.0, "tw": (1.0, 100), "service_time": 2}, # đúng giờ
    }
    fitness2, cost2, breakdown2 = calc.evaluate_solution(solution, dist_mat, nodes_late)
    rate2 = calc.calculate_ontime_rate(solution, dist_mat, nodes_late)

    assert breakdown2["on_time_deliveries"] == 1, f"Kỳ vọng 1 đơn đúng giờ, nhận {breakdown2['on_time_deliveries']}"
    assert breakdown2["total_deliveries"] == 2, f"Kỳ vọng tổng 2 đơn, nhận {breakdown2['total_deliveries']}"
    assert breakdown2["on_time_rate"] == 50.0, f"Kỳ vọng 50% đúng giờ, nhận {breakdown2['on_time_rate']}"
    assert breakdown2["tw_penalty"] > 0, "Phải có tiền phạt vi phạm khung giờ"
    assert rate2 == 50.0, f"calculate_ontime_rate phải trả về 50.0, nhận {rate2}"
    print(f"  -> Kịch bản có đơn trễ hạn: PASSED (Rate: {rate2}%, Phạt TW: {breakdown2['tw_penalty']:.2f})")


def test_parallel_distance_matrix():
    print("\n[TEST 2] Kiểm tra Tính toán Ma trận Khoảng cách Song song (Parallel A* Matrix):")
    nodes = {
        0: {"id": 0, "pos": (5, 5), "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "pos": (15, 20), "type": "delivery", "demand": 1.5, "tw": (10, 60), "service_time": 5},
        2: {"id": 2, "pos": (35, 10), "type": "delivery", "demand": 2.0, "tw": (15, 80), "service_time": 5},
        3: {"id": 3, "pos": (20, 45), "type": "delivery", "demand": 1.0, "tw": (20, 90), "service_time": 5},
        4: {"id": 4, "pos": (45, 40), "type": "delivery", "demand": 1.2, "tw": (25, 100), "service_time": 5},
    }
    no_fly_zones = [
        (10, 10, 8, 8),
        (25, 25, 10, 10)
    ]
    grid_size = (50, 50)

    # 1. Tính tuần tự
    dist_seq, paths_seq = compute_distance_matrix(
        nodes, no_fly_zones, grid_size, cache_path=None, force=True, parallel=False
    )

    # 2. Tính song song với 2 workers
    dist_par, paths_par = compute_distance_matrix(
        nodes, no_fly_zones, grid_size, cache_path=None, force=True, parallel=True, num_workers=2
    )

    # Kiểm tra tính đồng nhất của kết quả
    assert np.allclose(dist_seq, dist_par, atol=1e-5), "Ma trận tính song song phải giống hệt ma trận tính tuần tự"
    assert len(paths_seq) == len(paths_par), "Số lượng đường bay chi tiết phải bằng nhau"
    print(f"  -> So sánh ma trận Tuần tự vs Song song ({len(nodes)}x{len(nodes)}): PASSED (Khớp 100%)")


def test_speedup_measurement():
    print("\n[TEST 3] Kiểm tra Đo đạc Tốc độ Tăng tốc (Speedup Measurement):")
    nodes = {
        0: {"id": 0, "pos": (5, 5), "type": "depot", "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "pos": (12, 18), "type": "delivery", "demand": 1.0, "tw": (10, 60), "service_time": 5},
        2: {"id": 2, "pos": (30, 15), "type": "delivery", "demand": 1.0, "tw": (15, 80), "service_time": 5},
        3: {"id": 3, "pos": (18, 35), "type": "delivery", "demand": 1.0, "tw": (20, 90), "service_time": 5},
    }
    no_fly_zones = [(10, 10, 12, 12)]
    grid_size = (40, 40)

    res = benchmark_distance_matrix_speedup(nodes, no_fly_zones, grid_size, workers_list=[1, 2])
    assert "times_sec" in res, "Kết quả phải chứa times_sec"
    assert "speedup" in res, "Kết quả phải chứa speedup"
    assert "S_1" in res["speedup"], "S_1 phải tồn tại"
    assert res["speedup"]["S_1"] == 1.0, "S_1 với 1 worker phải bằng 1.0"
    print(f"  -> Đo đạc Speedup với 1 & 2 workers: PASSED ({res['times_sec']})")


def test_pipeline_integration_with_parallel_and_ontime():
    print("\n[TEST 4] Kiểm tra Tích hợp Pipeline với Chế độ Song song & On-time Rate:")
    pipeline = UAVRoutingPipeline(grid_size=(40, 40), num_drones=2, seed=42)
    pipeline.generate_synthetic_data(num_delivery=6, num_charging=2, num_no_fly=3)

    # 1. Tính ma trận song song
    pipeline.compute_distance_matrix(use_astar=True, parallel=True, num_workers=2)
    assert pipeline.dist_matrix is not None, "Ma trận khoảng cách không được None"

    # 2. Chạy thuật toán đối chuẩn Greedy
    res_greedy = pipeline.run_experiment(
        algorithm="greedy",
        save_figure_dir=None,
        show_plot=False,
        parallel=True,
        num_workers=2
    )

    assert "on_time_rate" in res_greedy, "Kết quả phải chứa on_time_rate"
    assert "on_time_deliveries" in res_greedy, "Kết quả phải chứa on_time_deliveries"
    assert "total_deliveries" in res_greedy, "Kết quả phải chứa total_deliveries"
    assert 0.0 <= res_greedy["on_time_rate"] <= 100.0, "on_time_rate phải nằm trong [0, 100]"
    assert res_greedy["total_deliveries"] == 6, f"Kỳ vọng 6 đơn hàng, nhận {res_greedy['total_deliveries']}"
    print(f"  -> Pipeline Greedy với cờ Parallel: PASSED (On-time Rate: {res_greedy['on_time_rate']}%, Cost: {res_greedy['total_cost']})")

    # 3. Đo speedup trực tiếp từ Pipeline
    sp_res = pipeline.measure_parallel_speedup(workers_list=[1, 2])
    assert "speedup" in sp_res, "measure_parallel_speedup phải trả về dict chứa speedup"
    print(f"  -> Pipeline measure_parallel_speedup: PASSED (S_2: {sp_res['speedup'].get('S_2', 1.0)}x)")


def main():
    print("=" * 75)
    print("  BẮT ĐẦU KIỂM THỬ ĐỘC LẬP NHIỆM VỤ THỨ TƯ (NGÀY 1) - THÀNH VIÊN 5   ")
    print("  Chức năng: Song song hóa A* Distance Matrix & Chỉ số Giao đúng giờ ")
    print("=" * 75)

    test_ontime_delivery_rate()
    test_parallel_distance_matrix()
    test_speedup_measurement()
    test_pipeline_integration_with_parallel_and_ontime()

    print("\n" + "=" * 75)
    print("  🎉 TẤT CẢ KIỂM THỬ THỨ TƯ (NGÀY 1) ĐÃ VƯỢT QUA 100% THÀNH CÔNG RỰC RỠ!  ")
    print("=" * 75)


if __name__ == "__main__":
    main()
