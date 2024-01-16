"""
Consent-to-Share helper functions. Consent-to-Share is also known as "C2S".
"""

import logging
import os
from pathlib import Path
from typing import List
from typing_extensions import Literal
# Third-party libraries
import pandas as pd
# Local libraries
from drapi.drapi import replace_sql_query
from drapi.drapi import successiveParents

# Arguments
MODULE_ROOT_DIRECTORY_PATH = successiveParents(Path(__file__), 4)

# Arguments: SQL connection settings
SERVER = "EDW.shands.ufl.edu"
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


def doCheck(result, statusType):
    """
    Analyzes table values to deduce if the entire table passes the check. Any patients that fail the check are returned in a table.
    """
    result = pd.DataFrame(result)
    if statusType == "C2S":
        s1 = pd.Series(result["CONSENT_SHARE_IND"])
        r1 = (s1 == "Y")
        r1sum = r1.sum()
        s2 = pd.Series(result["CONSENT_SHARE_DATE"])
        r2 = s2.notna()
        r2sum = r2.sum()
        length = len(result)
        if (r1sum == length) and (r2sum == length):
            checkResultPass = True
            failedRows = None
        else:
            checkResultPass = False
            # Print failed rows
            mask = ~r1 | ~r2
            failedRows = result[mask]

    elif statusType == "death":
        s1 = pd.Series(result["PATNT_SSN_DTH_IND"])
        r1 = (s1 == "N")
        r1sum = r1.sum()
        s2 = pd.Series(result["PATNT_SSN_DTH_DATE"])
        r2 = s2.isna()
        r2sum = r2.sum()
        s3 = pd.Series(result["PATNT_DTH_IND"])
        r3 = (s3 == "N")
        r3sum = r3.sum()
        s4 = pd.Series(result["PATNT_DTH_DATE"])
        r4 = s4.isna()
        r4sum = r4.sum()
        length = len(result)
        if (r1sum == length) and (r2sum == length) and (r3sum == length) and (r4sum == length):
            checkResultPass = True
            failedRows = None
        else:
            checkResultPass = False
            # Print failed rows
            mask = ~r1 | ~r2 | ~r3 | ~r4
            failedRows = result[mask]

    return checkResultPass, failedRows
