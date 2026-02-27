import os, csv, pickle
from framework import optimizer
from datetime import datetime
from tqdm import tqdm

class EvolutionaryAlgorithm(optimizer.Optimizer):

    def __init__(self, mutator, selector, fitness, iteration_limits):
        super().__init__()
        self.mutator = mutator
        self.selector = selector
        self.fitness = fitness
        self.iteration_limits = iteration_limits

    def optimize(self, init_solutions):
        current_populations = init_solutions
        population_size = len(current_populations)
        self.fitness(current_populations)

        for _ in tqdm(range(self.iteration_limits), desc="Optimizing Generations"):
            children_solutions = list()
            for each_solution in current_populations:
                child_solution = self.mutator(each_solution)                
                children_solutions.append(child_solution)            
            self.fitness(children_solutions)
            current_populations += children_solutions
            current_populations = self.selector(current_populations, population_size)    
        return current_populations
    
    def optimize_observations(self, init_solutions, parallelism, gpus, task_id):
        current_populations = init_solutions
        population_size = len(current_populations)
        self.fitness(current_populations, parallelism)

        for itr in tqdm(range(self.iteration_limits), desc="Optimizing Generations"):
            children_solutions = list()
            for each_solution in current_populations:
                child_solution = self.mutator(each_solution)                
                children_solutions.append(child_solution)            
            self.fitness(children_solutions, parallelism)
            current_populations += children_solutions
            current_populations = self.selector(current_populations, population_size) 
            save_results(current_populations, gpus, itr, task_id)   
        return current_populations
    

def save_results(solutions, total_gpus, iteration, task_id, save_dir="results"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    pkl_path = os.path.join(save_dir, f"solutions_task_{task_id}_iter_{iteration}.pkl")
    csv_path = os.path.join(save_dir, f"summary_task_{task_id}_{total_gpus}.csv")

    print(f"\n[Iteration {iteration}] Saving {len(solutions)} solutions to {pkl_path}...")
    try:
        with open(pkl_path, "wb") as f:
            pickle.dump(solutions, f)
        print(">>> Pickle save successful!")
    except Exception as e:
        print(f">>> Pickle save failed: {e}")

    print(f"[Iteration {iteration}] Appending summary to {csv_path}...")
    try:
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            # Headers: ID and the components of your fitness_score tuple
           
            writer.writerow(['Index', 'Latency', 'Cost', 'Extra_Metric', 'Iteration_', iteration,current_time])
            for i, sol in enumerate(solutions):
                # Unpack (latency, cost, 0)
                l, c, m = sol.fitness_score
                writer.writerow([i, l, c, m])
        print(">>> Summary export successful!")
    except Exception as e:
        print(f">>> Summary export failed: {e}")