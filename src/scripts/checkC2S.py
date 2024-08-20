#!/usr/bin/env python

"""
A template for creating command-line scripts.
"""

import argparse
import logging
import os
import multiprocessing as mp
import pandas as pd
import pprint
import shutil
from functools import partial
from pathlib import Path
from typing_extensions import List

# Third-party packages
pass
# First-party packages
from drapi import __version__ as drapiVersion
from drapi import PATH as drapiPath
from drapi import loggingChoices
from drapi.code.drapi.classes import (SecretString)
from drapi.code.drapi.cli_parsers import parse_string_to_boolean
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)

from drapi.code.drapi.c2s.c2s import C2Share_query

if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments
    parser.add_argument("--sql_path",
                        type=Path,
                        default=drapiPath.joinpath('../../../DRAPI-Lemur/src/drapi/sql/C2ShareAndDeathCheck.sql'), 
                        help="The path to the Consent to Share sql query"
                        )

    parser.add_argument("--MRNs_path",
                        type=Path,
                        required=True
                        )

    parser.add_argument("--facility",
                        choices=['UF','JAX'],
                        required=True
                                    )
    parser.add_argument("--MRNs_column_name",
                        type=str,
                        required=True
                        )

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
                        help="")
    parser.add_argument("--USER_PWD",
                        default=os.environ["TopSecret"],
                        type=SecretString,
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments
    sql_path: Path = argNamespace.sql_path
    facility: str = argNamespace.facility
    MRNs_path: Path = argNamespace.MRNs_path
    MRNs_column_name: str = argNamespace.MRNs_column_name

    # Parsed arguments: SQL connections
    SERVER: str = argNamespace.SERVER
    DATABASE: str = argNamespace.DATABASE
    USER_DOMAIN: str = argNamespace.USER_DOMAIN
    USERNAME: str = argNamespace.USERNAME
    USER_ID: str = argNamespace.USER_ID
    USER_PWD: str = argNamespace.USER_PWD

    # Parsed arguments: Meta-parameters
    TIMESTAMP: str = argNamespace.TIMESTAMP
    LOG_LEVEL: str = argNamespace.LOG_LEVEL
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
    if facility=='UF':
        facilityid=101
    elif facility == 'JAX':
        facilityid = 110
    else:
        raise Exception("Invalid Facility")
    # Variables: Other
    pass

    # Variables: SQL Parameters
    if USER_ID:
        uid = USER_ID[:]
    else:
        uid = fr"{USER_DOMAIN}\{USERNAME}"
    conStr = f"mssql+pymssql://{uid}:"+USER_PWD+f"@{SERVER}/{DATABASE}"
    

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
    table = pd.read_csv(filepath_or_buffer=MRNs_path)
    
    MRNs=','.join([f'{MRN}' for MRN in table[MRNs_column_name]])
    C2Share_SQLStatement = C2Share_query(sqlpath=sql_path,
                                         facility=facilityid,
                                         MRNs=MRNs,
                                         logger=logger)
   
    result=pd.read_sql(sql=C2Share_SQLStatement,
                       con=conStr)
    print(result)
    result.to_csv(runOutputDir.joinpath('result.csv'))
    # <<< End script body <<<

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # Script end confirmation
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
