"""
Script for downloading data using SQL queries.
"""

import argparse
import json
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
import sqlalchemy as sa
# First-party packages
from drapi import __version__ as drapiVersion
from drapi import loggingChoices
from drapi.code.drapi.classes import (SecretString)
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
from drapi.code.drapi.getData.getData import getData


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main: Multiple query option
    parser.add_argument("--DICTIONARY_OF_ARGUMENTS",
                        type=json.loads)

    # Arguments: Main: Single query option
    parser.add_argument("--CONNECTION_STRING",
                        type=SecretString)
    parser.add_argument("--SQL_FILE_PATH",
                        type=str)
    parser.add_argument("--OUTPUT_FILE_NAME",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_FILE_PATH",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_COLUMN_NAME",
                        type=str)
    parser.add_argument("--FILTER_VARIABLE_DATA",
                        default=None,
                        choices=[None],
                        help="This has not been implemented. For now, please just use the default value of `None` and instead pass the path to the file with the data and its column header.")
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

    parser.add_argument("--SCRIPT_TEST_MODE",
                        default=False,
                        choices=[True, False],
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

    # Parsed arguments: Main: Multiple query option
    DICTIONARY_OF_ARGUMENTS = argNamespace.DICTIONARY_OF_ARGUMENTS

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
    LOG_LEVEL = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # Argument parsing: Additional checks  # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    # NOTE That `SINGLE_OPTION_ARGUMENTS` doesn't include `FILTER_VARIABLE_DATA`, because for now it's only possible value is `None`.
    SINGLE_OPTION_ARGUMENTS = [CONNECTION_STRING,
                               SQL_FILE_PATH,
                               OUTPUT_FILE_NAME,
                               FILTER_VARIABLE_FILE_PATH,
                               FILTER_VARIABLE_COLUMN_NAME,
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
    2. 6. `FILTER_VARIABLE_SQL_QUERY_TEMPLATE_PLACEHOLDER`
    2. 7. `FILTER_VARIABLE_PYTHON_DATA_TYPE`
    2. 8. `FILTER_VARIABLE_CHUNK_SIZE`
    2. 9. `QUERY_CHUNK_SIZE`""")

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
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # End module body
    logger.info(f"""Finished running "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")
