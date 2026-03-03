import sys
import time
from generator.network import NodeType, GraphNode,construct_topology,test_blueprint_generation
from NSGAII.solution import NetTopology, NSGASolution


import networkx as nx
_maxflow_counter = 0
_maxflow_start_time = None
_maxflow_total_start_time = None
_maxflow_counter = 0
_maxflow_start_time = None
_maxflow_total_start_time = None
_maxflow_sum_100 = 0.0
def counted_maximum_flow_value(*args, **kwargs):
    global _maxflow_counter, _maxflow_start_time, _maxflow_total_start_time, _maxflow_sum_100
    import time
    if _maxflow_counter == 0:
        _maxflow_total_start_time = time.time()
    _maxflow_counter += 1
    if _maxflow_counter % 100 == 1:
        _maxflow_start_time = time.time()
        _maxflow_sum_100 = 0.0
    t0 = time.time()
    result = nx.maximum_flow_value(*args, **kwargs)
    t1 = time.time()
    interval = t1 - t0
    _maxflow_sum_100 += interval
    if _maxflow_counter % 100 == 0:
        elapsed = time.time() - _maxflow_start_time if _maxflow_start_time is not None else 0
        total_elapsed = time.time() - _maxflow_total_start_time if _maxflow_total_start_time is not None else 0
        print(f"nx.maximum_flow_value called {_maxflow_counter} times, last 100 calls took {elapsed:.6f} seconds, sum of 100 intervals: {_maxflow_sum_100:.6f} seconds, total elapsed: {total_elapsed:.6f} seconds")
    return result
from fractions import Fraction
import math
from generator.network import NodeType, GraphNode
from NSGAII.solution import NSGASolution

import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

epsilon = 1e-10
max_denom = 10000


def isclose(a, b):
    return math.isclose(a, b, abs_tol=epsilon, rel_tol=0.0)


class OptimalBranchingsAlgo:
    s_node = "SOURCE"

    def __init__(self, topo, capacitated: bool = False, compute_nodes=None):
        self.flow_graph = nx.DiGraph()
        self.flow_graph.add_nodes_from(topo.nodes())

        self.edge_capacity = {}
        for a, b in topo.edges():
            if a == b:
                continue
            if self.flow_graph.has_edge(a, b):
                assert not capacitated, "capacitated edges are not supported in multigraph"
                self.edge_capacity[a, b] += 1
            else:
                self.flow_graph.add_edge(a, b)
                if capacitated:
                    w = topo[a][b]['capacity']
                    assert w > 0 and type(w) is int
                    self.edge_capacity[a, b] = w
                else:
                    self.edge_capacity[a, b] = 1

        if compute_nodes is None:
            compute_nodes = topo.nodes()
        self.compute_nodes = set(compute_nodes)
        self.flow_graph.add_node(OptimalBranchingsAlgo.s_node)
        for n in self.compute_nodes:
            self.flow_graph.add_edge(OptimalBranchingsAlgo.s_node, n)

    def test(self, U: float, k: int, floor: bool) -> bool:
        # --- Counter and timing logic ---
        if not hasattr(self, '_test_call_counter'):
            self._test_call_counter = 0
            self._test_call_start_time = None
        import time
        self._test_call_counter += 1
        if self._test_call_counter % 2 == 1:
            self._test_call_start_time = time.time()
        if self._test_call_counter % 2 == 0:
            elapsed = time.time() - self._test_call_start_time if self._test_call_start_time is not None else 0
            print(f"self.test called {self._test_call_counter} times, last 2 calls took {elapsed:.6f} seconds")
        # --- End of counter and timing logic ---

        for b in self.compute_nodes:
            self.flow_graph[OptimalBranchingsAlgo.s_node][b]['capacity'] = k
        for (a, b), count in self.edge_capacity.items():
            capacity = count * U
            if type(capacity) is float and floor:
                if isclose(capacity, round(capacity)):
                    capacity = round(capacity)
                else:
                    capacity = math.floor(capacity)
            self.flow_graph[a][b]['capacity'] = capacity

        for v in self.compute_nodes:
            fval = counted_maximum_flow_value(self.flow_graph, OptimalBranchingsAlgo.s_node, v)
            if fval < len(self.compute_nodes) * k - epsilon:
                return False
        return True

    def binary_search(self) -> tuple[float, int]:
        N = len(self.compute_nodes)
        ingress_bw = {}
        for (_, b), count in self.edge_capacity.items():
            if b not in self.compute_nodes:
                continue
            ingress_bw[b] = ingress_bw.get(b, 0) + count
        try:
            min_bw = min(ingress_bw.values())
        except ValueError:
            return 0, 0

        assert type(min_bw) is int
        lb = (N - 1) / min_bw
        rb = N - 1
        assert rb >= lb
        end_range = 1 / min_bw ** 2
        while rb - lb > end_range:
            mid = (lb + rb) / 2
            if self.test(1, 1 / mid, False):
                rb = mid
            else:
                lb = mid
        mid = (lb + rb) / 2
        one_div_x_star = Fraction(mid).limit_denominator(min_bw)

        U = one_div_x_star.numerator / math.gcd(*(list(self.edge_capacity.values()) + [one_div_x_star.denominator]))
        k = round(U / one_div_x_star)

        assert isclose(U / k, one_div_x_star)
        for v in self.edge_capacity.values():
            assert isclose(U * v, round(U * v))

        return U, k

    # The return value x represents a runtime of M*x. Assuming weights of edges are true bandwidths.
    def convertToRuntime(self, U, k: int) -> float:
        return U / (k * len(self.compute_nodes))

def forestcoll_official_score(solution: NSGASolution):
    net_topo = solution.get_item()
    connection_blocks = net_topo.connection_blocks
    intra_blueprint = net_topo.blueprint
    
    nodes =  []     
    edges = {}
    compute_nodes = []
    
    for node_id,node in net_topo.topology.nodes.items():
        nodes.append(node_id)
        if node.node_type == NodeType.GPU:
            compute_nodes.append(node_id)
        for sibling_id in node.siblings:   
            sibling_layer = net_topo.topology.nodes[sibling_id].layer        
            if node.layer == sibling_layer:
                bandwidth = intra_blueprint[node.layer]['Bii']
            else:
                node_layer, sibling_layer = min(node.layer, sibling_layer), max(node.layer, sibling_layer)
                bandwidth = connection_blocks[(node_layer, sibling_layer)]['b_ij']
            edges[(node_id, sibling_id)] = bandwidth
    
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n)
    for (u, v), b in edges.items():
        G.add_edge(u, v, capacity=b)
    
    algo = OptimalBranchingsAlgo(G, capacitated=True, compute_nodes=compute_nodes)
    U, k = algo.binary_search()
    if U == 0 and k == 0:
        return 0
    opt_algbw = 1 / algo.convertToRuntime(U, k)
    # print(f"optimal algbw: {opt_algbw:.2f} GB/s")
        
    return opt_algbw

def build_simple_topology():
    # 4 GPUs, 4 switches, each GPU connects to all switches
    gpus = [GraphNode(NodeType.GPU) for _ in range(4)]
    switches = [GraphNode(NodeType.SWITCH) for _ in range(4)]
    # Assign readable node_id for test clarity
    for i, gpu in enumerate(gpus):
        gpu.node_id = f'c{i+1}'
    for i, sw in enumerate(switches):
        sw.node_id = f'sw{i+1}'
    for gpu in gpus:
        gpu.siblings = {sw.node_id: sw for sw in switches}
    for sw in switches:
        sw.siblings = {gpu.node_id: gpu for gpu in gpus}
    topology = [gpus, switches]
    # Layer lookup: 0 for GPUs, 1 for switches
    layer_lookup = {gpu.node_id: 0 for gpu in gpus}
    layer_lookup.update({sw.node_id: 1 for sw in switches})
    intra_blueprint = [ {'Bii': 10}, {'Bii': 0} ]
    connection_blocks = { (0,1): {'b_ij': 5}, (1,0): {'b_ij': 5} }
    return topology, connection_blocks, intra_blueprint

def main():
    # topology, connection_blocks, intra_blueprint = build_simple_topology()
    total_gpus = 1024
    total_layers = 2
    total_dimensions = 3
    num_topo = 1
    solutions = []
    for _ in range(num_topo):
        topology,connection_blocks,intra_blueprint  = construct_topology(total_gpus, total_layers, total_dimensions, generator = lambda x,y,z: [x,y,z])
        net_topo = NetTopology(topology, connection_blocks, intra_blueprint)
        solution = NSGASolution(net_topo, fitness_score=None)
        solutions.append(solution)

    # Score from forestcoll_bf_calc with timing
    official_scores = {}
    start_bf = time.time()
    for i in range(num_topo):
        solution = solutions[i]
        score_bf = forestcoll_official_score(solution)
        official_scores[i] = score_bf
    end_bf = time.time()
    print(f"forestcoll_official_score runtime: {end_bf - start_bf:.6f}")

    # Order y values, showing the keys order
    ordered_official = sorted(official_scores.items(), key=lambda x: x[1],reverse=False)
    print("Order of official_scores by value (key, value):", ordered_official)
    
    

if __name__ == "__main__":
    main()