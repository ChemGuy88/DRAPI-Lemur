#!/usr/bin/env python

"""
A template for creating command-line scripts.
"""

import argparse
import logging
import multiprocessing as pp
import os
import pprint
import shutil
from functools import partial
from pathlib import Path
# Third-party packages
pass
# First-party packages
from drapi.code.drapi.prep_for_text_deidentification import prep_for_text_deidentification
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
from drapi.code.drapi.cli_parsers import parse_string_to_boolean
from drapi import loggingChoices
from drapi import __version__ as drapiVersion


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments
    parser.add_argument("--list_of_file_paths",
                        type=Path,
                        required=True,
                        nargs="+",
                        help="The list of file paths to convert.")
    parser.add_argument("--rename_columns",
                        type=parse_string_to_boolean)
    parser.add_argument("--columns_to_keep",
                        help="The indices or labels of columns to keep. Max 2.",
                        nargs="+")

    # Arguments: Meta-parameters
    parser.add_argument("--TIMESTAMP",
                        type=str)
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=loggingChoiceParser,
                        choices=loggingChoices,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    argNamespace = parser.parse_args()

    # Parsed arguments
    list_of_file_paths = argNamespace.list_of_file_paths
    rename_columns = argNamespace.rename_columns
    columns_to_keep = argNamespace.columns_to_keep

    # Parsed arguments: Meta-parameters
    TIMESTAMP = argNamespace.TIMESTAMP
    LOG_LEVEL = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    # >>> Custom argument parsing: Parsing 1 >>>
    pass
    # <<< Custom argument parsing: Parsing 1 <<<

    # >>> Custom argument parsing: Parsing 2 >>>
    pass
    # <<< Custom argument parsing: Parsing 2 <<<
    # <<< Custom argument parsing <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    # >>> Argument checks: Check 1 >>>
    pass
    # <<< Argument checks: Check 1 <<<
    # >>> Argument checks: Check 2 >>>
    pass
    # <<< Argument checks: Check 2 <<<
    # <<< Argument checks <<<

    # Variables: Path construction: General
    if TIMESTAMP:
        runTimestamp = TIMESTAMP
    else:
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

    if False:
        # Serial implementation
        for file_path in list_of_file_paths:
            prep_for_text_deidentification(filepath=fp_obj,
                                           output_directory=runOutputDir,
                                           logger=logger,
                                           rename_columns=rename_columns,
                                           columns_to_keep=columns_to_keep)
    elif True:
        # Parallel implementation
        with pp.Pool() as pool:
            results = pool.map(partial(prep_for_text_deidentification,
                                       output_directory=runOutputDir,
                                       logger=logger,
                                       rename_columns=rename_columns,
                                       columns_to_keep=columns_to_keep),
                               list_of_file_paths)

    # <<< End script body <<<

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # Script end confirmation
    logger.info(f"""Finished running "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")
