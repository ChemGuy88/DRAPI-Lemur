"""
Script template to download data using SQL queries.
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
from typing import Union
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
# Super-local imports
from getData_inner import getData_inner
from getData_outer import getData_outer

# Functions


def getData(sqlFilePath: Union[Path, str],
            connectionString: str,
            filterVariableColumnName: str,
            filterVariableData: Union[pd.DataFrame, pd.Series],
            filterVariableFilePath: Union[Path, str],
            filterVariablePythonDataType: type,
            filterVariableSqlQueryTemplatePlaceholder: str,
            logger: logging.Logger,
            outputFileName: str,
            runOutputDir: Union[Path, str],
            queryChunkSize: int = 10000,
            filterVariableChunkSize: int = 1000):
    """
    Efficiently download data based on a SQL query. Can filter query by one variable.
    """
    # >>> Determine if we're filtering >>>
    # Case 1: We have both `filterVariableFilePath` and `filterVariableColumnName` defined
    # Case 2: We have `filterVariableData` defined.
    # Case 3: Neither case 1 nor case 2
    # Determine if we're filtering: Determine filter type
    # Determine if we're filtering: Determine filter type: Case 1
    if isinstance(filterVariableFilePath, (str, Path)) and isinstance(filterVariableColumnName, (str, int)):
        useFilteringCase1 = True
    else:
        useFilteringCase1 = False
    # Determine if we're filtering: Determine filter type: Case 2
    if isinstance(filterVariableData, (pd.Series, pd.DataFrame)):
        useFilteringCase2 = True
    else:
        useFilteringCase2 = False
    # Determine if we're filtering: Determine filter type: Ambiguous case: case 1 and 2
    if useFilteringCase1 and useFilteringCase2:
        message = "Ambiguous argument input. If you want to filter your query by a variable, you must either (1) pass the variable as a Pandas Series or DataFrame or (2) pass the (2.a) path to the file that contains the data and the (2.b.) column name of the variable."
        logger.fatal(message)
        raise Exception(message)
    # Determine if we're filtering: Make decision
    if useFilteringCase1:
        useFiltering = True
    elif useFilteringCase2:
        useFiltering = True
    elif (not useFilteringCase1) and (not useFilteringCase2):
        useFiltering = False
    else:
        message = "An unexpected error occurred."
        logger.fatal(message)
        raise Exception(message)
    # <<< Determine if we're filtering <<<

    # Choose core function
    if not useFiltering:
        getData_inner(conStr=connectionString,
                      logger=logger,
                      outputName=outputFileName,
                      queryChunkSize=queryChunkSize,
                      runOutputDir=runOutputDir,
                      sqlQuery=None,
                      itstring1=None,
                      numChunks1=None,
                      sqlFilePath=sqlFilePath)
    elif useFiltering:
        getData_outer(conStr=connectionString,
                      filterVariableColumnName=filterVariableColumnName,
                      filterVariableChunkSize=filterVariableChunkSize,
                      filterVariableData=filterVariableData,
                      filterVariableFilePath=filterVariableFilePath,
                      filterVariablePythonDataType=filterVariablePythonDataType,
                      filterVariableSqlQueryTemplatePlaceholder=filterVariableSqlQueryTemplatePlaceholder,
                      logger=logger,
                      outputName=outputFileName,
                      queryChunkSize=queryChunkSize,
                      runOutputDir=runOutputDir,
                      sqlFilePath=sqlFilePath)
    else:
        message = "An unexpected error occurred."
        logger.fatal(message)
        raise Exception(message)
    return


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main: Multiple query option
    parser.add_argument("--DICTIONARY_OF_ARGUMENTS",
                        type=json.loads)

    # Arguments: Main: Single query option
    parser.add_argument("--CONNECTION_STRING")
    parser.add_argument("--SQL_FILE_PATH",
                        type=str)
    parser.add_argument("--OUTPUT_FILE_NAME",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_FILE_PATH",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_COLUMN_NAME",
                        type=str)
    if False:
        parser.add_argument("--FILTER_VARIABLE_DATA")  # Not implemented
    parser.add_argument("--FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_PYTHON_DATA_TYPE",
                        type=str,
                        choices=["int", "str"],
                        help="""This affects how the data is sorted and if it's quoted or not in the SQL query.""")
    parser.add_argument("--FILTER_VARIABLE_CHUNK_SIZE",
                        default=10000,
                        type=int)
    parser.add_argument("--QUERY_CHUNK_SIZE",
                        default=10000,
                        type=int)

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
    parser.add_argument("--PROJECT_DIR_DEPTH",
                        default=2,
                        type=int,
                        help="")
    parser.add_argument("--DATA_REQUEST_DIR_DEPTH",
                        default=4,
                        type=int,
                        help="")
    parser.add_argument("--IRB_DIR_DEPTH",
                        default=3,
                        type=int,
                        help="")
    parser.add_argument("--IDR_DATA_REQUEST_DIR_DEPTH",
                        default=6,
                        type=int,
                        help="")
    parser.add_argument("--ROOT_DIRECTORY",
                        default="IRB_DIRECTORY",
                        type=str,
                        choices=["DATA_REQUEST_DIRECTORY",
                                 "IDR_DATA_REQUEST_DIRECTORY",
                                 "IRB_DIRECTORY",
                                 "PROJECT_OR_PORTION_DIRECTORY"],
                        help="")
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

    # Parsed arguments: Main: Multiple query option
    DICTIONARY_OF_ARGUMENTS = argNamespace.DICTIONARY_OF_MAPPING_ARGUMENTS

    # Parsed arguments: Main: Single query option
    CONNECTION_STRING = argNamespace.CONNECTION_STRING
    SQL_FILE_PATH = argNamespace.SQL_FILE_PATH
    OUTPUT_FILE_NAME = argNamespace.OUTPUT_FILE_NAME
    FILTER_VARIABLE_FILE_PATH = argNamespace.FILTER_VARIABLE_FILE_PATH
    FILTER_VARIABLE_COLUMN_NAME = argNamespace.FILTER_VARIABLE_COLUMN_NAME
    FILTER_VARIABLE_DATA = argNamespace.FILTER_VARIABLE_DATA
    FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER = argNamespace.FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER
    FILTER_VARIABLE_PYTHON_DATA_TYPE = argNamespace.FILTER_VARIABLE_PYTHON_DATA_TYPE
    FILTER_VARIABLE_CHUNK_SIZE = argNamespace.FILTER_VARIABLE_CHUNK_SIZE
    QUERY_CHUNK_SIZE = argNamespace.QUERY_CHUNK_SIZE

    # Parsed arguments: Main
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
    # <<< `Argparse` arguments <<<

    # Argument parsing: Additional checks  # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    SINGLE_OPTION_ARGUMENTS = [CONNECTION_STRING,
                               SQL_FILE_PATH,
                               OUTPUT_FILE_NAME,
                               FILTER_VARIABLE_FILE_PATH,
                               FILTER_VARIABLE_COLUMN_NAME,
                               FILTER_VARIABLE_DATA,
                               FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER,
                               FILTER_VARIABLE_PYTHON_DATA_TYPE,
                               FILTER_VARIABLE_CHUNK_SIZE,
                               QUERY_CHUNK_SIZE]
    if DICTIONARY_OF_ARGUMENTS and any(SINGLE_OPTION_ARGUMENTS):
        parser.error("""This program is meant to function one of two ways. Either
1. Pass `DICTIONARY_OF_ARGUMENTS`, or
2. Pass each of the single-option arguments
    2. 1. `CONNECTION_STRING`
    2. 2. `SQL_FILE_PATH`
    2. 3. `OUTPUT_FILE_NAME`
    2. 4. `FILTER_VARIABLE_FILE_PATH`
    2. 5. `FILTER_VARIABLE_COLUMN_NAME`
    2. 6. `FILTER_VARIABLE_DATA`
    2. 7. `FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER`
    2. 8. `FILTER_VARIABLE_PYTHON_DATA_TYPE`
    2. 9. `FILTER_VARIABLE_CHUNK_SIZE`
    2. 10. `QUERY_CHUNK_SIZE`""")

    # Variables: Path construction: General
    runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
    dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
    IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
    IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
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

    if ROOT_DIRECTORY == "PROJECT_OR_PORTION_DIRECTORY":
        rootDirectory = projectDir
    elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
        rootDirectory = dataRequestDir
    elif ROOT_DIRECTORY == "IRB_DIRECTORY":
        rootDirectory = IRBDir
    elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
        rootDirectory = IDRDataRequestDir
    else:
        raise Exception("An unexpected error occurred.")

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

    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:

    # Arguments: Meta
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    """)
    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)  # TODO Remove secrets from list to print, e.g., passwords.
    logger.info(f"""Script arguments:\n{argListString}""")

    # Begin module body

    # Conform mapping arguments
    if DICTIONARY_OF_ARGUMENTS:
        sqlFileSettings = DICTIONARY_OF_ARGUMENTS
    elif all(SINGLE_OPTION_ARGUMENTS):
        sqlFileSettings = {0: {"CONNECTION_STRING": CONNECTION_STRING,
                               "FILTER_VARIABLE_FILE_PATH": FILTER_VARIABLE_FILE_PATH,
                               "FILTER_VARIABLE_COLUMN_NAME": FILTER_VARIABLE_COLUMN_NAME,
                               "FILTER_VARIABLE_DATA": FILTER_VARIABLE_DATA,
                               "FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER": FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER,
                               "FILTER_VARIABLE_PYTHON_DATA_TYPE": FILTER_VARIABLE_PYTHON_DATA_TYPE,
                               "FILTER_VARIABLE_CHUNK_SIZE": FILTER_VARIABLE_CHUNK_SIZE,
                               "OUTPUT_FILE_NAME": OUTPUT_FILE_NAME,
                               "QUERY_CHUNK_SIZE": QUERY_CHUNK_SIZE,
                               "SQL_FILE_PATH": SQL_FILE_PATH}}
    else:
        raise Exception("This should not happen")

    # Iterate over SQL file settings
    logger.info("""Iterating over SQL directory contents.""")
    sqlFiles = sorted([(key, di["SQL_FILE_PATH"]) for key, di in sqlFileSettings.items()], key=lambda tu: tu[1])
    for dataKey, sqlFilePath in sqlFiles:
        logger.info(f"""  Working on data key "{dataKey}" with SQL file path "{sqlFilePath}".""")
        fileSettings = sqlFileSettings[dataKey]
        SQL_FILE_PATH = fileSettings["SQL_FILE_PATH"]
        CONNECTION_STRING = fileSettings["CONNECTION_STRING"]
        FILTER_VARIABLE_CHUNK_SIZE = fileSettings["FILTER_VARIABLE_CHUNK_SIZE"]
        FILTER_VARIABLE_COLUMN_NAME = fileSettings["FILTER_VARIABLE_COLUMN_NAME"]
        FILTER_VARIABLE_DATA = fileSettings["FILTER_VARIABLE_DATA"]
        FILTER_VARIABLE_FILE_PATH = fileSettings["FILTER_VARIABLE_FILE_PATH"]
        FILTER_VARIABLE_PYTHON_DATA_TYPE = fileSettings["FILTER_VARIABLE_PYTHON_DATA_TYPE"]
        FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER = fileSettings["FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER"]
        OUTPUT_FILE_NAME = fileSettings["OUTPUT_FILE_NAME"]
        QUERY_CHUNK_SIZE = fileSettings["QUERY_CHUNK_SIZE"]
        getData(sqlFilePath=SQL_FILE_PATH,
                connectionString=CONNECTION_STRING,
                filterVariableChunkSize=FILTER_VARIABLE_CHUNK_SIZE,
                filterVariableColumnName=FILTER_VARIABLE_COLUMN_NAME,
                filterVariableData=FILTER_VARIABLE_DATA,
                filterVariableFilePath=FILTER_VARIABLE_FILE_PATH,
                filterVariablePythonDataType=FILTER_VARIABLE_PYTHON_DATA_TYPE,
                filterVariableSqlQueryTemplatePlaceholder=FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER,
                outputFileName=OUTPUT_FILE_NAME,
                queryChunkSize=QUERY_CHUNK_SIZE,
                runOutputDir=runOutputDir,
                logger=logger)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End module body
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
