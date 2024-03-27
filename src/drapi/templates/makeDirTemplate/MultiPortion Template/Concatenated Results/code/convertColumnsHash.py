"""
"""

import argparse
import json
import logging
import os
import pprint
from pathlib import Path
from typing import List
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    makeMap,
                                    readDataFile,
                                    successiveParents)
# Super-local
from common import (IRB_NUMBER,
                    NOTES_PORTION_FILE_CRITERIA,
                    OMOP_PORTION_FILE_CRITERIA,
                    VARIABLE_ALIASES,
                    VARIABLE_SUFFIXES)
from commonFunctions import (choosePathToLog,
                             functionFromSettings)


# Functions
def convertColumnsHash(listOfPortionDirs: list,
                       listOfPortionNames: List[str],
                       LIST_OF_PORTION_CONDITIONS: list,
                       IRB_NUMBER: int,
                       VARIABLE_SUFFIXES: dict,
                       logger: logging.Logger,
                       deIdentificationFunctions: dict,
                       VARIABLE_ALIASES: dict,
                       CHUNKSIZE: int,
                       SCRIPT_TEST_MODE: bool = False):
    """
    """
    for variableName, func in deIdentificationFunctions.items():
        logger.info(f"""  {variableName}: {func(0)}.""")

    # Assert all portions have file criteria accounted for
    if len(listOfPortionDirs) == len(LIST_OF_PORTION_CONDITIONS):
        pass
    else:
        raise Exception("The number of portions does not equal the number of portion conditions.")

    # Collect columns to convert
    columnsToConvert = sorted(list(deIdentificationFunctions.keys()))

    # Load de-identification maps for each variable that needs to be de-identified
    logger.info("""Loading de-identification maps for each variable that needs to be de-identified.""")
    mapsColumnNames = {}
    variablesCollected = [fname for fname in deIdentificationFunctions.keys()]
    for varName in variablesCollected:
        logger.info(f"""  Creating de-identified variable name for "{varName}".""")
        mapsColumnNames[varName] = f"De-identified {varName}"
    # Add aliases to `mapsColumnNames`
    for varName in VARIABLE_ALIASES.keys():
        varAlias = VARIABLE_ALIASES[varName]
        map_ = makeMap(IDset=set(),
                       IDName=varName,
                       startFrom=1,
                       irbNumber=IRB_NUMBER,
                       suffix=VARIABLE_SUFFIXES[varAlias]["deIdIDSuffix"],
                       columnSuffix=varName,
                       deIdentificationMapStyle="lemur",
                       logger=logging.getLogger())
        mapsColumnNames[varName] = map_.columns[-1]

    # QA: Test de-identification functions
    logger.info(f"""QA: Testing de-identification functions.""")
    for variableName, func in DE_IDENTIFICATION_FUNCTIONS.items():
        logger.info(f"""  {variableName}: {func(1)}.""")

    # De-identify columns
    logger.info("""De-identifying files.""")
    allowLogging = False
    # Set file options: Map file
    for portionName, directory, fileConditions in zip(listOfPortionNames, listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        directory = Path(directory)  # For type hinting
        # Act on directory
        logger.info(f"""Working on directory "{choosePathToLog(directory, rootDirectory)}".""")
        listOfFiles = sorted(list(directory.iterdir()))
        for file in listOfFiles:
            logger.info(f"""  Working on file "{choosePathToLog(file, rootDirectory)}".""")
            fileOptions = {columnName: {"header": True,
                                        "mode": "w"} for columnName in columnsToConvert}
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options: Data file
                exportPath = runOutputDir.joinpath("Portions", portionName, f"{file.stem}.CSV")
                makeDirPath(exportPath.parent)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logger.info("""    File has met all conditions for processing.""")
                logger.info("""  ..  Reading file to count the number of chunks.""")
                # >>> TEST BLOCK >>>  # TODO Remove
                if SCRIPT_TEST_MODE:
                    it1Total = 100
                else:
                    it1Total = sum([1 for _ in readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)])
                # <<< TEST BLOCK <<<
                logger.info(f"""  ..  This file has {it1Total:,} chunks.""")
                # Calculate logging requency
                if it1Total < MESSAGE_MODULO_CHUNKS:
                    moduloChunks = it1Total
                else:
                    moduloChunks = round(it1Total / MESSAGE_MODULO_CHUNKS)
                if it1Total / moduloChunks < 100:
                    moduloChunks = 1
                else:
                    pass
                dfChunks = readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)
                filePreview = readDataFile(file, nrows=2)
                filePreview = pd.DataFrame(filePreview)
                for it1, dfChunk0 in enumerate(dfChunks, start=1):
                    # >>> TEST BLOCK >>>  # TODO Remove
                    if SCRIPT_TEST_MODE:
                        if it1 > 1:
                            logger.info(f"""  ..  `SCRIPT_TEST_MODE` engaged. BREAKING.""")
                            break
                    # <<< TEST BLOCK <<<
                    dfChunk = pd.DataFrame(dfChunk0)
                    # Work on chunk
                    if it1 % moduloChunks == 0:
                        allowLogging = True
                    else:
                        allowLogging = False
                    if allowLogging:
                        logger.info(f"""  ..  Working on chunk {it1:,} of {it1Total:,}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        if columnName in VARIABLE_ALIASES.keys():
                            columnNameAlias = VARIABLE_ALIASES[columnName]
                            hasAlias = True
                        else:
                            columnNameAlias = columnName
                            hasAlias = False
                        # Logging block
                        if allowLogging:
                            if hasAlias:
                                logger.info(f"""  ..    Working on column "{columnName}" aliased as "{columnNameAlias}".""")
                            else:
                                logger.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in columnsToConvert or columnNameAlias in columnsToConvert:
                            if allowLogging:
                                logger.info("""  ..  ..  Column must be converted. Converting column...""")
                            # De-identify column: create de-identified values
                            newColumnName = mapsColumnNames[columnName]
                            newColumn = dfChunk[columnName].apply(deIdentificationFunctions[columnNameAlias])
                            newColumn = pd.Series(newColumn)  # For type hinting
                            newColumnWithOldName = newColumn
                            newColumnWithNewName = newColumn.rename(newColumnName)  # We can change `newColumnName` with the aliased version
                            # QA: Column/Variable Map: Variables
                            mapSavePath = runOutputDir.joinpath("Metadata", "Maps by Portion", portionName, f"{columnNameAlias}", f"{file.stem}.CSV")
                            makeDirPath(mapSavePath.parent)
                            mapHeader = fileOptions[columnNameAlias]["header"]
                            mapMode = fileOptions[columnNameAlias]["mode"]
                            # QA: Column/Variable Map: Save mapped column
                            chunkColumnMap = pd.concat([dfChunk[columnName], newColumnWithNewName], axis=1).drop_duplicates()
                            logger.info(f"""  ..  ..  Saving QA table to "{choosePathToLog(mapSavePath.absolute(), rootPath=rootDirectory)}".""")
                            logger.info(f"""  ..  ..  Saving QA table to `mapHeader` set to "{mapHeader}".""")
                            logger.info(f"""  ..  ..  Saving QA table to `mapMode` set to "{mapMode}".""")
                            chunkColumnMap.to_csv(mapSavePath, index=False, header=mapHeader, mode=mapMode)
                            fileOptions[columnNameAlias]["header"] = False
                            fileOptions[columnNameAlias]["mode"] = "a"
                            # De-identify column: Replace old values
                            dfChunk[columnName] = newColumnWithOldName
                            dfChunk = dfChunk.rename(columns={columnName: newColumnName})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileHeaders = False
                    fileMode = "a"
                    if allowLogging:
                        logger.info(f"""  ..  Chunk saved to "{choosePathToLog(exportPath, rootDirectory)}".""")
                # End file lopp
                pass
            else:
                logger.info("""    This file does not need to be processed.""")


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

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

    # Arguments: Main: Single variable option
    parser.add_argument("--VARIABLE_NAME_TO_ENCRYPT",
                        type=str,
                        help="")
    parser.add_argument("--ENCRYPTION_TYPE",
                        type=int,
                        choices=[1, 2, 3],
                        help="""1: Additive encryption. E.g., `encryptValue1(value='123456789', secret=1)  # 123456790`.
2: Encrypt with character-wise XOR operation of both operands, with the second operand rotating over the set of character-wise values in `secretkey`. E.g., `encryptValue1(value='123456789', secret='password')  # 'AS@GBYE\I'
3: Encrypt with whole-value XOR operation. Requires both operands to be integers. E.g., `encryptValue1(value=123456789, secret=111111111)  # 1326016938`""")
    parser.add_argument("--ENCRYPTION_SECRET",
                        type=lambda stringValue: int(stringValue) if stringValue.isnumeric() else stringValue,
                        help="We expect an integer or stringValue. If the stringValue is purely numbers, it will be converted to an integer object. If you don't pass an argument then a secret value will be generated for you at random.")

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
    DICTIONARY_OF_MAPPING_ARGUMENTS = argNamespace.DICTIONARY_OF_MAPPING_ARGUMENTS
    MAPPING_ARGUMENTS = argNamespace.MAPPING_ARGUMENTS

    VARIABLE_NAME_TO_ENCRYPT = argNamespace.VARIABLE_NAME_TO_ENCRYPT
    ENCRYPTION_TYPE = argNamespace.ENCRYPTION_TYPE
    ENCRYPTION_SECRET = argNamespace.ENCRYPTION_SECRET

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

    LIST_OF_PORTION_NAMES = ["OMOP",
                             "Notes Text",
                             "Notes Metadata"]
    LIST_OF_PORTION_DIRS = ["../Concatenated Results/data/output/convertColumnsGeneral/2024-02-23 18-11-43",
                            "/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Notes/original_note_pull/data/Output/free_text/cohort_note/tsv",
                            "/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Notes/original_note_pull/data/Output/free_text"]
    LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA,
                                  [lambda pathObj: pathObj.suffix.lower() == ".tsv"],
                                  NOTES_PORTION_FILE_CRITERIA]  # TODO Remove hard-coded option

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
    DE_IDENTIFICATION_FUNCTIONS = {}
    mappingSettings = {}
    for di in mappingArguments:
        variableName = list(di.keys())[0]
        encryptionType, encryptionSecret0 = list(di.values())[0]
        encryptionSecret, variableFunction = functionFromSettings(ENCRYPTION_TYPE=encryptionType,
                                                                  ENCRYPTION_SECRET=encryptionSecret0,
                                                                  IRB_NUMBER=IRB_NUMBER)
        DE_IDENTIFICATION_FUNCTIONS[variableName] = lambda value: variableFunction(value=value,
                                                                                   suffix=VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"],
                                                                                   secret=encryptionSecret)
        mappingSettings[variableName] = {"Encryption Type": encryptionType,
                                         "Encryption Secret (Input)": encryptionSecret0,
                                         "Encryption Secret (Final)": encryptionSecret}
    
    # QA: Test de-identification functions
    logger.info(f"""QA: Testing de-identification functions.""")
    for variableName, func in DE_IDENTIFICATION_FUNCTIONS.items():
        logger.info(f"""  {variableName}: {func(1)}.""")

    # <<< Argument prep <<<

    # Save secrets
    secretPath = runOutputDir.joinpath("Metadata", "Mapping Settings", "Mapping Settings.CSV")
    makeDirPath(secretPath.parent)
    df = pd.DataFrame.from_dict(data=mappingSettings, orient="index")
    df = df.sort_index()
    df.to_csv(secretPath)

    convertColumnsHash(listOfPortionDirs=LIST_OF_PORTION_DIRS,
                       LIST_OF_PORTION_CONDITIONS=LIST_OF_PORTION_CONDITIONS,
                       listOfPortionNames=LIST_OF_PORTION_NAMES,
                       deIdentificationFunctions=DE_IDENTIFICATION_FUNCTIONS,
                       logger=logger,
                       IRB_NUMBER=IRB_NUMBER,
                       VARIABLE_ALIASES=VARIABLE_ALIASES,
                       VARIABLE_SUFFIXES=VARIABLE_SUFFIXES,
                       CHUNKSIZE=CHUNKSIZE,
                       SCRIPT_TEST_MODE=SCRIPT_TEST_MODE)

    # End module body
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
