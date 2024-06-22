import os
import networkx as nx
import pydot
from xml.sax.saxutils import escape
# dot -Tpng filename.dot -o outfile.png

import os
import networkx as nx
import pydot
from xml.sax.saxutils import escape


def load_graph(file_path):
    (graph,) = pydot.graph_from_dot_file(file_path)
    return nx.nx_pydot.from_pydot(graph)

def find_root(graph):
    for node in graph.nodes:
        if graph.in_degree(node) == 0:
            return node
    return None

def match_graphs(g1, g2):
    # Create the "Fix Point" node first
    bridge_node = "bridge"
    combined_graph = nx.DiGraph()
    combined_graph.add_node(bridge_node, label="Fix Point")

    # Add nodes and edges from vulnerable and fixed graphs
    for node in g1.nodes:
        combined_graph.add_node(node, **g1.nodes[node])
    for edge in g1.edges:
        # Filter out invalid edge attributes
        valid_edge_attrs = {
            key: value
            for key, value in g1.edges[edge].items()
            if key in ['color', 'style', 'penwidth', 'label']  # Adjust as needed
        }
        # Unpack edge as separate arguments, then unpack attributes
        u, v = edge
        combined_graph.add_edge(u, v, **valid_edge_attrs)

    for node in g2.nodes:
        combined_graph.add_node(node, **g2.nodes[node])
    for edge in g2.edges:
        # Filter out invalid edge attributes
        valid_edge_attrs = {
            key: value
            for key, value in g2.edges[edge].items()
            if key in ['color', 'style', 'penwidth', 'label']  # Adjust as needed
        }
        # Unpack edge as separate arguments, then unpack attributes
        u, v = edge
        combined_graph.add_edge(u, v, **valid_edge_attrs)

    # Identify root nodes and connect to "Fix Point"
    root_g1 = find_root(g1)
    root_g2 = find_root(g2)

    if root_g1:
        combined_graph.add_edge(bridge_node, root_g1, **{'color':'gray', 'style':'dashed', 'penwidth':'1.0'})
    if root_g2:
        combined_graph.nodes[root_g2]['shape'] = 'box'
        combined_graph.nodes[root_g2]['label'] = escape(g2.nodes[root_g2].get('label', '')) + " (fix)"
        combined_graph.add_edge(bridge_node, root_g2, **{'color':'red', 'style':'bold', 'penwidth':'2.0', 'label':"Fix"})

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
        # Load the vulnerable and fixed graphs (no change)
        vulnerable_file = os.path.join(function_path, f"vulnerability{function_number}.dot")
        fixed_file = os.path.join(function_path, f"fixed{function_number}.dot")

        if os.path.exists(vulnerable_file) and os.path.exists(fixed_file):
            try:
                g_vulnerable = load_graph(vulnerable_file)
                g_fixed = load_graph(fixed_file)

                # Match the graphs using disjoint union
                combined_graph = match_graphs(g_vulnerable, g_fixed)

                # Output the combined graph (no change)
                output_file = os.path.join(output_dir, f'{function}.dot')
                nx.drawing.nx_pydot.write_dot(combined_graph, output_file)
                print(f'Combined CPG for {function} written to {output_file}')

            except pydot.Error as e:
                print(f'Error processing {function}: {e}')  # More informative error message
        else:
            print(f"Warning: Missing vulnerability or fixed file for {function}")
