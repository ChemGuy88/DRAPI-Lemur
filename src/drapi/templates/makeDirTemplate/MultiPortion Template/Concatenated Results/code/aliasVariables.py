"""
Aliases variables that need to be de-identified.

INPUT:
Set Files

PROCESS:
Merge alias Set Files under the aliased (main) variable name

OUTPUT:
A new set file. This file would be the input to "makeMapsFromOthers.py"
"""

import csv
import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
from sqlalchemy import create_engine
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.constants.phiVariables import VARIABLE_NAME_TO_FILE_NAME_DICT, FILE_NAME_TO_VARIABLE_NAME_DICT
# Super-local
from common import VARIABLE_ALIASES, DATA_TYPES_DICT

# Arguments
SET_FILES_DIR = Path(r"..\Concatenated Results\data\output\getIDValues\...\Set Files")

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
    `SET_FILES_DIR`: "{SET_FILES_DIR}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}"

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
    for setFilePath in SET_FILES_DIR.iterdir():
        logger.info(f"""  Working on set file : "{setFilePath.absolute().relative_to(rootDirectory)}".""")
        try:
            df = pd.read_table(setFilePath, header=None)
        except EmptyDataError as err:
            _ = err
            df = pd.DataFrame(dtype=str)
        variableName = FILE_NAME_TO_VARIABLE_NAME_DICT[setFilePath.stem]
        condition1 = variableName in VARIABLE_ALIASES.keys()
        condition2 = variableName in VARIABLE_ALIASES.values()
        dataType = DATA_TYPES_DICT[variableName]
        if dataType == "Datetime":
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "Numeric":
            df = df.astype(float).astype("Int64")
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "String":
            quoting = csv.QUOTE_ALL
        elif dataType == "Numeric_Or_String":
            quoting = csv.QUOTE_ALL
        else:
            raise Exception(f"""Unexpected `dataType` value: "{dataType}".""")
        if condition1 or condition2:
            if condition1:
                aliasName = variableName
                mainName = VARIABLE_ALIASES[aliasName]
                logger.info(f"""    Variable is aliased to "{mainName}".""")
            elif condition2:
                mainName = variableName
                logger.info("""    Variable is the main name of several aliases.""")
            setFileName = f"{mainName}.txt"
            newSetFilePath = runOutputDir.joinpath(setFileName)
            if newSetFilePath.exists():
                logger.info("""  ..  Variable set exists. Appending to file.""")
                fileMode = "a"
            else:
                logger.info("""  ..  Variable set does not exists. Creating file.""")
                fileMode = "w"
            df.to_csv(newSetFilePath, quoting=quoting, mode=fileMode, index=False, header=False)
        else:
            logger.info("""    Variable set file is not aliased.""")
            setFileName = f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]}.txt"
            newSetFilePath = runOutputDir.joinpath(setFileName)
            df.to_csv(newSetFilePath, quoting=quoting, index=False, header=False)

    # Sort and remove duplicates from merged results.
    logger.info("Sorting data and removing duplicates.")
    listOfFiles = sorted(runOutputDir.iterdir())
    for setFilePath in listOfFiles:
        logger.info(f"""  Working on variable `setFilePath`: "{setFilePath.absolute().relative_to(rootDirectory)}".""")
        try:
            series = pd.read_table(setFilePath, header=None).iloc[:, 0]
        except EmptyDataError as err:
            _ = err
            series = pd.Series(dtype=str)
        logger.info(f"""    Starting size of variable set:               "{len(series):,}".""")
        variableName = FILE_NAME_TO_VARIABLE_NAME_DICT[setFilePath.stem]
        dataType = DATA_TYPES_DICT[variableName]
        if dataType == "Datetime":
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "Numeric":
            series = series.astype(float).astype("Int64")
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "String":
            quoting = csv.QUOTE_ALL
        elif dataType == "Numeric_Or_String":
            quoting = csv.QUOTE_ALL
        else:
            raise Exception(f"""Unexpected `dataType` value: "{dataType}".""")
        series = series.drop_duplicates().sort_values()
        logger.info(f"""    Variable set size after removing duplicates: "{len(series):,}".""")
        series.to_csv(setFilePath, quoting=quoting, index=False, header=False)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
