"""
Script for modifying clinical text TSV files so they can be handled by the SDOH pipeline. This is a parallelized implementation.
"""

import concurrent
import concurrent.futures
import logging
from pathlib import Path
# Third-party packages
import pandas as pd
# First-party packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.modifyTSV import wrapModify

# Arguments
CLINICAL_TEXT_DIR_1 = "../../../Data Request 2 - 2023-07-29/Intermediate Results/Notes Portion/data/output/freeText/2024-04-03 12-38-35/free_text/FlaDia_note"
CLINICAL_TEXT_DIR_2 = "../../../Data Request 2 - 2023-07-29/Intermediate Results/Notes Portion/data/output/freeText/2024-04-03 12-38-35/free_text/FlaDia_order_impression"
CLINICAL_TEXT_DIR_3 = "../../../Data Request 2 - 2023-07-29/Intermediate Results/Notes Portion/data/output/freeText/2024-04-03 12-38-35/free_text/FlaDia_order_narrative"
CLINICAL_TEXT_DIR_4 = "../../../Data Request 2 - 2023-07-29/Intermediate Results/Notes Portion/data/output/freeText/2024-04-03 12-38-35/free_text/FlaDia_order_result_comment"
ALL_CLINICAL_TEXT_DIRECTORIES = [CLINICAL_TEXT_DIR_1,
                                 CLINICAL_TEXT_DIR_2,
                                 CLINICAL_TEXT_DIR_3,
                                 CLINICAL_TEXT_DIR_4]


# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 3
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 1
IDR_DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 4

ROOT_DIRECTORY = "IRB_DIRECTORY"  # TODO One of the following:
# ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
#  "IRB_DIRECTORY",                 # noqa
#  "DATA_REQUEST_DIRECTORY",        # noqa
#  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    outputDataDir = dataDir.joinpath("output")
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

if ROOT_DIRECTORY == "PROJECT_OR_PORTION_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir
else:
    raise Exception("An unexpected error occurred.")

# Variables: Path construction: Project-specific
pass

# Variables: SQL Parameters
pass

# Variables: Other
pass

# Directory creation: General
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

if __name__ == "__main__":
    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:


    # Arguments
    ``: "{"..."}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)

    # Script
    # Initialize argument container for parallel wrapper
    allPaths0 = []
    allTypes0 = []
    allToDirectory = []
    allLogger = []
    for directory in ALL_CLINICAL_TEXT_DIRECTORIES:
        clinicalTextDirectory = Path(directory)
        for fpath in clinicalTextDirectory.iterdir():
            # Argument 1
            allPaths0.extend([fpath])
            # Argument 2
            if "note" in clinicalTextDirectory.name:
                allTypes0.extend(["note"])
            elif "order" in clinicalTextDirectory.name:
                allTypes0.extend(["order"])
            else:
                allTypes0.extend([None])
            # Argument 3
            allToDirectory.extend([runOutputDir])
            # Argument 4
            allLogger.extend([logger])


    df0 = pd.DataFrame()
    df0["All Paths"] = allPaths0
    df0["All Types"] = allTypes0
    select = ~df0.isna().any(axis=1)
    df = df0[select]
    logger.info(f"We dropped {sum(~select)} paths because of invalid clinical text types.")

    allPaths = df["All Paths"].to_list()
    allTypes = df["All Types"].to_list()
    message = f"Data for parallelization:\n{df.to_string()}"
    logger.info(message)

    with concurrent.futures.ProcessPoolExecutor() as pool:
        results = zip(*pool.map(wrapModify, allPaths,
                                            allTypes,
                                            allToDirectory,
                                            allLogger))

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
