import os
import networkx as nx
import pydot
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

# Directory paths
input_dir = 'Combined_CPG'
output_dir = 'Matched_CPG'

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

            # Find leaf nodes in the vulnerable graph and the root of the fixed graph
            vulnerable_leaf_nodes = ['vulnerable_' + leaf for leaf in find_leaf_nodes(g_vulnerable)]  # Add prefix
            root_fixed = 'fixed_' + find_root(g_fixed)

            # Connect each vulnerable leaf node to the fixed root
            # To reverse the direction, switch the order of `leaf_node` and `root_fixed`
            for leaf_node in vulnerable_leaf_nodes:
                combined_graph.add_edge(leaf_node, root_fixed, label='Connection to Fixed Root', color='red', style='solid', penwidth='2.0')

            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')

        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
