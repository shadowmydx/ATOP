import random
import sympy
import sys
from util.write_simai import write_topology_to_simai
from generator.node import InterLayer, GraphNode, NodeType



def construct_total_inter_connection(total_gpus, total_layers):
    target_layers = list()
    target_layers.append(total_gpus)
    for _ in range(1, total_layers):
        current_num_switches = random.randint(0, total_gpus)
        if current_num_switches == 0:
            continue
        target_layers.append(current_num_switches)
    target_connection_blocks = dict()
    real_total_laysers = len(target_layers)
    for i_index in range(real_total_laysers - 1):
        for j_index in range(i_index + 1, real_total_laysers):
            if (i_index, j_index) not in target_connection_blocks:
                target_connection_blocks[(i_index, j_index)] = dict()
            num_blocks_in_i = random.choice([0] + sympy.divisors(target_layers[i_index]))
            num_blocks_in_j = random.choice([0] + [each_num for each_num in sympy.divisors(target_layers[j_index]) if each_num <= num_blocks_in_i])
            if num_blocks_in_i == 0 or num_blocks_in_j == 0:
                continue
            layer_links = random.randint(1, int(target_layers[j_index] / num_blocks_in_j))
            layer_bandwidth = random.randint(1, 4)
            target_connection_blocks[(i_index, j_index)]["i"] = num_blocks_in_i
            target_connection_blocks[(i_index, j_index)]["j"] = num_blocks_in_j
            target_connection_blocks[(i_index, j_index)]["e_ij"] = layer_links
            target_connection_blocks[(i_index, j_index)]["b_ij"] = layer_bandwidth
    return InterLayer(target_layers, target_connection_blocks)


""" def transform_block_node_to_node_index(num_blocks, node_in_block, layer_index, total_layers):
    return None


def transform_node_index_to_block_node(node_index, block_index, layer_index, total_layers):
    return None


def calculate_mapping_block_node(target_connection_container, target_num_nodes, source_node_in_block):
    num_links = target_connection_container["e_ij"]
    return [(num_links * (source_node_in_block - 1) + m) % int(target_num_nodes / target_connection_container["j"]) + 1 for m in range(1, num_links + 1)]


def construct_graph_by_inter_layers(inter_layer: InterLayer):
    res_graph = dict()
    source_node_container = dict()
    should_be_gpu = True
    for each_layer in inter_layer.num_nodes_per_layer:
        for _ in range(each_layer):
            node_type = NodeType.GPU if should_be_gpu else NodeType.SWITCH
            cur_node = GraphNode(node_type)
            res_graph[cur_node.node_id] = cur_node
        should_be_gpu = False
    for each_source_layers in list(inter_layer.connection_blocks):
        if each_source_layers[0] not in source_node_container:
            source_node_container[each_source_layers[0]] = list()
        source_node_container[each_source_layers[0]].append(each_source_layers[1])
    start_node_index_in_cur_layer = 0
    for each_layer_index in range(inter_layer.total_layers - 1):
        cur_layer = inter_layer.num_nodes_per_layer[each_layer_index]
        for each_node_index in range(start_node_index_in_cur_layer, cur_layer + start_node_index_in_cur_layer):
            target_linked_layers = source_node_container[each_layer_index]
            cur_node = res_graph[each_node_index]
            cur_block = (each_node_index - start_node_index_in_cur_layer) % cur_layer
            for each_target_layer in target_linked_layers:
                cur_connection_block = inter_layer.connection_blocks[(each_layer_index, each_target_layer)]
            
        start_node_index_in_cur_layer += cur_layer
                
    GraphNode.reset_id_counter()
    return res_graph """


def construct_topology(total_gpus: int, total_layers: int):
    GraphNode.reset_id_counter()
    inter_layer_data = construct_total_inter_connection(total_gpus, total_layers)
    layers_nodes_count = inter_layer_data.layers
    connection_blocks = inter_layer_data.connection_blocks
    layers = []
    for i, node_count in enumerate(layers_nodes_count):
        if node_count == 0:
            layers.append([])  
            continue
        layer_nodes = []
        node_type = NodeType.GPU if i == 0 else NodeType.SWITCH
        for _ in range(node_count):
            layer_nodes.append(GraphNode(node_type))
        layers.append(layer_nodes)
        
    for (i, j), params in connection_blocks.items():
        params = connection_blocks.get((i, j))
        if 'i' not in params:
            continue
        num_blocks_i = params["i"]
        num_blocks_j = params["j"]
        e_ij = params["e_ij"]
        
        if not layers[i] or not layers[j]:
            continue

        block_size_i = layers_nodes_count[i] // num_blocks_i
        block_size_j = layers_nodes_count[j] // num_blocks_j
        
        for k in range(num_blocks_i):
            target_block_j_index = (k % num_blocks_j)
            
            for m in range(block_size_i):
                source_node_index = k * block_size_i + m
                source_node = layers[i][source_node_index]
                
                for link in range(1, e_ij + 1):
                    target_node_index_in_block = (e_ij * m + link - 1) % block_size_j
                    target_node_index = target_block_j_index * block_size_j + target_node_index_in_block
                    target_node = layers[j][target_node_index]
                    
                    source_node.siblings[target_node.node_id] = target_node
                    target_node.siblings[source_node.node_id] = source_node

    return layers



if __name__ == "__main__":
    total_gpus = 16
    total_layers = 3

    # 1. Build the topology
    print(f"--- Building a topology with {total_layers} layers and {total_gpus} GPUs ---")
    try:
        topology = construct_topology(total_gpus, total_layers)
        print("Topology successfully built.")
    except Exception as e:
        print(f"Error during topology construction: {e}")
        sys.exit(1)

    # 2. Print detailed topology information
    print("\n--- Topology Details ---")
    total_nodes = 0
    for i, layer in enumerate(topology):
        print(f"Layer {i} ({'GPU' if i == 0 else 'Switch'}): Node count = {len(layer)}")
        total_nodes += len(layer)
        for node in layer:
            sibling_ids = sorted([node.node_id for node in node.siblings.values()])
            print(f"  - Node {node.node_id} ({node.node_type.value}) connected to: {sibling_ids}")
    print(f"\nTotal nodes in topology: {total_nodes}")

    # 3. Validate bidirectional connections
    print("\n--- Topology Integrity Check ---")
    all_connections_valid = True
    for layer in topology:
        for node in layer:
            for neighbor in node.siblings.values():
                if node.node_id not in neighbor.siblings:
                    print(f"Error: Node {node.node_id} connects to {neighbor.node_id}, but {neighbor.node_id} does not connect back.")
                    all_connections_valid = False

    if all_connections_valid:
        print("All connections are bidirectional. Topology is complete and valid.")
    else:
        print("Topology build failed: Unidirectional connections found.")
        
    write_topology_to_simai(topology, filename="topology.txt")