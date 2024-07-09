import os
import networkx as nx
import pydot
import shutil

def load_graph(file_path):
    """Loads a graph from a DOT file."""
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

def find_sinks(graph):
    return [node for node in graph.nodes if graph.out_degree(node) == 0]

input_dir = 'Combined_CPG'
output_dir = 'Matched_CPG_Colored'

os.makedirs(output_dir, exist_ok=True)

# Iterate over each function directory (no need for temporary directory)
for function in os.listdir(input_dir):
    function_path = os.path.join(input_dir, function)
    if os.path.isdir(function_path):
        function_number = ''.join(filter(str.isdigit, function))
        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")

        if os.path.exists(vulnerable_file) and os.path.exists(fixed_file):
            g_vulnerable = load_graph(vulnerable_file)
            g_fixed = load_graph(fixed_file)
            combined_graph = nx.union(g_vulnerable, g_fixed, rename=('vulnerable_', 'fixed_'))

            # Connect and color SIMILAR nodes (yellow) (this also connects the root node)
            for node_v in combined_graph.nodes:
                if node_v.startswith('vulnerable_') and not node_v.endswith("entry") and not node_v.endswith("exit"):
                    node_f = node_v.replace('vulnerable_', 'fixed_')
                    if node_f in combined_graph and combined_graph.nodes[node_v] == combined_graph.nodes[node_f]:  # Check for same attributes
                        combined_graph.add_edge(node_v, node_f, color='yellow', label="SIMILAR_NODE")

            # Connect and color sinks (green)
            sink_vulnerable_nodes = find_sinks(combined_graph.subgraph([n for n in combined_graph if n.startswith('vulnerable_')]))
            sink_fixed_nodes = find_sinks(combined_graph.subgraph([n for n in combined_graph if n.startswith('fixed_')]))
            for sink_v, sink_f in zip(sink_vulnerable_nodes, sink_fixed_nodes):
                combined_graph.add_edge(sink_v, sink_f, color='green', label="SINK_EDGE")

            output_file = os.path.join(output_dir, f'{function}_final.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)

        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
