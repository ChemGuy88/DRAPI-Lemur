#!/usr/bin/env python

"""
Gather files.
"""

import argparse
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
# First-party packages
from drapi import __version__ as drapiVersion
from drapi import loggingChoices
from drapi.code.drapi.cli_parsers import parse_string_to_boolean
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
from drapi.code.drapi.gather_files import gather_files


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Required
    parser.add_argument("--destination_folder",
                        required=True,
                        type=Path)

    # Arguments: Add mutually exclusive groups
    group = parser.add_mutually_exclusive_group(required=True)
    # Arguments: Add mutually exclusive groups: Group 1
    group.add_argument("--list_of_directories",
                        type=Path,
                        nargs="+")

    # Arguments: Add mutually exclusive groups: Group 2  # NOTE TODO Not implemented yet
    group.add_argument("--list_of_files",
                        type=Path,
                        action="append",
                        nargs="+")

    # Arguments: Options
    parser.add_argument("--list_of_directories_new_names",
                        type=str,
                        nargs="*")
    parser.add_argument("--list_of_loose_files",
                        type=Path,
                        nargs="*",
                        help="These are files that are gathered in the root directory, and do not require a directory or portion name.")

    parser.add_argument("--overwrite_if_exists_archive",
                        type=parse_string_to_boolean)
    parser.add_argument("--overwrite_if_exists_folder",
                        type=parse_string_to_boolean)
    parser.add_argument("--overwrite_if_exists_file",
                        type=parse_string_to_boolean)

    parser.add_argument("--create_merged_folder",
                        type=parse_string_to_boolean)
    parser.add_argument("--create_compressed_archive",
                        type=parse_string_to_boolean)
    parser.add_argument("--delete_folder_after_archiving",
                        type=parse_string_to_boolean)

    # Arguments: Meta-parameters
    parser.add_argument("--TIMESTAMP",
                        type=str)
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=loggingChoiceParser,
                        choices=loggingChoices,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    argNamespace = parser.parse_args()

    # Parsed arguments: Required
    destination_folder = argNamespace.destination_folder

    # Parsed arguments: Mode 1
    list_of_files = argNamespace.list_of_files

    # Parsed arguments: Mode 2
    list_of_directories = argNamespace.list_of_directories

    # Parsed arguments: Optional arguments
    list_of_directories_new_names = argNamespace.list_of_directories_new_names
    list_of_loose_files = argNamespace.list_of_loose_files
    overwrite_if_exists_folder = argNamespace.overwrite_if_exists_folder
    overwrite_if_exists_file = argNamespace.overwrite_if_exists_file
    create_merged_folder = argNamespace.create_merged_folder
    create_compressed_archive = argNamespace.create_compressed_archive
    delete_folder_after_archiving = argNamespace.delete_folder_after_archiving

    # Parsed arguments: Meta-parameters
    TIMESTAMP = argNamespace.TIMESTAMP
    LOG_LEVEL = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    # >>> Custom argument parsing: Parsing 1 >>>
    if list_of_files:
        parser.error("Not implemented. Please do not use this option.")
    else:
        list_of_files = "Not implemented."
        argNamespace.list_of_files = "Not implemented."
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

    gather_files_parameters = ["destination_folder",
                               "list_of_files",
                               "list_of_directories",
                               "list_of_directories_new_names",
                               "list_of_loose_files",
                               "timestamp",
                               "overwrite_if_exists_archive",
                               "overwrite_if_exists_file",
                               "overwrite_if_exists_folder",
                               "create_merged_folder",
                               "create_compressed_archive",
                               "delete_folder_after_archiving",
                               "logger"]
    gather_files_kwargs = {}
    for argTuple in argList:
        keyword, value = argTuple
        condition_1 = keyword in gather_files_parameters
        condition_2 = not isinstance(value, type(None))
        if condition_1 and condition_2:
            gather_files_kwargs[keyword] = value
    gather_files_kwargs["logger"] = logger

    logger.info(f""" >>> Keyword arguments passed to `gather_files` >>>
{pprint.pformat(gather_files_kwargs)}
 <<< Keyword arguments passed to `gather_files` <<<""")

    gather_files(**gather_files_kwargs)

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
