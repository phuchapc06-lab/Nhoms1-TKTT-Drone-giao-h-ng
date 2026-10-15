"""
Module Dieu phoi Tich hop He thong (End-to-End Pipeline Coordinator).
Phu trach: Thanh vien 5 (Nguyen Phuc Ha - Tech Lead & System Integrator).
Chuc nang:
- Ket noi toan dien tat ca cac thanh phan: Data Loader -> Distance Matrix -> Solver (GA / Greedy) -> Fitness -> Visualizer.
- Cung cap giao dien chay thi nghiem, so sanh doi sanh va xuat bao cao truc quan.
"""
import os
import sys
import time
import math
import json
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

# Dam bao import dung
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from algorithms.fitness import FitnessCalculator
from utils.visualizer import UAVVisualizer
from utils.validator import DataContractValidator
from utils.data_generator import UDRPDataGenerator
from models.baseline_astar import astar

class UAVRoutingPipeline:
    def __init__(
        self,
        grid_size: Tuple[int, int] = (60, 60),
        num_drones: int = 3,
        drone_capacity: float = 5.0,
        drone_speed: float = 10.0,
        seed: Optional[int] = 42
    ):
        self.grid_size = grid_size
        self.num_drones = num_drones
        self.drone_capacity = drone_capacity
        self.drone_speed = drone_speed
        self.seed = seed

        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.no_fly_zones: List[Tuple[int, int, int, int]] = []
        self.dist_matrix: Optional[np.ndarray] = None
        self.detailed_paths: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

        self.fitness_calc = FitnessCalculator(
            alpha=1.0, beta=1.5, gamma=5.0, delta=1000.0,
            drone_speed=drone_speed, drone_capacity=drone_capacity
        )
        self.visualizer = UAVVisualizer(grid_size=grid_size)
        self.validator = DataContractValidator()

    def load_benchmark_from_json(self, file_path: str) -> bool:
        """
        Nap du lieu chuan tu file JSON (do TV4 tao ra).
        """
        if not os.path.exists(file_path):
            print(f"[Pipeline] Khong tim thay file: {file_path}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        is_valid, errors = self.validator.validate_benchmark_data(data)
        if not is_valid:
            print(f"[Pipeline] Du lieu JSON khong hop le:")
            for err in errors:
                print(f"  - {err}")
            return False

        self.grid_size = tuple(data["grid_size"])
        self.no_fly_zones = [tuple(z) for z in data["no_fly_zones"]]
        self.nodes = {int(k): v for k, v in data["nodes"].items()}
        print(f"[Pipeline] Da nap thanh cong benchmark tu {file_path} voi {len(self.nodes)} nodes.")
        return True

    def generate_synthetic_data(
        self,
        num_delivery: int = 10,
        num_charging: int = 3,
        num_no_fly: int = 6
    ):
        """
        Sinh du lieu mau chuan Data Contract de phuc vu test tich hop.
        """
        generator = UDRPDataGenerator(
            grid_size=self.grid_size,
            num_delivery=num_delivery,
            num_charging=num_charging,
            num_no_fly=num_no_fly,
            seed=self.seed
        )
        generator.generate()

        self.no_fly_zones = generator.no_fly_zones
        self.nodes = {}

        # 1. Depot (id = 0)
        self.nodes[0] = {
            "id": 0,
            "type": "depot",
            "pos": generator.depot,
            "demand": 0.0,
            "tw": (0.0, 1000.0),
            "service_time": 0.0
        }

        # 2. Delivery points (id = 1..N)
        np.random.seed(self.seed)
        for i, pt in enumerate(generator.delivery_points, start=1):
            # Tải trọng gói hàng UAV thực tế từ 0.5kg đến 1.5kg (chuẩn tải trọng Drone đô thị)
            demand = round(float(np.random.uniform(0.5, 1.5)), 2)
            # Khung gio time window
            start_tw = round(float(np.random.uniform(5.0, 40.0)), 1)
            end_tw = start_tw + round(float(np.random.uniform(30.0, 60.0)), 1)
            self.nodes[i] = {
                "id": i,
                "type": "delivery",
                "pos": pt,
                "demand": demand,
                "tw": (start_tw, end_tw),
                "service_time": 5.0
            }

        # 3. Charging stations (id = N+1..)
        curr_id = num_delivery + 1
        for pt in generator.charging_stations:
            self.nodes[curr_id] = {
                "id": curr_id,
                "type": "charging",
                "pos": pt,
                "demand": 0.0,
                "tw": (0.0, 1000.0),
                "service_time": 15.0
            }
            curr_id += 1

        print(f"[Pipeline] Da khoi tao du lieu mau: Depot + {num_delivery} don giao + {num_charging} tram sac + {num_no_fly} NFZs.")

    def compute_distance_matrix(self, use_astar: bool = True):
        """
        Tính ma trận khoảng cách giữa tất cả các cặp điểm.
        Sử dụng module tối ưu hóa của Thành viên 2 (A* tối ưu + Line-of-sight + Cache).
        """
        num_nodes = len(self.nodes)
        if use_astar:
            try:
                from utils.distance_matrix import compute_distance_matrix as tv2_compute_matrix
                dist, paths = tv2_compute_matrix(self.nodes, self.no_fly_zones, self.grid_size)
                # Thay thế inf (nếu có điểm rơi vào NFZ) bằng khoảng cách Euclidean phạt để thuật toán GA không bị crash
                for i in range(num_nodes):
                    for j in range(num_nodes):
                        if math.isinf(dist[i, j]):
                            pi = self.nodes[i]["pos"]
                            pj = self.nodes[j]["pos"]
                            dist[i, j] = math.dist(pi, pj) * 2.0
                self.dist_matrix = dist
                self.detailed_paths = paths
                print(f"[Pipeline] Đã tính ma trận khoảng cách tối ưu (A* Octile + Cache TV2): {num_nodes}x{num_nodes}.")
                return
            except Exception as e:
                print(f"[Pipeline] Lưu ý: Dùng fallback A* baseline do: {e}")

        self.dist_matrix = np.zeros((num_nodes, num_nodes))
        self.detailed_paths = {}

        def in_nfz(x, y):
            for (zx, zy, zw, zh) in self.no_fly_zones:
                if zx <= x <= zx + zw and zy <= y <= zy + zh:
                    return True
            return False

        node_ids = sorted(list(self.nodes.keys()))
        for i in node_ids:
            for j in node_ids:
                if i == j:
                    self.dist_matrix[i, j] = 0.0
                    continue

                pos_i = self.nodes[i]["pos"]
                pos_j = self.nodes[j]["pos"]

                if use_astar:
                    path = astar(pos_i, pos_j, self.grid_size, in_nfz)
                    if path:
                        # Tinh do dai duong bay thuc te theo A*
                        cost = 0.0
                        for step_idx in range(len(path) - 1):
                            p1 = path[step_idx]
                            p2 = path[step_idx + 1]
                            cost += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                        self.dist_matrix[i, j] = cost
                        self.detailed_paths[(i, j)] = path
                    else:
                        # Duong thang Euclidean co phat nang neu vuot qua vat can
                        self.dist_matrix[i, j] = math.sqrt((pos_i[0] - pos_j[0])**2 + (pos_i[1] - pos_j[1])**2) * 1.5
                else:
                    self.dist_matrix[i, j] = math.sqrt((pos_i[0] - pos_j[0])**2 + (pos_i[1] - pos_j[1])**2)

        is_valid, errors = self.validator.validate_distance_matrix(self.dist_matrix, num_nodes)
        if not is_valid:
            print("[Pipeline] Canh bao ma tran khoang cach:", errors)
        else:
            print(f"[Pipeline] Tinh toan ma tran khoang cach thanh cong ({num_nodes}x{num_nodes}).")

    def solve_greedy(self) -> List[List[int]]:
        """
        Thuat toan tham lam Nearest Neighbor co kiem soat can bang tai trong (Baseline cho TV6).
        """
        deliveries = [k for k, v in self.nodes.items() if v["type"] == "delivery"]
        unvisited = set(deliveries)
        solution = [[0] for _ in range(self.num_drones)]
        drone_loads = [0.0] * self.num_drones

        while unvisited:
            best_cand = None
            best_drone = -1
            best_dist = float("inf")

            # Tim cap (drone, khach hang) gan nhat thoa man tai trong
            for d_idx in range(self.num_drones):
                curr_pos = solution[d_idx][-1]
                for cand in unvisited:
                    demand = self.nodes[cand]["demand"]
                    if drone_loads[d_idx] + demand <= self.drone_capacity:
                        dist = self.dist_matrix[curr_pos, cand]
                        if dist < best_dist:
                            best_dist = dist
                            best_cand = cand
                            best_drone = d_idx

            if best_cand is not None and best_drone != -1:
                solution[best_drone].append(best_cand)
                drone_loads[best_drone] += self.nodes[best_cand]["demand"]
                unvisited.remove(best_cand)
            else:
                # Neu tat ca cac drone deu khong con du tai (qua tai toan cuc),
                # gan khach vao drone co tai trong it nhat
                cand = min(unvisited, key=lambda c: self.nodes[c]["demand"])
                min_d_idx = int(np.argmin(drone_loads))
                solution[min_d_idx].append(cand)
                drone_loads[min_d_idx] += self.nodes[cand]["demand"]
                unvisited.remove(cand)

        # Ket thuc tai Depot (0)
        for r in solution:
            r.append(0)

        return solution

    def solve_ga(self, generations: int = 80, pop_size: int = 60) -> Tuple[List[List[int]], List[float]]:
        """
        Tích hợp giải thuật Di truyền GA chính thức của Thành viên 1 (GA Core Engine).
        Có cơ chế dự phòng (fallback) tự động.
        """
        try:
            from algorithms.genetic_algorithm import GeneticAlgorithm
            ga = GeneticAlgorithm(
                nodes=self.nodes,
                dist_matrix=self.dist_matrix,
                num_drones=self.num_drones,
                fitness_calc=self.fitness_calc,
                pop_size=pop_size,
                generations=generations,
                seed=self.seed
            )
            solution, best_fitness, history_fitness = ga.evolve()
            # Bổ sung tuyến trống nếu số lượng UAV sử dụng ít hơn num_drones
            while len(solution) < self.num_drones:
                solution.append([0, 0])
            return solution, history_fitness
        except Exception as e:
            print(f"[Pipeline] Chạy fallback GA do: {e}")

        deliveries = [k for k, v in self.nodes.items() if v["type"] == "delivery"]
        num_deliveries = len(deliveries)

        if num_deliveries == 0:
            return [[0, 0] for _ in range(self.num_drones)], [0.0]

        np.random.seed(self.seed)

        def split_chromosome(chrom: List[int]) -> List[List[int]]:
            sol = [[] for _ in range(self.num_drones)]
            drone_loads = [0.0] * self.num_drones
            d_idx = 0
            for cust in chrom:
                demand = self.nodes[cust]["demand"]
                if drone_loads[d_idx] + demand > self.drone_capacity and d_idx < self.num_drones - 1:
                    d_idx += 1
                sol[d_idx].append(cust)
                drone_loads[d_idx] += demand
            return [[0] + r + [0] for r in sol]

        population = []
        for _ in range(pop_size):
            chrom = list(np.random.permutation(deliveries))
            population.append(chrom)

        # Them ca the Greedy vao quan the ban dau de tang toc hoi tu
        greedy_sol = self.solve_greedy()
        greedy_chrom = []
        for r in greedy_sol:
            greedy_chrom.extend([x for x in r if x != 0])
        if set(greedy_chrom) == set(deliveries):
            population[0] = greedy_chrom

        best_solution = None
        best_fitness = -float("inf")
        history_fitness = []

        # 2. Vong lap tien hoa
        for gen in range(generations):
            scores = []
            for chrom in population:
                sol = split_chromosome(chrom)
                fitness, _, _ = self.fitness_calc.evaluate_solution(sol, self.dist_matrix, self.nodes)
                scores.append(fitness)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = sol

            history_fitness.append(best_fitness)

            # Chon loc Tournament
            new_pop = []
            # Elitism: Giu lai ca the tot nhat
            best_idx = int(np.argmax(scores))
            new_pop.append(population[best_idx].copy())

            while len(new_pop) < pop_size:
                # Tournament selection
                i1, i2 = np.random.randint(0, pop_size, 2)
                p1 = population[i1] if scores[i1] > scores[i2] else population[i2]
                i3, i4 = np.random.randint(0, pop_size, 2)
                p2 = population[i3] if scores[i3] > scores[i4] else population[i4]

                # Order Crossover (OX)
                if np.random.rand() < 0.85 and num_deliveries > 2:
                    cut1, cut2 = sorted(np.random.choice(num_deliveries, 2, replace=False))
                    child = [-1] * num_deliveries
                    child[cut1:cut2] = p1[cut1:cut2]
                    fill = [item for item in p2 if item not in child[cut1:cut2]]
                    ptr = 0
                    for k in range(num_deliveries):
                        if child[k] == -1:
                            child[k] = fill[ptr]
                            ptr += 1
                else:
                    child = p1.copy()

                # Swap Mutation
                if np.random.rand() < 0.2 and num_deliveries > 1:
                    m1, m2 = np.random.choice(num_deliveries, 2, replace=False)
                    child[m1], child[m2] = child[m2], child[m1]

                new_pop.append(child)

            population = new_pop

        return best_solution, history_fitness

    def run_experiment(
        self,
        algorithm: str = "ga",
        save_figure_dir: Optional[str] = "docs/figures",
        show_plot: bool = False
    ) -> Dict[str, Any]:
        """
        Chay toan trinh mot thuat toan, danh gia va xuat ket qua.
        """
        if self.dist_matrix is None:
            self.compute_distance_matrix(use_astar=True)

        start_time = time.time()
        history_fitness = None

        if algorithm.lower() == "ga":
            solution, history_fitness = self.solve_ga(generations=80, pop_size=50)
            algo_name = "Thuật toán Di truyền (A* + Genetic Algorithm)"
        elif algorithm.lower() == "greedy":
            solution = self.solve_greedy()
            algo_name = "Thuật toán Tham lam (A* + Greedy Baseline)"
        else:
            raise ValueError(f"Khong ho tro thuat toan: {algorithm}")

        exec_time = time.time() - start_time
        fitness, total_cost, breakdown = self.fitness_calc.evaluate_solution(solution, self.dist_matrix, self.nodes)
        is_valid, validation_errors = self.validator.validate_solution(solution, self.nodes, self.drone_capacity)

        res = {
            "algorithm": algo_name,
            "exec_time_sec": round(exec_time, 4),
            "fitness": round(fitness, 4),
            "total_cost": round(total_cost, 2),
            "distance": round(breakdown["distance"], 2),
            "energy": round(breakdown["energy"], 2),
            "tw_penalty": round(breakdown["tw_penalty"], 2),
            "is_valid": is_valid,
            "errors": validation_errors,
            "solution": solution
        }

        # Luu anh neu co yeu cau
        if save_figure_dir:
            os.makedirs(save_figure_dir, exist_ok=True)
            map_path = os.path.join(save_figure_dir, f"route_{algorithm.lower()}.png")
            self.visualizer.plot_multi_uav_routes(
                nodes=self.nodes,
                no_fly_zones=self.no_fly_zones,
                solution=solution,
                detailed_paths=self.detailed_paths,
                title=f"{algo_name} | Cost: {total_cost:.1f}",
                save_path=map_path,
                show=show_plot
            )

            if history_fitness:
                conv_path = os.path.join(save_figure_dir, f"convergence_{algorithm.lower()}.png")
                self.visualizer.plot_convergence_curve(
                    history_fitness=history_fitness,
                    title=f"Đường cong Hội tụ GA ({len(self.nodes)-1} điểm)",
                    save_path=conv_path,
                    show=show_plot
                )

        return res

    def compare_algorithms(self, save_dir: Optional[str] = "docs/figures", show_plot: bool = False):
        """
        Chay so sanh truc tiep giua A* + GA va A* + Greedy Baseline.
        In bang Markdown so sanh chuyen nghiep.
        """
        print("\n=======================================================")
        print("  BẮT ĐẦU CHẠY THỬ NGHIỆM ĐỐI SÁNH (BENCHMARK COMPARISON) ")
        print("=======================================================")

        res_greedy = self.run_experiment(algorithm="greedy", save_figure_dir=save_dir, show_plot=False)
        res_ga = self.run_experiment(algorithm="ga", save_figure_dir=save_dir, show_plot=show_plot)

        # In bang so sanh
        dist_diff = ((res_greedy["distance"] - res_ga["distance"]) / res_greedy["distance"]) * 100
        cost_diff = ((res_greedy["total_cost"] - res_ga["total_cost"]) / res_greedy["total_cost"]) * 100

        print("\n" + "="*70)
        print("BẢNG KẾT QUẢ SO SÁNH HIỆU NĂNG THỰC NGHIỆM:")
        print("="*70)
        print(f"{'Chỉ số đánh giá':<28} | {'A* + Greedy (Baseline)':<20} | {'A* + GA (Đề xuất)':<18}")
        print("-" * 70)
        print(f"{'Tổng quãng đường (km)':<28} | {res_greedy['distance']:<20.2f} | {res_ga['distance']:<18.2f}")
        print(f"{'Năng lượng tiêu hao (Wh)':<28} | {res_greedy['energy']:<20.2f} | {res_ga['energy']:<18.2f}")
        print(f"{'Phạt trễ hẹn (Time Window)':<28} | {res_greedy['tw_penalty']:<20.2f} | {res_ga['tw_penalty']:<18.2f}")
        print(f"{'Tổng chi phí (Total Cost)':<28} | {res_greedy['total_cost']:<20.2f} | {res_ga['total_cost']:<18.2f}")
        print(f"{'Điểm thích nghi (Fitness)':<28} | {res_greedy['fitness']:<20.4f} | {res_ga['fitness']:<18.4f}")
        print(f"{'Thời gian tính toán (s)':<28} | {res_greedy['exec_time_sec']:<20.4f} | {res_ga['exec_time_sec']:<18.4f}")
        print(f"{'Hợp lệ ràng buộc (Valid)':<28} | {str(res_greedy['is_valid']):<20} | {str(res_ga['is_valid']):<18}")
        print("=" * 70)
        print(f"-> KẾT LUẬN: A* + GA tiết kiệm được {cost_diff:.1f}% chi phí tổng và rút ngắn {dist_diff:.1f}% quãng đường so với Greedy Baseline!")
        print("=" * 70 + "\n")

        return res_greedy, res_ga
