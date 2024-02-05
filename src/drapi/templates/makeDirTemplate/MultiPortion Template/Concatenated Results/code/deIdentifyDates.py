"""
Shifts the dates in a data set according to the date shift map for a patient.
"""

import logging
import os
import sys
import datetime
from pathlib import Path
import re
from typing import Union
# Third-party packages
import pandas as pd
from pandas.errors import OutOfBoundsDatetime
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    makeMap,
                                    map2di,
                                    successiveParents)
# Local packages: Script parameters: General
from drapi.constants.phiVariables import (LIST_OF_PHI_DATES_BO,
                                          LIST_OF_PHI_DATES_NOTES,
                                          LIST_OF_PHI_DATES_OMOP)
# Local packages: Script parameters: General
from common import IRB_NUMBER
# Local packages: Script parameters: Paths
# Local packages: Script parameters: File criteria
from common import BO_PORTION_FILE_CRITERIA

# Arguments
"""
Argument descriptions
`PATIENT_DATE_SHIFT_MAP`:                   A Path object. This is the file path of the date-shift map. It expects a four-columned CSV file.
`LOOK_UP_NAME_MAP_INDEX`:                   An integer. Assuming a typical IDR de-identification map format, `0`` is for the identified, original ID name, and `2` is for the de-identified variable name.
`LOOK_UP_NAME_DE_IDENTIFICATION_FORMAT`:    A string. This is required if `LOOK_UP_NAME_MAP_INDEX` is `2`. Options are "lemur" or "classic"
`LIST_OF_PHI_DATES`:                        A list of strings. This list the column headers (i.e., variable names) that need to have their dates de-identified (i.e., date-shifted).

`USE_MODIFIED_OMOP_DATA_SET`:               A boolean. This indicates which version of the OMOP data set to use, the original or the one that has had its columns converted. These versions are defined by their directory locations in `OMOP_PORTION_DIR_*` and `MODIFIED_OMOP_PORTION_DIR_*`, where `*` is `MAC` or `WIN`.
`MAC_PATHS`:                                A list of Path objects. The Path objects point to the directories that should be processed.
`WIN_PATHS`:                                A list of Path objects. The Path objects point to the directories that should be processed.
`LIST_OF_PORTION_CONDITIONS`:               A list of functions. All these fucntions are evaluated on each of the files in each of the directories defined by `*_PATHS`.
"""
PATIENT_DATE_SHIFT_MAP = Path(r"..\Concatenated Results\data\output\makeDateShiftMap\...\Date Shift Map.CSV")
LOOK_UP_NAME_MAP_INDEX = 2
LOOK_UP_NAME_DE_IDENTIFICATION_FORMAT = "lemur"
LIST_OF_PHI_DATES = LIST_OF_PHI_DATES_BO + LIST_OF_PHI_DATES_NOTES + LIST_OF_PHI_DATES_OMOP

# Arguments: Portion Paths and conditions
MAC_PATHS = [Path(r"..\Concatenated Results\data\output\deIdentify\2023-12-13 13-58-38")]
WIN_PATHS = [Path(r"..\Concatenated Results\data\output\deIdentify\2023-12-13 13-58-38")]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA]

# Arguments; General
CHUNK_SIZE = 50000

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
    print("Not implemented. Check settings in your script.")
    sys.exit()

# Variables: Path construction: Project-specific
pass

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

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
    `PATIENT_DATE_SHIFT_MAP`: "{PATIENT_DATE_SHIFT_MAP}"
    `MAC_PATHS`: "{MAC_PATHS}"
    `WIN_PATHS`: "{WIN_PATHS}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    # Load de-identification maps for dates, i.e., the date shift maps.
    logger.info("""Loading de-identification maps for dates.""")
    map_ = pd.read_csv(PATIENT_DATE_SHIFT_MAP)
    dateShiftMapDi = map2di(map_, fromColumnIndex=LOOK_UP_NAME_MAP_INDEX, toColumnIndex=3)
    lookUpNameOriginal = map_.columns[0]
    lookUpNameSelected = map_.columns[LOOK_UP_NAME_MAP_INDEX]

    # Create alias reverse look-up dictionary
    from common import VARIABLE_ALIASES
    reverseAliasLookup = {}
    for alias, mainName in VARIABLE_ALIASES.items():
        if mainName in reverseAliasLookup.keys():
            reverseAliasLookup[mainName].append(alias)
        else:
            reverseAliasLookup[mainName] = [alias]

    # Synthesize alias names. If we are looking for the original variable name, these are unchaged, but if we are looking for de-identified variable names, we must syntheisze the names.
    if LOOK_UP_NAME_MAP_INDEX == 0:
        pass
    elif LOOK_UP_NAME_MAP_INDEX == 2:
        listOfLookUpNameAliases = []
        for alias in reverseAliasLookup[lookUpNameOriginal]:
            df = makeMap(IDset={},
                         IDName="PatientKey",
                         startFrom=1,
                         irbNumber=IRB_NUMBER,
                         suffix="",
                         columnSuffix="",
                         logger=logger)
            lookUpNameAlias = df.columns[-1]
            listOfLookUpNameAliases.append(lookUpNameAlias)
    else:
        msg = """Invalid value for `LOOK_UP_NAME_MAP_INDEX`. See script arguments."""
        logger.error(msg)
        raise Exception(msg)

    def string2datetime(string: str) -> Union[datetime.datetime, pd.Timestamp]:
        """
        Attempts to convert a string to a pandas datetime object. If it's out of range it converts it to a Python datetime object.

        The Python datetime conversion works as follows:
        Using regex it detects if the string is one of the following formats:
            - Date and time with seconds-precision
            - Date and time with minutes-precision
            - Date
        NOTE: Additional formats can be implemented by adding the corresponding regular expression and `strptime` call combination.
        """
        try:
            newValue = pd.to_datetime(string)
        except OutOfBoundsDatetime as err:
            _ = err
            pattern1 = r"(?P<newValue>\d+[\/-]\d+[\/-]\d+\W+\d+:\d+:\d+)"   # Second-precision
            pattern2 = r"(?P<newValue>\d+[\/-]\d+[\/-]\d+\W+\d+:\d+)"  # Minutes-precision
            pattern3 = r"(?P<newValue>\d+[\/-]\d+[\/-]\d)"  # Days-precision
            reObj1 = re.match(pattern1, string)
            reObj2 = re.match(pattern2, string)
            reObj3 = re.match(pattern3, string)
            if reObj1:
                newValue = datetime.datetime.strptime(string, "%m/%d/%Y %H:%M:%S")
            elif reObj2:
                newValue = datetime.datetime.strptime(string, "%m/%d/%Y %H:%M")
            elif reObj3:
                newValue = datetime.datetime.strptime(string, "%m/%d/%Y")
        return newValue

    def datetimeOffset(timeObj: Union[datetime.datetime, pd.Timestamp], offset: int):
        """
        `offset`, an int, is the number of days.
        """
        if (pd.Timestamp.min < timeObj < pd.Timestamp.max):
            newValue = timeObj + pd.DateOffset(offset)
        else:
            newValue = timeObj + datetime.timedelta(days=offset)
        return newValue

    logger.info("""De-identifying files.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logger.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logger.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logger.info("""    File has met all conditions for processing.""")
                logger.info("""  ..  Reading file to count the number of chunks.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                logger.info(f"""  ..  This file has {numChunks} chunks.""")
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    # Work on chunk
                    logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        logger.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in LIST_OF_PHI_DATES:
                            logger.info("""  ..  ..  Column must be de-identified. Date-shifting values.""")
                            if lookUpNameSelected in dfChunk.columns:
                                lookUpName = lookUpNameSelected
                            elif any([alias in dfChunk.columns for alias in listOfLookUpNameAliases]):
                                for alias in listOfLookUpNameAliases:
                                    if alias in dfChunk.columns:
                                        break
                                lookUpName = alias
                            else:
                                msg = f"""The variable used to look up the date shift offset was not found. We searched for "{lookUpNameSelected}" and any of its aliases: {'", "'.join(listOfLookUpNameAliases)}"""
                                logger.error(msg)
                                raise Exception(msg)
                            dateShiftValues = dfChunk[lookUpName].apply(lambda lookUpID: dateShiftMapDi[lookUpID])
                            column = dfChunk[columnName].apply(string2datetime)
                            df = pd.concat([column, dateShiftValues], axis=1)
                            series = df.apply(lambda el: (el[columnName], el[lookUpName]), axis=1)
                            dfChunk[columnName] = series.apply(lambda tu: datetimeOffset(timeObj=tu[0], offset=tu[1]))
                            dfChunk = dfChunk.rename(columns={columnName: f"De-identified {columnName}"})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logger.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logger.info("""    This file does not need to be processed.""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
