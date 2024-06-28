#Just the same thing as cpg_to_pickle but for Match_CPG_Inverse

#Thanks Miles
import networkx as nx
import pickle
import glob
import os
from multiprocessing import Pool
from functools import partial


def write_to_pkl(dot_file, out_path, existing_files):
    graph = nx.drawing.nx_pydot.read_dot(dot_file)
    dot_name = dot_file.split('/')[-1].split('.dot')[0]

    if dot_name in existing_files:
        return None

    print(f"Converting {dot_name}.dot to pickle...")

    out_pkl = out_path + dot_name + '.pkl'
    with open(out_pkl, 'wb') as f:
        pickle.dump(graph, f)


def main():
    out_path = "../Pickle_Inverse/"  # Adjust output path if needed

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    matched_cpg_path = "../Matched_CPG_Inverse/"
    dot_files = glob.glob(matched_cpg_path + '*.dot')

    # Check existing files for faster processing
    existing_files = glob.glob(out_path + "/*.pkl")
    existing_files = [f.split('/')[-1].split('.pkl')[0] for f in existing_files]

    pool = Pool(18)  # You can adjust the number of processes in Pool()
    pool.map(partial(write_to_pkl, out_path=out_path, existing_files=existing_files), dot_files)


if __name__ == '__main__':
    main()