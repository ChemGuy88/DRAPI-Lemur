"""
Processes the notes text TSV files in preparation for processing by the SDOH pipeline.
"""

import argparse
import logging
import os
import pprint
from pathlib import Path
from typing import Union
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath

# Arguments
_ = None

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = 4
IRB_DIR_DEPTH = 4
IDR_DATA_REQUEST_DIR_DEPTH = 6

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

# Functions

def modifyTSV(fpath: Union[str, Path]):
    """
    Modifies notes text TSV files in preparation for analysis in the SDOH pipeline.
    Modifications:
        - Adds two dummy columns
        - Re-orders the columns
        - Renames the `OrderKey` column to "ordr_proc_key"
    """
    # Read file
    df = pd.read_csv(fpath, delimiter="\t")

    # Set dummy values
    df["CNTCT_NUM"] = 0
    df["NOTE_KEY"] = 123456789

    # Re-order columns
    df = df[["LinkageNoteID",
             "NOTE_KEY",
             "CNTCT_NUM",
             "note_text"]]
    
    # Rename columns
    df = df.rename(columns={"LinkageNoteID": "NOTE_ENCNTR_KEY"})

    # Save modified TSV file
    fname = fpath.name
    savePath = runOutputDir.joinpath(fname)
    df.to_csv(savePath, index=False, sep="\t")


if __name__ == "__main__":
    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory.absolute()}".""")

    # Parse arguments
    parser = argparse.ArgumentParser(description="Configure")

    parser.add_argument("--verbosity",
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""",
                        type=int,
                        default=10)

    parser.add_argument("fpath",
                        help="The path(s) to the TSV file(s).",
                        type=str,
                        nargs="+")

    args = parser.parse_args()

    fpathli = args.fpath
    verbosity = args.verbosity

    argsDict = vars(args)

    # Log arguments
    argumentsText = pprint.pformat(argsDict)
    logger.info(f"""Script arguments:

    # Arguments: Command-line arguments
    {argumentsText}

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)

    # Execute commands
    logger.setLevel(verbosity)
    for fpath in fpathli:
        fpath = Path(fpath)
        logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
        # modifyTSV(fpath)

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
