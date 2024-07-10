import os
import networkx as nx
import pydot
import dot_cleaner
import cpg_to_pickle
#To generate the CPG's where terminal nodes of the vulnerable function are connected to the root node
#of the fixed function
#vulnerable -> fixed
def load_graph(file_path):
    """Loads a graph from a DOT file."""
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

def find_root(graph):
    """Finds the root node (node with no incoming edges) in a graph."""
    for node in graph.nodes:
        if graph.in_degree(node) == 0:
            return node
    return None

def find_leaf_nodes(graph):
    """Finds all leaf nodes (nodes with no outgoing edges) in a graph."""
    leaf_nodes = []
    for node in graph.nodes:
        if graph.out_degree(node) == 0:
            leaf_nodes.append(node)
    return leaf_nodes

#Modified Directory Paths
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
output_root = os.path.join(os.path.dirname(script_dir))  # Parent directory of the scripts folder

# Define output directories relative to the output_root
output_dir = os.path.join(output_root, 'Matched_CPG_Terminal')
clean_dot_dir = os.path.join(output_root, 'Clean_Matched_CPG_Terminal')
pkl_dir = os.path.join(output_root, 'termPKL')

# Define the input directory
input_dir = os.path.join(output_root, 'Combined_CPG')

# Ensure the output directory exists
# Create the output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_dot_dir, exist_ok=True)
os.makedirs(pkl_dir, exist_ok=True)

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

            # Find leaf nodes in the vulnerable graph and the root of the fixed graph
            vulnerable_leaf_nodes = ['vulnerable_' + leaf for leaf in find_leaf_nodes(g_vulnerable)]  # Add prefix
            root_fixed = 'fixed_' + find_root(g_fixed)

            # Connect each vulnerable leaf node to the fixed root
            # To reverse the direction, switch the order of `leaf_node` and `root_fixed`
            for leaf_node in vulnerable_leaf_nodes:
                combined_graph.add_edge(leaf_node, root_fixed)

            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')

        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")

print("Moving to cleaning")
dot_cleaner.clean_dot_files(output_dir, clean_dot_dir)
print("Moving to pkl")
cpg_to_pickle.main(clean_dot_dir, pkl_dir)

