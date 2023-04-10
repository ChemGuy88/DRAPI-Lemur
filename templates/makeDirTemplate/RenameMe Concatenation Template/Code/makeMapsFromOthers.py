"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# NOTE Expects integer IDs, so no string IDs like Epic Patient IDs.
# TODO Needs to combine similar IDs, like different providers IDs.
"""

import json
import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path, makeMap, makeSetComplement, ditchFloat
from common import NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, COLUMNS_TO_DE_IDENTIFY, OLD_MAPS_DIR_PATH

# Arguments
SETS_PATH = Path("data/output/getIDValues/...")  # TODO

CHUNK_SIZE = 50000

IRB_NUMBER = None  # TODO

VARIABLE_SUFFIXES = {"AuthoringProviderKey": {"columnSuffix": "provider",
                                              "deIdIDSuffix": "PROV"},
                     "AuthorizingProviderKey": {"columnSuffix": "provider",
                                                "deIdIDSuffix": "PROV"},
                     "CosignProviderKey": {"columnSuffix": "provider",
                                           "deIdIDSuffix": "PROV"},
                     "EncounterCSN": {"columnSuffix": "encounter",
                                      "deIdIDSuffix": "ENC"},
                     "EncounterKey": {"columnSuffix": "encounter",
                                      "deIdIDSuffix": "ENC"},
                     "MRN_GNV": {"columnSuffix": "patient",
                                 "deIdIDSuffix": "PAT"},
                     "MRN_JAX": {"columnSuffix": "patient",
                                 "deIdIDSuffix": "PAT"},
                     "NoteID": {"columnSuffix": "note",
                                "deIdIDSuffix": "NOTE"},  # ?
                     "NoteKey": {"columnSuffix": "note",
                                 "deIdIDSuffix": "NOTE"},  # ?
                     "OrderID": {"columnSuffix": "order",
                                 "deIdIDSuffix": "ORD"},  # ?
                     "OrderKey": {"columnSuffix": "order",
                                  "deIdIDSuffix": "ORD"},  # ?
                     "PatientKey": {"columnSuffix": "patient",
                                    "deIdIDSuffix": "PAT"},
                     "ProviderKey": {"columnSuffix": "provider",
                                     "deIdIDSuffix": "PROV"},
                     "location_id": {"columnSuffix": "location",
                                     "deIdIDSuffix": "LOC"},
                     "person_id": {"columnSuffix": "patient",
                                   "deIdIDSuffix": "PAT"},
                     "preceding_visit_occurrence_id": {"columnSuffix": "encounter",
                                                       "deIdIDSuffix": "ENC"},
                     "provider_id": {"columnSuffix": "provider",
                                     "deIdIDSuffix": "PROV"},
                     "visit_occurrence_id": {"columnSuffix": "encounter",
                                             "deIdIDSuffix": "ENC"}}

MAC_PATHS = [NOTES_PORTION_DIR_MAC,
             OMOP_PORTION_DIR_MAC]
WIN_PATHS = [NOTES_PORTION_DIR_WIN,
             OMOP_PORTION_DIR_WIN]

NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]

LIST_OF_PORTION_CONDITIONS = [NOTES_PORTION_FILE_CRITERIA,
                              OMOP_PORTION_FILE_CRITERIA]

LOG_LEVEL = "DEBUG"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.absolute().parent.parent
IRBDir = projectDir.parent  # Uncommon
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

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        notesPortionDir = NOTES_PORTION_DIR_MAC
        omopPortionDir = OMOP_PORTION_DIR_MAC
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        notesPortionDir = NOTES_PORTION_DIR_WIN
        omopPortionDir = OMOP_PORTION_DIR_WIN
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    notesPortionDir = None
    omopPortionDir = None

# Directory creation: General
make_dir_path(runIntermediateDataDir)
make_dir_path(runOutputDir)
make_dir_path(runLogsDir)

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
    logging.info(f"""All other paths will be reported in debugging relative to `IRBDir`: "{IRBDir}".""")

    # Get set of values
    # NOTE The code that used to be in this section was moved to "getIDValues.py"
    getIDValuesOutput = SETS_PATH
    logging.debug(f"""Using the set of new values in the directory "{getIDValuesOutput.absolute().relative_to(IRBDir)}".""")

    # Concatenate all old maps
    oldMaps = {}
    logging.debug("""Concatenating all similar pre-existing maps.""")
    for variableName in COLUMNS_TO_DE_IDENTIFY:
        logging.debug(f"""  Working on variable "{variableName}".""")
        if variableName in OLD_MAPS_DIR_PATH.keys():
            logging.debug("""    Variable has pre-existing map(s).""")
            listOfMapPaths = OLD_MAPS_DIR_PATH[variableName]
            dfConcat = pd.DataFrame()
            for mapPath in listOfMapPaths:
                logging.debug(f"""  ..  Reading pre-existing map from "{mapPath}".""")
                df = pd.DataFrame(pd.read_csv(mapPath))
                dfConcat = pd.concat([dfConcat, df])
            oldMaps[variableName] = dfConcat
        elif variableName not in OLD_MAPS_DIR_PATH.keys():
            logging.debug("""    Variable has no pre-existing map.""")
            oldMaps[variableName] = pd.DataFrame()

    # Get the set difference between all old maps and the set of un-mapped values
    valuesToMap = {}
    setsToMapDataDir = runIntermediateDataDir.joinpath("valuesToMap")
    make_dir_path(setsToMapDataDir)
    logging.debug("""Getting the set difference between all old maps and the set of un-mapped values.""")
    for variableName in COLUMNS_TO_DE_IDENTIFY:
        logging.debug(f"""  Working on variable "{variableName}".""")

        # Get old set of IDs
        logging.debug("""    Getting the old set of IDs.""")
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldIDSet = set(oldMap[variableName].values)
            oldIDSet = set([ditchFloat(el) for el in oldIDSet])  # NOTE: Hack. Convert values to type int or string
        elif len(oldMap) == 0:
            oldIDSet = set()
        logging.debug(f"""    The size of this set is {len(oldIDSet):,}.""")

        # Get new set of IDs
        newSetPath = getIDValuesOutput.joinpath(f"{variableName}.txt")
        logging.debug(f"""    Getting the new set of IDs from "{newSetPath.absolute().relative_to(IRBDir)}".""")
        newIDSet = set()
        with open(newSetPath, "r") as file:
            text = file.read()
            lines = text.split()
        for line in lines:
            newIDSet.add(line)
        newIDSet = set([ditchFloat(el) for el in newIDSet])  # NOTE: Hack. Convert values to type int or string
        logging.debug(f"""    The size of this set is {len(newIDSet):,}.""")

        # Set difference
        IDSetDiff = newIDSet.difference(oldIDSet)
        valuesToMap[variableName] = IDSetDiff

        # Save new subset to `setsToMapDataDir`
        fpath = setsToMapDataDir.joinpath(f"{variableName}.JSON")
        with open(fpath, "w") as file:
            li = [ditchFloat(IDNumber) for IDNumber in IDSetDiff]  # NOTE: Hack. Convert values to type int or string
            file.write(json.dumps(li))
        if len(IDSetDiff) == 0:
            series = pd.Series(dtype=int)
        else:
            series = pd.Series(sorted(list(IDSetDiff)))

    # Get numbers for new map
    logging.debug("""Getting numbers for new map.""")
    newNumbersDict = {}
    for variableName in COLUMNS_TO_DE_IDENTIFY:
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
    logging.debug("""Mapping un-mapped values.""")
    for file in setsToMapDataDir.iterdir():
        variableName = file.stem
        logging.info(f"""  Working on un-mapped values for variable "{variableName}" located at "{file.absolute().relative_to(IRBDir)}".""")
        # Map contents
        values = valuesToMap[variableName]
        values = set(int(float(value)) for value in values)  # NOTE: Hack. Convert values to type int or string
        numbers = sorted(list(newNumbersDict[variableName]))
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=numbers, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName)
        # Save map
        mapPath = runOutputDir.joinpath(f"{variableName} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(IRBDir)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(IRBDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
