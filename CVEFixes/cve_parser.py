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


DATA_PATH = Path.cwd().parents[0] / 'Data'


Path(DATA_PATH).mkdir(parents=True, exist_ok=True)


conn = create_connection(DATA_PATH / "CVEfixes.db")

df_c_methods = pd.read_sql_query("SELECT m.name, m.signature, m.nloc, \
m.parameters, m.token_count, m.code, m.before_change, f.programming_language FROM method_change m, file_change f \
WHERE f.file_change_id=m.file_change_id AND f.programming_language='C'", conn)
df_c_methods.head(5)