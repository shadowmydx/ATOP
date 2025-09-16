import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from framework.evolutionary import EvolutionaryAlgorithm



class NSGASolution:

    def __init__(self, item, fitness_score):
        self.item = item
        self.fitness_score = fitness_score
    
    def get_item(self):
        return self.item
    
    def get_fitness_score(self):
        return self.fitness_score


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


def test_pareto_sort():
    test_solutions = [
        NSGASolution("A", (10, 5)),    
        NSGASolution("B", (8, 8)),     
        NSGASolution("C", (5, 12)),    
        NSGASolution("D", (15, 3)),    
        NSGASolution("E", (3, 10)),    
        NSGASolution("F", (8, 2)),     
        NSGASolution("G", (12, 4)),    
        NSGASolution("H", (7, 6)),
        NSGASolution("I", (6, 1))     
    ]
    test_result = nsga_pareto_sort(test_solutions)
    for each_item in test_result:
        for each_solution in each_item:
            print(each_solution.get_fitness_score())
        print("one front end.")


if __name__ == "__main__":
    test_pareto_sort()