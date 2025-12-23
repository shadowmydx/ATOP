import sys
import time
from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from simulator.forestcoll_scorer import calculate_optimality_star

def calc_xstar_onesol(nodes,edges,compute_nodes,S):
    in_compute_nodes = 0
    for node in S:
        if node in compute_nodes:
            in_compute_nodes +=1
    out_bandwidth = 0
    for p,bandwidth in edges.items():
        u,v = p
        if u in S and v not in S:
            out_bandwidth += bandwidth
    if out_bandwidth ==0:
        return -100
    return in_compute_nodes / out_bandwidth

def forestcoll_bf_calc(nodes,edges,compute_nodes):
    from itertools import chain, combinations
    best_xstar = 0
    all_nodes_set = set(nodes)
    for r in range(1,len(nodes)):
        for S in combinations(nodes,r):
            S_set = set(S)
            # Skip if S includes all or none of the compute_nodes
            compute_in_S = [n for n in compute_nodes if n in S_set]
            if len(compute_in_S) == 0 or len(compute_in_S) == len(compute_nodes):
                continue
            xstar_S = calc_xstar_onesol(nodes,edges,compute_nodes,S_set)
            if xstar_S > best_xstar:
                best_xstar = xstar_S
    return best_xstar

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
    total_gpus = 16
    total_layers = 2
    topology,connection_blocks,intra_blueprint  = construct_topology(total_gpus, total_layers, generator = lambda x,y,z: [x,y,z])
    nodes = []
    edges = {}
    compute_nodes = []
    layer_lookup = {}
    for i, layer in enumerate(topology):
        for node in layer:
            nodes.append(node.node_id)
            if node.node_type == NodeType.GPU:
                compute_nodes.append(node.node_id)
            layer_lookup[node.node_id] = i
    for i, layer in enumerate(topology):
        for node in layer:
            for sibling in node.siblings.values():
                node_layer = layer_lookup[node.node_id]
                sibling_layer = layer_lookup[sibling.node_id]
                if node_layer == sibling_layer:
                    bandwidth = intra_blueprint[node_layer]['Bii']
                else:
                    node_layer, sibling_layer = min(node_layer, sibling_layer), max(node_layer, sibling_layer)
                    bandwidth = connection_blocks[(node_layer, sibling_layer)]['b_ij']
                edges[(node.node_id, sibling.node_id)] = bandwidth
    # Score from calculate_optimality_star with timing
    start_opt = time.time()
    score_optimality = calculate_optimality_star(nodes, edges, compute_nodes)
    end_opt = time.time()
    print(f"calculate_optimality_star score: {float(score_optimality):.4f}")
    print(f"calculate_optimality_star runtime: {end_opt - start_opt:.6f} seconds")

    # Score from forestcoll_bf_calc with timing
    start_bf = time.time()
    score_bf = forestcoll_bf_calc(nodes, edges, compute_nodes)
    end_bf = time.time()
    print(f"forestcoll_bf_calc score: {score_bf:.4f}")
    print(f"forestcoll_bf_calc runtime: {end_bf - start_bf:.6f} seconds")

if __name__ == "__main__":
    main()