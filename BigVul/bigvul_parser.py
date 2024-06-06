import csv

import pandas as pd

#Path to BigVul Dataset
file_path = "Dataset/MSR_data_cleaned.csv"
#How many rows we are going to read at a time
#Optimizing performance
chunks = 25000

#Columns we want to read
vulnerableFunction = "func_before"
fixedFunction = "func_after"

#Reading the file in chunks
#While BigVul is in utf8, just checking for safety
with open(file_path, "r", encoding="utf8", errors="ignore") as file:
    #The reader for the specified number of chunks
    reader = csv.reader(file)
    #Printing the rows we want
    #O(n^2) - Oh no
    row_number = 1

    for chunk in reader:
        for row in chunk:
            print("Row number: "+ str(row_number))
            print("Function Before:")
            print(row.get(vulnerableFunction, "Not Found"))
            print("Function After:")
            print(row.get(fixedFunction, "Not Found"))
            row_number += 1




