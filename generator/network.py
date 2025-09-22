import random
import sympy
from enum import Enum


class InterLayer:

    def __init__(self, num_nodes_per_layer, connection_blocks):
        self.num_nodes_per_layer = num_nodes_per_layer
        self.connection_blocks = connection_blocks
        self.total_layers = len(self.num_nodes_per_layer)


class NodeType(Enum):
    GPU = 'GPU'
    SWITCH = 'SWITCH'


class GraphNode:

    _next_id = 0

    def __init__(self, node_type: NodeType):
        if not isinstance(node_type, NodeType):
            raise TypeError("Node type must be a NodeType enum.")

        self.node_id = GraphNode._next_id
        GraphNode._next_id += 1
        
        self.node_type = node_type
    
    @classmethod
    def reset_id_counter(cls):
        cls._next_id = 0

    def __hash__(self):
        return hash(self.node_id)
        
    def __eq__(self, other):
        if not isinstance(other, GraphNode):
            return NotImplemented
        return self.node_id == other.node_id

    def __repr__(self):
        return f"Node(id={self.node_id}, type={self.node_type.value})"


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


def construct_graph_by_inter_layers(inter_layer: InterLayer):
    res_graph = dict()
    source_node_container = dict()
    for each_source_node in list(inter_layer.connection_blocks):
        if each_source_node[0] not in source_node_container:
            source_node_container[each_source_node[0]] = list()
        source_node_container[each_source_node[0]].append(each_source_node[1])
    for each_layer in inter_layer.num_nodes_per_layer:
        for each_node_index in range(each_layer):
            cur_node = GraphNode()
            if cur_node not in res_graph[cur_node]:
                res_graph[cur_node] = dict()
            linked_layers = source_node_container[each_layer]
    GraphNode.reset_id_counter()
    return res_graph



if __name__ == "__main__":
    print(sympy.divisors(13))
    test_inter = construct_total_inter_connection(40, 4)
    construct_graph_by_inter_layers(test_inter)