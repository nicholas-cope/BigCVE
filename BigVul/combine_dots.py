#Thanks Miles Once Again
from multiprocessing import Pool
import os
import glob
import pydot
import networkx as nx
from pathlib import Path

raw_cpgs_location = "CPG/"
output_location = "Combined_CPG/"


def handle_sample(sample_folder):
    print(sample_folder)
    folder = Path(sample_folder)
    function_number = ''.join(filter(str.isdigit, sample_folder))

    fixed_folder = f"fixed{function_number}"
    vuln_folder = f"vulnerability{function_number}"

    dot_files = []
    for sub_folder in [fixed_folder, vuln_folder]:
        for item in os.listdir(folder / sub_folder):
            item_path = folder / sub_folder / item
            # Checking for "_global_.dot"
            if item.endswith(".cpp") and os.path.isdir(item_path):
                dot_path = item_path / "_global_.dot"
                if dot_path.exists():
                    dot_files.append(dot_path)
    if not dot_files:
        print("No relevant dot files found.")
        return

    # Validation (similar to original)
    for dot in dot_files:
        graph = nx.drawing.nx_pydot.read_dot(dot)
        labels_dict = dict(nx.get_node_attributes(graph, 'label'))
        if any(str(val)[2:9] == "UNKNOWN" for val in labels_dict.values()):
            print("Bad Joern parsing. Abandoning combination.")
            return

    # Combine the graphs
    overall_graph = nx.MultiDiGraph()
    for dot in dot_files:
        overall_graph = nx.compose(overall_graph, nx.drawing.nx_pydot.read_dot(dot))

    # Save the combined graph
    out = output_location + Path(sample_folder).name + ".dot"
    nx.nx_pydot.write_dot(overall_graph, out)


if __name__ == "__main__":
    # Get all the sample folders in the raw CPG location
    folders = [f.path for f in os.scandir(raw_cpgs_location) if f.is_dir()]
    with Pool(processes=15) as pool:
        pool.map(handle_sample, folders)