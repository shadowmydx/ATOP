from framework.evolutionary import EvolutionaryAlgorithm
from NSGAII.selection import nsga_pareto_selection
from NSGAII.solution import NSGASolution
from NSGAII.fitness import nsga_atop_fitness_calculation
from NSGAII.mutation import nsga_atop_mutation
from generator.network import construct_topology


def entry():
    atop = EvolutionaryAlgorithm(nsga_atop_mutation, nsga_pareto_selection, nsga_atop_fitness_calculation, 100000)
    atop.optimize([])


if __name__ == "__main__":
    entry()