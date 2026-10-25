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
            try:
                print(f"[Visualizer] Đã lưu đồ thị hội tụ vào: {save_path}")
            except UnicodeEncodeError:
                print(f"[Visualizer] Da luu do thi hoi tu vao: {save_path}")

        if show:
            plt.show()
        return fig, ax

    def plot_comparison_bar_charts(
        self,
        comparison_dict: Dict[str, Dict[str, float]],
        title: str = "So sánh Hiệu năng: A* + Greedy (Baseline) vs A* + GA (Đề xuất)",
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Vẽ biểu đồ cột nhóm (Grouped Bar Chart) so sánh 3 chỉ số chính:
        1. Tổng quãng đường (km)
        2. Tổng năng lượng tiêu thụ (Wh)
        3. Thời gian tính toán (giây)
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(title, fontsize=14, fontweight="bold", y=1.03)

        algos = list(comparison_dict.keys())
        colors = ["#7f7f7f", "#2ca02c"] if len(algos) == 2 else self.drone_colors[:len(algos)]

        # 1. Quãng đường
        distances = [comparison_dict[a].get("distance", 0.0) for a in algos]
        bars1 = axes[0].bar(algos, distances, color=colors, width=0.45, edgecolor="black")
        axes[0].set_title("Tổng quãng đường (km)", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Kilomet (km)")
        axes[0].grid(axis="y", linestyle="--", alpha=0.6)
        for bar in bars1:
            yval = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + (max(distances)*0.01), f"{yval:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=9)

        # 2. Năng lượng
        energies = [comparison_dict[a].get("energy", 0.0) for a in algos]
        bars2 = axes[1].bar(algos, energies, color=colors, width=0.45, edgecolor="black")
        axes[1].set_title("Năng lượng tiêu hao (Wh)", fontsize=11, fontweight="bold")
        axes[1].set_ylabel("Watt-giờ (Wh)")
        axes[1].grid(axis="y", linestyle="--", alpha=0.6)
        for bar in bars2:
            yval = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2.0, yval + (max(energies)*0.01), f"{yval:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=9)

        # 3. Thời gian tính toán
        times = [comparison_dict[a].get("exec_time_sec", 0.0) for a in algos]
        bars3 = axes[2].bar(algos, times, color=colors, width=0.45, edgecolor="black")
        axes[2].set_title("Thời gian tính toán (giây)", fontsize=11, fontweight="bold")
        axes[2].set_ylabel("Giây (s)")
        axes[2].grid(axis="y", linestyle="--", alpha=0.6)
        for bar in bars3:
            yval = bar.get_height()
            axes[2].text(bar.get_x() + bar.get_width()/2.0, yval + (max(times)*0.01), f"{yval:.3f}s", ha="center", va="bottom", fontweight="bold", fontsize=9)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            try:
                print(f"[Visualizer] Đã lưu biểu đồ so sánh cột vào: {save_path}")
            except UnicodeEncodeError:
                print(f"[Visualizer] Da luu bieu do so sanh cot vao: {save_path}")

        if show:
            plt.show()
        return fig, axes

    def plot_scalability_curve(
        self,
        scales: List[int],
        ga_metrics: Dict[str, List[float]],
        greedy_metrics: Dict[str, List[float]],
        title: str = "Khả năng Mở rộng (Scalability Analysis) theo Quy mô Điểm giao",
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Vẽ đồ thị đường thể hiện sự thay đổi về Quãng đường và Thời gian khi số lượng điểm tăng (10, 50, 100...).
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle(title, fontsize=13, fontweight="bold", y=1.02)

        # Trục 1: Quãng đường
        ax1.plot(scales, greedy_metrics.get("distance", []), marker="o", color="#7f7f7f", linewidth=2.0, label="A* + Greedy (Baseline)")
        ax1.plot(scales, ga_metrics.get("distance", []), marker="s", color="#2ca02c", linewidth=2.2, label="A* + GA (Đề xuất)")
        ax1.set_title("Quãng đường theo Quy mô (km)", fontweight="bold")
        ax1.set_xlabel("Số lượng điểm giao hàng (N)")
        ax1.set_ylabel("Tổng quãng đường (km)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()

        # Trục 2: Thời gian thực thi
        ax2.plot(scales, greedy_metrics.get("exec_time", []), marker="o", color="#7f7f7f", linewidth=2.0, label="A* + Greedy (Baseline)")
        ax2.plot(scales, ga_metrics.get("exec_time", []), marker="s", color="#2ca02c", linewidth=2.2, label="A* + GA (Đề xuất)")
        ax2.set_title("Thời gian tính toán theo Quy mô (s)", fontweight="bold")
        ax2.set_xlabel("Số lượng điểm giao hàng (N)")
        ax2.set_ylabel("Thời gian (giây)")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend()

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            try:
                print(f"[Visualizer] Đã lưu biểu đồ Scalability vào: {save_path}")
            except UnicodeEncodeError:
                print(f"[Visualizer] Da luu bieu do Scalability vao: {save_path}")

        if show:
            plt.show()
        return fig, (ax1, ax2)

    def plot_speedup_analysis(
        self,
        workers: List[int],
        speedups: List[float],
        times: Optional[List[float]] = None,
        title: str = "Đánh giá Tăng tốc Song song hóa A* (Parallel Speedup Analysis)",
        save_path: Optional[str] = None,
        show: bool = False
    ):
        """
        Vẽ đồ thị phân tích hệ số tăng tốc Sp = T1 / Tp so sánh với đường tăng tốc tuyến tính lý tưởng (Ideal Linear Speedup).
        """
        fig, axes = plt.subplots(1, 2 if times else 1, figsize=(12 if times else 7, 5))
        ax1 = axes[0] if times else axes

        # Trục 1: Hệ số tăng tốc (Speedup Sp)
        ax1.plot(workers, speedups, marker="o", color="#1f77b4", linewidth=2.2, label="Thực nghiệm (A* ThreadPool)")
        ax1.plot(workers, workers, linestyle="--", color="#d62728", alpha=0.7, label="Lý tưởng (Tuyến tính Sp = p)")
        ax1.set_title("Hệ số Tăng tốc (Speedup factor $S_p$)", fontweight="bold")
        ax1.set_xlabel("Số lượng Luồng / CPU Cores (p)")
        ax1.set_ylabel("Speedup ($S_p = T_1 / T_p$)")
        ax1.set_xticks(workers)
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()

        for x, y in zip(workers, speedups):
            ax1.annotate(f"{y:.2f}x", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontweight="bold")

        # Trục 2: Thời gian thực thi (nếu có dữ liệu times)
        if times:
            ax2 = axes[1]
            ax2.bar([str(w) for w in workers], times, color="#2ca02c", edgecolor="black", width=0.45)
            ax2.set_title("Thời gian tính toán A* (giây)", fontweight="bold")
            ax2.set_xlabel("Số lượng Luồng / CPU Cores (p)")
            ax2.set_ylabel("Thời gian (s)")
            ax2.grid(axis="y", linestyle="--", alpha=0.5)
            for idx, (w, t) in enumerate(zip(workers, times)):
                ax2.text(idx, t + max(times) * 0.02, f"{t:.4f}s", ha="center", fontweight="bold")

        fig.suptitle(title, fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            try:
                print(f"[Visualizer] Đã lưu biểu đồ Speedup vào: {save_path}")
            except UnicodeEncodeError:
                print(f"[Visualizer] Da luu bieu do Speedup vao: {save_path}")

        if show:
            plt.show()
        return fig, axes


    def plot_ontime_rate_comparison(
        self,
        scales: List[int],
        greedy_rates: List[float],
        ga_rates: List[float],
        title: str = "Đánh giá Tỷ lệ Giao hàng Đúng giờ (On-time Delivery Rate, %)",
        save_path: Optional[str] = None,
        show: bool = False
    ):
        """
        Vẽ biểu đồ đối sánh tỷ lệ giao hàng đúng giờ (%) giữa Greedy Baseline và GA Meta-heuristic
        trên chuỗi kịch bản đa quy mô có ràng buộc cửa sổ thời gian (Time Windows).
        """
        import numpy as np
        fig, ax = plt.subplots(figsize=(9, 5))

        x = np.arange(len(scales))
        width = 0.35

        bars1 = ax.bar(x - width/2, greedy_rates, width, label="Greedy Baseline (TV6)", color="#d62728", alpha=0.85, edgecolor="black")
        bars2 = ax.bar(x + width/2, ga_rates, width, label="A* + GA Đề xuất (Nhóm 1)", color="#2ca02c", alpha=0.85, edgecolor="black")

        ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Quy mô số lượng khách hàng (N điểm)", fontweight="bold")
        ax.set_ylabel("Tỷ lệ Giao đúng giờ (%)", fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([f"N={s}" for s in scales])
        ax.set_ylim(0, 115)
        ax.axhline(100, color="gray", linestyle=":", alpha=0.6, label="Mục tiêu tối đa (100%)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(loc="lower left", framealpha=0.9)

        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1a6e1a")

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            try:
                print(f"[Visualizer] Đã lưu biểu đồ On-time Rate vào: {save_path}")
            except UnicodeEncodeError:
                print(f"[Visualizer] Da luu bieu do On-time Rate vao: {save_path}")

        if show:
            plt.show()
        return fig, ax
