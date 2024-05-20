#!/usr/bin/env python

"""
Get the set of IDs from a Chocolate clinical text workflow.
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
# Third-party packages
import pandas as pd
from sqlalchemy import URL
# Local packages
from drapi import __version__ as drapiVersion
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    makeDirPath)

if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--FILE_PATHS",
                        nargs="*",
                        help="The list of file paths to the tables containing IDs")
    parser.add_argument("--ID_NAMES",
                        nargs="*",
                        type=json.loads,
                        help="A JSON-formatted list of variable name (ID name) pairs to make sets of.")
    parser.add_argument("--ALIASES",
                        nargs="*",
                        type=json.loads,
                        help="""A JSON-formatted list of dictionaries, one dictionary for each `ID_NAME` pair. The dictinoaries are used to rename their corresponding name pairs. If you wish to not rename a variable, map it to the empty string like this: {"original_name": ""}.""")
    parser.add_argument("--ROOT_PATH",
                        help="The root folder for `--FILE_PATHS`")

    # Arguments: Meta-parameters
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=int,
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
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    FILE_PATHS = argNamespace.FILE_PATHS
    ID_NAMES = argNamespace.ID_NAMES
    ALIASES = argNamespace.ALIASES
    ROOT_PATH = argNamespace.ROOT_PATH

    # Parsed arguments: Meta-parameters
    LOG_LEVEL = argNamespace.LOG_LEVEL

    # Parsed arguments: SQL connection settings
    SERVER = argNamespace.SERVER
    DATABASE = argNamespace.DATABASE
    USER_DOMAIN = argNamespace.USER_DOMAIN
    USERNAME = argNamespace.USERNAME
    USER_ID = argNamespace.USER_ID
    USER_PWD = argNamespace.USER_PWD
    # <<< `Argparse` arguments <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    pass
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

    # Variables: SQL Parameters
    if USER_ID:
        userID = USER_ID[:]
    else:
        userID = fr"{USER_DOMAIN}\{USERNAME}"
    if USER_PWD:
        userPwd = USER_PWD
    else:
        userPwd = os.environ["HFA_UFADPWD"]
    connectionString = URL.create(drivername="mssql+pymssql",
                                  username=userID,
                                  password=userPwd,
                                  host=SERVER,
                                  database=DATABASE)

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

    it1Total = len(ID_NAMES)
    nameZip = zip(ID_NAMES, ALIASES)
    # modeDict = {fpath: {"mode": "a",
    #                     "header": True} for fpath in FILE_PATHS}
    for it1, tu in enumerate(nameZip, start=1):
        variableNamePair, aliasDict0 = tu
        aliasDict = {variableAlias: (variableName if variableName != "" else variableAlias) for variableAlias, variableName in aliasDict0.items()}
        logger.info(f"""  Working on variable pair {it1:,} of {it1Total:,}: "{variableNamePair}".""")
        variableNamePair = list(variableNamePair)
        it2Total = len(FILE_PATHS)
        for it2, fpath in enumerate(FILE_PATHS, start=1):
            logger.info(f"""    Working on fpath {it2:,} of {it2Total:,}: "{fpath}".""")
            fpath = Path(fpath)
            df0 = pd.read_csv(filepath_or_buffer=fpath,
                            engine="pyarrow")
            df = df0[variableNamePair].drop_duplicates()

            # Rename variables
            df = df.rename(mapper=aliasDict)

            relativePath = fpath.relative_to(ROOT_PATH)
            variableAlias, variableName = variableNamePair
            variableNameStandard = aliasDict[variableName]
            savePath = runOutputDir.joinpath("Sets",
                                             variableNameStandard,
                                             relativePath.parents[0],
                                             f"{fpath.stem}.CSV")
            savePath.parent.mkdir(parents=True)

            df.to_csv(path_or_buf=savePath,
                                index=False)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # <<< End script body <<<
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
