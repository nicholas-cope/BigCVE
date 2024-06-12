print("Not working")

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