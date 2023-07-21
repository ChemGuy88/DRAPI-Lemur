"""
Get all variables/columns of tables/files in the project.
"""

import argparse
import json
import logging
import os
import sys
from collections import OrderedDict
from pathlib import Path
# Third-party packages
import numpy as np
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, make_dir_path, successiveParents, getCommonDirectoryParent
# from .common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH, BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN


def main(portionsOutputDirPath):
    """
    """
    # Get columns
    columns = {}
    for portionName, portionPath in portionsOutputDirPath.items():
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        content_names = "\n  ".join(sorted([path.name for path in content_paths]))
        _ = content_names
        dirRelativePath = portionPath.absolute().relative_to(rootDirectory)
        logging.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logging.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = [lambda x: x.is_file(), lambda x: x.suffix.lower() == ".csv", lambda x: x.name != ".DS_Store"]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logging.debug(f"""  Reading "{file.absolute().relative_to(rootDirectory)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns

    # Get all columns by file
    logging.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    columnsOrdered = OrderedDict(sorted(columns.items()))
    for key, value in columnsOrdered.items():
        if it > -1:
            logging.info(key)
            logging.info("")
            for el in sorted(value):
                logging.info(f"  {el}")
                allColumns.add(el)
            logging.info("")
        it += 1

    # Get all columns by portion
    # TODO
    pass

    # Print the set of all columns
    logging.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logging.info(f"  {el}")


if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--LOG_LEVEL", help="""Increase output verbosity. See "logging" module's log level for valid values.""", type=int, default=10)

    parser.add_argument("PORTIONS_OUTPUT_DIR_PATH_DICT", help="""The dictionary of portion names and paths to the output directory for a specified data request portion. For example: `{"All": "data/output/deleteColumns/data.csv"), "BO": "path/to/data"}`.""", type=json.loads)

    parser.add_argument("PROJECT_DIR_DEPTH", help="""The depth, or number of directories, from the present working directory to this file. The suite of concatenation and de-identification scripts is considered to be the "project".""", type=int)

    parser.add_argument("DATA_REQUEST_ROOT_DIRECTORY_DEPTH", help="""The depth, or number of directories, from the present working directory to the data request folder. Typically the data request folder is the same as the IRB folder, or it may be a subfolder.""", type=int)

    parser.add_argument("IRB_DIR_DEPTH", help="The depth, or number of directories, from the present working directory to the data request's IRB, or equivalent, folder.", type=int)

    parser.add_argument("IDR_DATA_REQUEST_DIR_DEPTH", help="The depth, or number of directories, from the present working directory the IDR Data Request folder on the shared drive.", type=int)

    parser.add_argument("ROOT_DIRECTORY", help="""The directory to be used as the point of reference for relative paths when displaying log messages.""", choices=["IDR_DATA_REQUEST_DIRECTORY", "IRB_DIRECTORY", "DATA_REQUEST_DIRECTORY", "PROJECT_DIRECTORY"], type=str)

    # Parse arguments
    args = parser.parse_args()

    PORTIONS_OUTPUT_DIR_PATH_DICT = args.PORTIONS_OUTPUT_DIR_PATH_DICT
    PORTIONS_OUTPUT_DIR_PATH_DICT = {portionName: Path(stringPath) for portionName, stringPath in PORTIONS_OUTPUT_DIR_PATH_DICT.items()}
    PORTIONS_OUTPUT_DIR_PATH_DICT_MAC = PORTIONS_OUTPUT_DIR_PATH_DICT
    PORTIONS_OUTPUT_DIR_PATH_DICT_WIN = PORTIONS_OUTPUT_DIR_PATH_DICT

    # Arguments: Meta-variables
    PROJECT_DIR_DEPTH = args.PROJECT_DIR_DEPTH
    DATA_REQUEST_ROOT_DIRECTORY_DEPTH = args.DATA_REQUEST_ROOT_DIRECTORY_DEPTH
    IRB_DIR_DEPTH = args.IRB_DIR_DEPTH
    IDR_DATA_REQUEST_DIR_DEPTH = args.IDR_DATA_REQUEST_DIR_DEPTH

    ROOT_DIRECTORY = args.ROOT_DIRECTORY

    LOG_LEVEL = args.LOG_LEVEL

    # Variables: Path construction: General
    runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    projectDir = Path(os.getcwd())
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

    if ROOT_DIRECTORY == "PROJECT_DIRECTORY":
        rootDirectory = projectDir
    elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
        rootDirectory = dataRequestDir
    elif ROOT_DIRECTORY == "IRB_DIRECTORY":
        rootDirectory = IRBDir
    elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
        rootDirectory = IDRDataRequestDir

    # Variables: Path construction: OS-specific
    accesibilityTestMac = [path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_DICT_MAC.values()]
    accesibilityTestWin = [path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_DICT_WIN.values()]
    isAccessibleMac = np.all(accesibilityTestMac)
    isAccessibleWin = np.all(accesibilityTestWin)
    isAccessible = isAccessibleMac or isAccessibleWin
    if isAccessible:
        # If you have access to either of the below directories, use this block.
        operatingSystem = sys.platform
        if operatingSystem == "darwin":
            portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_DICT_MAC
        elif operatingSystem == "win32":
            portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_DICT_WIN
        else:
            raise Exception("Unsupported operating system")
    else:
        # If the above option doesn't work, manually copy the database to the `input` directory.
        # portionsOutputDirPath = None
        print("Not implemented")
        sys.exit()

    # Directory creation: General
    make_dir_path(runIntermediateDataDir)
    make_dir_path(runOutputDir)
    make_dir_path(runLogsDir)
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

    main(portionsOutputDirPath)

    # End script
    logging.info(f"""Finished running "{getCommonDirectoryParent(thisFilePath, rootDirectory)}".""")
