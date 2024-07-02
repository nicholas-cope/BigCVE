import os
import networkx as nx
import pydot
import os
import subprocess
import networkx as nx
import pydot
from multiprocessing import Pool
#To generate the CPG's where terminal nodes of the fixed function are connected to the root node
#of the vulnerable  function
#fixed -> vulnerable
# Function to load a graph from a DOT file
def load_graph(file_path):
    """Loads a graph from a DOT file."""
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

# Function to identify the root node in a graph (node with no incoming edges)
def find_root(graph):
    """Finds the root node (node with no incoming edges) in a graph."""
    for node in graph.nodes:
        if graph.in_degree(node) == 0:
            return node
    return None

# Function to identify all leaf nodes (nodes with no outgoing edges) in a graph
def find_leaf_nodes(graph):
    """Finds all leaf nodes (nodes with no outgoing edges) in a graph."""
    leaf_nodes = []
    for node in graph.nodes:
        if graph.out_degree(node) == 0:
            leaf_nodes.append(node)
    return leaf_nodes

# Directory paths
input_dir = 'Combined_CPG/'
output_dir = 'Matched_CPG_Inverse/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def process_function(function):
    function_path = os.path.join(input_dir, function)
    if os.path.isdir(function_path):
        function_number = ''.join(filter(str.isdigit, function))

        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")
        output_file = os.path.join(output_dir, f'{function}.dot')

        if os.path.exists(vulnerable_file) and os.path.exists(fixed_file) and not os.path.exists(output_file):
            g_vulnerable = load_graph(vulnerable_file)
            g_fixed = load_graph(fixed_file)
            combined_graph = nx.union(g_vulnerable, g_fixed, rename=('vulnerable_', 'fixed_'))

            # Find leaf nodes in the FIXED graph and the root of the VULNERABLE graph
            fixed_leaf_nodes = ['fixed_' + leaf for leaf in find_leaf_nodes(g_fixed)]
            root_vulnerable = 'vulnerable_' + find_root(g_vulnerable)

            # Connect each fixed leaf node to the vulnerable root
            for leaf_node in fixed_leaf_nodes:
                combined_graph.add_edge(leaf_node, root_vulnerable)

            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')

        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")

if __name__ == "__main__":
    try:
        # Create a pool of worker processes (adjust the number based on your CPU cores)
        with Pool(18) as pool:  # Defaults to the number of CPU cores
            pool.map(process_function, os.listdir(input_dir))

        print("Moving to cleaning")
        subprocess.run(["python", "dot_cleaner_inverse.py"], check=True)
        print("Moving to pkl")
        subprocess.run(["python", "cpg_to_pickle_inverse.py"], check=True)

    except subprocess.CalledProcessError:
        print("Error occurred during script execution or cleanup.")