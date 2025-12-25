from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from simulator.networkcost_scorer import network_cost
from NSGAII.solution import NSGASolution

def main():
    # topology, connection_blocks, intra_blueprint = build_simple_topology()
    total_gpus = 16
    total_layers = 2
    topology, connection_blocks, intra_blueprint = construct_topology(total_gpus, total_layers, generator = lambda x, y, z: [x, y, z])

    from NSGAII.solution import NetTopology, NSGASolution
    net_topo = NetTopology(topology, connection_blocks, intra_blueprint)
    solution = NSGASolution(net_topo, fitness_score=None)
    cost = network_cost(solution)
    print(f"Calculated network cost: {cost}")

if __name__ == "__main__":
    main()