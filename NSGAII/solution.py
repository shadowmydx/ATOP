class NetTopology:

    def __init__(self):
        pass


class NSGASolution:

    def __init__(self, item, fitness_score):
        self.item = item
        self.fitness_score = fitness_score
        self.crowding_distance = 0
    
    def get_item(self):
        return self.item
    
    def get_fitness_score(self):
        return self.fitness_score
    
    def set_crowding_distance(self, distance):
        self.crowding_distance = distance

    def get_crowding_distance(self, distance):
        return self.crowding_distance