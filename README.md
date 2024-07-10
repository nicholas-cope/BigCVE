# BigCVE

## :round_pushpin: About
BigCVE is a data pipeline created by Yuri Batan (OSU :chestnut: ) and Nicholas Cope (UNC :ram: ) in the University of Missouri's Consumer Networking REU Program. BigCVE extracts vulnerable code snippets and their corresponding fixes from the BigVul and CVEFixes dataset. 

BigCVE takes these functions and converts them into Code Property Graphs and creates a temporal representation of the fixes introduced to fix the vulnerability by utilizing one of the many graph matching approaches in :file_folder: Matching. 

Finally, these graphs are tokenized with the StarCoder model and transforms the CPG's into a format suitable for machine learning models, especially Graph Neural Networks.
## Data Preperation Steps
### For BigVul
1. Run the CSV Cleaner on BigVul dataset to isolate changing functions. This script is present in Data_Prep/csv_cleaner.py
2. Convert all of the functions into .cpp format by running Data_Prep/bigvul_parser.py
3. Convert all of the functions into a Code Property Graph(CPG) using generate_cpgs.py
4. Create a concatenated version of each function's CPG using combine_dots.py
5. Run your desired graph matching algorithm and its inverse counterpart by using one of the graph_match scripts in Data_Prep
6. Assign each edge/node in the matched .dot file a unique integer ID by running Data_Prep/dot_cleaner.py
7. Convert into a PKL file using cpg_to_pickle in Data_Prep.
8. Send into VulGNN
### For CVEFixes

1. 

