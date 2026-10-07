import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class UDRPDataGenerator:
    def __init__(self, grid_size=(100, 100), num_delivery=10, num_charging=3, num_no_fly=5, seed=None):
        self.grid_width, self.grid_height = grid_size
        self.num_delivery = num_delivery
        self.num_charging = num_charging
        self.num_no_fly = num_no_fly
        if seed is not None:
            np.random.seed(seed)
        
        self.depot = None
        self.delivery_points = []
        self.charging_stations = []
        self.no_fly_zones = [] # List of (x, y, width, height)
    
    def generate(self):
        # 1. Khởi tạo Trạm gốc (Depot)
        self.depot = (np.random.randint(5, self.grid_width-5), np.random.randint(5, self.grid_height-5))
        
        # 2. Khởi tạo Điểm giao hàng (Delivery Points)
        for _ in range(self.num_delivery):
            pt = (np.random.randint(0, self.grid_width), np.random.randint(0, self.grid_height))
            self.delivery_points.append(pt)
            
        # 3. Khởi tạo Trạm sạc pin (Charging Stations)
        for _ in range(self.num_charging):
            pt = (np.random.randint(0, self.grid_width), np.random.randint(0, self.grid_height))
            self.charging_stations.append(pt)
            
        # 4. Khởi tạo Vùng cấm bay (No-fly zones) dạng hình chữ nhật
        for _ in range(self.num_no_fly):
            w = np.random.randint(5, 15)
            h = np.random.randint(5, 15)
            x = np.random.randint(0, self.grid_width - w)
            y = np.random.randint(0, self.grid_height - h)
            self.no_fly_zones.append((x, y, w, h))
            
    def is_in_no_fly_zone(self, x, y):
        # Kiểm tra xem tọa độ (x, y) có nằm trong bất kỳ vùng cấm bay nào không
        for (zx, zy, zw, zh) in self.no_fly_zones:
            if zx <= x <= zx + zw and zy <= y <= zy + zh:
                return True
        return False

    def plot_map(self, show=True, title="UAV Routing Environment"):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, self.grid_width)
        ax.set_ylim(0, self.grid_height)
        
        # Vẽ các vùng cấm bay (No-fly zones)
        for (zx, zy, zw, zh) in self.no_fly_zones:
            rect = patches.Rectangle((zx, zy), zw, zh, linewidth=1, edgecolor='red', facecolor='red', alpha=0.3)
            ax.add_patch(rect)
            
        # Vẽ các điểm giao hàng
        if self.delivery_points:
            dx, dy = zip(*self.delivery_points)
            ax.scatter(dx, dy, c='blue', label='Điểm giao hàng', s=50)
            
        # Vẽ trạm sạc
        if self.charging_stations:
            cx, cy = zip(*self.charging_stations)
            ax.scatter(cx, cy, c='green', marker='^', label='Trạm sạc', s=100)
            
        # Vẽ Depot
        if self.depot:
            ax.scatter(self.depot[0], self.depot[1], c='black', marker='*', label='Trạm gốc (Depot)', s=200)
        
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_title(title)
        
        if show:
            plt.show()
        return fig, ax
