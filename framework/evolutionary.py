from framework import optimizer
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