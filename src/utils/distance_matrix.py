"""Tính trước ma trận khoảng cách né vùng cấm bay + cache ra file .pkl.
Song song hóa bằng ProcessPoolExecutor (A* là CPU-bound nên thread bị GIL chặn).
Phụ trách: Thành viên 2 (A* Engine) & Thành viên 5 (Tích hợp).
"""
import hashlib
import math
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

# Đảm bảo in tiếng Việt UTF-8 không lỗi trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Hỗ trợ cả 2 kiểu import (repo dùng sys.path trỏ vào src/)
try:
    from models.optimized_astar import build_grid, astar, line_of_sight
except ImportError:
    from src.models.optimized_astar import build_grid, astar, line_of_sight

# Đường dẫn cache tính từ vị trí file, không phụ thuộc thư mục đang đứng chạy lệnh
DEFAULT_CACHE = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "distance_matrix.pkl"))

# Thống kê lần tính gần nhất (None nếu lần gọi cuối nạp từ cache):
# {"pairs", "los_pairs", "astar_pairs", "los_ratio", "workers", "elapsed_s"}
LAST_STATS = None

# Dữ liệu dùng chung trong mỗi tiến trình (nạp 1 lần qua initializer)
_G = {}


def _snap(pos):
    return (int(round(pos[0])), int(round(pos[1])))


def _fingerprint(nodes, no_fly_zones, grid_size):
    # số workers KHÔNG đưa vào key vì kết quả không phụ thuộc số nhân
    raw = repr(sorted((i, tuple(n["pos"])) for i, n in nodes.items()))
    raw += repr([tuple(z) for z in no_fly_zones]) + repr(tuple(grid_size))
    return hashlib.md5(raw.encode()).hexdigest()


def _init_worker(grid, pts):
    _G["grid"], _G["pts"] = grid, pts


def _solve_row(i):
    """Tính mọi cặp (i, j) với j > i. Ở mức module để pickle được trên Windows."""
    grid, pts = _G["grid"], _G["pts"]
    out = []
    n_los = n_astar = 0
    for j in range(i + 1, len(pts)):
        if line_of_sight(grid, pts[i], pts[j]):      # đường thẳng thông -> khỏi chạy A*
            d, p = math.dist(pts[i], pts[j]), [pts[i], pts[j]]
            n_los += 1
        else:
            d, p = astar(grid, pts[i], pts[j])
            n_astar += 1
        out.append((j, d, p))
    return i, out, n_los, n_astar


def _run_sequential(grid, pts):
    _init_worker(grid, pts)
    return [_solve_row(i) for i in range(len(pts))]


def compute_distance_matrix(
    nodes: Dict[int, Dict[str, Any]],
    no_fly_zones: List[Tuple[int, int, int, int]],
    grid_size: Tuple[int, int],
    cache_path: Optional[str] = DEFAULT_CACHE,
    force: bool = False,
    parallel: bool = False,
    num_workers: Optional[int] = None,
    workers: Optional[int] = None,
) -> Tuple[np.ndarray, Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    """
    nodes: dict id -> node (đúng Data Contract), id phải liên tục 0..M-1
           (key dạng chuỗi "0","1",... từ file JSON sẽ tự được đổi sang int)
    grid_size: (width, height)
    Số tiến trình (chọn 1 trong 2 cách, `workers` được ưu tiên):
      - workers=k: dùng k tiến trình (1 = tuần tự)
      - parallel=True [, num_workers=k]: tương thích với main.py/pipeline.py của TV5;
        mặc định k = min(cpu_count, 8)
    Dùng >1 tiến trình thì script gọi nên bọc trong `if __name__ == "__main__":`.
    Nếu không sinh được tiến trình con, hàm tự chạy tuần tự (kết quả không đổi).
    Trả về (dist_matrix: np.ndarray MxM, detailed_paths: {(i, j): [(x, y), ...]})
    Cặp không tới được: dist = inf, không có trong detailed_paths.
    """
    global LAST_STATS
    t_start = time.perf_counter()

    if workers is None:
        if parallel:
            workers = num_workers if num_workers and num_workers > 0 \
                else min(os.cpu_count() or 4, 8)
        else:
            workers = 1

    nodes = {int(k): v for k, v in nodes.items()}     # chuẩn hóa key về int
    key = _fingerprint(nodes, no_fly_zones, grid_size)

    if not force and cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        if data.get("key") == key:          # dữ liệu không đổi -> dùng lại
            LAST_STATS = None
            return data["dist_matrix"], data["detailed_paths"]

    ids = sorted(nodes)
    n = len(ids)
    assert ids == list(range(n)), "id node phải liên tục từ 0 đến M-1"

    grid = build_grid(grid_size[0], grid_size[1], no_fly_zones)
    pts = [_snap(nodes[i]["pos"]) for i in ids]
    for i, p in enumerate(pts):
        if grid[p]:
            print(f"[CẢNH BÁO] node {i} tại {p} nằm trong vùng cấm bay -> khoảng cách = inf")

    # ---- Tính các hàng (tuần tự hoặc song song theo tiến trình) ----
    workers = max(1, min(workers, n))
    if workers <= 1 or n < 3:
        workers = 1
        results = _run_sequential(grid, pts)
    else:
        try:
            # chunksize=1: hàng i nhỏ có nhiều cặp hơn -> chia nhỏ để cân tải
            with ProcessPoolExecutor(max_workers=workers,
                                     initializer=_init_worker,
                                     initargs=(grid, pts)) as ex:
                results = list(ex.map(_solve_row, range(n), chunksize=1))
        except (BrokenProcessPool, OSError, RuntimeError) as e:
            print(f"[CẢNH BÁO] Không chạy được đa tiến trình ({type(e).__name__}). "
                  f"Chuyển sang chạy tuần tự. Hãy bọc lệnh gọi trong "
                  f"`if __name__ == \"__main__\":`.")
            workers = 1
            results = _run_sequential(grid, pts)

    # ---- Gộp kết quả ----
    dist = np.zeros((n, n))
    paths: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    total_los = total_astar = 0
    for i, row, n_los, n_astar in results:
        total_los += n_los
        total_astar += n_astar
        for j, d, p in row:
            dist[i, j] = dist[j, i] = d
            if p is not None:
                paths[(i, j)] = p
                paths[(j, i)] = p[::-1]

    n_pairs = total_los + total_astar
    LAST_STATS = {
        "pairs": n_pairs,
        "los_pairs": total_los,
        "astar_pairs": total_astar,
        "los_ratio": (total_los / n_pairs) if n_pairs else 1.0,
        "workers": workers,
        "elapsed_s": time.perf_counter() - t_start,
    }

    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump({"key": key, "dist_matrix": dist, "detailed_paths": paths}, f)
    return dist, paths


def benchmark_distance_matrix_speedup(
    nodes: Dict[int, Dict[str, Any]],
    no_fly_zones: List[Tuple[int, int, int, int]],
    grid_size: Tuple[int, int],
    workers_list: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Đo thời gian và hệ số tăng tốc (Speedup Sp = T1 / Tp) khi song song hóa A*.
    (Giữ nguyên giao diện do TV5 đã tích hợp.)
    """
    if workers_list is None:
        workers_list = [1, 2, 4]

    results: Dict[str, Any] = {}
    times: Dict[int, float] = {}

    for w in workers_list:
        t0 = time.perf_counter()
        compute_distance_matrix(nodes, no_fly_zones, grid_size,
                                cache_path=None, force=True, workers=w)
        times[w] = time.perf_counter() - t0

    t1 = times.get(1, 1e-6)
    speedups = {w: round(t1 / times[w], 2) for w in workers_list}

    results["times_sec"] = {f"{w}_workers": round(times[w], 4) for w in workers_list}
    results["speedup"] = {f"S_{w}": speedups[w] for w in workers_list}
    return results