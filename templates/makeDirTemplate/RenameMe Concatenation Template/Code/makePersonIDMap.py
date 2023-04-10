"""
Convert OMOP person IDs to IDR patient keys.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path, personIDs2patientKeys
from common import OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN

# Arguments
LOG_LEVEL = "DEBUG"

COLUMNS_TO_CONVERT = ["person_id"]

MAC_PATHS = [OMOP_PORTION_DIR_MAC]
WIN_PATHS = [OMOP_PORTION_DIR_WIN]

NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]

LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA]

SETS_PATH = None

CHUNK_SIZE = 50000

IRB_NUMBER = None  # TODO

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
        omopPortionDir = OMOP_PORTION_DIR_MAC
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
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
    if SETS_PATH:
        logging.info(f"""Using the set of values previously collected from "{SETS_PATH}".""")
    else:
        logging.info("""Getting the set of values for each variable to convert.""")
        columnSetsVarsDi = {columnName: {"fpath": runIntermediateDataDir.joinpath(f"{columnName}.txt"),
                                         "fileMode": "w"} for columnName in COLUMNS_TO_CONVERT}
        for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
            # Act on directory
            logging.info(f"""Working on directory "{directory.relative_to(IRBDir)}".""")
            for file in directory.iterdir():
                logging.info(f"""  Working on file "{file.absolute().relative_to(IRBDir)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logging.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logging.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_CONVERT:
                                logging.info("""  ..  ..  Column must be converted. Collecting values.""")
                                valuesSet = sorted(list(set(dfChunk[columnName].dropna().values)))
                                columnSetFpath = columnSetsVarsDi[columnName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[columnName]["fileMode"]
                                with open(columnSetFpath, columnSetFileMode) as file:
                                    for value in valuesSet:
                                        file.write(str(value))
                                        file.write("\n")
                                columnSetsVarsDi[columnName]["fileMode"] = "a"
                                logging.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(IRBDir)}" in the project directory.""")
                else:
                    logging.info("""    This file does not need to be processed.""")

    # Map values
    if SETS_PATH:
        setsPathDir = SETS_PATH
    else:
        setsPathDir = runIntermediateDataDir
    for file in setsPathDir.iterdir():
        columnName = file.stem
        logging.info(f"""  Working on variable "{columnName}" located at "{file.absolute().relative_to(IRBDir)}".""")
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
        map_ = personIDs2patientKeys(list(values))
        # Save map
        mapPath = runOutputDir.joinpath(f"{columnName} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    PersonID-to-PatientKey map saved to "{mapPath.absolute().relative_to(IRBDir)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(IRBDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
