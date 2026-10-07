import heapq
import math

def heuristic(a, b):
    # Khoảng cách Euclidean làm hàm Heuristic cho A*
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def get_neighbors(node, grid_size):
    x, y = node
    # 8 hướng di chuyển (Lên, Xuống, Trái, Phải, và 4 đường chéo)
    neighbors = [
        (x+1, y), (x-1, y), (x, y+1), (x, y-1),
        (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)
    ]
    valid_neighbors = []
    for nx, ny in neighbors:
        # Kiểm tra xem tọa độ có nằm trong giới hạn bản đồ không
        if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
            valid_neighbors.append((nx, ny))
    return valid_neighbors

def astar(start, goal, grid_size, is_in_no_fly_zone_fn):
    """
    Thuật toán A-Star tìm đường đi ngắn nhất trên Grid 2D tránh vùng cấm bay.
    """
    # Nếu điểm bắt đầu hoặc kết thúc nằm trong vùng cấm bay
    if is_in_no_fly_zone_fn(start[0], start[1]) or is_in_no_fly_zone_fn(goal[0], goal[1]):
        return None
        
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        # Nếu đã đến đích
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        for neighbor in get_neighbors(current, grid_size):
            # Nếu lân cận là vùng cấm bay -> Bỏ qua
            if is_in_no_fly_zone_fn(neighbor[0], neighbor[1]):
                continue
                
            # Chi phí để di chuyển tới neighbor (1 cho thẳng, ~1.414 cho chéo)
            cost = heuristic(current, neighbor)
            tentative_g_score = g_score[current] + cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                
    return None # Không tìm được đường
