"""
Get "Person ID" from "Patient Key" using `getData`.
"""

import logging
import os
import shutil
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.getData.getData import getData

# Arguments
PATIENT_KEYS_CSV_FILE_PATH = ""  # TODO
PATIENT_KEYS_CSV_FILE_HEADER = ""  # TODO

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "IRB_DIRECTORY"  # TODO One of the following:
                                                 # ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
                                                 #  "IRB_DIRECTORY",                 # noqa
                                                 #  "DATA_REQUEST_DIRECTORY",        # noqa
                                                 #  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_OMOP_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
IRBDir, _ = successiveParents(thisFilePath, IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
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

if ROOT_DIRECTORY == "PROJECT_OR_PORTION_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir
else:
    raise Exception("An unexpected error occurred.")

# Variables: Path construction: Project-specific
personID_SQLQueryFilePath = sqlDir.joinpath("grabPersonIDs.SQL")

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Variables: Other
pass

# Directory creation: General
makeDirPath(runIntermediateDataDir)
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Directory creation: Project-specific
pass

# Logging block
logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
logFormat = logging.Formatter("""[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s""")

logger = logging.getLogger(__name__)

fileHandler = logging.FileHandler(logpath)
fileHandler.setLevel(9)
fileHandler.setFormatter(logFormat)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(LOG_LEVEL)
streamHandler.setFormatter(logFormat)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

logger.setLevel(9)

if __name__ == "__main__":
    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:

    # Arguments
    `PATIENT_KEYS_CSV_FILE_PATH`: "{PATIENT_KEYS_CSV_FILE_PATH}"
    `PATIENT_KEYS_CSV_FILE_HEADER`: "{PATIENT_KEYS_CSV_FILE_HEADER}"

    # Arguments: Meta-arguments
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    # Script
    # Get patient keys
    data = pd.read_csv(PATIENT_KEYS_CSV_FILE_PATH)

    # Get input file header
    nColumns = data.shape[1]
    if PATIENT_KEYS_CSV_FILE_HEADER:
        inputFileHeader = PATIENT_KEYS_CSV_FILE_HEADER
    else:
        if nColumns == 1:
            inputFileHeader = data.columns[0]
        else:
            message = f"""The input data has more than one column and you did not specify the column to use. Please set a value for `PATIENT_KEYS_CSV_FILE_HEADER`."""
            logger.critical(message)
            raise Exception(message)

    patientKeysInput = data[inputFileHeader].astype(int).drop_duplicates().sort_values()

    # Query person IDs
    logger.info("""Querying database for person IDs.""")
    queryResultsDir = runIntermediateDataDir.joinpath("Query Results")
    queryResultsDir.mkdir()
    getData(sqlFilePath=personID_SQLQueryFilePath,
            connectionString=conStr,
            filterVariablePythonDataType="int",
            filterVariableSqlQueryTemplatePlaceholder="{PYTHON_VARIABLE: Patient Key}",
            logger=logger,
            outputFileName="Person ID",
            runOutputDir=queryResultsDir,
            filterVariableColumnName=PATIENT_KEYS_CSV_FILE_HEADER,
            filterVariableFilePath=PATIENT_KEYS_CSV_FILE_PATH)
    logger.info("""Querying database for person IDs - done.""")

    # Load query results
    queryResults = pd.DataFrame()
    resultsList = sorted(queryResultsDir.iterdir())
    it1Total = len(resultsList)
    for it1, fpath in enumerate(resultsList, start=1):
        logger.info(f"""  Loading query result {it1:,} of {it1Total:,}.""")
        df = pd.read_csv(fpath)
        queryResults = pd.concat([queryResults, df])

    # Compare number of Person IDs returned with Patient Keys queried
    patientKeysInput = pd.DataFrame(patientKeysInput)
    patientKeysInput = patientKeysInput.rename(columns={inputFileHeader: "Patient Key"})
    patientKeysInput["Patient Key"] = patientKeysInput["Patient Key"].astype(int)
    queryResults["Patient Key"] = queryResults["Patient Key"].astype(int)
    patientKeysInput["Found"] = patientKeysInput["Patient Key"].isin(queryResults["Patient Key"])
    personIDsFound = patientKeysInput.set_index("Patient Key").join(queryResults.set_index("Patient Key"), "Patient Key", "left")
    personIDsFound = personIDsFound.sort_values("person_id")

    # Summary statistics
    numFound = personIDsFound["Found"].sum()
    numPatientKeys = len(patientKeysInput)
    logger.info(f"""A total of {numFound:,} patient keys of {numPatientKeys:,} were mapped to OMOP person IDs.""")
    logger.info("""If the number of person IDs is LESS THAN the number of patient keys, it's possible that some patients were merged BEFORE the OMOP database was updated.""")
    logger.info("""If the number of person IDs is GREATER THAN the number of patient keys, it's possible that some patients were merged AFTER the OMOP database was updated.""")

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
    personIDsFoundExportPath = runOutputDir.joinpath("Person IDs - QA.csv")
    personIDsFound2.to_csv(personIDsFoundExportPath)
    logger.info(f"""The map of patient keys to person IDs, and those missing or found, was saved to "{personIDsFoundExportPath.absolute().relative_to(rootDirectory)}".""")

    # Save results: person IDs
    personIDs = personIDsFound["person_id"].drop_duplicates().dropna().sort_values().astype(int)
    personIDsExportPath = runOutputDir.joinpath("Person IDs.csv")
    personIDs.to_csv(personIDsExportPath, index=False)
    logger.info(f"""Person IDs were saved to "{personIDsExportPath.relative_to(projectDir)}".""")

    # Remove intermediate files
    shutil.rmtree(runIntermediateDataDir)

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
