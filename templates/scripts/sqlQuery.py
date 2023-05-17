"""

A template for pulling SQL queries in Python

Outline:

  - Load arguments
  - Load query
  - Insert arguments into query
  - Run query
  - Post-processing
"""

import os
import pandas as pd
import sqlalchemy as sa
from drapi.drapi import getTimestamp, isValidPatientID, replace_sql_query
from pathlib import Path

# Arguments
pass

# Variables
this_file_path = Path(__file__)
project_dir = this_file_path.absolute().parent.parent
irb_dir = project_dir.parent
irbNumber = None  # TODO
input_dir = os.path.join(project_dir, "data",
                                      "input")
output_dir = os.path.join(project_dir, "data",
                                       "output")
sql_dir = os.path.join(project_dir, "sql")
run_timestamp = getTimestamp()

# SQL Server settings
SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = fr"{USERDOMAIN}\{USERNAME}"
PWD = os.environ["HFA_UFADPWD"]

# SQLAlchemy connection
connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"  # Create connection string
engine = sa.create_engine(connstr)  # Make connection/engine

# Test connections
if True:
    # SQL
    print(f"""[{getTimestamp()}] Testing SQL connection.""")
    query_test = """SELECT 1"""
    test = pd.read_sql(query_test, con=engine).values[0][0]
    if test:
        print(f"""[{getTimestamp()}] SQL connection successful: "{test}".""")
