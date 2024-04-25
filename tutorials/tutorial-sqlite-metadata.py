"""
How to access the metadata in a SQLite database

This uses IDEALIST de-identification database as an example.
"""

from pathlib import Path
import os
import re
import sys
# Third-party packages
import sqlite3
# Local imports
from drapi.code.drapi.drapi import sqlite2df, getTimestamp

# Arguments
DATABSE_PATH_MAC = Path("/Volumes/FTP/IDR/ANES/IRB201600223 - aka R01/Deiden_db/deiden_2021-05-01_0.db")
DATABSE_PATH_WINDOWS = Path("")  # TODO

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
        database_path = Path(DATABSE_PATH_WINDOWS)
    elif operatingSystem == "darwin":
        database_path = Path(DATABSE_PATH_MAC)
    else:
        raise Exception("Unsupported operating system")
elif True:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    database_path = input_dir


def getDeidenDBSeriesNumber(string):
    """
    Regular expression to get the series number from the IDEALIST encounter de-identification database file.

    Expects files to be of the format "deiden_YYYY-MM-DD_XX.db", where YYYY is the year four-digit year, MM is the two-digit month, DD is the two-digit day, and XX is the series number (with no zero padding).
    """
    seriesNumber = re.search(r"_(\d+).db$", string).groups(0)[0]
    return seriesNumber


# SQLite connection
print(f"""Loading sqlite database from "{database_path}".""")
sqliteConnection = sqlite3.connect(database_path)
cursor = sqliteConnection.cursor()

# Test SQLite connection
print(f"""[{getTimestamp()}] Testing SQLite connection.""")
query = """SELECT 1"""
cursor.execute(query)
test1 = cursor.fetchall()[0][0]
if test1:
    print(f"""[{getTimestamp()}] SQLite connection successful: "{test1}".""")

# Query database metadata
print(f"""[{getTimestamp()}] Running SQLite query for encounter map.""")
query = """SELECT *
FROM sqlite_master"""
cursor.execute(query)
resultsList = cursor.fetchall()
print(f"""[{getTimestamp()}] SQLite query completed.""")
results = sqlite2df(resultsList, "sqlite_master", cursor)  # NOTE that `sqlite2df` automatically gets the metadata. See the function definition for details.

print(f"""[{getTimestamp()}] Done running "{this_file_path}".""")