"""
Converts columns by using one of three pre-defined mapping functions.
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
# Third-party packages
import pandas as pd
import pathos.pools as pp
# First-party packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.convertColumns.hash import convertColumnsHash
from drapi.code.drapi.deIdentificationFunctions import functionFromSettings
from drapi.code.drapi.parseAliasArguments import parseAliasArguments
from drapi.code.drapi.constants.phiVariables import VARIABLE_SUFFIXES
from drapi.code.drapi.constants.variableAliases import VARIABLE_ALIASES


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()
    # Arguments: Main
    parser.add_argument("IRB_NUMBER",
                        type=str,
                        help="""The IRB number, usually in the form "<PROTOCOL_ABBREVIATION><SERIAL_NUMBER>, where <PROTOCOL_ABBREVIATION> is something like "IRB", "NH", "WIRB", and <SERIAL_NUMBER> is a 9-digit number where the first four digits is the four-digit year, e.g., "2024".""")
    parser.add_argument("SCRIPT_TEST_MODE",
                        type=lambda stringValue: True if stringValue.lower() == "true" else False if stringValue.lower() == "false" else None,
                        help=""" Choose one of {{True, False}}""")


    # Arguments: Main: Multiple variable option: Dictionary format
    parser.add_argument("--DICTIONARY_OF_MAPPING_ARGUMENTS",
                        type=json.loads,
                        help="""The input must be of this format: {variableName: {"Encryption Type": encryptionType, "Encryption Secret": encryptionSecret}}""")

    # Arguments: Main: Multiple variable option: String format
    # NOTE TODO Not implemented yet. This should allow the user to input a space-delimitted list of arguments, easier than the dictionary option
    parser.add_argument("--MAPPING_ARGUMENTS",
                        nargs="+",
                        type=json.loads,
                        help="""The input must be of this format: {variableName: {"Encryption Type": encryptionType, "Encryption Secret": encryptionSecret}}""")
    
    # Arguments: Main: File paths and portion names
    parser.add_argument("PATHS",
                        nargs="+",
                        type=str,
                        help="")
    parser.add_argument("--PORTION_NAME",
                        type=str,
                        help="""The name of the set or subset of data, usually one of "BO", "Clinical Text", "Clinical Text Metadata", "Line-level", "OMOP", "SDOH".""")
    parser.add_argument("--BY",
                        choices=["dir", "file", "file-dir"],
                        help="""Whether the `PATHS` values passed are for directories or files. If you are passing directories but wish their contents to be processed in parallel, use the option "file-dir".""")
    

    # Arguments: Main: Single variable option
    parser.add_argument("--VARIABLE_NAME_TO_ENCRYPT",
                        type=str,
                        help="")
    helptext = r"""1: Additive encryption. E.g., `encryptValue1(value='123456789', secret=1)  # 123456790`.
2: Encrypt with character-wise XOR operation of both operands, with the second operand rotating over the set of character-wise values in `secretkey`. E.g., `encryptValue1(value='123456789', secret='password')  # 'AS@GBYE\I'
3: Encrypt with whole-value XOR operation. Requires both operands to be integers. E.g., `encryptValue1(value=123456789, secret=111111111)  # 1326016938`"""
    parser.add_argument("--ENCRYPTION_TYPE",
                        type=int,
                        choices=[1, 2, 3],
                        help=helptext)
    parser.add_argument("--ENCRYPTION_SECRET",
                        type=lambda stringValue: int(stringValue) if stringValue.isnumeric() else stringValue,
                        help="We expect an integer or stringValue. If the stringValue is purely numbers, it will be converted to an integer object. If you don't pass an argument then a secret value will be generated for you at random.")

    parser.add_argument("--CUSTOM_ALIASES",
                        help="""A JSON-formatted string of the form {`ALIAS`: `VARIABLE_NAME`}, where `VARIABLE_NAME` is the BO version of a variable name, and `ALIAS` is an alias of the variable name. An example is {"EncounterCSN": "Encounter # (CSN)"}.""",
                        type=json.loads)
    parser.add_argument("--DEFAULT_ALIASES",
                        help="""Indicates whether to include the default IDR aliases for variables.""",
                        action="store_true")

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

    # Parsed arguments: Main
    IRB_NUMBER = argNamespace.IRB_NUMBER

    DICTIONARY_OF_MAPPING_ARGUMENTS = argNamespace.DICTIONARY_OF_MAPPING_ARGUMENTS
    MAPPING_ARGUMENTS = argNamespace.MAPPING_ARGUMENTS

    VARIABLE_NAME_TO_ENCRYPT = argNamespace.VARIABLE_NAME_TO_ENCRYPT
    ENCRYPTION_TYPE = argNamespace.ENCRYPTION_TYPE
    ENCRYPTION_SECRET = argNamespace.ENCRYPTION_SECRET

    BY = argNamespace.BY
    PATHS = argNamespace.PATHS
    PORTION_NAME = argNamespace.PORTION_NAME

    CUSTOM_ALIASES = argNamespace.CUSTOM_ALIASES
    DEFAULT_ALIASES = argNamespace.DEFAULT_ALIASES

    # TODO Proper definition
    listOfPortionDirs, listOfPortionNames, LIST_OF_PORTION_CONDITIONS = None, None, None

    SCRIPT_TEST_MODE = argNamespace.SCRIPT_TEST_MODE

    # Custom argument parsing: aliases
    variableAliases = parseAliasArguments(customAliases=CUSTOM_ALIASES,
                                          useDefaultAliases=DEFAULT_ALIASES,
                                          defaultAliases=VARIABLE_ALIASES)
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

    # Argument parsing: Additional checks  # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    if DICTIONARY_OF_MAPPING_ARGUMENTS and (VARIABLE_NAME_TO_ENCRYPT or ENCRYPTION_TYPE or ENCRYPTION_SECRET):
        parser.error("""This program is meant to function one of two ways. Either
1. Pass `DICTIONARY_OF_MAPPING_ARGUMENTS`, or
2. Pass each of
    2. a. `VARIABLE_NAME_TO_ENCRYPT`
    2. b. `ENCRYPTION_TYPE`
    2. c. `ENCRYPTION_SECRET`""")

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
        uid = USER_ID[:]
    else:
        uid = fr"{USER_DOMAIN}\{USERNAME}"
    if USER_PWD:
        userPwd = USER_PWD
    else:
        userPWD = os.environ["HFA_UFADPWD"]
    conStr = f"mssql+pymssql://{uid}:{userPWD}@{SERVER}/{DATABASE}"

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

    # >>> Argument prep >>>
    # Conform mapping arguments
    if DICTIONARY_OF_MAPPING_ARGUMENTS:
        mappingArguments = [{variableName: tu} for variableName, tu in DICTIONARY_OF_MAPPING_ARGUMENTS.items()]
    elif MAPPING_ARGUMENTS:
        mappingArguments = [di for di in MAPPING_ARGUMENTS]
    elif VARIABLE_NAME_TO_ENCRYPT and ENCRYPTION_TYPE and ENCRYPTION_SECRET:
        mappingArguments = [{VARIABLE_NAME_TO_ENCRYPT: [ENCRYPTION_TYPE, ENCRYPTION_SECRET]}]
    else:
        raise Exception("This should not happen")

    # Define the de-identification functions for each variable.
    deIdentificationFunctions = {}
    mappingSettings = {}
    for di in mappingArguments:
        variableName = list(di.keys())[0]
        encryptionType, encryptionSecret0 = list(di.values())[0]
        encryptionSecret, variableFunction = functionFromSettings(ENCRYPTION_TYPE=encryptionType,
                                                                  ENCRYPTION_SECRET=encryptionSecret0,
                                                                  IRB_NUMBER=IRB_NUMBER,
                                                                  suffix=VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"])
        deIdentificationFunctions[variableName] = variableFunction
        mappingSettings[variableName] = {"Encryption Type": encryptionType,
                                         "Encryption Secret (Input)": encryptionSecret0,
                                         "Encryption Secret (Final)": encryptionSecret}

    # QA: Test de-identification functions
    logger.info("""QA: Testing de-identification functions.""")
    for variableName, func in deIdentificationFunctions.items():
        logger.info(f"""  {variableName}: {func(1)}.""")

    PARGS = []
    if BY.lower() == "dir":
        zipObj = zip(LIST_OF_PORTION_CONDITIONS,
                     listOfPortionDirs,
                     listOfPortionNames)
        for portionCondition, portionDir, portionName in zipObj:
            argsClone = (BY,
                         # Arguments used in preparation of case functions
                         IRB_NUMBER,
                         VARIABLE_SUFFIXES,
                         # Arguments used in preparation AND passed to other functions: Common to both cases
                         VARIABLE_ALIASES,
                         deIdentificationFunctions,
                         logger,
                         # Arguments passed to other functions: Common to both cases
                         rootDirectory,
                         runOutputDir,
                         CHUNKSIZE,
                         MESSAGE_MODULO_CHUNKS,
                         SCRIPT_TEST_MODE,
                         # Arguments passed to other functions: "dir" case
                         portionDir,
                         portionCondition,
                         portionName,
                         # Arguments passed to other functions: "file" case
                         None,
                         None)
            PARGS.append(argsClone)
    # Arguments passed to other functions: "file" case
    elif BY.lower() == "file":
        li = list(map(lambda fpath: (PORTION_NAME, fpath), PATHS))
        for portionName, fpath in li:
            argsClone = (BY,
                         # Arguments used in preparation of case functions
                         IRB_NUMBER,
                         VARIABLE_SUFFIXES,
                         # Arguments used in preparation AND passed to other functions: Common to both cases
                         VARIABLE_ALIASES,
                         deIdentificationFunctions,
                         logger,
                         # Arguments passed to other functions: Common to both cases
                         rootDirectory,
                         runOutputDir,
                         CHUNKSIZE,
                         MESSAGE_MODULO_CHUNKS,
                         SCRIPT_TEST_MODE,
                         # Arguments passed to other functions: "dir" case
                         None,
                         None,
                         None,
                         # Arguments passed to other functions: "file" case
                         fpath,
                         portionName)
            PARGS.append(argsClone)
    elif BY.lower() == "file-dir":
        paths = []
        for pathString in PATHS:
            dpath = Path(pathString)
            paths.extend(dpath.iterdir())
        li = list(map(lambda fpath: (PORTION_NAME, fpath), paths))
        for portionName, fpath in li:
            argsClone = (BY,
                         # Arguments used in preparation of case functions
                         IRB_NUMBER,
                         VARIABLE_SUFFIXES,
                         # Arguments used in preparation AND passed to other functions: Common to both cases
                         VARIABLE_ALIASES,
                         deIdentificationFunctions,
                         logger,
                         # Arguments passed to other functions: Common to both cases
                         rootDirectory,
                         runOutputDir,
                         CHUNKSIZE,
                         MESSAGE_MODULO_CHUNKS,
                         SCRIPT_TEST_MODE,
                         # Arguments passed to other functions: "dir" case
                         None,
                         None,
                         None,
                         # Arguments passed to other functions: "file" case
                         fpath,
                         portionName)
            PARGS.append(argsClone)
    else:
        raise Exception("This should not happen!")
    parallelizationArgListString = pprint.pformat(PARGS)
    logger.info(f"""`PARGS`:\n{parallelizationArgListString}""")

    # <<< Argument prep <<<

    # Save secrets
    secretPath = runOutputDir.joinpath("Metadata", "Mapping Settings", "Mapping Settings.CSV")
    makeDirPath(secretPath.parent)
    df = pd.DataFrame.from_dict(data=mappingSettings, orient="index")
    df = df.sort_index()
    df.to_csv(secretPath)

    with pp._ProcessPool() as pool:
        results = pool.starmap(convertColumnsHash, PARGS)

    # End module body
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
