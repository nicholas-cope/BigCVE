import pandas as pd
import sqlite3 as lite
from sqlite3 import Error
from pathlib import Path
import subprocess

def create_connection(db_file):
    conn = None
    try:
        conn = lite.connect(db_file, timeout=10)  # Connection via sqlite3
    except Error as e:
        print(e)
    return conn

# Create connection to sqlite3 database
conn = create_connection(Path.cwd() / "CVEfixes_v1.0.7" / "Data" / "CVEfixes.db")

# # Query database for vulnerable methods
# vul_methods = pd.read_sql_query("SELECT m.signature, m.code \
# FROM method_change m, file_change f \
# WHERE f.file_change_id=m.file_change_id AND m.before_change='True' AND (f.programming_language='C' OR f.programming_language='C++')", conn)
#
# # Query database for fixed methods
# fixed_methods = pd.read_sql_query("SELECT m.signature,  m.code \
# FROM method_change m, file_change f \
# WHERE f.file_change_id=m.file_change_id AND m.before_change='False' AND (f.programming_language='C' OR f.programming_language='C++')", conn)
#
# # Merge queries based on function signature
# merged_methods = vul_methods.merge(fixed_methods, on='signature', how='inner')
#
#
# # Write first 5 vulnerable functions as C++ files (code_x)
# for i in range(5):
#   vulnerable_code = merged_methods.iloc[i]['code_x']  # Access code_x column for vulnerable function
#   with open(f"Functions/vulnerability{i+1}.cpp", 'w') as f:
#     f.write(vulnerable_code)
#
# # Write first 5 fixed functions as C++ files (code_y)
# for i in range(5):
#   fixed_code = merged_methods.iloc[i]['code_y']  # Access code_y column for fixed function
#   with open(f"Functions/fixed{i+1}.cpp", 'w') as f:
#     f.write(fixed_code)

subprocess.run(["/usr/bin/python3", "generate_cpgs_cve.py"])

