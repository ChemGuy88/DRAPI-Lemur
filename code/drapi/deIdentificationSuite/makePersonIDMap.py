"""
Convert OMOP person IDs to IDR patient keys.

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
from pandas.errors import EmptyDataError
# Local packages
from drapi.drapi import getTimestamp, make_dir_path, personIDs2patientKeys, successiveParents
from .common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, OMOP_PORTION_FILE_CRITERIA


def makePersonIDMap(SETS_PATH, listOfPortionDirs, COLUMNS_TO_CONVERT, LIST_OF_PORTION_CONDITIONS, CHUNK_SIZE):
    # Get set of values
    if SETS_PATH:
        logger.info(f"""Using the set of values previously collected from "{SETS_PATH}".""")
    else:
        logger.info("""Getting the set of values for each variable to convert.""")
        columnSetsVarsDi = {columnName: {"fpath": runIntermediateDataDir.joinpath(f"{columnName}.txt"),
                                         "fileMode": "w"} for columnName in COLUMNS_TO_CONVERT}
        for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
            # Act on directory
            logger.info(f"""Working on directory "{directory.relative_to(IRBDir)}".""")
            for file in directory.iterdir():
                logger.info(f"""  Working on file "{file.absolute().relative_to(IRBDir)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logger.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logger.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_CONVERT:
                                logger.info("""  ..  ..  Column must be converted. Collecting values.""")
                                valuesSet = sorted(list(set(dfChunk[columnName].dropna().values)))
                                columnSetFpath = columnSetsVarsDi[columnName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[columnName]["fileMode"]
                                with open(columnSetFpath, columnSetFileMode) as file:
                                    for value in valuesSet:
                                        file.write(str(value))
                                        file.write("\n")
                                columnSetsVarsDi[columnName]["fileMode"] = "a"
                                logger.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(IRBDir)}" in the project directory.""")
                else:
                    logger.info("""    This file does not need to be processed.""")

    # Map values
    if SETS_PATH:
        setsPathDir = SETS_PATH
    else:
        setsPathDir = runIntermediateDataDir
    for file in setsPathDir.iterdir():
        columnName = file.stem
        logger.info(f"""  Working on variable "{columnName}" located at "{file.absolute().relative_to(IRBDir)}".""")
        # Read file
        try:
            df = pd.read_table(file, header=None)
        except EmptyDataError as err:
            _ = err
            df = pd.DataFrame()
        # Assert
        if df.shape[1] == 1:
            # Try to convert to integer-type
            try:
                df.iloc[:, 0] = df.iloc[:, 0].astype(int)
            except ValueError as err:
                _ = err
            # Check length differences
            len0 = len(df)
            values = set(df.iloc[:, 0].values)
            len1 = len(values)
            logger.info(f"""    The length of the ID array was reduced from {len0:,} to {len1:,} when removing duplicates.""")
        elif df.shape[1] == 0:
            pass
        # Map contents
        map_ = personIDs2patientKeys(list(values))
        # Save map
        mapPath = runOutputDir.joinpath(f"{columnName} map.csv")
        map_.to_csv(mapPath, index=False)
        logger.info(f"""    PersonID-to-PatientKey map saved to "{mapPath.absolute().relative_to(IRBDir)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory


if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--LOG_LEVEL",
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""", type=int, default=10)

    parser.add_argument("--COLUMNS_TO_CONVERT",
                        help="""The list of of column names to convert.""", type=list, default=["person_id"])

    parser.add_argument("--MAC_PATHS",
                        help="""The directory path of the OMOP portion as a macOS path.""", type=list, default=[OMOP_PORTION_DIR_MAC])
    parser.add_argument("--WIN_PATHS",
                        help="""The directory path of the OMOP portion as a windows path.""", type=list, default=[OMOP_PORTION_DIR_WIN])

    parser.add_argument("--LIST_OF_PORTION_CONDITIONS",
                        help="""Command-line option not implemented. Leave blank to use the default value.""",
                        type=list,
                        default=OMOP_PORTION_FILE_CRITERIA)

    parser.add_argument("--SETS_PATH",
                        help="""The path, if any, where the variables sets are located.""", type=str, default=None)

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
    COLUMNS_TO_CONVERT = args.COLUMNS_TO_CONVERT

    MAC_PATHS = args.OMOP_PORTION_DIR_MAC
    WIN_PATHS = args.OMOP_PORTION_DIR_WIN

    LIST_OF_PORTION_CONDITIONS = args.OMOP_PORTION_FILE_CRITERIA

    SETS_PATH = args.SETS_PATH

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

    makePersonIDMap(SETS_PATH, listOfPortionDirs, COLUMNS_TO_CONVERT, LIST_OF_PORTION_CONDITIONS, CHUNK_SIZE)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(IRBDir)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
