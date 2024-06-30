import csv
import os
import time
import subprocess

start_time = time.time()

# Path to BigVul Dataset
file_path = "../Dataset/vulnerable_functions.csv"
# How many rows we are going to read at a time
# Optimizing performance
chunks = 25000

# Columns we want to read
vulnerableFunction = "func_before"
fixedFunction = "func_after"

# Increasing CSV field limit
csv.field_size_limit(100000000)
# Reading the file in chunks
# While BigVul is in utf8, just checking for safety
with open(file_path, "r", encoding="utf8", errors="ignore") as file:
    # The reader for the specified number of chunks
    # Reading as a dictionary in order to use direct access
    reader = csv.DictReader(file)
    # Printing the rows we want
    row_number = 1
    # Max Numbers of Rows Read
    max_rows = 1

    for row in reader:
        #Ensuring that rows does not over max rows
        if row_number > max_rows:
            break
        vulnerable_file_name = os.path.join("../Functions", f"vulnerability{row_number}.cpp")
        fixed_file_name = os.path.join("../Functions", f"fixed{row_number}.cpp")

        # Automatically closes files so don't have to worry
        # Vulnerable File
        with open(vulnerable_file_name, "w", encoding="utf8", errors="ignore") as vulnerable_file:
            vulnerable_file.write(row.get(vulnerableFunction, "Not Found"))

        # Fixed File
        with open(fixed_file_name, "w", encoding="utf8", errors="ignore") as fixed_file:
            fixed_file.write(row.get(fixedFunction, "Not Found"))

        row_number += 1

#Executing Generation
subprocess.run(["python", "generate_cpgs.py"])
#End Time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")




