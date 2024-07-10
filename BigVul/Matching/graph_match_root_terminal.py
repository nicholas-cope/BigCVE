import os
import re
import networkx as nx
import pydot
import shutil
import subprocess
import cpg_to_pickle
import dot_cleaner

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

#Modified Directory Paths
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
output_root = os.path.join(os.path.dirname(script_dir))  # Parent directory of the scripts folder

# Define output directories relative to the output_root
output_dir = os.path.join(output_root, 'Matched_CPG_Root_Terminal')
print(output_dir)
clean_dot_dir = os.path.join(output_root, 'Clean_Matched_CPG_Root_Termninal')
pkl_dir = os.path.join(output_root, 'rootTermInvPKL')

# Define the input directory
input_dir = os.path.join(output_root, 'Combined_CPG')

# Ensure the output directory exists
# Create the output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_dot_dir, exist_ok=True)
os.makedirs(pkl_dir, exist_ok=True)

os.makedirs(output_dir, exist_ok=True)


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
dot_cleaner.clean_dot_files(output_dir, clean_dot_dir)
print("Moving to pkl")
cpg_to_pickle.main(clean_dot_dir, pkl_dir)

