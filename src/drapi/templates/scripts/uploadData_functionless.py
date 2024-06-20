"""
Template script for uploading pandas-compatible files to a SQL server - functionless implementation.
"""

import os
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

from drapi.code.drapi.drapi import (getTimestamp,
                                    readDataFile)

DIRECTORY_OR_LIST_OF_PATHS = "../../Data Request 03 - 2024-04-15/Intermediate Results/Clinical Text Portion/data/output/freeText/2024-06-04 17-14-41/free_text/Sepsis_order_impression"
TABLE_NAME = f"DR IRB202202722 Text - OI {getTimestamp()}"
SCHEMA_NAME = "dbo"
CONNECTION_STRING = f"""mssql+pymssql://UFAD\herman:{os.environ["HFA_UFADPWD"]}@DWSRSRCH01.shands.ufl.edu/DWS_OMOP"""

if Path(DIRECTORY_OR_LIST_OF_PATHS).is_dir():
    list_of_paths = sorted(list(Path(DIRECTORY_OR_LIST_OF_PATHS).iterdir()))
elif isinstance(DIRECTORY_OR_LIST_OF_PATHS, list):
    list_of_paths = sorted([Path(el) for el in DIRECTORY_OR_LIST_OF_PATHS])
else:
    raise Exception(f"""`DIRECTORY_OR_LIST_OF_PATHS` should be a directory or a list of file paths.""")

print("Dropping table if it exists.")
query_prep_table = f"""\
DROP TABLE IF EXISTS [{SCHEMA_NAME}].[{TABLE_NAME}]
\
"""
with sa.engine.create_engine(url=CONNECTION_STRING).connect() as connection:
    with connection.begin():
        _ = connection.execute(sa.text(query_prep_table))
print("Dropping table if it exists - done.")

num_files = len(list_of_paths)
for it, fpath in enumerate(list_of_paths, start=1):
    print(f"""  Working on file {it:,} of {num_files:,}.""")
    df = readDataFile(fname=fpath,
                      engine="pyarrow")
    df = pd.DataFrame(df)  # For type hinting
    df.to_sql(name=TABLE_NAME,
              con=CONNECTION_STRING,
              schema=SCHEMA_NAME,
              if_exists="append",
              index=False)
    print(f"""  Working on file {it:,} of {num_files:,} - done.""")
