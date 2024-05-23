"""
Joins two local tables
"""

import argparse
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi import __version__ as drapiVersion
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    makeDirPath)

if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--LEFT_TABLE",
                        type=Path,
                        help="The path to the left table to join.",
                        required=True)
    parser.add_argument("--RIGHT_TABLE",
                        help="The path to the right table to join.",
                        required=True)

    parser.add_argument("--LEFT_TABLE_INDEX",
                        default=None,
                        type=str,
                        help="The column to use as index to join on for the left table.")
    parser.add_argument("--RIGHT_TABLE_INDEX",
                        default=None,
                        type=str,
                        help="The column to use as index to join on for the right table.")
    
    if False:
        parser.add_argument("--COLUMNS_TO_JOIN_ON",
                            nargs="+",
                            required=True)

    parser.add_argument("--HOW",
                        type=str,
                        choices=["inner","outer","left","right"],
                        help="The method to join on.")

    parser.add_argument("--COLUMNS_TO_KEEP",
                        default=[],
                        nargs="*",
                        help="The columns to keep. By default, all are kept.")
    parser.add_argument("--COLUMNS_TO_DROP",
                        default=[],
                        nargs="*",
                        help="The columns to drop. By defautl, all are kept")
    
    parser.add_argument("--FILE_EXTENSION",
                        default=".CSV",
                        type=str,
                        help="The file extension to use for the output.")

    # Arguments: Meta-parameters
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=int,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    LEFT_TABLE = argNamespace.LEFT_TABLE
    RIGHT_TABLE = argNamespace.RIGHT_TABLE

    LEFT_TABLE_INDEX = argNamespace.LEFT_TABLE_INDEX
    RIGHT_TABLE_INDEX = argNamespace.RIGHT_TABLE_INDEX

    if False:
        COLUMNS_TO_JOIN_ON = argNamespace.COLUMNS_TO_JOIN_ON

    HOW = argNamespace.HOW

    COLUMNS_TO_KEEP = argNamespace.COLUMNS_TO_KEEP
    COLUMNS_TO_DROP = argNamespace.COLUMNS_TO_DROP

    FILE_EXTENSION = argNamespace.FILE_EXTENSION
    FILE_EXTENSION = str(FILE_EXTENSION)  # For type hinting

    # Parsed arguments: Meta-parameters
    LOG_LEVEL = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    pass

    # Check columns to join on
    if False:
        if len(COLUMNS_TO_JOIN_ON) == 1:
            columnsToJoinOn = COLUMNS_TO_JOIN_ON[0]
        elif len(COLUMNS_TO_JOIN_ON) >= 1:
            columnsToJoinOn = COLUMNS_TO_JOIN_ON
        else:
            message = f"""You can only supply either one or two columns to join on."""
            parser.error(message)

    # Check columns to drop and keep
    intersection = set(COLUMNS_TO_DROP).intersection(set(COLUMNS_TO_KEEP))
    if len(intersection) > 0:
        intersectionAsString = ", ".join(sorted(list(intersection)))
        message = f"""The following column names were in both the list of columns to drop and keep: {intersectionAsString}"""
        parser.error(message)
    # <<< Argument checks <<<

    # Variables: Path construction: General
    runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    currentWorkingDir = Path(os.getcwd()).absolute()
    projectDir = currentWorkingDir
    dataDir = projectDir.joinpath("data")
    if dataDir:
        inputDataDir = dataDir.joinpath("input")
        intermediateDataDir = dataDir.joinpath("intermediate")
        outputDataDir = dataDir.joinpath("output")
        if intermediateDataDir:
            runIntermediateDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
        if outputDataDir:
            runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
    logsDir = projectDir.joinpath("logs")
    if logsDir:
        runLogsDir = logsDir.joinpath(thisFileStem)
    sqlDir = projectDir.joinpath("sql")

    # Variables: Path construction: Project-specific
    pass

    # Variables: Other
    pass

    # Directory creation: General
    makeDirPath(runIntermediateDir)
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

    logger.info(f"""Begin running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
    logger.info(f"""DRAPI-Lemur version is "{drapiVersion}".""")
    logger.info(f"""All other paths will be reported in debugging relative to the current working directory: "{choosePathToLog(path=projectDir, rootPath=projectDir)}".""")

    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)  # TODO Remove secrets from list to print, e.g., passwords.
    logger.info(f"""Script arguments:\n{argListString}""")

    # >>> Begin script body >>>

    # Load tables
    leftTable = pd.read_csv(LEFT_TABLE, engine="pyarrow")
    rightTable = pd.read_csv(RIGHT_TABLE, engine="pyarrow")

    # Set indices
    indexCounter = 0
    if LEFT_TABLE_INDEX:
        leftTable = leftTable.set_index(LEFT_TABLE_INDEX)
        indexCounter += 1
    
    if RIGHT_TABLE_INDEX:
        rightTable = rightTable.set_index(RIGHT_TABLE_INDEX)
        indexCounter += 1

    joinedTable = leftTable.join(other=rightTable,
                                 how=HOW,
                                 lsuffix="_L",
                                 rsuffix="_R")
    
    # Reset indices with names
    if LEFT_TABLE_INDEX and RIGHT_TABLE_INDEX:
        joinedTable = joinedTable.reset_index(names=LEFT_TABLE_INDEX)
    elif LEFT_TABLE_INDEX:
        joinedTable = joinedTable.reset_index(names=LEFT_TABLE_INDEX)
    elif RIGHT_TABLE_INDEX:
        joinedTable = joinedTable.reset_index(names=RIGHT_TABLE_INDEX)

    
    # Select columns
    columns0 = joinedTable.columns

    # Seelct columns: Columns to drop
    finalColumns = columns0.drop(labels=COLUMNS_TO_DROP)

    # Select columns: Columns to 
    if COLUMNS_TO_KEEP:
        finalColumns = finalColumns[finalColumns.isin(COLUMNS_TO_KEEP)]

    # Select columns: final columns
    finalTable = joinedTable[finalColumns]

    # Make export path
    if FILE_EXTENSION:
        if FILE_EXTENSION.startswith("."):
            fileExtension = FILE_EXTENSION
        else:
            fileExtension = f".{FILE_EXTENSION}"
    else:
        fileExtension = ""
    exportPath = runOutputDir.joinpath(f"""Joined Table{fileExtension}""")
    
    # Save results
    finalTable.to_csv(path_or_buf=exportPath,
                      index=False)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files
    logger.info("Removing intermediate files.")
    shutil.rmtree(runIntermediateDir)
    logger.info("Removing intermediate files - done.")

    # <<< End script body <<<
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
