import networkx as nx
from fractions import Fraction
import math
from generator.network import NodeType, GraphNode
from NSGAII.solution import NSGASolution

def calculate_optimality_star(nodes, edges, compute_nodes):
    """
    实现 ForestColl 算法 1：求解公式 (*) 的值 (1/x*)
    :param nodes: 所有节点列表 (计算节点 Vc + 交换机节点 Vs)
    :param edges: 边字典，格式为 {(u, v): bandwidth}
    :param compute_nodes: 计算节点 Vc 列表
    :return: 1/x* 的精确分数值
    """
    N = len(compute_nodes)
    
    # 构建基础拓扑图
    G = nx.DiGraph()
    # Ensure all nodes are present in the graph
    for n in nodes:
        G.add_node(n)
    for (u, v), b in edges.items():
        G.add_edge(u, v, capacity=b)
    
    # 计算每个计算节点的入带宽 B-(v)
    in_bandwidths = {v: sum(G[u][v]['capacity'] for u in G.predecessors(v)) 
                     for v in compute_nodes}
    min_in_bw = min(in_bandwidths.values())
    
    if min_in_bw <= 0:
        return float('inf')
    
    # 1. 设定二分查找的范围 [l, r] [cite: 61]
    # l 是 1/x* 的下界，r 是上界
    l = (N - 1) / min_in_bw
    r = float(N - 1)
    
    # 2. 二分查找过程 [cite: 61, 76]
    # 精度限制：直到范围足够小以确定唯一的候选分数
    epsilon = 1.0 / (min_in_bw ** 2)
    while r - l >= epsilon:
        inv_x = (l + r) / 2
        x = 1.0 / inv_x
        
        # 构建辅助网络 Gx [cite: 61, 67]
        aux_G = G.copy()
        source = "virtual_s"
        for c in compute_nodes:
            aux_G.add_edge(source, c, capacity=x)
            
        # 判定准则：检查从 s 到每个计算节点的 maxflow 是否为 Nx [cite: 62, 75]
        is_feasible = True
        target_flow = N * x
        for c in compute_nodes:
            # 使用 NetworkX 的预推流或 Edmonds-Karp 计算最大流
            flow_value = nx.maximum_flow_value(aux_G, source, c)
            # 考虑浮点数精度误差
            if flow_value < target_flow - 1e-9:
                is_feasible = False
                break
        
        if is_feasible:
            r = inv_x  # 当前 1/x 偏大或刚好，尝试更小的 1/x (更大的 x)
        else:
            l = inv_x  # 当前 1/x 偏小，需要增加 1/x
            
    # 3. 寻找唯一的分数解 p/q [cite: 62, 76]
    # 在 [l, r] 范围内寻找分母 q <= min_in_bw 的最简分数
    return find_fraction_in_range(l, r, min_in_bw)

def find_fraction_in_range(l, r, max_q):
    """
    根据 Farey 序列或其他方法在给定范围内找到符合分母约束的分数
    """
    # 简化实现：在此范围内迭代分母寻找匹配项
    for q in range(1, int(max_q) + 1):
        p = round(l * q)
        if l <= p/q <= r:
            return Fraction(p, q)
    return Fraction(math.ceil(l))

# 示例用法
# 假设 2 个 Box，每个 Box 4 个 GPU (c1..c8)，IB 带宽为 b=10
nodes = [f'c{i}' for i in range(1, 9)] + ['sw1', 'sw2']
compute_nodes = [f'c{i}' for i in range(1, 9)]
edges = {} # 此处填入拓扑连接和带宽
# result = calculate_optimality_star(nodes, edges, compute_nodes)

def forestcoll_score(solution: NSGASolution):
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
    
    score = calculate_optimality_star(nodes, edges, compute_nodes)
    return score