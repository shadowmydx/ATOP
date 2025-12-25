import random
from framework.evolutionary import EvolutionaryAlgorithm
from NSGAII.selection import nsga_pareto_selection
from NSGAII.solution import NSGASolution, NetTopology
from NSGAII.fitness import nsga_atop_fitness_calculation
from NSGAII.mutation import nsga_atop_mutation, solution_generater
from generator.network import construct_topology
import os, pickle, csv
from datetime import datetime


total_gpus = 16
max_layers = random.randint(1, 5)
max_dimensions = random.randint(1, 5)


def save_results(solutions, save_dir="results"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pkl_path = os.path.join(save_dir, f"solutions_{timestamp}.pkl")
    csv_path = os.path.join(save_dir, f"summary_{timestamp}.csv")

    print(f"\n[Action] Saving {len(solutions)} solutions to {pkl_path}...")
    try:
        with open(pkl_path, "wb") as f:
            pickle.dump(solutions, f)
        print(">>> Pickle save successful!")
    except Exception as e:
        print(f">>> Pickle save failed: {e}")

    print(f"[Action] Exporting summary to {csv_path}...")
    try:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Headers: ID and the components of your fitness_score tuple
            writer.writerow(['Index', 'Latency', 'Cost', 'Extra_Metric'])
            for i, sol in enumerate(solutions):
                # Unpack (latency, cost, 0)
                l, c, m = sol.fitness_score
                writer.writerow([i, l, c, m])
        print(">>> Summary export successful!")
    except Exception as e:
        print(f">>> Summary export failed: {e}")


def initilize_solutions():
    global total_gpus, max_layers, max_dimensions
    NetTopology.TOTAL_GPUS = total_gpus
    NetTopology.MAX_LAYERS = max_layers
    NetTopology.MAX_DIMENSION = max_dimensions
    cur_population = list()
    initial_solutions = 3
    for _ in range(initial_solutions):
        solution = construct_topology(total_gpus, max_layers, max_dimensions, solution_generater)
        cur_population.append(solution)
    return cur_population


def entry():
    atop = EvolutionaryAlgorithm(nsga_atop_mutation, nsga_pareto_selection, nsga_atop_fitness_calculation, 3)
    final_solutions = atop.optimize(initilize_solutions())
    save_results(final_solutions)


if __name__ == "__main__":
    entry()