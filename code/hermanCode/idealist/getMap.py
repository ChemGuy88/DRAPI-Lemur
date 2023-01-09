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
from hermanCode.hermanCode import sqlite2df, getTimestamp

# Arguments
database_file_name = "deiden_2021-05-01.db"

# Variables
this_file_path = Path(__file__)
project_dir = this_file_path.absolute().parent.parent
irb_dir = project_dir.parent
irbNumber = "IRB201600223"
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
        if False:
            # This is the ideal way to have things running, but it's hard to implement.
            pass
            # driveValue = someFunction(someArguments)  # TODO: Find out what drive contains the current working directory. Make sure it is returned as a `Path` object, so I can use the `joinpath` method below. This works assuming I always run the script from that drive, which is my current standard operating procedure.
            # database_dir = driveValue_asPathObject.joinpath("FILES",
            #                                                 "FTP",
            #                                                 "IDR",
            #                                                 "ANES",
            #                                                 "IRB201600223 - aka R01",
            #                                                 "Deiden_db"  # TODO: Needs the above line first
        elif False:
            pass  # This is workaround # 2, not implemented
            # TODO CD to drive "X:"
            # r"""cd "FTP\IDR\ANES\IRB201600223 - aka R01\On-Demand Requests\2022-12-09 DNR Orders"""  # NOTE The drives are mapped weird
        elif True:
            # This is workaround # 1
            database_dir = input_dir  # TODO: This is the current workaround. Remove this once the two above if-lines are implemented.
    elif operatingSystem == "darwin":
        database_dir = Path(r"/Volumes/FILES/FTP/IDR/ANES/IRB201600223 - aka R01/Deiden_db")
elif True:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    database_dir = input_dir
database_path = Path(os.path.join(database_dir,
                                  database_file_name))

# SQLite connection
sqliteConnection = sqlite3.connect(database_path)
cursor = sqliteConnection.cursor()

# Test connections
if True:
    # SQLite
    print(f"""[{getTimestamp()}] Testing SQLite connection.""")
    query = """SELECT 1"""
    cursor.execute(query)
    test1 = cursor.fetchall()[0][0]
    if test1:
        print(f"""[{getTimestamp()}] SQLite connection successful: "{test1}".""")

# Query de-identification map
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
