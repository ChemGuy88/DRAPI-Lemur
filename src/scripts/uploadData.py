#!/usr/bin/env python

"""
Uploads a pandas-compatible file to a SQL server
"""

import argparse
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
pass
# First-party packages
from drapi import __version__ as drapiVersion
from drapi import loggingChoices
from drapi.code.drapi.classes import (SecretString)
from drapi.code.drapi.cli_parsers import parse_string_to_boolean
from drapi.code.drapi.uploadData import uploadData
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
from drapi.code.drapi.uploadData import uploadData


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments
    parser.add_argument("--directory_or_list_of_paths",
                        required=True,
                        nargs="+")
    parser.add_argument("--schema_name",
                        required=True,
                        type=str)
    parser.add_argument("--table_name",
                        required=True,
                        type=str)
    parser.add_argument("--connection_string",
                        type=SecretString)
    parser.add_argument("--lazy_hack_1",
                        default=False,
                        type=parse_string_to_boolean)

    # Arguments: Meta-parameters
    parser.add_argument("--TIMESTAMP",
                        type=str)
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=loggingChoiceParser,
                        choices=loggingChoices,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    # Arguments: SQL connection settings
    parser.add_argument("--SERVER",
                        default="DWSRSRCH01.shands.ufl.edu",
                        type=str,
                        choices=["Acuo03.shands.ufl.edu",
                                 "EDW.shands.ufl.edu",
                                 "DWSRSRCH01.shands.ufl.edu",
                                 "IDR01.shands.ufl.edu",
                                 "RDW.shands.ufl.edu"],
                        help="")
    parser.add_argument("--DATABASE",
                        default="DWS_PROD",
                        type=str,
                        choices=["DWS_NOTES",
                                 "DWS_OMOP_PROD",
                                 "DWS_OMOP",
                                 "DWS_PROD"],  # TODO Add the i2b2 databases... or all the other databases?
                        help="")
    parser.add_argument("--USER_DOMAIN",
                        default="UFAD",
                        type=str,
                        choices=["UFAD"],
                        help="")
    parser.add_argument("--USERNAME",
                        default=os.environ["USER"],
                        type=str,
                        help="")
    parser.add_argument("--USER_ID",
                        default=None,
                        help="")
    parser.add_argument("--USER_PWD",
                        default=None,
                        type=SecretString,
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments
    directory_or_list_of_paths = argNamespace.directory_or_list_of_paths
    schema_name = argNamespace.schema_name
    table_name = argNamespace.table_name
    connection_string = argNamespace.connection_string
    lazy_hack_1 = argNamespace.lazy_hack_1

    # Parsed arguments: Meta-parameters
    TIMESTAMP = argNamespace.TIMESTAMP
    LOG_LEVEL = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    # >>> Custom argument parsing: determine if input is a directory or list of file paths >>>
    # Case 1: One directory
    # Case 2: One or more files
    # Case 3: All other cases
    arguments_as_files = [Path(el).is_file() for el in directory_or_list_of_paths]
    arguments_as_dirs = [Path(el).is_dir() for el in directory_or_list_of_paths]
    if len(arguments_as_dirs) ==1 and all(arguments_as_dirs):
        # case 1
        directory_path = directory_or_list_of_paths[0]
        list_of_paths = sorted(list([file_path for file_path in Path(directory_path).iterdir()]))
    elif all(arguments_as_files):
        # case 2
        list_of_paths = sorted([Path(file_path) for file_path in directory_or_list_of_paths])
    else:
        raise Exception(f"""`directory_or_list_of_paths` should be a single directory or a list of file paths.""")
    # <<< Custom argument parsing: determine if input is a directory or list of file paths <<<
    # <<< Custom argument parsing <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    # >>> Argument checks: Check booleans >>>
    if isinstance(lazy_hack_1, type(None)):
        parser.error("`lazy_hack_1` must be one of {{True, False}}.")
    # <<< Argument checks: Check booleans <<<
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

    # Begin module body

    _ = uploadData(list_of_paths=list_of_paths,
                   schema_name=schema_name,
                   table_name=table_name,
                   connection_string=connection_string,
                   lazy_hack_1=lazy_hack_1,
                   logger=logger)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # End module body
    logger.info(f"""Finished running "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")
