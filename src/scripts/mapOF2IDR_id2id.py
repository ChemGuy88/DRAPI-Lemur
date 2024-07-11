"""
Create a map from OneFlorida Patient IDs to IDR Patient Keys
"""

import argparse
import logging
import os
import pprint
import shutil
from pathlib import Path
from typing_extensions import List
# Third-party packages
import pandas as pd
from sqlalchemy import URL
# Local packages
from drapi import __version__ as drapiVersion
from drapi import PATH as drapiInstallationPath
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    makeDirPath,
                                    replace_sql_query)
from drapi.code.drapi.getData.getData import getData
from drapi.code.drapi.oneFlorida import ID_TYPE_DICT as ONE_FLORIDA_ID_TYPE_DICT
from drapi.code.drapi.oneFlorida import ID_TYPE_LIST as ONE_FLORIDA_ID_TYPE_LIST


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--FILE_PATH",
                        help="The path to the file that is used as input. The file can contain either OneFlorida patient IDs or IDR patient IDs.")
    parser.add_argument("--FILE_HEADER",
                        help="The header of the file containing the variable you want to convert from.")
    parser.add_argument("--FROM",
                        type=str,
                        choices=ONE_FLORIDA_ID_TYPE_LIST,
                        help="The variable used as input.")
    parser.add_argument("--TO_VARIABLES",
                        nargs="+",
                        action="extend",
                        choices=ONE_FLORIDA_ID_TYPE_LIST,
                        help="The variable(s) to be output.")
    parser.add_argument("--ID_TYPE",
                        type=str,
                        choices=ONE_FLORIDA_ID_TYPE_LIST,
                        help="The standard variable name use to filter the SQL query.")
    parser.add_argument("--FIRST_TIME",
                        action="store_true",
                        help="""If you have run this script before and have downloaded the data, select "True", otherwise select "False".""")
    parser.add_argument("--OLD_RUN_PATH",
                        help="The path to the directory that contains the downloaded intermediate data.")

    # Arguments: Main
    parser.add_argument("--SCRIPT_TEST_MODE",
                        action="store_true",
                        help="""Use this option to run a shorter version.""")

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
    FILE_PATH: str = argNamespace.FILE_PATH
    FILE_HEADER: str = argNamespace.FILE_HEADER
    FROM: str = argNamespace.FROM
    TO_VARIABLES: List = argNamespace.TO_VARIABLES
    ID_TYPE: str = argNamespace.ID_TYPE
    FIRST_TIME: bool = argNamespace.FIRST_TIME
    OLD_RUN_PATH: str = argNamespace.OLD_RUN_PATH

    # >>> meta variable <<<
    FORM_1_ARGUMENTS = [FIRST_TIME,
                        FILE_PATH,
                        FILE_HEADER,
                        FROM,
                        TO_VARIABLES,
                        ID_TYPE]
    FORM_2_ARGUMENTS = [OLD_RUN_PATH,
                        FROM,
                        TO_VARIABLES,
                        ID_TYPE]
    # <<< meta variable <<<

    SCRIPT_TEST_MODE = argNamespace.SCRIPT_TEST_MODE

    # Parsed arguments: General
    CHUNKSIZE = argNamespace.CHUNKSIZE
    MESSAGE_MODULO_CHUNKS = argNamespace.MESSAGE_MODULO_CHUNKS
    MESSAGE_MODULO_FILES = argNamespace.MESSAGE_MODULO_FILES

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
    if FIRST_TIME and OLD_RUN_PATH:
        message = "It is ambiguous if you provide both `FIRST_TIME` and `OLD_RUN_PATH`. Please only choose one."
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

    # Download OneFlorida to IDR map
    if FIRST_TIME:
        # Select input: NOTE This block is structured like an else-if block to remind the programmer of how he can use `getData`.
        # Select input: Dataframe
        if False:
            fromData = pd.read_csv(filepath_or_buffer=FILE_PATH)
            filePath = None
            fileHeader = None
        # Select input: Series
        elif False:
            fromData = pd.read_csv(filepath_or_buffer=FILE_PATH)[FILE_HEADER]
            filePath = None
            fileHeader = None
        # Select input: File path with column name
        elif True:
            fromData = None
            filePath = FILE_PATH
            fileHeader = FILE_HEADER
        else:
            raise Exception("This should not happen")

        downloadDir = runIntermediateDir.joinpath("Downloaded Data")
        downloadDir.mkdir()

        connectionString = URL.create(drivername="mssql+pymssql",
                                      username=userID,
                                      password=userPwd,
                                      host=SERVER,
                                      database=DATABASE)

        # Modify query according to `TO_VARIABLES` and `FROM` arguments
        SQL_FILE_PATH_RELATIVE = Path("../../src/drapi/sql/OneFlorida to UF Health Patient ID Map.SQL")
        SQL_FILE_PATH = drapiInstallationPath.joinpath(SQL_FILE_PATH_RELATIVE)
        with open(SQL_FILE_PATH, "r") as file:
            query0 = file.read()
            IDTypeInput = ID_TYPE.lower()
            IDTypeSQL = ONE_FLORIDA_ID_TYPE_DICT[IDTypeInput]
            query = replace_sql_query(query=query0,
                                      old="{PYTHON_VARIABLE: IDTypeSQL}",
                                      new=IDTypeSQL,
                                      logger=logger)
        sqlFilePathTemp = runIntermediateDir.joinpath(f"OneFlorida to UF Health Patient ID Map - Filter by {FROM}.SQL")
        with open(sqlFilePathTemp, "w") as file:
            file.write(query)

        getData(sqlFilePath=sqlFilePathTemp,
                connectionString1=connectionString,
                filterVariableChunkSize=10000,
                filterVariableColumnName=fileHeader,
                filterVariableData=fromData,
                filterVariableFilePath=filePath,
                filterVariablePythonDataType="int",
                filterVariableSqlQueryTemplatePlaceholder="{PYTHON_VARIABLE: IDTypeValues}",
                logger=logger,
                outputFileName=f"OneFlorida to UF Health Patient ID Map",
                runOutputDir=downloadDir,
                downloadData=True,
                connectionString2=None,
                newSQLTable_Database=None,
                newSQLTable_Name=None,
                newSQLTable_Schema=None)
    else:
        downloadDir = Path(OLD_RUN_PATH)

    # Concatenate downloaded data
    pathli = sorted(list(downloadDir.iterdir()))
    concatenatedMapPath = runOutputDir.joinpath(f"OneFlorida to UF Health Patient ID Map - Raw.CSV")
    header = True
    for fpath in pathli:
        logger.info(f"""  Reading file "{choosePathToLog(path=fpath, rootPath=projectDir)}".""")
        df = pd.read_csv(filepath_or_buffer=fpath)
        df.to_csv(path_or_buf=concatenatedMapPath,
                  index=False,
                  header=header,
                  mode="a")
        header = False

    # Select data to output
    finalMap = pd.read_csv(filepath_or_buffer=concatenatedMapPath)
    columnsToExport = TO_VARIABLES
    finalMap = finalMap[columnsToExport]
    finalMap = finalMap.sort_values(by=columnsToExport)
    exportPath = runOutputDir.joinpath(f"OneFlorida to UF Health Patient ID Map - Final.CSV")
    finalMap.to_csv(exportPath, index=False)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files
    logger.info("Removing intermediate files.")
    shutil.rmtree(runIntermediateDir)
    logger.info("Removing intermediate files - done.")

    # <<< End module body <<<
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
