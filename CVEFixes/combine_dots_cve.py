#Thanks Miles Once Again
#Checking what the file looks like
# dot -Tpng filename.dot -o outfile.png
import shutil
import networkx as nx
import glob
from pathlib import Path
from multiprocessing import Pool, freeze_support

raw_cpgs_location = "/home/ybc67/data/BigCVE/CVEFixes/CPG/"
output_location = "/home/ybc67/data/BigCVE/CVEFixes/Combined_CPG/"

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

    #Checking for an empty folder
    if num_dots == 0:
        print("No dot files.")
        return
    # Handle single file case so no need to combine
    elif num_dots == 1:
        graph = nx.drawing.nx_pydot.read_dot(list(folder.iterdir())[0])
        labels_dict = dict(nx.get_node_attributes(graph, 'label'))
        # Joern-specific check for bad parsing (optional)
        for val in labels_dict.values():
            if str(val)[2:9] == "UNKNOWN":
                print("Bad Joern parsing. Abandoning combination.")
                return
    # If it's more than 1, create an empty graph to begin with, to which we will
    # add (compose) all the other graphs
    overall_graph = nx.MultiDiGraph()
    # Combine multiple .dot files
    for dot in folder.iterdir():
        graph = nx.drawing.nx_pydot.read_dot(dot)
        # Quote node names and attribute values containing colons (fixing pydot issue)
        for node in graph.nodes():
            if ':' in node:
                graph = nx.relabel_nodes(graph, {node: f'"{node}"'})
            for attr, value in graph.nodes[node].items():
                if ':' in value:
                    graph.nodes[node][attr] = f'"{value}"'

        #Combining Graphs
        overall_graph = nx.compose(overall_graph, graph)

    # Generate output file name and save
    out = output_location + Path(sample_folder).name + ".dot"
    nx.nx_pydot.write_dot(overall_graph, out)

#Organizing the Files
def organize_files(output_location):
    """
    Organizes combined .dot files into function-specific subfolders, maintaining fixed/vulnerability distinction.
    """
    for dot_file in Path(output_location).glob("*.dot"):
        filename = dot_file.name

        # Extract the file type and function number (handling potential mismatches)
        if filename.startswith("fixed"):
            file_type = "fixed"
            function_num = filename[5:-4]
        elif filename.startswith("vulnerability"):
            file_type = "vulnerability"
            function_num = filename[13:-4]
        else:
            print(f"Skipping file with unexpected name: {filename}")
            continue

        # Create the function folder
        function_dir = Path(output_location) / f"function{function_num}"
        function_dir.mkdir(parents=True, exist_ok=True)  # Create parent directories if needed

        # Move the file to the appropriate subfolder
        shutil.move(dot_file, function_dir / filename)  # Keep original filename

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Required for multiprocessing
    freeze_support()

    try:
        import pydot
    except ModuleNotFoundError:
        import subprocess
        subprocess.check_call(["python", "-m", "pip", "install", "pydot", "pydotplus"])
    # Collect all "fixed" and "vulnerability" folders within function directories
    all_folders = []
    for function_dir in glob.glob(raw_cpgs_location + "*/"):
        for subfolder in ["fixed", "vulnerability"]:
            folders = glob.glob(function_dir + subfolder + "*/")
            all_folders.extend(folders)

    #Debugging output
    print("Folders to process:", all_folders)

    # Process folders in parallel
    with Pool(12) as p:  # Adjust number of processes if needed
        p.map(handle_sample, all_folders)

    organize_files(output_location)