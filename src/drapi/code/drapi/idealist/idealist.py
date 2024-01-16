"""
Herman's utility functions commonly used in his IDEALIST projects
"""

__all__ = ["idealistMap2dict",
           "patientKey2MRNs"]

from pathlib import Path
from drapi.drapi import replace_sql_query
import os
import pandas as pd
import sqlalchemy as sa

# Variables
this_file_path = Path(__file__)
this_file_stem = this_file_path.stem
project_dir = this_file_path.absolute().parent.parent.parent.parent
input_dir = project_dir.joinpath("data", "input")
output_dir = project_dir.joinpath("data", "output")
sql_dir = project_dir.joinpath("sql")


# SQL Server settings
SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = fr"{USERDOMAIN}\{USERNAME}"
PWD = os.environ["HFA_UFADPWD"]

# SQLAlchemy connections
connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"  # Create connection string
engine = sa.create_engine(connstr)  # Make connection/engine


def idealistMap2dict(idealistMap, fromID, toID):
    """
    """
    idealistMap.index = idealistMap[fromID]
    mapDi = idealistMap[toID].to_dict()
    return mapDi


def patientKey2MRNs(patientKeys: list):
    """
    """
    assert isinstance(patientKeys, list), "This function expects an object of type list."
    queryPath = sql_dir.joinpath("MRNfromPatientKey.sql")
    with open(queryPath, "r") as file:
        query0 = file.read()
    old = "0123456789, 1234567890"
    new = ",".join(str(id) for id in patientKeys)
    query = replace_sql_query(query0, old, new)
    results = pd.read_sql(query, engine)
    return results
