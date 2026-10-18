import json
import random
import os


def generate_benchmark(num_customers, num_charging, num_nofly, output_path, map_size=100, seed=42):
    """Sinh dữ liệu mô phỏng đô thị thực tế theo Data Contract của ."""
    random.seed(seed + num_customers)
    nodes = []

    # 1. Trạm gốc (Depot) - ID = 0
    nodes.append({
        "id": 0,
        "type": "depot",
        "pos": (map_size // 2, map_size // 2),
        "demand": 0.0,
        "tw": (0, 1000),
        "service_time": 0
    })

    # Tạo các tâm cụm dân cư (Clustered)
    num_clusters = max(2, num_customers // 15 + 2)
    clusters = [(random.randint(15, map_size - 15), random.randint(15, map_size - 15)) for _ in range(num_clusters)]

    # 2. Khách hàng (Delivery) - ID: 1..N
    for i in range(1, num_customers + 1):
        cx, cy = random.choice(clusters)
        x = max(0, min(map_size, int(random.gauss(cx, 10))))
        y = max(0, min(map_size, int(random.gauss(cy, 10))))

        t_min = random.randint(0, 400)
        t_max = t_min + random.randint(60, 180)

        nodes.append({
            "id": i,
            "type": "delivery",
            "pos": (x, y),
            "demand": round(random.uniform(1.0, 5.0), 1),
            "tw": (t_min, t_max),
            "service_time": 5
        })

    # 3. Trạm sạc (Charging) - ID: N+1..
    start_charging_id = num_customers + 1
    for i in range(start_charging_id, start_charging_id + num_charging):
        nodes.append({
            "id": i,
            "type": "charging",
            "pos": (random.randint(10, map_size - 10), random.randint(10, map_size - 10)),
            "demand": 0.0,
            "tw": (0, 1000),
            "service_time": 5
        })

    # 4. Vùng cấm bay (No-fly zones)
    no_fly_zones = []
    for i in range(num_nofly):
        w = random.randint(8, 15)
        h = random.randint(8, 15)
        x_min = random.randint(5, map_size - w - 5)
        y_min = random.randint(5, map_size - h - 5)
        if x_min <= map_size // 2 <= x_min + w and y_min <= map_size // 2 <= y_min + h:
            x_min = max(5, x_min - 20)

        no_fly_zones.append({
            "id": i + 1,
            "bounds": (x_min, y_min, x_min + w, y_min + h)
        })

    data = {
        "map_size": map_size,
        "num_customers": num_customers,
        "num_charging": num_charging,
        "nodes": nodes,
        "no_fly_zones": no_fly_zones
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"Đã xuất thành công file mẫu Ngày 2: {output_path}")


def load_benchmark(file_path):
    """Hàm nạp dữ liệu từ file JSON theo Data Contract."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for node in data.get("nodes", []):
        node["pos"] = tuple(node["pos"])
        node["tw"] = tuple(node["tw"])

    for zone in data.get("no_fly_zones", []):
        if "bounds" in zone:
            zone["bounds"] = tuple(zone["bounds"])

    return data


if __name__ == "__main__":
    #4 bộ dữ liệu đa quy mô chuẩn
    configs = [
        (10, 2, 2, "data/raw/benchmark_10.json"),
        (50, 5, 4, "data/raw/benchmark_50.json"),
        (100, 10, 6, "data/raw/benchmark_100.json"),
        (500, 25, 10, "data/raw/benchmark_500.json"),
    ]

    for n_cust, n_chg, n_nfz, path in configs:
        generate_benchmark(
            num_customers=n_cust,
            num_charging=n_chg,
            num_nofly=n_nfz,
            output_path=path
        )

    # Kiểm tra đọc thử bộ 100 điểm
    du_lieu_100 = load_benchmark("data/raw/benchmark_100.json")
    print(
        f"Kiểm tra bộ 100 điểm: Tổng số node = {len(du_lieu_100['nodes'])}, Vùng cấm bay = {len(du_lieu_100['no_fly_zones'])}")