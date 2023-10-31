"""
Test the `makeMap` function from DRAPI
"""

import json
import logging
import os
from logging import Logger
from pathlib import Path
from typing import Union
from typing_extensions import Literal
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath, mapGroupCriteria4unknownValue, sortIntegersAndStrings

# Arguments
_ = None

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = DATA_REQUEST_DIR_DEPTH + 0
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "IRB_DIRECTORY"  # TODO One of the following:
                                                 # ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
                                                 #  "IRB_DIRECTORY",                 # noqa
                                                 #  "DATA_REQUEST_DIRECTORY",        # noqa
                                                 #  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
IRBDir, _ = successiveParents(thisFilePath, IRB_DIR_DEPTH)
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
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"
connection = create_engine(conStr).connect().execution_options(stream_results=True)

# Variables: Other
pass

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Logging block
logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
logFormat = logging.Formatter(f"""[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s""")

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
    ``: "{""}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    #

    def makeMap2(IDset: set,
                IDName: str,
                startFrom: Union[int, list],
                irbNumber: str,
                suffix: str,
                columnSuffix: str,
                logger: Logger,
                groups: dict = {0: {"criteria": [mapGroupCriteria4unknownValue],
                                    "deidNum": 0}},
                deIdentificationMapStyle: Literal["classic", "lemur"] = "lemur") -> pd.DataFrame:
        """
        Makes an IDR de-identification map.

        INPUT
            `IDset`, a set of IDs
            `IDName`, the name of the ID
            `startFrom`, the integer number to start from
            `groups`, ID values to group or map in a many-to-one fashion. E.g., invalid IDs (negative numbers) are usually all mapped to the same de-identified number, like "0".
            `deIdentificationMapStyle`, a string, one of {"classic, "lemur"}. The formats are as follow:
                | Format Style  | de-Identififed ID Column Header   |
                | ------------- | -------------------------------   |
                | "clasic"      | `f"deid_{columnSuffix}_id"`       |
                | "lemur"       | `f"de-Identified {IDName}"`       |

        OUTPUT
            `map_`, a Pandas DataFrame with the following format:
            | `IDName` | deid_num   | de-Identififed ID Column Header |
            | -------- | --------   | ------------------------ |
            | IDset[0] | numbers[0] | ... |
            | ...      | ...        | ... |
        """
        # Assign header formats: de-Identififed ID Column Header
        if deIdentificationMapStyle == "classic":
            deIdentificationSerialNumberHeader = "deid_num"
        elif deIdentificationMapStyle == "lemur":
            deIdentificationSerialNumberHeader = "De-identification Serial Number"
        # Assign header formats: de-Identififed ID Column Header
        if deIdentificationMapStyle == "classic":
            deIdentifiedIDColumnHeader = f"deid_{columnSuffix}_id"
        elif deIdentificationMapStyle == "lemur":
            deIdentifiedIDColumnHeader = f"De-identified {IDName}"

        if len(IDset) == 0:
            return pd.DataFrame(columns=[IDName,
                                        deIdentificationSerialNumberHeader,
                                        deIdentifiedIDColumnHeader])
        else:
            pass
        if isinstance(startFrom, int):
            startFrom = startFrom
            numbers = list(range(startFrom, startFrom + len(IDset)))
        elif isinstance(startFrom, list):
            numbers = startFrom[:]
            startFrom = numbers[0]
        numbers.extend([None])
        logger.info("    Sorting `IDset`.")
        IDli = sortIntegersAndStrings(list(IDset))
        logger.info("    Sorting `IDset` - done.")
        logger.info("    Creating `mapDi`.")
        mapDi = {IDNum: {} for IDNum in IDli}
        logger.info("    Creating `mapDi` - done.")
        lenIDli = len(IDli)
        if lenIDli > 100000:
            itChunk = 1000
        else:
            itChunk = round(lenIDli/50)
        IDseries = pd.Series(IDli)
        IDseries.index = range(1, lenIDli+1)
        newMap = IDseries.apply(assignDeIdentificationNumber)
        for it, IDNum in enumerate(IDli, start=1):
            fromGroup = False
            for group, groupAttributes in groups.items():
                criteriaList = groupAttributes["criteria"]
                criteria = [criterion(IDNum) for criterion in criteriaList]
                if all(criteria):
                    deid_num = groupAttributes["deidNum"]
                    fromGroup = True
                    break
            if fromGroup:
                pass
            else:
                deid_num = numbers.pop(0)
            deid_id = f"{irbNumber}_{suffix}_{deid_num}"
            mapDi[IDNum] = {IDName: IDNum,
                            deIdentificationSerialNumberHeader: deid_num,
                            deIdentifiedIDColumnHeader: deid_id}
            if it % itChunk == 0:
                logger.info(f"  ..  Working on item {it:,} of {len(IDli):,} ({it/lenIDli:.2%} done).")
        newMap = pd.DataFrame.from_dict(mapDi, orient="index")
        newMap.index = range(1, len(newMap) + 1)
        return newMap
    
    def assignDeIdentificationNumber(IDNum: Union[str, int],
                                     groups: dict,
                                     IDName: str) -> str:
        pass


    with open(r"data\intermediate\makeMapsFromOthers\2023-10-25 15-39-24\valuesToMap\NoteID.JSON", "r") as file:
        values = json.load(file)

    m = makeMap2(IDset=values, IDName="testVar", startFrom=list(range(len(values))), irbNumber="TEST_IRB", suffix="_T", columnSuffix="_TT", deIdentificationMapStyle="lemur", logger=logger)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")


