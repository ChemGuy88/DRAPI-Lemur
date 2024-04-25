"""
Downloads i2b2 data. Optionally also de-identifies it into a limited data set.
"""

from __future__ import annotations

import os
import logging
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection
from typing_extensions import Literal
# Third-party packages
import pandas as pd
import pymssql
import sqlalchemy as sa
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)

# Arguments
COHORT_IDS_FILE_PATH = Path(r"..\..\..\work_2023_02_21\data\intermediate\createCohortFile_requestedCohort\2023-03-02 10-15-50\i2b2Cohort_fromRequestedCohort.CSV")
COHORT_ID_TYPE = "i2b2 Patient Number"  # A string. One of the `filderID` values of `getIDs`.
COHORT_COLUMN_NAME = "I2B2_PATIENT_NUM"  # A string. The column name of `COHORT_IDS_FILE_PATH` that contains the IDs.
COHORT_NAME = 'SGMCPLGB'  # A string. The name of cohort or study, e.g., "cancer_patients"
IRB_NUMBER = 'IRB201902162'  # A string. The IRB protocol and its number. E.g., "IRB123456789", "CED123456789", or "NH12345678". This is used in creating the patient de-identified IDs.
DE_IDENTIFY = None  # None-type or string "LDS", for "Limited data set".

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
USE_WINDOWS_AUTHENTICATION = True
SERVER = "EDW.shands.ufl.edu"
SERVER_I2B2 = "IDR01.shands.ufl.edu"
DATABASE = "DWS_PROD"
DATABASE_I2B2_GNV = "I2B2LTDDATA"
DATABASE_I2B2_JAX = "I2B2LTDDATAJAX"
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

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"

# Variables: Map legacy variables to DRAPI-LEMUR standard variables
cohort = COHORT_NAME
irb = IRB_NUMBER

base_dir = projectDir
data_dir = dataDir
i2b2_dir = runOutputDir.joinpath("i2b2")
map_dir = runOutputDir.joinpath("mapping")
disclosure_dir = runOutputDir.joinpath("disclosure")

host = SERVER
database_prod = DATABASE
host_i2b2 = SERVER_I2B2
database_i2b2_GNV = DATABASE_I2B2_GNV
database_i2b2_JAX = DATABASE_I2B2_JAX

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Directory creation: Project-specific
makeDirPath(i2b2_dir)
if DE_IDENTIFY.lower():
    makeDirPath(map_dir)
    makeDirPath(disclosure_dir)
elif isinstance(DE_IDENTIFY, type(None)):
    pass
else:
    raise Exception("Invalid option for `DE_IDENTIFY`.")

# Functions: SQL


def connectToDatabase(host: str,
                      database: str,
                      useWindowsAuthentication=True) -> DBAPIConnection:
    """
    Connects to a SQL database given a `host` (server) and `database` value.
    """
    if useWindowsAuthentication:
        connection = pymssql.connect(host=host,
                                     database=database)
    else:
        conStr = f"mssql+pymssql://{uid}:{PWD}@{host}/{database}"
        connection = sa.create_engine(conStr).connect()
    return connection


def executeQuery(query: str, host: str, database: str) -> pd.DataFrame:
    """
    Executes a SQL query.
    INPUT:
        `query`: a string
        `host`: a string
        `databse`: a string
    OUTPUT:
        A pandas dataframe object.
    """
    databaseConnection = connectToDatabase(host, database)
    queryResult = pd.read_sql(query, databaseConnection)
    databaseConnection.close()
    return queryResult


# Functions: Script-specific
def getIDs(cohortFilePath: Union[Path, str],
           filterID: Literal["Patient Key", "EPIC Patient ID", "i2b2 Patient Number", "MRN (UF)", "MRN (Jax)"],
           logger: Logger,
           cohortColumnName: Union[None, str] = None) -> None:
    """
    Get i2b2 patient IDs from any of the following ID types:
        - Patient Key
        - EPIC Patient ID
        - i2b2 Patient Number
        - MRN (UF)
        - MRN (Jax)
    """

    if filterID == "Patient Key":
        filterStatement = "WHERE\n\tB.PATNT_KEY IN (XXXXX)"
        filterIDColumnName = filterID
    elif filterID == "EPIC Patient ID":
        filterStatement = "WHERE\n\tA.PATIENT_IDE IN (XXXXX)"
        filterIDColumnName = filterID
    elif filterID == "i2b2 Patient Number":
        filterStatement = "WHERE\n\tA.PATIENT_NUM IN (XXXXX)"
        filterIDColumnName = filterID
    elif filterID == "MRN (UF)":
        filterStatement = "WHERE\n\tC.IDENT_ID IN (XXXXX)"  # NOTE: Not tested
        filterIDColumnName = filterID
    elif filterID == "MRN (Jax)":
        filterStatement = "WHERE\n\tD.IDENT_ID IN (XXXXX)"  # NOTE: Not tested
        filterIDColumnName = filterID
    else:
        raise Exception("No valid option for `filterID` was passed.")

    if cohortColumnName:
        lookupColumnName = cohortColumnName
    else:
        lookupColumnName = filterIDColumnName

    query = f"""
    SELECT DISTINCT
        A.PATIENT_IDE AS 'EPIC Patient ID',
        A.PATIENT_NUM AS 'I2B2_PATIENT_NUM',
        B.PATNT_KEY AS 'Patient Key',
        C.IDENT_ID AS 'MRN (UF)',
        D.IDENT_ID AS 'MRN (Jax)'
    FROM
        [DWS_I2B2].[dbo].PATIENT_MAPPING A
        LEFT OUTER JOIN [DWS_PROD].[dbo].ALL_PATIENT_IDENTITIES B ON A.PATIENT_IDE = B.PATNT_ID
        LEFT OUTER JOIN [DWS_PROD].[dbo].ALL_PATIENT_IDENTITIES C ON A.PATIENT_IDE = C.PATNT_ID AND C.IDENT_ID_TYPE=101 AND C.LOOKUP_IND='Y'
        LEFT OUTER JOIN [DWS_PROD].[dbo].ALL_PATIENT_IDENTITIES D ON A.PATIENT_IDE = D.PATNT_ID AND D.IDENT_ID_TYPE=110 AND D.LOOKUP_IND='Y'
    {filterStatement}
    """
    m = 'w'
    h = True
    for chunk in pd.read_csv(COHORT_IDS_FILE_PATH, chunksize=3000):
        chunk = chunk[[lookupColumnName]]
        chunk = chunk.drop_duplicates()
        id = chunk[lookupColumnName].tolist()
        ids = "','".join(str(x) for x in id)
        ids = "'" + ids + "'"
        query1 = query.replace('XXXXX', ids)
        result = executeQuery(query1, host, database_prod)
        result = result.drop_duplicates()
        result.to_csv(os.path.join(data_dir, 'Cohort IDs.CSV'), index=False, mode=m, header=h)
        m = 'a'
        h = False
        logger.debug(query1)


def i2b2_dump_main(source, table, cohort_dir, i2b2_dir, cohort, logger):
    """
    source: 'GNV' or 'JAX'. Indicates which i2b2 instance to use as the source of data.
    table: 'patient_dimension', 'visit_dimension', or 'observation_fact'. Indicates which table to dump.
    cohort_dir: Specifies directory where cohort file is saved.
    i2b2_dir: directory where i2b2 data will be saved.
    cohort: The name of the cohort. E.g., 'subjects'.
    """
    h = True
    m = 'w'
    # Cohort should be saved in "Cohort IDs.CSV" file. It should contain i2b2 patient IDs in 'I2B2_PATIENT_NUM' column.
    for it, ids in enumerate(pd.read_csv(os.path.join(cohort_dir, 'Cohort IDs.CSV'), chunksize=100), start=1):
        logger.info(f"""  Working on batch {it:,}.""")
        ids = ids[['I2B2_PATIENT_NUM']].drop_duplicates().dropna()
        ids = ids['I2B2_PATIENT_NUM'].unique().tolist()
        ids = "','".join(str(x) for x in ids)
        ids = "'" + ids + "'"

        if (source == 'GNV'):
            database = 'I2B2LTDDATA'
        elif (source == 'JAX'):
            database = 'I2B2LTDDATAJAX'

        if (table == 'patient_dimension'):
            query = """
            select  PATIENT_NUM,VITAL_STATUS_CD,BIRTH_DATE,DEATH_DATE,SEX_CD,AGE_IN_YEARS_NUM,LANGUAGE_CD,RACE_CD,MARITAL_STATUS_CD,RELIGION_CD,ZIP_CD,STATECITYZIP_PATH,INCOME_CD,ETHNIC_CD,PAYER_CD,SMOKING_STATUS_CD,COUNTY_CD,SSN_VITAL_STATUS_CD,MYCHART_CD,CANCER_IND
            from database.dbo.PATIENT_DIMENSION
            where PATIENT_NUM in ( XXXXX )
            """
        elif (table == 'visit_dimension'):
            query = """
            select
            PATIENT_NUM,ENCOUNTER_NUM,ACTIVE_STATUS_CD,START_DATE,END_DATE,INOUT_CD,LOCATION_CD,LOCATION_PATH,LENGTH_OF_STAY
            from database.dbo.VISIT_DIMENSION
            where PATIENT_NUM in ( XXXXX )
            """
        elif (table == 'observation_fact'):
            query = """
            select  PATIENT_NUM,ENCOUNTER_NUM,CONCEPT_CD,START_DATE,MODIFIER_CD,VALTYPE_CD,TVAL_CHAR,NVAL_NUM,VALUEFLAG_CD,QUANTITY_NUM,UNITS_CD,END_DATE,LOCATION_CD
            from database.dbo.OBSERVATION_FACT
            where PATIENT_NUM in ( XXXXX )
            """
        query = query.replace('XXXXX', ids)
        query = query.replace('database', database)
        if (source == 'GNV'):
            result = executeQuery(query, host_i2b2, database_i2b2_GNV)
        elif (source == 'JAX'):
            result = executeQuery(query, host_i2b2, database_i2b2_JAX)
        result = result.drop_duplicates()
        file = cohort + '_' + table + '_' + source + '.csv'
        result.to_csv(os.path.join(i2b2_dir, file), mode=m, header=h, index=False)
        h = False
        m = 'a'
    logger.info(f"""Completed i2b2 dump for table "{table}" for location "{source}".""")


def generate_patient_map(map_dir, cohort_dir):
    pat = pd.read_csv(os.path.join(cohort_dir, 'Cohort IDs.CSV'))
    pat_map = pat[['Patient Key']].drop_duplicates()
    pat_map = pat_map.reset_index()
    pat_map['deid_num'] = pat_map.index + 1
    pat_map['deid_pat_ID'] = pat_map.apply(lambda row: str(irb) + '_PAT_' + str(int(row['deid_num'])), axis=1)
    pat = pd.merge(pat, pat_map, how='left', on='Patient Key')
    pat.to_csv(os.path.join(map_dir, 'map_patient.csv'), index=False)


def generate_encounter_map_i2b2(map_dir, i2b2_dir):
    # GNV
    in_file = cohort + '_visit_dimension_GNV.csv'
    df = pd.read_csv(os.path.join(i2b2_dir, in_file))
    df = df[['ENCOUNTER_NUM']].drop_duplicates()
    df1 = pd.DataFrame()
    in_file = cohort + '_observation_fact_GNV.csv'
    for chunk in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        chunk = chunk[['ENCOUNTER_NUM']].drop_duplicates()
        df1 = pd.concat([df1, chunk])
        df1 = df1.drop_duplicates()
    df = pd.concat([df, df1])
    df = df.drop_duplicates()
    df = df.reset_index()
    df['deid_num'] = df.index + 1
    df['deid_enc_ID'] = df.apply(lambda row: str(irb) + '_ENC_' + str(int(row['deid_num'])), axis=1)
    df['source'] = 'GNV'
    size = df.shape[0]

    # JAX
    in_file = cohort + '_visit_dimension_JAX.csv'
    df2 = pd.read_csv(os.path.join(i2b2_dir, in_file))
    df2 = df2[['ENCOUNTER_NUM']].drop_duplicates()
    df1 = pd.DataFrame()
    in_file = cohort + '_observation_fact_JAX.csv'
    for chunk in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        chunk = chunk[['ENCOUNTER_NUM']].drop_duplicates()
        df1 = pd.concat([df1, chunk])
        df1 = df1.drop_duplicates()
    df2 = pd.concat([df2, df1])
    df2 = df2.drop_duplicates()
    df2 = df2.reset_index()
    df2['deid_num'] = df2.index + 1 + size
    df2['deid_enc_ID'] = df2.apply(lambda row: str(irb) + '_ENC_' + str(int(row['deid_num'])), axis=1)
    df2['source'] = 'JAX'

    # Concatenate GNV and JAX
    df = pd.concat([df, df2])
    df.to_csv(os.path.join(map_dir, 'map_encounter.csv'), index=False)


def generate_mappings():
    generate_patient_map(map_dir, data_dir)
    generate_encounter_map_i2b2(map_dir, i2b2_dir)


def lds_i2b2_patient_dim(map_dir, i2b2_dir, disclosure_dir_i2b2, logger):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), index=False)

    # GNV
    in_file = cohort + '_patient_dimension_GNV.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = df[['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), header=False, index=False, mode='a')
    logger.info("De-identified GNV patient dimension.")

    # JAX
    in_file = cohort + '_patient_dimension_JAX.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = df[['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), header=False, index=False, mode='a')
    logger.info("De-identified JAX patient dimension.")


def lds_i2b2_visit_dim(map_dir, i2b2_dir, disclosure_dir_i2b2, logger):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    map_enc = pd.read_csv(os.path.join(map_dir, 'map_encounter.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), index=False)

    # GNV
    in_file = cohort + '_visit_dimension_GNV.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), header=False, index=False, mode='a')
    logger.info("De-identified GNV visit dimension.")

    # JAX
    in_file = cohort + '_visit_dimension_JAX.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), header=False, index=False, mode='a')
    logger.info("De-identified JAX visit dimension.")


def lds_i2b2_observation_fact(map_dir, i2b2_dir, disclosure_dir_i2b2, logger):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    map_enc = pd.read_csv(os.path.join(map_dir, 'map_encounter.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), index=False)

    CHUNK_SIZE = 10000

    # GNV
    in_file = cohort + '_observation_fact_GNV.csv'
    logger.info("""  ..  Reading file to count the number of chunks.""")
    numChunks = sum([1 for _ in pd.read_csv(in_file, chunksize=CHUNK_SIZE, dtype=str)])
    logger.info(f"""  ..  This file has {numChunks} chunks.""")
    fpath = os.path.join(i2b2_dir, in_file)
    dfChunks = pd.read_csv(fpath, chunksize=CHUNK_SIZE, low_memory=False)
    for it, df in enumerate(dfChunks, start=1):
        logger.info(f"""  Working on chunk {it:,} of {numChunks:,}.""")
        df = df.drop_duplicates()
        df = df[df['PATIENT_NUM'] != 'PATIENT_NUM']
        df['PATIENT_NUM'] = df['PATIENT_NUM'].astype(int)
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), header=False, index=False, mode='a')
    logger.info("De-identified GNV observation fact.")

    # JAX
    in_file = cohort + '_observation_fact_JAX.csv'
    logger.info("""  ..  Reading file to count the number of chunks.""")
    numChunks = sum([1 for _ in pd.read_csv(in_file, chunksize=CHUNK_SIZE, dtype=str)])
    logger.info(f"""  ..  This file has {numChunks} chunks.""")
    fpath = os.path.join(i2b2_dir, in_file)
    dfChunks = pd.read_csv(fpath, chunksize=CHUNK_SIZE, low_memory=False)
    for it, df in enumerate(dfChunks, start=1):
        logger.info(f"""  Working on chunk {it:,} of {numChunks:,}.""")
        df = df.drop_duplicates()
        df = df[df['PATIENT_NUM'] != 'PATIENT_NUM']
        df['PATIENT_NUM'] = df['PATIENT_NUM'].astype(int)
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), header=False, index=False, mode='a')
    logger.info("De-identified JAX observation fact.")


def lds_i2b2(map_dir, i2b2_dir, disclosure_dir_i2b2, logger):
    lds_i2b2_patient_dim(map_dir, i2b2_dir, disclosure_dir_i2b2, logger=logger)
    lds_i2b2_visit_dim(map_dir, i2b2_dir, disclosure_dir_i2b2, logger=logger)
    lds_i2b2_observation_fact(map_dir, i2b2_dir, disclosure_dir_i2b2, logger=logger)


def limited_data_set(logger):
    lds_i2b2(map_dir, i2b2_dir, disclosure_dir, logger=logger)


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
    `COHORT_IDS_FILE_PATH`: "{COHORT_IDS_FILE_PATH}"
    `COHORT_NAME`: "{COHORT_NAME}"
    `IRB_NUMBER`: "{IRB_NUMBER}"

    # Arguments: SQL connection settings
    `USE_WINDOWS_AUTHENTICATION` : "{USE_WINDOWS_AUTHENTICATION}"
    `SERVER`                     : "{SERVER}"
    `SERVER_I2B2`                : "{SERVER_I2B2}"
    `DATABASE`                   : "{DATABASE}"
    `DATABASE_I2B2_GNV`          : "{DATABASE_I2B2_GNV}"
    `DATABASE_I2B2_JAX`          : "{DATABASE_I2B2_JAX}"
    `USERDOMAIN`                 : "{USERDOMAIN}"
    `USERNAME`                   : "{USERNAME}"
    `UID`                        : "{UID}"
    `PWD`                        : censored

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    """)

    # Generate i2b2 patient IDs
    logger.info("Generating i2b2 patient IDs.")
    getIDs(cohortFilePath=COHORT_IDS_FILE_PATH,
           cohortColumnName=COHORT_COLUMN_NAME,
           filterID=COHORT_ID_TYPE,
           logger=logger)
    logger.info("Generating i2b2 patient IDs - done.")

    # Perform i2b2 dump
    makeDirPath(i2b2_dir)
    i2b2_dump_main('GNV', 'patient_dimension', data_dir, i2b2_dir, cohort, logger=logger)  # Pull data from patient_dimension in GNV i2b2 instance.
    i2b2_dump_main('JAX', 'patient_dimension', data_dir, i2b2_dir, cohort, logger=logger)
    i2b2_dump_main('GNV', 'visit_dimension', data_dir, i2b2_dir, cohort, logger=logger)
    i2b2_dump_main('JAX', 'visit_dimension', data_dir, i2b2_dir, cohort, logger=logger)
    i2b2_dump_main('GNV', 'observation_fact', data_dir, i2b2_dir, cohort, logger=logger)
    i2b2_dump_main('JAX', 'observation_fact', data_dir, i2b2_dir, cohort, logger=logger)

    # Prepare limited data set for disclosure
    if DE_IDENTIFY.lower() == "lds":
        generate_mappings()
        limited_data_set(logger=logger)
    elif isinstance(DE_IDENTIFY, type(None)):
        pass
    else:
        raise Exception("Invalid option for `DE_IDENTIFY`.")

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(projectDir)}".""")
