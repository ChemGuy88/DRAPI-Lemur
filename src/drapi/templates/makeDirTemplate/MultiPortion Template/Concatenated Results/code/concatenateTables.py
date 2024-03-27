"""
Concatenates files by converting them to Pandas DataFrames and using `pd.concat`.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    readDataFile,
                                    successiveParents)

# Arguments
LIST_OF_FILE_PATHS = Path(r"..\..").iterdir()
TARGET_FILE_PATH = Path()

CHUNKSIZE = 10000

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = DATA_REQUEST_DIR_DEPTH + 0
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

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
    `LIST_OF_FILE_PATHS`: "{LIST_OF_FILE_PATHS}"
    `TARGET_FILE_PATH`: "{TARGET_FILE_PATH}"
    `CHUNKSIZE`: "{CHUNKSIZE}"

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

    # Concatenate files
    mode = "w"
    numFiles = len(LIST_OF_FILE_PATHS)
    logger
    for it1, fpath in enumerate(sorted(LIST_OF_FILE_PATHS), start=1):
        logger.info(f"""  Working on file {it1:,} of {numFiles:,}: {fpath.absolute().relative_to(projectDir)}.""")
        logger.info("""    Counting the number of chunks.""")
        numChunks = sum([1 for _ in readDataFile(fname=fpath,
                                                 chunksize=CHUNKSIZE)])
        logger.info("""    Counting the number of chunks - done.""")
        fileChunks = readDataFile(fname=fpath,
                                  chunksize=CHUNKSIZE)
        for it2, df in enumerate(fileChunks, start=1):
            logger.info(f"""    Working on chunk {it2:,} of {numChunks:,}: {fpath.absolute().relative_to(projectDir)}.""")
            df = pd.DataFrame(df)
            topath = TARGET_FILE_PATH.joinpath(fpath.name)
            df.to_csv(topath)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
