from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from simulator.faulttolerance_scorer import fault_tolerance_score
from NSGAII.solution import NSGASolution


def main():
    # topology, connection_blocks, intra_blueprint = build_simple_topology()
    total_gpus = 128
    total_layers = 2
    topology, connection_blocks, intra_blueprint = construct_topology(total_gpus, total_layers, generator = lambda x, y, z: [x, y, z])

    from NSGAII.solution import NetTopology, NSGASolution
    net_topo = NetTopology(topology, connection_blocks, intra_blueprint)
    solution = NSGASolution(net_topo, fitness_score=None)
    import time
    start_time = time.time()
    score = fault_tolerance_score(solution)
    elapsed = time.time() - start_time
    print(f"Calculated fault tolerance score: {score}")
    print(f"Elapsed time: {elapsed:.6f} seconds")

if __name__ == "__main__":
    main()