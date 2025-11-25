import sys
from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from util.write_simai import write_topology_to_simai, execute_simai

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

# 4. Write topology to SimAI format
print("\n--- Writing Topology to SimAI Format ---")
write_topology_to_simai(topology, filename="sample_topology.txt")

# 5. Execute SimAI simulator
print("\n--- Executing SimAI Simulator ---")
execute_simai(topology_path="sample_topology.txt",printing=True)