"""
QA: Make sure values were correctly converted.
"""

import argparse
import logging
import os
import pprint
from pathlib import Path
from typing_extensions import List, Union
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getMapType,
                                    getTimestamp,
                                    makeDirPath,
                                    successiveParents)


# Functions
def iterateOverFiles(listOfFiles: List[Union[str, Path]],
                     SCRIPT_TEST_MODE: bool,
                     directoryName: Union[str, None] = None) -> pd.DataFrame:
    """
    """
    di = {}
    it1Total = len(listOfFiles)
    for it1, fpath in enumerate(listOfFiles, start=1):
        logger.info(f"""  Working on file {it1:,} of {it1Total:,}: "{fpath.name}".""")
        if SCRIPT_TEST_MODE:
            pass
        else:
            df = pd.read_csv(fpath, low_memory=False)
            result = getMapType(df=df)
            di[it1] = {"Directory": directoryName,
                       "File Name": fpath.name,
                       "Result": result}
    dfresult = pd.DataFrame.from_dict(data=di, orient="index")
    return dfresult


def qaListOfFilesAndDirectories(LIST_OF_FILES: List[Union[str, Path]],
                                LIST_OF_DIRECTORIES: List[Union[str, Path]],
                                SCRIPT_TEST_MODE: bool):
    """
    """
    # Sort input alphabetically for easier debugging.
    if LIST_OF_FILES:
        listOfFiles1 = sorted([Path(fpath) for fpath in LIST_OF_FILES])
    else:
        listOfFiles1 = []
    if LIST_OF_DIRECTORIES:
        listOfDirectories = sorted([Path(dpath) for dpath in LIST_OF_DIRECTORIES])
    else:
        listOfDirectories = []

    # Work on files first
    dfresult1 = iterateOverFiles(listOfFiles=listOfFiles1,
                                 SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                 directoryName=None)

    # Work on directories
    resultsli = []
    for dpath in listOfDirectories:
        logger.info(f"""  Working on directory "{dpath.name}".""")
        listOfFiles2 = sorted(list(dpath.iterdir()))
        dfresult2 = iterateOverFiles(listOfFiles=listOfFiles2,
                                     SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                     directoryName=dpath.name)
        resultsli.append(dfresult2)

    dfresult = pd.concat([dfresult1] + resultsli, axis=0)
    return dfresult


def combineMaps(path: Path,
                runIntermediateDir: Path,
                runOutputDir: Path,
                MESSAGE_MODULO_CHUNKS: int,
                rootPath: Path,
                logger: logging.Logger) -> List[Path]:
    """
    Assumes `PATH` is the "Maps by Portion" folder with the following structure
    - Maps by Portion
      - Portion 1
        - Variable 1
          - CSV File 1
          - CSV File 2
          - etc.
        - Variable 2
          - CSV File 1
          - CSV File 2
          - etc.
      - Portion 2
        - Variable 1
          - CSV File 1
          - CSV File 2
          - etc.
        - Variable 2
          - CSV File 1
          - CSV File 2
          - etc.
        - etc.
      - etc.
    """
    listOfPortions = sorted(list(path.iterdir()))
    dictOfVariables = {}
    it1 = 1
    for portionDir in listOfPortions:
        listOfVariables = sorted(list(portionDir.iterdir()))
        for variableDir in listOfVariables:
            variableDirName = variableDir.name
            listOfFiles = sorted(list(variableDir.iterdir()))
            diNew = {it: {"Variable Name": variableDirName,
                          "File Path": fpath} for it, fpath in enumerate(listOfFiles, start=it1)}
            it1 += len(listOfFiles)
            dictOfVariables.update(diNew)

    dfAllPaths = pd.DataFrame.from_dict(data=dictOfVariables, orient="index")
    dfAllPaths.index.name = "Index"
    dfAllPaths = dfAllPaths.sort_values(by=["Variable Name", "File Path"])
    savePathAllPaths = runOutputDir.joinpath("Paths for All Maps.CSV")
    dfAllPaths.to_csv(path_or_buf=savePathAllPaths)

    # Combine maps by variable name
    listOfVariableNames = dfAllPaths["Variable Name"].drop_duplicates()
    it2Total = len(listOfVariableNames)
    CHUNKSIZE = 50000
    savePathDir = runIntermediateDir.joinpath("Combined Maps", "By Variable")
    savePathDir.mkdir(mode=744, parents=True)
    listOfPathsForCombinedMaps = []
    for it2, variableName in enumerate(listOfVariableNames, start=1):
        logger.info(f"""  Working on variable {it2:,} of {it2Total}: "{variableName}".""")
        mask = dfAllPaths["Variable Name"] == variableName
        listOfPaths = dfAllPaths["File Path"][mask].to_list()
        it3Total = len(listOfPaths)
        listOfDataFrames = []
        for it3, fpath in enumerate(listOfPaths, start=1):
            logger.info(f"""    Working on file {it3:,} of {it3Total}: "{choosePathToLog(path=fpath, rootPath=rootPath)}".""")
            chunkGenerator1 = pd.read_csv(fpath, chunksize=CHUNKSIZE)
            chunkGenerator2 = pd.read_csv(fpath, chunksize=CHUNKSIZE)
            logger.info("    Reading the file to count the number of chunks.")
            it4Total = sum([1 for _ in chunkGenerator1])
            logger.info(f"    Reading the file to count the number of chunks - done. The file has {it4Total:,} chunks.")
            # Calculate logging frequency
            if it4Total < MESSAGE_MODULO_CHUNKS:
                moduloChunks = it4Total
            else:
                moduloChunks = round(it4Total / MESSAGE_MODULO_CHUNKS)
            if it4Total / moduloChunks < 100:
                moduloChunks = 1
            else:
                pass
            for it4, dfChunk in enumerate(chunkGenerator2, start=1):
                # Work on chunk
                if it4 % moduloChunks == 0:
                    allowLogging = True
                else:
                    allowLogging = False
                if allowLogging:
                    logger.info(f"""  ..  Working on chunk {it4:,} of {it4Total:,}.""")
                dfChunk = pd.DataFrame(dfChunk)  # For type hinting
                dfChunk = dfChunk.drop_duplicates()
                listOfDataFrames.append(dfChunk)
        dfAllUnique = pd.concat(listOfDataFrames)
        dfAllUnique = dfAllUnique.drop_duplicates()
        savePath = savePathDir.joinpath(f"{variableName}.CSV")
        logger.info(f"""    Saving combined maps to "{choosePathToLog(path=savePath, rootPath=rootDirectory)}".""")
        dfAllUnique.to_csv(path_or_buf=savePath,
                           index=False)
        listOfPathsForCombinedMaps.append(savePath)

    return listOfPathsForCombinedMaps


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("-d",
                        "--LIST_OF_DIRECTORIES",
                        nargs="*",
                        help="")
    parser.add_argument("-f",
                        "--LIST_OF_FILES",
                        nargs="*",
                        help="")

    parser.add_argument("-c",
                        "--COMBINE_MAPS",
                        help="This is the path to the directory that contains the portions and their respective variables. When this option is used all maps are combined by variable name and the analysis is performed on the resulting tables. Input is a string that is converted to a Path object.",
                        type=Path)

    parser.add_argument("-t",
                        "--SCRIPT_TEST_MODE",
                        help="",
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

    # Arguments: Meta-variables
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
    LIST_OF_DIRECTORIES = argNamespace.LIST_OF_DIRECTORIES
    LIST_OF_FILES = argNamespace.LIST_OF_FILES

    COMBINE_MAPS = argNamespace.COMBINE_MAPS

    SCRIPT_TEST_MODE = argNamespace.SCRIPT_TEST_MODE

    # Parsed arguments: General
    CHUNKSIZE = argNamespace.CHUNKSIZE
    MESSAGE_MODULO_CHUNKS = argNamespace.MESSAGE_MODULO_CHUNKS
    MESSAGE_MODULO_FILES = argNamespace.MESSAGE_MODULO_FILES

    # Parsed arguments: Meta-variables
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

    # >>> Custom argument parsing >>>
    if LIST_OF_FILES or LIST_OF_DIRECTORIES:
        pass
    elif COMBINE_MAPS:
        pass
    else:
        parser.error("Although `LIST_OF_FILES`, `LIST_OF_DIRECTORIES`, and `COMBINE_MAPS` are marked as optional in the help text, you must actually provide arguments for at least one of them.")

    # <<< Custom argument parsing <<<

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
            runIntermediateDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
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

    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:


    # Arguments
    `CHUNKSIZE`: "{CHUNKSIZE}"
    `MESSAGE_MODULO_CHUNKS`: "{MESSAGE_MODULO_CHUNKS}"
    `MESSAGE_MODULO_FILES`: "{MESSAGE_MODULO_FILES}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USER_DOMAIN` = "{USER_DOMAIN}"
    `USERNAME` = "{USERNAME}"
    `USER_ID` = "{USER_ID}"
    `USER_PWD` = censored
    """)
    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)
    logger.info(f"""Script arguments:\n{argListString}""")

    # >>> Begin module body >>>
    if LIST_OF_FILES or LIST_OF_DIRECTORIES:
        dfresult = qaListOfFilesAndDirectories(LIST_OF_DIRECTORIES=LIST_OF_DIRECTORIES,
                                               LIST_OF_FILES=LIST_OF_FILES,
                                               SCRIPT_TEST_MODE=SCRIPT_TEST_MODE)
    elif COMBINE_MAPS:
        listOfPathsForCombinedMaps = combineMaps(path=COMBINE_MAPS,
                                                 runIntermediateDir=runIntermediateDir,
                                                 runOutputDir=runOutputDir,
                                                 MESSAGE_MODULO_CHUNKS=MESSAGE_MODULO_CHUNKS,
                                                 rootPath=rootDirectory,
                                                 logger=logger)
        dfresult = qaListOfFilesAndDirectories(LIST_OF_DIRECTORIES=[],
                                               LIST_OF_FILES=listOfPathsForCombinedMaps,
                                               SCRIPT_TEST_MODE=SCRIPT_TEST_MODE)

    # Report results
    if SCRIPT_TEST_MODE:
        pass
    else:
        dfresult = dfresult.sort_values(by=["Directory",
                                            "File Name"])
        savePath = runOutputDir.joinpath("Map Type Results.CSV")
        dfresult.to_csv(savePath)
        dfString = dfresult.to_string()

        logger.info(f"""Map Type Results:\n{dfString}""")

    # <<< End module body <<<
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
