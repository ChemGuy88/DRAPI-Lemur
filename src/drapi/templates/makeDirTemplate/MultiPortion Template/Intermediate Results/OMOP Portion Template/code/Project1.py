"""
OMOP Data Pull Script

Please be sure to review the README for this script before running.
"""

__all__ = []

import glob
import logging
import os
import sys
from pathlib import Path
# Third-party libraries
import pandas as pd
import sqlalchemy as sa
import yaml
# Super-local libraries
import drapi.code.drapi.omop.deidentify as deidentify
from drapi.code.drapi.drapi import (makeDirPath,
                                    getTimestamp)
from drapi.code.drapi.omop.configProcessing import (editConfig,
                                                    interpretPath)

# Arguments
LOG_LEVEL = "DEBUG"  # Lowest level available is "9"

# Arguments: SQL server settings
if False:
    # TODO Not implemented. See `db_connect`
    USERNAME_ENVIRONMENT_VARIABLE = "USER"
    PASSWORD_ENVIRONMENT_VARIABLE = "HFA_UFADPWD"
    SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
    DATABASE = "DWS_OMOP_PROD"
    USERDOMAIN = "UFAD"

# Variables
timestamp = getTimestamp()
config_file0 = os.path.join("Config1.yml")
config_file = os.path.join("Data", "Output", "Config2.yml")
editConfig(config_file0, config_file, timestamp)
base_dir = Path(__file__).parent.parent

# Variables: SQL server settings
if False:
    # TODO Not implemented. See `db_connect`
    username = os.environ[USERNAME_ENVIRONMENT_VARIABLE]
    userid = fr"{USERDOMAIN}\{username}"
    userpwd = os.environ[PASSWORD_ENVIRONMENT_VARIABLE]


def db_connect(host, database):
    # SQL Server settings
    SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
    DATABASE = "DWS_OMOP_PROD"
    USERDOMAIN = "UFAD"
    USERNAME = os.environ["USER"]
    UID = fr"{USERDOMAIN}\{USERNAME}"
    PWD = os.environ["HFA_UFADPWD"]
    connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"
    engine = sa.create_engine(connstr)
    return engine


def db_close(db_conn):
    db_conn.dispose()


def import_config():
    try:
        config_setting = yaml.safe_load(open(config_file))
    except Exception as e:
        logging.critical(e)
        sys.exit(1)
    return config_setting


def db_query(query, db_connection):
    dfs = pd.DataFrame()
    for chunk in pd.read_sql(query, db_connection, chunksize=50000):
        df = pd.DataFrame(chunk)
        dfs = dfs.append(df, ignore_index=False)
    return dfs


def db_execute_read_query(host, database, query):
    db_conn = db_connect(host, database)
    data = db_query(query, db_conn)
    db_close(db_conn)
    return data


def db_info(config):
    host = config['db_connections']['data_pull']['server']
    database = config['db_connections']['data_pull']['database']
    schema = config['db_connections']['data_pull']['schema']
    dict_of_dates = config['clinical_data_tables']
    dict_of_search = config['data_selection']
    person_id_file_path = interpretPath(search_config['person_id'])
    start_date = str(search_config['date_range']['start_date'])
    end_date = str(search_config['date_range']['end_date'])
    start_date = "'" + start_date + "'"
    end_date = "'" + end_date + "'"
    try:
        list_of_tables = list(dict_of_dates)
    except TypeError as error:
        message = error.args[0]
        if "object is not iterable" in message:
            list_of_tables = []
        else:
            raise
    return host, database, schema, list_of_tables, dict_of_dates, person_id_file_path, start_date, end_date, search_config, dict_of_search


def person_info_query(search_config):
    person_id_file_path = interpretPath(search_config['person_id'])
    list_of_tables = search_config['person_information_tables']['person_and_death']
    if (list_of_tables):
        for i in range(len(list_of_tables)):
            h = True
            m = 'w'
            current_table = list_of_tables[i]
            columns = search_config.get(current_table)
            columns_string = ', '.join(map(str, columns))
            for person_id in pd.read_csv(person_id_file_path, chunksize=500):
                person_id_list = person_id.iloc[:, 0]
                person_id_list_string = ', '.join(map(str, person_id_list))
                query_string = "SELECT " + columns_string + " FROM " + schema + "." + current_table + " WHERE person_id IN (" + person_id_list_string + ")"
                data = db_execute_read_query(host, database, query_string)
                if not data.empty:
                    identified_file_location_AsString = interpretPath(search_config['data_output']['identified_file_location'])
                    file_location = identified_file_location_AsString + current_table + '.csv'
                    csv_output_file = (file_location)
                    try:
                        data.to_csv(csv_output_file, index=False, header=h, mode=m)
                        h = False
                        m = 'a'
                    except Exception as err:
                        errorMessage = f"{err.__class__.__name__}: {err.__str__()}"
                        message = f"An exception has occurred. This may be caused by an output directory error; please double check the directory in the config file. The actual exception message is below:\n{errorMessage}"
                        logging.error(message)
    list_of_tables = search_config['person_information_tables']['location_table']
    if (list_of_tables and ('person' in search_config['person_information_tables']['person_and_death'])):
        identified_file_location_AsString = interpretPath(search_config['data_output']['identified_file_location'])
        person_file_path = identified_file_location_AsString + 'person.csv'
        h = True
        m = 'w'
        for location_id in pd.read_csv(person_file_path, chunksize=500):
            location_id_list = []
            location_id_list = location_id['location_id']
            location_id_list_string = ', '.join(map(str, location_id_list))
            current_table = list_of_tables[0]
            columns = search_config.get(current_table)
            columns_string = ', '.join(map(str, columns))
            query_string = "SELECT " + columns_string + " FROM " + current_table + " WHERE location_id IN (" + location_id_list_string + ")"
            data = db_execute_read_query(host, database, query_string)
            if not data.empty:
                identified_file_location_AsString = interpretPath(search_config['data_output']['identified_file_location'])
                file_location = identified_file_location_AsString + current_table + '.csv'
                csv_output_file = (file_location)
                try:
                    data.to_csv(csv_output_file, index=False, header=h, mode=m)
                    h = False
                    m = 'a'
                except Exception as err:
                    errorMessage = f"{err.__class__.__name__}: {err.__str__()}"
                    message = f"An exception has occurred. This may be caused by an output directory error; please double check the directory in the config file. The actual exception message is below:\n{errorMessage}"
                    logging.error(message)


def query_attempt(search_config, list_of_tables, dict_of_dates, person_id_file_path, start_date, end_date, dict_of_search):
    numTables = len(list_of_tables)
    for i in range(numTables):
        h = True
        m = 'w'
        h1 = True
        m1 = 'w'
        current_table = list_of_tables[i]
        message = f"""  Working on table "{current_table}", table {i+1} of {numTables}."""
        logging.info(message)
        columns = search_config.get(current_table)
        columns_string = ', '.join(map(str, columns))
        # Get number of chunks of table
        numChunks = sum([1 for _ in pd.read_csv(person_id_file_path, chunksize=500)])
        for it, person_id in enumerate(pd.read_csv(person_id_file_path, chunksize=500), start=1):
            logging.debug(f"""    Working on table chunk {it} of {numChunks}""")
            person_id_list = person_id.iloc[:, 0]
            person_id_list_string = ', '.join(map(str, person_id_list))
            date_sorted_by = dict_of_dates.get(current_table)
            query_string = "(SELECT " + columns_string + " FROM " + current_table + " WHERE person_id IN (" + person_id_list_string + ") AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
            if ((dict_of_search.get(current_table) is not None)):
                row_query_string = ''
                rows = dict_of_search.get(current_table)
                before, sep, after = current_table.partition('_')
                current_key = before
                if (current_table == 'condition_occurrence'):
                    row_query_string = "("
                    for i in range(len(rows)):
                        row_string = rows[i]
                        row_query_string += "(SELECT " + columns_string + " FROM " + current_table + " WHERE " + current_key + "_source_value LIKE '" + row_string + "%' AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
                        if (i != len(rows) - 1):
                            row_query_string += " UNION "
                        else:
                            row_query_string += ")"
                elif (current_table == 'measurement'):
                    rows_string = "', '".join(map(str, rows))
                    row_query_string = "(SELECT " + columns_string + " FROM " + current_table + " WHERE " + current_key + "_source_value IN ('" + rows_string + "') AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
                    if (dict_of_search.get('measurement_laboratory_search') is not None):
                        row_string = "', '".join(map(str, dict_of_search.get('measurement_laboratory_search')))
                        search_query_string = "(SELECT " + columns_string + " FROM " + current_key + " WHERE " + current_key + "_source_value IN ('" + row_string + "') AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
                    else:
                        search_query_string = "(SELECT " + columns_string + " FROM " + current_key + " WHERE " + current_key + "_source_value LIKE '%[0-9]-[0-9]'  AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
                    query = query_string + " INTERSECT " + search_query_string + " ORDER BY person_id, " + date_sorted_by
                    logging.log(9, f"  ..  >>> This is the query >>>\n{query}\n<<< End of query <<<")
                    data1 = db_execute_read_query(host, database, query)
                    identified_file_location_asString = interpretPath(search_config['data_output']['identified_file_location'])
                    file_location = identified_file_location_asString + 'measurement_laboratories.csv'
                    if not data1.empty:
                        csv_output_file = (file_location)
                        try:
                            logging.log(9, f"""  ..  Saving query chunk results to "{csv_output_file}".""")
                            data1.to_csv(csv_output_file, index=False, header=h1, mode=m1)
                            h1 = False
                            m1 = 'a'
                        except Exception as err:
                            errorMessage = f"{err.__class__.__name__}: {err.__str__()}"
                            message = f" . . . . . . .An exception has occurred. This may be caused by an output directory error; please double check the directory in the config file. The actual exception message is below:\n{errorMessage}"
                            logging.error(message)
                else:
                    rows_string = "', '".join(map(str, rows))
                    row_query_string = "(SELECT " + columns_string + " FROM " + current_table + " WHERE " + current_key + "_source_value IN ('" + rows_string + "') AND " + date_sorted_by + " BETWEEN " + start_date + " AND " + end_date + ")"
                query = query_string + " INTERSECT " + row_query_string
                query_string = query
            query_string += " ORDER BY person_id, " + date_sorted_by
            logging.log(9, f"  ..  >>> This is the query >>>\n{query_string}\n<<< End of query <<<")
            data = db_execute_read_query(host, database, query_string)
            if not data.empty:
                identified_file_location_asString = interpretPath(search_config['data_output']['identified_file_location'])
                file_location = identified_file_location_asString + current_table + '.csv'
                csv_output_file = (file_location)
                try:
                    logging.debug(f"""  ..  Saving query chunk results to "{csv_output_file}".""")
                    data.to_csv(csv_output_file, index=False, header=h, mode=m)
                    h = False
                    m = 'a'
                except Exception as err:
                    errorMessage = f"{err.__class__.__name__}: {err.__str__()}"
                    message = f"An exception has occurred. This may be caused by an output directory error; please double check the directory in the config file. The actual exception message is below:\n{errorMessage}"
                    logging.error(message)
        logging.info(f"""  Done processing table "{current_table}".""")


def deidentify_(mapping_file_location):
    data_release = search_config.get('data_release')
    if ('deidentified' in data_release or 'limited' in data_release):
        path = interpretPath(search_config['data_output']['identified_file_location'])
        map_path = interpretPath(search_config['data_output']['mapping_location'])
        all_files = glob.glob(path + "/*.csv")
        map_files = glob.glob(map_path + "/*.csv")
        for file in all_files:
            current_table = os.path.basename(file)
            file_location = search_config['data_output']['deidentified_file_location'] + data_release[0] + "-" + current_table
            deidentified_file = deidentify.shift_person_occurrence(file, map_files, data_release)
            deidentified_file.to_csv(file_location, index=False)


if __name__ == '__main__':
    # Logging block
    loglevel = "DEBUG"
    this_file_path = Path(__file__)
    logpath = os.path.join(base_dir, "logs", f"log {timestamp}.log")
    makeDirPath(Path(logpath).parent)
    fileHandler = logging.FileHandler(logpath)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(loglevel)
    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler,
                                  streamHandler],
                        level=loglevel)

    logging.info("Starting program.")
    # import search configuration
    search_config = import_config()
    # import connection information for DB connection
    host, database, schema, list_of_tables, dict_of_dates, person_id_file_path, start_date, end_date, search_config, dict_of_search = db_info(search_config)

    logging.debug(f"""Reading cohort from `person_id_file_path`: "{person_id_file_path}".""")

    for dataType, path in search_config["data_output"].items():
        path = Path(interpretPath(path))
        makeDirPath(path)

    if (list_of_tables):
        query_attempt(search_config, list_of_tables, dict_of_dates, person_id_file_path, start_date, end_date, dict_of_search)
    person_info_query(search_config)
    # deidentify_(mapping_file_location)
    logging.info("Finished program.")
