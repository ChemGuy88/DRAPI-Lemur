"""
Test lazy hack 1

Originally from "SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Xu/IRB202202722/Data Request 03 - 2024-04-15/Concatenated Results - v03"
"""

from pathlib import Path

import pandas as pd

from drapi.code.drapi.drapi import readDataFile
from drapi.code.drapi.uploadData import lazy_hack_1_function

FILE_PATH = "../../Data Request 03 - 2024-04-15/Intermediate Results/Clinical Text Portion/data/output/freeText/2024-06-04 17-14-41/free_text/Sepsis_note/note_1.tsv"
lazy_hack_1 = True

df = readDataFile(fname=Path(FILE_PATH),
                  engine="pyarrow")
df = pd.DataFrame(df)  # For type hinting
if lazy_hack_1:
    column_name = "note_text"
    series = df[column_name]
    df[column_name] = series.apply(lazy_hack_1_function)
    print(df)
