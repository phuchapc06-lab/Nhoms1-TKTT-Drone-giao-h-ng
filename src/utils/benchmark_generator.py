"""
Module Sinh dữ liệu thử nghiệm đa quy mô (Benchmark Generator & Data Contract).
Phụ trách: Thành viên 4 (Benchmark Data & Scenarios).
Tích hợp: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
"""
import os
import sys
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Any

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class BenchmarkGenerator:
    """
    Trình sinh bộ dữ liệu benchmark chuẩn hóa theo chuẩn Data Contract của đề tài.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate(
        self,
        num_delivery: int = 10,
        num_charging: int = 3,
        num_no_fly: int = 5,
        grid_size: Tuple[int, int] = (60, 60)
    ) -> Dict[str, Any]:
        """
        Sinh tập dữ liệu benchmark chuẩn hóa theo Data Contract:
        - Depot tại trung tâm bản đồ (ID = 0)
        - Điểm giao hàng phân bố cụm ngẫu nhiên (ID = 1..N)
        - Tải trọng gói hàng cân đối theo quy mô đội bay
        - Khung giờ Time Windows hợp lý
        - Các vùng cấm bay No-fly zones
        """
        np.random.seed(self.seed + num_delivery)
        random.seed(self.seed + num_delivery)
        w, h = grid_size

        # 1. Depot (id = 0)
        depot_pos = (int(w // 2), int(h // 2))
        nodes: Dict[str, Any] = {
            "0": {
                "id": 0,
                "type": "depot",
                "pos": list(depot_pos),
                "demand": 0.0,
                "tw": [0.0, 1000.0],
                "service_time": 0.0
            }
        }

        # 2. Vùng cấm bay No-fly zones (x, y, w, h) - đảm bảo sinh đủ num_no_fly vùng không đè lên Depot
        no_fly_zones = []
        nfz_attempts = 0
        while len(no_fly_zones) < num_no_fly and nfz_attempts < num_no_fly * 300:
            nfz_attempts += 1
            zw = int(np.random.randint(5, 12))
            zh = int(np.random.randint(5, 12))
            zx = int(np.random.randint(2, max(3, w - zw - 2)))
            zy = int(np.random.randint(2, max(3, h - zh - 2)))
            # Tránh đè lên Depot
            if not (zx <= depot_pos[0] <= zx + zw and zy <= depot_pos[1] <= zy + zh):
                no_fly_zones.append([zx, zy, zw, zh])

        def in_nfz(px, py):
            for (zx, zy, zw, zh) in no_fly_zones:
                if zx <= px <= zx + zw and zy <= py <= zy + zh:
                    return True
            return False

        # 3. Điểm giao hàng (id = 1..N)
        curr_id = 1
        low_d = 0.8 if num_delivery <= 10 else 1.0
        high_d = 1.3 if num_delivery <= 10 else 1.5
        cust_attempts = 0
        while curr_id <= num_delivery and cust_attempts < num_delivery * 300:
            cust_attempts += 1
            px = int(np.random.randint(2, max(3, w - 2)))
            py = int(np.random.randint(2, max(3, h - 2)))
            if not in_nfz(px, py) and (px, py) != depot_pos:
                demand = round(float(np.random.uniform(low_d, high_d)), 1)
                start_tw = round(float(np.random.uniform(5.0, 50.0)), 1)
                end_tw = start_tw + round(float(np.random.uniform(30.0, 60.0)), 1)
                nodes[str(curr_id)] = {
                    "id": curr_id,
                    "type": "delivery",
                    "pos": [px, py],
                    "demand": demand,
                    "tw": [start_tw, end_tw],
                    "service_time": 5.0
                }
                curr_id += 1

        # 4. Trạm sạc (id = N+1..)
        cs_count = 0
        cs_attempts = 0
        while cs_count < num_charging and cs_attempts < num_charging * 300:
            cs_attempts += 1
            px = int(np.random.randint(5, max(6, w - 5)))
            py = int(np.random.randint(5, max(6, h - 5)))
            if not in_nfz(px, py) and (px, py) != depot_pos:
                nodes[str(curr_id)] = {
                    "id": curr_id,
                    "type": "charging",
                    "pos": [px, py],
                    "demand": 0.0,
                    "tw": [0.0, 1000.0],
                    "service_time": 15.0
                }
                curr_id += 1
                cs_count += 1

        return {
            "name": f"UDRP_Benchmark_{num_delivery}",
            "map_size": int(max(w, h)),
            "grid_size": list(grid_size),
            "num_customers": num_delivery,
            "num_charging": cs_count,
            "no_fly_zones": no_fly_zones,
            "nodes": nodes
        }

    def save_to_file(self, data: Dict[str, Any], filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[Generator] Đã tạo file benchmark: {filepath}")


def generate_benchmark(
    num_customers: int,
    num_charging: int,
    num_nofly: int,
    output_path: str,
    map_size: int = 100,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Hàm sinh dữ liệu tương thích giao diện module TV4.
    """
    gen = BenchmarkGenerator(seed=seed)
    data = gen.generate(
        num_delivery=num_customers,
        num_charging=num_charging,
        num_no_fly=num_nofly,
        grid_size=(map_size, map_size)
    )
    gen.save_to_file(data, output_path)
    return data


def load_benchmark(file_path: str) -> Dict[str, Any]:
    """
    Hàm nạp dữ liệu từ file JSON theo Data Contract (tương thích cả dict và list nodes).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Chuyển đổi nodes sang list có thứ tự theo id để hỗ trợ indexing nodes[0], nodes[1]
    raw_nodes = data.get("nodes", {})
    if isinstance(raw_nodes, dict):
        node_list = []
        for k in sorted(raw_nodes.keys(), key=lambda x: int(x)):
            node = dict(raw_nodes[k])
            node["pos"] = tuple(node.get("pos", (0, 0)))
            node["tw"] = tuple(node.get("tw", (0, 1000)))
            node_list.append(node)
        data["nodes"] = node_list
    elif isinstance(raw_nodes, list):
        for node in raw_nodes:
            node["pos"] = tuple(node.get("pos", (0, 0)))
            node["tw"] = tuple(node.get("tw", (0, 1000)))

    # Đảm bảo các thuộc tính đếm số lượng luôn chính xác
    data["num_customers"] = len([n for n in data["nodes"] if n.get("type") == "delivery"])
    data["num_charging"] = len([n for n in data["nodes"] if n.get("type") == "charging"])

    # Chuẩn hóa no_fly_zones
    zones = []
    for idx, z in enumerate(data.get("no_fly_zones", [])):
        if isinstance(z, dict) and "bounds" in z:
            b = tuple(z["bounds"])
            zones.append({"id": z.get("id", idx + 1), "bounds": b})
        elif isinstance(z, (list, tuple)) and len(z) >= 4:
            x, y, w, h = z[:4]
            zones.append({"id": idx + 1, "bounds": (x, y, x + w, y + h)})
    data["no_fly_zones"] = zones

    return data


if __name__ == "__main__":
    gen = BenchmarkGenerator(seed=100)
    configs = [
        (10, 3, 5, "data/raw/benchmark_10.json", (60, 60)),
        (50, 6, 12, "data/raw/benchmark_50.json", (100, 100)),
        (100, 10, 20, "data/raw/benchmark_100.json", (150, 150)),
        (500, 25, 10, "data/raw/benchmark_500.json", (250, 250)),
    ]
    for count, charging, nfz, out_path, grid in configs:
        b_data = gen.generate(num_delivery=count, num_charging=charging, num_no_fly=nfz, grid_size=grid)
        gen.save_to_file(b_data, out_path)
