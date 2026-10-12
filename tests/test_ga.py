"""
Unit test kiem thu doc lap cho module GA cua Thanh vien 1 (GeneticAlgorithm).
"""
import sys
import os
import math
import numpy as np

# Dam bao ho tro tieng Viet tren Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Them duong dan src vao he thong
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.fitness import FitnessCalculator


def make_mock_data():
    """8 diem giao hang, 1 tram sac, ma tran khoang cach Euclid (gia lap TV2)."""
    nodes = {
        0: {"id": 0, "type": "depot", "pos": (30, 30), "demand": 0.0, "tw": (0, 1000), "service_time": 0},
        1: {"id": 1, "type": "delivery", "pos": (10, 12), "demand": 2.0, "tw": (0, 120), "service_time": 5},
        2: {"id": 2, "type": "delivery", "pos": (15, 45), "demand": 1.5, "tw": (0, 120), "service_time": 5},
        3: {"id": 3, "type": "delivery", "pos": (48, 50), "demand": 2.5, "tw": (0, 120), "service_time": 5},
        4: {"id": 4, "type": "delivery", "pos": (52, 18), "demand": 1.0, "tw": (0, 120), "service_time": 5},
        5: {"id": 5, "type": "delivery", "pos": (22, 8), "demand": 1.5, "tw": (0, 120), "service_time": 5},
        6: {"id": 6, "type": "delivery", "pos": (8, 30), "demand": 2.0, "tw": (0, 120), "service_time": 5},
        7: {"id": 7, "type": "delivery", "pos": (40, 55), "demand": 1.0, "tw": (0, 120), "service_time": 5},
        8: {"id": 8, "type": "delivery", "pos": (55, 35), "demand": 2.0, "tw": (0, 120), "service_time": 5},
        9: {"id": 9, "type": "charging", "pos": (30, 15), "demand": 0.0, "tw": (0, 1000), "service_time": 15},
    }
    n = len(nodes)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            pi, pj = nodes[i]["pos"], nodes[j]["pos"]
            dist_matrix[i, j] = math.sqrt((pi[0] - pj[0])**2 + (pi[1] - pj[1])**2)
    return nodes, dist_matrix


def is_valid_chromosome(chromosome, ga):
    return sorted(chromosome) == sorted(ga.customers + ga.separators)


def test_init_and_validation():
    print("\n1. Kiem tra khoi tao & validate tham so:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=1)

    assert ga.customers == [1, 2, 3, 4, 5, 6, 7, 8], "Chi lay diem giao hang, bo depot & tram sac"
    assert ga.separators == [-1, -2], "K=3 -> 2 vach ngan -1, -2"
    assert GeneticAlgorithm(nodes, dist, num_drones=1).separators == [], "K=1 -> khong co vach ngan"

    for bad_kwargs in ({"num_drones": 0}, {"num_drones": 2, "pop_size": 1},
                       {"num_drones": 2, "mutation_rate": 1.5}, {"num_drones": 2, "elitism": 80}):
        try:
            GeneticAlgorithm(nodes, dist, **bad_kwargs)
            assert False, f"Phai bao loi voi tham so {bad_kwargs}"
        except ValueError:
            pass

    only_depot = {0: nodes[0], 9: nodes[9]}
    try:
        GeneticAlgorithm(only_depot, dist, num_drones=2)
        assert False, "Phai bao loi khi khong co diem giao hang"
    except ValueError:
        pass
    print("-> Khoi tao & validate hoat dong chinh xac!")


def test_decode():
    print("\n2. Kiem tra decode:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=1)

    assert ga.decode([3, 1, -1, 5, 2, -2, 4, 6, 7, 8]) == [[0, 3, 1, 0], [0, 5, 2, 0], [0, 4, 6, 7, 8, 0]]
    # Vach ngan o dau / cuoi / lien nhau -> bo tuyen rong
    assert ga.decode([-1, -2, 1, 2, 3, 4, 5, 6, 7, 8]) == [[0, 1, 2, 3, 4, 5, 6, 7, 8, 0]]
    assert ga.decode([1, 2, -1, -2, 3, 4, 5, 6, 7, 8]) == [[0, 1, 2, 0], [0, 3, 4, 5, 6, 7, 8, 0]]
    assert ga.decode([1, 2, 3, 4, 5, 6, 7, 8, -1, -2]) == [[0, 1, 2, 3, 4, 5, 6, 7, 8, 0]]
    print("-> decode hoat dong chinh xac!")


def test_random_population():
    print("\n3. Kiem tra sinh quan the ngau nhien:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=60, seed=7)
    population = ga._init_population()

    assert len(population) == 60
    for chrom in population:
        assert is_valid_chromosome(chrom, ga), f"Chromosome khong hop le: {chrom}"
        assert 9 not in chrom, "Tram sac khong duoc nam trong chromosome"

        solution = ga.decode(chrom)
        delivered = sorted(c for route in solution for c in route[1:-1])
        assert delivered == ga.customers, "Moi khach phai duoc giao dung 1 lan"
        assert len(solution) <= ga.num_drones
        assert all(route[0] == 0 and route[-1] == 0 for route in solution)

    assert len({tuple(c) for c in population}) > 1, "Quan the phai da dang"

    # Cung seed -> cung quan the
    ga2 = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=60, seed=7)
    assert ga2._init_population() == population, "Cung seed phai cho cung ket qua"
    print("-> Quan the ngau nhien hop le & tai lap duoc theo seed!")


def test_evaluate():
    print("\n4. Kiem tra danh gia fitness:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=3)
    chrom = ga._random_chromosome()

    fitness, cost, breakdown = ga._evaluate(chrom)
    expected = FitnessCalculator().evaluate_solution(ga.decode(chrom), dist, nodes)
    assert fitness > 0 and cost > 0
    assert (fitness, cost) == expected[:2], "Phai khop voi FitnessCalculator cua TV5"

    ga._evaluate(chrom)
    assert len(ga._cache) == 1, "Danh gia lai cung chromosome phai dung cache"

    print(f"-> Chromosome: {chrom}")
    print(f"-> Solution:   {ga.decode(chrom)}")
    print(f"-> Fitness={fitness:.4f}, Cost={cost:.2f}, Qua tai phat={breakdown['cap_penalty']:.2f}")
    print("-> Danh gia fitness hoat dong chinh xac!")


def test_tournament_select():
    print("\n5. Kiem tra chon loc Tournament:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=40, seed=11)
    population = ga._init_population()
    fitnesses = [ga._fitness(c) for c in population]
    best_idx = max(range(len(population)), key=lambda i: fitnesses[i])

    # Tournament bang ca quan the -> luon chon ca the tot nhat
    ga.tournament_size = len(population)
    assert ga._tournament_select(population, fitnesses) == population[best_idx]

    # Tournament 3 -> trung binh fitness duoc chon phai cao hon trung binh quan the
    ga.tournament_size = 3
    picked = [ga._fitness(ga._tournament_select(population, fitnesses)) for _ in range(500)]
    avg_picked = sum(picked) / len(picked)
    avg_pop = sum(fitnesses) / len(fitnesses)
    assert avg_picked > avg_pop, "Tournament phai uu tien ca the tot"
    print(f"-> Fitness TB duoc chon={avg_picked:.4f} > TB quan the={avg_pop:.4f}")
    print("-> Tournament selection hoat dong chinh xac!")


def test_order_crossover():
    print("\n6. Kiem tra lai ghep OX:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=5)

    # Vi du kinh dien: giu doan [3..6] cua p1, dien phan con lai theo thu tu p2 tu vi tri 7
    p1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    p2 = [9, 3, 7, 8, 2, 6, 5, 1, 4]
    assert ga._order_crossover(p1, p2, cut=(3, 6)) == [3, 8, 2, 4, 5, 6, 7, 1, 9]

    # Doan cat phu ca chuoi -> con = p1
    assert ga._order_crossover(p1, p2, cut=(0, 8)) == p1

    # 200 lan ngau nhien tren chromosome that (co vach ngan) -> con luon hop le
    for _ in range(200):
        c1, c2 = ga._random_chromosome(), ga._random_chromosome()
        child = ga._order_crossover(c1, c2)
        assert is_valid_chromosome(child, ga), f"Con OX khong hop le: {child}"
    print("-> OX luon sinh hoan vi hop le (khong trung / thieu don hang)!")


def test_swap_mutation():
    print("\n7. Kiem tra dot bien Swap:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=9)
    original = ga._random_chromosome()

    ga.mutation_rate = 1.0
    mutant = ga._swap_mutation(original)
    assert is_valid_chromosome(mutant, ga)
    diff = [i for i in range(len(original)) if original[i] != mutant[i]]
    assert len(diff) == 2, "Swap phai doi cho dung 2 vi tri"
    assert mutant is not original, "Phai tra ve ban sao, khong sua cha"

    ga.mutation_rate = 0.0
    assert ga._swap_mutation(original) == original, "mutation_rate=0 -> khong doi"
    print("-> Swap mutation hoat dong chinh xac!")


if __name__ == "__main__":
    print("=== KIEM THU DOC LAP MODULE THANH VIEN 1 (GA) ===")
    test_init_and_validation()
    test_decode()
    test_random_population()
    test_evaluate()
    test_tournament_select()
    test_order_crossover()
    test_swap_mutation()
    print("\n=== TAT CA UNIT TEST CHO THANH VIEN 1 DA VUOT QUA! ===")
