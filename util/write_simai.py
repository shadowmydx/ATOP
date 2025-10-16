import time, sys, os
from typing import Callable
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from generator.network import NodeType, GraphNode

def default_bandwidth(layer_a,layer_b):
    return '800GBps'

def default_latency(layer_a,layer_b):
    return '0.0025ms'

def write_topology_to_simai(node_list: list[list[GraphNode]],bandwidth: Callable=default_bandwidth, latency: Callable=default_latency, switch_per_node: int=4, GPU_type: str='A100', filename: str = "topology.txt") -> None:
    filename += str(time.time())
    total_nodes = sum(len(layer) for layer in node_list)
    GPU_list = [node for layer in node_list for node in layer if node.node_type == NodeType.GPU]
    GPU_idx_list = [node.node_id for node in GPU_list]
    switch_list = [node for layer in node_list for node in layer if node.node_type == NodeType.SWITCH]
    switch_idx_list = [node.node_id for node in switch_list]
    node_switch_idx_list = []
    for GPUnode in GPU_list:
        for neighbor in GPUnode.siblings.keys():
            if neighbor not in node_switch_idx_list and neighbor in switch_idx_list:
                node_switch_idx_list.append(neighbor)
    board_switch_idx_list = []
    for switch_node in switch_idx_list:
        if switch_node not in node_switch_idx_list:
            board_switch_idx_list.append(switch_node)
    print(f"Total Nodes: {total_nodes}, GPU Nodes: {len(GPU_idx_list)}, Node Switches: {len(node_switch_idx_list)}, Board Switches: {len(board_switch_idx_list)}, All Switches: {len(switch_idx_list)}")
            
    counter = 0
    atop_simai_ref = {}
    simai_atop_ref = {}
    for i in range(len(GPU_idx_list)):
        atop_simai_ref[GPU_idx_list[i]] = counter
        simai_atop_ref[counter] = GPU_idx_list[i]
        counter += 1
    for i in range(len(node_switch_idx_list)):
        atop_simai_ref[node_switch_idx_list[i]] = counter
        simai_atop_ref[counter] = node_switch_idx_list[i]
        counter += 1
    for i in range(len(board_switch_idx_list)):
        atop_simai_ref[board_switch_idx_list[i]] = counter
        simai_atop_ref[counter] = board_switch_idx_list[i]
        counter += 1
    
    layer_ref = {}
    for layer_idx in range(len(node_list)):
        for node in node_list[layer_idx]:
            layer_ref[node.node_id] = layer_idx
    
    link_dict = {}
    for layer in node_list:
        for node in layer:
            for sibling in node.siblings.keys():
                if (node.node_id, sibling) not in link_dict and (sibling, node.node_id) not in link_dict:
                    source_id = atop_simai_ref[node.node_id]
                    target_id = atop_simai_ref[sibling]
                    source_id, target_id = min(source_id, target_id), max(source_id, target_id)
                    bw = bandwidth(layer_ref[node.node_id], layer_ref[sibling])
                    lat = latency(layer_ref[node.node_id], layer_ref[sibling])
                    link_dict[(source_id, target_id)] = (bw, lat)

    with open(filename, 'w') as f:
        first_line = f"{total_nodes} {switch_per_node} {len(node_switch_idx_list)} {len(board_switch_idx_list)} {len(link_dict)} {GPU_type}\n"
        f.write(first_line)
        second_line = ' '.join([str(atop_simai_ref[node_id]) for node_id in node_switch_idx_list])
        if len(second_line) > 0:
            second_line += ' '
        second_line += ' '.join([str(atop_simai_ref[node_id]) for node_id in board_switch_idx_list]) + '\n'
        f.write(second_line)
        for (src, dst), (bw, lat) in link_dict.items():
            f.write(f"{src} {dst} {bw} {lat} {0}\n")
    