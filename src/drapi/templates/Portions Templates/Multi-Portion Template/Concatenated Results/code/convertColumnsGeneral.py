"""
Convert columns.

# NOTE This is a more general form of the OMOP-only version, "convertColumns.py"
# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# TODO Assign portion name to each path (per OS) so that portion files are stored in their respective folders, this prevents file from being overwritten in the unlikely, but possible, case files from different portions have the same name.
"""

import logging
import os
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
import sqlite3
# Local packages
from drapi.code.drapi.drapi import (flatExtend,
                                    getTimestamp,
                                    makeDirPath,
                                    makeMap,
                                    readDataFile,
                                    successiveParents)
# Local packages: Script parameters: General
from common import (IRB_NUMBER,
                    ALIAS_DATA_TYPES,
                    DATA_REQUEST_ROOT_DIRECTORY_DEPTH,
                    DATA_TYPES_DICT,
                    VARIABLE_ALIASES,
                    VARIABLE_SUFFIXES)
# Local packages: Script parameters: Paths
from common import (MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN,
                    NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN,
                    OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN,
                    OMOP_PORTION_2_DIR_MAC, OMOP_PORTION_2_DIR_WIN)
# Local packages: Script parameters: File criteria
from common import (NOTES_PORTION_FILE_CRITERIA,
                    OMOP_PORTION_FILE_CRITERIA)

# Arguments
if True:
    MAPS = {"provider_id": {"to": "Provider Key",
                            "mapPath": r"../Concatenated Results/data/output/mapToSqlite/2024-02-23 17-36-14/provider_id to Provider Key.db"}}
    MAC_PATHS = [Path("/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Concatenated Results/data/output/convertColumnsGeneral/2024-01-24 17-48-25"),
                 Path("/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Concatenated Results/data/output/convertColumnsGeneral/2024-01-26 20-17-44")]
    WIN_PATHS = []
    LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA,
                                  OMOP_PORTION_FILE_CRITERIA]
elif False:
    MAPS = {"person_id": {"to": "PatientKey",
                          "mapPath": r"..\Concatenated Results\data\output\mapToSqlite\2024-01-22 20-58-28\person_id to PatientKey.db"}}
    MAC_PATHS = [OMOP_PORTION_DIR_MAC]
    WIN_PATHS = [OMOP_PORTION_DIR_WIN]
    LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA + [lambda pathObj: pathObj.stem != "condition_occurrence"]]
elif True:
    MAPS = {"person_id": {"to": "PatientKey",
                          "mapPath": r"..\Concatenated Results\data\output\mapToSqlite\2024-01-22 20-58-28\person_id to PatientKey.db"},
            "visit_occurrence_id": {"to": "Encounter # (CSN)",
                                    "mapPath": r"..\Concatenated Results\data\output\mapToSqlite\2024-01-22 21-11-13\visit_occurrence_id to Encounter # (CSN).db"}}
    MAC_PATHS = [OMOP_PORTION_DIR_MAC,
                 OMOP_PORTION_2_DIR_MAC]
    WIN_PATHS = [OMOP_PORTION_DIR_WIN,
                 OMOP_PORTION_2_DIR_WIN]
    previouslyDoneFiles = flatExtend([[fpath.stem for fpath in Path(r"..\Concatenated Results\data\output\convertColumnsGeneral\2024-01-24 17-48-25").iterdir()],
                                      []])
    newOMOPFileCriteria = OMOP_PORTION_FILE_CRITERIA + [lambda pathObj: pathObj.stem not in previouslyDoneFiles]
    LIST_OF_PORTION_CONDITIONS = [newOMOPFileCriteria,
                                  newOMOPFileCriteria]
elif True:
    MAPS = {"PatientKey": {"to": "De-identified PatientKey",
                           "mapPath": r""},
            "EncounterCSN": {"to": "De-identified EncounterCSN",
                             "mapPath": r""}}
    MAC_PATHS = [MODIFIED_OMOP_PORTION_DIR_MAC,
                 NOTES_PORTION_DIR_MAC]
    WIN_PATHS = [MODIFIED_OMOP_PORTION_DIR_WIN,
                 NOTES_PORTION_DIR_WIN]
    LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA,
                                  NOTES_PORTION_FILE_CRITERIA]

# Arguments; General
CHUNK_SIZE = 50000
MESSAGE_MODULO_CHUNKS = 100  # How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_CHUNKS`

# Arguments: Meta-variables
CONCATENATED_RESULTS_DIRECTORY_DEPTH = DATA_REQUEST_ROOT_DIRECTORY_DEPTH - 1
PROJECT_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH  # The concatenation suite of scripts is considered to be the "project".
IRB_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH + 2
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "DATA_REQUEST_DIRECTORY"  # TODO One of the following:
# ["IDR_DATA_REQUEST_DIRECTORY",      # noqa
#  "IRB_DIRECTORY",                   # noqa
#  "DATA_REQUEST_DIRECTORY",          # noqa
#  "CONCATENATED_RESULTS_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
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

if ROOT_DIRECTORY == "CONCATENATED_RESULTS_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "linux":
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    print("Not implemented. Check settings in your script.")
    sys.exit()

# Directory creation: General
makeDirPath(runIntermediateDataDir)
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Functions

def choosePathToLog(path: Path, rootPath: Path) -> Path:
    """
    Decides if a path is a subpath of `rootPath`. If it is, display it reltaive to `rootPath`. If it is not, display it as an absolute path.
    """
    commonPath = os.path.commonpath([path.absolute(), rootPath.absolute()])

    lenCommonPath = len(commonPath)
    lenRootPath = len(str(rootPath.absolute()))
    if lenCommonPath < lenRootPath:
        pathToDisplay = path
    elif lenCommonPath >= lenRootPath:
        pathToDisplay = path.absolute().relative_to(rootPath)
    else:
        raise Exception("An unexpected error occurred.")
                                    
    return pathToDisplay


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
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Assert all portions have file criteria accounted for
    if len(listOfPortionDirs) == len(LIST_OF_PORTION_CONDITIONS):
        pass
    else:
        raise Exception("The number of portions does not equal the number of portion conditions.")

    # Collect columns to convert
    columnsToConvert = sorted(list(MAPS.keys()))

    # Load de-identification maps for each variable that needs to be de-identified
    logging.info("""Loading de-identification maps for each variable that needs to be de-identified.""")
    mapsDi = {}
    mapsColumnNames = {}
    variablesCollected = [fname for fname in MAPS.keys()]
    for varName in variablesCollected:
        logging.info(f"""  Loading map for "{varName}".""")
        toVariable = MAPS[varName]["to"]
        varPath = MAPS[varName]["mapPath"]
        tableName = f"{varName} to {toVariable}"
        with sqlite3.connect(varPath) as connection:
            map_ = pd.read_sql_query(sql=f"SELECT * FROM '{tableName}' LIMIT 1", con=connection)
        mapsDi[varName] = map_
        mapsColumnNames[varName] = map_.columns[-1]
    # Add aliases to `mapsColumnNames`
    for varName in VARIABLE_ALIASES.keys():
        varAlias = VARIABLE_ALIASES[varName]
        map_ = makeMap(IDset=set(),
                       IDName=varName,
                       startFrom=1,
                       irbNumber=IRB_NUMBER,
                       suffix=VARIABLE_SUFFIXES[varAlias]["deIdIDSuffix"],
                       columnSuffix=varName,
                       deIdentificationMapStyle="lemur",
                       logger=logging.getLogger())
        mapsColumnNames[varName] = map_.columns[-1]
    # Add aliases to `DATA_TYPES_DICT`
    DATA_TYPES_DICT.update(ALIAS_DATA_TYPES)

    # De-identify columns
    logging.info("""De-identifying files.""")
    allowLogging = False
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{choosePathToLog(directory, rootDirectory)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{choosePathToLog(file, rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logging.info("""    File has met all conditions for processing.""")
                logging.info("""  ..  Reading file to count the number of chunks.""")
                numChunks = sum([1 for _ in readDataFile(file, chunksize=CHUNK_SIZE, low_memory=False)])
                logging.info(f"""  ..  This file has {numChunks:,} chunks.""")
                # Calculate logging requency
                if numChunks < MESSAGE_MODULO_CHUNKS:
                    moduloChunks = numChunks
                else:
                    moduloChunks = round(numChunks / MESSAGE_MODULO_CHUNKS)
                if numChunks / moduloChunks < 100:
                    moduloChunks = 1
                else:
                    pass
                dfChunks = readDataFile(file, chunksize=CHUNK_SIZE, low_memory=False)
                filePreview = readDataFile(file, nrows=2)
                filePreview = pd.DataFrame(filePreview)
                nasumDict = {columnName: {"nasumRows": 0,
                                          "nasumValues": 0,
                                          "nasumRowsTotal": 0,
                                          "nasumValuesTotal": 0} for columnName in filePreview.columns}
                for it, dfChunk0 in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk0)
                    # Work on chunk
                    if it % moduloChunks == 0:
                        allowLogging = True
                    else:
                        allowLogging = False
                    if allowLogging:
                        logging.info(f"""  ..  Working on chunk {it:,} of {numChunks:,}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        if allowLogging:
                            logging.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in columnsToConvert:
                            if allowLogging:
                                logging.info("""  ..  ..  Column must be converted. Converting column...""")
                            # Get position of (old) column
                            oldColumnPosition = dfChunk.columns.get_loc(columnName)
                            # Build map for chunk
                            databasePath = MAPS[columnName]["mapPath"]
                            toVariable = MAPS[columnName]["to"]
                            tableName = f"{columnName} to {toVariable}"
                            with sqlite3.connect(database=databasePath) as connection:
                                cursor = connection.cursor()
                                uniqueValues = dfChunk[columnName].dropna().drop_duplicates()
                                queryFilterArgument = ",".join(uniqueValues.astype(str).to_list())
                                query = f"""SELECT
                                                A.'{columnName}'
                                                ,A.'{toVariable}'
                                            FROM
                                                '{tableName}' AS A
                                            WHERE
                                                A.'{columnName}' in ({queryFilterArgument})
                                         """
                                cursor.execute(query)
                                sqliteResult = cursor.fetchall()
                                chunkMapColumnNames = [columnName, toVariable]
                                chunkMap = pd.DataFrame(sqliteResult, columns=chunkMapColumnNames)
                            # Add new column
                            dfChunk = dfChunk.join(other=chunkMap.set_index(columnName),
                                                   on=columnName,
                                                   how="outer",
                                                   lsuffix="",
                                                   rsuffix="_R")
                            # Remove old column and extra column
                            _ = dfChunk.pop(columnName)
                            # Move new column to old column position
                            newColumnName = mapsColumnNames[columnName]
                            _ = dfChunk.insert(loc=oldColumnPosition,
                                               column=newColumnName,
                                               value=dfChunk.pop(newColumnName))
                            # QA: Count un-mapped rows and values. Update total count for file
                            columnSeries = pd.Series(dfChunk[newColumnName])
                            nasumRows = columnSeries.isna().sum()
                            nasumValues = len(uniqueValues) - uniqueValues.isin(chunkMap[columnName]).sum()
                            nasumDict[columnName]["nasumRows"] = nasumRows
                            nasumDict[columnName]["nasumValues"] = nasumValues
                            nasumDict[columnName]["nasumRowsTotal"] += nasumRows
                            nasumDict[columnName]["nasumValuesTotal"] += nasumValues
                            if nasumValues > 0:
                                logging.warning(f"""  ..  WARNING: there were {nasumRows:,} missing ID values (NaNs) for "{columnName}". This might be an indication of failure to map values. The number is not a count of unique values.""")
                            if nasumValues > 0:
                                logging.warning(f"""  ..  WARNING: There were {nasumValues:,} missing unique ID values (NaNs) for "{columnName}". This might be an indication of failure to map values.""")
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    if allowLogging:
                        logging.info(f"""  ..  Chunk saved to "{choosePathToLog(exportPath, rootDirectory)}".""")
                nasumRowsTotal = nasumDict[columnName]["nasumRowsTotal"]
                nasumValuesTotal = nasumDict[columnName]["nasumValuesTotal"]
                nasumdf = pd.DataFrame.from_dict(data=nasumDict)
                warningText = f"""  ..  WARNING: Below are the missing value summaries. Missing values are NaNs. Missing values may be an indication of failure to map values (as in the case of IDs).\n{nasumdf.to_string()}"""
                logging.warning(warningText)
            else:
                logging.info("""    This file does not need to be processed.""")

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{choosePathToLog(runOutputDir, rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
