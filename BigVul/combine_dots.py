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
    function_name = Path(sample_folder).name
    #Extracting the number
    function_number = ''.join(filter(str.isdigit, function_name))

    fixed_folder = Path(sample_folder) / f"fixed{function_number}" / f"fixed{function_number}.cpp"
    vulnerable_folder = Path(sample_folder) / f"vulnerable{function_number}" / f"vulnerable{function_number}.cpp"

    #Specific Graph We Are Combining
    fixed_dot_file = fixed_folder / "check_rodc_critical_attribute.dot"
    vulnerable_dot_file = vulnerable_folder / "check_rodc_critical_attribute.dot"

    #Checking if .dot fiels exists
    if not fixed_dot_file.exists() or not vulnerable_dot_file.exists():
        print(f"Missing .dot files for {function_name}. Skipping")
        return

    #To Catch Errors without killing the program
    try:
        #Reading the fixed graph
        fixed_graph = nx.drawing.nx_pydot.read_dot(fixed_dot_file)
        labels_dict = dict(nx.get_node_attributes(fixed_graph, 'label'))
        for val in labels_dict.values():
            if str(val)[2:9] == "UNKNOWN":
                print("Bad Joern parsing. Abandoning combination.")
                return

        #Reading the vulnerable graph
        vulnerable_graph = nx.drawing.nx_pydot.read_dot(vulnerable_dot_file)
        labels_dict = dict(nx.get_node_attributes(vulnerable_graph, 'label'))
        for val in labels_dict.values():
            if str(val)[2:9] == "UNKNOWN":
                print("Bad Joern parsing. Abandoning combination.")
                return

    except:
        print(f"Could not read .dot file for {function_name}. Skipping")
        return


if __name__ == '__main__':
    folders = glob.glob(raw_cpgs_location + "*/")

    with Pool(12) as p:
        p.map(handle_sample, folders)