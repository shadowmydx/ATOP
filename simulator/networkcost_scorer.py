from NSGAII.solution import NSGASolution
from generator.network import NodeType, GraphNode

def network_cost(solution: NSGASolution):
    net_topo = solution.get_item()
    topology = net_topo.topology
    connection_blocks = net_topo.connection_blocks
    intra_blueprint = net_topo.blueprint

    cost_per_switch = 10
    cost_per_link_bandwidth = 1

    # Count switches in topology
    layer_lookup = {}
    num_switches = 0
    for i, layer in enumerate(topology):
        for node in layer:
            layer_lookup[node.node_id] = i
            if node.node_type == NodeType.SWITCH:
                num_switches += 1

    switch_cost = num_switches * cost_per_switch
    # Sum all outgoing link bandwidths from node.siblings
    link_cost = 0
    for i, layer in enumerate(topology):
        for node in layer:
            for sibling in node.siblings.values():
                node_layer = layer_lookup[node.node_id]
                sibling_layer = layer_lookup[sibling.node_id]
                if node_layer == sibling_layer:
                    bandwidth = intra_blueprint[node_layer]['Bii']
                else:
                    node_layer_idx, sibling_layer_idx = min(node_layer, sibling_layer), max(node_layer, sibling_layer)
                    bandwidth = connection_blocks[(node_layer_idx, sibling_layer_idx)]['b_ij']
                link_cost += bandwidth * cost_per_link_bandwidth

    total_cost = switch_cost + link_cost
    return total_cost
    
    