"""
This is a template Python script.
"""

import logging
import os
import sys
from contextlib import redirect_stderr
from pathlib import Path
# Third-party packages
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path

# Arguments
LOG_LEVEL = "DEBUG"
PATH_FOR_MAC = None  # TODO
PATH_FOR_WINDOWS = None  # TODO
PATH_SET_MANUALLY = None  # TODO

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

# Variables: Path construction: OS-specific
isAccessible = Path(PATH_FOR_MAC).exists or Path(PATH_FOR_WINDOWS).exists
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        commonVariable = PATH_FOR_MAC
    elif operatingSystem == "win32":
        commonVariable = PATH_FOR_WINDOWS
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    commonVariable = PATH_SET_MANUALLY

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
make_dir_path(runLogsDir)
make_dir_path(runOutputDir)

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

    # Logging block: Context manager
    with open(logpath) as file:
        with redirect_stderr(file):
            pass

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
