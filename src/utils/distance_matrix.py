<<<<<<< HEAD
"""Tính trước ma trận khoảng cách né vùng cấm bay + cache ra file .pkl."""
=======
"""Tính trước ma trận khoảng cách né vùng cấm bay + cache ra file .pkl.
Hỗ trợ tính toán song song (Parallel Computing) qua ThreadPoolExecutor / ProcessPool.
Phụ trách: Thành viên 2 (A* Engine) & Thành viên 5 (Tích hợp & Song song hóa).
"""
>>>>>>> develop
import hashlib
import math
import os
import pickle
<<<<<<< HEAD
from concurrent.futures import ProcessPoolExecutor
import numpy as np

=======
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

# Đảm bảo in tiếng Việt UTF-8 không lỗi trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

>>>>>>> develop
# Hỗ trợ cả 2 kiểu import (repo dùng sys.path trỏ vào src/)
try:
    from models.optimized_astar import build_grid, astar, line_of_sight
except ImportError:
    from src.models.optimized_astar import build_grid, astar, line_of_sight

# Đường dẫn cache tính từ vị trí file, không phụ thuộc thư mục đang đứng chạy lệnh
DEFAULT_CACHE = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "distance_matrix.pkl"))

<<<<<<< HEAD
# Thống kê của lần tính gần nhất (None nếu lần gọi cuối nạp từ cache):
# {"pairs", "los_pairs", "astar_pairs", "los_ratio", "workers"}
LAST_STATS = None

# Dữ liệu dùng chung trong mỗi tiến trình (nạp 1 lần qua initializer,
# tránh pickle grid cho từng tác vụ)
_G = {}

=======
>>>>>>> develop

def _snap(pos):
    return (int(round(pos[0])), int(round(pos[1])))


def _fingerprint(nodes, no_fly_zones, grid_size):
<<<<<<< HEAD
    # workers KHÔNG đưa vào key vì kết quả không phụ thuộc số nhân
=======
>>>>>>> develop
    raw = repr(sorted((i, tuple(n["pos"])) for i, n in nodes.items()))
    raw += repr(list(no_fly_zones)) + repr(tuple(grid_size))
    return hashlib.md5(raw.encode()).hexdigest()


<<<<<<< HEAD
def _init_worker(grid, pts):
    _G["grid"], _G["pts"] = grid, pts


def _solve_row(i):
    """Tính mọi cặp (i, j) với j > i. Hàm ở mức module để pickle được trên Windows/macOS."""
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


def compute_distance_matrix(nodes, no_fly_zones, grid_size,
                            cache_path=DEFAULT_CACHE, force=False, workers=1):
    """
    nodes: dict id -> node (đúng Data Contract), id phải liên tục 0..M-1
    grid_size: (width, height)
    workers: số tiến trình (1 = tuần tự). Dùng >1 thì script gọi phải bọc
             trong `if __name__ == "__main__":`.
    Trả về (dist_matrix: np.ndarray MxM, detailed_paths: {(i, j): [(x, y), ...]})
    Cặp không tới được: dist = inf, không có trong detailed_paths.
    """
    global LAST_STATS
=======
def compute_distance_matrix(
    nodes: Dict[int, Dict[str, Any]],
    no_fly_zones: List[Tuple[int, int, int, int]],
    grid_size: Tuple[int, int],
    cache_path: Optional[str] = DEFAULT_CACHE,
    force: bool = False,
    parallel: bool = False,
    num_workers: Optional[int] = None
) -> Tuple[np.ndarray, Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    """
    nodes: dict id -> node (đúng Data Contract), id phải liên tục 0..M-1
    grid_size: (width, height)
    parallel: True để bật tính song song đa luồng cho các cặp điểm (i, j)
    num_workers: số worker luồng xử lý song song (mặc định: min(cpu_count, 8))
    Trả về (dist_matrix: np.ndarray MxM, detailed_paths: {(i, j): [(x, y), ...]})
    Cặp không tới được: dist = inf, không có trong detailed_paths.
    """
>>>>>>> develop
    key = _fingerprint(nodes, no_fly_zones, grid_size)

    if not force and cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        if data.get("key") == key:          # dữ liệu không đổi -> dùng lại
<<<<<<< HEAD
            LAST_STATS = None
=======
>>>>>>> develop
            return data["dist_matrix"], data["detailed_paths"]

    ids = sorted(nodes)
    n = len(ids)
    assert ids == list(range(n)), "id node phải liên tục từ 0 đến M-1"

    grid = build_grid(grid_size[0], grid_size[1], no_fly_zones)
    pts = [_snap(nodes[i]["pos"]) for i in ids]
    for i, p in enumerate(pts):
        if grid[p]:
            print(f"[CẢNH BÁO] node {i} tại {p} nằm trong vùng cấm bay -> khoảng cách = inf")

<<<<<<< HEAD
    # ---- Tính các hàng (tuần tự hoặc song song) ----
    if workers <= 1 or n < 3:
        _init_worker(grid, pts)
        results = [_solve_row(i) for i in range(n)]
    else:
        # chunksize=1: hàng i nhỏ có nhiều cặp hơn -> chia nhỏ để cân tải
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_init_worker,
                                 initargs=(grid, pts)) as ex:
            results = list(ex.map(_solve_row, range(n), chunksize=1))

    # ---- Gộp kết quả ----
    dist = np.zeros((n, n))
    paths = {}
    total_los = total_astar = 0
    for i, row, n_los, n_astar in results:
        total_los += n_los
        total_astar += n_astar
        for j, d, p in row:
=======
    dist = np.zeros((n, n))
    paths: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    def _eval_pair(pair: Tuple[int, int]):
        i, j = pair
        pi, pj = pts[i], pts[j]
        if line_of_sight(grid, pi, pj):
            return i, j, math.dist(pi, pj), [pi, pj]
        else:
            d, p = astar(grid, pi, pj)
            return i, j, d, p

    if parallel and len(pairs) > 1:
        workers = num_workers if num_workers and num_workers > 0 else min(os.cpu_count() or 4, 8)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = executor.map(_eval_pair, pairs)
            for i, j, d, p in results:
                dist[i, j] = dist[j, i] = d
                if p is not None:
                    paths[(i, j)] = p
                    paths[(j, i)] = p[::-1]
    else:
        for pair in pairs:
            i, j, d, p = _eval_pair(pair)
>>>>>>> develop
            dist[i, j] = dist[j, i] = d
            if p is not None:
                paths[(i, j)] = p
                paths[(j, i)] = p[::-1]

<<<<<<< HEAD
    pairs = total_los + total_astar
    LAST_STATS = {
        "pairs": pairs,
        "los_pairs": total_los,
        "astar_pairs": total_astar,
        "los_ratio": (total_los / pairs) if pairs else 1.0,
        "workers": workers,
    }

=======
>>>>>>> develop
    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump({"key": key, "dist_matrix": dist, "detailed_paths": paths}, f)
    return dist, paths

<<<<<<< HEAD
#Use
"""
from src.utils import distance_matrix as dm

D, P = dm.compute_distance_matrix(nodes, nfz, grid_size, workers=4)
print(dm.LAST_STATS)   # lấy tỷ lệ LOS cho bảng thực nghiệm
"""
=======

def benchmark_distance_matrix_speedup(
    nodes: Dict[int, Dict[str, Any]],
    no_fly_zones: List[Tuple[int, int, int, int]],
    grid_size: Tuple[int, int],
    workers_list: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Đo đạc thời gian tính toán và hệ số tăng tốc (Speedup Sp = T1 / Tp) khi song song hóa A*.
    """
    if workers_list is None:
        workers_list = [1, 2, 4]

    results: Dict[str, Any] = {}
    times: Dict[int, float] = {}

    for w in workers_list:
        t0 = time.perf_counter()
        if w == 1:
            compute_distance_matrix(nodes, no_fly_zones, grid_size, cache_path=None, force=True, parallel=False)
        else:
            compute_distance_matrix(nodes, no_fly_zones, grid_size, cache_path=None, force=True, parallel=True, num_workers=w)
        times[w] = time.perf_counter() - t0

    t1 = times.get(1, 1e-6)
    speedups = {w: round(t1 / times[w], 2) for w in workers_list}

    results["times_sec"] = {f"{w}_workers": round(times[w], 4) for w in workers_list}
    results["speedup"] = {f"S_{w}": speedups[w] for w in workers_list}
    return results
>>>>>>> develop
