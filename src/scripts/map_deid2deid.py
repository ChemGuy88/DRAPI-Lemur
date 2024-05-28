"""
Create a map from one de-identified ID to another de-identified ID.
"""

import argparse
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
import pandas as pd
from sqlalchemy import URL
# Local packages
from drapi import __version__ as drapiVersion
from drapi import loggingChoices
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
# Super-local imports
from drapi.code.drapi.getData.getData import getData


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--LEFT_DEIDENTIFICATION_MAP_PATH",
                        type=str,
                        required=True)
    parser.add_argument("--LEFT_VARIABLE_NAME",
                        type=str,
                        help="The column header for the left map.")
    parser.add_argument("--RIGHT_DEIDENTIFICATION_MAP_PATH",
                        type=str,
                        required=True)
    parser.add_argument("--RIGHT_VARIABLE_NAME",
                        type=str,
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
    parser.add_argument("--LEFT_VARIABLE_DEIDENTIFIED_NAME",
                        type=str,
                        help="The de-identified version of the left variable's name")
    parser.add_argument("--RIGHT_VARIABLE_DEIDENTIFIED_NAME",
                        type=str,
                        help="The de-identified version of the right variable's name")

    # Variable aliases
    parser.add_argument("--LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP",
                        type=str,
                        help="")
    parser.add_argument("--LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP",
                        type=str,
                        help="")
    parser.add_argument("--RIGHT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP",
                        type=str,
                        help="")
    parser.add_argument("--RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP",
                        type=str,
                        help="")
    parser.add_argument("--STANDARDIZE_COLUMN_NAMES",
                        action="store_true",
                        help="Whether to rename variable aliases to standard variable names.")

    parser.add_argument("--DROP_NA_HOW",
                        default="all",
                        choices=["all",
                                 "any"],
                        help="How to drop NAs from the final results.")

    parser.add_argument("--FIRST_TIME",
                        action="store_true")
    parser.add_argument("--OLD_RUN_PATH",
                        type=str,
                        help="""The path to the data previously downloaded from another session of this program. This is usually the "Left-to-right Map" directory.""")

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
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    LEFT_DEIDENTIFICATION_MAP_PATH = argNamespace.LEFT_DEIDENTIFICATION_MAP_PATH
    LEFT_VARIABLE_NAME = argNamespace.LEFT_VARIABLE_NAME
    RIGHT_DEIDENTIFICATION_MAP_PATH = argNamespace.RIGHT_DEIDENTIFICATION_MAP_PATH
    RIGHT_VARIABLE_NAME = argNamespace.RIGHT_VARIABLE_NAME
    SQL_FILE_PATH = argNamespace.SQL_FILE_PATH
    SQL_FILE_PLACEHOLDER = argNamespace.SQL_FILE_PLACEHOLDER
    OUTPUT_FILE_NAME = argNamespace.OUTPUT_FILE_NAME

    LEFT_VARIABLE_DEIDENTIFIED_NAME = argNamespace.LEFT_VARIABLE_DEIDENTIFIED_NAME
    RIGHT_VARIABLE_DEIDENTIFIED_NAME = argNamespace.RIGHT_VARIABLE_DEIDENTIFIED_NAME

    LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP = argNamespace.LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP
    LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP = argNamespace.LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP
    RIGHT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP = argNamespace.RIGHT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP
    RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP = argNamespace.RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP
    STANDARDIZE_COLUMN_NAMES = argNamespace.STANDARDIZE_COLUMN_NAMES

    DROP_NA_HOW = argNamespace.DROP_NA_HOW

    FIRST_TIME = argNamespace.FIRST_TIME
    OLD_RUN_PATH = argNamespace.OLD_RUN_PATH

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

    # >>> Custom parsing >>>
    # If `STANDARDIZE_COLUMN_NAMES` is passed, we need `LEFT_VARIABLE_NAME` and `RIGHT_VARIABLE_NAME`
    if STANDARDIZE_COLUMN_NAMES:
        if isinstance(LEFT_VARIABLE_NAME, type(None)) or isinstance(LEFT_VARIABLE_NAME, type(None)):
            message = "If `STANDARDIZE_COLUMN_NAMES` is passed, we need `LEFT_VARIABLE_NAME` and `RIGHT_VARIABLE_NAME`"
            parser.error(message)
    # If `LEFT_VARIABLE_DEIDENTIFIED_NAME` is NOT passed, we need `LEFT_VARIABLE_NAME`
    if isinstance(LEFT_VARIABLE_DEIDENTIFIED_NAME, type(None)):
        if isinstance(LEFT_VARIABLE_NAME, type(None)):
            message = "If `LEFT_VARIABLE_DEIDENTIFIED_NAME` is NOT passed, we need `LEFT_VARIABLE_NAME`"
            parser.error(message)
    # If `RIGHT_VARIABLE_DEIDENTIFIED_NAME` is not passed, we need `RIGHT_VARIABLE_NAME`
    if isinstance(RIGHT_VARIABLE_DEIDENTIFIED_NAME, type(None)):
        if isinstance(RIGHT_VARIABLE_NAME, type(None)):
            message = "If `RIGHT_VARIABLE_DEIDENTIFIED_NAME` is not passed, we need `RIGHT_VARIABLE_NAME`"
            parser.error(message)
    # <<< Custom parsing <<<

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
                filterVariableColumnName=LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP,
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
        logger.info(f"""  Working on file {it:,} of {itTotal:,}.""")
        df = pd.read_csv(fpath)
        left2rightdf = pd.concat([left2rightdf, df])
    del df

    # Map 3: Right de-identification map
    rightdf = pd.read_csv(RIGHT_DEIDENTIFICATION_MAP_PATH)

    # Join maps: Homogenize variable names
    pass

    # Join maps
    joinedMaps = leftdf.set_index(LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP).join(other=left2rightdf.set_index(LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP),
                                                                                      how="outer")
    joinedMaps = joinedMaps.reset_index(names=LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP)

    joinedMaps = joinedMaps.set_index(RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP).join(other=rightdf.set_index(RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP),
                                                                                        how="outer")
    joinedMaps = joinedMaps.reset_index(names=RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP)

    # Standardize column names
    if STANDARDIZE_COLUMN_NAMES:
        joinedMaps = joinedMaps.rename(columns={LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP: f"{LEFT_VARIABLE_NAME}_L",
                                                LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP: f"{LEFT_VARIABLE_NAME}_LR",
                                                RIGHT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP: f"{RIGHT_VARIABLE_NAME}_R",
                                                RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP: f"{RIGHT_VARIABLE_NAME}_LR",
                                                LEFT_VARIABLE_DEIDENTIFIED_NAME: f"De-identified {LEFT_VARIABLE_NAME}",
                                                RIGHT_VARIABLE_DEIDENTIFIED_NAME: f"De-identified {RIGHT_VARIABLE_NAME}",
                                                # For the below options we are assuming the de-identification prefix is "De-identififed" and not "deid" or another variant. These lines can possibly be removed.
                                                f"De-identified {LEFT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP}": f"De-identified {LEFT_VARIABLE_NAME}",
                                                f"De-identified {LEFT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP}": f"De-identified {LEFT_VARIABLE_NAME}",
                                                f"De-identified {RIGHT_VARIABLE_NAME_ALIAS_DEIDENTIFICATION_MAP}": f"De-identified {RIGHT_VARIABLE_NAME}",
                                                f"De-identified {RIGHT_VARIABLE_NAME_ALIAS_LEFT_TO_RIGHT_MAP}": f"De-identified {RIGHT_VARIABLE_NAME}"})
    else:
        pass

    # Select data to output: Select column names
    # We are assuming that if the left and right de-identified variable names are not supplied we are using the standard variable names.
    if LEFT_VARIABLE_DEIDENTIFIED_NAME:
        leftDeidentifiedColumnName = LEFT_VARIABLE_DEIDENTIFIED_NAME
    else:
        leftDeidentifiedColumnName = f"De-identified {LEFT_VARIABLE_NAME}"
    if RIGHT_VARIABLE_DEIDENTIFIED_NAME:
        rightDeidentifiedColumnName = RIGHT_VARIABLE_DEIDENTIFIED_NAME
    else:
        rightDeidentifiedColumnName = f"De-identified {RIGHT_VARIABLE_NAME}"
    COLUMNS_TO_EXPORT = [leftDeidentifiedColumnName,
                         rightDeidentifiedColumnName]

    # Select data to output: Select columns
    logger.info(joinedMaps.columns)
    logger.info(joinedMaps.head().T)
    finalMap = joinedMaps[COLUMNS_TO_EXPORT]

    mapSize0 = finalMap.shape[0]
    finalMap = finalMap.dropna(how=DROP_NA_HOW)
    finalMap = finalMap.sort_values(by=COLUMNS_TO_EXPORT)
    exportPath = runOutputDir.joinpath(f"{LEFT_VARIABLE_NAME} to {RIGHT_VARIABLE_NAME}.CSV")
    finalMap.to_csv(exportPath, index=False)

    # QA
    mapSize1 = finalMap.shape[0]
    logger.info(f"""Final map shape before and after dropping "{DROP_NA_HOW}" NAs: {mapSize0:,} -> {mapSize1:,}.""")

    # Output location summary
    logger.info(f"""Results are in "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # End module body
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
