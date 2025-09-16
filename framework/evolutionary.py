import optimizer


class EvolutionaryAlgorithm(optimizer.Optimizer):

    def __init__(self, mutator, selector, fitness, iteration_limits):
        super().__init__()
        self.mutator = mutator
        self.selector = selector
        self.fitness = fitness
        self.iteration_limits = iteration_limits

    def optimize(self, init_solutions):
        start_index = 0
        current_populations = init_solutions
        for each_solution in current_populations:
            self.fitness(each_solution)
        while start_index <= self.iteration_limits:
            children_solutions = list()
            for each_solution in current_populations:
                child_solution = self.mutator(each_solution)
                child_solution = self.fitness(child_solution)
                children_solutions.append(child_solution)
            current_populations += children_solutions
            current_populations = self.selector(current_populations)
        return super().optimize(init_solutions)