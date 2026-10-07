from utils.data_generator import UDRPDataGenerator
from models.baseline_astar import astar
import matplotlib.pyplot as plt

def main():
    print("=== Khởi tạo Môi trường Drone Delivery ===")
    
    # 1. Sinh bản đồ và dữ liệu
    # Sử dụng seed để kết quả map luôn cố định trong mỗi lần test (có thể đổi seed khác)
    env = UDRPDataGenerator(grid_size=(60, 60), num_delivery=8, num_charging=3, num_no_fly=6, seed=42)
    env.generate()
    print(f"Đã tạo bản đồ kích thước {env.grid_width}x{env.grid_height} với:")
    print(f"- Depot: {env.depot}")
    print(f"- {len(env.delivery_points)} Điểm giao hàng")
    print(f"- {len(env.charging_stations)} Trạm sạc")
    print(f"- {len(env.no_fly_zones)} Vùng cấm bay")
    
    # 2. Tìm đường bằng A* Baseline
    start = env.depot
    # Tìm đường từ Depot đến điểm giao hàng đầu tiên
    goal = env.delivery_points[0] 
    
    print(f"\n[A* Baseline] Đang tìm đường từ {start} -> {goal}...")
    path = astar(start, goal, (env.grid_width, env.grid_height), env.is_in_no_fly_zone)
    
    # 3. Vẽ biểu đồ hiển thị kết quả
    fig, ax = env.plot_map(show=False, title=f"A* Pathfinding: Depot {start} -> Delivery Point {goal}")
    
    if path:
        print(f"✅ Đã tìm thấy đường đi! Chiều dài: {len(path)} bước.")
        px, py = zip(*path)
        # Vẽ đường đi màu tím đứt nét
        ax.plot(px, py, color='purple', linewidth=2.5, label='A* Path', linestyle='--')
        ax.legend()
    else:
        print("❌ Không tìm thấy đường đi (Điểm giao hàng có thể bị chặn bởi vùng cấm bay).")
        
    print("Đang hiển thị biểu đồ...")
    plt.show()

if __name__ == "__main__":
    main()
