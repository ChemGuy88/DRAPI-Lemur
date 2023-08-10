"""
Get the set of ID values for all variables to de-identify.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

__all__ = ["runIntermediateDataDir"]

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, make_dir_path, successiveParents
from common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH, COLUMNS_TO_DE_IDENTIFY, VARIABLE_ALIASES, NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, NOTES_PORTION_FILE_CRITERIA, OMOP_PORTION_FILE_CRITERIA, BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN, BO_PORTION_FILE_CRITERIA, ZIP_CODE_PORTION_DIR_MAC, ZIP_CODE_PORTION_DIR_WIN, ZIP_CODE_PORTION_FILE_CRITERIA

# Arguments
SETS_PATH = None

CHUNK_SIZE = 50000

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Arguments: Portion Paths and conditions
if USE_MODIFIED_OMOP_DATA_SET:
    OMOPPortionDirMac = MODIFIED_OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = MODIFIED_OMOP_PORTION_DIR_WIN
else:
    OMOPPortionDirMac = OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = OMOP_PORTION_DIR_WIN

MAC_PATHS = [BO_PORTION_DIR_MAC,
             NOTES_PORTION_DIR_MAC,
             OMOPPortionDirMac,
             ZIP_CODE_PORTION_DIR_MAC]
WIN_PATHS = [BO_PORTION_DIR_WIN,
             NOTES_PORTION_DIR_WIN,
             OMOPPortionDirWin,
             ZIP_CODE_PORTION_DIR_WIN]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA,
                              NOTES_PORTION_FILE_CRITERIA,
                              OMOP_PORTION_FILE_CRITERIA,
                              ZIP_CODE_PORTION_FILE_CRITERIA]

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
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    print("Not implemented. Check settings in your script.")
    sys.exit()

# Directory creation: General
make_dir_path(runOutputDir)
make_dir_path(runLogsDir)

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

    # Get set of values
    if SETS_PATH:
        logging.info(f"""Using the set of values previously collected from "{SETS_PATH}".""")
    else:
        logging.info("""Getting the set of values for each variable to de-identify.""")
        mapNames = [columnName for columnName in COLUMNS_TO_DE_IDENTIFY if columnName not in VARIABLE_ALIASES.keys()]
        columnSetsVarsDi = {columnName: {"fpath": runOutputDir.joinpath(f"{columnName}.txt"),
                                         "fileMode": "w"} for columnName in mapNames}
        for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
            # Act on directory
            logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
            for file in directory.iterdir():
                logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logging.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logging.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_DE_IDENTIFY:
                                logging.info("""  ..  ..  Column must be de-identified. Collecting values.""")
                                valuesSet = sorted(list(set(dfChunk[columnName].dropna().values)))
                                if columnName in VARIABLE_ALIASES.keys():
                                    mapLookUpName = VARIABLE_ALIASES[columnName]
                                else:
                                    mapLookUpName = columnName
                                columnSetFpath = columnSetsVarsDi[mapLookUpName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[mapLookUpName]["fileMode"]
                                with open(columnSetFpath, columnSetFileMode) as file:
                                    for value in valuesSet:
                                        file.write(str(value))
                                        file.write("\n")
                                columnSetsVarsDi[mapLookUpName]["fileMode"] = "a"
                                logging.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(rootDirectory)}" in the project directory.""")
                else:
                    logging.info("""    This file does not need to be processed.""")

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logging.info(f"""Finished collecting the set of ID values to de-identify. The set files are located in "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
