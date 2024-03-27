"""
QA: Make sure values were correctly converted.
"""

import argparse
import logging
import os
import pprint
from pathlib import Path
from typing_extensions import Union
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    readDataFile,
                                    successiveParents)
# Super-local
pass


# Functions

def spotCheckColumns(listOfFiles1: list,
                     listofFiles2: list,
                     logger: logging.Logger,
                     moduloChunks: int,
                     columnsToCheck1: dict[int: str] = {0: "visit_occurrence_id",
                                                        1: "person_id",
                                                        2: "provider_id"},
                     columnsToCheck2: dict[int: str] = {0: "Encounter # (CSN)",
                                                        1: "Patient Key",
                                                        2: "Provider Key"}) -> None:
    """
    This function "spot checks" pairs of files to see if the passed variables have been properly converted from the OMOP data model to the UF Health data model.

    In `columnsToCheck1` and `columnsToCheck2` the keys of the dictionary have the following meaning:
    - 0: Encounter ID Variable Name
    - 1: Patient ID Variable Name
    - 2: Provider ID Variable Name

    The code is only meant to check these three ID types, because under the hood these integer values are mapped to SQL queries. So, for example, you could not pass `{0: "Note Key"}` to the function, because it would use the SQL query that maps encounter IDs.

    NOTE This has only been tested and verified on 3-on-3 checks. That is, checking if all three informative OMOP ID variables have been mapped to their three UF Health equivalents. The code should be able to also do spot checks for less number of variables, like just `person_id` to `Patient Key`, but it has not been tested.
    """
    with open("../Concatenated Results/sql/BO Variable Spot Check - Encounter # (CSN).sql", "r") as file:
        query0_0 = file.read()
    with open("../Concatenated Results/sql/BO Variable Spot Check - Patient Key.sql", "r") as file:
        query1_0 = file.read()
    with open("../Concatenated Results/sql/BO Variable Spot Check - Provider Key.sql", "r") as file:
        query2_0 = file.read()

    for file1, file2 in zip(listOfFiles1, listofFiles2):
        try:
            logger.info(f"""  Working on file pair:
        `file1`: "{file1}"
        `file2`: "{file2}".""")
            df2_0 = pd.read_csv(file2, nrows=2)
            df2_0columns = df2_0.columns
            columnChecks2 = df2_0columns.isin(columnsToCheck2.values())
            logger.debug(f"""  Group 2 table:\n{df2_0.to_string()}""")
            logger.debug(f"""  Group 2 columns:\n{df2_0.columns}""")
            logger.debug(f"""  Group 2 columns check:\n{columnChecks2}""")
            spot2df = df2_0.loc[0, columnChecks2]
            spot2df = pd.DataFrame(spot2df)  # For type hinting
            logger.info(f"  A row has been selected for a spot check:\n{spot2df.T.to_string()}")
            # Convert group 2 spot to group 1 values
            spot2dict = spot2df.to_dict()[0]
            logger.info(spot2dict)
            query0_1 = query0_0[:]
            query1_1 = query1_0[:]
            query2_1 = query2_0[:]
            spot1dict = {}
            if 0 in columnsToCheck2.keys():
                encounterIDVariableName = columnsToCheck2[0]
                if df2_0columns.isin([encounterIDVariableName]).sum() > 0:
                    queryEncounterIDValue = spot2dict[encounterIDVariableName]
                    query0_1 = query0_1.replace("{PYTHON_VARIABLE: Encounter # (CSN)}", str(queryEncounterIDValue))
                    result0 = pd.read_sql(sql=query0_1, con=conStr)
                    if result0.shape != (1,2):
                        logger.warning(f"""  ..  The encounter ID mapping is not one-to-one:\n{result0.to_string()}.""")
                        spot1EncounterID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1EncounterID = result0["visit_occurrence_id"][0]
                    spot1dict["visit_occurrence_id"] = [spot1EncounterID]
            if 1 in columnsToCheck2.keys():
                patientIDVariableName = columnsToCheck2[1]
                if df2_0columns.isin([patientIDVariableName]).sum() > 0:
                    queryPatientIDValue = spot2dict[patientIDVariableName]
                    query1_1 = query1_1.replace("{PYTHON_VARIABLE: Patient Key}", str(queryPatientIDValue))
                    result1 = pd.read_sql(sql=query1_1, con=conStr)
                    if result1.shape != (1,2):
                        logger.warning(f"""  ..  The patient ID mapping is not one-to-one:\n{result1.to_string()}.""")
                        spot1PatientID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1PatientID = result1["person_id"][0]
                    spot1dict["person_id"] = [spot1PatientID]
            if 1 in columnsToCheck2.keys():
                providerIDVariableName = columnsToCheck2[2]
                if df2_0columns.isin([providerIDVariableName]).sum() > 0:
                    queryProviderIDValue = spot2dict[providerIDVariableName]
                    query2_1 = query2_1.replace("{PYTHON_VARIABLE: Provider Key}", str(queryProviderIDValue))
                    result2 = pd.read_sql(sql=query2_1, con=conStr)
                    if result2.shape != (1,2):
                        logger.warning(f"""  ..  The provider ID mapping is not one-to-one:\n{result2.to_string()}.""")
                        spot1ProviderID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1ProviderID = result2["provider_id"][0]
                    spot1dict["provider_id"] = [spot1ProviderID]
            spot1Targetdf = pd.DataFrame.from_dict(data=spot1dict, orient="columns")
            logger.info(f"""The values that we are looking for in the group 1 set of files is below:\n{spot1Targetdf}""" )
            # Chunk
            chunkGenerator1 = pd.read_csv(file1, chunksize=CHUNKSIZE, low_memory=False)
            chunkGenerator2 = pd.read_csv(file1, chunksize=CHUNKSIZE, low_memory=False)
            logger.info("    Counting the number of chunks in the file.")
            it1Total = sum([1 for _ in chunkGenerator1])
            logger.info(f"    Counting the number of chunks in the file - done. There are {it1Total:,} chunks.")
            if it1Total < MESSAGE_MODULO_CHUNKS:
                moduloChunks = it1Total
            else:
                moduloChunks = round(it1Total / MESSAGE_MODULO_CHUNKS)
            if it1Total / moduloChunks < 100:
                moduloChunks = 1
            else:
                pass
            for it1, df1Chunk in enumerate(chunkGenerator2, start=1):
                if it1 % moduloChunks == 0:
                    allowLogging = True
                else:
                    allowLogging = False
                if allowLogging:
                    logger.info(f"""  ..  Working on chunk {it1:,} of {it1Total:,}.""")
                df1Chunk = pd.DataFrame(df1Chunk)  # For type hinting
                columnChecks1 = df1Chunk.columns.isin(columnsToCheck1.values())
                df1 = df1Chunk.loc[:, columnChecks1]
                df1 = pd.DataFrame(df1)  # For type hinting
                mask = df1.isin(spot1Targetdf.values.flatten()).all(axis=1)
                rowLocation = mask.index[mask][0]
                if mask.sum() > 0:
                    spot1Hitdf = df1[mask]
                    logger.info(f"""    Found spot located at index value (row number) "{rowLocation}":\n{spot1Hitdf.to_string()}.""")
                    break
        except Exception as error:
            logger.fatal(error)


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
                     columnsToCheck1=columnsToCheck1,
                     columnsToCheck2=columnsToCheck2,
                     logger=logger,
                     moduloChunks=MESSAGE_MODULO_CHUNKS)

    # End module body
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
