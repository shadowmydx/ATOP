import random
import sympy
import sys
import pprint
from enum import Enum

class InterLayer:

    def __init__(self, num_nodes_per_layer, connection_blocks):
        self.layers = num_nodes_per_layer
        self.connection_blocks = connection_blocks
        self.total_layers = len(self.layers)


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
        self.siblings = dict()
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


def generate_intra_layer_blueprint(num_nodes_per_layer, d_max):
    blueprint = {}
    num_layers = len(num_nodes_per_layer)
    for i in range(num_layers):
        N_i = num_nodes_per_layer[i]
        if N_i <= 1:
            continue

        layer_params = {}
        
        D_i = random.randint(0, d_max)
        if D_i == 0:
            blueprint[i] = {'Di': 0}
            continue 
        layer_params['Di'] = D_i

        Sik_list = []
        n_remained = N_i
        for k in range(D_i):
            if k < D_i - 1: 
                possible_divisors = sympy.divisors(n_remained)
                S_ik = random.choice(possible_divisors)
                Sik_list.append(S_ik)
                n_remained //= S_ik
            else: 
                Sik_list.append(n_remained)
        layer_params['Sik'] = Sik_list

        Pik_list = []
        A_matrix = [] # A[k][r][t]
        C_matrix = [] # C[k][t]
        
        for k in range(D_i):
            S_ik = Sik_list[k]
            
            P_ik = random.randint(0, S_ik - 1)
            Pik_list.append(P_ik)

            A_k = []
            C_k = []
            for t in range(D_i):
                A_k_t = []
                for r in range(D_i + 1):
                    A_ikrt = random.randint(-S_ik, S_ik)
                    A_k_t.append(A_ikrt)
                
                C_tik = random.randint(-S_ik, S_ik)
                C_k.append(C_tik)
                A_k.append(A_k_t)

            A_matrix.append(A_k)
            C_matrix.append(C_k)

        layer_params['Pik'] = Pik_list
        layer_params['A'] = A_matrix
        layer_params['C'] = C_matrix
        layer_params['Bii'] = random.randint(1, 4)
        blueprint[i] = layer_params
        
    return blueprint


def test_blueprint_generation(test_case_name, num_nodes, max_dims):
    print(f"\n===== Running Test Case: {test_case_name} =====")
    print(f"Parameters: Node counts={num_nodes}, Max dimensions={max_dims}")

    blueprint = generate_intra_layer_blueprint(num_nodes, max_dims)

    print("\n--- Generated Blueprint ---")
    pp = pprint.PrettyPrinter(indent=2, width=100)
    pp.pprint(blueprint)

    print("\n--- Verifying Blueprint Integrity ---")
    try:
        for layer_idx, params in blueprint.items():
            print(f"Verifying Layer {layer_idx}...")
            assert 'Di' in params, f"Layer {layer_idx} missing 'Di'"
            D_i = params['Di']
            assert 0 <= D_i <= max_dims, f"Layer {layer_idx} Di={D_i} is out of range [0, {max_dims}]"

            if D_i > 0:
                Sik = params['Sik']
                assert len(Sik) == D_i, f"Layer {layer_idx} len(Sik)={len(Sik)} != Di={D_i}"
                product_Sik = 1
                for s in Sik: product_Sik *= s
                assert product_Sik == num_nodes[layer_idx], \
                    f"Layer {layer_idx} product of Sik={product_Sik} != N_i={num_nodes[layer_idx]}"

                Pik = params['Pik']
                assert len(Pik) == D_i, f"Layer {layer_idx} len(Pik)={len(Pik)} != Di={D_i}"
                for k in range(D_i):
                    assert 0 <= Pik[k] < Sik[k], \
                        f"Layer {layer_idx} Pik[{k}]={Pik[k]} is out of range [0, {Sik[k]-1}]"
                
                A = params['A']
                C = params['C']
                assert len(A) == D_i
                assert len(C) == D_i
                for k in range(D_i):
                    assert len(A[k]) == D_i
                    assert len(C[k]) == D_i
                    for t in range(D_i):
                        assert len(A[k][t]) == D_i + 1
        
        print("\n[SUCCESS] Blueprint validation passed all checks.")

    except AssertionError as e:
        print(f"\n[FAILURE] Blueprint validation failed: {e}")
    
    print("=" * (len(test_case_name) + 28))


def _virtual_idx_to_coords(virtual_idx, Sik):
    """将节点的1D虚拟索引转换为多维坐标。"""
    coords = []
    temp_idx = virtual_idx
    # 从最后一个维度开始计算，维度尺寸列表也应该相应反转
    # 例如 32 = 8x4, 索引20 -> 20 // 4 = 5 (dim0), 20 % 4 = 0 (dim1) -> (5,0)
    # 这要求我们知道每个维度的乘数，或者反向计算
    # temp_idx = 20, Sik = [8, 4]
    # reversed(Sik) = [4, 8]
    # temp_idx % 4 = 0 (coord for dim1), temp_idx //= 4 -> 5
    # temp_idx % 8 = 5 (coord for dim0), temp_idx //= 8 -> 0
    # coords = [0], then [5, 0]
    
    # 修正坐标计算逻辑，使其更直观
    # idx = x1 * S2*S3... + x2 * S3*S4... + ...
    # 因此 x1 = idx // (S2*S3...), rem = idx % (S2*S3...)
    # x2 = rem // (S3*S4...), ...
    product = 1
    for s in Sik[1:]:
        product *= s
        
    rem = virtual_idx
    for i in range(len(Sik)):
        coord = rem // product
        coords.append(coord)
        rem %= product
        if i < len(Sik) - 1:
            product //= Sik[i+1] if Sik[i+1] > 0 else 1
            if product == 0: product = 1
            
    return coords


def _coords_to_virtual_idx(coords, Sik):
    virtual_idx = 0
    multiplier = 1
    for i in range(len(Sik) - 1, -1, -1):
        virtual_idx += coords[i] * multiplier
        if i > 0:
            multiplier *= Sik[i]
    return virtual_idx


def add_intra_layer_connections(layers, intra_blueprint):
    for layer_idx, params in intra_blueprint.items():
        if params.get('Di', 0) == 0:
            continue
        nodes_in_layer = layers[layer_idx]
        if not nodes_in_layer:
            continue
        Di = params['Di']
        Sik = params['Sik']
        Pik = params['Pik']
        A = params['A']
        C = params['C']
        for source_virtual_idx, source_node in enumerate(nodes_in_layer):
            source_coords = _virtual_idx_to_coords(source_virtual_idx, Sik)
            for k in range(Di):
                for m in range(1, Pik[k] + 1): # m from 1 to Pik[k]
                    dest_coords = [0] * Di
                    for t in range(Di):
                        m_term = A[k][t][0] * m
                        sum_term = sum(A[k][t][r] * source_coords[r-1] for r in range(1, Di + 1))
                        c_term = C[k][t]
                        S_it = Sik[t]
                        dest_coords[t] = (m_term + sum_term + c_term) % S_it
                    dest_virtual_idx = _coords_to_virtual_idx(dest_coords, Sik)
                    dest_node = nodes_in_layer[dest_virtual_idx]
                    if source_node.node_id == dest_node.node_id:
                        continue
                    if dest_node.node_id not in source_node.siblings:
                        source_node.siblings[dest_node.node_id] = dest_node
                        dest_node.siblings[source_node.node_id] = source_node


def construct_topology(total_gpus: int, total_layers: int, d_max=2, generator=lambda x,y,z: x):
    GraphNode.reset_id_counter()
    inter_layer_data = construct_total_inter_connection(total_gpus, total_layers)
    layers_nodes_count = inter_layer_data.layers
    intra_blueprint = generate_intra_layer_blueprint(layers_nodes_count, d_max)
    connection_blocks = inter_layer_data.connection_blocks
    layers = []
    all_nodes = dict()
    for i, node_count in enumerate(layers_nodes_count):
        if node_count == 0:
            layers.append([])  
            continue
        layer_nodes = []
        node_type = NodeType.GPU if i == 0 else NodeType.SWITCH
        for _ in range(node_count):
            cur_node = GraphNode(node_type)
            all_nodes[cur_node.node_id] = cur_node
            layer_nodes.append(cur_node)
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
    add_intra_layer_connections(layers, intra_blueprint)
    return generator(layers, connection_blocks, intra_blueprint)



if __name__ == "__main__":
    total_gpus = 160
    total_layers = 3

    # 1. Build the topology
    print(f"--- Building a topology with {total_layers} layers and {total_gpus} GPUs ---")
    construct_topology(total_gpus, total_layers)
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
    test_blueprint_generation("unit test", [72, 24, 24], 3)
