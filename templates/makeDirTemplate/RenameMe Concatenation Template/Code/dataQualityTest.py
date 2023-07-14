"""
Iterates over the files that would be processed in the pipeline and runs quality tests on them. Currently the quality tests are

  1. Check for delimmeter issues. This is done by reading the whole file with `pd.read_csv`. Usually if there's an unexpected presence or absence of a delimmeter this will raise an error.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
"""

__all__ = ["runIntermediateDataDir"]

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import ParserError
# Local packages
from drapi.drapi import getTimestamp, make_dir_path
from common import BO_PORTION_DIR, BO_PORTION_FILE_CRITERIA

# Arguments
CHUNK_SIZE = 50000

# Arguments: General
LOG_LEVEL = "INFO"

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Arguments: Portion Paths and conditions
MAC_PATHS = [BO_PORTION_DIR]
WIN_PATHS = [BO_PORTION_DIR]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.absolute().parent.parent
IRBDir = projectDir.parent.parent  # Uncommon. TODO: Adjust directory depth/level as necessary
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
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    boPortionDir = BO_PORTION_DIR
    listOfPortionDirs = [boPortionDir]

# Directory creation: General
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

    # Data quality check
    logging.info("""Getting the set of values for each variable to de-identify.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.absolute().relative_to(IRBDir)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(IRBDir)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Read file
                logging.info("""    This file has met all conditions for testing.""")
                # Test 1: Make sure all lines have the same number of delimiters
                logging.info("""  ..  Test 1: Make sure all lines have the same number of delimiters.""")
                try:
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    logging.info("""  ..    There are no apparent problems reading this file.""")
                except ParserError as err:
                    args = err
                    logging.info("""  ..    This file raised an error: "{err}".""")
                # Test 2: ...
                pass
            else:
                logging.info("""    This file does not need to be tested.""")

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logging.info(f"""Finished collecting the set of ID values to de-identify. The set files are located in "{runOutputDir.relative_to(projectDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
