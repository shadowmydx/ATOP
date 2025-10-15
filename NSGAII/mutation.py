import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from NSGAII.solution import NSGASolution, solution_generater, NetTopology
from generator.network import construct_topology


def nsga_atop_mutation(solution):
    new_child = construct_topology(NetTopology.TOTAL_GPUS, NetTopology.MAX_LAYERS, NetTopology.MAX_DIMENSION, solution_generater)
    return new_child