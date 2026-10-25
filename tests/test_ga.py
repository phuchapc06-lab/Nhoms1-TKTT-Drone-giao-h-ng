"""
Unit test kiem thu doc lap cho module GA cua Thanh vien 1 (GeneticAlgorithm).
"""
import sys
import os
import math
import threading
import numpy as np

# Dam bao ho tro tieng Viet tren Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Them duong dan src vao he thong
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import matplotlib.pyplot as plt

from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.fitness import FitnessCalculator
from algorithms.energy_manager import EnergyManager
from utils.visualizer import UAVVisualizer


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
                       {"num_drones": 2, "mutation_rate": 1.5}, {"num_drones": 2, "pop_size": 10, "elitism": 10},
                       {"num_drones": 2, "constraint_penalty_factor": 0.5}):
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
    assert (cost, breakdown) == expected[1:], "cost & breakdown phai khop voi FitnessCalculator cua TV5"
    # Chon loc dung phat vi pham nang hon (x constraint_penalty_factor)
    penalized = cost + (ga.constraint_penalty_factor - 1) * breakdown["cap_penalty"]
    assert math.isclose(fitness, 1000.0 / (penalized + 1.0))
    # factor = 1 -> dung nguyen fitness cua TV5
    plain = GeneticAlgorithm(nodes, dist, num_drones=3, constraint_penalty_factor=1.0)
    assert plain._evaluate(chrom)[:2] == expected[:2], "factor=1 phai trung fitness cua TV5"

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


def check_solution(solution, ga):
    delivered = sorted(c for route in solution for c in route[1:-1])
    assert delivered == ga.customers, "Moi khach phai duoc giao dung 1 lan"
    assert len(solution) <= ga.num_drones, "So tuyen khong duoc vuot qua K"
    assert all(route[0] == 0 and route[-1] == 0 for route in solution), "Tuyen phai bat dau & ket thuc o Depot"


def test_evolve():
    print("\n8. Kiem tra vong lap tien hoa (evolve):")
    nodes, dist = make_mock_data()

    # Quan the ban dau (cung seed -> trung voi quan the dau tien ma evolve() se tao)
    ref = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=80, seed=42)
    initial_costs = [ref._evaluate(c)[1] for c in ref._init_population()]

    ga = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=80, generations=300, seed=42)
    solution, best_fitness, history = ga.evolve()

    check_solution(solution, ga)
    assert len(history) == ga.generations, "Moi the he ghi 1 diem vao history"
    assert all(history[i] <= history[i + 1] for i in range(len(history) - 1)), "History khong duoc giam"
    assert best_fitness == history[-1] == ga.best_fitness
    assert ga.best_cost <= min(initial_costs), "GA phai tot hon ca the tot nhat ban dau"
    assert ga.best_breakdown["cap_penalty"] == 0, "Tong demand 13.5kg <= 3 x 5kg -> GA phai het qua tai"
    assert ga.runtime > 0

    recomputed = FitnessCalculator().evaluate_solution(solution, dist, nodes)
    assert math.isclose(recomputed[1], ga.best_cost), "best_cost phai khop voi FitnessCalculator"

    avg0 = sum(initial_costs) / len(initial_costs)
    print(f"-> Cost quan the ban dau: TB={avg0:.2f}, tot nhat={min(initial_costs):.2f}")
    print(f"-> Cost GA sau {ga.generations} the he: {ga.best_cost:.2f} (giam {100 * (1 - ga.best_cost / avg0):.1f}% so voi TB)")
    print(f"-> Chi tiet: {', '.join(f'{k}={v:.2f}' for k, v in ga.best_breakdown.items())}")
    print(f"-> Loi giai: {solution}")
    print(f"-> Thoi gian chay: {ga.runtime:.2f}s")

    # Truong hop bien K = 1 (khong co vach ngan) van chay duoc
    ga1 = GeneticAlgorithm(nodes, dist, num_drones=1, pop_size=20, generations=30, seed=1)
    solution1, _, _ = ga1.evolve()
    assert len(solution1) == 1
    check_solution(solution1, ga1)

    # Ket noi voi Visualizer cua TV5 (khong bat cua so)
    visualizer = UAVVisualizer(grid_size=(60, 60))
    fig, _ = visualizer.plot_multi_uav_routes(nodes, [], solution, show=False)
    fig2, _ = visualizer.plot_convergence_curve(history, show=False)
    assert fig is not None and fig2 is not None
    plt.close("all")
    print("-> evolve() hoat dong chinh xac & ket noi duoc voi Visualizer!")


def test_seed_reproducible():
    print("\n9. Kiem tra tai lap ket qua theo seed:")
    nodes, dist = make_mock_data()
    run1 = GeneticAlgorithm(nodes, dist, num_drones=3, generations=50, seed=123).evolve()
    run2 = GeneticAlgorithm(nodes, dist, num_drones=3, generations=50, seed=123).evolve()
    assert run1 == run2, "Cung seed phai cho cung loi giai & history"
    print("-> Cung seed -> cung ket qua!")


def test_encode_and_initial_solutions():
    print("\n10. Kiem tra encode & khoi tao quan the tu loi giai co san:")
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, seed=4)

    # encode la nguoc cua decode; bo qua tram sac (9) neu co trong tuyen
    solution = [[0, 3, 1, 0], [0, 5, 9, 2, 0], [0, 4, 6, 7, 8, 0]]
    chrom = ga.encode(solution)
    assert chrom == [3, 1, -1, 5, 2, -2, 4, 6, 7, 8]
    assert ga.decode(chrom) == [[0, 3, 1, 0], [0, 5, 2, 0], [0, 4, 6, 7, 8, 0]]
    # It tuyen hon K -> vach ngan con thua dat o cuoi
    assert ga.encode([[0, 1, 2, 3, 4, 5, 6, 7, 8, 0]]) == [1, 2, 3, 4, 5, 6, 7, 8, -1, -2]

    for bad in ([[0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 5, 6, 7, 8, 0]],  # 4 tuyen > K = 3
                [[0, 1, 2, 3, 0]],                                       # thieu khach
                [[0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 0]]):                    # trung khach
        try:
            ga.encode(bad)
            assert False, f"Phai bao loi voi loi giai {bad}"
        except ValueError:
            pass

    # Ca the dau tien cua quan the la loi giai co san; elitism -> GA khong bao gio te hon no
    seeded = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=30, generations=40,
                              initial_solutions=[solution], seed=4)
    population = seeded._init_population()
    assert population[0] == chrom and len(population) == 30
    assert all(is_valid_chromosome(c, seeded) for c in population)
    seeded_cost = FitnessCalculator().evaluate_solution(seeded.decode(chrom), dist, nodes)[1]
    seeded.evolve()
    assert seeded.best_cost <= seeded_cost, "GA khoi tao tu loi giai co san khong duoc te hon loi giai do"
    print(f"-> Cost loi giai co san={seeded_cost:.2f} -> GA={seeded.best_cost:.2f}")
    print("-> encode & initial_solutions hoat dong chinh xac!")


def test_energy_manager_with_charging():
    print("\n11. Kiem tra danh gia co EnergyManager (cham diem sau khi chen tram sac):")
    nodes, dist = make_mock_data()
    em = EnergyManager(battery_capacity=80.0)  # pin nho -> tuyen dai phai ghe tram sac 9
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, energy_manager=em, generations=60, seed=2)

    chrom = ga.encode([[0, 1, 6, 2, 3, 0], [0, 7, 8, 0], [0, 4, 5, 0]])
    raw = ga.decode(chrom)
    repaired = [em.repair_route_with_charging(r, dist, nodes)[0] for r in raw]
    assert any(9 in r for r in repaired), "Pin 80Wh: phai co tuyen can ghe tram sac 9"

    _, cost, breakdown = ga._evaluate(chrom)
    expected = FitnessCalculator().evaluate_solution(repaired, dist, nodes, em)
    assert (cost, breakdown) == expected[1:], "Phai cham diem tuyen da chen tram sac"
    raw_cost = FitnessCalculator().evaluate_solution(raw, dist, nodes, em)[1]
    print(f"-> Cost chua chen tram sac={raw_cost:.2f} (bi phat thieu pin) -> sau khi chen={cost:.2f}")

    # Hoi quy loi vong lap vo han cua repair_route_with_charging: tu tram sac 9 (pin day) cho 12kg
    # khong toi duoc khach 3 -> truoc day chen tram 9 mai mai
    result = {}
    worker = threading.Thread(
        target=lambda: result.update(r=em.repair_route_with_charging([0, 5, 3, 1, 2, 4, 6, 7, 8, 0], dist, nodes)),
        daemon=True
    )
    worker.start()
    worker.join(5)
    assert "r" in result, "repair_route_with_charging bi treo (vong lap vo han)"
    assert result["r"][2] is False, "Tuyen khong the bay toi phai bi danh dau khong kha thi"

    solution, _, _ = ga.evolve()
    check_solution(solution, ga)  # GA tra tuyen chua co tram sac, pipeline tu chen sau
    print("-> Danh gia sau khi chen tram sac hoat dong chinh xac!")


def test_parallel_matches_sequential():
    print("\n12. Kiem tra danh gia song song (num_workers) cho ket qua trung chay tuan tu:")
    nodes, dist = make_mock_data()

    try:
        GeneticAlgorithm(nodes, dist, num_drones=3, num_workers=0)
        assert False, "num_workers=0 phai bao loi"
    except ValueError:
        pass

    for energy_manager in (None, EnergyManager(battery_capacity=80.0)):
        kwargs = dict(num_drones=3, pop_size=30, generations=25, energy_manager=energy_manager, seed=7)
        seq = GeneticAlgorithm(nodes, dist, **kwargs)
        par = GeneticAlgorithm(nodes, dist, num_workers=2, **kwargs)
        assert seq.evolve() == par.evolve(), "Cung seed: song song phai trung tuan tu (loi giai + history)"
        assert (seq.best_cost, seq.best_breakdown) == (par.best_cost, par.best_breakdown)
        print(f"-> EnergyManager={'co' if energy_manager else 'khong'}: cost={par.best_cost:.2f}, "
              f"tuan tu {seq.runtime:.2f}s / song song 2 tien trinh {par.runtime:.2f}s")

    # K = 1 (khong co vach ngan) van chay song song duoc
    solution, _, _ = GeneticAlgorithm(nodes, dist, num_drones=1, pop_size=10, generations=5,
                                      num_workers=2, seed=1).evolve()
    assert len(solution) == 1
    print("-> Danh gia song song hoat dong chinh xac!")


def save_demo_plots(out_dir):
    """Chay GA tren du lieu gia lap va luu hinh tuyen bay + duong hoi tu (de xem bang mat)."""
    nodes, dist = make_mock_data()
    ga = GeneticAlgorithm(nodes, dist, num_drones=3, pop_size=80, generations=300, seed=42)
    solution, _, history = ga.evolve()

    os.makedirs(out_dir, exist_ok=True)
    visualizer = UAVVisualizer(grid_size=(60, 60))
    visualizer.plot_multi_uav_routes(
        nodes, [], solution,
        title=f"GA demo - du lieu gia lap 8 khach, 3 UAV (cost={ga.best_cost:.1f})",
        save_path=os.path.join(out_dir, "ga_demo_routes.png"), show=False
    )
    visualizer.plot_convergence_curve(
        history, title="GA demo - duong cong hoi tu",
        save_path=os.path.join(out_dir, "ga_demo_convergence.png"), show=False
    )
    plt.close("all")


if __name__ == "__main__":
    print("=== KIEM THU DOC LAP MODULE THANH VIEN 1 (GA) ===")
    test_init_and_validation()
    test_decode()
    test_random_population()
    test_evaluate()
    test_tournament_select()
    test_order_crossover()
    test_swap_mutation()
    test_evolve()
    test_seed_reproducible()
    test_encode_and_initial_solutions()
    test_energy_manager_with_charging()
    test_parallel_matches_sequential()

    # Hinh demo luu vao data/processed/ (thu muc nay da bi .gitignore)
    save_demo_plots(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed")))
    print("\n=== TAT CA UNIT TEST CHO THANH VIEN 1 DA VUOT QUA! ===")
