import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from NSGAII.solution import NSGASolution
from util.process_pool import ProcessPool


def nsga_atop_fitness_calculation(population):
    pass