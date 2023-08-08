"""
Convert person ID column to patient key

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import argparse
import logging
import os
import sys
from pathlib import Path
# Third-party packages
import numpy as np
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, make_dir_path, successiveParents
from drapi.idealist.idealist import idealistMap2dict
from .common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN

# Arguments
COLUMNS_TO_CONVERT_DI = {"person_id": "PatientKey"}

MAC_PATHS = [OMOP_PORTION_DIR_MAC]
WIN_PATHS = [OMOP_PORTION_DIR_WIN]

NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA]

PERSON_ID_MAP_PATH = Path("data/output/makePersonIDMap/.../person_id map.csv")  # TODO

CHUNK_SIZE = 50000


if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--LOG_LEVEL",
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""", type=int, default=10)

    parser.add_argument("--COLUMNS_TO_CONVERT",
                        help="""The list of of column names to convert.""", type=list, default=["person_id"])

    parser.add_argument("--MAC_PATHS",
                        help="""The directory path of the OMOP portion as a macOS path.""",
                        type=list, default=[OMOP_PORTION_DIR_MAC])
    parser.add_argument("--WIN_PATHS",
                        help="""The directory path of the OMOP portion as a windows path.""",
                        type=list, default=[OMOP_PORTION_DIR_WIN])

    parser.add_argument("--LIST_OF_PORTION_CONDITIONS",
                        help="""Command-line option not implemented. Leave blank to use the default value.""",
                        type=list,
                        default=OMOP_PORTION_FILE_CRITERIA)
    
    parser.add_argument("--COLUMNS_TO_CONVERT_MAP_PATH",
                        help=""".""",
                        type=json.loads,
                        default="""{"person_id": "PatientKey"}""")

    parser.add_argument("--READ_CSV_CHUNK_SIZE",
                        help="""The chunk size for when reading CSV files.""", type=int, default=50000)

    parser.add_argument("--PROJECT_DIR_DEPTH",
                        help="""The depth, or number of directories, from the present working directory to this file. The suite of concatenation and de-identification scripts is considered to be the "project".""",
                        type=int,
                        default=0)

    parser.add_argument("--DATA_REQUEST_ROOT_DIRECTORY_DEPTH",
                        help="""The depth, or number of directories, from the present working directory to the data request folder. Typically the data request folder is the same as the IRB folder, or it may be a subfolder.""",
                        type=int,
                        default=DATA_REQUEST_ROOT_DIRECTORY_DEPTH)

    parser.add_argument("IRB_DIR_DEPTH",
                        help="The depth, or number of directories, from the present working directory to the data request's IRB, or equivalent, folder.",
                        type=int,
                        default=2)

    parser.add_argument("IDR_DATA_REQUEST_DIR_DEPTH",
                        help="The depth, or number of directories, from the present working directory the IDR Data Request folder on the shared drive.",
                        type=int,
                        default=4)

    parser.add_argument("ROOT_DIRECTORY",
                        help="""The directory to be used as the point of reference for relative paths when displaying log messages.""",
                        choices=["IDR_DATA_REQUEST_DIRECTORY", "IRB_DIRECTORY", "DATA_REQUEST_DIRECTORY", "PROJECT_DIRECTORY"],
                        type=str)

    # Parse arguments
    args = parser.parse_args()

    # Arguments
    COLUMNS_TO_CONVERT_DI = args.COLUMNS_TO_CONVERT_DI

    MAC_PATHS = args.MAC_PATHS
    WIN_PATHS = args.WIN_PATHS

    LIST_OF_PORTION_CONDITIONS = args.LIST_OF_PORTION_CONDITIONS

    COLUMNS_TO_CONVERT_MAP_PATH = args.COLUMNS_TO_CONVERT_MAP_PATH

    CHUNK_SIZE = args.READ_CSV_CHUNK_SIZE

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

    # Directory creation: General
    make_dir_path(runIntermediateDataDir)
    make_dir_path(runOutputDir)
    make_dir_path(runLogsDir)

    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    logFormat = logging.Formatter("""[%(asctime)s][%(levelname)s](%(funcName)s)%(message)s""")

    logger = logging.getLogger(__name__)

    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(LOG_LEVEL)
    fileHandler.setFormatter(logFormat)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)
    streamHandler.setFormatter(logFormat)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    logger.setLevel(LOG_LEVEL)

    # Variables: Path construction: OS-specific
    accesibilityTestMac = [path.exists() for path in MAC_PATHS]
    accesibilityTestWin = [path.exists() for path in WIN_PATHS]
    isAccessibleMac = np.all(accesibilityTestMac)
    isAccessibleWin = np.all(accesibilityTestWin)
    isAccessible = isAccessibleMac or isAccessibleWin
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
        # portionsOutputDirPath = None
        logger.critical("Not implemented")
        sys.exit()

    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
