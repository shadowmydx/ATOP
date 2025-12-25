import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from NSGAII.solution import NSGASolution
from util.process_pool import ProcessPool
from simulator.forestcoll_scorer import forestcoll_score
from simulator.networkcost_scorer import network_cost


def nsga_atop_fitness_calculation(population):
    for solution in population:
        fitness = {}
        fitness['latency'] = forestcoll_score(solution)
        fitness['cost'] = network_cost(solution)
        solution.fitness_score = fitness
    
    return population