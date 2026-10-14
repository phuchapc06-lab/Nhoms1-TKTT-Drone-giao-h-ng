import os
import sys
import json
import numpy as np
from typing import Dict, List, Tuple, Any

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class BenchmarkGenerator:
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
        - Depot tại trung tâm bản đồ
        - Điểm giao hàng phân bố cụm ngẫu nhiên
        - Tải trọng gói hàng từ 0.5kg đến 2.0kg
        - Khung giờ Time Windows hợp lý
        - Các vùng cấm bay No-fly zones
        """
        np.random.seed(self.seed + num_delivery)
        w, h = grid_size

        # 1. Depot (id = 0)
        depot_pos = (int(w // 2), int(h // 2))
        nodes = {
            "0": {
                "id": 0,
                "type": "depot",
                "pos": depot_pos,
                "demand": 0.0,
                "tw": [0.0, 1000.0],
                "service_time": 0.0
            }
        }

        # 2. Vùng cấm bay No-fly zones (x, y, w, h)
        no_fly_zones = []
        for _ in range(num_no_fly):
            zw = int(np.random.randint(5, 12))
            zh = int(np.random.randint(5, 12))
            zx = int(np.random.randint(2, w - zw - 2))
            zy = int(np.random.randint(2, h - zh - 2))
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
        while curr_id <= num_delivery:
            px = int(np.random.randint(2, w - 2))
            py = int(np.random.randint(2, h - 2))
            if not in_nfz(px, py) and (px, py) != depot_pos:
                demand = round(float(np.random.uniform(0.5, 1.8)), 2)
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
        while cs_count < num_charging:
            px = int(np.random.randint(5, w - 5))
            py = int(np.random.randint(5, h - 5))
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
            "grid_size": list(grid_size),
            "no_fly_zones": no_fly_zones,
            "nodes": nodes
        }

    def save_to_file(self, data: Dict[str, Any], filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[Generator] Đã tạo file benchmark: {filepath}")

if __name__ == "__main__":
    gen = BenchmarkGenerator(seed=100)
    for count in [10, 50, 100]:
        grid = (60, 60) if count <= 10 else ((100, 100) if count <= 50 else (150, 150))
        nfz = 5 if count <= 10 else (12 if count <= 50 else 20)
        charging = 3 if count <= 10 else (6 if count <= 50 else 10)
        benchmark_data = gen.generate(num_delivery=count, num_charging=charging, num_no_fly=nfz, grid_size=grid)
        out_path = os.path.join("data", "raw", f"benchmark_{count}.json")
        gen.save_to_file(benchmark_data, out_path)
