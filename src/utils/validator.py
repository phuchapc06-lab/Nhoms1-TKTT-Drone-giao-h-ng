"""
Module kiem tra va xac thuc tinh hop le cua du lieu (Data Contract & Solution Validator).
Phu trach: Thanh vien 5 (Nguyen Phuc Ha - Tech Lead & Integrator).
Muc tieu: Dam bao code cua ca 6 thanh vien tuan thu chuan Data Contract,
          tu dong phat hien loi sai format truoc khi tich hop vao nhanh develop.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

class DataContractValidator:
    """
    Bo kiem dinh chuan du lieu cho bai toan UDRP.
    """

    @staticmethod
    def validate_benchmark_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Kiem tra cau truc du lieu dau vao (do TV4 tao ra hoac nhat vao tu file JSON).
        Ho tro linh hoat ca dinh dang dict lan list cua cac thanh vien trong nhom.
        """
        errors = []

        # 1. Kiem tra cac truong cap cao
        if "grid_size" not in data:
            if "map_size" in data and isinstance(data["map_size"], (int, float)):
                pass
            else:
                errors.append("Thieu truong 'grid_size' trong benchmark data.")
        elif not (isinstance(data["grid_size"], (list, tuple)) and len(data["grid_size"]) == 2):
            errors.append("'grid_size' phai la tuple/list co 2 phan tu (width, height).")

        if "nodes" not in data:
            errors.append("Thieu truong 'nodes' trong benchmark data.")
        elif not isinstance(data["nodes"], (dict, list)) or len(data["nodes"]) == 0:
            errors.append("'nodes' phai la dictionary khac rong.")

        if "no_fly_zones" not in data:
            errors.append("Thieu truong 'no_fly_zones' trong benchmark data.")
        elif not isinstance(data["no_fly_zones"], list):
            errors.append("'no_fly_zones' phai la danh sach cac hinh chu nhat (x, y, w, h).")

        if errors:
            return False, errors

        # 2. Kiem tra Depot (Node 0)
        raw_nodes = data["nodes"]
        nodes_dict: Dict[Any, Any] = {}
        if isinstance(raw_nodes, list):
            for item in raw_nodes:
                if isinstance(item, dict) and "id" in item:
                    try:
                        nodes_dict[int(item["id"])] = item
                    except ValueError:
                        nodes_dict[item["id"]] = item
                else:
                    errors.append("Moi phan tu trong danh sach nodes phai la dictionary chua 'id'.")
        else:
            for k, v in raw_nodes.items():
                try:
                    nodes_dict[int(k)] = v
                except ValueError:
                    errors.append(f"Node key '{k}' khong hop le, phai la so nguyen.")
                    nodes_dict[k] = v

        if 0 not in nodes_dict:
            errors.append("Bat buoc phai co Trạm gốc (Depot) voi ID = 0.")

        # 3. Kiem tra chi tiet tung Node
        has_delivery = False
        for nid, node in nodes_dict.items():
            if not isinstance(node, dict):
                errors.append(f"Node {nid} phai la mot dictionary.")
                continue

            # Kiem tra type
            ntype = node.get("type")
            if ntype not in ["depot", "delivery", "charging"]:
                errors.append(f"Node {nid} co type='{ntype}' khong hop le (chi chap nhan depot, delivery, charging).")
            if ntype == "delivery":
                has_delivery = True

            # Kiem tra pos
            pos = node.get("pos")
            if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
                errors.append(f"Node {nid} thieu toa do hop le 'pos': (x, y).")

            # Kiem tra demand
            demand = node.get("demand", 0.0)
            if demand < 0:
                errors.append(f"Node {nid} co nhu cau tai trong demand am ({demand}).")

            # Kiem tra time window
            tw = node.get("tw")
            if tw is not None:
                if not (isinstance(tw, (list, tuple)) and len(tw) == 2 and tw[0] <= tw[1]):
                    errors.append(f"Node {nid} co Time Window hop le tw=[start, end] voi start <= end.")

        if not has_delivery:
            errors.append("Du lieu phai co it nhat mot diem giao hang (delivery).")

        return len(errors) == 0, errors

    @staticmethod
    def validate_distance_matrix(matrix: Any, num_nodes: int) -> Tuple[bool, List[str]]:
        """
        Kiem tra tinh hop le cua Ma tran khoang cach (do TV2 tao ra).
        """
        errors = []
        mat = np.array(matrix)

        if mat.shape != (num_nodes, num_nodes):
            errors.append(f"Kich thuoc ma tran khong khop: Ky vong ({num_nodes}, {num_nodes}), thuc te la {mat.shape}.")
            return False, errors

        # Kiem tra gia tri khong am
        if np.any(mat < 0):
            errors.append("Ma tran khoang cach chua gia tri am khong hop le.")

        # Kiem tra duong cheo chinh phai bang 0
        diag = np.diag(mat)
        if not np.allclose(diag, 0):
            errors.append("Cac phan tu tren duong cheo chinh (khoang cach tu i den i) phai bang 0.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_solution(
        solution: List[List[int]],
        nodes: Dict[int, Dict[str, Any]],
        drone_capacity: float = 5.0
    ) -> Tuple[bool, List[str]]:
        """
        Kiem tra tinh hop le cua Loi giai dinh tuyen da UAV (do TV1 hoac TV6 sinh ra).
        Cac tieu chi nghiem ngat:
        1. Moi tuyen phai bat dau va ket thuc tai Depot (0).
        2. Tat ca cac diem giao hang (delivery) phai duoc phuc vu dung 1 lan duy nhat.
        3. Tong tai trong tren moi tuyen khong duoc vuot qua gioi han drone_capacity.
        """
        errors = []

        if not isinstance(solution, list) or len(solution) == 0:
            return False, ["Loi giai (solution) phai la danh sach cac tuyen bay khong rong."]

        delivery_nodes = set(
            int(k) for k, v in nodes.items()
            if v.get("type") == "delivery"
        )
        visited_deliveries = []

        for drone_idx, route in enumerate(solution):
            if not isinstance(route, list):
                errors.append(f"Tuyen bay cua Drone #{drone_idx + 1} phai la mot danh sach ID.")
                continue

            if len(route) < 2:
                errors.append(f"Tuyen bay cua Drone #{drone_idx + 1} qua ngan (len={len(route)}).")
                continue

            # Kiem tra bat dau va ket thuc tai Depot (0)
            if route[0] != 0 or route[-1] != 0:
                errors.append(f"Tuyen Drone #{drone_idx + 1} bat buoc phai xuat phat va tro ve Depot (0). Tuyen hien tai: {route}")

            # Kiem tra tai trong
            route_demand = 0.0
            for node_id in route:
                node_data = nodes.get(node_id, {})
                if node_data.get("type") == "delivery":
                    visited_deliveries.append(node_id)
                    route_demand += node_data.get("demand", 0.0)

            # Kiem tra tai trong (cho phep sai so lam tron 0.01kg)
            tolerance = 0.01
            if route_demand > drone_capacity + tolerance:
                errors.append(
                    f"Tuyen Drone #{drone_idx + 1} vi pham tai trong toi da: {route_demand:.2f}kg > {drone_capacity:.2f}kg."
                )

        # Kiem tra tinh toan ven cua tap diem giao hang
        visited_set = set(visited_deliveries)
        missing_deliveries = delivery_nodes - visited_set
        if missing_deliveries:
            errors.append(f"Con {len(missing_deliveries)} diem giao chua duoc phuc vu: {sorted(list(missing_deliveries))}.")

        if len(visited_deliveries) != len(visited_set):
            # Co diem bi giao trung lap
            duplicates = [nid for nid in visited_set if visited_deliveries.count(nid) > 1]
            errors.append(f"Cac diem giao sau bi phuc vu trung lap nhieu lan: {duplicates}.")

        return len(errors) == 0, errors
