"""
SQL helper functions
"""

import logging
import os
from pathlib import Path
from typing import List
from typing_extensions import Literal
# Third-party libraries
import pandas as pd
# Local libraries
from hermanCode.hermanCode import replace_sql_query

# Arguments
MODULE_ROOT_DIRECTORY_PATH = Path(__file__).absolute().parent.parent.parent

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"


def labelMRNColumns(query):
    """
    NOTE Not implemented

    Replace text in a query for each of the MRN columsn thusly:

    `Table__1308.IDENT_ID_INT` --> `Table__1308.IDENT_ID_INT as MRN_UF`
    `Table__1311.IDENT_ID_int` --> `Table__1311.IDENT_ID_int as MRN_Vista`
    `Table__1312.IDENT_ID_int` --> `Table__1312.IDENT_ID_int as MRN_Rehab`
    `Table__1117.IDENT_ID_INT` --> `Table__1117.IDENT_ID_INT as MRN_Jax`
    `Table__2699.IDENT_ID_INT` --> `Table__2699.IDENT_ID_INT as MRN_CFH_Lessburg`
    `Table__2700.IDENT_ID_INT` --> `Table__2700.IDENT_ID_INT AS MRN_CFH_Villages`

    Outline

    for each instance of the above strings, if it's not behind a comment marker (e.g., `--`), replace it with its corresponding string pair. If it's the last column make sure to no add a comma
    """
    # TODO
    return


def checkStatus(statusType=Literal["C2S", "death"],
                location=Literal["gnv", "jax"],
                listOfMRNs=List[str]) -> pd.DataFrame:
    """
    This functions performs the Consent-to-Share ("C2S") check before release, to ensure deceased or opted-out patients aren't contacted.
    """

    # Determine query type
    if statusType == "C2S":
        queryFilePath = MODULE_ROOT_DIRECTORY_PATH.joinpath("sql/Consent2Share.sql")
    elif statusType == "death":
        queryFilePath = MODULE_ROOT_DIRECTORY_PATH.joinpath("sql/LADMF.sql")

    # Define values for query: LOCATION_NAME, LOCATION_TYPE
    location_lower_case = location.lower()
    if location_lower_case == "gnv":
        locationNameForQuery = "UF"
        locationValueForQuery = "101"
    elif location_lower_case == "jax":
        locationNameForQuery = "Jax"
        locationValueForQuery = "110"

    # Define value for query: LIST_OF_MRNS
    MRNValuesForQuery = ",".join(f"'{MRNNumber}'" for MRNNumber in listOfMRNs)

    # Load query template
    with open(queryFilePath, "r") as file:
        query0 = file.read()

    # Prepare query
    query = replace_sql_query(query=query0, old="{<PYTHON_PLACEHOLDER : LOCATION_NAME>}", new=locationNameForQuery)
    query = replace_sql_query(query=query, old="{<PYTHON_PLACEHOLDER : LOCATION_TYPE>}", new=locationValueForQuery)
    query = replace_sql_query(query=query, old="{<PYTHON_PLACEHOLDER : LIST_OF_MRNS>}", new=MRNValuesForQuery)

    # Run query
    logging.debug(query)
    queryResult = pd.read_sql(sql=query, con=conStr)

    return queryResult
