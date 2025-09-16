from framework.evolutionary import EvolutionaryAlgorithm



class NSGASolution:

    def __init__(self, item, fitness_score):
        self.item = item
        self.fitness_score = fitness_score
    
    def get_item(self):
        return self.item
    
    def get_fitness_score(self):
        return self.fitness_score


def nsga_pareto_sort(population):
    num_individuals = len(population)
    dominating_sets = [set() for _ in range(num_individuals)]
    dominated_counts = [0] * num_individuals
    fronts = [[]]
    