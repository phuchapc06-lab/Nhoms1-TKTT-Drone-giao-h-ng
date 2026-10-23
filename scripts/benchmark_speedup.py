import csv
import json
import os
import statistics
import sys
import time

# Đưa src/ vào sys.path (giống cách repo import), đặt ở mức module
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from utils import distance_matrix as dm   # cùng kiểu import với các file trong src/

SIZES = [10, 50, 100, 500]
WORKERS = [1, 2, 4]


def repeats_for(n_delivery):
    return 1 if n_delivery >= 500 else 3     # 500 điểm chạy rất lâu


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    nodes = {int(k): v for k, v in data["nodes"].items()}   # key "0" -> 0
    return nodes, data["no_fly_zones"], tuple(data["grid_size"])


def run(n_delivery):
    path = os.path.join(ROOT, "data", "raw", f"benchmark_{n_delivery}.json")
    if not os.path.exists(path):
        print(f"[BỎ QUA] chưa có {path}")
        return []
    nodes, nfz, grid_size = load(path)
    rows, t1 = [], None
    for w in WORKERS:
        ts = []
        for _ in range(repeats_for(n_delivery)):
            s = time.perf_counter()
            dm.compute_distance_matrix(nodes, nfz, grid_size,
                                       cache_path=None, force=True, workers=w)
            ts.append(time.perf_counter() - s)
        tp = statistics.median(ts)
        if w == 1:
            t1 = tp
        st = dm.LAST_STATS
        row = (n_delivery, len(nodes), w, round(tp, 3), round(t1 / tp, 2),
               round(t1 / tp / w, 2), st["pairs"], st["astar_pairs"],
               round(100 * st["los_ratio"], 1))
        rows.append(row)
        print(row, flush=True)
    return rows


if __name__ == "__main__":
    out = []
    for n in SIZES:
        out += run(n)
    os.makedirs(os.path.join(ROOT, "data", "processed"), exist_ok=True)
    out_path = os.path.join(ROOT, "data", "processed", "speedup_results.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_delivery", "n_nodes", "workers", "time_s", "speedup",
                    "efficiency", "pairs", "astar_pairs", "los_pct"])
        w.writerows(out)
    print("Đã lưu", out_path)