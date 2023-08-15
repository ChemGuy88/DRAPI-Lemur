"""
OS-aware settings selection
"""

import os
import platform
import pandas as pd
import sqlalchemy as sa

# Global variables
host = "DWSRSRCH01.shands.ufl.edu"
db = "DWS_PROD"


# Detection of operating system
def match_settings():
    """
    Matches the appropriate driver based on the detected operating system.
    """
    operating_system = getattr(platform.uname(), "system")
    if operating_system.lower() == "darwin":
        DRIVER = "ODBC Driver 13 for SQL Server".replace(" ", "+")
        DRIVER = "ODBC Driver 17 for SQL Server".replace(" ", "+")
        USERDOMAIN = "UFAD"
    elif operating_system.lower() == "windows":
        DRIVER = "SQL Server Native Client 11.0".replace(" ", "+")
        USERDOMAIN = os.environ["USERDOMAIN_ROAMINGPROFILE"]
    di = {"DRIVER": DRIVER,
          "USERDOMAIN": USERDOMAIN}
    return di


SETTINGS = match_settings()

USERDOMAIN = SETTINGS["USERDOMAIN"]
USERNAME = os.environ["USER"]

if False:
    # Regular settings
    DRIVER = "{ODBC Driver 13 for SQL Server}"
    SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
    DATABASE = "DWS_PROD"
    UID = f"{USERDOMAIN}\{USERNAME}"  # or `HFA_UFADUID`
    PWD = os.environ["HFA_UFADPWD"]
elif True:
    # CLARITY settings
    DRIVER = "{SQL Server Native Client 11.0}"
    SERVER = "CLARITYSQLPROD.shands.ufl.edu"  # AKA `HOST`
    DATABASE = "CLARITY"
    UID = os.environ["HFA_CLARITYSVC1UID"]
    PWD = os.environ["HFA_CLARITYSVC1PWD"]

# DRIVER, SERVER, DATABASE, UID, PWD = getSettings()

# Create connection string
connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"
# connstr = f'mssql://{host}/{db}?driver=SQL+Server+Native+Client+11.0'

# Make connection/engine
engine = sa.create_engine(connstr)

# Test connection
query = """SELECT 1"""
result1 = pd.read_sql(query, engine)

if result1.iloc[0, 0] == 1:
    print("Connection test was a success")

# Confirm login user identity
result2 = pd.read_sql("SELECT SYSTEM_USER", engine)
result2_value = result2.iloc[0, 0]
if result2_value:
    print(f"Logged in as `{result2_value}`")

# Get server version
if True:
    query = "SELECT @@VERSION"
    result3 = pd.read_sql(query, engine)
    result3_value = result3.iloc[0, 0]
    print(result3_value)

# Close connections
if True:
    engine.dispose()
    numConnections = engine.pool.checkedin()
    if numConnections == 0:
        print("Connections have been closed")
    elif numConnections > 0:
        print("Connections are still open")
