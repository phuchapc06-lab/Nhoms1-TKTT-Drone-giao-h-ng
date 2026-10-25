"""
Thực nghiệm tinh chỉnh tham số và đánh giá GA trên bộ benchmark của TV4.
Phụ trách: Thành viên 1 (GA Core Engine).

Chạy từ thư mục repo (cần data/raw/benchmark_{N}.json, sinh bằng src/utils/benchmark_generator.py):
    python src/utils/ga_tuning.py sweep --scales 10 50 --seeds 10
    python src/utils/ga_tuning.py sweep --scales 50 --pop-sizes 100 --generations 500 1000 2000 --seed-greedy
    python src/utils/ga_tuning.py compare --scales 10 50 100 --seeds 5 --pop-size 100 --mutation-rate 0.2 --generations 1000
    python src/utils/ga_tuning.py compare --scales 500 --seeds 3 --pop-size 100 --mutation-rate 0.5 --generations 2000 --workers 8 --only-proposed
    python src/utils/ga_tuning.py speedup --scales 10 100 500 --workers 1 2 4 8 --generations 200
"""
import argparse
import csv
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

    # Mỗi quy mô một file cache riêng (cache mặc định của TV2 chỉ giữ 1 bộ dữ liệu).
    # Chưa có cache thì tính song song (ma trận 500 điểm: ~50 s với 8 tiến trình)
    cache_path = os.path.join(REPO_DIR, "data", "processed", f"distance_matrix_{num_delivery}.pkl")
    dist, paths = compute_distance_matrix(
        pipeline.nodes, pipeline.no_fly_zones, pipeline.grid_size, cache_path=cache_path, parallel=True
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
def battery_infeasible_routes(pipeline: UAVRoutingPipeline, solution: List[List[int]], repair: bool = False) -> int:
    """
    Số tuyến thiếu pin theo EnergyManager (đúng phép kiểm tra FitnessCalculator dùng để phạt 1000 / tuyến).
    repair=True: chèn trạm sạc trước khi kiểm tra (cho lời giải chưa qua bước sửa pin của pipeline).
    Không dùng cờ thứ 3 của repair_route_with_charging: cờ đó còn báo cả tuyến chỉ xuống dưới ngưỡng 15%
    (pin vẫn dương), khắt khe hơn phép kiểm tra của FitnessCalculator và của cột "sau 2-Opt".
    Validator của TV5 không kiểm tra pin nên phải đếm riêng.
    """
    em, dist, nodes = pipeline.energy_manager, pipeline.dist_matrix, pipeline.nodes
    if repair:
        solution = [em.repair_route_with_charging(r, dist, nodes)[0] for r in solution]
    return sum(not em.calculate_route_energy(r, dist, nodes)[1] for r in solution)


def run_greedy(pipeline: UAVRoutingPipeline) -> Dict[str, Any]:
    """Greedy qua đúng luồng run_experiment của pipeline (Greedy -> 2-Opt -> chèn trạm sạc -> chấm điểm)."""
    # solve_greedy có fallback âm thầm khi GreedyRouter lỗi -> bảo đảm đang đo đúng thuật toán của TV6
    assert pipeline.solve_greedy() == greedy_solution(pipeline), "Pipeline không dùng GreedyRouter của TV6"
    result = pipeline.run_experiment("greedy", save_figure_dir=None)
    result["battery_infeasible"] = battery_infeasible_routes(pipeline, result["solution"])
    return result


def run_ga(
    pipeline: UAVRoutingPipeline, seed: int, ga_params: Dict[str, Any],
    use_energy_manager: bool = False, seed_greedy: bool = False
) -> Dict[str, Any]:
    """
    GA qua đúng luồng run_experiment của pipeline (GA -> 2-Opt -> chèn trạm sạc -> chấm điểm có EnergyManager).
    Thời gian đo bởi run_experiment gồm cả bước chạy Greedy để khởi tạo (nếu seed_greedy).
    Kết quả có thêm khóa "history" (đường hội tụ của GA) để kiểm tra số thế hệ đã đủ chưa, và số tuyến
    thiếu pin của lời giải GA trước 2-Opt ("battery_infeasible_ga") lẫn sau cả luồng ("battery_infeasible").
    """
    captured = {}

    def solve_ga(*_args, **_kwargs):  # bỏ qua tham số run_experiment truyền vào: cấu hình lấy từ ga_params
        ga = GeneticAlgorithm(
            pipeline.nodes, pipeline.dist_matrix, pipeline.num_drones,
            fitness_calc=pipeline.fitness_calc,
            energy_manager=pipeline.energy_manager if use_energy_manager else None,
            initial_solutions=[greedy_solution(pipeline)] if seed_greedy else None,
            seed=seed, **ga_params
        )
        solution, _, history = ga.evolve()
        captured["history"], captured["solution"] = history, solution
        return solution, history

    pipeline.solve_ga = solve_ga
    try:
        result = pipeline.run_experiment("ga", save_figure_dir=None)
    finally:
        del pipeline.solve_ga  # trả lại phương thức gốc của class
    result["history"] = captured["history"]
    result["battery_infeasible_ga"] = battery_infeasible_routes(pipeline, captured["solution"], repair=True)
    result["battery_infeasible"] = battery_infeasible_routes(pipeline, result["solution"])
    return result


def compare(
    pipeline: UAVRoutingPipeline, seeds: List[int], ga_params: Dict[str, Any], full: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Thang cải tiến: mỗi dòng GA thêm đúng một thay đổi so với dòng trên.
    full=False: chỉ chạy Greedy và GA đề xuất (dòng cuối), dùng cho quy mô lớn (500 điểm).
    Cấu hình cũ luôn chạy tuần tự (không nhận num_workers trong ga_params).
    """
    tuned = ", ".join(f"{k}={v}" for k, v in ga_params.items() if k != "num_workers")
    variants = {"Greedy + 2-Opt (baseline)": [run_greedy(pipeline)]}  # tất định -> chạy 1 lần
    if full:
        variants["GA - cấu hình cũ của pipeline (80 thế hệ, 50 cá thể, mutation_rate=0.2, phạt gốc của TV5)"] = [
            run_ga(pipeline, s, PIPELINE_OLD_PARAMS) for s in seeds
        ]
        variants[f"GA - tham số tinh chỉnh ({tuned})"] = [run_ga(pipeline, s, ga_params) for s in seeds]
        variants["GA - tinh chỉnh + EnergyManager"] = [
            run_ga(pipeline, s, ga_params, use_energy_manager=True) for s in seeds
        ]
    variants["GA - tinh chỉnh + EnergyManager + khởi tạo từ Greedy"] = [
        run_ga(pipeline, s, ga_params, use_energy_manager=True, seed_greedy=True) for s in seeds
    ]
    return variants


def format_convergence(results: List[Dict[str, Any]]) -> str:
    """
    Cost theo thước đo chọn lọc của GA (có nhân phạt, chưa 2-Opt) ở 1/2, 3/4 và cuối số thế hệ,
    trung bình qua các seed: nếu 1/4 số thế hệ cuối còn giảm đáng kể thì nên chạy thêm thế hệ.
    """
    generations = len(results[0]["history"])
    marks = [generations // 2, 3 * generations // 4, generations]
    means = [statistics.mean(1000.0 / r["history"][g - 1] - 1.0 for r in results) for g in marks]
    parts = ", ".join(f"thế hệ {g}: {m:.2f}" for g, m in zip(marks, means))
    before = [r["battery_infeasible_ga"] for r in results]
    after = [r["battery_infeasible"] for r in results]
    return (f"- Hội tụ (GA đề xuất, cost chọn lọc TB): {parts} → 1/4 cuối giảm {100 * (1 - means[2] / means[1]):.2f}%\n"
            f"- Tuyến thiếu pin của GA đề xuất theo seed: trước 2-Opt {before}, sau 2-Opt {after}")


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
        "| Thuật toán | Số lần chạy | Quãng đường | Năng lượng | Phạt trễ giờ | Đúng giờ (%) | Tuyến thiếu pin "
        "| Tổng chi phí | Hợp lệ | Thời gian (s) |",
        "| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: |",
    ]
    for name, results in variants.items():
        valid = sum(r["is_valid"] for r in results)
        lines.append(
            f"| {name} | {len(results)} | {stat(results, 'distance')} | {stat(results, 'energy')} | "
            f"{stat(results, 'tw_penalty')} | {stat(results, 'on_time_rate', 1)} | "
            f"{stat(results, 'battery_infeasible', 1)} | {stat(results, 'total_cost')} | "
            f"{valid}/{len(results)} | "
            f"{stat(results, 'exec_time_sec', 3)} |"
        )

    greedy_cost = next(iter(variants.values()))[0]["total_cost"]
    lines.append("")
    for name, results in list(variants.items())[1:]:
        mean_cost = statistics.mean(r["total_cost"] for r in results)
        lines.append(f"- {name}: tổng chi phí {'thấp' if mean_cost < greedy_cost else 'cao'} hơn Greedy "
                     f"{abs(100 * (1 - mean_cost / greedy_cost)):.2f}%")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 3. Đo tăng tốc khi đánh giá fitness song song
# ----------------------------------------------------------------------
def speedup(
    pipeline: UAVRoutingPipeline, workers: List[int], generations: int, pop_size: int,
    repeats: int, use_energy_manager: bool, seed: int = 0
) -> List[Dict[str, Any]]:
    """
    Chạy cùng một cấu hình GA (cùng seed) với từng số tiến trình p, mỗi p lặp `repeats` lần và lấy lần
    nhanh nhất làm T_p (giảm nhiễu do máy bận). Thời gian là ga.runtime, gồm cả khởi động Pool.
    S_p = T_1 / T_p, E_p = S_p / p; Karp-Flatt e = (1/S_p - 1/p) / (1 - 1/p) ước lượng phần
    chạy tuần tự (chọn lọc, lai ghép, đột biến ở tiến trình chính, truyền dữ liệu, khởi động Pool).
    Cùng seed thì mọi p phải cho cùng lời giải: hàm kiểm tra luôn điều này.
    """
    if workers[0] != 1:
        raise ValueError("workers phải bắt đầu bằng 1 (T_1 là thời gian chạy tuần tự)")
    rows = []
    reference = None
    for p in workers:
        times = []
        for _ in range(repeats):
            ga = GeneticAlgorithm(
                pipeline.nodes, pipeline.dist_matrix, pipeline.num_drones,
                fitness_calc=pipeline.fitness_calc,
                energy_manager=pipeline.energy_manager if use_energy_manager else None,
                pop_size=pop_size, generations=generations, seed=seed, num_workers=p
            )
            ga.evolve()
            times.append(ga.runtime)
        if reference is None:
            reference = (ga.best_chromosome, ga.history)
        elif (ga.best_chromosome, ga.history) != reference:
            raise AssertionError(f"num_workers={p} cho kết quả khác chạy tuần tự")

        t_p = min(times)
        s_p = rows[0]["time_s"] / t_p if rows else 1.0
        rows.append({
            "workers": p, "time_s": t_p, "ms_per_gen": 1000 * t_p / generations,
            "speedup": s_p, "efficiency": s_p / p,
            "karp_flatt": (1 / s_p - 1 / p) / (1 - 1 / p) if p > 1 else None,
        })
        print(f"  xong p = {p}: {t_p:.2f} s", flush=True)
    return rows


def format_speedup(rows: List[Dict[str, Any]]) -> str:
    """Bảng Markdown T_p / S_p / E_p / Karp-Flatt."""
    lines = [
        "| Số tiến trình $p$ | $T_p$ (s) | ms / thế hệ | $S_p = T_1/T_p$ | $E_p = S_p/p$ | Karp-Flatt $e$ |",
        "| :---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        e = "—" if r["karp_flatt"] is None else f"{r['karp_flatt']:.3f}"
        lines.append(f"| {r['workers']} | {r['time_s']:.2f} | {r['ms_per_gen']:.1f} | {r['speedup']:.2f}x | "
                     f"{100 * r['efficiency']:.1f}% | {e} |")
    return "\n".join(lines)


def plot_speedup(csv_path: str, out_path: str) -> None:
    """
    Vẽ S_p theo số tiến trình từ CSV của lệnh `speedup`: 2 khung (không có / có EnergyManager),
    mỗi quy mô một đường, kèm đường lý tưởng S_p = p và mức tiêu chí 1.8x của nhóm.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    scales = sorted({int(r["n_delivery"]) for r in rows})
    workers = sorted({int(r["workers"]) for r in rows})
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # thứ tự cố định theo quy mô
    ink, muted, grid = "#0b0b0b", "#52514e", "#e4e3df"

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for ax, em in zip(axes, ("0", "1")):
        ax.plot(workers, workers, color=muted, lw=1.2, ls="--", zorder=1, label="Lý tưởng $S_p = p$")
        ax.hlines(1.8, 0.7, workers[-1], color=muted, lw=1, ls=":", zorder=1, label="Tiêu chí của nhóm (1.8x)")
        ends = []
        for n, color in zip(scales, colors):
            pts = sorted((int(r["workers"]), float(r["speedup"])) for r in rows
                         if r["energy_manager"] == em and int(r["n_delivery"]) == n)
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=color, lw=2, marker="o", ms=7, mec="white", mew=1.5, label=f"{n} điểm", zorder=3)
            ends.append([ys[-1], ys[-1], f"{n} điểm  {ys[-1]:.1f}x"])
        # Nhãn cuối đường: giãn theo chiều dọc để không chồng nhau (cách nhau >= 0.35 đơn vị trục tung)
        ends.sort()
        for prev, cur in zip(ends, ends[1:]):
            cur[1] = max(cur[1], prev[1] + 0.35)
        for y_true, y_text, text in ends:
            ax.annotate(text, (workers[-1], y_true), xytext=(workers[-1] + 0.25, y_text), va="center",
                        fontsize=9, color=ink)
        ax.set_title("Có EnergyManager" if em == "1" else "Không có EnergyManager", fontsize=11, color=ink, loc="left")
        ax.set_xticks(workers)
        ax.set_xlim(0.7, workers[-1] + 2.6)
        ax.set_xlabel("Số tiến trình $p$", color=muted)
        ax.grid(axis="y", color=grid, lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(grid)
        ax.tick_params(colors=muted)
    axes[0].set_ylabel("Tăng tốc $S_p = T_1 / T_p$", color=muted)
    axes[0].set_ylim(0, max(workers) + 0.5)
    axes[0].legend(loc="upper left", frameon=False, fontsize=9)
    fig.suptitle("Tăng tốc khi chấm fitness song song (GA 100 cá thể × 200 thế hệ)", fontsize=12, color=ink,
                 x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor="white")
    plt.close(fig)


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
    p_cmp.add_argument("--workers", type=int, default=None,
                       help="num_workers của GA (đánh giá fitness song song); bỏ trống = tuần tự")
    p_cmp.add_argument("--only-proposed", action="store_true",
                       help="Chỉ chạy Greedy và GA đề xuất (bỏ các dòng GA trung gian), dùng cho quy mô lớn")

    p_spd = sub.add_parser("speedup", help="Đo T_p, S_p, E_p khi đánh giá fitness song song")
    p_spd.add_argument("--scales", type=int, nargs="+", default=[10, 100, 500])
    p_spd.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4, 8], help="Phải bắt đầu bằng 1")
    p_spd.add_argument("--generations", type=int, default=200)
    p_spd.add_argument("--pop-size", type=int, default=100)
    p_spd.add_argument("--repeats", type=int, default=3, help="Số lần lặp mỗi cấu hình, lấy lần nhanh nhất")
    p_spd.add_argument("--energy", choices=["off", "on", "both"], default="both",
                       help="Chạy không có / có / cả hai trường hợp EnergyManager")
    p_spd.add_argument("--output", default=os.path.join(REPO_DIR, "data", "processed", "ga_speedup_results.csv"))

    p_plot = sub.add_parser("plot-speedup", help="Vẽ biểu đồ S_p từ CSV của lệnh speedup (không chạy lại GA)")
    p_plot.add_argument("--input", default=os.path.join(REPO_DIR, "data", "processed", "ga_speedup_results.csv"))
    p_plot.add_argument("--output", default=os.path.join(REPO_DIR, "docs", "figures", "ga_speedup.png"))
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
        if args.workers is not None:
            ga_params["num_workers"] = args.workers
        for n in args.scales:
            pipeline = load_benchmark(n)
            workers = f", GA tính fitness trên {args.workers} tiến trình" if args.workers else ""
            print(f"\n## Benchmark {n} điểm giao (K = {pipeline.num_drones} Drone, GA chạy {args.seeds} seed"
                  f"{workers})\n", flush=True)
            variants = compare(pipeline, list(range(args.seeds)), ga_params, full=not args.only_proposed)
            print(format_compare(variants), flush=True)
            print(format_convergence(list(variants.values())[-1]), flush=True)

    elif args.command == "speedup":
        energy_modes = {"off": [False], "on": [True], "both": [False, True]}[args.energy]
        fields = ["n_delivery", "num_drones", "chromosome_len", "energy_manager", "pop_size", "generations",
                  "workers", "time_s", "ms_per_gen", "speedup", "efficiency", "karp_flatt"]
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for n in args.scales:
                pipeline = load_benchmark(n)
                for use_em in energy_modes:
                    em = "có" if use_em else "không có"
                    print(f"\n## Benchmark {n} điểm giao (K = {pipeline.num_drones} Drone, {em} EnergyManager, "
                          f"{args.pop_size} cá thể x {args.generations} thế hệ, lấy lần nhanh nhất / "
                          f"{args.repeats} lần)\n", flush=True)
                    rows = speedup(pipeline, args.workers, args.generations, args.pop_size, args.repeats, use_em)
                    print("\n" + format_speedup(rows), flush=True)
                    for r in rows:
                        writer.writerow({
                            "n_delivery": n, "num_drones": pipeline.num_drones,
                            "chromosome_len": n + pipeline.num_drones - 1, "energy_manager": int(use_em),
                            "pop_size": args.pop_size, "generations": args.generations,
                            **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()},
                        })
                    f.flush()
        print(f"\nĐã ghi {args.output}", flush=True)

    elif args.command == "plot-speedup":
        plot_speedup(args.input, args.output)
        print(f"Đã lưu {args.output}", flush=True)


if __name__ == "__main__":
    main()
