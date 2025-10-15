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