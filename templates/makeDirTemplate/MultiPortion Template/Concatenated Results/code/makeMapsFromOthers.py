"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# NOTE Expects integer IDs, so no string IDs like Epic Patient IDs.
"""

import json
import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.constants.constants import DATA_TYPES
from drapi.drapi import getTimestamp, successiveParents, makeDirPath, makeMap, makeSetComplement, ditchFloat, handleDatetimeForJson
from common import IRB_NUMBER, DATA_REQUEST_ROOT_DIRECTORY_DEPTH, VARIABLE_SUFFIXES, NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, NOTES_PORTION_FILE_CRITERIA, OLD_MAPS_DIR_PATH, OMOP_PORTION_FILE_CRITERIA, BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN, BO_PORTION_FILE_CRITERIA, ZIP_CODE_PORTION_DIR_MAC, ZIP_CODE_PORTION_DIR_WIN, ZIP_CODE_PORTION_FILE_CRITERIA

# Arguments
SETS_PATH = Path("data/output/getIDValues/...")

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

MAC_PATHS = [BO_PORTION_DIR_MAC,
             NOTES_PORTION_DIR_MAC,
             OMOPPortionDirMac,
             ZIP_CODE_PORTION_DIR_MAC]
WIN_PATHS = [BO_PORTION_DIR_WIN,
             NOTES_PORTION_DIR_WIN,
             OMOPPortionDirWin,
             ZIP_CODE_PORTION_DIR_WIN]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA,
                              NOTES_PORTION_FILE_CRITERIA,
                              OMOP_PORTION_FILE_CRITERIA,
                              ZIP_CODE_PORTION_FILE_CRITERIA]

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
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
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

    # Get set of values
    # NOTE The code that used to be in this section was moved to "getIDValues.py"
    getIDValuesOutput = SETS_PATH
    logging.info(f"""Using the set of new values in the directory "{getIDValuesOutput.absolute().relative_to(rootDirectory)}".""")

    # Concatenate all old maps
    oldMaps = {}
    logging.info("""Concatenating all similar pre-existing maps.""")
    collectedVariables = [fname.stem for fname in getIDValuesOutput.iterdir()]
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        if variableName in OLD_MAPS_DIR_PATH.keys():
            logging.info("""    Variable has pre-existing map(s).""")
            listOfMapPaths = OLD_MAPS_DIR_PATH[variableName]
            dfConcat = pd.DataFrame()
            for mapPath in listOfMapPaths:
                logging.info(f"""  ..  Reading pre-existing map from "{mapPath}".""")
                df = pd.DataFrame(pd.read_csv(mapPath))
                dfConcat = pd.concat([dfConcat, df])
            oldMaps[variableName] = dfConcat
        elif variableName not in OLD_MAPS_DIR_PATH.keys():
            logging.info("""    Variable has no pre-existing map.""")
            oldMaps[variableName] = pd.DataFrame()

    # Get the set difference between all old maps and the set of un-mapped values
    valuesToMap = {}
    setsToMapDataDir = runIntermediateDataDir.joinpath("valuesToMap")
    makeDirPath(setsToMapDataDir)
    logging.info("""Getting the set difference between all old maps and the set of un-mapped values.""")
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        variableDataType = DATA_TYPES[variableName]

        # Get old set of IDs
        logging.info("""    Getting the old set of IDs.""")
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldIDSet = set(oldMap[variableName].values)
            oldIDSet = set([ditchFloat(el) for el in oldIDSet])  # NOTE: Hack. Convert values to type int or string
        elif len(oldMap) == 0:
            oldIDSet = set()
        logging.info(f"""    The size of this set is {len(oldIDSet):,}.""")

        # Get new set of IDs
        newSetPath = getIDValuesOutput.joinpath(f"{variableName}.txt")
        logging.info(f"""    Getting the new set of IDs from "{newSetPath.absolute().relative_to(rootDirectory)}".""")
        newIDSet = set()
        with open(newSetPath, "r") as file:
            text = file.read()
            lines = text.split("\n")[:-1]
        for line in lines:
            newIDSet.add(line)
        if variableDataType.lower() == "numeric":
            newIDSet = set([ditchFloat(el) for el in newIDSet])  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise ValueError(msg)
        logging.info(f"""    The size of this set is {len(newIDSet):,}.""")

        # Set difference
        IDSetDiff = newIDSet.difference(oldIDSet)
        valuesToMap[variableName] = IDSetDiff

        # Save new subset to `setsToMapDataDir`
        fpath = setsToMapDataDir.joinpath(f"{variableName}.JSON")
        with open(fpath, "w") as file:
            if variableDataType.lower() == "numeric":
                li = [ditchFloat(IDNumber) for IDNumber in IDSetDiff]  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                li = list(IDSetDiff)
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)
            file.write(json.dumps(li, default=handleDatetimeForJson))
        if len(IDSetDiff) == 0:
            series = pd.Series(dtype=int)
        else:
            if variableDataType.lower() == "numeric":
                series = pd.Series(sorted(list(IDSetDiff)))
            elif variableDataType.lower() == "string":
                series = pd.Series(sorted([str(el) for el in IDSetDiff]))
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)

    # Get numbers for new map
    logging.info("""Getting numbers for new map.""")
    newNumbersDict = {}
    for variableName in collectedVariables:
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldNumbersSet = set(oldMap["deid_num"].values)
        elif len(oldMap) == 0:
            oldNumbersSet = set()
        # Get quantity of numbers needed for map
        quantityOfNumbersUnmapped = len(valuesToMap[variableName])
        # Get new numbers
        lenOlderNumbersSet = len(oldNumbersSet)
        if lenOlderNumbersSet == 0:
            newNumbers = list(range(1, quantityOfNumbersUnmapped + 1))
        else:
            newNumbersSet = makeSetComplement(oldNumbersSet, quantityOfNumbersUnmapped)
            newNumbers = sorted(list(newNumbersSet))
        newNumbersDict[variableName] = newNumbers

    # Map un-mapped values
    logging.info("""Mapping un-mapped values.""")
    for file in setsToMapDataDir.iterdir():
        variableName = file.stem
        variableDataType = DATA_TYPES[variableName]
        logging.info(f"""  Working on un-mapped values for variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Map contents
        values = valuesToMap[variableName]
        if variableDataType.lower() == "numeric":
            values = set(int(float(value)) for value in values)  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise Exception(msg)
        numbers = sorted(list(newNumbersDict[variableName]))
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=numbers, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName, deIdentifiedIDColumnHeaderFormatStyle="lemur")
        # Save map
        mapPath = runOutputDir.joinpath(f"{variableName} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
