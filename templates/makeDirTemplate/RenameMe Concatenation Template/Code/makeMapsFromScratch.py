"""
Makes de-identification maps from scratch.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Needs to combine similar IDs, like different providers IDs.
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path, makeMap
from common import NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN

# Arguments
LOG_LEVEL = "DEBUG"

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

SETS_PATH = None

CHUNK_SIZE = 50000

IRB_NUMBER = "IRB202202436"

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
    # Imported from "getIDValues.py"

    # Map values
    for file in SETS_PATH.iterdir():
        variableName = file.stem
        logging.info(f"""  Working on variable "{variableName}" located at "{file.absolute().relative_to(IRBDir)}".""")
        # Read file
        try:
            df = pd.read_table(file, header=None)
        except EmptyDataError as err:
            _ = err
            df = pd.DataFrame()
        # Assert
        if df.shape[1] == 1:
            # Try to convert to integer-type
            try:
                df.iloc[:, 0] = df.iloc[:, 0].astype(int)
            except ValueError as err:
                _ = err
            # Check length differences
            len0 = len(df)
            values = set(df.iloc[:, 0].values)
            len1 = len(values)
            logging.info(f"""    The length of the ID array was reduced from {len0:,} to {len1:,} when removing duplicates.""")
        elif df.shape[1] == 0:
            pass
        # Map contents
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=1, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName)
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
