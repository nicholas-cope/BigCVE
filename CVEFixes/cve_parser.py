import pandas as pd
# import matplotlib.pyplot as plt
import sqlite3 as lite
from sqlite3 import Error
from pathlib import Path
# from datetime import date
# import numpy as np
# import seaborn as sns
# import matplotlib.ticker as tick
# import requests
# import difflib as diff
# import re
# import csv
# import ast

def create_connection(db_file):
    """
    create a connection to sqlite3 database
    """
    conn = None
    try:
        conn = lite.connect(db_file, timeout=10)  # connection via sqlite3
        # engine = sa.create_engine('sqlite:///' + db_file)  # connection via sqlalchemy
        # conn = engine.connect()
    except Error as e:
        print(e)
    return conn

#
# DATA_PATH = Path.cwd() / 'Data'
#
#
# Path(DATA_PATH).mkdir(parents=True, exist_ok=True)


# conn = create_connection(DATA_PATH / "CVEfixes.db")

conn = create_connection(Path.cwd() / "CVEfixes_v1.0.7" / "Data" / "CVEfixes.db")

# df_c_methods = pd.read_sql_query("SELECT m.name, m.signature, m.nloc, \
# m.parameters, m.token_count, m.code, m.before_change, f.programming_language FROM method_change m, file_change f \
# WHERE f.file_change_id=m.file_change_id AND f.programming_language='C'", conn)

all_methods = pd.read_sql_query("SELECT m.code, m.before_change, f.programming_language \
FROM method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND (f.programming_language='C' OR f.programming_language='C++')", conn)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# pd.set_option('display.max_colwidth', None)

vul_methods = pd.read_sql_query("SELECT m.code \
FROM method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND m.before_change='True' AND (f.programming_language='C' OR f.programming_language='C++')", conn)

fixed_methods = pd.read_sql_query("SELECT m.code \
FROM method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND m.before_change='False' AND (f.programming_language='C' OR f.programming_language='C++')", conn)


print(vul_methods)
print(fixed_methods)
