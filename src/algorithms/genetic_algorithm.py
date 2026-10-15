"""
Module giải thuật di truyền (Genetic Algorithm) tối ưu phân chia và thứ tự giao hàng cho đội bay K UAV.
Phụ trách: Thành viên 1 (GA Core Engine).

Biểu diễn nhiễm sắc thể (Chromosome):
    Hoán vị các ID khách hàng xen kẽ K-1 vách ngăn mang số âm (-1, -2, ..., -(K-1)).
    Mỗi đoạn nằm giữa hai vách ngăn là tuyến bay của một Drone.
    Ví dụ (K = 3): [3, 1, -1, 5, 2, -2, 4]  ->  [[0, 3, 1, 0], [0, 5, 2, 0], [0, 4, 0]]
"""
import random
import time
from typing import List, Dict, Tuple, Any, Optional

from algorithms.fitness import FitnessCalculator

DEPOT_ID = 0

Chromosome = List[int]


class GeneticAlgorithm:
    def __init__(
        self,
        nodes: Dict[int, Dict[str, Any]],
        dist_matrix: Any,
        num_drones: int,
        fitness_calc: Optional[FitnessCalculator] = None,
        energy_manager: Optional[Any] = None,
        # Mặc định chọn từ thực nghiệm tinh chỉnh trên benchmark 10 & 50 điểm (src/utils/ga_tuning.py)
        pop_size: int = 100,
        generations: int = 2000,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.5,
        tournament_size: int = 3,
        elitism: int = 2,
        seed: Optional[int] = None,
        initial_solutions: Optional[List[List[List[int]]]] = None,
        constraint_penalty_factor: float = 100.0
    ):
        if num_drones < 1:
            raise ValueError("num_drones phải >= 1")
        if pop_size < 2:
            raise ValueError("pop_size phải >= 2")
        if generations < 1:
            raise ValueError("generations phải >= 1")
        if not (0.0 <= crossover_rate <= 1.0 and 0.0 <= mutation_rate <= 1.0):
            raise ValueError("crossover_rate và mutation_rate phải nằm trong [0, 1]")
        if tournament_size < 1:
            raise ValueError("tournament_size phải >= 1")
        if not (0 <= elitism < pop_size):
            raise ValueError("elitism phải nằm trong [0, pop_size)")
        if constraint_penalty_factor < 1.0:
            raise ValueError("constraint_penalty_factor phải >= 1")

        self.nodes = nodes
        self.dist_matrix = dist_matrix
        self.num_drones = num_drones
        self.fitness_calc = fitness_calc if fitness_calc is not None else FitnessCalculator()
        self.energy_manager = energy_manager
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism = elitism
        # Hệ số nhân phần phạt vi phạm ràng buộc cứng (quá tải / cạn pin) khi chọn lọc.
        # delta của FitnessCalculator quá nhẹ ở quy mô lớn: quá tải 0.05 kg chỉ bị phạt 50 trong cost ~10^4,
        # nên GA chấp nhận vi phạm nhỏ. Đặt 1.0 để dùng nguyên fitness của TV5.
        self.constraint_penalty_factor = constraint_penalty_factor

        # Bộ sinh số ngẫu nhiên riêng -> không ảnh hưởng random toàn cục của module khác
        self.rng = random.Random(seed)

        # Chỉ điểm giao hàng mới nằm trong chromosome (bỏ qua Depot và trạm sạc)
        self.customers: List[int] = sorted(
            nid for nid, node in nodes.items() if node.get("type") == "delivery"
        )
        if not self.customers:
            raise ValueError("Không có điểm giao hàng (type == 'delivery') nào trong nodes")

        # K-1 vách ngăn: -1, -2, ..., -(K-1)
        self.separators: List[int] = list(range(-1, -num_drones, -1))
        self.genes: List[int] = self.customers + self.separators
        self._customer_set = set(self.customers)

        # Lời giải có sẵn (vd. Greedy của TV6) được đưa vào quần thể ban đầu; mã hóa ngay để báo lỗi sớm
        self.initial_chromosomes: List[Chromosome] = [self.encode(s) for s in (initial_solutions or [])]

        # Cache: tuple(chromosome) -> (fitness, cost, breakdown)
        self._cache: Dict[Tuple[int, ...], Tuple[float, float, Dict[str, float]]] = {}

        # Kết quả, được gán sau khi gọi evolve()
        self.best_chromosome: Optional[Chromosome] = None
        self.best_solution: Optional[List[List[int]]] = None
        self.best_fitness: float = 0.0
        self.best_cost: float = float("inf")
        self.best_breakdown: Dict[str, float] = {}
        self.history: List[float] = []
        self.runtime: float = 0.0

    # ------------------------------------------------------------------
    # 1. Mã hóa / Giải mã
    # ------------------------------------------------------------------
    def decode(self, chromosome: Chromosome) -> List[List[int]]:
        """
        Giải mã chromosome thành lời giải theo Data Contract.
        Cắt dãy tại các vách ngăn (số âm); tuyến rỗng (hai vách ngăn liền nhau) bị bỏ qua.
        """
        solution: List[List[int]] = []
        current: List[int] = []
        for gene in chromosome:
            if gene < 0:
                if current:
                    solution.append([DEPOT_ID] + current + [DEPOT_ID])
                current = []
            else:
                current.append(gene)
        if current:
            solution.append([DEPOT_ID] + current + [DEPOT_ID])
        return solution

    def encode(self, solution: List[List[int]]) -> Chromosome:
        """
        Mã hóa ngược lời giải (danh sách tuyến) thành chromosome; bỏ qua Depot và trạm sạc trong tuyến.
        Ví dụ (K = 3): [[0, 3, 1, 0], [0, 4, 0]]  ->  [3, 1, -1, 4, -2]
        """
        routes = [[nid for nid in route if nid in self._customer_set] for route in solution]
        routes = [route for route in routes if route]
        if len(routes) > self.num_drones:
            raise ValueError(f"Lời giải có {len(routes)} tuyến, nhiều hơn số Drone K = {self.num_drones}")

        chromosome: Chromosome = []
        for idx, route in enumerate(routes):
            if idx > 0:
                chromosome.append(self.separators[idx - 1])
            chromosome.extend(route)
        chromosome.extend(self.separators[max(len(routes) - 1, 0):])  # vách ngăn còn thừa -> tuyến rỗng ở cuối

        if sorted(chromosome) != sorted(self.genes):
            raise ValueError("Lời giải phải giao mỗi điểm giao hàng đúng 1 lần")
        return chromosome

    def _random_chromosome(self) -> Chromosome:
        """Sinh một cá thể ngẫu nhiên: xáo trộn khách hàng và vách ngăn."""
        chromosome = self.genes[:]
        self.rng.shuffle(chromosome)
        return chromosome

    def _init_population(self) -> List[Chromosome]:
        """Khởi tạo quần thể: các lời giải có sẵn (nếu có) + cá thể ngẫu nhiên cho đủ pop_size."""
        population = [c[:] for c in self.initial_chromosomes[:self.pop_size]]
        population += [self._random_chromosome() for _ in range(self.pop_size - len(population))]
        return population

    # ------------------------------------------------------------------
    # 2. Đánh giá độ thích nghi
    # ------------------------------------------------------------------
    def _evaluate(self, chromosome: Chromosome) -> Tuple[float, float, Dict[str, float]]:
        """
        Đánh giá cá thể bằng FitnessCalculator của TV5.
        Trả về (fitness, cost, breakdown); kết quả được cache theo chromosome.
        - cost, breakdown: đúng giá trị của TV5 (dùng để báo cáo).
        - fitness: dùng để chọn lọc, = 1000 / (cost + (factor - 1) * cap_penalty + 1);
          bằng fitness của TV5 khi lời giải thỏa ràng buộc hoặc factor = 1.
        """
        key = tuple(chromosome)
        if key not in self._cache:
            _, cost, breakdown = self.fitness_calc.evaluate_solution(
                self.decode(chromosome), self.dist_matrix, self.nodes, self.energy_manager
            )
            penalized = cost + (self.constraint_penalty_factor - 1.0) * breakdown["cap_penalty"]
            self._cache[key] = (1000.0 / (penalized + 1.0), cost, breakdown)
        return self._cache[key]

    def _fitness(self, chromosome: Chromosome) -> float:
        return self._evaluate(chromosome)[0]

    # ------------------------------------------------------------------
    # 3. Toán tử di truyền
    # ------------------------------------------------------------------
    def _tournament_select(self, population: List[Chromosome], fitnesses: List[float]) -> Chromosome:
        """Chọn lọc Tournament: lấy ngẫu nhiên tournament_size cá thể, giữ cá thể có fitness cao nhất."""
        k = min(self.tournament_size, len(population))
        contenders = self.rng.sample(range(len(population)), k)
        winner = max(contenders, key=lambda idx: fitnesses[idx])
        return population[winner]

    def _order_crossover(
        self, parent1: Chromosome, parent2: Chromosome, cut: Optional[Tuple[int, int]] = None
    ) -> Chromosome:
        """
        Lai ghép thứ tự (Order Crossover - OX):
        1. Chép nguyên đoạn [a, b] của parent1 sang con.
        2. Các vị trí còn lại điền gen của parent2 theo thứ tự xuất hiện, bắt đầu từ b+1 và vòng về đầu,
           bỏ qua gen đã có -> con luôn là hoán vị hợp lệ (không trùng / thiếu đơn hàng hay vách ngăn).
        Tham số cut=(a, b) chỉ dùng để kiểm thử.
        """
        n = len(parent1)
        if n < 2:
            return parent1[:]
        a, b = cut if cut is not None else sorted(self.rng.sample(range(n), 2))

        child: List[Optional[int]] = [None] * n
        child[a:b + 1] = parent1[a:b + 1]
        used = set(parent1[a:b + 1])

        fill_genes = [g for g in parent2[b + 1:] + parent2[:b + 1] if g not in used]
        fill_positions = list(range(b + 1, n)) + list(range(0, a))
        for pos, gene in zip(fill_positions, fill_genes):
            child[pos] = gene
        return child  # type: ignore[return-value]

    def _swap_mutation(self, chromosome: Chromosome) -> Chromosome:
        """Đột biến hoán đổi (Swap): với xác suất mutation_rate, đổi chỗ 2 gen ngẫu nhiên. Trả về bản sao mới."""
        mutant = chromosome[:]
        if len(mutant) >= 2 and self.rng.random() < self.mutation_rate:
            i, j = self.rng.sample(range(len(mutant)), 2)
            mutant[i], mutant[j] = mutant[j], mutant[i]
        return mutant

    # ------------------------------------------------------------------
    # 4. Vòng lặp tiến hóa
    # ------------------------------------------------------------------
    def _next_generation(self, population: List[Chromosome], fitnesses: List[float]) -> List[Chromosome]:
        """
        Sinh thế hệ kế tiếp:
        - Elitism: giữ nguyên `elitism` cá thể tốt nhất.
        - Phần còn lại: Tournament chọn 2 cha -> OX (theo crossover_rate, không lai thì sao chép cha 1) -> Swap.
        """
        ranked = sorted(range(len(population)), key=lambda idx: fitnesses[idx], reverse=True)
        next_population = [population[idx][:] for idx in ranked[:self.elitism]]

        while len(next_population) < self.pop_size:
            parent1 = self._tournament_select(population, fitnesses)
            parent2 = self._tournament_select(population, fitnesses)
            if self.rng.random() < self.crossover_rate:
                child = self._order_crossover(parent1, parent2)
            else:
                child = parent1[:]
            next_population.append(self._swap_mutation(child))
        return next_population

    def evolve(self) -> Tuple[List[List[int]], float, List[float]]:
        """
        Chạy GA qua `generations` thế hệ (thế hệ đầu tiên là quần thể khởi tạo ngẫu nhiên).
        Trả về:
            - best_solution: lời giải tốt nhất theo Data Contract
            - best_fitness: độ thích nghi (dùng để chọn lọc, xem _evaluate) của lời giải đó
            - history: best fitness tốt nhất tính đến mỗi thế hệ (dùng cho UAVVisualizer.plot_convergence_curve)
        Sau khi chạy có thêm các thuộc tính: best_chromosome, best_cost, best_breakdown (giá trị của TV5),
        runtime (giây).
        """
        start = time.perf_counter()
        best_chromosome: Optional[Chromosome] = None
        best_eval: Optional[Tuple[float, float, Dict[str, float]]] = None
        history: List[float] = []

        population = self._init_population()
        fitnesses: List[float] = []
        for gen in range(self.generations):
            if gen > 0:
                population = self._next_generation(population, fitnesses)

            evaluations = [self._evaluate(c) for c in population]
            fitnesses = [ev[0] for ev in evaluations]
            # Chỉ giữ cache của quần thể hiện tại: đủ để thế hệ sau dùng lại cho elite / bản sao,
            # và bộ nhớ không phình theo số thế hệ (quan trọng với benchmark 500 điểm)
            self._cache = {tuple(c): ev for c, ev in zip(population, evaluations)}

            gen_best = max(range(len(population)), key=fitnesses.__getitem__)
            if best_eval is None or fitnesses[gen_best] > best_eval[0]:
                best_chromosome = population[gen_best][:]
                best_eval = evaluations[gen_best]
            history.append(best_eval[0])

        self.best_chromosome = best_chromosome
        self.best_solution = self.decode(best_chromosome)
        self.best_fitness, self.best_cost, self.best_breakdown = best_eval
        self.history = history
        self.runtime = time.perf_counter() - start
        return self.best_solution, self.best_fitness, history
