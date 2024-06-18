import os
import networkx as nx
import pydot

# Function to load a graph from a DOT file
def load_graph(file_path):
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

# Function to identify the root node in a graph (node with no incoming edges)
def find_root(graph):
    for node in graph.nodes:
        if graph.in_degree(node) == 0:
            return node
    return None

# Function to combine two graphs by adding a directed edge from the root of g1 to the root of g2
def combine_graphs(g1, g2):
    combined_graph = nx.compose(g1, g2)
    # Identify corresponding nodes in both graphs
    for node in g2.nodes:
        if node in g1.nodes:
            combined_graph.nodes[node]['label'] = 'fix'  # Mark as fixed
            for pred in g1.predecessors(node):
                combined_graph.add_edge(pred, node, label='fix', color='red', style='bold', penwidth='2.0')  # Mark edges as fixed

    return combined_graph

# Directory paths
input_dir = 'Combined_CPG'
output_dir = 'Matched_CPG'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over each function directory
for function in os.listdir(input_dir):
    function_path = os.path.join(input_dir, function)
    if os.path.isdir(function_path):
        #Extracting function number
        #Fixes only converting the first 9 files
        function_number = ''.join(filter(str.isdigit, function))

        # Load the vulnerable and fixed graphs
        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")

        if os.path.exists(vulnerable_file) and os.path.exists(fixed_file):
            g_vulnerable = load_graph(vulnerable_file)
            g_fixed = load_graph(fixed_file)

            # Combine the graphs
            combined_graph = combine_graphs(g_vulnerable, g_fixed)

            # Output the combined graph to the output directory
            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')
        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
