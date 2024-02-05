"""
Converts OneFlorida patient ID to UF medical record number (MRN).
"""

import os
from pathlib import Path
from typing_extensions import Literal
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import replace_sql_query, successiveParents


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


def mapOneFloridaIDs(IDTypeValues: pd.Series, IDType: Literal["PATID", "Patient Key", "MRN (UF)", "MRN (Jax)", "MRN (Pathology)"]) -> pd.Series:
    """
    Queries the ID map containing all of the following variables, any of which can be used as a query filter using the `IDType` parameter. The values to query by are used in the `IDTypeValues` parameter.
        | Variable Definition           | Standard or Common Column Name    |
        |-------------------------------|-----------------------------------|
        | OneFlorida patient ID         | OneFlorida Patient ID             |
        | IDR patient key               | Patient Key                       |
        | UF Health Gainesvile MRN      | MRN (UF)                          |
        | UF Health Jacksonville MRN    | MRN (Jax)                         |
        | UF Health Pathology MRN       | MRN (Pathology)                   |
    """

    listAsString = ",".join([f"'{el}'" for el in IDTypeValues.iloc[:].sort_values()])

    with open(sqlFilePath2, "r") as file:
        query0 = file.read()

    query = replace_sql_query(query=query0,
                              old="{PYTHON_VARIABLE: IDTypeValues}",
                              new=listAsString)
    IDTypeInput = IDType.lower()
    IDTypeDict = {"oneflorida patient id": "a.PATID",
                  "patient key": "a.PATNT_KEY",
                  "mrn (uf)": "b.IDENT_ID",
                  "mrn (jax)": "c.IDENT_ID",
                  "mrn (pathology)": "d.IDENT_ID"}
    IDTypeSQL = IDTypeDict[IDTypeInput]
    query = replace_sql_query(query=query,
                              old="{PYTHON_VARIABLE: IDTypeSQL}",
                              new=IDTypeSQL)

    MRNseries = pd.read_sql(query, con=conStr)

    return MRNseries
