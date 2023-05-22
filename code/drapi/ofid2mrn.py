"""
Converts OneFlorida patient ID to UF medical record number (MRN).
"""

import os
from pathlib import Path
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
sqlFilePath = sqlDir.joinpath("ConvertBetweenMrnAndOneFloridaPatID.SQL")

# Variables: SQL connection settings
uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"


def convertOFID2MRN(OFIDseries: pd.Series) -> pd.DataFrame:
    """

    """
    listAsString = ",".join([str(el) for el in OFIDseries.values])

    with open(sqlFilePath, "r") as file:
        query0 = file.read()

    query = replace_sql_query(query=query0,
                              old="{PYTHON_VARIABLE: ONE_FLORIDA_PATIENT_IDS}",
                              new=listAsString)

    MRNseries = pd.read_sql(query, con=conStr)

    return MRNseries
