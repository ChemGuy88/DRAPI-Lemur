"""
Get all variables/columns of tables/files in the project.
"""

import logging
import os
import sys
from collections import OrderedDict
from pathlib import Path
# Third-party packages
import numpy as np
import pandas as pd
from colorama import init as colorama_init
from colorama import (Fore,
                      Style)
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
# Project parameters:
from common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH
# Project parameters: Portion paths and criteria
from common import (BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN,
                    I2B2_PORTION_DIR_MAC, I2B2_PORTION_DIR_WIN,
                    MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN,
                    NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN,
                    OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN)
# Project parameters: Criteria
from common import (BO_PORTION_FILE_CRITERIA,
                    I2B2_PORTION_FILE_CRITERIA,
                    NOTES_PORTION_FILE_CRITERIA,
                    OMOP_PORTION_FILE_CRITERIA)
from drapi.constants.phiVariables import (LIST_OF_PHI_DATES_BO,
                                          LIST_OF_PHI_DATES_NOTES,
                                          LIST_OF_PHI_DATES_OMOP)

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Arguments: Portion Paths and conditions
if USE_MODIFIED_OMOP_DATA_SET:
    OMOPPortionDirMac = MODIFIED_OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = MODIFIED_OMOP_PORTION_DIR_WIN
else:
    OMOPPortionDirMac = OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = OMOP_PORTION_DIR_WIN

PORTIONS_OUTPUT_DIR_PATH_MAC = {"BO": BO_PORTION_DIR_MAC,  # TODO
                                "i2b2": I2B2_PORTION_DIR_MAC,
                                "Notes": NOTES_PORTION_DIR_MAC,
                                "OMOP": OMOP_PORTION_DIR_MAC}
PORTIONS_OUTPUT_DIR_PATH_WIN = {"BO": BO_PORTION_DIR_WIN,  # TODO
                                "i2b2": I2B2_PORTION_DIR_WIN,
                                "Notes": NOTES_PORTION_DIR_WIN,
                                "OMOP": OMOP_PORTION_DIR_WIN}
PORTION_FILE_CRITERIA_DICT = {"BO": BO_PORTION_FILE_CRITERIA,
                              "i2b2": I2B2_PORTION_FILE_CRITERIA,
                              "Notes": NOTES_PORTION_FILE_CRITERIA,
                              "OMOP": OMOP_PORTION_FILE_CRITERIA}

COMPARISON_SET = LIST_OF_PHI_DATES_BO + LIST_OF_PHI_DATES_NOTES + LIST_OF_PHI_DATES_OMOP

# Arguments: Meta-variables
LOG_LEVEL = "DEBUG"

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
isAccessible = np.all([path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_MAC.values()]) or np.all([path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_WIN.values()])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_MAC
    elif operatingSystem == "win32":
        portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_WIN
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
    ``: "{"..."}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)
    # Colorama initialization
    colorama_init()

    # Get columns
    columns = {}
    columnsByPortion = {portionName: {} for portionName in portionsOutputDirPath.keys()}
    for portionName, portionPath in portionsOutputDirPath.items():
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        content_names = "\n  ".join(sorted([path.name for path in content_paths]))
        dirRelativePath = portionPath.absolute().relative_to(rootDirectory)
        logger.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logger.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = PORTION_FILE_CRITERIA_DICT[portionName]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logger.debug(f"""  Reading "{file.absolute().relative_to(rootDirectory)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns
                columnsByPortion[portionName][file.name] = df.columns

    # Get all columns by file
    logger.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    columnsOrdered = OrderedDict(sorted(columns.items()))
    for key, value1 in columnsOrdered.items():
        if it > -1:
            logger.info(key)
            logger.info("")
            for el in sorted(value1):
                logger.info(f"  {el}")
                allColumns.add(el)
            logger.info("")
        it += 1

    # Get all columns by portion and file
    logger.info("""Printing columns by portion and file.""")
    allColumnsByPortion = OrderedDict({portionName: set() for portionName in sorted(columnsByPortion.keys())})
    columnsByPortionOrdered = OrderedDict(sorted(columnsByPortion.items()))
    for portionName, di in columnsByPortionOrdered.items():
        logger.info(f"{portionName}")
        for fileName, value2 in di.items():
            logger.info(f"  {fileName}")
            for el in sorted(value2):
                logger.info(f"    {el}")
                allColumnsByPortion[portionName].add(el)
            logger.info("")

    # Print the set of all columns
    logger.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logger.info(f"  {el}")
    logger.info("")

    # Print the set of all columns by portion
    logger.info("""Print set of columns by portion.""")
    for portionName, columnsSet in allColumnsByPortion.items():
        logger.info(f"""{portionName}""")
        for columnName in sorted(list(columnsSet)):
            if columnName in COMPARISON_SET:
                text = f"""{Fore.LIGHTCYAN_EX}{columnName}{Style.RESET_ALL}"""
            else:
                text = columnName
            logger.info(f"  {text}")
        logger.info("")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
