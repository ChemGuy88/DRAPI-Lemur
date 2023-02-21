"""
Outline

    - Initilalize an empty pandas dataframe as the master de-identification map.
    - Iterate over the encounter SQLite database files.
    - For each file, append the encounter de-identification maps to the master map.
"""

# Private variables ("dunders")
__all__ = ["encounterMapDf"]

# Imports
from pathlib import Path
import os
import re
import sys
# Third-party packages
import numpy as np
import pandas as pd
import sqlite3
# Local imports
from hermanCode.hermanCode import sqlite2df, getTimestamp, replace_sql_query, makeChunks

# Arguments
QUERY_PATH = Path("sql/encounterNumber2patientKey.SQL")
DATABSE_DIR_WINDOWS = os.path.join("X:\\",
                                   "FTP",
                                   "IDR",
                                   "ANES",
                                   "IRB201600223 - aka R01",
                                   "Deiden_db")
DATABSE_DIR_MAC = os.path.join("/",
                               "Volumes",
                               "FILES",
                               "FTP",
                               "IDR",
                               "ANES",
                               "IRB201600223 - aka R01",
                               "Deiden_db")
CHUNK_SIZE = "100,000"

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.absolute().parent.parent
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    outputDataDir = dataDir.joinpath("output")
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Variables: more
chunkSize = int(CHUNK_SIZE.replace(",", ""))

# Connect to SQLite database
if True:
    # If you have connection to the below directory, use the below line.
    operatingSystem = sys.platform
    if operatingSystem == "win32":
        database_dir = Path(DATABSE_DIR_WINDOWS)
    elif operatingSystem == "darwin":
        database_dir = Path(DATABSE_DIR_MAC)
    else:
        raise Exception("Unsupported operating system")
elif True:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    database_dir = None


def getDeidenDBSeriesNumber(string):
    """
    Regular expression to get the series number from the IDEALIST encounter de-identification database file.

    Expects files to be of the format "deiden_YYYY-MM-DD_XX.db", where YYYY is the year four-digit year, MM is the two-digit month, DD is the two-digit day, and XX is the series number (with no zero padding).
    """
    seriesNumber = re.search(r"_(\d+).db$", string).groups(0)[0]
    return seriesNumber


if __name__ == "__main__":
    print(f"""[{getTimestamp()}] Begin running "{thisFilePath}".""")
    print(f"""[{getTimestamp()}] All other paths will be reported in debugging relative to `projectDir`: "{projectDir}".""")

    # SQLite connection
    databaseFiles = sorted([fPath for fPath in database_dir.iterdir() if "deiden_2021-05-01_" in fPath.name], key=lambda fPath: int(getDeidenDBSeriesNumber(str(fPath))))
    encounterMapDf = pd.DataFrame()
    for it, file in enumerate(databaseFiles, start=1):
        database_path = file
        print(f"""[{getTimestamp()}]   Loading file {it} of {len(databaseFiles)}.""")
        print(f"""[{getTimestamp()}]     Loading sqlite database from "{database_path}".""")
        sqliteConnection = sqlite3.connect(database_path)
        cursor = sqliteConnection.cursor()

        if it == 1:
            # Test SQLite connection
            print(f"""[{getTimestamp()}]   ..  Testing SQLite connection.""")
            query = """SELECT 1"""
            cursor.execute(query)
            test1 = cursor.fetchall()[0][0]
            if test1:
                print(f"""[{getTimestamp()}]   ..    SQLite connection successful: "{test1}".""")

        # Query encounter de-identification map
        print(f"""[{getTimestamp()}]     Running SQLite query for encounter map.""")
        query = """SELECT *
    FROM EncounterDeidenMap"""
        cursor.execute(query)
        resultsList = cursor.fetchall()
        print(f"""[{getTimestamp()}]     SQLite query completed.""")
        results = sqlite2df(resultsList, "EncounterDeidenMap", cursor)
        encounterMapDf = pd.concat([encounterMapDf, results])

    # Post-processing
    print(f"""[{getTimestamp()}] Ordering encounter de-identification map dataframe by values.""")
    encounterMapDf = encounterMapDf.sort_values(by="real_id")

    # Map encounter numbers to patient keys, in parallel / series
    print(f"""[{getTimestamp()}] Reading SQL file.""")
    with open(QUERY_PATH, "r") as file:
        query0 = file.read()

    indexChunks = makeChunks(array_range=range(len(encounterMapDf)), chunkSize=chunkSize)
    numChunks = int(np.ceil(len(encounterMapDf) / chunkSize))
    allResults = pd.DataFrame()
    for it, indices in enumerate(indexChunks, start=1):
        print(f"""[{getTimestamp()}]   Working on chunk {it} of {numChunks}.""")
        # Make chunk
        print(f"""[{getTimestamp()}]     Making chunk.""")
        indices = list(indices)
        dfChunk = encounterMapDf.iloc[indices, :]
        # Make query string from chunk
        print(f"""[{getTimestamp()}]     Making query string.""")
        series = dfChunk["real_id"]
        # li = sorted(series.to_list())
        li = series.to_list()
        encountersListAsString = ",".join([str(int(el)) for el in li])
        query = replace_sql_query(query0, "0123456789, 1234567890", encountersListAsString)
        # Query chunk
        print(f"""[{getTimestamp()}]     Querying database.""")
        results = pd.read_sql(query, con=conStr)
        # results.sort_values(by="ENCNTR_CSN_ID", key=int)
        allResults = pd.concat([allResults, results])

    # Create final de-identification map.
    if False:
        COLUMN_NAME = None
        encounterMapDf[COLUMN_NAME] = encounterMapDf["deiden_id"].apply(lambda integer: f"{integer}")

    # Script end
    print(f"""[{getTimestamp()}] Finished running "{thisFilePath}".""")
