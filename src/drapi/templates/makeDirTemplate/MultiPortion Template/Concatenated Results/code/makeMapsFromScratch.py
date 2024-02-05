"""
Makes de-identification maps from scratch.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Needs to combine similar IDs, like different providers IDs.
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    makeMap,
                                    successiveParents)
# Local packages: Script parameters: General
from common import (IRB_NUMBER,
                    DATA_REQUEST_ROOT_DIRECTORY_DEPTH,
                    VARIABLE_SUFFIXES)
# Project parameters: Portion paths
from common import (BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN,
                    I2B2_PORTION_DIR_MAC, I2B2_PORTION_DIR_WIN,
                    NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN,
                    OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN)
# Project parameters: File criteria
from common import (BO_PORTION_FILE_CRITERIA,
                    I2B2_PORTION_FILE_CRITERIA,
                    NOTES_PORTION_FILE_CRITERIA,
                    OMOP_PORTION_FILE_CRITERIA)

# Arguments
LOG_LEVEL = "DEBUG"

MAC_PATHS = [BO_PORTION_DIR_MAC,
             I2B2_PORTION_DIR_MAC,
             NOTES_PORTION_DIR_MAC,
             OMOP_PORTION_DIR_MAC]
WIN_PATHS = [BO_PORTION_DIR_WIN,
             I2B2_PORTION_DIR_WIN,
             NOTES_PORTION_DIR_WIN,
             OMOP_PORTION_DIR_WIN]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA,
                              I2B2_PORTION_FILE_CRITERIA,
                              NOTES_PORTION_FILE_CRITERIA,
                              OMOP_PORTION_FILE_CRITERIA]

SETS_PATH = Path(r"..\Concatenated Results\data\output\getIDValues\...\Set Files")

CHUNK_SIZE = 50000

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
makeDirPath(runIntermediateDataDir)
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

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
    # Imported from "getIDValues.py"

    # Map values
    for file in SETS_PATH.iterdir():
        variableName = file.stem
        logging.info(f"""  Working on variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Read file
        try:
            df = pd.read_table(file, header=None)
            series = df[0]
        except EmptyDataError as err:
            _ = err
            series = pd.Series()
        values = set(series.values)
        # Map contents
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=1, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName, logger=logging.getLogger())
        # Save map
        mapPath = runOutputDir.joinpath(f"{variableName} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
