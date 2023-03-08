"""
Herman's utility functions commonly used in his projects
"""

import logging
import os
import re
from datetime import datetime as dt
from itertools import islice
from pathlib import Path
from typing import Union
import sys
# Third-party packages
import pandas as pd
import sqlalchemy as sa
import sqlite3
# Local packages
pass

logger = logging.getLogger(__name__)

# SQL Server settings
SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = fr"{USERDOMAIN}\{USERNAME}"
PWD = os.environ["HFA_UFADPWD"]

# SQLAlchemy connections
connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"  # Create connection string
engine = sa.create_engine(connstr)  # Make connection/engine


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    h/t to https://stackoverflow.com/a/39215961/5478086
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


class LoggerWriter:
    """
    h/t to https://stackoverflow.com/a/31688396/5478086
    """

    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        self.level(sys.stderr)


def make_dir_path(directory_path: str) -> None:
    """
    Check if all directories exists in a path. If not, create them
    """
    path_obj = Path(directory_path)
    paths = list(path_obj.parents)[::-1] + [path_obj]
    for dir in paths:
        if not os.path.exists(dir):
            os.mkdir(dir)


def getTimestamp():
    return dt.now().strftime("%Y-%m-%d %H-%M-%S")


def getLastIDNum(df, columnName="deid_num"):
    """
    Gets the last ID number in a de-identification map.
    """
    numbers = df[columnName].astype(int)
    return max(numbers)


def makeMap(IDset: set,
            IDName: str,
            startFrom: int,
            irbNumber: str,
            suffix: str,
            columnSuffix: str) -> pd.DataFrame:
    """
    Makes an IDR de-identification map.

    INPUT
        `IDset`, a set of IDs
        `IDName`, the name of the ID
        `startFrom`, the integer number to start from
    OUTPUT
        `map_`, a Pandas DataFrame with the following format:
    """
    IDli = sorted(list(IDset))
    mapDi = {IDNum: {} for IDNum in IDli}
    deid_num = startFrom
    for IDNum in IDli:
        deid_pat_id = f"{irbNumber}_{suffix}_{deid_num}"
        mapDi[IDNum] = {IDName: IDNum,
                        "deid_num": deid_num,
                        f"deid_{columnSuffix}_id": deid_pat_id}
        deid_num += 1
    newMap = pd.DataFrame.from_dict(mapDi, orient="index")
    newMap.index = range(1, len(newMap) + 1)
    return newMap


def loglevel2int(loglevel: Union[int, str]) -> int:
    """
    An agnostic converter that takes int or str and returns int. If input is int, output is the same as input"""
    dummy = logging.getLogger("dummy")
    dummy.setLevel(loglevel)
    loglevel = dummy.level
    return loglevel


def replace_sql_query(query: str, old: str, new: str, loglevel: Union[int, str] = "INFO") -> str:
    """
    Replaces text in a SQL query only if it's not commented out. I.e., this function applies string.replace() only if the string doesn't begin with "--".
    TODO Don't replace text after "--".
    """
    loglevel_asnumber = loglevel2int(loglevel)
    logger.setLevel(loglevel_asnumber + 10)

    pattern = r"^\w*--"
    li = query.split("\n")
    result = []
    logger.debug("Starting")
    for line in li:
        logger.debug(f"""  Working on "{line}".""")
        obj = re.search(pattern, line)
        if obj:
            logger.debug("    Passing")
            nline = line
        else:
            nline = line.replace(old, new)
            logger.debug(f"""    Replacing text in "{line}" --> "{nline}".""")
        logger.debug("  Appending...")
        result.append(nline)
    logger.debug("Finished")
    return "\n".join(result)


def sqlite2df(tableContents: list, tableName: str, cursor: sqlite3.Cursor) -> pd.DataFrame:
    """
    `tableContents` must be a "*" query where all the columns are returned.
    """
    # Get metadata on table
    query = f"PRAGMA table_info({tableName});"
    cursor.execute(query)
    query_results = cursor.fetchall()
    column_header = [tu[1] for tu in query_results]

    tableContents_asDict = {}
    for it, table_info in enumerate(tableContents):
        di = {}
        for key, value in zip(column_header, table_info):
            di[key] = value
        tableContents_asDict[it] = di
    df = pd.DataFrame.from_dict(tableContents_asDict, orient="index")
    df.index = range(1, len(tableContents) + 1)
    return df


def patient_key_from_person_id(person_id, map_={}):
    """
    Assumes "map_" is a dictionary with person IDs as integers that map patient keys as integers.
    """
    if person_id in map_.keys():
        patient_key = map_[person_id]
        source = 0
    else:
        query = f"""use DWS_OMOP_PROD
        SELECT
            xref.PERSON_MAPPING.person_id as person_id,
            xref.PERSON_MAPPING.patient_key as patient_key
        FROM
            xref.PERSON_MAPPING
        WHERE
            xref.PERSON_MAPPING.person_id IN ({person_id})"""
        results = pd.read_sql(query, engine)
        person_id = results["person_id"][0]
        patient_key = results["patient_key"][0]
        source = 1
    return patient_key, source


def map2di(map_: pd.DataFrame):
    """
    Assumes the following structure to "map_":
    column 1 | column 2 | column 3
        a1   |     1    |    b1
        .    |     .    |     .
        .    |     .    |     .
        .    |     .    |     .
        an   |     n    |    bn
    """
    di = {}
    errors = []
    for _, row in map_.iterrows():
        oldValue, _, newValue = row.values
        if oldValue in di.keys() and di[oldValue] != newValue:
            errors.append({oldValue: newValue})
        di[oldValue] = newValue
    if len(errors) > 0:
        raise Exception(f"This map is not one to one. At least one ID is duplicated with multiple de-identified IDs: {errors}")
    else:
        return di


def isNumber(string):
    """
    Checks if the string represents a number

    For a discussion see https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
    """
    try:
        int(string)
        return True
    except ValueError as error:
        msg = error.args[0]
        if "invalid literal for int() with base 10:" in msg:
            return False


def float2str(value, navalue=""):
    """
    Converts values to string-type. If a value is NaN it is replaced with a value that can be converted to a string, default empty string, "".
    """
    assert isinstance(navalue, str), """"navalue" is not a string type."""
    if pd.isna(value):
        newValue = str(navalue)
    else:
        newValue = str(int(value))
    return newValue


def str2int(value, navalue=-1):
    """
    Converts values to integer-type. If a value is NaN it is replaced with a value that can be converted to an integer, default is "-1".
    """
    assert isinstance(navalue, int), """"navalue" is not an integer type."""
    if pd.isna(value):
        newValue = int(navalue)
    else:
        newValue = int(float(value))
    return newValue


def str2bool(value, navalue=""):
    """
    Converts values to boolean-type. If a value is missing it is replaced with an empty string.
    """
    if pd.isna(value):
        newValue = int(navalue)
    else:
        newValue = bool(value)
    return newValue


def isValidPatientID(value):
    """
    Checks if the value is a valid UFHealth patient ID. Invalid patient IDs are defined as negative integers
    """
    isNumber_bool = isNumber(value)
    if isNumber_bool:
        number = int(value)
        if number < 0:
            result = False
        elif number >= 0:  # Assumes `0` is a valid patient ID
            result = True
    elif not isNumber_bool:
        result = True  # Assumes all non-numeric IDs are valid
    return result


def makeChunks(array_range, chunkSize):
    """
    Inspired by GeekForGeeks.com (https://www.geeksforgeeks.org/break-list-chunks-size-n-python/)

    Doesn't really make chunks of an array, but rather its range. Can be further developed to make chunks of the actual array.

    Example:
    array = range(30)
    chunks = makeChunks(array, chunkSize)
    """
    array_range = iter(array_range)
    return iter(lambda: tuple(islice(array_range, chunkSize)), ())


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>> tree function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# h/t https://stackoverflow.com/a/59109706/5478086

# prefix components:
space = '    '
branch = '│   '
# pointers:
tee = '├── '
last = '└── '


def tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False,
         length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""
    dir_path = Path(dir_path)  # accept string coerceable to Path
    files = 0
    directories = 0

    def inner(dir_path: Path, prefix: str = '', level=-1):
        nonlocal files, directories
        if not level:
            return  # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix + extension, level=level - 1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1
    print(dir_path.name)
    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        print(line)
    if next(iterator, None):
        print(f'... length_limit, {length_limit}, reached, counted:')
    print(f'\n{directories} directories' + (f', {files} files' if files else ''))


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
