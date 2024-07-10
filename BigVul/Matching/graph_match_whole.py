import os
import networkx as nx
import pydot
import cpg_to_pickle
import dot_cleaner

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

#Modified Directory Paths
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
output_root = os.path.join(os.path.dirname(script_dir))  # Parent directory of the scripts folder

# Define output directories relative to the output_root
output_dir = os.path.join(output_root, 'Matched_CPG_Whole')
clean_dot_dir = os.path.join(output_root, 'Clean_Matched_CPG_Whole')
pkl_dir = os.path.join(output_root, 'wholePKL')

# Define the input directory
input_dir = os.path.join(output_root, 'Combined_CPG')

# Ensure the output directory exists
# Create the output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_dot_dir, exist_ok=True)
os.makedirs(pkl_dir, exist_ok=True)

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

print("Moving to cleaning")
dot_cleaner.clean_dot_files(output_dir, clean_dot_dir)
print("Moving to pkl")
cpg_to_pickle.main(clean_dot_dir, pkl_dir)