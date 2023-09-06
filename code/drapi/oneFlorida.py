"""
Converts OneFlorida patient ID to UF medical record number (MRN).
"""

import os
from pathlib import Path
from typing_extensions import Literal
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import replace_sql_query, successiveParents


# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
thisFilePath = Path(__file__)
drapiRootDir, _ = successiveParents(thisFilePath, 3)
sqlDir = drapiRootDir.joinpath("sql")

# Variables: More
sqlFilePath1 = sqlDir.joinpath("ConvertBetweenMrnAndOneFloridaPatID.SQL")
sqlFilePath2 = sqlDir.joinpath("MapOneFloridaIDs.SQL")

# Variables: SQL connection settings
uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"


def OFID2MRN(OFIDseries: pd.Series) -> pd.DataFrame:
    """

    """
    listAsString = ",".join([str(el) for el in OFIDseries.values])

    with open(sqlFilePath1, "r") as file:
        query0 = file.read()

    query = replace_sql_query(query=query0,
                              old="{PYTHON_VARIABLE: ONE_FLORIDA_PATIENT_IDS}",
                              new=listAsString)

    MRNseries = pd.read_sql(query, con=conStr)

    return MRNseries


def mapOneFloridaIDs(mrnSeries: pd.Series, IDType: Literal["OF", "Patient Key", "UF", "JAX", "path"]) -> pd.Series:
    """
    """

    listAsString = ",".join([f"'{el}'" for el in sorted(mrnSeries.values)])

    with open(sqlFilePath2, "r") as file:
        query0 = file.read()

    query = replace_sql_query(query=query0,
                              old="{PYTHON_VARIABLE: ONE_FLORIDA_PATIENT_IDS}",
                              new=listAsString)
    IDTypeInput = IDType.lower()
    IDTypeDict = {"of": "a.PATID",
                  "patient key": "a.PATNT_KEY",
                  "uf": "b.IDENT_ID",
                  "jax": "c.IDENT_ID",
                  "path": "d.IDENT_ID"}
    IDTypeValue = IDTypeDict[IDTypeInput]
    query = replace_sql_query(query=query,
                              old="{PYTHON_VARIABLE: ID_TYPE}",
                              new=IDTypeValue)

    MRNseries = pd.read_sql(query, con=conStr)

    return MRNseries
