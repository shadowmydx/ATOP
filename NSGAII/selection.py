import sys
import os
import pickle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from NSGAII.solution import NSGASolution


def nsga_pareto_sort(population):
    num_individuals = len(population)
    dominating_sets = [set() for _ in range(num_individuals)]
    dominated_counts = [0] * num_individuals
    fronts = [[]]
    for i in range(num_individuals):
        for j in range(num_individuals):
            if i == j:
                continue
            solution_a = population[i].get_fitness_score()
            solution_b = population[j].get_fitness_score()
            is_i_dominant = all(solution_a[k] >= solution_b[k] for k in range(len(population[0].get_fitness_score()))) and \
                            any(solution_a[k] > solution_b[k] for k in range(len(population[0].get_fitness_score())))

            if is_i_dominant:
                dominating_sets[i].add(j)
            else:
                is_j_dominant = all(solution_b[k] >= solution_a[k] for k in range(len(population[0].get_fitness_score()))) and \
                                any(solution_b[k] > solution_a[k] for k in range(len(population[0].get_fitness_score())))
                if is_j_dominant:
                    dominated_counts[i] += 1
    for i in range(num_individuals):
        if dominated_counts[i] == 0:
            fronts[0].append(i)
    front_index = 0
    while fronts[front_index]:
        next_front = []
        for p_idx in fronts[front_index]:
            for q_idx in dominating_sets[p_idx]:
                dominated_counts[q_idx] -= 1
                if dominated_counts[q_idx] == 0:
                    next_front.append(q_idx)
        front_index += 1
        fronts.append(next_front)
    return [[population[i] for i in sublist] for sublist in fronts[: -1]]


def sort_by_crowding_distance(front):
    if not front or len(front) <= 2:
        for sol in front:
            sol.crowding_distance = float('inf')
        return
    num_objectives = len(front[0].get_fitness_score())
    num_solutions = len(front)
    for sol in front:
        sol.crowding_distance = 0
    for obj_idx in range(num_objectives):
        front.sort(key=lambda sol: sol.get_fitness_score()[obj_idx])
        front[0].crowding_distance = float('inf')
        front[num_solutions - 1].crowding_distance = float('inf')
        obj_min = front[0].get_fitness_score()[obj_idx]
        obj_max = front[num_solutions - 1].get_fitness_score()[obj_idx]
        if obj_max - obj_min == 0:
            continue
        for i in range(1, num_solutions - 1):
            front[i].crowding_distance += \
                (front[i+1].get_fitness_score()[obj_idx] - front[i-1].get_fitness_score()[obj_idx]) / (obj_max - obj_min)
    front.sort(key=lambda sol: sol.crowding_distance, reverse=True)
    return front


def nsga_pareto_selection(population, limitation):
    total_fronts = nsga_pareto_sort(population)
    new_population = list()
    cur_solution = 0
    for each_front in total_fronts:
        sort_by_crowding_distance(each_front)
        for each_sol in each_front:
            if cur_solution < limitation:
                new_population.append(each_sol)
                cur_solution += 1
    return new_population


def test_pareto_sort():
    test_solutions = [
        NSGASolution("A", (10, 5, 3)),    
        NSGASolution("B", (8, 8, 1)),     
        NSGASolution("C", (5, 12, 1)),    
        NSGASolution("D", (15, 3, 2)),    
        NSGASolution("E", (3, 10, 1)),    
        NSGASolution("F", (8, 2, 2)),     
        NSGASolution("G", (12, 4, 3)),    
        NSGASolution("H", (7, 6, 1)),
        NSGASolution("I", (6, 1, 2))     
    ]
    test_result = nsga_pareto_sort(test_solutions)
    for each_item in test_result:
        for each_solution in each_item:
            print(each_solution.get_fitness_score())
        print("one front end.")
    test_population = nsga_pareto_selection(test_solutions, 3)
    for each_item in test_population:
        print(each_item.get_fitness_score())


def test_merge_and_pareto_from_pickle(f1, f2):
    with open(f1, 'rb') as fp: list1 = pickle.load(fp)
    with open(f2, 'rb') as fp: list2 = pickle.load(fp)
    
    merged = list1 + list2
    print(f"Merged: {len(merged)} solutions")

    print("--- Pareto Sort ---")
    fronts = nsga_pareto_sort(merged)
    for i, front in enumerate(fronts, 1):
        print(f"Front {i}:")
        for sol in front: print(f"  {sol.get_fitness_score()}")
        print("one front end.")

    print(f"\n--- Select Top {len(list1)} ---")
    selected = nsga_pareto_selection(merged, len(list1))
    for sol in selected: print(f"  {sol.get_fitness_score()}")


if __name__ == "__main__":
    #test_pareto_sort()
    test_merge_and_pareto_from_pickle("iter_378.pkl", "iter_379.pkl")