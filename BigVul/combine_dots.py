#Thanks Miles Once Again
#Checking what the file looks like
# dot -Tpng filename.dot -o outfile.png
import networkx as nx
import glob
from pathlib import Path
from multiprocessing import Pool, freeze_support

raw_cpgs_location = "CPG/"
output_location = "Combined_CPG/"

"""
   Combines all .dot files within a single sample folder.

   This function performs the following steps:
       1. Checks if the folder contains .dot files.
       2. Handles special cases (empty folder or single file).
       3. Iterates over each .dot file:
           - Reads the graph from the file.
           - Quotes node names/attributes containing colons (for pydot compatibility).
           - Combines the graph with the overall graph.
       4. Saves the combined graph to a new .dot file.

   Args:
       sample_folder (str): Path to the folder containing .dot files.
   """
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
    overall_graph = nx.MultiDiGraph()
    for dot in folder.iterdir():
        graph = nx.drawing.nx_pydot.read_dot(dot)
        # Quote node names and attribute values containing colons
        for node in graph.nodes():
            if ':' in node:
                graph = nx.relabel_nodes(graph, {node: f'"{node}"'})
            for attr, value in graph.nodes[node].items():
                if ':' in value:
                    graph.nodes[node][attr] = f'"{value}"'

        overall_graph = nx.compose(overall_graph, graph)


    out = output_location + Path(sample_folder).name + ".dot"
    nx.nx_pydot.write_dot(overall_graph, out)

if __name__ == '__main__':
    freeze_support()

    all_folders = []
    for function_dir in glob.glob(raw_cpgs_location + "*/"):
        for subfolder in ["fixed", "vulnerability"]:
            folders = glob.glob(function_dir + subfolder + "*/")
            all_folders.extend(folders)

    print("Folders to process:", all_folders)

    with Pool(12) as p:  # Adjust number of processes if needed
        p.map(handle_sample, all_folders)
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

