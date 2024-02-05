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
from pandas.errors import EmptyDataError
# Local packages
from drapi.code.drapi.drapi import (ditchFloat,
                                    getTimestamp,
                                    handleDatetimeForJson,
                                    makeDirPath,
                                    makeMap,
                                    makeSetComplement,
                                    successiveParents)
from drapi.constants.phiVariables import (FILE_NAME_TO_VARIABLE_NAME_DICT,
                                          VARIABLE_NAME_TO_FILE_NAME_DICT)
# Local packages: Script parameters: General
from common import (IRB_NUMBER,
                    DATA_REQUEST_ROOT_DIRECTORY_DEPTH,
                    DATA_TYPES_DICT,
                    OLD_MAPS_DIR_PATH,
                    VARIABLE_ALIASES,
                    VARIABLE_SUFFIXES)

# Arguments
SETS_PATH = Path(r"..\Concatenated Results\data\output\aliasVariables\...")

CHUNK_SIZE = 50000

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
isAccessible = all([path.exists() for path in SETS_PATH.iterdir()])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        getIDValuesOutput = SETS_PATH
    elif operatingSystem == "win32":
        getIDValuesOutput = SETS_PATH
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
    logging.info(f"""Using the set of new values in the directory "{getIDValuesOutput.absolute().relative_to(rootDirectory)}".""")

    # QA: Make sure all data variables are present in the script parameters.
    collectedVariables = [FILE_NAME_TO_VARIABLE_NAME_DICT[fname.stem] for fname in getIDValuesOutput.iterdir()]
    missingDataTypes = []
    missingVariableSuffixes = []
    for variableName in collectedVariables:
        if variableName not in DATA_TYPES_DICT.keys():
            missingDataTypes.append(variableName)
        if variableName not in VARIABLE_SUFFIXES.keys():
            missingVariableSuffixes.append(variableName)
    if len(missingDataTypes) > 0:
        text = "\n".join(missingDataTypes)
        raise Exception(f"""Not all variables have a data type assigned to them:\n{text}""")
    if len(missingVariableSuffixes) > 0:
        text = "\n".join(missingVariableSuffixes)
        raise Exception(f"Not all variables have a de-identification suffix assigned to them:\n{text}")

    # Create reverse-look-up alias map
    variableAliasesReverse = {}
    for variableAlias, variableMainName in VARIABLE_ALIASES.items():
        if variableMainName in variableAliasesReverse.keys():
            variableAliasesReverse[variableMainName].append(variableAlias)
        else:
            variableAliasesReverse[variableMainName] = [variableAlias]

    # Concatenate all old maps
    oldMaps = {}
    logging.info("""Concatenating all similar pre-existing maps.""")
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        # Get maps explicitely or implicietly referring to this variable name.
        condition1 = variableName in OLD_MAPS_DIR_PATH.keys()
        if condition1:
            variableLookupName = variableName
            logging.info("""    Variable has pre-existing map(s).""")
            listOfMapPaths = OLD_MAPS_DIR_PATH[variableLookupName]
            dfConcat = pd.DataFrame()
            for mapPath in listOfMapPaths:
                logging.info(f"""  ..  Reading pre-existing map from "{mapPath.absolute().relative_to(rootDirectory)}".""")
                df = pd.DataFrame(pd.read_csv(mapPath))
                dfConcat = pd.concat([dfConcat, df])
            oldMaps[variableName] = dfConcat
        if variableName in variableAliasesReverse.keys():
            for variableAlias in variableAliasesReverse[variableName]:
                condition2 = variableAlias in OLD_MAPS_DIR_PATH.keys()
                if condition2:
                    variableLookupName = variableAlias
                    logging.info("""    Variable has pre-existing aliased map(s).""")
                    listOfMapPaths = OLD_MAPS_DIR_PATH[variableLookupName]
                    dfConcat = pd.DataFrame()
                    for mapPath in listOfMapPaths:
                        logging.info(f"""  ..  Reading pre-existing map from "{mapPath}".""")
                        df = pd.DataFrame(pd.read_csv(mapPath))
                        dftemp = makeMap(IDset=set(), IDName=variableName, startFrom=0, irbNumber=IRB_NUMBER, suffix="", columnSuffix=variableName, deIdentificationMapStyle="lemur", logger=logging.getLogger())
                        df.columns = dftemp.columns
                        dfConcat = pd.concat([dfConcat, df])
                    if condition1:
                        df = oldMaps[variableName]
                        dfConcat = pd.concat([dfConcat, df])
                        oldMaps[variableName] = dfConcat
                    else:
                        oldMaps[variableName] = dfConcat
        else:
            condition2 = False
        if not (condition1 or condition2):
            logging.info("""    Variable has no pre-existing map.""")
            oldMaps[variableName] = pd.DataFrame()

    # Get the set difference between all old maps and the set of un-mapped values
    valuesToMap = {}
    setsToMapDataDir = runIntermediateDataDir.joinpath("valuesToMap")
    makeDirPath(setsToMapDataDir)
    logging.info("""Getting the set difference between all old maps and the set of un-mapped values.""")
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        variableDataType = DATA_TYPES_DICT[variableName]

        # Get old set of IDs
        logging.info("""    Getting the old set of IDs.""")
        oldMap = oldMaps[variableName]
        oldMap = pd.DataFrame(oldMap)
        if len(oldMap) > 0:
            if variableDataType.lower() == "numeric":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.unique()
                oldIDSet = set([ditchFloat(el) for el in oldIDSet])  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.astype(str)
                oldIDSet = oldIDSet.unique()
            elif variableDataType.lower() == "numeric_or_string":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.astype(str)
                oldIDSet = oldIDSet.unique()
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)
        elif len(oldMap) == 0:
            oldIDSet = set()
        logging.info(f"""    The size of this set is {len(oldIDSet):,}.""")

        # Get new set of IDs
        newSetPath = getIDValuesOutput.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]}.txt")
        logging.info(f"""    Getting the new set of IDs from "{newSetPath.absolute().relative_to(rootDirectory)}".""")
        try:
            setSeries = pd.read_table(newSetPath, header=None)[0]
            newIDSet = set(setSeries.to_list())
        except EmptyDataError as err:
            _ = err
            newIDSet = set()
        if variableDataType.lower() == "numeric":
            newIDSet = set([ditchFloat(el) for el in newIDSet])  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            newIDSet = set([str(el) for el in newIDSet])
        elif variableDataType.lower() == "numeric_or_string":
            newIDSet = set([str(el) for el in newIDSet])
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise Exception(msg)
        logging.info(f"""    The size of this set is     {len(newIDSet):,}.""")

        # Set difference
        IDSetDiff = newIDSet.difference(oldIDSet)
        logging.info(f"""    The set difference size is  {len(IDSetDiff):,}.""")
        valuesToMap[variableName] = IDSetDiff

        # Save new subset to `setsToMapDataDir`
        fpath = setsToMapDataDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]}.JSON")
        with open(fpath, "w") as file:
            if variableDataType.lower() == "numeric":
                li = [ditchFloat(IDNumber) for IDNumber in IDSetDiff]  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                li = list(IDSetDiff)
            elif variableDataType.lower() == "numeric_or_string":
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
            elif variableDataType.lower() == "numeric_or_string":
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
            oldNumbersSet = set(oldMap.iloc[:, 1].values)
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
        variableName = FILE_NAME_TO_VARIABLE_NAME_DICT[file.stem]
        variableDataType = DATA_TYPES_DICT[variableName]
        logging.info(f"""  Working on un-mapped values for variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Map contents
        values = valuesToMap[variableName]
        if variableDataType.lower() == "numeric":
            values = set(int(float(value)) for value in values)  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        elif variableDataType.lower() == "numeric_or_string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise Exception(msg)
        numbers = sorted(list(newNumbersDict[variableName]))
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values,
                       IDName=variableName,
                       startFrom=numbers,
                       irbNumber=IRB_NUMBER,
                       suffix=deIdIDSuffix,
                       columnSuffix=variableName,
                       deIdentificationMapStyle="lemur",
                       logger=logging.getLogger())
        # Save map
        mapPath = runOutputDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
