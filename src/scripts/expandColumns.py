"""
Split a column into multiple columns from a pre-existing table.
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
# Third-party packages
import pandas as pd
import pathos.pools as pp
# First-party packages
from drapi import __version__ as drapiVersion
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    makeDirPath)
from drapi.code.drapi.expandColumn import expandColumnWrapper

# Functions


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--PATHS",
                        nargs="+",
                        required=True,
                        help="The path to the file where the table is located. Usually a CSV or TSV file.")
    parser.add_argument("--COLUMN_TO_SPLIT",
                        required=True,
                        help="The label of the column to split.")
    parser.add_argument("--NAME_OF_NEW_COLUMNS",
                        nargs="+",
                        required=True,
                        help="A list of column names to give to the new columns.")
    parser.add_argument("--LOCATION_OF_NEW_COLUMNS",
                        nargs="+",
                        type=int,
                        required=True,
                        help="A list of index locations of the new columns.")
    parser.add_argument("--SPLITTING_PATTERN",
                        required=True,
                        help="The regular expression pattern to use to split the column.")
    parser.add_argument("--SEPARATOR",
                        default="\t",
                        type=str,
                        help="The separator.")

    # Arguments: Meta-parameters
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=int,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    PATHS = argNamespace.PATHS
    COLUMN_TO_SPLIT = argNamespace.COLUMN_TO_SPLIT
    NAME_OF_NEW_COLUMNS = argNamespace.NAME_OF_NEW_COLUMNS
    LOCATION_OF_NEW_COLUMNS = argNamespace.LOCATION_OF_NEW_COLUMNS
    SPLITTING_PATTERN = argNamespace.SPLITTING_PATTERN

    SEPARATOR = argNamespace.SEPARATOR

    # Parsed arguments: Meta-parameters
    LOG_LEVEL = argNamespace.LOG_LEVEL

    # Variables: Path construction: General
    runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    currentWorkingDir = Path(os.getcwd()).absolute()
    projectDir = currentWorkingDir
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

    # Variables: Path construction: Project-specific
    pass

    # Variables: Other
    pass

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

    logger.info(f"""Begin running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
    logger.info(f"""DRAPI-Lemur version is "{drapiVersion}".""")
    logger.info(f"""All other paths will be reported in debugging relative to the current working directory: "{choosePathToLog(path=projectDir, rootPath=projectDir)}".""")

    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)  # TODO Remove secrets from list to print, e.g., passwords.
    logger.info(f"""Script arguments:\n{argListString}""")

    # Begin module body
    PARGS = []
    li = sorted(PATHS)
    for fpathString in li:
        fpath = Path(fpathString)
        runOutputPath = runOutputDir.joinpath(fpath.name)
        argsClone = (runOutputPath,
                     fpath,
                     COLUMN_TO_SPLIT,
                     NAME_OF_NEW_COLUMNS,
                     LOCATION_OF_NEW_COLUMNS,
                     SPLITTING_PATTERN,
                     logger,
                     SEPARATOR)
        PARGS.append(argsClone)

    with pp._ProcessPool() as pool:
        results = pool.starmap(expandColumnWrapper, PARGS)

    logger.info(f"""Results are in "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}.""")

    # End module body
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
