"""
Collects i2b2 `PATIENT_NUM` and `ENCOUNTER_NUM` values.

NOTE This is not needed if you use the output from i2b2_dump.get_IDs().
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)

# Arguments
I2B2_PORTION_OUTPUT_DIR_PATH = Path(r"..\Intermediate Results\i2b2 Portion\data\output\i2b2_dump\2023-11-20 20-35-58\i2b2")

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
connection = create_engine(conStr).connect().execution_options(stream_results=True)

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
    `I2B2_PORTION_OUTPUT_DIR_PATH`: "{I2B2_PORTION_OUTPUT_DIR_PATH}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    # Get set of all patient and encounter IDs
    logger.info("Getting the set of all patient and encounter IDs.")
    patientpath = runOutputDir.joinpath("Sets", "PATIENT_NUM.CSV")
    encounterpath = runOutputDir.joinpath("Sets", "ENCOUNTER_NUM.CSV")
    makeDirPath(patientpath.parent)
    makeDirPath(encounterpath.parent)
    patientmode = "w"
    encountermode = "w"
    patientheader = True
    encounterheader = True
    MESSAGE_MODULO = 50
    for fpath in I2B2_PORTION_OUTPUT_DIR_PATH.iterdir():
        logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
        if fpath.suffix.lower() == ".csv":
            numChunks = 0
            CHUNKSIZE = 10000
            for _ in pd.read_csv(fpath, chunksize=CHUNKSIZE):
                numChunks += 1
            if numChunks < MESSAGE_MODULO:
                numChunksTenth = numChunks
            else:
                numChunksTenth = round(numChunks / MESSAGE_MODULO)
            for it, chunk in enumerate(pd.read_csv(fpath, chunksize=CHUNKSIZE), start=1):
                if it % numChunksTenth == 0:
                    logger.info(f"""    Working on chunk {it} of {numChunks}.""")
                chunk = pd.DataFrame(chunk)
                if "PATIENT_NUM" in chunk.columns:
                    patientIDs = chunk["PATIENT_NUM"].drop_duplicates().sort_values()
                    patientIDs.to_csv(patientpath, mode=patientmode, header=patientheader, index=False)
                    patientmode = "a"
                    patientheader = False
                if "ENCOUNTER_NUM" in chunk.columns:
                    encounterIDs = chunk["ENCOUNTER_NUM"].drop_duplicates().sort_values()
                    encounterIDs.to_csv(encounterpath, mode=encountermode, header=encounterheader, index=False)
                    encountermode = "a"
                    encounterheader = False
        else:
            pass

    # Save sorted, unique IDs, and drop negative encounter IDs
    # Note that in i2b2, negative encounter IDs are actually negative patient IDs.
    logger.info("Saving sorted, unique IDs - patients.")
    patientset = pd.read_csv(patientpath)["PATIENT_NUM"].drop_duplicates().dropna().sort_values()
    logger.info("Saving sorted, unique IDs - patients - done.")

    logger.info("Saving sorted, unique IDs - encounters.")
    encounterset = pd.read_csv(encounterpath)["ENCOUNTER_NUM"].drop_duplicates().dropna().sort_values()
    logger.info("Saving sorted, unique IDs - encounters - done.")
    mask = encounterset > 0
    encounterset = encounterset[mask]

    patientset.to_csv(patientpath, index=False)
    encounterset.to_csv(encounterpath, index=False)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
