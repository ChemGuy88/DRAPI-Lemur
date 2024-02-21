from __future__ import annotations

import concurrent.futures
import logging
import os
import random
import re
import shutil
from datetime import timedelta
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection
# Third-party packages
import pandas as pd
import pymssql
import sqlalchemy as sa
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    replace_sql_query,
                                    successiveParents)

# Arguments: Script settings
COHORT_NAME = ""                                    # An arbitrary name used in file names
COHORT_FILE = ""                                    # A file name that is located directory specified by the variable `data_dir`
IRB_NUMBER = ""                                     # Used for creating the de-identification map IDs.
ID_TYPE = ""                                        # Pick from "EncounterCSN", "EncounterKey", or "PatientKey". Choose the ID type you used in `COHORT_FILE`
NOTE_VERSION = ""                                   # Pick from "all", or "last"
DE_IDENTIFICATION_MODE = ""                         # Pick from "deid", "lds", or "phi"
LOG_LEVEL = ""                                      # See the "logging" module for valid values for the `loglevel` parameter.
SQL_ENCOUNTER_EFFECTIVE_DATE_START = ''   # The beginning of date range of encounters to collect. Format: YYYY-MM-DD
SQL_ENCOUNTER_EFFECTIVE_DATE_END = ''     # The end of date range of encounters to collect. Format: YYYY-MM-DD

# Arguments: SQL connection settings
USE_WINDOWS_AUTHENTICATION = True
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE_PROD = "DWS_PROD"
DATABASE_NOTES = "DWS_NOTES"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = DATA_REQUEST_DIR_DEPTH + 0
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "PROJECT_OR_PORTION_DIRECTORY"  # TODO One of the following:
                                                 # ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
                                                 #  "IRB_DIRECTORY",                 # noqa
                                                 #  "DATA_REQUEST_DIRECTORY",        # noqa
                                                 #  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

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

# Variables: Path Construction: Project-specific
notes_dir = runOutputDir.joinpath('free_text')  # all notes related files are saved in 'notes' subdirectory of 'data' directory
map_dir = runOutputDir.joinpath('mapping')  # mappings are saved in 'mapping' subdirectory of 'data' folder.
disclosure_dir = runOutputDir.joinpath('disclosure')

# Variables: Map legacy variables to DRAPI-LEMUR standard variables: Script settings
cohort = COHORT_NAME
id_type = ID_TYPE
note_version = NOTE_VERSION
irb = IRB_NUMBER
deid_mode = DE_IDENTIFICATION_MODE

# Variables: Map legacy variables to DRAPI-LEMUR standard variables: Path construction
base_dir = str(projectDir)
data_dir = dataDir
sql_dir = sqlDir

# Variables: Map legacy variables to DRAPI-LEMUR standard variables: SQL Parameters
host = SERVER
database_prod = DATABASE_PROD
database_notes = DATABASE_NOTES

# Variables: SQL connection settings
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Directory creation: Project-specific
for dir in [data_dir, sql_dir, notes_dir, disclosure_dir]:
    makeDirPath(dir)
if DE_IDENTIFICATION_MODE.lower() == "phi":
    pass
elif DE_IDENTIFICATION_MODE.lower() in ["deid", "lds"]:
    makeDirPath(map_dir)
else:
    raise Exception(f"Unexpected value for `DE_IDENTIFICATION_MODE`: {DE_IDENTIFICATION_MODE}.")

# Functions


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


# notes methods


def pull_metadata(note_version, id_type, note_type, sql_dir, cohort_dir, notes_dir, cohort, logger: Logger):
    logger.info(f"""Function arguments:
    `note_version`: {note_version}
    `id_type`:      {id_type}
    `note_type`:    {note_type}
    `sql_dir`:      {sql_dir}
    `cohort_dir`:   {cohort_dir}
    `notes_dir`:    {notes_dir}
    `cohort`:       {cohort}
    `logger`:       {logger}""")
    m = 'w'  # mode of the output file
    h = True  # header of the output file
    counter = 1  # used only for tracking/time estimation purposes
    if (id_type == 'PatientKey'):
        in_file = COHORT_FILE
    elif (id_type == 'EncounterCSN' or id_type == 'EncounterKey'):
        in_file = COHORT_FILE
    for df in pd.read_csv(os.path.join(cohort_dir, in_file), chunksize=1000, engine='python'):
        df = df[[id_type]]
        id_str = df[id_type].unique().tolist()
        logger.info(f"  This chunk of your input file containing patient or encounter ID's is of length {len(id_str):,}.")
        id_str = "','".join(str(x) for x in id_str)
        id_str = "'" + id_str + "'"
        query_file = note_type + '_metadata.sql'
        logger.info(f"Reading query file: {query_file}")
        fpath = os.path.join(sql_dir, query_file)
        with open(fpath, "r") as file:
            query = file.read()
        query = replace_sql_query(query, "XXXXX", id_str)
        query = replace_sql_query(query, "{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_START}", SQL_ENCOUNTER_EFFECTIVE_DATE_START)
        query = replace_sql_query(query, "{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_END}", SQL_ENCOUNTER_EFFECTIVE_DATE_END)

        logger.log(9, f"Using the following query:\n>>> Begin query >>>\n{query}\n<<< End query <<<")
        result = executeQuery(query=query,
                              host=host,
                              database=database_prod)

        logger.info(f"The chunk query has {len(result):,} rows.")
        result = result.drop_duplicates()

        logger.info(f"After dropping duplicates, the chunk query has {len(result):,} rows.")
        if (note_type == 'note' and note_version == 'last'):  # keep only the last version of the note
            result = result.sort_values(by=['NoteKey', 'ContactNumber'], ascending=[True, False])
            result = result.drop_duplicates(['NoteKey'])
        result_file = cohort + '_' + note_type + '_metadata.csv'
        result.to_csv(os.path.join(notes_dir, result_file), index=False, mode=m, header=h)
        m = 'a'
        h = False
        logger.info(f'Completed chunk {counter}')
        counter = counter + 1
    return


def split_metadata(note_type, notes_dir, cohort, logger: Logger):
    in_file = cohort + '_' + note_type + '_metadata.csv'
    file_count = 1
    for df in pd.read_csv(os.path.join(notes_dir, in_file), chunksize=1000000):
        out_file = cohort + '_' + note_type + '_metadata_' + str(file_count) + '.csv'

        logger.info(f"Working on file {file_count}.")
        # ensure that all ID columns are integers
        columns = df.columns
        for c in ['NoteKey', 'NoteID', 'LinkageNoteID', 'OrderKey', 'OrderID', 'PatientKey', 'EncounterKey', 'EncounterCSN', 'AuthoringProviderKey', 'CosignProviderKey', 'OrderingProviderKey', 'AuthorizingProviderKey']:
            if (c in columns):
                # fill missing values with 0 since 0 is never used for these IDs in reality
                df[c] = df[c].fillna(0)
                # use string instead of int type since some fields, such as EncounterCSN, are bigger than what python considers an integer
                df[c] = df.apply(lambda row: str(row[c]).split('.0')[0], axis=1)
        df.to_csv(os.path.join(notes_dir, out_file), index=False)
        file_count = file_count + 1
    return


def pull_text(item, note_type, note_id, sql_dir, notes_dir, dir_final, logger: Logger):
    logger.info(f"""Processing item "{item}".""")
    # Pull text
    header = True  # header of the output file
    mode = 'w'  # mode of the output file
    for notes in pd.read_csv(os.path.join(notes_dir, item), chunksize=10000, engine='python'):
        note_list = notes[note_id].unique().tolist()
        note_list = ",".join(str(int(x)) for x in note_list)
        query_file = note_type + '_text.sql'
        query_file = os.path.join(sql_dir, query_file)
        fpath = os.path.join(sql_dir, query_file)
        with open(fpath, "r") as file:
            query = file.read()
        query = replace_sql_query(query, "XXXXX", note_list)
        result = executeQuery(query=query,
                              host=host,
                              database=database_notes)
        # ensure that all ID columns are integers
        columns = result.columns
        for c in ['LinkageNoteID', 'OrderKey']:
            if (c in columns):
                # fill missing values with 0 since 0 is never used for these IDs in reality
                result[c] = result[c].fillna(0)
                # use string instead of int type since some fields, such as EncounterCSN, are bigger than what python considers an integer
                result[c] = result.apply(lambda row: str(row[c]).split('.0')[0], axis=1)
        file_count = item.split('.csv')[0].split('_')[-1]
        file_out = note_type + '_' + str(file_count) + '.tsv'
        result.to_csv(os.path.join(dir_final, file_out), header=header, mode=mode, sep='\t', encoding="UTF-8", index=False)
        header = False
        mode = 'a'
    return


def pull_text_in_parallel(note_type, sql_dir, notes_dir, cohort, logger: Logger):
    # Prepare for text pull
    if (note_type == 'note'):
        dir_final = os.path.join(notes_dir, cohort + '_note')
        if (not os.path.exists(dir_final)):
            os.makedirs(dir_final)
        note_id = 'LinkageNoteID'
    elif (note_type == 'order_narrative'):
        dir_final = os.path.join(notes_dir, cohort + '_order_narrative')
        if (not os.path.exists(dir_final)):
            os.makedirs(dir_final)
        note_id = 'OrderKey'
    elif (note_type == 'order_impression'):
        dir_final = os.path.join(notes_dir, cohort + '_order_impression')
        if (not os.path.exists(dir_final)):
            os.makedirs(dir_final)
        note_id = 'OrderKey'
    elif (note_type == 'order_result_comment'):
        dir_final = os.path.join(notes_dir, cohort + '_order_result_comment')
        if (not os.path.exists(dir_final)):
            os.makedirs(dir_final)
        note_id = 'OrderKey'
    # identify all metadata files for specific note type
    pattern = cohort + '_' + note_type + '_metadata_.*.csv'  # hot fix 2022-05-10
    items = [f for f in os.listdir(notes_dir) if re.match(pattern, f)]
    logger.info(f"""This is the list of items that matched the criteria for processing: {items}.""")
    # start pullng text. By default, number of parallel threads is set to 4.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        result_futures = {executor.submit(pull_text, item, note_type, note_id, sql_dir, notes_dir, dir_final, logger): item for item in items}
        for future in concurrent.futures.as_completed(result_futures):
            item = result_futures[future]
            try:
                _ = future.result()
                logger.info(f"""Completed item "{item}".""")
            except Exception as e:
                logger.info(f"""An exception was generated by item "{item}": "{e}".""")
    return


def combine_order_metadata(notes_dir, cohort):
    m = 'w'
    h = True
    for file1 in ['order_narrative', 'order_impression', 'order_result_comment']:
        file = cohort + '_' + file1 + '_metadata.csv'
        if os.path.exists(os.path.join(notes_dir, file)):
            df = pd.read_csv(os.path.join(notes_dir, file))
            if (file1 in ['order_narrative', 'order_impression']):
                df['Line'] = ''
            df = df[['OrderKey', 'Line', 'OrderID', 'OrderPlacedDatetime', 'OrderResultDatetime', 'PatientKey', 'MRN_GNV', 'MRN_JAX', 'NoteType', 'EncounterDate', 'EncounterKey', 'EncounterCSN', 'OrderingProviderKey', 'OrderingProviderType', 'OrderingProviderSpecialty', 'AuthorizingProviderKey', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']]
            df.to_csv(os.path.join(notes_dir, '{}_order_metadata.csv'.format(cohort)), index=False, mode=m, header=h)
            m = 'a'
            h = False
    return


def create_encounters(notes_dir):
    df = pd.DataFrame()
    for file in ['{}_order_narrative_metadata.csv'.format(cohort), '{}_order_impression_metadata.csv'.format(cohort), '{}_order_result_comment_metadata.csv'.format(cohort), '{}_note_metadata.csv'.format(cohort)]:
        for dfx in pd.read_csv(os.path.join(notes_dir, file), chunksize=100000):
            df1 = dfx[['EncounterCSN']].drop_duplicates()
            df = pd.concat([df, df1])
            df.drop_duplicates(inplace=True)
    df.to_csv(os.path.join(notes_dir, 'encounters.csv'), index=False)
    return


def create_provider_metadata(notes_dir, cohort):
    m = 'w'
    h = True
    df = pd.DataFrame()
    for file1 in ['order_narrative', 'order_impression', 'order_result_comment', 'note']:
        # for file in ['note']:
        file = cohort + '_' + file1 + '_metadata.csv'
        if os.path.exists(os.path.join(notes_dir, file)):
            for dfx in pd.read_csv(os.path.join(notes_dir, file), chunksize=100000):
                if (file1 in ['order_narrative', 'order_impression', 'order_result_comment']):
                    df1 = dfx[['OrderingProviderKey', 'OrderingProviderType', 'OrderingProviderSpecialty']]
                    df1 = df1.rename(columns={"OrderingProviderKey": "ProviderKey", "OrderingProviderType": "ProviderType", "OrderingProviderSpecialty": "ProviderSpecialty"})
                    df2 = dfx[['AuthorizingProviderKey', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']]
                    df2 = df2.rename(columns={"AuthorizingProviderKey": "ProviderKey", "AuthorizingProviderType": "ProviderType", "AuthorizingProviderSpecialty": "ProviderSpecialty"})
                elif (file1 in ['note']):
                    df1 = dfx[['AuthoringProviderKey', 'AuthoringProviderType', 'AuthoringProviderSpecialty']]
                    df1 = df1.rename(columns={"AuthoringProviderKey": "ProviderKey", "AuthoringProviderType": "ProviderType", "AuthoringProviderSpecialty": "ProviderSpecialty"})
                    df2 = dfx[['CosignProviderKey', 'CosignProviderType', 'CosignProviderSpecialty']]
                    df2 = df2.rename(columns={"CosignProviderKey": "ProviderKey", "CosignProviderType": "ProviderType", "CosignProviderSpecialty": "ProviderSpecialty"})
                df1 = pd.concat([df1, df2])
                df1.drop_duplicates(inplace=True)
                df = pd.concat([df, df1])
                df.drop_duplicates(inplace=True)
            df.to_csv(os.path.join(notes_dir, 'provider_metadata.csv'), index=False, mode=m, header=h)
            m = 'a'
            h = False
    return


def generate_map(deid_mode, in_dir, map_dir, concept, cohort):
    """
    `concept` can be any of the following values:
        - patient
        - encounter
        - note
        - note_link
        - order
        - provider
    """
    # define variables
    if (concept == 'patient'):
        concept_cd = 'PAT'
        concept_id = 'deid_pat_id'
        file = os.path.join(in_dir, COHORT_FILE)  # NOTE
        concept_column = 'PatientKey'
    elif (concept == 'encounter'):
        concept_cd = 'ENC'
        concept_id = 'deid_enc_id'
        create_encounters(in_dir)
        file = os.path.join(in_dir, 'encounters.csv')
        concept_column = 'EncounterCSN'
    elif (concept == 'note'):
        concept_cd = 'NOTE'
        concept_id = 'deid_note_id'
        file = os.path.join(in_dir, '{}_note_metadata.csv'.format(cohort))
        concept_column = 'NoteKey'
    elif (concept == 'note_link'):
        concept_cd = 'LINK_NOTE'
        concept_id = 'deid_link_note_id'
        file = os.path.join(in_dir, '{}_note_metadata.csv'.format(cohort))
        concept_column = 'LinkageNoteID'
    elif (concept == 'order'):
        concept_cd = 'ORDER'
        concept_id = 'deid_order_id'
        combine_order_metadata(in_dir, cohort)
        file = os.path.join(in_dir, '{}_order_metadata.csv'.format(cohort))
        concept_column = 'OrderKey'
    elif (concept == 'provider'):
        concept_cd = 'PROV'
        concept_id = 'deid_provider_id'
        create_provider_metadata(in_dir, cohort)
        file = os.path.join(in_dir, 'provider_metadata.csv')
        concept_column = 'ProviderKey'
    else:
        logging.error(f"""Nonexisting concept in `generate_map` method: "{concept}".""")

    ids_final = pd.DataFrame()
    for ids in pd.read_csv(file, chunksize=10000):
        ids = ids[[concept_column]].drop_duplicates()
        ids_final = pd.concat([ids_final, ids])
        ids_final.drop_duplicates(inplace=True)
    ids_map = ids_final.reset_index()
    ids_map['deid_num'] = ids_map.index + 1
    # assign deid value 0 for unknown input (e.g., provider key < 0)
    ids_map[concept_id] = ids_map.apply(lambda row: (str(irb) + '_' + concept_cd + '_0') if (int(row[concept_column]) < 0) else (str(irb) + '_' + concept_cd + '_' + str(int(row['deid_num']))), axis=1)
    if (deid_mode == 'deid' and concept == 'patient'):
        ids_map['date_shift'] = ids_map.apply(lambda row: random.randint(-30, 30), axis=1)
    out_file = 'map_{}.csv'.format(concept)
    ids_map = ids_map.drop(['index'], axis=1)
    ids_map.to_csv(os.path.join(map_dir, out_file), index=False)
    return


def deid_metadata(deid_mode, note_type, map_dir, notes_dir, disclosure_dir):
    # define variables
    text_file = '{}_{}_metadata.csv'.format(cohort, note_type)
    if (note_type == 'note'):
        if (deid_mode == 'deid'):
            final_columns = ['deid_note_id', 'deid_link_note_id', 'ContactNumber', 'ContactDate_shifted', 'CreatedDatetime_shifted', 'ServiceDatetime_shifted', 'deid_pat_id', 'NoteType', 'InpatientNoteType', 'EncounterDate_shifted', 'deid_enc_id', 'deid_authoring_provider_id', 'AuthoringProviderType', 'AuthoringProviderSpecialty', 'deid_cosign_provider_id', 'CosignProviderType', 'CosignProviderSpecialty']
        elif (deid_mode == 'lds'):
            final_columns = ['deid_note_id', 'deid_link_note_id', 'ContactNumber', 'ContactDate', 'CreatedDatetime', 'ServiceDatetime', 'deid_pat_id', 'NoteType', 'InpatientNoteType', 'EncounterDate', 'deid_enc_id', 'deid_authoring_provider_id', 'AuthoringProviderType', 'AuthoringProviderSpecialty', 'deid_cosign_provider_id', 'CosignProviderType', 'CosignProviderSpecialty']
        elif (deid_mode == 'phi'):
            final_columns = ['NoteID', 'LinkageNoteID', 'ContactNumber', 'ContactDate', 'CreatedDatetime', 'ServiceDatetime', 'MRN_GNV', 'MRN_JAX', 'NoteType', 'InpatientNoteType', 'EncounterDate', 'EncounterCSN', 'AuthoringProviderKey', 'AuthoringProviderType', 'AuthoringProviderSpecialty', 'CosignProviderKey', 'CosignProviderType', 'CosignProviderSpecialty']
    elif (note_type == 'order'):
        if (deid_mode == 'deid'):
            final_columns = ['deid_order_id', 'Line', 'OrderPlacedDatetime_shifted', 'OrderResultDatetime_shifted', 'deid_pat_id', 'NoteType', 'EncounterDate_shifted', 'deid_enc_id', 'deid_ordering_provider_id', 'OrderingProviderType', 'OrderingProviderSpecialty', 'deid_authorizing_provider_id', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']
        elif (deid_mode == 'lds'):
            final_columns = ['deid_order_id', 'Line', 'OrderPlacedDatetime', 'OrderResultDatetime', 'deid_pat_id', 'NoteType', 'EncounterDate', 'deid_enc_id', 'deid_ordering_provider_id', 'OrderingProviderType', 'OrderingProviderSpecialty', 'deid_authorizing_provider_id', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']
        elif (deid_mode == 'phi'):
            final_columns = ['OrderID', 'Line', 'OrderPlacedDatetime', 'OrderResultDatetime', 'MRN_GNV', 'MRN_JAX', 'NoteType', 'EncounterDate', 'EncounterCSN', 'OrderingProviderKey', 'OrderingProviderType', 'OrderingProviderSpecialty', 'AuthorizingProviderKey', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']
    # import mappings
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    if (deid_mode == 'deid'):
        map_pat = map_pat[['PatientKey', 'deid_pat_id', 'date_shift']]
    else:
        map_pat = map_pat[['PatientKey', 'deid_pat_id']]
    map_enc = pd.read_csv(os.path.join(map_dir, 'map_encounter.csv'))
    map_enc = map_enc[['EncounterCSN', 'deid_enc_id']]
    map_prov = pd.read_csv(os.path.join(map_dir, 'map_provider.csv'))
    map_prov = map_prov[['ProviderKey', 'deid_provider_id']]
    if (note_type == 'order'):
        map_order = pd.read_csv(os.path.join(map_dir, 'map_order.csv'))
        map_order = map_order[['OrderKey', 'deid_order_id']]
    elif (note_type == 'note'):
        map_note = pd.read_csv(os.path.join(map_dir, 'map_note.csv'))
        map_note = map_note[['NoteKey', 'deid_note_id']]
        map_linkage_note = pd.read_csv(os.path.join(map_dir, 'map_note_link.csv'))
        map_linkage_note = map_linkage_note[['LinkageNoteID', 'deid_link_note_id']]

    # merge file with mapping files
    m = 'w'
    h = True
    for df in pd.read_csv(os.path.join(notes_dir, text_file), chunksize=100000):
        df = pd.merge(df, map_pat, how='left', on='PatientKey')
        df = df[df['PatientKey'] > 0]
        df = pd.merge(df, map_enc, how='left', on='EncounterCSN')
        df = df[df['EncounterKey'] > 0]
        if (note_type == 'order'):
            df = pd.merge(df, map_order, how='left', on='OrderKey')
            df = pd.merge(df, map_prov, how='left', left_on='OrderingProviderKey', right_on='ProviderKey')
            df = df.rename(columns={"deid_provider_id": "deid_ordering_provider_id"})
            df = pd.merge(df, map_prov, how='left', left_on='AuthorizingProviderKey', right_on='ProviderKey')
            df = df.rename(columns={"deid_provider_id": "deid_authorizing_provider_id"})
        elif (note_type == 'note'):
            df = pd.merge(df, map_note, how='left', on='NoteKey')
            df = pd.merge(df, map_linkage_note, how='left', on='LinkageNoteID')
            df = pd.merge(df, map_prov, how='left', left_on='AuthoringProviderKey', right_on='ProviderKey')
            df = df.rename(columns={"deid_provider_id": "deid_authoring_provider_id"})
            df = pd.merge(df, map_prov, how='left', left_on='CosignProviderKey', right_on='ProviderKey')
            df = df.rename(columns={"deid_provider_id": "deid_cosign_provider_id"})
        if (deid_mode == 'deid'):
            if (note_type == 'note'):
                df['ContactDate'] = pd.to_datetime(df['ContactDate'])
                df['ContactDate'] = df['ContactDate'].fillna('0')
                df['CreatedDatetime'] = pd.to_datetime(df['CreatedDatetime'])
                df['CreatedDatetime'] = df['CreatedDatetime'].fillna('0')
                df['ServiceDatetime'] = pd.to_datetime(df['ServiceDatetime'])
                df['ServiceDatetime'] = df['ServiceDatetime'].fillna('0')
                df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
                df['EncounterDate'] = df['EncounterDate'].fillna('0')
                df['ContactDate_shifted'] = df.apply(lambda row: row['ContactDate'] + timedelta(days=row['date_shift']) if row['ContactDate'] != '0' else '', axis=1)
                df['CreatedDatetime_shifted'] = df.apply(lambda row: row['CreatedDatetime'] + timedelta(days=row['date_shift']) if row['CreatedDatetime'] != '0' else '', axis=1)
                df['ServiceDatetime_shifted'] = df.apply(lambda row: row['ServiceDatetime'] + timedelta(days=row['date_shift']) if row['ServiceDatetime'] != '0' else '', axis=1)
                df['EncounterDate_shifted'] = df.apply(lambda row: row['EncounterDate'] + timedelta(days=row['date_shift']) if row['EncounterDate'] != '0' else '', axis=1)
            elif (note_type == 'order'):
                df['OrderPlacedDatetime'] = pd.to_datetime(df['OrderPlacedDatetime'])
                df['OrderPlacedDatetime'] = df['OrderPlacedDatetime'].fillna('0')
                df['OrderResultDatetime'] = pd.to_datetime(df['OrderResultDatetime'])
                df['OrderResultDatetime'] = df['OrderResultDatetime'].fillna('0')
                df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
                df['EncounterDate'] = df['EncounterDate'].fillna('0')
                df['OrderPlacedDatetime_shifted'] = df.apply(lambda row: row['OrderPlacedDatetime'] + timedelta(days=row['date_shift']) if row['OrderPlacedDatetime'] != '0' else '', axis=1)
                df['OrderResultDatetime_shifted'] = df.apply(lambda row: row['OrderResultDatetime'] + timedelta(days=row['date_shift']) if row['OrderResultDatetime'] != '0' else '', axis=1)
                df['EncounterDate_shifted'] = df.apply(lambda row: row['EncounterDate'] + timedelta(days=row['date_shift']) if row['EncounterDate'] != '0' else '', axis=1)
        df = df[final_columns]
        df.to_csv(os.path.join(disclosure_dir, text_file), index=False, mode=m, header=h)
        m = 'a'
        h = False
    return


def deid_tsv_note(map_dir, notes_dir, logger: Logger):
    map_note_link = pd.read_csv(os.path.join(map_dir, 'map_note_link.csv'))
    for file_prefix in ['note']:
        # find all files with specified prefix in the name
        pattern = file_prefix + '_.*.tsv'
        in_dir = os.path.join(notes_dir, '{}_{}'.format(cohort, file_prefix))
        final_columns = ['deid_link_note_id', 'note_text']
        items = [f for f in os.listdir(in_dir) if re.match(pattern, f)]
        for file in items:
            logger.info(f"""Processing `file` "{file}".""")
            out_file = 'deid_{}'.format(file)
            m = 'w'
            h = True
            for df in pd.read_csv(os.path.join(in_dir, file), chunksize=100000, sep='\t'):
                df = pd.merge(df, map_note_link, how='left', on='LinkageNoteID')
                df = df[final_columns]
                df.to_csv(os.path.join(in_dir, out_file), index=False, sep='\t', mode=m, header=h)
                m = 'a'
                h = False
    return


def deid_tsv_order(map_dir, notes_dir, logger: Logger):
    map_order = pd.read_csv(os.path.join(map_dir, 'map_order.csv'))
    for file_prefix in ['order_narrative', 'order_impression', 'order_result_comment']:
        # find all files with specified prefix in the name
        pattern = file_prefix + '_.*.tsv'
        in_dir = os.path.join(notes_dir, '{}_{}'.format(cohort, file_prefix))
        if (file_prefix == 'order_result_comment'):
            final_columns = ['deid_order_id', 'LINE', 'note_text']
        else:
            final_columns = ['deid_order_id', 'note_text']
        items = [f for f in os.listdir(in_dir) if re.match(pattern, f)]
        for file in items:
            logger.info(f"""    Processing `file` "{file}".""")
            out_file = 'deid_{}'.format(file)
            m = 'w'
            h = True
            for df in pd.read_csv(os.path.join(in_dir, file), chunksize=100000, sep='\t'):
                df = pd.merge(df, map_order, how='left', on='OrderKey')
                df = df[final_columns]
                df.to_csv(os.path.join(in_dir, out_file), index=False, sep='\t', mode=m, header=h)
                m = 'a'
                h = False
    return


def format_metadata_files(note_type, notes_dir, disclosure_dir):
    # define variables
    text_file = '{}_{}_metadata.csv'.format(cohort, note_type)
    if (note_type == 'note'):
        final_columns = ['NoteID', 'LinkageNoteID', 'ContactNumber', 'ContactDate', 'CreatedDatetime', 'ServiceDatetime', 'MRN_GNV', 'MRN_JAX', 'NoteType', 'InpatientNoteType', 'EncounterDate', 'EncounterCSN', 'AuthoringProviderKey', 'AuthoringProviderType', 'AuthoringProviderSpecialty', 'CosignProviderKey', 'CosignProviderType', 'CosignProviderSpecialty']
    elif (note_type == 'order'):
        final_columns = ['OrderID', 'Line', 'OrderPlacedDatetime', 'OrderResultDatetime', 'MRN_GNV', 'MRN_JAX', 'NoteType', 'EncounterDate', 'EncounterCSN', 'OrderingProviderKey', 'OrderingProviderType', 'OrderingProviderSpecialty', 'AuthorizingProviderKey', 'AuthorizingProviderType', 'AuthorizingProviderSpecialty']
    # read and format the file
    m = 'w'
    h = True
    for df in pd.read_csv(os.path.join(notes_dir, text_file), chunksize=100000):
        df = df[final_columns]
        df.to_csv(os.path.join(disclosure_dir, text_file), index=False, mode=m, header=h)
        m = 'a'
        h = False
    return


def copy_tsv(cohort, notes_dir, disclosure_dir):
    for item in ['note', 'order_narrative', 'order_impression', 'order_result_comment']:
        dir = cohort + '_' + item
        if (os.path.exists(os.path.join(notes_dir, dir))):
            file_list = [f for f in os.listdir(os.path.join(notes_dir, dir))]
            for f in file_list:
                shutil.copy(os.path.join(os.path.join(notes_dir, dir, f)), os.path.join(os.path.join(disclosure_dir, f)))
    return


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
    `COHORT_NAME`: "{COHORT_NAME}"
    `COHORT_FILE`: "{COHORT_FILE}"
    `IRB_NUMBER`: "{IRB_NUMBER}"
    `ID_TYPE`: "{ID_TYPE}"
    `NOTE_VERSION`: "{NOTE_VERSION}"
    `DE_IDENTIFICATION_MODE`: "{DE_IDENTIFICATION_MODE}"
    `SQL_ENCOUNTER_EFFECTIVE_DATE_START`: "{SQL_ENCOUNTER_EFFECTIVE_DATE_START}"
    `SQL_ENCOUNTER_EFFECTIVE_DATE_END`: "{SQL_ENCOUNTER_EFFECTIVE_DATE_END}"

    # Arguments: SQL connection settings
    `USE_WINDOWS_AUTHENTICATION` : "{USE_WINDOWS_AUTHENTICATION}"
    `SERVER`                     : "{SERVER}"
    `DATABASE_PROD`              : "{DATABASE_PROD}"
    `DATABASE_NOTES`             : "{DATABASE_NOTES}"
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
    logger.info(f"""`base_dir` set to "{base_dir}".""")

    # pull metadata
    pull_metadata(note_version, id_type, 'note', sql_dir, data_dir, notes_dir, cohort, logger)
    pull_metadata(note_version, id_type, 'order_narrative', sql_dir, data_dir, notes_dir, cohort, logger)
    pull_metadata(note_version, id_type, 'order_impression', sql_dir, data_dir, notes_dir, cohort, logger)
    pull_metadata(note_version, id_type, 'order_result_comment', sql_dir, data_dir, notes_dir, cohort, logger)

    # split metadata into chunks, so that we can process data in chunks
    split_metadata('note', notes_dir, cohort, logger)
    split_metadata('order_narrative', notes_dir, cohort, logger)
    split_metadata('order_impression', notes_dir, cohort, logger)
    split_metadata('order_result_comment', notes_dir, cohort, logger)

    # pull text in parallel
    pull_text_in_parallel('note', sql_dir, notes_dir, cohort, logger)
    pull_text_in_parallel('order_narrative', sql_dir, notes_dir, cohort, logger)
    pull_text_in_parallel('order_impression', sql_dir, notes_dir, cohort, logger)
    pull_text_in_parallel('order_result_comment', sql_dir, notes_dir, cohort, logger)
    if (deid_mode == 'phi'):

        # copy note_metadata file to disclosure folder
        format_metadata_files('note', notes_dir, disclosure_dir)

        # combine all order metadata files and copy to discosure folder
        combine_order_metadata(notes_dir, cohort)
        format_metadata_files('order', notes_dir, disclosure_dir)

        # copy .tsv files with free text
        copy_tsv(cohort, notes_dir, disclosure_dir)
    else:
        # generate mappings
        generate_map(deid_mode, data_dir, map_dir, 'patient', cohort)
        generate_map(deid_mode, notes_dir, map_dir, 'encounter', cohort)
        generate_map(deid_mode, notes_dir, map_dir, 'note', cohort)
        generate_map(deid_mode, notes_dir, map_dir, 'note_link', cohort)
        generate_map(deid_mode, notes_dir, map_dir, 'order', cohort)
        generate_map(deid_mode, notes_dir, map_dir, 'provider', cohort)

        # deidentify metadata. We can create deidentified dataset or limited dataset.
        deid_metadata(deid_mode, 'note', map_dir, notes_dir, disclosure_dir)
        deid_metadata(deid_mode, 'order', map_dir, notes_dir, disclosure_dir)

        # prepare for text deidentification, i.e., deidentify ID in .tsv file(s)
        deid_tsv_note(map_dir, notes_dir, logger)
        deid_tsv_order(map_dir, notes_dir, logger)

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
