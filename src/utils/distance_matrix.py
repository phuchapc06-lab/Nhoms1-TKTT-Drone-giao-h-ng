"""Tính trước ma trận khoảng cách né vùng cấm bay + cache ra file .pkl.
Hỗ trợ tính toán song song (Parallel Computing) qua ThreadPoolExecutor / ProcessPool.
Phụ trách: Thành viên 2 (A* Engine) & Thành viên 5 (Tích hợp & Song song hóa).
"""
import hashlib
import math
import os
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor
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


def _snap(pos):
    return (int(round(pos[0])), int(round(pos[1])))


def _fingerprint(nodes, no_fly_zones, grid_size):
    raw = repr(sorted((i, tuple(n["pos"])) for i, n in nodes.items()))
    raw += repr(list(no_fly_zones)) + repr(tuple(grid_size))
    return hashlib.md5(raw.encode()).hexdigest()


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
    key = _fingerprint(nodes, no_fly_zones, grid_size)

    if not force and cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        if data.get("key") == key:          # dữ liệu không đổi -> dùng lại
            return data["dist_matrix"], data["detailed_paths"]

    ids = sorted(nodes)
    n = len(ids)
    assert ids == list(range(n)), "id node phải liên tục từ 0 đến M-1"

    grid = build_grid(grid_size[0], grid_size[1], no_fly_zones)
    pts = [_snap(nodes[i]["pos"]) for i in ids]
    for i, p in enumerate(pts):
        if grid[p]:
            print(f"[CẢNH BÁO] node {i} tại {p} nằm trong vùng cấm bay -> khoảng cách = inf")

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
            dist[i, j] = dist[j, i] = d
            if p is not None:
                paths[(i, j)] = p
                paths[(j, i)] = p[::-1]

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
