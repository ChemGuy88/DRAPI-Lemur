"""
Define and query cohort
"""

import logging
import os
from pathlib import Path
# Third-party libraries
import numpy as np
import pandas as pd
# Local libraries
from hermanCode.hermanCode import replace_sql_query, getTimestamp, make_dir_path, makeChunks
from hermanCode.idealist.getMap import patientMapDf

# Arguments
LOG_LEVEL = "DEBUG"
COHORT_STEP_1_FILE_NAME = "cohortStep1.sql"
COHORT_STEP_2_FILE_NAME = "cohortStep2.sql"

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.parent.parent
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

# Variables: SQL
uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Directory creation
make_dir_path(runLogsDir)
make_dir_path(runOutputDir)

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

# Test connection
test_query = """SELECT 1;"""
test_result = pd.read_sql(test_query, con=conStr)
if test_result.iloc[0, 0] == 1:
    logging.debug("""Connection test was a success.""")
else:
    logging.debug("""Failed connection test.""")

# Script Core
query = """SELECT * FROM INFORMATION_SCHEMA.COLUMNS"""
df = pd.read_sql(query, con=conStr)

logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
