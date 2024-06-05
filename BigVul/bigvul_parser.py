import csv

import pandas as pd

file = "Dataset/MSR_data_cleaned.csv"

df = pd.read_csv(file, nrows = 1)
print(df.to_string())