import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from framework.evolutionary import EvolutionaryAlgorithm
from NSGAII.selection import nsga_pareto_selection
from NSGAII.fitness import nsga_atop_fitness_calculation
from NSGAII.mutation import nsga_atop_mutation


def nsga_algorithm_factory():
    iteration_limits = 100
    return EvolutionaryAlgorithm(nsga_atop_mutation, nsga_pareto_selection, nsga_atop_fitness_calculation, iteration_limits)


if __name__ == "__main__":
    nsga_algorithm_factory()