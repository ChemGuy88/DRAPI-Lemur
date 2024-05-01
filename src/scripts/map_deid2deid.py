"""
Create a map from one de-identified ID to another de-identified ID.
"""

import argparse
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
from drapi.code.drapi.constants.phiVariables import VARIABLE_SUFFIXES_BO
# Super-local imports
from drapi.code.drapi.getData.getData import getData


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main: Single input option: Data sources
    parser.add_argument("--LEFT_DEIDENTIFICATION_MAP_PATH",
                        type=str,
                        required=True)
    parser.add_argument("--LEFT_VARIABLE_NAME",
                        type=str,
                        required=True,
                        help="The column header for the left map.")
    parser.add_argument("--RIGHT_DEIDENTIFICATION_MAP_PATH",
                        type=str,
                        required=True)
    parser.add_argument("--RIGHT_VARIABLE_NAME",
                        type=str,
                        required=True,
                        help="The column header for the right map.")
    parser.add_argument("--SQL_FILE_PATH",
                        type=Path,
                        help="The path to the SQL file to use for creating the left-to-right map.")
    parser.add_argument("--SQL_FILE_PLACEHOLDER",
                        type=str,
                        help="The SQL file template placeholder.")
    parser.add_argument("--OUTPUT_FILE_NAME",
                        type=str,
                        required=True,
                        help="The name of the query results.")

    parser.add_argument("--FIRST_TIME",
                        action="store_true",
                        type=bool)
    parser.add_argument("--OLD_RUN_PATH",
                        type=str,
                        help="The path to the data previously downloaded from another session of this program.")

    # Arguments: Main
    parser.add_argument("SCRIPT_TEST_MODE",
                        type=lambda stringValue: True if stringValue.lower() == "true" else False if stringValue.lower() == "false" else None,
                        help=""" Choose one of {{True, False}}""")

    # Arguments: General
    parser.add_argument("--CHUNKSIZE",
                        default=50000,
                        type=int,
                        help="The number of rows to read at a time from the CSV using Pandas `chunksize`")
    parser.add_argument("--MESSAGE_MODULO_CHUNKS",
                        default=50,
                        type=int,
                        help="How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_CHUNKS`")
    parser.add_argument("--MESSAGE_MODULO_FILES",
                        default=100,
                        type=int,
                        help="How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_FILES`")

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
    DICTIONARY_OF_ARGUMENTS = argNamespace.DICTIONARY_OF_ARGUMENTS
    ARGUMENTS = argNamespace.ARGUMENTS

    LEFT_DEIDENTIFICATION_MAP_PATH = argNamespace.LEFT_DEIDENTIFICATION_MAP_PATH
    LEFT_VARIABLE_NAME = argNamespace.LEFT_VARIABLE_NAME
    RIGHT_DEIDENTIFICATION_MAP_PATH = argNamespace.RIGHT_DEIDENTIFICATION_MAP_PATH
    RIGHT_VARIABLE_NAME = argNamespace.RIGHT_VARIABLE_NAME
    SQL_FILE_PATH = argNamespace.SQL_FILE_PATH
    SQL_FILE_PLACEHOLDER = argNamespace.SQL_FILE_PLACEHOLDER
    OUTPUT_FILE_NAME = argNamespace.OUTPUT_FILE_NAME

    FIRST_TIME = argNamespace.FIRST_TIME
    OLD_RUN_PATH = argNamespace.OLD_RUN_PATH

    SCRIPT_TEST_MODE = argNamespace.SCRIPT_TEST_MODE

    # Parsed arguments: General
    CHUNKSIZE = argNamespace.CHUNKSIZE
    MESSAGE_MODULO_CHUNKS = argNamespace.MESSAGE_MODULO_CHUNKS
    MESSAGE_MODULO_FILES = argNamespace.MESSAGE_MODULO_FILES

    # Parsed arguments: Meta-parameters
    PROJECT_DIR_DEPTH = argNamespace.PROJECT_DIR_DEPTH
    DATA_REQUEST_DIR_DEPTH = argNamespace.DATA_REQUEST_DIR_DEPTH
    IRB_DIR_DEPTH = argNamespace.IRB_DIR_DEPTH
    IDR_DATA_REQUEST_DIR_DEPTH = argNamespace.IDR_DATA_REQUEST_DIR_DEPTH

    ROOT_DIRECTORY = argNamespace.ROOT_DIRECTORY
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
    if FIRST_TIME and OLD_RUN_PATH:
        message = "It is ambiguous if you provide both `FIRST_TIME` and `OLD_RUN_PATH`. Please only choose one."
        parser.error(message=message)

    if isinstance(SCRIPT_TEST_MODE, bool):
        pass
    else:
        message = """`SCRIPT_TEST_MODE` Must be one of "True" or "False"."""
        parser.error(message=message)

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
    conStr = f"mssql+pymssql://{userID}:{userPwd}@{SERVER}/{DATABASE}"

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

    # >>> Begin module body >>>

    # Map 1: Left de-identification map
    leftdf = pd.read_csv(LEFT_DEIDENTIFICATION_MAP_PATH)

    # Map 2: Left-to-right map
    if FIRST_TIME:
        left2rightMapDir = runOutputDir.joinpath("Left-to-right Map")
        left2rightMapDir.mkdir()
        connectionString = URL.create(drivername="mssql+pymssql",
                                      username=userID,
                                      password=userPwd,
                                      host=SERVER,
                                      database=DATABASE)

        getData(sqlFilePath=SQL_FILE_PATH,
                connectionString=connectionString,
                filterVariableChunkSize=10000,
                filterVariableColumnName=LEFT_VARIABLE_NAME,
                filterVariableData=leftdf,
                filterVariableFilePath=None,
                filterVariablePythonDataType="int",
                filterVariableSqlQueryTemplatePlaceholder=SQL_FILE_PLACEHOLDER,
                logger=logger,
                outputFileName=OUTPUT_FILE_NAME,
                runOutputDir=left2rightMapDir,
                queryChunkSize=10000)
    else:
        left2rightMapDir = Path(OLD_RUN_PATH)

    # Join maps: Concatenate left-to-right map
    listofPaths = sorted([fpath for fpath in left2rightMapDir.iterdir() if fpath.suffix.lower() == ".csv"])
    left2rightdf = pd.DataFrame()
    itTotal = len(listofPaths)
    for it, fpath in enumerate(listofPaths, start=1):
        logger.info(f"""  Working on file {it:,} of {itTotal}.""")
        df = pd.read_csv(fpath)
        left2rightdf = pd.concat([left2rightdf, df])
    del df

    # Map 3: Right de-identification map
    rightdf = pd.read_csv(RIGHT_DEIDENTIFICATION_MAP_PATH)

    # Join maps: Homogenize variable names
    pass

    # Join maps
    joinedMaps = leftdf.set_index(LEFT_VARIABLE_NAME).join(other=left2rightdf.set_index(LEFT_VARIABLE_NAME),
                                                        how="outer")
    joinedMaps = joinedMaps.reset_index()
    joinedMaps = joinedMaps.set_index(RIGHT_VARIABLE_NAME).join(other=rightdf.set_index(RIGHT_VARIABLE_NAME),
                                                  how="outer")
    joinedMaps = joinedMaps.reset_index()

    # Select data to output
    COLUMNS_TO_EXPORT = [f"De-identified {LEFT_VARIABLE_NAME}",
                         f"De-identififed {RIGHT_VARIABLE_NAME}"]
    finalMap = joinedMaps[COLUMNS_TO_EXPORT]
    finalMap = finalMap.sort_values(by=COLUMNS_TO_EXPORT)
    exportPath = runOutputDir.joinpath(f"{LEFT_VARIABLE_NAME} to {RIGHT_VARIABLE_NAME}.CSV")
    finalMap.to_csv(exportPath, index=False)

    # QA
    mapSize = finalMap.dropna().shape[0]
    logger.info(f"""Final map shape after dropping any NAs: {mapSize:,}.""")

    # Output location summary
    logger.info(f"""Results are in "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}.""")

    # End module body
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
