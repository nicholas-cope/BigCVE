import os
import re

#This code is used so that the IDs can easily be used as indices in a graph when covnerted into a PKL file
#once sent into VulGNN


def renumber_dot_file(content, node_prefix="", start_index=1):
    """
    Renumbers node IDs in a .dot file content string.

    Args:
        content (str): The content of the .dot file.
        node_prefix (str, optional): The prefix to use for the new node IDs (default is "node").
        start_index (int, optional): The starting index for the new node IDs (default is 1).

    Returns:
        str: The modified content with renumbered node IDs.
    """

    try:
        # Pattern to match node IDs (allows for letters, underscores, and digits)
        pattern = re.compile(rf"\b[a-zA-Z_]+\d+\b")

        unique_ids = {}
        counter = start_index

        def replace_id(match):
            nonlocal counter
            node_id = match.group()
            if node_id not in unique_ids:
                unique_ids[node_id] = f"{node_prefix}{counter}"
                counter += 1
            return unique_ids[node_id]

        new_content = pattern.sub(replace_id, content)
        return new_content

    except Exception as e:  # Catch any unexpected errors
        print(f"Error renumbering nodes: {e}")
        return content  # Return the original content if there's an error


def process_dot_files_in_directory(input_directory, output_directory):
    """Renumbers node IDs and saves modified .dot files in an output directory."""

    os.makedirs(output_directory, exist_ok=True)  # Create output directory if it doesn't exist

    for filename in os.listdir(input_directory):
        if filename.endswith(".dot"):
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join(output_directory, filename)  # Output in separate folder

            with open(input_filepath, "r") as file:
                content = file.read()

            renumbered_content = renumber_dot_file(content)

            with open(output_filepath, "w") as output_file:
                output_file.write(renumbered_content)

def clean_dot_files(input_dir, output_dir):
    """
    Cleans .dot files by renumbering node IDs.

    Args:
        input_dir (str): Path to the directory containing .dot files to clean.
        output_dir (str): Path to the directory where cleaned files will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    process_dot_files_in_directory(input_dir, output_dir)
# If run as a script
if __name__ == "__main__":
    clean_dot_files()  # Use default directories or modify the arguments
