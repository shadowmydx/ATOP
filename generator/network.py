import random
import sympy


class InterLayer:

    def __init__(self, num_nodes_per_layer, connection_blocks):
        self.num_nodes_per_layer = num_nodes_per_layer
        self.connection_blocks = connection_blocks
        self.total_layers = len(self.num_nodes_per_layer)


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
    for i_index in range(1, real_total_laysers - 1):
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


if __name__ == "__main__":
    print(sympy.divisors(13))
    print(construct_total_inter_connection(40, 4))