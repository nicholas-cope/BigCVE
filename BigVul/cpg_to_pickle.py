import networkx as nx
import numpy as np
import argparse
import os
import pickle
import glob
from multiprocessing import Pool
from functools import partial
import random
from huggingface_hub import login, HfFolder

# This file is originaly based on VulCNN, but is fairly different now
# Imports for tokenization via codebert model
import torch
from transformers import AutoTokenizer

#Needed for Hellbender
'''
HF_TOKEN = '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'
HfFolder.save_token(HF_TOKEN)
login(HF_TOKEN, add_to_git_credential=True)
'''
# Imports for graph construction
from torch_geometric.data import Data, Batch
tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder")

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


def sentence_embedding(sentence):
    # Truncate sentence at 196 characters to avoid overrunning codebert tokenization max lengths
    # This only loses information on a small fraction of sentences,
    # usually just lengthy preprocessor directives like complex macros
    print(len(sentence))
    if len(sentence) > 196:
        sentence = sentence[:196]

    print(sentence)
    print(tokenizer.tokenize(sentence))
    tokens = tokenizer.tokenize(sentence)
    print(tokens)
    return tokenizer.convert_tokens_to_ids(tokens)


def graph_generation(dot):
    try:
        label_node_map = {}
        nodes = []
        edges = []
        edge_features = []
        edge_types = []

        pdg = graph_extraction(dot)
        #print(pdg)
        labels_dict = nx.get_node_attributes(pdg, 'label')
        #print(labels_dict)
        labels_code = dict()
        for label, all_code in labels_dict.items():
            # Remove parenthesis around info and the markdown at the end
            # No longer represents just code. Also includes some joern info at the beginning
            code = all_code
            labels_code[label] = code

        id = 0
        for label, code in labels_code.items():
            label_node_map[label] = id
            id += 1
            line_vec = sentence_embedding(code)
            max_length = 64
            sized_line_vec = [0] * max_length
            for i in range(0, min(len(line_vec), max_length) - 1):
                sized_line_vec[i] = line_vec[i]
            nodes.append(sized_line_vec)
        for edge in pdg.edges(data=True):
            # Manual determination of edge type
            edge_type = 0
            try:
                print(edge[2]["label"])
                edge_type_string = edge[2]["label"].replace("\"", "").split(":")[0]
            except:
                print("Edge feature parsing error")

            edge_types.append([edge_type])

            edges.append([label_node_map[edge[0]], label_node_map[edge[1]]])

            edge_features.append([0])

        data = Data(x=torch.tensor(nodes, dtype=torch.float),
                    edge_index=torch.tensor(edges, dtype=torch.long).t().contiguous(),
                    edge_attr=torch.tensor(edge_features, dtype=torch.float)
                    )

        return data
    except:
        print('exception')
        return None

def write_to_pkl(dot, out, existing_files):
    dot_name = dot.split('/')[-1].split('.dot')[0]
    if dot_name in existing_files:
        return None
    else:
        graph = graph_generation(dot)
        if graph == None:
            return None
        else:
            out_pkl = out + dot_name + '.pkl'
            with open(out_pkl, 'wb') as f:
                pickle.dump(graph, f)


def main():
    #args = parse_options()
    print("Running")
    dir_name = "Clean_Matched_CPG_2/"
    out_path = "vulFixing/"
    # Don't judge my global variables. This was the way VulCNN did it and I don't feel like changing the structure
    if dir_name[-1] == '/':
        dir_name = dir_name
    else:
        dir_name += "/"
    dotfiles = glob.glob(dir_name + '*.dot')

    if out_path[-1] == '/':
        out_path = out_path
    else:
        out_path += '/'

    if not os.path.exists(out_path):
        os.makedirs(out_path)
    existing_files = glob.glob(out_path + "/*.pkl")
    existing_files = [f.split('.pkl')[0] for f in existing_files]

    # Shuffling takes some computation time, but it overall speeds up the process
    # because it splits up groups of longer cpgs more evenly between the workers
    # so there aren't 1-3 workers left processing much longer than the others
    random.shuffle(dotfiles)
    pool = Pool(10)
    pool.map(partial(write_to_pkl, out=out_path, existing_files=existing_files), dotfiles)


if __name__ == '__main__':
    main()