"""
QA: Make sure values were correctly converted.
"""

import argparse
import logging
import os
import pprint
from pathlib import Path
# Third-party packages
import pandas as pd
# First-party packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)
from drapi.code.drapi.qa.columnConversion import spotCheckColumns


# Functions


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--Encounter_ID_1",
                        default="visit_occurrence_id",
                        type=str,
                        choices=["visit_occurrence_id"],
                        help="")
    parser.add_argument("--Encounter_ID_2",
                        default="Encounter # (CSN)",
                        type=str,
                        choices=["Encounter # (CSN)"],
                        help="")
    parser.add_argument("--Patient_ID_1",
                        default="person_id",
                        type=str,
                        choices=["person_id"],
                        help="")
    parser.add_argument("--Patient_ID_2",
                        default="Patient Key",
                        type=str,
                        choices=["Patient Key",
                                 "PatientKey"],
                        help="")
    parser.add_argument("--Provider_ID_1",
                        default="provider_id",
                        type=str,
                        choices=["provider_id"],
                        help="")
    parser.add_argument("--Provider_ID_2",
                        default="Provider Key",
                        type=str,
                        choices=["Provider Key"],
                        help="")

    # Arguments: General
    parser.add_argument("--CHUNKSIZE",
                        default=50000,
                        type=int,
                        help="The number of rows to read at a time from the CSV using Pandas `chunksize`")
    parser.add_argument("--MESSAGE_MODULO_CHUNKS",
                        default=50,
                        type=int,
                        help="How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_CHUNKS`")
    parser.add_argument("--MESSAGE_MODULO_FILES",
                        default=100,
                        type=int,
                        help="How often to print a log message, i.e., print a message every x number of chunks, where x is `MESSAGE_MODULO_FILES`")

    # Arguments: Meta-variables
    parser.add_argument("--PROJECT_DIR_DEPTH",
                        default=2,
                        type=int,
                        help="")
    parser.add_argument("--DATA_REQUEST_DIR_DEPTH",
                        default=4,
                        type=int,
                        help="")
    parser.add_argument("--IRB_DIR_DEPTH",
                        default=3,
                        type=int,
                        help="")
    parser.add_argument("--IDR_DATA_REQUEST_DIR_DEPTH",
                        default=6,
                        type=int,
                        help="")
    parser.add_argument("--ROOT_DIRECTORY",
                        default="IRB_DIRECTORY",
                        type=str,
                        choices=["DATA_REQUEST_DIRECTORY",
                                 "IDR_DATA_REQUEST_DIRECTORY",
                                 "IRB_DIRECTORY",
                                 "PROJECT_OR_PORTION_DIRECTORY"],
                        help="")
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=int,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    # Arguments: SQL connection settings
    parser.add_argument("--SERVER",
                        default="DWSRSRCH01.shands.ufl.edu",
                        type=str,
                        choices=["Acuo03.shands.ufl.edu",
                                 "EDW.shands.ufl.edu",
                                 "DWSRSRCH01.shands.ufl.edu",
                                 "IDR01.shands.ufl.edu",
                                 "RDW.shands.ufl.edu"],
                        help="")
    parser.add_argument("--DATABASE",
                        default="DWS_PROD",
                        type=str,
                        choices=["DWS_NOTES",
                                 "DWS_OMOP_PROD",
                                 "DWS_OMOP",
                                 "DWS_PROD"],  # TODO Add the i2b2 databases... or all the other databases?
                        help="")
    parser.add_argument("--USER_DOMAIN",
                        default="UFAD",
                        type=str,
                        choices=["UFAD"],
                        help="")
    parser.add_argument("--USERNAME",
                        default=os.environ["USER"],
                        type=str,
                        help="")
    parser.add_argument("--USER_ID",
                        default=None,
                        help="")
    parser.add_argument("--USER_PWD",
                        default=None,
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    encounterID1 = argNamespace.Encounter_ID_1
    patientID1 = argNamespace.Patient_ID_1
    providerID1 = argNamespace.Provider_ID_1
    encounterID2 = argNamespace.Encounter_ID_2
    patientID2 = argNamespace.Patient_ID_2
    providerID2 = argNamespace.Provider_ID_2

    # Parsed arguments: General
    CHUNKSIZE = argNamespace.CHUNKSIZE
    MESSAGE_MODULO_CHUNKS = argNamespace.MESSAGE_MODULO_CHUNKS
    MESSAGE_MODULO_FILES = argNamespace.MESSAGE_MODULO_FILES

    # Parsed arguments: Meta-variables
    PROJECT_DIR_DEPTH = argNamespace.PROJECT_DIR_DEPTH
    DATA_REQUEST_DIR_DEPTH = argNamespace.DATA_REQUEST_DIR_DEPTH
    IRB_DIR_DEPTH = argNamespace.IRB_DIR_DEPTH
    IDR_DATA_REQUEST_DIR_DEPTH = argNamespace.IDR_DATA_REQUEST_DIR_DEPTH

    ROOT_DIRECTORY = argNamespace.ROOT_DIRECTORY
    LOG_LEVEL = argNamespace.LOG_LEVEL

    # Parsed arguments: SQL connection settings
    SERVER = argNamespace.SERVER
    DATABASE = argNamespace.DATABASE
    USER_DOMAIN = argNamespace.USER_DOMAIN
    USERNAME = argNamespace.USERNAME
    USER_ID = argNamespace.USER_ID
    USER_PWD = argNamespace.USER_PWD
    # <<< `Argparse` arguments <<<

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
    if USER_ID:
        uid = USER_ID[:]
    else:
        uid = fr"{USER_DOMAIN}\{USERNAME}"
    if USER_PWD:
        userPwd = USER_PWD
    else:
        userPWD = os.environ["HFA_UFADPWD"]
    conStr = f"mssql+pymssql://{uid}:{userPWD}@{SERVER}/{DATABASE}"

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

    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:


    # Arguments
    `CHUNKSIZE`: "{CHUNKSIZE}"
    `MESSAGE_MODULO_CHUNKS`: "{MESSAGE_MODULO_CHUNKS}"
    `MESSAGE_MODULO_FILES`: "{MESSAGE_MODULO_FILES}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USER_DOMAIN` = "{USER_DOMAIN}"
    `USERNAME` = "{USERNAME}"
    `USER_ID` = "{USER_ID}"
    `USER_PWD` = censored
    """)
    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)
    logger.info(f"""Script arguments:\n{argListString}""")

    # Begin module body

    TEST_SCRIPT = False

    if not TEST_SCRIPT:
        LIST_1 = ["/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/Intermediate Results/OMOP Portion/data/output/identified/2024-01-23 13-54-26/condition_occurrence.csv"] + [path.absolute() for path in Path("/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/OMOP_Structured_Data/data/output/identified").iterdir() if path.suffix == ".csv"]
        LIST_2 = [path.absolute() for path in Path("../Concatenated Results/data/output/convertColumnsGeneral/2024-02-23 18-11-43").iterdir()]
    elif TEST_SCRIPT:
        LIST_1 = ["/data/herman/mnt/ufhsd/SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Liu/IRB202300703/OMOP_Structured_Data/data/output/identified/device_exposure.csv"]
        LIST_2 = ["/data/herman/Projects/IRB202300703/Concatenated Results/data/output/convertColumnsGeneral/2024-02-23 18-11-43/device_exposure.csv"]

    listOfFiles1 = sorted([Path(string) for string in LIST_1])
    listOfFiles2 = sorted([Path(string) for string in LIST_2])

    lof1 = [pathObj.name for pathObj in listOfFiles1]
    lof2 = [pathObj.name for pathObj in listOfFiles2]

    dfFiles = pd.DataFrame([lof1, lof2]).T
    dfFiles.columns = ["Group 1 Files", "Group 2 Files"]

    logger.info(f"\n{dfFiles}")

    columnsToCheck1 = {integer: string for integer, string in [(0, encounterID1), (1, patientID1), (2, providerID1)] if not isinstance(string, type(None))}
    columnsToCheck2 = {integer: string for integer, string in [(0, encounterID2), (1, patientID2), (2, providerID2)] if not isinstance(string, type(None))}

    spotCheckColumns(listOfFiles1=listOfFiles1,
                     listofFiles2=listOfFiles2,
                     connectionString=conStr,
                     logger=logger,
                     moduloChunks=MESSAGE_MODULO_CHUNKS,
                     columnsToCheck1=columnsToCheck1,
                     columnsToCheck2=columnsToCheck2)

    # End module body
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
