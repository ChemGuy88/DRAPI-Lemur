"""
Convert person ID column to patient key

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path
from hermanCode.idealist.idealist import idealistMap2dict
from common import OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN

# Arguments
LOG_LEVEL = "DEBUG"
COLUMNS_TO_CONVERT_DI = {"person_id": "PatientKey"}

MAC_PATHS = [OMOP_PORTION_DIR_MAC]
WIN_PATHS = [OMOP_PORTION_DIR_WIN]

NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
LIST_OF_PORTION_CONDITIONS = [OMOP_PORTION_FILE_CRITERIA]

PERSON_ID_MAP_PATH = Path("data/output/makePersonIDMap/.../person_id map.csv")  # TODO

CHUNK_SIZE = 50000

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

    # Load person ID map
    personIDMap = pd.read_csv(PERSON_ID_MAP_PATH)
    personIDMapDi = idealistMap2dict(personIDMap, "person_id", "patient_key")

    # Convert columns
    logging.info("""Getting the set of values for each variable to convert.""")
    # Create file parameters dictionary

    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.relative_to(IRBDir)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(IRBDir)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logging.info("""    File has met all conditions for processing.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        logging.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in COLUMNS_TO_CONVERT_DI.keys():
                            logging.info("""  ..  ..  Column must be converted. Converting values.""")
                            dfChunk[columnName] = dfChunk[columnName].apply(lambda IDNum: personIDMapDi[IDNum])
                            dfChunk = dfChunk.rename(columns={columnName: COLUMNS_TO_CONVERT_DI[columnName]})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logging.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(IRBDir)}".""")
            else:
                logging.info("""    This file does not need to be processed.""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(IRBDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
