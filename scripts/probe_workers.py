import json, os, statistics, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from utils import distance_matrix as dm

def load(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return {int(k): v for k, v in d["nodes"].items()}, d["no_fly_zones"], tuple(d["grid_size"])

if __name__ == "__main__":
    nodes, nfz, gs = load(os.path.join(ROOT, "data", "raw", "benchmark_100.json"))
    for w in [1, 2, 3, 4, 6, 8]:
        ts = []
        for _ in range(5):
            s = time.perf_counter()
            dm.compute_distance_matrix(nodes, nfz, gs, cache_path=None, force=True, workers=w)
            ts.append(time.perf_counter() - s)
        print(w, "median", round(statistics.median(ts), 2),
              "min", round(min(ts), 2), "max", round(max(ts), 2), flush=True)