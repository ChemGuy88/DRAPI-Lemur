"""
Converts a map CSV to a SQLite database.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
import sqlite3
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    readDataFile,
                                    successiveParents)
from drapi.code.drapi.constants.constants import DATA_TYPES_DICT_SQL
# Super-local
pass

# Arguments
if True:
    MAP_PATH = r"/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Intermediate Results/SQL Portion/data/output/getData/2024-02-22 16-44-29"  # String, the path to the map CSV file or the directory that contains a series of files that combined form a map CSV.
    VARIABLE_NAME_FROM = "provider_id"
    VARIABLE_NAME_TO = "Provider Key"
elif True:
    MAP_PATH = r"..\Intermediate Results\SQL Portion\data\output\getData\2024-01-19 21-42-27"  # String, the path to the map CSV file or the directory that contains a series of files that combined form a map CSV.
    VARIABLE_NAME_FROM = "visit_occurrence_id"
    VARIABLE_NAME_TO = "Encounter # (CSN)"
elif True:
    MAP_PATH = r"..\OMOP_Structured_Data\data\output\mapping\MRN_mapping.csv"  # String, the path to the map CSV file or the directory that contains a series of files that combined form a map CSV.
    VARIABLE_NAME_FROM = "person_id"
    VARIABLE_NAME_TO = "PatientKey"

CHUNKSIZE = 50000  # The number of rows to read at a time from the CSV using Pandas `chunksize`
MESSAGE_MODULO_CHUNKS = 50  # How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_CHUNKS`
MESSAGE_MODULO_FILES = 100  # How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_FILES`

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 1
IDR_DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 4

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

# Functions


def createSqliteDatabase(databasePath: str,
                         variableNameFrom: str,
                         variableNameTo: str,
                         dataTypesDictSql: dict) -> None:
    """
    """
    with sqlite3.connect(databasePath) as connection:
        cursor = connection.cursor()
        cursor.execute(f"""CREATE TABLE '{tableName}'
                    (
                    '{variableNameFrom}' {dataTypesDictSql[variableNameFrom]},
                    '{variableNameTo}' {dataTypesDictSql[variableNameTo]}
                    )""")


def insertIntoSqliteDatabase(databasePath: str,
                             variableNameFrom: str,
                             variableNameTo: str,
                             dataFrame: pd.DataFrame) -> None:
    """
    """
    with sqlite3.connect(databasePath) as connection:
        cursor = connection.cursor()
        for it, (label, rowSeries) in enumerate(dataFrame.iterrows(), start=1):
            cursor.execute(f"""INSERT INTO '{tableName}'
                        (
                        '{variableNameFrom}',
                        '{variableNameTo}'
                        )
                        values
                        (
                        {rowSeries[variableNameFrom]},
                        {rowSeries[variableNameTo]}
                        )""")
        connection.commit()


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
    `MAP_PATH`: "{MAP_PATH}"
    `VARIABLE_NAME_FROM`: "{VARIABLE_NAME_FROM}"
    `VARIABLE_NAME_TO`: "{VARIABLE_NAME_TO}"
    `CHUNKSIZE`: "{CHUNKSIZE}"
    `MESSAGE_MODULO_CHUNKS`: "{MESSAGE_MODULO_CHUNKS}"
    `MESSAGE_MODULO_FILES`: "{MESSAGE_MODULO_FILES}"

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

    # Create script variables
    mapPath = Path(MAP_PATH)
    databaseName = f"""{VARIABLE_NAME_FROM} to {VARIABLE_NAME_TO}"""
    tableName = databaseName[:]
    databasePath = runOutputDir.joinpath(f"{databaseName}.db")

    # Create SQLite database
    logger.info("""Creating SQLite database.""")
    if mapPath.is_file():
        logger.info("""  The path provided is for a file.""")
        logger.info("""  Counting the number of chunks in the file.""")
        fileChunks = readDataFile(fname=mapPath,
                                  chunksize=CHUNKSIZE)
        numChunks = sum([1 for _ in fileChunks])
        logger.info("""  Counting the number of chunks in the file - done.""")
        fileChunks = readDataFile(fname=mapPath,
                                  chunksize=CHUNKSIZE)
        if numChunks < MESSAGE_MODULO_CHUNKS:
            moduloChunks = numChunks
        else:
            moduloChunks = round(numChunks / MESSAGE_MODULO_CHUNKS)
        createSqliteDatabase(databasePath=databasePath,
                             variableNameFrom=VARIABLE_NAME_FROM,
                             variableNameTo=VARIABLE_NAME_TO,
                             dataTypesDictSql=DATA_TYPES_DICT_SQL)
        for it1, dfChunk in enumerate(fileChunks, start=1):
            if it1 == 1 or it1 % moduloChunks == 0:
                logger.info(f"""    Working on chunk {it1:,} of {numChunks:,}.""")
            insertIntoSqliteDatabase(databasePath=databasePath,
                                     variableNameFrom=VARIABLE_NAME_FROM,
                                     variableNameTo=VARIABLE_NAME_TO,
                                     dataFrame=dfChunk)
    elif mapPath.is_dir():
        logger.info("""  The path provided is for a directory.""")
        logger.info("""  Counting the number of files in the directory.""")
        files = sorted(list(mapPath.iterdir()))
        numFiles = len(files)
        logger.info("""  Counting the number of files in the directory - done.""")
        if numFiles < MESSAGE_MODULO_FILES:
            moduloFiles = numFiles
        else:
            moduloFiles = round(numFiles / MESSAGE_MODULO_FILES)
        createSqliteDatabase(databasePath=databasePath,
                             variableNameFrom=VARIABLE_NAME_FROM,
                             variableNameTo=VARIABLE_NAME_TO,
                             dataTypesDictSql=DATA_TYPES_DICT_SQL)
        for it2, fpath in enumerate(files, start=1):
            if it2 == 1 or it2 % moduloFiles == 0:
                allowLogs = True
            else:
                allowLogs = False
            if allowLogs:
                logger.info(f"""  Working on file {it2:,} of {numFiles:,}.""")
                logger.info("""  Counting the number of chunks in the file.""")
            fileChunks = readDataFile(fname=fpath,
                                      chunksize=CHUNKSIZE)
            numChunks = sum([1 for _ in fileChunks])
            if allowLogs:
                logger.info("""  Counting the number of chunks in the file - done.""")
            fileChunks = readDataFile(fname=fpath,
                                      chunksize=CHUNKSIZE)
            if numChunks < MESSAGE_MODULO_CHUNKS:
                moduloChunks = numChunks
            else:
                moduloChunks = round(numChunks / MESSAGE_MODULO_CHUNKS)
            for it1, dfChunk in enumerate(fileChunks, start=1):
                if allowLogs:
                    if it1 == 1 or it1 % moduloChunks == 0:
                        logger.info(f"""    Working on chunk {it1:,} of {numChunks:,}.""")
                insertIntoSqliteDatabase(databasePath=databasePath,
                                         variableNameFrom=VARIABLE_NAME_FROM,
                                         variableNameTo=VARIABLE_NAME_TO,
                                         dataFrame=dfChunk)

    else:
        raise Exception(f"""Input file "{mapPath.absolute().relative_to(rootDirectory)}" is neither a file nor a directory.""")
    logger.info("""Creating SQLite database - done.""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
