"""
Create a map from OneFlorida de-identified IDs to de-identified IDR Patient Keys
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
from typing import (Literal,
                    Union)
# Third-party packages
import pandas as pd
from sqlalchemy import URL
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.constants.phiVariables import VARIABLE_SUFFIXES_BO
# Super-local imports
from drapi.code.drapi.getData.getData import getData


# Functions
def deIdentificationFunction(value: Union[float, int],
                             protocol_id: str,
                             id_suffix: Literal["ACCT",
                                                "ENC",
                                                "LINK",
                                                "LOC",
                                                "NOTE",
                                                "ORD",
                                                "PAT",
                                                "PROV",
                                                "STN"],
                             secret: int) -> str:
    """
    Creates the de-identified ID based on a valid value using an additive mapping.
    """
    newValue = value + secret
    return f"""{protocol_id}_{id_suffix}_{newValue}"""


def deIdentifyByGroups(value,
                       protocol_id: str,
                       id_suffix: str,
                       secret: int) -> Union[pd.NA, str]:
    """
    A wrapper for `deIdentificationFunction` that handles invalid value groups, like NANs and negative numbers.
    """
    if pd.isna(value):
        return value
    elif value <= 0:
        return f"""{protocol_id}_{id_suffix}_0"""
    else:
        return deIdentificationFunction(value=value,
                                        protocol_id=protocol_id,
                                        id_suffix=id_suffix,
                                        secret=secret)


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main: Multiple input option: Dictionary format
    parser.add_argument("--DICTIONARY_OF_ARGUMENTS",
                        type=json.loads,
                        help="""The input must be of this format: {variableName: {"Encryption Type": encryptionType, "Encryption Secret": encryptionSecret}}""")

    # Arguments: Main: Multiple input option: String format
    # NOTE TODO Not implemented yet. This should allow the user to input a space-delimitted list of arguments, easier than the dictionary option
    parser.add_argument("--ARGUMENTS")

    # Arguments: Main: Single input option: Data sources
    parser.add_argument("--MAP_1_PATH",
                        type=str)
    parser.add_argument("--PATIENT_KEYS_FILE_PATH",
                        type=str)
    parser.add_argument("--FIRST_TIME",
                        type=bool)
    parser.add_argument("--OLD_RUN_PATH",
                        type=str,
                        help="The path to the data previously downloaded from another session of this program.")
    parser.add_argument("--MAP_1_COLUMN_NAME_FROM",
                        type=str,
                        help="The column header for the OneFlorida patient ID values.")

    # Arguments: Main: Single input option: De-identification settings
    parser.add_argument("--PROTOCOL_ID",
                        type=str)
    parser.add_argument("--ID_SUFFIX",
                        type=str)
    parser.add_argument("--SECRET",
                        type=int)

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
    parser.add_argument("--PROJECT_DIR_DEPTH",
                        default=2,
                        type=int,
                        help="")
    parser.add_argument("--DATA_REQUEST_DIR_DEPTH",
                        default=4,
                        type=int,
                        help="")
    parser.add_argument("--IRB_DIR_DEPTH",
                        default=4,
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

    # Parsed arguments: Main
    DICTIONARY_OF_ARGUMENTS = argNamespace.DICTIONARY_OF_ARGUMENTS
    ARGUMENTS = argNamespace.ARGUMENTS

    MAP_1_PATH = argNamespace.MAP_1_PATH
    PATIENT_KEYS_FILE_PATH = argNamespace.PATIENT_KEYS_FILE_PATH
    FIRST_TIME = argNamespace.FIRST_TIME
    OLD_RUN_PATH = argNamespace.OLD_RUN_PATH
    MAP_1_COLUMN_NAME_FROM = argNamespace.MAP_1_COLUMN_NAME_FROM

    PROTOCOL_ID = argNamespace.PROTOCOL_ID
    SECRET = argNamespace.SECRET
    ID_SUFFIX = argNamespace.ID_SUFFIX

    # >>> meta variable <<<
    SINGLE_VALUE_ARGUMENTS = [MAP_1_PATH,
                              PATIENT_KEYS_FILE_PATH,
                              FIRST_TIME,
                              OLD_RUN_PATH,
                              PROTOCOL_ID,
                              SECRET,
                              ID_SUFFIX]
    # <<< meta variable <<<

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
    if DICTIONARY_OF_ARGUMENTS and any(SINGLE_VALUE_ARGUMENTS):
        message = f"""This program is meant to function one of two ways. Either
1. Pass `DICTIONARY_OF_ARGUMENTS`, or
2. Pass each of
    2. a. `FIRST_TIME`
    2. b. `MAP_1_PATH`
    2. c. `OLD_RUN_PATH`
    2. d. `PATIENT_KEYS_FILE_PATH`
    """
        parser.error(message=message)

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

    # >>> Begin module body >>>

    # Map 1: OneFlorida de-identification map
    map1df = pd.read_csv(MAP_1_PATH)

    # Map 2: OneFlorida to IDR map
    patientKeys = pd.read_csv(PATIENT_KEYS_FILE_PATH)["PatientKey"]
    if FIRST_TIME:
        map2dir = runOutputDir.joinpath("Map 2")
        map2dir.mkdir()
        connectionString = URL.create(drivername="mssql+pymssql",
                                      username=userID,
                                      password=userPwd,
                                      host=SERVER,
                                      database=DATABASE)

        getData(sqlFilePath="../../Intermediate Results/SQL Portion/sql/OneFlorida to IDR Patient Map.SQL",
                connectionString=connectionString,
                filterVariableChunkSize=10000,
                filterVariableColumnName=MAP_1_COLUMN_NAME_FROM,
                filterVariableData=map1df,
                filterVariableFilePath=None,
                filterVariablePythonDataType="int",
                filterVariableSqlQueryTemplatePlaceholder="{ PYTHON_VARIABLE: IDTypeValues }",
                logger=logger,
                outputFileName="OneFlorida to IDR Patient Map",
                runOutputDir=map2dir,
                queryChunkSize=10000)
    else:
        map2dir = Path(OLD_RUN_PATH)

    # Join maps: Concatenate Map 2
    listofPaths = sorted([fpath for fpath in map2dir.iterdir() if fpath.suffix.lower() == ".csv"])
    map2df = pd.DataFrame()
    itTotal = len(listofPaths)
    for it, fpath in enumerate(listofPaths, start=1):
        logger.info(f"""  Working on file {it:,} of {itTotal}.""")
        df = pd.read_csv(fpath)
        map2df = pd.concat([map2df, df])
    del df

    # Map 3: IDR de-identification map
    map3df = pd.DataFrame()
    map3df["Patient Key"] = map2df["Patient Key"]
    map3df["De-identified Patient Key"] = map3df["Patient Key"].apply(lambda value: deIdentifyByGroups(value=value,
                                                                                                       protocol_id=PROTOCOL_ID,
                                                                                                       id_suffix=ID_SUFFIX,
                                                                                                       secret=SECRET))

    # Join maps: Homogenize variable names
    map1df = map1df.rename(columns={"deid_patient_id": "De-identififed OneFlorida Patient ID",
                                    MAP_1_COLUMN_NAME_FROM: "OneFlorida Patient ID"})
    map2df = map2df.rename(columns={"": ""})
    map3df = map3df.rename(columns={"De-identified PatientKey": "Patient Key",
                                    "De-identified PatientKey.1": "De-identified Patient Key"})

    # Join maps
    df = map1df.set_index("OneFlorida Patient ID").join(other=map2df.set_index("OneFlorida Patient ID"),
                                                        how="outer")
    df = df.reset_index()
    joinedMaps = df.set_index("Patient Key").join(other=map3df.set_index("Patient Key"),
                                                  how="outer")
    joinedMaps = joinedMaps.reset_index()

    # Select data to output
    COLUMNS_TO_EXPORT = ["De-identified Patient Key",
                         "De-identififed OneFlorida Patient ID"]
    finalMap = joinedMaps[COLUMNS_TO_EXPORT]
    finalMap = finalMap.sort_values(by=COLUMNS_TO_EXPORT)
    exportPath = runOutputDir.joinpath("OneFlorida to UFHealth Patient ID Map.CSV")
    finalMap.to_csv(exportPath, index=False)

    # QA
    mapSize = finalMap.dropna().shape[0]
    logger.info(f"""Final map shape after dropping any NAs: {mapSize:,}.""")

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # <<< End module body <<<
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
