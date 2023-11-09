"""
This is a work in progress; a version of the i2b2 data download script in the style of DRAPI-lemur.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath
from i2b2_dump import get_IDs, i2b2_dump_main

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

# Variables: Other
pass

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Logging block
logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
logFormat = logging.Formatter(f"""[%(asctime)s]\n[%(levelname)s](%(funcName)s)\n{"-"*24}> %(message)s""")

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
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    print('START')
    #generate i2b2 patient IDs
    get_IDs()

	#i2b2 dump
    if (not os.path.exists(i2b2_dir)): #i2b2 dump will be saved in 'i2b2' subdirectory of 'data' folder.
        os.makedirs(i2b2_dir)
    i2b2_dump_main('GNV', 'patient_dimension', data_dir, i2b2_dir, cohort)  #Pull data from patient_dimension in GNV i2b2 instance.
    i2b2_dump_main('JAX', 'patient_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('GNV', 'visit_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('JAX', 'visit_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('GNV', 'observation_fact', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('JAX', 'observation_fact', data_dir, i2b2_dir, cohort)

	#prepare limited data set for disclosure
    if(not os.path.exists(map_dir)): #mappings for patient IDs and encounter IDs will be saved in 'mapping' subdirectory of 'data' folder.
        os.makedirs(map_dir)
    generate_mappings()
    if(not os.path.exists(disclosure_dir)): #limited data set of i2b2 dump will be saved in 'disclosure' directory.
        os.makedirs(disclosure_dir)
    limited_data_set()
    print('END')

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
