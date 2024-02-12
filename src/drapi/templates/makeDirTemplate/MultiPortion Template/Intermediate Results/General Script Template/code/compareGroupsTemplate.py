"""
Compare two cohort (group) files.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.compareGroups import (compareGroups,
                                            determineMapType,
                                            determineMapTypeFromMap,
                                            mappingAnalysis)

# Arguments
COHORT_1_FILE_PATH = r""
COHORT_2_FILE_PATH = r""
PATIENT_MAP_FILE_PATH = r""
FROM_COLUMN = ""
TO_COLUMN = ""

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 3
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 3
IDR_DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 6

ROOT_DIRECTORY = "IRB_DIRECTORY"  # TODO One of the following:
# ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
#  "IRB_DIRECTORY",                 # noqa
#  "DATA_REQUEST_DIRECTORY",        # noqa
#  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

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
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
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
pass

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Variables: Other
pass

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

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
    `COHORT_1_FILE_PATH`: "{COHORT_1_FILE_PATH}"
    `COHORT_2_FILE_PATH`: "{COHORT_2_FILE_PATH}"
    `PATIENT_MAP_FILE_PATH`: "{PATIENT_MAP_FILE_PATH}"

    # Arguments: General
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

    # Load raw data
    group1data0 = pd.read_csv(COHORT_1_FILE_PATH)
    group2data = pd.read_csv(COHORT_2_FILE_PATH)

    patientMap0 = pd.read_csv(PATIENT_MAP_FILE_PATH)

    # Process data
    patientMap = patientMap0[[FROM_COLUMN, TO_COLUMN]]

    # Mapping analysis
    mappingAnalysis(x0=group1data0,
                    m0=patientMap,
                    logger=logger)
    group1data1_inner = group1data0.dropna().drop_duplicates().set_index(FROM_COLUMN).join(other=patientMap.set_index(FROM_COLUMN),
                                                                                           how="inner",
                                                                                           lsuffix="_L",
                                                                                           rsuffix="_R").reset_index()
    group1data1_outer = group1data0.dropna().drop_duplicates().set_index(FROM_COLUMN).join(other=patientMap.set_index(FROM_COLUMN),
                                                                                           how="outer",
                                                                                           lsuffix="_L",
                                                                                           rsuffix="_R").reset_index()
    group1series1 = group1data1_inner[TO_COLUMN].dropna().drop_duplicates()
    group1series2 = group1data1_outer[TO_COLUMN].dropna().drop_duplicates()
    group2series = group2data[TO_COLUMN].dropna().drop_duplicates()
    compareGroups(group1=group1series1,
                  group2=group2series,
                  logger=logger)
    compareGroups(group1=group1series2,
                  group2=group2series,
                  logger=logger)

    mapType1 = determineMapType(x0=group1data0,
                                x1=group1data1_inner[TO_COLUMN])
    mapType2 = determineMapType(x0=group1data0,
                                x1=group1data1_outer[TO_COLUMN])
    mapType3 = determineMapTypeFromMap(x0=group1data0,
                                       m0=patientMap,
                                       logger=logger)
    logger.info(f"""The mapping of group1 (inner-joined) is of type "{mapType1}".""")
    logger.info(f"""The mapping of group1 (outer-joined) is of type "{mapType2}".""")
    logger.info(f"""The mapping of group1 (from `determineMapTypeFromMap`) is of type "{mapType3}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
