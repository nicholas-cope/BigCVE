import os
import re
import networkx as nx
import pydot
import shutil
import subprocess

def load_graph(file_path):
    """Loads a graph from a DOT file."""
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

def find_roots(graph):
    """Finds root nodes (nodes with no incoming edges) in a graph."""
    return [node for node in graph.nodes if graph.in_degree(node) == 0]

def find_sinks(graph):
    """Finds sink nodes (nodes with no outgoing edges) in a graph."""
    return [node for node in graph.nodes if graph.out_degree(node) == 0]

input_dir = 'Combined_CPG/'
output_dir = 'Matched_CPG_Root_Terminal/'

os.makedirs(output_dir, exist_ok=True)

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

            # Connect and color root nodes (red)
            vuln_roots = find_roots(g_vulnerable)
            fixed_roots = find_roots(g_fixed)
            for root_v, root_f in zip(vuln_roots, fixed_roots):  # Assuming same number of roots
                combined_graph.add_edge('vulnerable_' + root_v, 'fixed_' + root_f)

            # Connect and color sinks (green)
            sink_vulnerable_nodes = find_sinks(combined_graph.subgraph([n for n in combined_graph if n.startswith('vulnerable_')]))
            sink_fixed_nodes = find_sinks(combined_graph.subgraph([n for n in combined_graph if n.startswith('fixed_')]))
            for sink_v, sink_f in zip(sink_vulnerable_nodes, sink_fixed_nodes):
                combined_graph.add_edge(sink_v, sink_f)

            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)

        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
    
print("Moving to cleaning")
subprocess.run(["python", "dot_cleaner_root.py"], check=True)
print("Moving to pkl")
subprocess.run(["python", "cpg_to_pickle_root.py"], check=True)

