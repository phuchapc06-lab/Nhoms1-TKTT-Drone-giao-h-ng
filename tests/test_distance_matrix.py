"""Unit test cho Thanh vien 2: A* toi uu va ma tran khoang cach."""
import sys
import os
import math
import time
import numpy as np

# Them duong dan src vao he thong (giong test_member5.py)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from models.optimized_astar import build_grid, astar
from utils.distance_matrix import compute_distance_matrix


def make_nodes(points):
    return {i: {"id": i, "type": "depot" if i == 0 else "delivery", "pos": p,
                "demand": 0.0, "tw": (0, 100), "service_time": 0}
            for i, p in enumerate(points)}


def test_straight_line_without_obstacle():
    grid = build_grid(50, 50, [])
    d, path = astar(grid, (0, 0), (30, 40))
    assert abs(d - 50.0) < 1e-6          # smoothing -> duong thang dung bang Euclid


def test_detour_around_nfz_is_longer():
    grid = build_grid(50, 50, [(20, 0, 10, 40)])   # buc tuong chan
    d, path = astar(grid, (10, 20), (40, 20))
    assert d > 30 and math.isfinite(d)


def test_boundary_is_inclusive():
    grid = build_grid(50, 50, [(10, 10, 5, 5)])
    assert grid[10, 10] and grid[15, 15] and not grid[16, 16]


def test_unreachable_returns_inf():
    grid = build_grid(50, 50, [(0, 25, 50, 2)])     # tuong kin ngang ban do
    d, path = astar(grid, (5, 5), (5, 45))
    assert d == math.inf and path is None


def test_matrix_properties(tmp_path):
    nodes = make_nodes([(5, 5), (40, 5), (40, 40), (5, 40)])
    D, paths = compute_distance_matrix(nodes, [(15, 15, 10, 10)], (50, 50),
                                       cache_path=str(tmp_path / "m.pkl"))
    assert D.shape == (4, 4)
    assert np.allclose(np.diag(D), 0)
    assert np.allclose(D, D.T)
    assert (0, 2) in paths and paths[(0, 2)][0] == (5, 5)


def test_cache_is_reused(tmp_path):
    nodes = make_nodes([(5, 5), (40, 5), (40, 40)])
    cp = str(tmp_path / "m.pkl")
    D1, _ = compute_distance_matrix(nodes, [], (50, 50), cache_path=cp)
    t = time.time()
    D2, _ = compute_distance_matrix(nodes, [], (50, 50), cache_path=cp)
    assert time.time() - t < 0.5 and np.allclose(D1, D2)


if __name__ == "__main__":
    from pathlib import Path
    import tempfile

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== KIỂM THỬ ĐỘC LẬP MODULE THÀNH VIÊN 2 (A* TỐI ƯU & MA TRẬN) ===")
    test_straight_line_without_obstacle()
    print("-> test_straight_line_without_obstacle: PASSED")
    test_detour_around_nfz_is_longer()
    print("-> test_detour_around_nfz_is_longer: PASSED")
    test_boundary_is_inclusive()
    print("-> test_boundary_is_inclusive: PASSED")
    test_unreachable_returns_inf()
    print("-> test_unreachable_returns_inf: PASSED")
    with tempfile.TemporaryDirectory() as td:
        tpath = Path(td)
        test_matrix_properties(tpath)
        print("-> test_matrix_properties: PASSED")
        test_cache_is_reused(tpath)
        print("-> test_cache_is_reused: PASSED")
    print("\n=== TẤT CẢ UNIT TEST CHO THÀNH VIÊN 2 ĐÃ VƯỢT QUA XUẤT SẮC! ===")