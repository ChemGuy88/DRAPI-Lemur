"""
Outline

    - Load the cohort defined in "deiden_2021-05-01.db"
"""

# Private variables ("dunders")
__all__ = ["patientMapDf"]

# Imports
from pathlib import Path
import os
import sqlite3
import sys
# Local imports
from drapi.drapi import sqlite2df, getTimestamp

# Arguments
DATABASE_FILE_NAME = "deiden_2021-05-01.db"
DATABSE_DIR_WINDOWS = os.path.join("X:\\",
                                   "FTP",
                                   "IDR",
                                   "ANES",
                                   "IRB201600223 - aka R01",
                                   "Deiden_db")
DATABSE_DIR_MAC = os.path.join("/",
                               "Volumes",
                               "FILES",
                               "FTP",
                               "IDR",
                               "ANES",
                               "IRB201600223 - aka R01",
                               "Deiden_db")

# Variables
this_file_path = Path(__file__)
project_dir = this_file_path.absolute().parent.parent
irb_dir = project_dir.parent
input_dir = os.path.join(project_dir, "data",
                                      "input")
output_dir = os.path.join(project_dir, "data",
                                       "output")
sql_dir = os.path.join(project_dir, "sql")
run_timestamp = getTimestamp()

# Connect to SQLite database
if True:
    # If you have connection to the below directory, use the below line.
    operatingSystem = sys.platform
    if operatingSystem == "win32":
        database_dir = DATABSE_DIR_WINDOWS
    elif operatingSystem == "darwin":
        database_dir = DATABSE_DIR_MAC
    else:
        raise Exception("Unsupported operating system")
elif True:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    database_dir = input_dir
database_path = Path(os.path.join(database_dir,
                                  DATABASE_FILE_NAME))

# SQLite connection
print(f"""[{getTimestamp()}] Loading sqlite database from "{database_path}".""")
sqliteConnection = sqlite3.connect(database_path)
cursor = sqliteConnection.cursor()


def testSQLiteConection():
    """Test SQLite connection"""
    print(f"""[{getTimestamp()}] Testing SQLite connection.""")
    query = """SELECT 1"""
    cursor.execute(query)
    test1 = cursor.fetchall()[0][0]
    if test1:
        print(f"""[{getTimestamp()}] SQLite connection successful: "{test1}".""")


def getPatientMapDf():
    """Query patient de-identification map"""
    print(f"""[{getTimestamp()}] Running SQLite query.""")
    query = """SELECT
            *
            FROM
            PatientDeidenMap
            WHERE
            active_ind_y_n = 1;"""
    cursor.execute(query)
    patientMapLi = cursor.fetchall()
    print(f"""[{getTimestamp()}] SQLite query completed.""")
    patientMapDf = sqlite2df(patientMapLi, "PatientDeidenMap", cursor)
    patientMapDf["deiden_id_string"] = patientMapDf["deiden_id"].apply(lambda integer: f"IDEALIST_2021-05-01_{integer}")
    return patientMapDf


def getEncounterMapDf():
    """Query patient de-identification map"""
    return


if __name__ == "__main__":
    print("This file not implemented to run as script.")
else:
    testSQLiteConection()
    patientMapDf = getPatientMapDf()
