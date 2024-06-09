#Thanks Miles Once Again
from multiprocessing import Pool
import os
import glob
import networkx as nx
from pathlib import Path

raw_cpgs_location = "CPG/"
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

    # Operation is assumed to be normal at this point
    overall_graph = nx.MultiDiGraph()
    for dot in folder.iterdir():
        overall_graph = nx.compose(overall_graph, nx.drawing.nx_pydot.read_dot(dot))

    out = output_location + Path(sample_folder).name + ".dot"

    nx.nx_pydot.write_dot(overall_graph, out)


folders = glob.glob(raw_cpgs_location + "*/")

with Pool(12) as p:
    p.map(handle_sample, folders)