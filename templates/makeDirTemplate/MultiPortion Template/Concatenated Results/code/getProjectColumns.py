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
# Local packages
from drapi.drapi import getTimestamp, makeDirPath, successiveParents
from common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH
from common import BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN, BO_PORTION_FILE_CRITERIA
from common import I2B2_PORTION_DIR_MAC, I2B2_PORTION_DIR_WIN, I2B2_PORTION_FILE_CRITERIA
from common import NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, NOTES_PORTION_FILE_CRITERIA
from common import OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, OMOP_PORTION_FILE_CRITERIA

# Arguments
LOG_LEVEL = "DEBUG"
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

    # Get columns
    columns = {}
    columnsByPortion = {portionName: {} for portionName in portionsOutputDirPath.keys()}
    for portionName, portionPath in portionsOutputDirPath.items():
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        content_names = "\n  ".join(sorted([path.name for path in content_paths]))
        dirRelativePath = portionPath.absolute().relative_to(rootDirectory)
        logging.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logging.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = PORTION_FILE_CRITERIA_DICT[portionName]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logging.debug(f"""  Reading "{file.absolute().relative_to(rootDirectory)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns
                columnsByPortion[portionName][file.name] = df.columns

    # Get all columns by file
    logging.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    columnsOrdered = OrderedDict(sorted(columns.items()))
    for key, value1 in columnsOrdered.items():
        if it > -1:
            logging.info(key)
            logging.info("")
            for el in sorted(value1):
                logging.info(f"  {el}")
                allColumns.add(el)
            logging.info("")
        it += 1

    # Get all columns by portion
    logging.info("""Printing columns by portion and file.""")
    allColumnsByPortion = OrderedDict({portionName: set() for portionName in sorted(columnsByPortion.keys())})
    columnsByPortionOrdered = OrderedDict(sorted(columnsByPortion.items()))
    for portionName, di in columnsByPortionOrdered.items():
        logging.info(f"{portionName}")
        for fileName, value2 in di.items():
            logging.info(f"  {fileName}")
            for el in sorted(value2):
                logging.info(f"    {el}")
                allColumnsByPortion[portionName].add(el)
            logging.info("")

    # Print the set of all columns
    logging.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logging.info(f"  {el}")
    logging.info("")

    # Print the set of all columns by portion
    logging.info("""Print set of columns by portion.""")
    # TODO
    for portionName, columnsSet in allColumnsByPortion.items():
        logging.info(f"""{portionName}""")
        for columnName in sorted(list(columnsSet)):
            logging.info(f"  {columnName}")
        logging.info("")

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
