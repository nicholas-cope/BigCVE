import csv

import pandas as pd


file = "Dataset/MSR_data_cleaned.csv"

df = pd.read_csv(file, nrows=10000)

if 'func_before' in df.columns and 'func_after' in df.columns:
    if 'func_before' in df.columns and 'func_after' in df.columns:
        for index, row in df.iterrows():
            print(f"\n--- Row {index + 1} ---")
            print(f"func_before: {row['func_before']}")
            print(f"func_after: {row['func_after']}")
    else:
        print("Error: One or both columns 'func_before' and 'func_after' were not found in the CSV file.")