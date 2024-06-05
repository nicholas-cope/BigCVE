import csv

import pandas as pd


file = "Dataset/MSR_data_cleaned.csv"

df = pd.read_csv(file, nrows = 1)

if 'func_before' in df.columns and 'func_after' in df.columns:
    selected_columns = df[['func_before', 'func_after']]
    first_row = selected_columns.iloc[0]

    print(f"func_before: {first_row['func_before']}")
    print(f"func_after: {first_row['func_after']}")