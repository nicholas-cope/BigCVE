import os
import networkx as nx
import pydot
import os
import subprocess
import networkx as nx
import pydot
from multiprocessing import Pool
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

input_dir = 'Combined_CPG/'
output_dir = 'Matched_CPG/'

os.makedirs(output_dir, exist_ok=True)

def process_function(function):
    function_path = os.path.join(input_dir, function)
    if os.path.isdir(function_path):
        function_number = ''.join(filter(str.isdigit, function))
        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")

        g_vulnerable = load_graph(vulnerable_file)
        g_fixed = load_graph(fixed_file)

        if g_vulnerable and g_fixed:  # Ensure both graphs loaded successfully

            combined_graph = nx.union(g_vulnerable, g_fixed, rename=('vulnerable_', 'fixed_'))

            vulnerable_leaf_nodes = ['vulnerable_' + leaf for leaf in find_leaf_nodes(g_vulnerable)]
            root_fixed = 'fixed_' + find_root(g_fixed)

            # Connect leaf nodes to root, adding edge attributes for visualization
            for leaf_node in vulnerable_leaf_nodes:
                combined_graph.add_edge(
                    leaf_node, root_fixed,
                )

            output_file = os.path.join(output_dir, f'{function}.dot')
            nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
            print(f'Combined CPG for {function} written to {output_file}')
        else:
            print(f"Warning: Missing or invalid graph files for {function}")


if __name__ == "__main__":
    try:
        # Create a pool of worker processes (adjust the number based on your CPU cores)
        with Pool(18) as pool:
            pool.map(process_function, os.listdir(input_dir))


        # Run the cleaner script
        print("Moving to cleaning")
        subprocess.run(["python", "dot_cleaner.py"], check=True)
        print("Moving to pkl")
        subprocess.run(["python", "cpg_to_pickle.py"], check=True)

    except subprocess.CalledProcessError:
        print("Error occurred during script execution or cleanup.")
# Directory paths






