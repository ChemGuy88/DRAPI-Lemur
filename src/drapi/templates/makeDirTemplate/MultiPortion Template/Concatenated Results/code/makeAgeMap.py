"""
Creates an age de-identification map. This is an object that identifies patients who are aged 90 or more at the time of processing (i.e., now, when the script is run).

This is usually run before `deIdentifyByAge`.

Optionally this also creates a second map using a second set of ID's, which is usually necessary if you are operating on a data set that has already had its IDs de-identified. This optional function uses the following parameters:

    - `SECONDARY_MAP`
    - `SECONDARY_MAP_COLUMN_NAME_FROM`
    - `SECONDARY_MAP_COLUMN_NAME_TO`

Note that there must be a variable (column) in common between the tables `SECONDARY_MAP` and `INPUT_FILE`, for the patients to be correctly mapped from one table to the other.
"""

import logging
import os
from datetime import datetime as dt
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)

# Arguments
INPUT_FILE = Path(r"..\Concatenated Results\data\output\convertColumns\...\person.csv")
PATIENT_ID_NAME = "Patient Key"
DATE_OF_BIRTH_COLUMN = "birth_datetime"
AGE_THRESHOLD = 90

SECONDARY_MAP = Path(r"..\Concatenated Results\data\output\concatenateMaps\...\Patient Key map.csv")  # Path object or `None`
SECONDARY_MAP_COLUMN_NAME_FROM = "Patient Key"
SECONDARY_MAP_COLUMN_NAME_TO = "De-identified Patient Key"

# Arguments; General
CHUNK_SIZE = 50000

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 1
IDR_DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2

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
makeDirPath(runIntermediateDataDir)
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
    `INPUT_FILE`: "{INPUT_FILE}"
    `PATIENT_ID_NAME`: "{PATIENT_ID_NAME}"
    `DATE_OF_BIRTH_COLUMN`: "{DATE_OF_BIRTH_COLUMN}"
    `AGE_THRESHOLD`: "{AGE_THRESHOLD}"

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

    logger.info(f"""Working on file "{INPUT_FILE.absolute().relative_to(rootDirectory)}".""")
    # Set file options
    exportPath = runIntermediateDataDir.joinpath(INPUT_FILE.name)
    fileMode = "w"
    fileHeaders = True
    # Read file
    logger.info("""    Reading file to count the number of chunks.""")
    numChunks = sum([1 for _ in pd.read_csv(INPUT_FILE, chunksize=CHUNK_SIZE)])
    logger.info(f"""    This file has {numChunks} chunks.""")
    dfChunks = pd.read_csv(INPUT_FILE, chunksize=CHUNK_SIZE)
    for it, dfChunk in enumerate(dfChunks, start=1):
        dfChunk = pd.DataFrame(dfChunk)
        # Work on chunk
        logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
        dfChunk = dfChunk[[PATIENT_ID_NAME, DATE_OF_BIRTH_COLUMN]]
        dfChunk = dfChunk.drop_duplicates()
        dfChunk = dfChunk.set_index(PATIENT_ID_NAME)
        series = dfChunk[DATE_OF_BIRTH_COLUMN]
        series = pd.to_datetime(series)
        currentAge = dt.today() - series
        currentAge = currentAge.apply(lambda timeDelta: timeDelta.days / 365.25)
        dfChunk["Over Age Threshold"] = currentAge >= AGE_THRESHOLD
        dfChunk["Over Age Threshold"] = dfChunk["Over Age Threshold"].apply(lambda boolean: 1 if boolean else 0)

        # Save chunk
        dfChunk["Over Age Threshold"].to_csv(exportPath, mode=fileMode, header=fileHeaders, index=True)
        fileMode = "a"
        fileHeaders = False
        logger.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")

    # Sort and remove duplicates from map
    logger.info("Sorting and removing duplicates from map.")
    df1 = pd.read_csv(exportPath)
    df1 = df1.drop_duplicates()
    df1 = df1.sort_values(by=[PATIENT_ID_NAME, "Over Age Threshold"])
    logger.info("Sorting and removing duplicates from map - done.")
    savePath1 = runOutputDir.joinpath(f"Age Map - {PATIENT_ID_NAME}.CSV")
    metadataText = f"""# Map generation parameters: `AGE_THRESHOLD`: "{AGE_THRESHOLD}".
# Map generation parameters: `PATIENT_ID_NAME`: "{PATIENT_ID_NAME}".
# Map generation parameters: `DATE_OF_BIRTH_COLUMN`: "{DATE_OF_BIRTH_COLUMN}".
"""
    with open(savePath1, "w") as file:
        file.write(metadataText)
    df1.to_csv(savePath1, index=False, mode="a")

    # Create a map using a secondary map
    if SECONDARY_MAP:
        df1 = df1.set_index(PATIENT_ID_NAME)
        df2 = pd.read_csv(SECONDARY_MAP)
        df2 = df2.set_index(SECONDARY_MAP_COLUMN_NAME_FROM)
        newMap = df1.join(other=df2[SECONDARY_MAP_COLUMN_NAME_TO],
                          how="inner")
        newMap = newMap[[SECONDARY_MAP_COLUMN_NAME_TO, "Over Age Threshold"]]
        savePath2 = runOutputDir.joinpath(f"Age Map - {SECONDARY_MAP_COLUMN_NAME_TO}.CSV")
        with open(savePath2, "w") as file:
            file.write(metadataText)
        newMap.to_csv(savePath2, index=False, mode="a")
    else:
        pass

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
