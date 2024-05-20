"""
QA: Make sure values were correctly converted.

# TODO Handle headers for aliased variables. Currently when tables are concatenated for the same variable but with different aliases, each alias is stored in a separate column. This can be done under `combineMaps`.
"""

import argparse
import json
import logging
import os
import pprint
import shutil
from pathlib import Path
# Third-party packages
pass
# Local packages
from drapi import __version__ as drapiVersion
from drapi.code.drapi.constants.variableAliases import VARIABLE_ALIASES
from drapi.code.drapi.constants.constants import DATA_TYPES_DICT
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    makeDirPath)
from drapi.code.drapi.parseAliasArguments import parseAliasArguments
from drapi.code.drapi.qa.deidentification import (combineMaps,
                                                  qaListOfFilesAndDirectories)


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
                        help="""When used with `COMBINE_MAPS_MODE=1`, this is the list of paths to the portion de-identification metadata directories (e.g. "Metadata/Maps by Portion/<PORTION_NAME>"). When this option is used all maps are combined by variable name and the analysis is performed on the resulting tables. Input is a string that is converted to a Path object.\nWhen used with `COMBINE_MAPS_MODE=2`... .""",
                        nargs="*",
                        type=Path)
    parser.add_argument("-m",
                        "--COMBINE_MAPS_MODE",
                        help="""Select "1" if combining atomic maps, select "2" if combining combined maps.""",
                        choices=[1, 2],
                        type=int)

    parser.add_argument("--CUSTOM_ALIASES",
                        help="""A JSON-formatted string of the form {`ALIAS`: `VARIABLE_NAME`}, where `VARIABLE_NAME` is the BO version of a variable name, and `ALIAS` is an alias of the variable name. An example is {"EncounterCSN": "Encounter # (CSN)"}.""",
                        type=json.loads)
    parser.add_argument("--DEFAULT_ALIASES",
                        help="""Indicates whether to include the default IDR aliases for variables.""",
                        action="store_true")
    parser.add_argument("--PANDAS_ENGINE",
                        help="""The pandas engine to use when reading data files.""",
                        default="pyarrow",
                        choices=["c",
                                 "none",
                                 "python",
                                 "pyarrow"])

    parser.add_argument("-t",
                        "--SCRIPT_TEST_MODE",
                        help="Runs the script in a shorter fashion, to test its main features.",
                        action="store_true")

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
    COMBINE_MAPS_MODE = argNamespace.COMBINE_MAPS_MODE

    CUSTOM_ALIASES = argNamespace.CUSTOM_ALIASES
    DEFAULT_ALIASES = argNamespace.DEFAULT_ALIASES
    PANDAS_ENGINE = argNamespace.PANDAS_ENGINE

    SCRIPT_TEST_MODE = argNamespace.SCRIPT_TEST_MODE

    # Parsed arguments: Meta-variables
    LOG_LEVEL = argNamespace.LOG_LEVEL

    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    # Custom argument parsing: input paths
    if LIST_OF_FILES or LIST_OF_DIRECTORIES:
        pass
    elif COMBINE_MAPS:
        pass
    else:
        parser.error("Although `LIST_OF_FILES`, `LIST_OF_DIRECTORIES`, and `COMBINE_MAPS` are marked as optional in the help text, you must actually provide arguments for at least one of them.")

    # Custom argument parsing: aliases
    variableAliases = parseAliasArguments(customAliases=CUSTOM_ALIASES,
                                          useDefaultAliases=DEFAULT_ALIASES,
                                          defaultAliases=VARIABLE_ALIASES)
    
    # Custom argument parsing: `PANDAS_ENGINE`
    if PANDAS_ENGINE.lower() == "none":
        PANDAS_ENGINE = None
    # <<< Custom argument parsing <<<

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
    argListString = pprint.pformat(argList)
    logger.info(f"""Script arguments:\n{argListString}""")

    # >>> Begin module body >>>
    if LIST_OF_FILES or LIST_OF_DIRECTORIES:
        dfresult = qaListOfFilesAndDirectories(LIST_OF_DIRECTORIES=LIST_OF_DIRECTORIES,
                                               LIST_OF_FILES=LIST_OF_FILES,
                                               SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                               logger=logger)
    elif COMBINE_MAPS:
        listOfPathsForCombinedMaps = combineMaps(listOfDirectories=COMBINE_MAPS,
                                                 mode=COMBINE_MAPS_MODE,
                                                 variableAliases=variableAliases,
                                                 dataTypesDict=DATA_TYPES_DICT,
                                                 runIntermediateDir=runIntermediateDir,
                                                 runOutputDir=runOutputDir,
                                                 rootPath=projectDir,
                                                 rootDirectory=projectDir,
                                                 logger=logger,
                                                 pandasEngine=PANDAS_ENGINE)
        dfresult = qaListOfFilesAndDirectories(LIST_OF_DIRECTORIES=[],
                                               LIST_OF_FILES=listOfPathsForCombinedMaps,
                                               SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                               logger=logger)

    # Report results
    if SCRIPT_TEST_MODE:
        pass
    else:
        dfresult = dfresult.sort_values(by=["Directory",
                                            "File Name"])
        savePath = runOutputDir.joinpath("Map Type Results.CSV")
        dfresult.to_csv(savePath, index=False)
        dfString = dfresult.to_string()

        logger.info(f"""Map Type Results:\n{dfString}""")

    if not SCRIPT_TEST_MODE:
        logger.info(f"""Removing intermediate files.""")
        shutil.rmtree(runIntermediateDir)

    # <<< End module body <<<
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
