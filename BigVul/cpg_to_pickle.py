import networkx as nx
import numpy as np
import argparse
import os
import pickle
import glob
from multiprocessing import Pool
from functools import partial
import random
from huggingface_hub import login
#access_token = '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'
#login(token= access_token)

# This file is originaly based on VulCNN, but is fairly different now

# Imports for tokenization via codebert model
import torch
from transformers import AutoTokenizer

# Imports for graph construction
from torch_geometric.data import Data, Batch
from torch_geometric.loader import DataLoader
access_token = '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'
#HF_DATASETS_OFFLINE=1
#HF_HUB_OFFLINE=1
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
            # code = all_code[all_code.find("(") + 1:-14].split('\\n')[0]
            code = all_code
            # code = code.replace("static void", "void")
            labels_code[label] = code
        #print('fine 1')
        #print(labels_code)

        id = 0
        for label, code in labels_code.items():
            print('fine 1.0')
            #print(label)
            label_node_map[label] = id
            id += 1
            print('fine 1.1')
            print(code)
            line_vec = sentence_embedding(code)
            print('fine 1.2')
            max_length = 64
            sized_line_vec = [0] * max_length
            for i in range(0, min(len(line_vec), max_length) - 1):
                sized_line_vec[i] = line_vec[i]
            nodes.append(sized_line_vec)
        print('fine 2')
        for edge in pdg.edges(data=True):
            # Tokenization of edge features
            max_edge_length = 16
            sized_edge_vec = [0] * max_edge_length
            try:
                edge_type_string = edge[2]["label"]
                edge_vec = sentence_embedding(edge_type_string)
                for i in range(0, min(len(edge_vec), max_edge_length) - 1):
                    sized_edge_vec[i] = edge_vec[i]
            except:
                print("Edge feature parsing error")
            edge_features.append(sized_edge_vec)

            # Manual determination of edge type
            edge_type = 0
            try:
                edge_type_string = edge[2]["label"].replace("\"", "").split(":")[0]
                edge_type = edge_type_map[edge_type_string]
            except:
                print("Edge feature parsing error")
            edge_types.append([edge_type])

            edges.append([label_node_map[edge[0]], label_node_map[edge[1]]])

        data = Data(x=torch.tensor(nodes, dtype=torch.float),
                    edge_index=torch.tensor(edges, dtype=torch.long).t().contiguous(),
                    edge_attr=torch.tensor(edge_features, dtype=torch.float),
                    edge_type=torch.tensor(edge_type, dtype=torch.long)
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
        print(dot_name)
        print('HI')
        graph = graph_generation(dot)
        if graph == None:
            return None
        else:
            out_pkl = out + dot_name + '.pkl'
            with open(out_pkl, 'wb') as f:
                print('test')
                pickle.dump(graph, f)


def main():
    args = parse_options()
    dir_name = args.input
    out_path = args.out
    # Don't judge my global variables. This was the way VulCNN did it and I don't feel like changing the structure
    # global tokenizer
    #tokenizer = AutoTokenizer.from_pretrained("neulab/codebert-c")
    #tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder", token = access_token, local_files_only=True)
    # tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder")

    # tokens = tokenizer.tokenize("<(METHOD,ssl_get_algorithm2)")
    # print(tokens)

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

##out_path = "Pickle/"

  ##  if not os.path.exists(out_path):
   ##     os.makedirs(out_path)


 ##   matched_cpg_path = "Matched_CPG/"