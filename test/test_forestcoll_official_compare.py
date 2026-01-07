import sys
import time
from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from simulator.forestcoll_scorer import calculate_optimality_star, forestcoll_official_score, forestcoll_score
from NSGAII.solution import NetTopology, NSGASolution

def build_simple_topology():
    # 4 GPUs, 4 switches, each GPU connects to all switches
    gpus = [GraphNode(NodeType.GPU) for _ in range(4)]
    switches = [GraphNode(NodeType.SWITCH) for _ in range(4)]
    # Assign readable node_id for test clarity
    for i, gpu in enumerate(gpus):
        gpu.node_id = f'c{i+1}'
    for i, sw in enumerate(switches):
        sw.node_id = f'sw{i+1}'
    for gpu in gpus:
        gpu.siblings = {sw.node_id: sw for sw in switches}
    for sw in switches:
        sw.siblings = {gpu.node_id: gpu for gpu in gpus}
    topology = [gpus, switches]
    # Layer lookup: 0 for GPUs, 1 for switches
    layer_lookup = {gpu.node_id: 0 for gpu in gpus}
    layer_lookup.update({sw.node_id: 1 for sw in switches})
    intra_blueprint = [ {'Bii': 10}, {'Bii': 0} ]
    connection_blocks = { (0,1): {'b_ij': 5}, (1,0): {'b_ij': 5} }
    return topology, connection_blocks, intra_blueprint

def main():
    # topology, connection_blocks, intra_blueprint = build_simple_topology()
    total_gpus = 128
    total_layers = 2
    num_topo = 1
    solutions = []
    for _ in range(num_topo):
        topology,connection_blocks,intra_blueprint  = construct_topology(total_gpus, total_layers, generator = lambda x,y,z: [x,y,z])
        net_topo = NetTopology(topology, connection_blocks, intra_blueprint)
        solution = NSGASolution(net_topo, fitness_score=None)
        solutions.append(solution)

    myimpl_scores = {}
    start_opt = time.time()
    for i in range(num_topo):
        solution = solutions[i]
        score_optimality = float(forestcoll_score(solution))
        myimpl_scores[i] = score_optimality
    end_opt = time.time()
    print(f"my implementation runtime: {end_opt - start_opt:.6f} seconds")

    # Score from forestcoll_bf_calc with timing
    official_scores = {}
    start_bf = time.time()
    for i in range(num_topo):
        solution = solutions[i]
        score_bf = forestcoll_official_score(solution)
        official_scores[i] = score_bf
    end_bf = time.time()
    print(f"forestcoll_official_score runtime: {end_bf - start_bf:.6f}")

    # Order y values, showing the keys order
    ordered_myimpl = sorted(myimpl_scores.items(), key=lambda x: x[1],reverse=True)
    ordered_official = sorted(official_scores.items(), key=lambda x: x[1],reverse=False)
    print("Order of myimpl_scores by value (key, value):", ordered_myimpl)
    print("Order of official_scores by value (key, value):", ordered_official)
    
    

if __name__ == "__main__":
    main()