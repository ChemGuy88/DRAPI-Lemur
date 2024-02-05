"""
Get the set of ID values for all variables to de-identify.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

__all__ = ["runIntermediateDataDir"]

import csv
import json
import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    readDataFile,
                                    sortIntegersAndStrings,
                                    successiveParents)
from drapi.constants.phiVariables import VARIABLE_NAME_TO_FILE_NAME_DICT
# Project parameters: General
from common import (COLUMNS_TO_DE_IDENTIFY,
                    DATA_REQUEST_ROOT_DIRECTORY_DEPTH,
                    DATA_TYPES_DICT)
# Project parameters: Portion paths and criteria
from common import (BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN,
                    I2B2_PORTION_DIR_MAC, I2B2_PORTION_DIR_WIN,
                    MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN,
                    NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN,
                    OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN)
# Project parameters: Criteria
from common import (BO_PORTION_FILE_CRITERIA,
                    I2B2_PORTION_FILE_CRITERIA,
                    NOTES_PORTION_FILE_CRITERIA,
                    OMOP_PORTION_FILE_CRITERIA)


# Arguments
SETS_INTERMEDIATE_PATH = None

CHUNK_SIZE = 50000

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Arguments: Portion Paths and conditions
if USE_MODIFIED_OMOP_DATA_SET:
    OMOPPortionDirMac = MODIFIED_OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = MODIFIED_OMOP_PORTION_DIR_WIN
else:
    OMOPPortionDirMac = OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = OMOP_PORTION_DIR_WIN

PORTION_PATHS_MAC = {"BO": BO_PORTION_DIR_MAC,
                     "i2b2": I2B2_PORTION_DIR_MAC,
                     "Notes": NOTES_PORTION_DIR_MAC,
                     "OMOP": OMOPPortionDirMac}
PORTION_PATHS_WIN = {"BO": BO_PORTION_DIR_WIN,
                     "i2b2": I2B2_PORTION_DIR_WIN,
                     "Notes": NOTES_PORTION_DIR_WIN,
                     "OMOP": OMOPPortionDirWin}

DICT_OF_PORTION_CONDITIONS = {"BO": BO_PORTION_FILE_CRITERIA,
                              "i2b2": I2B2_PORTION_FILE_CRITERIA,
                              "Notes": NOTES_PORTION_FILE_CRITERIA,
                              "OMOP": OMOP_PORTION_FILE_CRITERIA}

# Arguments: Meta-variables
CONCATENATED_RESULTS_DIRECTORY_DEPTH = DATA_REQUEST_ROOT_DIRECTORY_DEPTH - 1
PROJECT_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH  # The concatenation suite of scripts is considered to be the "project".
IRB_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH + 2
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "DATA_REQUEST_DIRECTORY"  # TODO One of the following:
                                           # ["IDR_DATA_REQUEST_DIRECTORY",      # noqa
                                           #  "IRB_DIRECTORY",                   # noqa
                                           #  "DATA_REQUEST_DIRECTORY",          # noqa
                                           #  "CONCATENATED_RESULTS_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    intermediateDataDir = dataDir.joinpath("intermediate")
    outputDataDir = dataDir.joinpath("output")
    if intermediateDataDir:
        runIntermediateDataDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

if ROOT_DIRECTORY == "CONCATENATED_RESULTS_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in PORTION_PATHS_MAC.values()]) or all([path.exists() for path in PORTION_PATHS_WIN.values()])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        dictOfPortionPaths = PORTION_PATHS_MAC.copy()
    elif operatingSystem == "win32":
        dictOfPortionPaths = PORTION_PATHS_WIN.copy()
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    print("Not implemented. Check settings in your script.")
    sys.exit()

# Directory creation: General
makeDirPath(runIntermediateDataDir)
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

if __name__ == "__main__":
    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(LOG_LEVEL)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)

    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler, streamHandler],
                        level=LOG_LEVEL)

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Match portion paths and conditions
    portionPathsAndConditions = {portionName: (dictOfPortionPaths[portionName], DICT_OF_PORTION_CONDITIONS[portionName]) for portionName in dictOfPortionPaths.keys()}
    check1 = [pn1 in DICT_OF_PORTION_CONDITIONS.keys() for pn1 in dictOfPortionPaths.keys()]
    check2 = [pn2 in dictOfPortionPaths.keys() for pn2 in DICT_OF_PORTION_CONDITIONS.keys()]
    assert sum(check1) == len(check1), "Not all portion paths are associated with a portion condition"
    assert sum(check2) == len(check2), "Not all portion conditions are associated with a portion path"

    # Misc
    columnSetsVarsDiFname = "Column Sets Dict.JSON"

    # Get set of values
    if SETS_INTERMEDIATE_PATH:
        logging.info(f"""Using the set of values previously collected from "{SETS_INTERMEDIATE_PATH}".""")
        with open(SETS_INTERMEDIATE_PATH.joinpath(columnSetsVarsDiFname)) as file:
            columnSetsVarsDi = json.loads(file.read())
    else:
        logging.info("""Getting the set of values for each variable to de-identify.""")
        columnSetsVarsDi = {columnName: {"fpath": runIntermediateDataDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[columnName]}.txt"),
                                         "fileMode": "w",
                                         "portionName": None,
                                         "collected": False} for columnName in COLUMNS_TO_DE_IDENTIFY}
        for portionName, (directory, fileConditions) in portionPathsAndConditions.items():
            # Act on directory
            logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
            for file in directory.iterdir():
                logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logging.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in readDataFile(file, chunkSize=CHUNK_SIZE)])
                    dfChunks = readDataFile(file, chunkSize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        dfChunk = pd.DataFrame(dfChunk)
                        logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logging.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_DE_IDENTIFY:
                                logging.info("""  ..  ..  Column must be de-identified. Collecting values.""")
                                dataType = DATA_TYPES_DICT[columnName]
                                series = dfChunk[columnName]
                                series = series.dropna()
                                series = series.drop_duplicates()
                                if dataType == "Datetime":
                                    values = series.sort_values()
                                    quoting = csv.QUOTE_NONE
                                elif dataType == "Numeric":
                                    series = series.astype(float).astype("Int64")
                                    values = series.sort_values()
                                    quoting = csv.QUOTE_NONE
                                elif dataType == "String":
                                    values = series.astype(str).sort_values()
                                    quoting = csv.QUOTE_ALL
                                elif dataType == "Numeric_Or_String":
                                    mask = series.apply(lambda el: isinstance(el, float))
                                    series.loc[mask[mask].index] = series[mask].astype(int)
                                    values = sortIntegersAndStrings(series.to_list())
                                    values = pd.Series(values)
                                    quoting = csv.QUOTE_ALL
                                else:
                                    raise Exception(f"""Unexpected `dataType` value: "{dataType}".""")
                                columnSetFpath = columnSetsVarsDi[columnName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[columnName]["fileMode"]
                                # logging.info(f"""  ..  ..  Values table preview:\n{values.head()}.""")
                                values.to_csv(path_or_buf=columnSetFpath,
                                              quoting=quoting,
                                              index=False,
                                              header=False,
                                              mode=columnSetFileMode)
                                # logging.info(f"""  ..  ..  Preview of table after saving:\n{pd.read_table(columnSetFpath)}.""")
                                columnSetsVarsDi[columnName]["fileMode"] = "a"
                                columnSetsVarsDi[columnName]["portionName"] = portionName
                                columnSetsVarsDi[columnName]["collected"] = True
                                logging.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(rootDirectory)}" in the project directory.""")
                else:
                    logging.info("""    This file does not need to be processed.""")

        columnSetsVarsDiPath = runIntermediateDataDir.joinpath("Metadata", columnSetsVarsDiFname)
        makeDirPath(columnSetsVarsDiPath.parent)
        columnSetsVarsDiSerializable = columnSetsVarsDi.copy()
        for columnName, di in columnSetsVarsDiSerializable.items():
            columnSetsVarsDiSerializable[columnName]["fpath"] = str(di["fpath"])
        with open(columnSetsVarsDiPath, "w") as file:
            file.write(json.dumps(columnSetsVarsDi))

    # Drop variables that weren't found
    for columnName in COLUMNS_TO_DE_IDENTIFY:
        if columnName in columnSetsVarsDi.keys():
            if columnSetsVarsDi[columnName]["collected"] is False:
                columnSetsVarsDi.pop(columnName)

    # Remove duplicates from set files and save according to data type
    logging.info("Removing duplicates from set files and saving according to data type.")
    columnSetsVarsLi = sorted(list(columnSetsVarsDi.items()), key=lambda tu: tu[0].lower())
    for columnName, fileDi in columnSetsVarsLi:
        logging.info(f"""  Working on variable "{columnName}".""")
        fpath = fileDi["fpath"]
        try:
            series = pd.read_table(fpath, header=None)[0]
        except EmptyDataError as err:
            _ = err
            series = pd.Series(dtype=str)
        # Save according to data type
        portionName = fileDi["portionName"]
        dataType = DATA_TYPES_DICT[columnName]
        if dataType == "Datetime":
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "Numeric":
            series = series.astype(float).astype("Int64")
            quoting = csv.QUOTE_MINIMAL
        elif dataType == "String":
            quoting = csv.QUOTE_ALL
        elif dataType == "Numeric_Or_String":
            quoting = csv.QUOTE_ALL
        else:
            raise Exception(f"""Unexpected `dataType` value: "{dataType}".""")
        series = series.drop_duplicates()
        series = series.sort_values()
        fpath2 = runOutputDir.joinpath("Set Files", f"{VARIABLE_NAME_TO_FILE_NAME_DICT[columnName]}.txt")
        makeDirPath(fpath2.parent)
        series.to_csv(fpath2, quoting=quoting, index=False, header=False)

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logging.info(f"""Finished collecting the set of ID values to de-identify. The set files are located in "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
