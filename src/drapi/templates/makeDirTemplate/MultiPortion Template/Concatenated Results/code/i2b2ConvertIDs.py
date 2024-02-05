"""
Converts i2b2 `PATIENT_NUM` and `ENCOUNTER_NUM` IDs to "Patient Key" and "Encounter # (CSN)", respectively.
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
I2B2_PORTION_OUTPUT_DIR_PATH = Path(r"..\Intermediate Results\i2b2 Portion\data\output\i2b2_dump\...\i2b2")
I2B2_COHORT_IDS_FILE_PATH = Path(r"..\Intermediate Results\i2b2 Portion\data\Cohort IDs.CSV")
ENCOUNTER_MAP_PATH = Path(r"..\Concatenated Results\data\output\i2b2MakeMap\...\i2b2 Encounter Map.CSV")
PATIENT_MAP_PATH1 = Path(r"..\Concatenated Results\data\output\i2b2MakeMap\...\i2b2 Patient Map.CSV")  # i2b2 to EPIC Patient ID
PATIENT_MAP_PATH2 = Path(r"..\Concatenated Results\data\output\i2b2MakeMap\...\i2b2 Patient Map.CSV")  # EPIC Patient ID to Patient Key

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
    `I2B2_COHORT_IDS_FILE_PATH`: "{I2B2_COHORT_IDS_FILE_PATH}"
    `ENCOUNTER_MAP_PATH`: "{ENCOUNTER_MAP_PATH}"
    `PATIENT_MAP_PATH1`: "{PATIENT_MAP_PATH1}"
    `PATIENT_MAP_PATH2`: "{PATIENT_MAP_PATH2}"

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

    # Load maps
    logger.info("""Loading maps.""")
    encounterMap = pd.read_csv(ENCOUNTER_MAP_PATH)

    # Get un-linked patients and drop them.
    cohortIDs = pd.read_csv(I2B2_COHORT_IDS_FILE_PATH)
    unlinkedPatientsMask = cohortIDs["Patient Key"].isna()
    unlinkedPatients = cohortIDs["I2B2_PATIENT_NUM"][unlinkedPatientsMask]

    TARGET_ID_NAME = "Patient Key"

    colnamedict = {"ENCOUNTER_NUM": encounterMap.columns[1],
                   "PATIENT_NUM": TARGET_ID_NAME}

    # Convert maps to dictionaries
    logger.info("""Converting maps to dictionaries.""")
    encounterDict = {k: v for k, v in zip(encounterMap.iloc[:, 0], encounterMap.iloc[:, 1])}
    encounterDict[""] = ""
    patientDict3 = {k: v for k, v in zip(cohortIDs["I2B2_PATIENT_NUM"], cohortIDs[TARGET_ID_NAME])}

    # Convert i2b2 IDs
    logger.info("""Converting i2b2 IDs.""")
    MESSAGE_MODULO = 50
    for fpath in I2B2_PORTION_OUTPUT_DIR_PATH.iterdir():
        logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
        if fpath.suffix.lower() == ".csv":
            numChunks = 0
            CHUNKSIZE = 10000
            for _ in pd.read_csv(fpath, chunksize=CHUNKSIZE):
                numChunks += 1
            # Logger block
            if numChunks < MESSAGE_MODULO:
                numChunksTenth = numChunks
            else:
                numChunksTenth = round(numChunks / MESSAGE_MODULO)

            # Iterate over file chunks
            header = True
            mode = "w"
            savepath = runOutputDir.joinpath(fpath.name)
            for it, chunk in enumerate(pd.read_csv(fpath, chunksize=CHUNKSIZE), start=1):
                if it % numChunksTenth == 0:
                    logger.info(f"""    Working on chunk {it} of {numChunks}.""")
                chunk = pd.DataFrame(chunk)
                newChunk = chunk.copy()

                # Drop un-linked patients
                mdrop = newChunk["PATIENT_NUM"].isin(unlinkedPatients)
                newChunk = newChunk[~mdrop]

                # Convert patient IDs
                if "PATIENT_NUM" in chunk.columns:
                    newChunk["PATIENT_NUM"] = newChunk["PATIENT_NUM"].apply(lambda i2b2ID: patientDict3[i2b2ID])
                    newChunk = newChunk.rename(columns={"PATIENT_NUM": colnamedict["PATIENT_NUM"]})

                # Convert encounter IDs
                if "ENCOUNTER_NUM" in chunk.columns:
                    newChunk = newChunk.copy()
                    mask = newChunk["ENCOUNTER_NUM"] < 0
                    newChunk.loc[mask, "ENCOUNTER_NUM"] = ""
                    newChunk["ENCOUNTER_NUM"] = newChunk["ENCOUNTER_NUM"].apply(lambda i2b2ID: encounterDict[i2b2ID])
                    newChunk = newChunk.rename(columns={"ENCOUNTER_NUM": colnamedict["ENCOUNTER_NUM"]})

                # Save converted chunk
                newChunk.to_csv(savepath, header=header, mode=mode, index=False)
                header = False
                mode = "a"
        else:
            pass

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
