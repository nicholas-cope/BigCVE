#Thanks Miles Once Again
#Checking what the file looks like
# dot -Tpng filename.dot -o outfile.png
import os
import networkx as nx
import glob
from pathlib import Path
from multiprocessing import Pool, freeze_support

raw_cpgs_location = "CPG/function1/fixed1"
output_location = "Combined_CPG/"


def handle_sample(sample_folder):
    print(sample_folder)
    folder = Path(sample_folder)
    num_dots = len(list(folder.iterdir()))

    if num_dots == 0:
        print("No dot files.")
        return
    elif num_dots == 1:
        graph = nx.drawing.nx_pydot.read_dot(list(folder.iterdir())[0])
        labels_dict = dict(nx.get_node_attributes(graph, 'label'))
        for val in labels_dict.values():
            if str(val)[2:9] == "UNKNOWN":
                print("Bad Joern parsing. Abandoning combination.")
                return

    print("Creating overall graph...")
    overall_graph = nx.MultiDiGraph()
    for dot in folder.iterdir():
        print(f"  Reading: {dot}")
        graph = nx.drawing.nx_pydot.read_dot(dot)

        print(f"    Before quoting: {list(graph.nodes(data=True))[:5]}")
        # Quote node names and attribute values containing colons
        for node in graph.nodes():
            if ':' in node:
                graph = nx.relabel_nodes(graph, {node: f'"{node}"'})
            for attr, value in graph.nodes[node].items():
                if ':' in value:
                    graph.nodes[node][attr] = f'"{value}"'

        print(f"    After quoting: {list(graph.nodes(data=True))[:5]}")  # Convert to list before slicing

        overall_graph = nx.compose(overall_graph, graph)
        print(f"    Composed graph size: {len(overall_graph.nodes())} nodes")


    out = output_location + Path(sample_folder).name + ".dot"
    print(f"Writing combined graph to: {out}")
    nx.nx_pydot.write_dot(overall_graph, out)
    print("--- Finished ---\n")

if __name__ == '__main__':
    freeze_support()  # Call freeze_support to prepare for multiprocessing
    folders = glob.glob(raw_cpgs_location + "*/")
    print("Folders:", folders)  # Add debugging print

    with Pool(12) as p:
        p.map(handle_sample, folders)
    '''
    # Create paths to fixed and vulnerable subfolders
    fixed_folder = folder / f"fixed{function_number}"
    vuln_folder = folder / f"vulnerability{function_number}"

    # Initialize empty graphs to store combined graphs
    vuln_graph = nx.MultiDiGraph()
    fixed_graph = nx.MultiDiGraph()

    # Find root nodes in each graph (nodes with no incoming edges)
    fixed_roots = [n for n, d in fixed_graph.in_degree() if d == 0]
    vuln_roots = [n for n, d in vuln_graph.in_degree() if d == 0]

    # Combine the final vulnerable and fixed graphs
    combined_graph = nx.compose(vuln_graph, fixed_graph)

    # Add "fix" edges from each vulnerable root to each fixed root
    for vuln_root in vuln_roots:
        for fixed_root in fixed_roots:
            combined_graph.add_edge(vuln_root, fixed_root, label="fix")

    # Save the combined graph with fix edges to the output directory
    out = Path(output_location) / (folder.name + ".dot")  # Convert output_location to Path
    nx.drawing.nx_pydot.write_dot(combined_graph, out)
'''

