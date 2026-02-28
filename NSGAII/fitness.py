import sys
import os
import math
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from NSGAII.solution import NSGASolution
from util.process_pool import ProcessPool
from simulator.forestcoll_scorer import forestcoll_score
from simulator.networkcost_scorer import network_cost
from simulator.faulttolerance_scorer import fault_tolerance_score
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from reward.reward_chain import RewardChain
from reward.topology_feasible import is_solution_feasible


def evaluate_single_solution(solution):
    latency = - forestcoll_score(solution)
    cost = - network_cost(solution)
    faulttolerance = -fault_tolerance_score(solution)
    
    if math.isinf(latency) or cost == 0 or math.isinf(faulttolerance):
        return (-float('inf'), -float('inf'), -float('inf'))
    return (latency, cost, faulttolerance)


def nsga_atop_fitness_calculation_paralleism(population, parallelism):
    total_size = len(population)
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        future_to_sol = {executor.submit(evaluate_single_solution, sol): sol for sol in population}
        with tqdm(total=total_size, desc="  └─ Evaluating Individuals", leave=False, position=1) as pbar:
            for future in as_completed(future_to_sol):
                solution = future_to_sol[future]
                try:
                    score = future.result()
                    solution.fitness_score = score
                except Exception as e:
                    print(f"\n[Error] Individual evaluation failed: {e}")
                finally:
                    pbar.update(1)
    return population


def evaluate_feasible_solution(solution):
    cur_chain = RewardChain()
    cur_chain.add_reward_function(is_solution_feasible, "feasible")
    result = cur_chain.default_reward_processing(solution)
    return (result, result, result)


def nsga_atop_feasible_fitness_calculation_paralleism(population, parallelism):
    total_size = len(population)
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        future_to_sol = {executor.submit(evaluate_feasible_solution, sol): sol for sol in population}
        with tqdm(total=total_size, desc="  └─ Evaluating Individuals", leave=False, position=1) as pbar:
            for future in as_completed(future_to_sol):
                solution = future_to_sol[future]
                try:
                    score = future.result()
                    solution.fitness_score = score
                except Exception as e:
                    print(f"\n[Error] Individual evaluation failed: {e}")
                finally:
                    pbar.update(1)
    return population


def nsga_atop_fitness_calculation(population):
    #for solution in population:
    #    fitness = {}
    #    fitness['latency'] = forestcoll_score(solution)
    #    fitness['cost'] = network_cost(solution)
    #    solution.fitness_score = (fitness['latency'], fitness['cost'], 0)

    #with ProcessPoolExecutor() as executor:
    #    scores = list(executor.map(evaluate_single_solution, population))
    #for solution, score in zip(population, scores):
    #    solution.fitness_score = score

    total_size = len(population)
    fixed_parallelism = 8
    with ProcessPoolExecutor(max_workers=fixed_parallelism) as executor:
        future_to_sol = {executor.submit(evaluate_single_solution, sol): sol for sol in population}
        with tqdm(total=total_size, desc="  └─ Evaluating Individuals", leave=False, position=1) as pbar:
            for future in as_completed(future_to_sol):
                solution = future_to_sol[future]
                try:
                    score = future.result()
                    solution.fitness_score = score
                except Exception as e:
                    print(f"\n[Error] Individual evaluation failed: {e}")
                finally:
                    pbar.update(1)
    return population