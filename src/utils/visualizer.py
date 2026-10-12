"""
Module trực quan hóa kết quả định tuyến đa UAV và đường cong tiến hóa GA.
Phụ trách: Thành viên 5 (Nhóm trưởng / Tech Lead & Integrator).
"""
from typing import List, Dict, Tuple, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class UAVVisualizer:
    def __init__(self, grid_size: Tuple[int, int] = (100, 100)):
        self.grid_width, self.grid_height = grid_size
        # Bảng màu phong phú để phân biệt nhiều Drone
        self.drone_colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", 
            "#bcbd22", "#17becf"
        ]

    def plot_multi_uav_routes(
        self,
        nodes: Dict[int, Dict[str, Any]],
        no_fly_zones: List[Tuple[int, int, int, int]],
        solution: List[List[int]],
        detailed_paths: Optional[Dict[Tuple[int, int], List[Tuple[int, int]]]] = None,
        title: str = "Tối ưu hóa Tuyến bay Đa UAV (Multi-UAV Routing)",
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Vẽ toàn bộ bản đồ không gian, bao gồm:
        - Vùng cấm bay (No-fly zones) màu đỏ mờ.
        - Trạm gốc (Depot) màu vàng viền đen.
        - Các điểm giao hàng màu xanh dương kèm ID.
        - Trạm sạc màu xanh lá kèm ID.
        - Tuyến bay của từng UAV được vẽ bằng màu sắc riêng biệt.
        """
        fig, ax = plt.subplots(figsize=(11, 10))
        ax.set_xlim(0, self.grid_width)
        ax.set_ylim(0, self.grid_height)
        ax.set_xlabel("Tọa độ X (Grid unit)", fontsize=11)
        ax.set_ylabel("Tọa độ Y (Grid unit)", fontsize=11)
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

        # 1. Vẽ các vùng cấm bay (No-Fly Zones)
        for idx, (zx, zy, zw, zh) in enumerate(no_fly_zones):
            label = "Vùng cấm bay (NFZ)" if idx == 0 else ""
            rect = patches.Rectangle(
                (zx, zy), zw, zh,
                linewidth=1.5, edgecolor="#d62728", facecolor="#ff9999", alpha=0.45,
                hatch="//", label=label
            )
            ax.add_patch(rect)

        # 2. Vẽ các điểm (Nodes)
        for nid, data in nodes.items():
            pos = data["pos"]
            node_type = data.get("type", "delivery")

            if node_type == "depot":
                ax.scatter(pos[0], pos[1], c="gold", edgecolors="black", s=250, marker="*", zorder=6, label="Trạm gốc (Depot)")
                ax.text(pos[0], pos[1] + 1.5, f"Depot (0)", fontsize=10, fontweight="bold", ha="center", zorder=7)
            elif node_type == "charging":
                first_charge_id = min([k for k, v in nodes.items() if v.get("type") == "charging"], default=-1)
                label = "Trạm sạc pin" if nid == first_charge_id else ""
                ax.scatter(pos[0], pos[1], c="#2ca02c", edgecolors="darkgreen", s=130, marker="^", zorder=5, label=label)
                ax.text(pos[0], pos[1] + 1.2, f"CS_{nid}", fontsize=8, color="darkgreen", ha="center", zorder=7)
            else:
                label = "Điểm giao hàng" if nid == 1 else ""
                ax.scatter(pos[0], pos[1], c="#1f77b4", edgecolors="navy", s=70, marker="o", zorder=4, label=label)
                ax.text(pos[0], pos[1] + 1.0, f"{nid}", fontsize=8, color="navy", ha="center", zorder=7)

        # 3. Vẽ đường đi của từng Drone
        for drone_idx, route in enumerate(solution):
            if not route or len(route) <= 1:
                continue

            color = self.drone_colors[drone_idx % len(self.drone_colors)]
            num_delivered = len([x for x in route if nodes.get(x, {}).get("type") == "delivery"])
            route_label = f"UAV #{drone_idx + 1} ({num_delivered} đơn)"

            route_x = []
            route_y = []

            for i in range(len(route) - 1):
                u = route[i]
                v = route[i + 1]

                # Nếu có chi tiết đường bay né vật cản từ A*
                if detailed_paths and (u, v) in detailed_paths:
                    sub_path = detailed_paths[(u, v)]
                    px = [p[0] for p in sub_path]
                    py = [p[1] for p in sub_path]
                else:
                    pu = nodes[u]["pos"]
                    pv = nodes[v]["pos"]
                    px = [pu[0], pv[0]]
                    py = [pu[1], pv[1]]

                route_x.extend(px)
                route_y.extend(py)

            # Vẽ đường bay
            ax.plot(route_x, route_y, color=color, linewidth=2.2, alpha=0.85, linestyle="-", label=route_label, zorder=3)

            # Vẽ mũi tên chỉ hướng ở giữa mỗi chặng
            for i in range(len(route) - 1):
                u, v = route[i], route[i+1]
                pu = nodes[u]["pos"]
                pv = nodes[v]["pos"]
                mid_x = (pu[0] + pv[0]) / 2
                mid_y = (pu[1] + pv[1]) / 2
                dx = (pv[0] - pu[0]) * 0.05
                dy = (pv[1] - pu[1]) * 0.05
                ax.annotate(
                    "", xy=(mid_x + dx, mid_y + dy), xytext=(mid_x - dx, mid_y - dy),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5), zorder=3
                )

        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"[Visualizer] Đã lưu bản đồ vào: {save_path}")

        if show:
            plt.show()
        return fig, ax

    def plot_convergence_curve(
        self,
        history_fitness: List[float],
        title: str = "Đường cong Hội tụ Giải thuật Di truyền (GA Convergence)",
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Vẽ đồ thị biểu diễn điểm thích nghi tốt nhất (Best Fitness) qua các thế hệ.
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        generations = list(range(1, len(history_fitness) + 1))

        ax.plot(generations, history_fitness, color="#d62728", linewidth=2.2, label="Best Fitness")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Thế hệ (Generations)", fontsize=11)
        ax.set_ylabel("Độ thích nghi (Fitness Score)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="lower right", fontsize=10)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"[Visualizer] Đã lưu đồ thị hội tụ vào: {save_path}")

        if show:
            plt.show()
        return fig, ax
