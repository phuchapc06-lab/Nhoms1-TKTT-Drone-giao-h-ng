"""
Module giải thuật di truyền (Genetic Algorithm) tối ưu phân chia và thứ tự giao hàng cho đội bay K UAV.
Phụ trách: Thành viên 1 (GA Core Engine).

Biểu diễn nhiễm sắc thể (Chromosome):
    Hoán vị các ID khách hàng xen kẽ K-1 vách ngăn mang số âm (-1, -2, ..., -(K-1)).
    Mỗi đoạn nằm giữa hai vách ngăn là tuyến bay của một Drone.
    Ví dụ (K = 3): [3, 1, -1, 5, 2, -2, 4]  ->  [[0, 3, 1, 0], [0, 5, 2, 0], [0, 4, 0]]
"""
import random
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
        pop_size: int = 80,
        generations: int = 300,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
        elitism: int = 2,
        seed: Optional[int] = None
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

        # Cache: tuple(chromosome) -> (fitness, cost, breakdown)
        self._cache: Dict[Tuple[int, ...], Tuple[float, float, Dict[str, float]]] = {}

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

    def _random_chromosome(self) -> Chromosome:
        """Sinh một cá thể ngẫu nhiên: xáo trộn khách hàng và vách ngăn."""
        chromosome = self.genes[:]
        self.rng.shuffle(chromosome)
        return chromosome

    def _init_population(self) -> List[Chromosome]:
        """Khởi tạo quần thể ban đầu gồm pop_size cá thể ngẫu nhiên."""
        return [self._random_chromosome() for _ in range(self.pop_size)]

    # ------------------------------------------------------------------
    # 2. Đánh giá độ thích nghi
    # ------------------------------------------------------------------
    def _evaluate(self, chromosome: Chromosome) -> Tuple[float, float, Dict[str, float]]:
        """
        Đánh giá cá thể bằng FitnessCalculator của TV5.
        Trả về (fitness, cost, breakdown); kết quả được cache theo chromosome.
        """
        key = tuple(chromosome)
        if key not in self._cache:
            self._cache[key] = self.fitness_calc.evaluate_solution(
                self.decode(chromosome), self.dist_matrix, self.nodes, self.energy_manager
            )
        return self._cache[key]

    def _fitness(self, chromosome: Chromosome) -> float:
        return self._evaluate(chromosome)[0]
