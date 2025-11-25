import time, sys, os
from typing import Callable
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from generator.network import NodeType, GraphNode
import subprocess

def default_bandwidth(layer_a,layer_b):
    return '800GBps'

def default_latency(layer_a,layer_b):
    return '0.0025ms'

def write_topology_to_simai(node_list: list[list[GraphNode]],bandwidth: Callable=default_bandwidth, latency: Callable=default_latency, switch_per_node: int=4, GPU_type: str='A100', filename: str = "topology.txt") -> None:
    total_nodes = sum(len(layer) for layer in node_list)
    GPU_list = [node for layer in node_list for node in layer if node.node_type == NodeType.GPU]
    GPU_idx_list = [node.node_id for node in GPU_list]
    switch_list = [node for layer in node_list for node in layer if node.node_type == NodeType.SWITCH]
    switch_idx_list = [node.node_id for node in switch_list]
    

    print(f"Total Nodes: {total_nodes}, GPU Nodes: {len(GPU_idx_list)}, Real Switches: {len(switch_idx_list)}")
            
    counter = 0
    atop_simai_ref = {}
    simai_atop_ref = {}
    for i in range(len(GPU_idx_list)):
        atop_simai_ref[GPU_idx_list[i]] = counter
        simai_atop_ref[counter] = GPU_idx_list[i]
        counter += 1
    # create virtual NICs
    GPU_NIC_ref = {}
    virtual_NIC_list = []
    for i in range(len(GPU_idx_list)):
        GPU_NIC_ref[atop_simai_ref[i]] = counter
        virtual_NIC_list.append(counter)
        counter += 1
        
    for i in range(len(switch_idx_list)):
        atop_simai_ref[switch_idx_list[i]] = counter
        simai_atop_ref[counter] = switch_idx_list[i]
        counter += 1
    
    layer_ref = {}
    for layer_idx in range(len(node_list)):
        for node in node_list[layer_idx]:
            layer_ref[node.node_id] = layer_idx
    
    link_dict = {}
    
    # links from GPU to virtual NIC
    for node in GPU_list:
        source_id = atop_simai_ref[node.node_id]
        target_id = GPU_NIC_ref[source_id]
        source_id, target_id = min(source_id, target_id), max(source_id, target_id)
        bw = bandwidth(-1,-1)
        lat = latency(-1,-1)
        link_dict[(source_id, target_id)] = (bw, lat)
    for layer in node_list:
        for node in layer:
            for sibling in node.siblings.keys():
                if (node.node_id, sibling) not in link_dict and (sibling, node.node_id) not in link_dict:
                    source_id = atop_simai_ref[node.node_id]
                    if node.node_type == NodeType.GPU:
                        source_id = GPU_NIC_ref[source_id]
                    target_id = atop_simai_ref[sibling]
                    if node.siblings[sibling].node_type == NodeType.GPU:
                        target_id = GPU_NIC_ref[target_id]
                    source_id, target_id = min(source_id, target_id), max(source_id, target_id)
                    bw = bandwidth(layer_ref[node.node_id], layer_ref[sibling])
                    lat = latency(layer_ref[node.node_id], layer_ref[sibling])
                    link_dict[(source_id, target_id)] = (bw, lat)

    total_nodes = total_nodes + len(GPU_idx_list) # add virtual NICs
    with open(filename, 'w') as f:
        first_line = f"{total_nodes} {1} {len(GPU_idx_list)} {len(switch_idx_list)} {len(link_dict)} {GPU_type}\n"
        f.write(first_line)
        second_line = ' '.join([str(x) for x in virtual_NIC_list])
        if len(second_line) > 0:
            second_line += ' '
        second_line += ' '.join([str(atop_simai_ref[node_id]) for node_id in switch_idx_list]) + '\n'
        f.write(second_line)
        for (src, dst), (bw, lat) in link_dict.items():
            f.write(f"{src} {dst} {bw} {lat} {0}\n")
    
def execute_simai(topology_path: str,\
    simai_executable_path: str = '../SimAI/bin/SimAI_simulator',\
        workload_path: str = '../SimAI/example/microAllReduce.txt',\
            printing: bool = False) -> None:
    # Place the executable path as the first argument in the argv list
    # and pass AS_* variables via the `env` parameter (safer than embedding them in argv).
    env = os.environ.copy()
    env.update({
        'AS_SEND_LAT': '3',
        'AS_NVLS_ENABLE': '1',
    })

    cmd = [
        str(simai_executable_path),
        '-t', '16',
        '-w', str(workload_path),
        '-n', str(topology_path),
        '-c', str('../SimAI/astra-sim-alibabacloud/inputs/config/SimAI.conf'),
    ]

    # Run the simulator. Use check=True if you want an exception on non-zero exit.
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if printing is True:
        print('returncode:', completed.returncode)
        if completed.stdout:
            print('stdout:\n', completed.stdout)
        if completed.stderr:
            print('stderr:\n', completed.stderr)

    return float(completed.returncode)