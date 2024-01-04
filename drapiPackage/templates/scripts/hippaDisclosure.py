"""
HIPPA disclosure template  # TODO
"""

import datetime as dt
import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath

# Arguments: Script-specific
# Enter full path to the file with MRNs
FILE_PATH_STRING = "data/output"
file_path = Path(FILE_PATH_STRING)
# Enter file name. The file should be within `file_path`
FILE_NAME_STRING = "MRNs.csv"
file = Path(FILE_NAME_STRING)
# Enter the column name that contains MRNs
column = 'MRN_JAX'
# Enter GNV or JAX to denote whether MRNs are GNV or JAX
site = 'JAX'
# Enter IRB number
irb = 'IRB202202467'
# Enter the PI name
PI_name = 'Jiang Bian'
# Enter PI email
PI_email = 'bianjiang@ufl.edu'
# Analyst
analyst = 'Herman Autore'
# Analyst initials
ANALYST_INITIALS = "HA"
# Analyst email
analyst_email = 'haut0001@shands.ufl.edu'
# Analyst username
analyst_username = 'haut0001'
# Output file prefix
out = f"{ANALYST_INITIALS}_{irb}_{site}_"
# HIPPA directory
hipaa_dir = Path(r'\\shandsdfs.shands.ufl.edu\FILES\SHARE\DSS\IDR Data Requests\HIPAA_Disclosure_files')

# Arguments: General
PROJECT_DIR_DEPTH = 2
IRB_DIR_DEPTH = 2
IDR_DATA_REQUEST_DIR_DEPTH = 5

LOG_LEVEL = "DEBUG"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)

# Directory creation: General
makeDirPath(runLogsDir)


def left_padding(str1):
    """
    Pads a numeric string with leading 0s up to a length of eight (8).
    """
    while (len(str1) < 8):
        str1 = '0' + str1
    return str1


def hipaa_disclosure():
    today = dt.date.today()
    hipaa_disclosure_date_field = today.strftime("%m%d%Y")
    if (site == 'GNV'):
        hipaa_disclosure_header = ['H', analyst_username, analyst_email, irb, '102', 'RE', analyst, hipaa_disclosure_date_field, 'ALL', 'N', ' ', PI_name, '', '', '', '', '', '', '', '', PI_email]
    elif (site == 'JAX'):
        hipaa_disclosure_header = ['H', analyst_username, analyst_email, irb, '998', 'RE', analyst, hipaa_disclosure_date_field, 'ALL', 'N', ' ', PI_name, '', '', '', '', '', '', '', '', PI_email]
    fpath = os.path.join(file_path, file)
    logging.debug(fpath)
    mrns = pd.read_csv(fpath)
    mrns = mrns[[column]].drop_duplicates()
    mrns[column] = mrns[column].fillna(0)
    mrns = mrns[mrns[column] != 0]
    mrns[column] = mrns[column].astype(int)
    mrns[column] = mrns[column].astype(str)
    if (site == 'JAX'):
        mrns[column] = mrns.apply(lambda row: left_padding(row[column]), axis=1)
    mrns = mrns[column].tolist()
    hipaa_disclosure_df = pd.DataFrame(columns=hipaa_disclosure_header)
    hipaa_disclosure_df[hipaa_disclosure_df.columns[1]] = mrns
    hipaa_disclosure_df[hipaa_disclosure_df.columns[0]] = "M"
    hipaa_file = out + str(today) + '.csv'
    hipaa_disclosure_df.to_csv(os.path.join(file_path, hipaa_file), index=False)
    return


if __name__ == '__main__':
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
    hipaa_disclosure()

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
