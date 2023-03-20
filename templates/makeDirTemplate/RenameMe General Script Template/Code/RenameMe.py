"""
This is a template Python script.
"""

import logging
import os
import sys
from pathlib import Path
# Third-party packages
import numpy as np
# import pandas as pd
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path

# Arguments
LOG_LEVEL = "DEBUG"
PATH_1_FOR_MAC = None
PATH_2_FOR_MAC = None
PATH_1_FOR_WINDOWS = None
PATH_2_FOR_WINDOWS = None
PATH_1_SET_MANUALLY = None
PATH_2_SET_MANUALLY = None
MAC_PATHS = [PATH_1_FOR_MAC,
             PATH_2_FOR_MAC]
WIN_PATHS = [PATH_1_FOR_WINDOWS,
             PATH_2_FOR_WINDOWS]

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
        runOutputDataDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

# Variables: Path construction: OS-specific
isAccessible = np.all([path.exists() for path in MAC_PATHS]) or np.all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        commonVariable1 = PATH_1_FOR_MAC
        commonVariable2 = PATH_2_FOR_MAC
    elif operatingSystem == "win32":
        commonVariable1 = PATH_1_FOR_WINDOWS
        commonVariable2 = PATH_2_FOR_WINDOWS
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    commonVariable1 = PATH_1_SET_MANUALLY
    commonVariable2 = PATH_2_SET_MANUALLY

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
make_dir_path(runIntermediateDataDir)
make_dir_path(runOutputDataDir)
make_dir_path(runLogsDir)

# Directory creation: Project-specific
pass


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
    logging.info(f"""All other paths will be reported in debugging relative to `projectDir`: "{projectDir}".""")

    # Script
    pass

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
