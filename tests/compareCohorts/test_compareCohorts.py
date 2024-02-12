"""
Compare two groups and any mapping between them.
"""

import logging
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.compareGroups import (compareGroups,
                                            determineMapType,
                                            determineMapTypeFromMap,
                                            mappingAnalysis)

# Arguments
pass

# Arguments: Meta-variables
TEST_DIR_DEPTH = 2
TEST_ROOT_DIR_DEPTH = TEST_DIR_DEPTH + 3

ROOT_DIRECTORY = "TEST_DIRECTORY"  # TODO One of the following:
# ["TEST_DIRECTORY",       # noqa
#  "TEST_ROOT_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), TEST_DIR_DEPTH)
testRootDir, _ = successiveParents(thisFilePath.absolute(), TEST_ROOT_DIR_DEPTH)
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

if ROOT_DIRECTORY == "TEST_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "TEST_ROOT_DIRECTORY":
    rootDirectory = testRootDir
else:
    raise Exception("An unexpected error occurred.")

# Directory creation: General
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
    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)

    # Define test cases
    testCases = []

    # Define test case: x2
    x2 = pd.Series([10,
                    20,
                    30,
                    40,
                    50,
                    50])

    # Define test case: 1:1
    x0 = pd.Series([1,
                    2,
                    3])
    m0 = pd.DataFrame([[1, 10],
                       [2, 20],
                       [3, 30]])
    x1 = pd.Series([10,
                    20,
                    30])

    testCases.append((x0, m0, x1, x2))

    # Define test case: 1:m
    x0 = pd.Series([1,
                    2,
                    3])
    m0 = pd.DataFrame([[1, 10],
                       [2, 20],
                       [3, 30]])
    x1 = pd.Series([10,
                    20,
                    30])

    testCases.append((x0, m0, x1, x2))

    # Define test case: m:1
    x0 = pd.Series([1,
                    2,
                    3])
    m0 = pd.DataFrame([[1, 10],
                       [2, 20],
                       [3, 30]])
    x1 = pd.Series([10,
                    20,
                    30])

    testCases.append((x0, m0, x1, x2))

    # Define test case: m:m
    x0 = pd.Series([1,
                    2,
                    3])
    m0 = pd.DataFrame([[1, 10],
                       [2, 20],
                       [3, 30]])
    x1 = pd.Series([10,
                    20,
                    30])

    testCases.append((x0, m0, x1, x2))

    # Mapping analysis
    for tu in testCases:
        x0, m0, x1, x2 = tu
        for tableType in [pd.DataFrame, pd.Series]:
            x0_tableTyped = tableType(x0)
            mappingAnalysis(x0=x0_tableTyped,
                            m0=m0,
                            logger=logger)
            x1_inner = pd.DataFrame(x0_tableTyped).set_index(0).join(other=m0.set_index(0),
                                                                     how="inner",
                                                                     lsuffix="_L",
                                                                     rsuffix="_R")
            x1_outer = pd.DataFrame(x0_tableTyped).set_index(0).join(other=m0.set_index(0),
                                                                     how="outer",
                                                                     lsuffix="_L",
                                                                     rsuffix="_R")
            mapType1 = determineMapType(x0=x0_tableTyped,
                                        x1=x1)
            mapType2 = determineMapType(x0=x0_tableTyped,
                                        x1=x1)
            mapType3 = determineMapTypeFromMap(x0=x0_tableTyped,
                                               m0=m0,
                                               logger=logger)
            logger.info(f"""The mapping of group1 (inner-joined) is of type "{mapType1}".""")
            logger.info(f"""The mapping of group1 (outer-joined) is of type "{mapType2}".""")
            logger.info(f"""The mapping of group1 (from `determineMapTypeFromMap`) is of type "{mapType3}".""")

            compareGroups(group1=x1,
                          group2=x2,
                          logger=logger)
            compareGroups(group1=x1_inner,
                          group2=x2,
                          logger=logger)
            compareGroups(group1=x1_outer,
                          group2=x2,
                          logger=logger)

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
