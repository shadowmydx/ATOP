from NSGAII.solution import NSGASolution
from generator.network import NodeType, GraphNode

def network_cost(solution: NSGASolution):
    net_topo = solution.get_item()
    connection_blocks = net_topo.connection_blocks
    intra_blueprint = net_topo.blueprint
    
    cost_per_switch = 10
    cost_per_link_bandwidth = 1

    num_switches = 0
    link_cost = 0
    for node_id, node in net_topo.topology.nodes.items():
        # Count switches in topology
        if node.node_type == NodeType.SWITCH:
            num_switches += 1 
            
        # Sum all outgoing link bandwidths from node.siblings
        for sibling_id in node.siblings:            
            sibling_layer = net_topo.topology.nodes[sibling_id].layer
            if node.layer == sibling_layer:
                bandwidth = intra_blueprint[node.layer]['Bii']
            else:
                node_layer_idx, sibling_layer_idx = min(node.layer, sibling_layer), max(node.layer, sibling_layer)
                bandwidth = connection_blocks[(node_layer_idx, sibling_layer_idx)]['b_ij']
            link_cost += bandwidth * cost_per_link_bandwidth

    switch_cost = num_switches * cost_per_switch    
    total_cost = switch_cost + link_cost
    
    return total_cost
    
    