import numpy as np
import argparse
import os
import pickle
import glob
from multiprocessing import Pool
from functools import partial
import random
import sent2vec
import networkx as nx

#Imports for tokenization via codebert model
import torch
from transformers import AutoTokenizer, AutoModel

#Imports for graph construction
from torch_geometric.data import Data, Batch
from torch_geometric.loader import DataLoader

edge_type_map = {
    "AST": 0,
    "CFG": 1,
    "DDG": 2,
    "CDG": 3
}


def parse_options():
    parser = argparse.ArgumentParser(description='Generate graph pkls')
    parser.add_argument('-i', '--input', help='The path of a dir which consists of some dot_files')
    parser.add_argument('-o', '--out', help='The path of output.', required=True)
    args = parser.parse_args()
    return args


def graph_extraction(dot):
    graph = nx.drawing.nx_pydot.read_dot(dot)
    return graph


def graph_generation(dot):
    try:
        label_node_map = {}
        nodes = []
        edges = []
        edge_features = []

        pdg = graph_extraction(dot)
        labels_dict = nx.get_node_attributes(pdg, 'label')

        # Initialize label_node_map with string keys
        for label in labels_dict.keys():
            label_node_map[label] = len(label_node_map)

        for label, code in labels_dict.items():
            code = code[code.find("(") + 1:-14].split('\\n')[0]
            nodes.append(code)  # Store code directly in nodes

        for edge in pdg.edges(data=True):
            # ... (rest of your edge processing logic) ...
            # Make sure edge[0] and edge[1] are keys in label_node_map
            edges.append([label_node_map[edge[0]], label_node_map[edge[1]]])

        # Convert nodes and edges to tensors (adjust data type as needed)
        x = [nodes]  # Keep nodes as a list of strings (no tensor conversion)
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor(edge_features, dtype=torch.float)

        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

        return data
    except Exception as e:
        print(f"Error processing {dot}: {e}")
        return None
def write_to_pkl(dot_file, out_path):
    graph = graph_generation(dot_file)
    dot_name = dot_file.split('/')[-1].split('.dot')[0]

    if graph is not None:
        print(f"Converting {dot_name}.dot to pickle...")
        out_pkl = out_path + dot_name + '.pkl'
        with open(out_pkl, 'wb') as f:
            pickle.dump(graph, f)


def main():

    out_path = "../Pickle/"

    os.makedirs(out_path, exist_ok=True)

    matched_cpg_path = "../Matched_CPG/"
    dot_files = glob.glob(matched_cpg_path + '*.dot')

    with Pool(18) as pool:
        pool.map(partial(write_to_pkl, out_path=out_path), dot_files)


if __name__ == '__main__':
    main()