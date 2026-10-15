"""A* tối ưu (heapq, 8 hướng, octile) + làm mịn đường bay (line-of-sight)."""
import heapq
import math
import numpy as np

SQRT2 = math.sqrt(2)
NEIGHBORS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, SQRT2), (1, -1, SQRT2), (-1, 1, SQRT2), (-1, -1, SQRT2)]


def build_grid(width, height, no_fly_zones):
    """grid[x, y] = True nếu ô bị vùng cấm bay chiếm (biên tính bao gồm)."""
    grid = np.zeros((width + 1, height + 1), dtype=bool)
    for (x, y, w, h) in no_fly_zones:
        x0, y0 = max(int(math.floor(x)), 0), max(int(math.floor(y)), 0)
        x1, y1 = min(int(math.ceil(x + w)), width), min(int(math.ceil(y + h)), height)
        grid[x0:x1 + 1, y0:y1 + 1] = True
    return grid


def octile(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dx + dy) + (SQRT2 - 2) * min(dx, dy)


def line_of_sight(grid, a, b):
    """True nếu đoạn thẳng a->b không đi qua ô bị chặn (Bresenham)."""
    x0, y0 = a
    x1, y1 = b
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if grid[x, y]:
            return False
        if (x, y) == (x1, y1):
            return True
        e2 = 2 * err
        nx, ny = x, y
        if e2 > -dy:
            err -= dy
            nx += sx
        if e2 < dx:
            err += dx
            ny += sy
        # đi chéo: không cho lách qua khe giữa 2 ô bị chặn
        if nx != x and ny != y and (grid[nx, y] or grid[x, ny]):
            return False
        x, y = nx, ny


def smooth_path(grid, path):
    """Nhảy tới điểm xa nhất còn nhìn thẳng được -> đường ít góc gãy."""
    if len(path) <= 2:
        return path
    out, i = [path[0]], 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not line_of_sight(grid, path[i], path[j]):
            j -= 1
        out.append(path[j])
        i = j
    return out


def path_length(path):
    return sum(math.dist(path[k], path[k + 1]) for k in range(len(path) - 1))


def astar(grid, start, goal, smooth=True):
    """Trả về (khoảng_cách, đường_đi). Không tới được -> (inf, None)."""
    W, H = grid.shape
    if grid[start] or grid[goal]:
        return math.inf, None
    if start == goal:
        return 0.0, [start]

    open_heap = [(octile(start, goal), 0.0, start)]
    g = {start: 0.0}
    parent = {}
    closed = set()

    while open_heap:
        _, gc, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        if cur == goal:
            path = [cur]
            while cur in parent:
                cur = parent[cur]
                path.append(cur)
            path.reverse()
            if smooth:
                path = smooth_path(grid, path)
            return path_length(path), path
        closed.add(cur)

        x, y = cur
        for dx, dy, cost in NEIGHBORS:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < H) or grid[nx, ny]:
                continue
            if dx and dy and (grid[x + dx, y] or grid[x, y + dy]):
                continue  # cấm cắt góc vật cản
            ng = gc + cost
            nb = (nx, ny)
            if ng < g.get(nb, math.inf):
                g[nb] = ng
                parent[nb] = cur
                heapq.heappush(open_heap, (ng + octile(nb, goal), ng, nb))
    return math.inf, None