"""
Chương trình thực thi chính (Main Entrypoint) cho Đề tài Định tuyến Đa UAV (UDRP).
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import argparse
import sys
import os

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn src vào Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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
        default="6",
        help="Quy mô số điểm giao hàng (10, 50, 100) hoặc đường dẫn file JSON"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Chạy so sánh đối sánh giữa A* + GA và A* + Greedy Baseline"
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
        default=123,
        help="Random seed để tái lập kịch bản thử nghiệm"
    )
    parser.add_argument(
        "--drones",
        type=int,
        default=2,
        help="Số lượng UAV khả dụng trong đội bay"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    print("======================================================================")
    print("   HỆ THỐNG TỐI ƯU HÓA ĐỊNH TUYẾN ĐỘI BAY UAV GIAO HÀNG ĐÔ THỊ (UDRP)  ")
    print("   Phụ trách Kiến trúc & Tích hợp: Nguyễn Phúc Hà (Thành viên 5)       ")
    print("======================================================================")

    # 1. Khởi tạo Pipeline tích hợp
    pipeline = UAVRoutingPipeline(
        grid_size=(120, 120),
        num_drones=args.drones,
        drone_capacity=5.0,
        drone_speed=10.0,
        seed=args.seed
    )

    # 2. Nạp dữ liệu
    if args.benchmark.endswith(".json") and os.path.exists(args.benchmark):
        print(f"[*] Đang nạp tập dữ liệu từ file: {args.benchmark}")
        pipeline.load_benchmark_from_json(args.benchmark)
    else:
        try:
            n_cust = int(args.benchmark)
        except ValueError:
            n_cust = 10
        print(f"[*] Đang khởi tạo kịch bản thử nghiệm với {n_cust} điểm giao hàng...")
        pipeline.generate_synthetic_data(num_delivery=n_cust, num_charging=3, num_no_fly=6)

    # 3. Tính toán ma trận khoảng cách né vật cản A*
    print("[*] Đang tính toán ma trận khoảng cách né vùng cấm bay (A* Engine)...")
    pipeline.compute_distance_matrix(use_astar=True)

    # 4. Thực thi thuật toán
    show_gui = not args.no_plot

    if args.compare:
        # Chế độ so sánh đối sánh
        pipeline.compare_algorithms(save_dir=args.save_dir, show_plot=show_gui)
    else:
        # Chạy 1 thuật toán đơn lẻ
        print(f"[*] Đang chạy thuật toán: {args.algorithm.upper()}...")
        result = pipeline.run_experiment(
            algorithm=args.algorithm,
            save_figure_dir=args.save_dir,
            show_plot=show_gui
        )
        print("\n--- KẾT QUẢ THỰC THI ---")
        print(f"Thuật toán:             {result['algorithm']}")
        print(f"Thời gian tính toán:    {result['exec_time_sec']} giây")
        print(f"Tổng quãng đường:       {result['distance']} km")
        print(f"Tổng năng lượng:        {result['energy']} Wh")
        print(f"Phạt vi phạm:           {result['tw_penalty']}")
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
