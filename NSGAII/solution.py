class NetTopology:

    TOTAL_GPUS = 0
    MAX_LAYERS = 0
    MAX_DIMENSION = 0

    def __init__(self, topology, connection_blocks, blueprint):
        self.topology = topology
        self.connection_blocks = connection_blocks
        self.blueprint = blueprint


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
    

def solution_generater(topology, connection_blocks, blueprint):
    cur_topology = NetTopology(topology, connection_blocks, blueprint)
    solution = NSGASolution(cur_topology, (0, 0, 0))
    return solution