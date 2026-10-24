import json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from utils import distance_matrix as dm

if __name__ == "__main__":
    with open(os.path.join(ROOT, "data", "raw", "benchmark_500.json"), encoding="utf-8") as f:
        d = json.load(f)
    nodes = {int(k): v for k, v in d["nodes"].items()}
    s = time.perf_counter()
    dm.compute_distance_matrix(nodes, d["no_fly_zones"], tuple(d["grid_size"]),
                               cache_path=None, force=True, workers=2)
    print("n_nodes", len(nodes), "grid", d["grid_size"],
          "time_s", round(time.perf_counter() - s, 1), dm.LAST_STATS, flush=True)