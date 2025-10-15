import random
from framework.evolutionary import EvolutionaryAlgorithm
from NSGAII.selection import nsga_pareto_selection
from NSGAII.solution import NSGASolution, NetTopology
from NSGAII.fitness import nsga_atop_fitness_calculation
from NSGAII.mutation import nsga_atop_mutation, solution_generater
from generator.network import construct_topology


total_gpus = 160
max_layers = random.randint(1, 5)
max_dimensions = random.randint(1, 5)


def initilize_solutions():
    global total_gpus, max_layers, max_dimensions
    NetTopology.TOTAL_GPUS = total_gpus
    NetTopology.MAX_LAYERS = max_layers
    NetTopology.MAX_DIMENSION = max_dimensions
    cur_population = list()
    initial_solutions = 100
    for _ in range(initial_solutions):
        solution = construct_topology(total_gpus, max_layers, max_dimensions, solution_generater)
        cur_population.append(solution)
    return cur_population


def entry():
    atop = EvolutionaryAlgorithm(nsga_atop_mutation, nsga_pareto_selection, nsga_atop_fitness_calculation, 100000)
    atop.optimize(initilize_solutions())


if __name__ == "__main__":
    entry()