"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
import re
from collections import OrderedDict
from pathlib import Path
# Third-party packages
import pandas as pd
import pprint
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    getPercentDifference,
                                    successiveParents,
                                    makeMap)
from drapi.constants.phiVariables import (VARIABLE_NAME_TO_FILE_NAME_DICT,
                                          FILE_NAME_TO_VARIABLE_NAME_DICT)
# Project parameters: General
from common import (IRB_NUMBER,
                    DATA_REQUEST_ROOT_DIRECTORY_DEPTH,
                    OLD_MAPS_DIR_PATH,
                    VARIABLE_ALIASES,
                    VARIABLE_SUFFIXES)

# Arguments
NEW_MAPS_DIR_PATH = Path(r"..\Concatenated Results\data\output\makeMapsFromOthers\...")  # TODO
DE_IDENTIFICATION_MAP_STYLE = "lemur"

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

    # Map new maps to variable names
    logging.info("""Mapping new maps to variable names.""")
    pattern = r"^([a-zA-Z_0-9\(\)# -]+) map"
    newMapsFileDict = {}
    for fpath in NEW_MAPS_DIR_PATH.iterdir():
        fname = fpath.stem
        obj = re.match(pattern, fname)
        if obj:
            extractedText = obj.groups()[0]
            variableName = FILE_NAME_TO_VARIABLE_NAME_DICT[extractedText]
        else:
            msg = "File name is of an unexpected format."
            logging.info(msg)
            raise Exception(msg)
        newMapsFileDict[variableName] = [fpath]
    logging.info("The list of variables extracted from the new maps:")
    for el in sorted(newMapsFileDict.keys()):
        logging.info(f"  {el}")

    # Match old and new maps by variable name
    logging.info("""Matching old and new maps by variable name.""")
    matchedMaps0 = {}
    MAPS_COLLECTION_DICT = {"Old Maps": OLD_MAPS_DIR_PATH,
                            "New Maps": newMapsFileDict}
    for mapCollectionName, mapCollection in MAPS_COLLECTION_DICT.items():
        logging.info(f"""  Working on map collection "{mapCollectionName}".""")
        for variableName, li in mapCollection.items():
            if variableName in VARIABLE_ALIASES.keys():
                variableLookUpName = VARIABLE_ALIASES[variableName]
            else:
                variableLookUpName = variableName
            if variableLookUpName in matchedMaps0.keys():
                matchedMaps0[variableLookUpName].extend(li)
            else:
                matchedMaps0[variableLookUpName] = li
    matchedMaps = OrderedDict()
    for key in sorted(matchedMaps0.keys()):
        matchedMaps[key] = matchedMaps0[key]
    text = pprint.pformat(matchedMaps, indent=4)
    logging.info(f"""  The old and new maps have been matched to the variable names. Aliases have been used:\n{text}""")

    # Load, concatenate, and save maps by variable names
    logging.info("""Loading, concatenating, and saving maps by variable names.""")
    concatenatedMapsDict = {}
    for variableName, li in matchedMaps.items():
        logging.info(f"""  Working on variable "{variableName}".""")
        concatenatedMap = pd.DataFrame()
        emptyMap = makeMap(IDset=set(),
                           IDName=variableName,
                           startFrom=1,
                           irbNumber=IRB_NUMBER,
                           suffix=VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"],
                           columnSuffix=variableName,
                           deIdentificationMapStyle=DE_IDENTIFICATION_MAP_STYLE,
                           logger=logging.getLogger())
        newColumns = emptyMap.columns
        for fpath in li:
            fpath = Path(fpath)
            logging.info(f"""    Working on map located at "{fpath.absolute().relative_to(rootDirectory)}".""")
            df = pd.read_csv(fpath)
            oldColumns = df.columns
            logging.info(f"""  ..  Over-writing map header format to "{DE_IDENTIFICATION_MAP_STYLE}".""")
            logging.info(f"""  ..  Old map columns: {oldColumns.to_list()}.""")
            logging.info(f"""  ..  New map columns: {newColumns.to_list()}.""")
            df.columns = newColumns
            concatenatedMap = pd.concat([concatenatedMap, df])
        concatenatedMapsDict[variableName] = concatenatedMap
        fpath = runOutputDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]} map.csv")
        concatenatedMap.to_csv(fpath, index=False)

    # Quality control
    results = {}
    for variableName, df in concatenatedMapsDict.items():
        uniqueIDs = len(df.iloc[:, 0].unique())
        numIDs = len(df)
        percentDifference = getPercentDifference(uniqueIDs, numIDs)
        results[variableName] = {"Unique IDs": uniqueIDs,
                                 "Total IDs": numIDs,
                                 "Percent Similarity": percentDifference}
    resultsdf = pd.DataFrame.from_dict(results, orient="index")
    logging.info(f"Concatenation summary:\n{resultsdf.to_string()}")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
