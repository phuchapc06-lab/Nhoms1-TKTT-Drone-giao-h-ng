"""Tính trước ma trận khoảng cách né vùng cấm bay + cache ra file .pkl."""
import hashlib
import math
import os
import pickle
import numpy as np

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


def compute_distance_matrix(nodes, no_fly_zones, grid_size,
                            cache_path=DEFAULT_CACHE, force=False):
    """
    nodes: dict id -> node (đúng Data Contract), id phải liên tục 0..M-1
    grid_size: (width, height)
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
    paths = {}
    for i in range(n):
        for j in range(i + 1, n):
            if line_of_sight(grid, pts[i], pts[j]):      # đường thẳng thông -> khỏi chạy A*
                d, p = math.dist(pts[i], pts[j]), [pts[i], pts[j]]
            else:
                d, p = astar(grid, pts[i], pts[j])
            dist[i, j] = dist[j, i] = d
            if p is not None:
                paths[(i, j)] = p
                paths[(j, i)] = p[::-1]

    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump({"key": key, "dist_matrix": dist, "detailed_paths": paths}, f)
    return dist, paths