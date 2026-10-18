"""
Thực nghiệm tinh chỉnh tham số và đánh giá GA trên bộ benchmark của TV4.
Phụ trách: Thành viên 1 (GA Core Engine).

Chạy từ thư mục repo (cần data/raw/benchmark_{N}.json, sinh bằng src/utils/benchmark_generator.py):
    python src/utils/ga_tuning.py sweep --scales 10 50 --seeds 10
    python src/utils/ga_tuning.py sweep --scales 50 --pop-sizes 100 --generations 500 1000 2000 --seed-greedy
    python src/utils/ga_tuning.py compare --scales 10 50 100 --seeds 5 --pop-size 100 --mutation-rate 0.2 --generations 1000
"""
import argparse
import itertools
import math
import os
import statistics
import sys
from typing import Dict, List, Any, Optional

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline import UAVRoutingPipeline
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.baseline_greedy import GreedyRouter
from utils.distance_matrix import compute_distance_matrix

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DRONE_CAPACITY = 5.0
# Mô hình hiện tại mỗi Drone chỉ bay 1 chuyến -> đội bay phải chở được >= 1.2 x tổng khối lượng hàng
CAPACITY_SLACK = 1.2
# Cấu hình GA mà pipeline.run_experiment đang dùng trước Phase 5 (mốc "trước tinh chỉnh")
PIPELINE_OLD_PARAMS = {"pop_size": 50, "generations": 80, "mutation_rate": 0.2, "constraint_penalty_factor": 1.0}


def load_benchmark(num_delivery: int) -> UAVRoutingPipeline:
    """
    Nạp benchmark_{N}.json qua pipeline của TV5, chọn số Drone K theo tổng khối lượng hàng
    (K = 3 với N = 10, khớp mặc định của pipeline) và tính ma trận khoảng cách A* của TV2.
    """
    data_path = os.path.join(REPO_DIR, "data", "raw", f"benchmark_{num_delivery}.json")
    pipeline = UAVRoutingPipeline(drone_capacity=DRONE_CAPACITY)
    if not pipeline.load_benchmark_from_json(data_path):
        raise SystemExit(f"Không nạp được {data_path} - hãy chạy src/utils/benchmark_generator.py trước")

    total_demand = sum(n["demand"] for n in pipeline.nodes.values() if n["type"] == "delivery")
    pipeline.num_drones = math.ceil(total_demand * CAPACITY_SLACK / DRONE_CAPACITY)

    # Mỗi quy mô một file cache riêng (cache mặc định của TV2 chỉ giữ 1 bộ dữ liệu)
    cache_path = os.path.join(REPO_DIR, "data", "processed", f"distance_matrix_{num_delivery}.pkl")
    dist, paths = compute_distance_matrix(
        pipeline.nodes, pipeline.no_fly_zones, pipeline.grid_size, cache_path=cache_path
    )
    # Cặp không tới được: xử lý giống pipeline.compute_distance_matrix (Euclid x 2)
    for i, j in zip(*np.where(np.isinf(dist))):
        dist[i, j] = math.dist(pipeline.nodes[i]["pos"], pipeline.nodes[j]["pos"]) * 2.0
    pipeline.dist_matrix, pipeline.detailed_paths = dist, paths
    return pipeline


def greedy_solution(pipeline: UAVRoutingPipeline) -> List[List[int]]:
    """Lời giải Greedy của TV6 (chưa qua 2-Opt / chèn trạm sạc)."""
    return GreedyRouter(pipeline.nodes, pipeline.dist_matrix, pipeline.num_drones, pipeline.drone_capacity).solve()


# ----------------------------------------------------------------------
# 1. Quét tham số
# ----------------------------------------------------------------------
def sweep(
    pipeline: UAVRoutingPipeline, seeds: List[int], pop_sizes: List[int], mutation_rates: List[float],
    checkpoints: List[int], seed_greedy: bool = False
) -> List[Dict[str, Any]]:
    """
    Quét pop_size x mutation_rate; mỗi cấu hình chạy mọi seed với số thế hệ lớn nhất.
    Kết quả ở các mốc thế hệ nhỏ hơn đọc từ history của cùng lần chạy: cùng seed thì các thế hệ đầu
    giống hệt một lần chạy ngắn hơn. Thời gian ở mốc nhỏ được ước lượng theo tỷ lệ số thế hệ.
    """
    initial = [greedy_solution(pipeline)] if seed_greedy else None
    rows = []
    max_gen = max(checkpoints)
    for pop_size, mutation_rate in itertools.product(pop_sizes, mutation_rates):
        costs: Dict[int, List[float]] = {g: [] for g in checkpoints}
        runtimes = []
        for seed in seeds:
            ga = GeneticAlgorithm(
                pipeline.nodes, pipeline.dist_matrix, pipeline.num_drones,
                fitness_calc=pipeline.fitness_calc, pop_size=pop_size,
                generations=max_gen, mutation_rate=mutation_rate, seed=seed, initial_solutions=initial
            )
            ga.evolve()
            for g in checkpoints:
                costs[g].append(1000.0 / ga.history[g - 1] - 1.0)  # fitness = 1000 / (cost + 1)
            runtimes.append(ga.runtime)
        for g in checkpoints:
            rows.append({
                "pop_size": pop_size, "mutation_rate": mutation_rate, "generations": g,
                "costs": costs[g], "runtime": statistics.mean(runtimes) * g / max_gen
            })
        print(f"  xong pop_size={pop_size}, mutation_rate={mutation_rate}", flush=True)
    return rows


def format_sweep(rows: List[Dict[str, Any]], reference_cost: Optional[float] = None) -> str:
    """Bảng Markdown, sắp theo cost trung bình tăng dần. reference_cost: cost của Greedy cùng thước đo."""
    best_known = min(min(r["costs"]) for r in rows)
    lines = [f"Cost tốt nhất tìm được qua mọi lần chạy: **{best_known:.2f}**"]
    if reference_cost is not None:
        lines.append(f"Cost của Greedy (cùng thước đo của GA, chưa 2-Opt): **{reference_cost:.2f}**")
    lines += [
        "",
        "| pop_size | mutation_rate | Thế hệ | Cost TB | Độ lệch chuẩn | Tốt nhất | Tệ nhất | TB lệch so với tốt nhất | Số lần đạt tốt nhất | Thời gian TB (s) |",
        "| :---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: |",
    ]
    for r in sorted(rows, key=lambda r: statistics.mean(r["costs"])):
        c = r["costs"]
        mean = statistics.mean(c)
        hits = sum(math.isclose(x, best_known, rel_tol=1e-9) for x in c)
        lines.append(
            f"| {r['pop_size']} | {r['mutation_rate']} | {r['generations']} | {mean:.2f} | "
            f"{statistics.stdev(c) if len(c) > 1 else 0.0:.2f} | {min(c):.2f} | {max(c):.2f} | "
            f"{100 * (mean / best_known - 1):.2f}% | {hits}/{len(c)} | {r['runtime']:.2f} |"
        )
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 2. So sánh với Greedy qua luồng đầy đủ của pipeline
# ----------------------------------------------------------------------
def run_greedy(pipeline: UAVRoutingPipeline) -> Dict[str, Any]:
    """Greedy qua đúng luồng run_experiment của pipeline (Greedy -> 2-Opt -> chèn trạm sạc -> chấm điểm)."""
    # solve_greedy có fallback âm thầm khi GreedyRouter lỗi -> bảo đảm đang đo đúng thuật toán của TV6
    assert pipeline.solve_greedy() == greedy_solution(pipeline), "Pipeline không dùng GreedyRouter của TV6"
    return pipeline.run_experiment("greedy", save_figure_dir=None)


def run_ga(
    pipeline: UAVRoutingPipeline, seed: int, ga_params: Dict[str, Any],
    use_energy_manager: bool = False, seed_greedy: bool = False
) -> Dict[str, Any]:
    """
    GA qua đúng luồng run_experiment của pipeline (GA -> 2-Opt -> chèn trạm sạc -> chấm điểm có EnergyManager).
    Thời gian đo bởi run_experiment gồm cả bước chạy Greedy để khởi tạo (nếu seed_greedy).
    """
    def solve_ga(*_args, **_kwargs):  # bỏ qua tham số run_experiment truyền vào: cấu hình lấy từ ga_params
        ga = GeneticAlgorithm(
            pipeline.nodes, pipeline.dist_matrix, pipeline.num_drones,
            fitness_calc=pipeline.fitness_calc,
            energy_manager=pipeline.energy_manager if use_energy_manager else None,
            initial_solutions=[greedy_solution(pipeline)] if seed_greedy else None,
            seed=seed, **ga_params
        )
        solution, _, history = ga.evolve()
        return solution, history

    pipeline.solve_ga = solve_ga
    try:
        return pipeline.run_experiment("ga", save_figure_dir=None)
    finally:
        del pipeline.solve_ga  # trả lại phương thức gốc của class


def compare(pipeline: UAVRoutingPipeline, seeds: List[int], ga_params: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Thang cải tiến: mỗi dòng GA thêm đúng một thay đổi so với dòng trên."""
    tuned = ", ".join(f"{k}={v}" for k, v in ga_params.items())
    return {
        "Greedy + 2-Opt (baseline)": [run_greedy(pipeline)],  # tất định -> chạy 1 lần
        "GA - cấu hình cũ của pipeline (80 thế hệ, 50 cá thể, mutation_rate=0.2, phạt gốc của TV5)": [
            run_ga(pipeline, s, PIPELINE_OLD_PARAMS) for s in seeds
        ],
        f"GA - tham số tinh chỉnh ({tuned})": [run_ga(pipeline, s, ga_params) for s in seeds],
        "GA - tinh chỉnh + EnergyManager": [run_ga(pipeline, s, ga_params, use_energy_manager=True) for s in seeds],
        "GA - tinh chỉnh + EnergyManager + khởi tạo từ Greedy": [
            run_ga(pipeline, s, ga_params, use_energy_manager=True, seed_greedy=True) for s in seeds
        ],
    }


def format_compare(variants: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Bảng Markdown so sánh các biến thể (trung bình ± độ lệch chuẩn qua các seed),
    kèm % chênh lệch tổng chi phí so với Greedy (biến thể đầu tiên trong variants).
    """
    def stat(results, key, digits=2):
        values = [r[key] for r in results]
        if len(values) == 1:
            return f"{values[0]:.{digits}f}"
        return f"{statistics.mean(values):.{digits}f} ± {statistics.stdev(values):.{digits}f}"

    lines = [
        "| Thuật toán | Số lần chạy | Quãng đường | Năng lượng | Phạt trễ giờ | Tổng chi phí | Hợp lệ | Thời gian (s) |",
        "| :--- | :---: | ---: | ---: | ---: | ---: | :---: | ---: |",
    ]
    for name, results in variants.items():
        valid = sum(r["is_valid"] for r in results)
        lines.append(
            f"| {name} | {len(results)} | {stat(results, 'distance')} | {stat(results, 'energy')} | "
            f"{stat(results, 'tw_penalty')} | {stat(results, 'total_cost')} | {valid}/{len(results)} | "
            f"{stat(results, 'exec_time_sec', 3)} |"
        )

    greedy_cost = next(iter(variants.values()))[0]["total_cost"]
    lines.append("")
    for name, results in list(variants.items())[1:]:
        mean_cost = statistics.mean(r["total_cost"] for r in results)
        lines.append(f"- {name}: tổng chi phí {'thấp' if mean_cost < greedy_cost else 'cao'} hơn Greedy "
                     f"{abs(100 * (1 - mean_cost / greedy_cost)):.2f}%")
    return "\n".join(lines)


def main():
    """Dòng lệnh: `sweep` (quét tham số) hoặc `compare` (so sánh với Greedy); in kết quả dạng Markdown."""
    parser = argparse.ArgumentParser(description="Thực nghiệm tinh chỉnh tham số GA (TV1)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sweep = sub.add_parser("sweep", help="Quét pop_size x mutation_rate x số thế hệ")
    p_sweep.add_argument("--scales", type=int, nargs="+", default=[10, 50])
    p_sweep.add_argument("--seeds", type=int, default=10)
    p_sweep.add_argument("--pop-sizes", type=int, nargs="+", default=[50, 80, 100])
    p_sweep.add_argument("--mutation-rates", type=float, nargs="+", default=[0.2, 0.5, 0.8])
    p_sweep.add_argument("--generations", type=int, nargs="+", default=[200, 500],
                         help="Các mốc số thế hệ (chỉ chạy 1 lần với mốc lớn nhất)")
    p_sweep.add_argument("--seed-greedy", action="store_true", help="Đưa lời giải Greedy vào quần thể ban đầu")

    p_cmp = sub.add_parser("compare", help="So sánh Greedy và GA qua luồng đầy đủ của pipeline")
    p_cmp.add_argument("--scales", type=int, nargs="+", default=[10, 50, 100])
    p_cmp.add_argument("--seeds", type=int, default=5)
    p_cmp.add_argument("--pop-size", type=int, required=True)
    p_cmp.add_argument("--mutation-rate", type=float, required=True)
    p_cmp.add_argument("--generations", type=int, required=True)
    p_cmp.add_argument("--penalty-factor", type=float, default=100.0, help="constraint_penalty_factor của GA")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.command == "sweep":
        for n in args.scales:
            pipeline = load_benchmark(n)
            mode = ", khởi tạo từ Greedy" if args.seed_greedy else ""
            print(f"\n## Benchmark {n} điểm giao (K = {pipeline.num_drones} Drone, {args.seeds} seed / cấu hình{mode})\n", flush=True)
            rows = sweep(pipeline, list(range(args.seeds)), args.pop_sizes, args.mutation_rates,
                         args.generations, args.seed_greedy)
            greedy_cost = pipeline.fitness_calc.evaluate_solution(greedy_solution(pipeline), pipeline.dist_matrix, pipeline.nodes)[1]
            print("\n" + format_sweep(rows, greedy_cost), flush=True)

    elif args.command == "compare":
        ga_params = {"pop_size": args.pop_size, "mutation_rate": args.mutation_rate, "generations": args.generations,
                     "constraint_penalty_factor": args.penalty_factor}
        for n in args.scales:
            pipeline = load_benchmark(n)
            print(f"\n## Benchmark {n} điểm giao (K = {pipeline.num_drones} Drone, GA chạy {args.seeds} seed)\n", flush=True)
            print(format_compare(compare(pipeline, list(range(args.seeds)), ga_params)), flush=True)


if __name__ == "__main__":
    main()
