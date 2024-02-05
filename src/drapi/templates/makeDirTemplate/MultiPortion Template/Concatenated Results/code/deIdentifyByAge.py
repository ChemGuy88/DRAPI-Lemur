"""
De-identifies those above a certain age threshold by replacing the age with a label and setting the birthdate to "1/1/1800". The label is "> X", where "X" is the age threshold.
"""

import logging
import os
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
# Local packages: Script parameters: General
from drapi.constants.phiVariables import (DICT_OF_PHI_VARIABLES_AGE,
                                          DICT_OF_PHI_VARIABLES_BIRTHDATES)
# Local packages: Script parameters: Paths
# Local packages: Script parameters: File criteria
from common import BO_PORTION_FILE_CRITERIA

# Arguments
AGE_MAP = Path(r"..\Concatenated Results\data\output\makeAgeMap\2024-01-03 13-20-23\Age Map - De-identified Patient Key.CSV")
USE_DE_IDENTIFIED_DATES = True

DE_IDENTIFIED_AGE_VALUE = "> 90"
DE_IDENTIFIED_BIRTHDATE_VALUE = "1/1/1800"

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Variables: Script parameters: Date variables
# NOTE Set `USE_DE_IDENTIFIED_DATES` to `True` if the dates have been de-identified. If the IDs have been de-identified, it is not necessary to set this to `True`.
if USE_DE_IDENTIFIED_DATES:
    DE_IDENTIFICATION_PREFIX = "De-identified "
    dictOfPHIVariablesBirthdates = {portion: [] for portion in DICT_OF_PHI_VARIABLES_BIRTHDATES.keys()}
    for portion, li in DICT_OF_PHI_VARIABLES_BIRTHDATES.items():
        for columnName in li:
            dictOfPHIVariablesBirthdates[portion].append(f"{DE_IDENTIFICATION_PREFIX} {columnName}")
else:
    dictOfPHIVariablesBirthdates = DICT_OF_PHI_VARIABLES_BIRTHDATES

# Variables: Script parameters: Age variables
dictOfPHIVariablesAge = DICT_OF_PHI_VARIABLES_AGE

# Arguments: Portion Paths and conditions
MAC_PATHS = [Path(r"..\Concatenated Results\data\output\deIdentify\...")]  # TODO
WIN_PATHS = [Path(r"..\Concatenated Results\data\output\deIdentify\...")]  # TODO

listOfAgeColumns = [el for value in dictOfPHIVariablesAge.values() for el in value]
listOfBirthdateColumns = [el for value in dictOfPHIVariablesBirthdates.values() for el in value]
listOfColumnsToDeIdentify = listOfAgeColumns + listOfBirthdateColumns
LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA]

# Arguments; General
CHUNK_SIZE = 50000

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

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    print("Not implemented. Check settings in your script.")
    sys.exit()

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
    `AGE_MAP`: "{AGE_MAP}"
    `USE_MODIFIED_OMOP_DATA_SET`: "{USE_MODIFIED_OMOP_DATA_SET}"
    `MAC_PATHS`: "{MAC_PATHS}"
    `WIN_PATHS`: "{WIN_PATHS}"

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

    # Load age de-identification map
    logger.info("""Loading age de-identification map.""")
    map_ = pd.read_csv(AGE_MAP, comment="#")
    logger.info("""Loading age de-identification map - done.""")
    PATIENT_LOOK_UP_ID_NAME = map_.columns[0]
    mapMask = map_["Over Age Threshold"].apply(lambda integer: True if integer else (False if not integer else None))
    patientsToDeIdentify = map_[PATIENT_LOOK_UP_ID_NAME][mapMask]

    # De-identify by age
    logger.info("""De-identifying files.""")
    columnDeIdentificationRenamePrefix = f"{DE_IDENTIFICATION_PREFIX}"
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logger.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logger.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logger.info("""    File has met all conditions for processing.""")
                logger.info("""  ..  Reading file to count the number of chunks.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE, dtype=str)])
                logger.info(f"""  ..  This file has {numChunks} chunks.""")
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE, low_memory=False)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    # Work on chunk
                    logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        logger.info(f"""  ..    Working on column "{columnName}".""")
                        columnShouldBeProcessed = False
                        if columnName in listOfColumnsToDeIdentify:
                            columnShouldBeProcessed = True
                        else:
                            continue
                        if columnShouldBeProcessed:
                            logger.info("""  ..  ..  Column must be de-identified.""")
                            mask = dfChunk[PATIENT_LOOK_UP_ID_NAME].isin(patientsToDeIdentify)
                            if columnName in listOfAgeColumns:
                                dfChunk.loc[mask, columnName] = DE_IDENTIFIED_AGE_VALUE
                            elif columnName in listOfBirthdateColumns:
                                dfChunk.loc[mask, columnName] = DE_IDENTIFIED_BIRTHDATE_VALUE
                            if USE_DE_IDENTIFIED_DATES:
                                if columnName in listOfAgeColumns:
                                    columnRenamePrefix = columnDeIdentificationRenamePrefix
                                else:
                                    columnRenamePrefix = ""
                            else:
                                columnRenamePrefix = columnDeIdentificationRenamePrefix
                            dfChunk = dfChunk.rename(columns={columnName: f"{columnRenamePrefix}{columnName}"})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logger.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logger.info("""    This file does not need to be processed.""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
