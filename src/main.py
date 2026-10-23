"""
Chương trình thực thi chính (Main Entrypoint) cho Đề tài Định tuyến Đa UAV (UDRP).
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import argparse
import sys
import os
import math

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src và root vào Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline import UAVRoutingPipeline

def parse_args():
    parser = argparse.ArgumentParser(
        description="UAV Delivery Routing Problem (UDRP) - Hệ thống Tối ưu hóa Định tuyến Đa Drone"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["ga", "greedy"],
        default="ga",
        help="Thuật toán tối ưu cần chạy: 'ga' (Genetic Algorithm) hoặc 'greedy' (Baseline)"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="10",
        help="Quy mô số điểm giao hàng (10, 50, 100, 500) hoặc đường dẫn file JSON"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Chạy so sánh đối sánh giữa A* + GA và A* + Greedy Baseline"
    )
    parser.add_argument(
        "--evaluate-all",
        action="store_true",
        help="Chạy kiểm thử đối sánh đa quy mô, xuất báo cáo EXPERIMENT_RESULTS.md và biểu đồ cột/scalability/speedup"
    )
    parser.add_argument(
        "--scales",
        type=str,
        default="10,20,30,50",
        help="Danh sách quy mô điểm giao hàng phân tách bằng dấu phẩy (mặc định: 10,20,30,50)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Chạy toàn bộ các bộ kiểm thử tự động của hệ thống (Master Test Runner)"
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Không hiển thị popup cửa sổ đồ thị (chế độ chạy tự động / batch test)"
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="docs/figures",
        help="Thư mục lưu ảnh bản đồ và đồ thị hội tụ"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed để tái lập kịch bản thử nghiệm"
    )
    parser.add_argument(
        "--drones",
        type=int,
        default=None,
        help="Số lượng UAV khả dụng trong đội bay (mặc định: tự động tính theo tổng tải trọng)"
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=None,
        help="Số lượng thế hệ tiến hóa của GA (mặc định: tự động tối ưu theo quy mô)"
    )
    parser.add_argument(
        "--pop-size",
        type=int,
        default=None,
        help="Kích thước quần thể của GA (mặc định: tự động tối ưu theo quy mô)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Bật chế độ tính toán song song (Parallel Computing) cho ma trận khoảng cách A*"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Số lượng luồng/worker tính toán song song (mặc định: tự động phát hiện số CPU cores)"
    )
    parser.add_argument(
        "--speedup",
        action="store_true",
        help="Đo đạc và in hệ số tăng tốc (Speedup Sp = T1 / Tp) khi song song hóa A*"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    print("======================================================================")
    print("   HỆ THỐNG TỐI ƯU HÓA ĐỊNH TUYẾN ĐỘI BAY UAV GIAO HÀNG ĐÔ THỊ (UDRP)  ")
    print("   Phụ trách Kiến trúc & Tích hợp: Nguyễn Phúc Hà (Thành viên 5)       ")
    print("======================================================================")

    # Nếu người dùng chọn chạy bộ kiểm thử toàn diện
    if args.test:
        from tests.run_all_tests import main as run_tests
        run_tests()
        return

    # Nếu người dùng chọn chạy bộ đánh giá thực nghiệm đa quy mô
    if args.evaluate_all:
        from utils.benchmark_evaluator import BenchmarkEvaluator
        print("[*] Đang khởi chạy bộ đánh giá thực nghiệm đa quy mô (Multi-Scale Evaluator)...")
        evaluator = BenchmarkEvaluator(
            save_figures_dir=args.save_dir,
            results_dir="docs",
            csv_dir="data/processed",
            seed=args.seed
        )
        scale_list = [int(s.strip()) for s in args.scales.split(",") if s.strip().isdigit()]
        if not scale_list:
            scale_list = [10, 20, 30, 50]
        evaluator.run_multi_scale_benchmark(scales=scale_list, include_speedup=True)
        print(f"\n[✓] Đã hoàn tất thực nghiệm đối sánh đa quy mô!")
        print(f"[✓] Xem báo cáo chi tiết tại: docs/EXPERIMENT_RESULTS.md")
        print(f"[✓] Xem file số liệu CSV tại: data/processed/benchmark_comparison_results.csv")
        print(f"[✓] Xem bộ biểu đồ tại: {args.save_dir}/ (comparison_bars.png, scalability_analysis.png, speedup_analysis.png)")
        return

    # 1. Khởi tạo Pipeline tích hợp
    pipeline = UAVRoutingPipeline(
        grid_size=(60, 60),
        num_drones=3,
        drone_capacity=5.0,
        drone_speed=10.0,
        seed=args.seed
    )

    # 2. Nạp dữ liệu
    candidate_file = (
        args.benchmark
        if args.benchmark.endswith(".json")
        else os.path.join("data", "raw", f"benchmark_{args.benchmark}.json")
    )

    if os.path.exists(candidate_file):
        print(f"[*] Đang nạp tập dữ liệu từ file: {candidate_file}")
        pipeline.load_benchmark_from_json(candidate_file)
    else:
        try:
            n_cust = int(args.benchmark)
        except ValueError:
            n_cust = 10
        print(f"[*] Đang khởi tạo kịch bản thử nghiệm với {n_cust} điểm giao hàng...")
        pipeline.generate_synthetic_data(num_delivery=n_cust, num_charging=3, num_no_fly=6)

    # 3. Phân bổ số lượng UAV linh hoạt theo tổng tải trọng nếu người dùng không chỉ định
    total_demand = sum(node.get("demand", 0.0) for node in pipeline.nodes.values() if node.get("type") == "delivery")
    min_drones = max(3, int(math.ceil(total_demand / pipeline.drone_capacity * 1.2)))
    if args.drones is not None:
        pipeline.num_drones = args.drones
    else:
        pipeline.num_drones = min_drones

    num_deliveries = len([k for k, v in pipeline.nodes.items() if v.get("type") == "delivery"])
    print(f"[*] Quy mô: {num_deliveries} điểm giao hàng, Tổng tải: {total_demand:.2f}kg -> Bố trí đội bay: {pipeline.num_drones} UAVs.")

    # 4. Tính toán ma trận khoảng cách né vật cản A* (hỗ trợ đo Speedup và chạy song song)
    if args.speedup:
        print("[*] Đang thực nghiệm đo đạc tốc độ tăng tốc song song hóa (Parallel Speedup)...")
        speedup_res = pipeline.measure_parallel_speedup(workers_list=[1, 2, 4])
        print("\n" + "="*50)
        print("   KẾT QUẢ ĐO ĐẠC HỆ SỐ TĂNG TỐC SONG SONG HÓA A*")
        print("="*50)
        for w in [1, 2, 4]:
            t_w = speedup_res["times_sec"].get(f"{w}_workers", 0.0)
            sp_w = speedup_res["speedup"].get(f"S_{w}", 1.0)
            print(f"  - {w} Worker(s): {t_w:.4f}s  ->  Speedup S_{w} = {sp_w:.2f}x")
        print("="*50 + "\n")

    par_mode_str = f" [Song song {args.workers or 'đa'} luồng]" if args.parallel else ""
    print(f"[*] Đang tính toán ma trận khoảng cách né vùng cấm bay (A* Engine){par_mode_str}...")
    pipeline.compute_distance_matrix(use_astar=True, parallel=args.parallel, num_workers=args.workers)

    # 5. Thực thi thuật toán
    show_gui = not args.no_plot

    if args.compare:
        # Chế độ so sánh đối sánh
        pipeline.compare_algorithms(
            save_dir=args.save_dir,
            show_plot=show_gui,
            generations=args.generations,
            pop_size=args.pop_size,
            parallel=args.parallel,
            num_workers=args.workers
        )
    else:
        # Chạy 1 thuật toán đơn lẻ
        print(f"[*] Đang chạy thuật toán: {args.algorithm.upper()}...")
        result = pipeline.run_experiment(
            algorithm=args.algorithm,
            save_figure_dir=args.save_dir,
            show_plot=show_gui,
            generations=args.generations,
            pop_size=args.pop_size,
            parallel=args.parallel,
            num_workers=args.workers
        )
        print("\n--- KẾT QUẢ THỰC THI ---")
        print(f"Thuật toán:             {result['algorithm']}")
        print(f"Thời gian tính toán:    {result['exec_time_sec']} giây")
        print(f"Tổng quãng đường:       {result['distance']} km")
        print(f"Tổng năng lượng:        {result['energy']} Wh")
        print(f"Phạt vi phạm:           {result['tw_penalty']}")
        print(f"Tỷ lệ đúng giờ:         {result.get('on_time_rate', 100.0)}% ({result.get('on_time_deliveries', 0)}/{result.get('total_deliveries', 0)} đơn)")
        print(f"Tổng chi phí (Cost):    {result['total_cost']}")
        print(f"Điểm thích nghi (Fit):  {result['fitness']}")
        print(f"Hợp lệ ràng buộc:       {result['is_valid']}")
        print("\nLộ trình phân bổ các Drone:")
        for idx, route in enumerate(result['solution']):
            print(f"  - Drone #{idx+1}: {route}")
        print(f"\n[+] Đã lưu hình ảnh bản đồ và đồ thị vào thư mục: {args.save_dir}")

    print("\n[✓] Chương trình hoàn tất thành công.")

if __name__ == "__main__":
    main()
