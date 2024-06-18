import sqlite3

import pandas as pd
import sqlite3 as lite
from sqlite3 import Error
from pathlib import Path
import shutil
import subprocess

def create_connection(db_file):
    conn = None
    try:
        conn = lite.connect(db_file, timeout=10)  # Connection via sqlite3
    except Error as e:
        print(e)
    return conn

# Create connection to sqlite3 database
conn = create_connection(Path.cwd() / "CVEfixes_v1.0.7" / "Data" / "CVEfixes - Copy.db")
# cursor = conn.cursor()
# cursor.execute("DELETE FROM cve WHERE (file_change.programming_language!='C' OR file_change.programming_language!='C++')")
# conn.commit()
# conn.close()
# shutil.copyfile(Path.cwd() / "CVEfixes_v1.0.7" / "Data" / "CVEfixes - Copy.db", 'backup.db')
#Query database for vulnerable methods
# vul_methods = pd.read_sql_query("SELECT m.signature, m.code, m.method_change_id \
# FROM method_change m, file_change f \
# WHERE f.file_change_id=m.file_change_id AND m.before_change='True' AND (f.programming_language='C' OR f.programming_language='C++')", conn)

new_db = pd.read_sql("SELECT c.cve_id, m.signature, m.code, m.before_change \
FROM cve c, method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND (f.programming_language='C' OR f.programming_language='C++')", conn)
conn2 = sqlite3.connect('test.db')
new_db.to_sql('vulfix', conn2, if_exists='replace', index=False)


# Query database for vulnerable methods
# Query database for vulnerable methods
vul_methods = pd.read_sql_query("SELECT c.cve_id, m.signature, m.code \
FROM cve c, method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND m.before_change='True' AND (f.programming_language='C' OR f.programming_language='C++')", conn)
print("Vulnerable query finished.")

# Query database for fixed methods
fixed_methods = pd.read_sql_query("SELECT c.cve_id, m.signature,  m.code \
FROM cve c, method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND m.before_change='False' AND (f.programming_language='C' OR f.programming_language='C++')", conn)
print("Fixed query finished.")

print(vul_methods)

conn2.close()
conn.close()



# fixed_methods = pd.read_sql_query("SELECT f.code_after \
# FROM method_change m, file_change f \
# WHERE m.method_change_id='38197852149195' AND m.before_change='False' AND (f.programming_language='C' OR f.programming_language='C++')", conn)

#Merge queries based on function signature
# merged_methods = vul_methods.merge(fixed_methods, on='signature', how='inner')

# fixed_code = merged_methods.iloc[1]  # Access code_x column for vulnerable function
# print(fixed_methods.iloc[0]['code_after'])


# Write first 10 vulnerable functions as C++ files (code_x)
# for i in range(10):
#   vulnerable_code = merged_methods.iloc[i]['code_x']  # Access code_x column for vulnerable function
#   with open(f"Functions/vulnerability{i+1}.cpp", 'w') as f:
#     f.write(vulnerable_code)
#
# # Write first 10 fixed functions as C++ files (code_y)
# for i in range(10):
#   fixed_code = merged_methods.iloc[i]['code_y']  # Access code_y column for fixed function
#   with open(f"Functions/fixed{i+1}.cpp", 'w') as f:
#     f.write(fixed_code)

