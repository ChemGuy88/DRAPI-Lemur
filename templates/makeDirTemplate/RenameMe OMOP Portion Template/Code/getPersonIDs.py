"""
Get "Person ID" from "Patient Key"
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path

# Arguments
PATIENT_KEYS_CSV_FILE_PATH = Path("data/input/cohort.csv")
PATIENT_KEYS_CSV_FILE_HEADER = None
LOG_LEVEL = "DEBUG"

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
    intermediateDataDir = dataDir.joinpath("intermediate")
    outputDataDir = dataDir.joinpath("output")
    if intermediateDataDir:
        runIntermediateDataDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

# Variables: Path construction: Project-specific
pass

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Variables: Other
personID_SQLQueryFilePath = sqlDir.joinpath("grabPersonIDs.SQL")

# Directory creation: General
make_dir_path(runIntermediateDataDir)
make_dir_path(runOutputDir)
make_dir_path(runLogsDir)

# Directory creation: Project-specific
pass


if __name__ == "__main__":
    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(LOG_LEVEL)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)

    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler, streamHandler],
                        level=LOG_LEVEL)

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `projectDir`: "{projectDir}".""")

    # Script
    # Get patient keys
    patientKeysInput = pd.read_csv(PATIENT_KEYS_CSV_FILE_PATH).drop_duplicates()
    listAsString = ",".join([str(x) for x in patientKeysInput.values.flatten()])

    # Get input file header
    assert patientKeysInput.shape[1] == 1, "Expected file input should be just one column containing patient keys."
    if PATIENT_KEYS_CSV_FILE_HEADER:
        inputFileHeader = PATIENT_KEYS_CSV_FILE_HEADER
    else:
        inputFileHeader = patientKeysInput.columns[0]

    # Query person IDs
    logging.info("""Querying database for person IDs.""")
    with open(personID_SQLQueryFilePath, "r") as file:
        text = file.read()
    query = text.replace("XXXXX", listAsString)
    queryResults = pd.read_sql(query, con=conStr)
    logging.info("""Finished query.""")

    # Compare number of Person IDs returned with Patient Keys queried
    li = []
    for value in patientKeysInput.values:
        if value in queryResults.iloc[:, 1].values:
            li.append(True)
        else:
            li.append(False)
    patientKeysInput["Found"] = li
    patientKeysInput = patientKeysInput.rename(columns={inputFileHeader: "patient_key"})
    personIDsFound = patientKeysInput.set_index("patient_key").join(queryResults.set_index("patient_key"), "patient_key", "left")
    personIDsFound = personIDsFound.sort_values("person_id")

    # Summary statistics
    numFound = personIDsFound["Found"].sum()
    numPatientKeys = len(patientKeysInput)
    logging.info(f"""A total of {numFound} patient keys of {numPatientKeys} were mapped to OMOP person IDs.""")

    # If any column contains NaNs, convert the column to the "Object" data type, to preserve data quality
    personIDsFound2 = personIDsFound.copy()
    for column in personIDsFound.columns:
        if personIDsFound[column].isna().sum() > 0:
            li = []
            for value in personIDsFound[column].values:
                if pd.isna(value):
                    li.append("")
                else:
                    li.append(str(int(value)))
            personIDsFound2[column] = li

    # Save results: Person IDs found
    personIDsFoundExportPath = runOutputDir.joinpath("personIDsFound.csv")
    personIDsFound2.to_csv(personIDsFoundExportPath)
    logging.info(f"""The map of patient keys to person IDs, and those missing or found, was saved to "{personIDsFoundExportPath}".""")

    # Save results: person IDs
    personIDs = personIDsFound["person_id"].drop_duplicates().dropna().sort_values().astype(int)
    personIDsExportPath = runOutputDir.joinpath("personIDs.csv")
    personIDs.to_csv(personIDsExportPath, index=False)
    logging.info(f"""Person IDs were saved to "{personIDsExportPath.relative_to(projectDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
