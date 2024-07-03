import os
import networkx as nx
import pydot
import subprocess
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

# Iterate over each function directory
for function in os.listdir(input_dir):
    function_path = os.path.join(input_dir, function)
    if os.path.isdir(function_path):
        function_number = ''.join(filter(str.isdigit, function))

        # Load the vulnerable and fixed graphs
        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")

        if os.path.exists(vulnerable_file) and os.path.exists(fixed_file):
            g_vulnerable = load_graph(vulnerable_file)
            g_fixed = load_graph(fixed_file)

            # Create a new graph that includes both vulnerable and fixed graphs as subgraphs
            combined_graph = nx.union(g_vulnerable, g_fixed, rename=('vulnerable_', 'fixed_'))

            # Find leaf nodes in the fixed graph and the root of the vulnerable graph
            fixed_leaf_nodes = ['fixed_' + leaf for leaf in find_leaf_nodes(g_fixed)]  # Add prefix
            root_vulnerable = 'vulnerable_' + find_root(g_vulnerable)

            # Connect each fixed leaf node to the vulnerable root
            # Direction: Fixed leaf nodes --> Vulnerable root node
            for leaf_node in fixed_leaf_nodes:
                combined_graph.add_edge(leaf_node, root_vulnerable, label='Connection to Vulnerable Root', color='blue', style='dashed', penwidth='2.0')

            # Output the combined graph to the output directory
            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')
        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
print("Moving to cleaning")
subprocess.run(["python", "dot_cleaner_inverse.py"], check=True)
print("Moving to pkl")
subprocess.run(["python", "cpg_to_pickle_inverse.py"], check=True)
