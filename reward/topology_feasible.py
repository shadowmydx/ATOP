from collections import deque
from typing import Set

def is_connected(topology) -> bool:
    nodes_dict = topology.nodes
    
    if not nodes_dict or len(nodes_dict) <= 1:
        return True
    
    all_nodes = set(nodes_dict)
    start_node = next(iter(all_nodes))
    
    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    
    while queue:
        current = queue.popleft()
        cur_node = nodes_dict[current]
        for neighbor in cur_node.siblings:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    
    return len(visited) == len(all_nodes)


def is_solution_feasible(solution):
    cur_topo = solution.item.topology
    result = is_connected(cur_topo)
    return 1 if result else 0, True