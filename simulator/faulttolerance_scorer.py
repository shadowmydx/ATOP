from NSGAII.solution import NSGASolution
from generator.network import NodeType, GraphNode
import networkx as nx
from itertools import combinations

def fault_tolerance_score(solution: NSGASolution):
    net_topo = solution.get_item()
    connection_blocks = net_topo.connection_blocks
    intra_blueprint = net_topo.blueprint
    
    nodes =  []     
    edges = {}
    compute_nodes = []
    switch_nodes = []
    
    for node_id,node in net_topo.topology.nodes.items():
        nodes.append(node_id)
        if node.node_type == NodeType.GPU:
            compute_nodes.append(node_id)
        if node.node_type == NodeType.SWITCH:
            switch_nodes.append(node_id)
        for sibling_id in node.siblings:   
            sibling_layer = net_topo.topology.nodes[sibling_id].layer        
            if node.layer == sibling_layer:
                bandwidth = intra_blueprint[node.layer]['Bii']
            else:
                node_layer, sibling_layer = min(node.layer, sibling_layer), max(node.layer, sibling_layer)
                bandwidth = connection_blocks[(node_layer, sibling_layer)]['b_ij']
            edges[(node_id, sibling_id)] = bandwidth
            
    N = len(compute_nodes)
    
    # 构建基础拓扑图
    G = nx.DiGraph()
    # Ensure all nodes are present in the graph
    for n in nodes:
        G.add_node(n)
    for (u, v), b in edges.items():
        G.add_edge(u, v, capacity=b)
        
    return calculate_apl_fail(G, switch_nodes, compute_nodes)
        
        
def calculate_apl_fail(G, switch_nodes, gpu_nodes):
    """
    计算单交换机故障下的平均路径长度（APLfail），即容错得分
    
    参数:
        G (nx.Graph/nx.DiGraph): networkx构建的图对象（支持无向/有向图）
        switch_nodes (list): 交换机节点列表（Vs）
        gpu_nodes (list): GPU节点列表（Vg）
    
    返回:
        float: APLfail得分（容错得分）；若无法计算则返回None
    
    异常处理:
        - GPU节点数<2：无法计算路径，返回None
        - 交换机节点为空：返回原始图的GPU对平均路径长度
        - 移除交换机后无可达GPU对：该场景不计入整体平均
    """
    # 输入验证：检查节点是否都在图中
    all_nodes = set(G.nodes())
    invalid_switches = [n for n in switch_nodes if n not in all_nodes]
    invalid_gpus = [n for n in gpu_nodes if n not in all_nodes]
    if invalid_switches:
        raise ValueError(f"交换机节点 {invalid_switches} 不在图中")
    if invalid_gpus:
        raise ValueError(f"GPU节点 {invalid_gpus} 不在图中")
    
    # 基础检查：GPU节点数至少为2才能计算路径
    gpu_count = len(gpu_nodes)
    if gpu_count < 2:
        print("警告：GPU节点数量小于2，无法计算路径长度")
        return None
    
    # 生成所有不重复的GPU节点对（无序对，i<j）
    gpu_pairs = list(combinations(gpu_nodes, 2))
    total_pairs = len(gpu_pairs)
    if total_pairs == 0:
        return None
    
    # 存储每个交换机故障后的平均路径长度
    per_switch_apl = []
    
    # 遍历每个交换机节点，模拟故障（移除该节点）
    for failed_switch in switch_nodes:
        # 创建移除故障交换机后的子图（深拷贝避免修改原图）
        G_failed = G.copy()
        G_failed.remove_node(failed_switch)
        
        # 计算该故障场景下所有GPU对的路径长度总和
        path_length_sum = 0
        valid_pairs = 0  # 记录可达的GPU对数量
        
        for (u, v) in gpu_pairs:
            try:
                # 计算u和v之间的最短路径长度（无向图用shortest_path_length）
                path_len = nx.shortest_path_length(G_failed, source=u, target=v)
                path_length_sum += path_len
                valid_pairs += 1
            except nx.NetworkXNoPath:
                # 无可达路径，跳过该GPU对
                return float('inf')
            except nx.NodeNotFound:
                # 节点被移除（理论上不会触发，因为只移除交换机）
                continue
        
        # 只有存在可达GPU对时，才计算该场景的平均路径长度
        if valid_pairs > 0:
            apl = path_length_sum / valid_pairs
            per_switch_apl.append(apl)
    
    # 处理交换机为空的情况：返回原始图的GPU对平均路径长度
    if not switch_nodes:
        path_length_sum = 0
        valid_pairs = 0
        for (u, v) in gpu_pairs:
            try:
                path_len = nx.shortest_path_length(G, source=u, target=v)
                path_length_sum += path_len
                valid_pairs += 1
            except nx.NetworkXNoPath:
                continue
        if valid_pairs == 0:
            print("警告：原始图中无可达的GPU节点对")
            return None
        return path_length_sum / valid_pairs
    
    # 计算所有交换机故障场景的整体平均（APLfail）
    if not per_switch_apl:
        print("警告：所有交换机故障场景下均无可达的GPU节点对")
        return None
    apl_fail = sum(per_switch_apl) / len(per_switch_apl)
    return apl_fail