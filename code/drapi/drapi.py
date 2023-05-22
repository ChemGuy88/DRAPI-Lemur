"""
Herman's utility functions commonly used in his projects
"""

import logging
import os
import re
from datetime import datetime as dt
from itertools import islice
from pathlib import Path
from typing import List, Tuple, Union
from typing_extensions import Literal
import sys
# Third-party packages
import numpy as np
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
conStr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"  # Create connection string
engine = sa.create_engine(conStr)  # Make connection/engine


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


def successiveParents(pathObj: Path, numLevels: int) -> Tuple[Path, int]:
    """
    Successively get the parents of the Path object submitted.
    """
    while numLevels > 0:
        pathObj = pathObj.parent
        numLevels -= 1
    return pathObj, numLevels


def getLastIDNum(df, columnName="deid_num"):
    """
    Gets the last ID number in a de-identification map.
    """
    numbers = df[columnName].astype(int)
    return max(numbers)


def makeMap(IDset: set,
            IDName: str,
            startFrom: Union[int, list],
            irbNumber: str,
            suffix: str,
            columnSuffix: str,
            groups: dict = {0: {"criteria": [lambda x: x < 0],
                                "deidNum": 0}}) -> pd.DataFrame:
    """
    Makes an IDR de-identification map.

    INPUT
        `IDset`, a set of IDs
        `IDName`, the name of the ID
        `startFrom`, the integer number to start from
        `groups`, ID values to group or map in a many-to-one fashion. E.g., invalid IDs (negative numbers) are usually all mapped to the same de-identified number, like "0".
    OUTPUT
        `map_`, a Pandas DataFrame with the following format:
        | `IDName` | deid_num   | deid_{`columnSuffix`}_id |
        | -------- | --------   | ------------------------ |
        | IDset[0] | numbers[0] | ... |
        | ...      | ...        | ... |
    """
    if len(IDset) == 0:
        return pd.DataFrame(columns=[IDName, "deid_num", f"deid_{columnSuffix}_id"])
    else:
        pass
    if isinstance(startFrom, int):
        startFrom = startFrom
        numbers = list(range(startFrom, startFrom + len(IDset)))
    elif isinstance(startFrom, list):
        numbers = startFrom[:]
        startFrom = numbers[0]
    numbers.extend([None])
    IDli = sorted(list(IDset))
    mapDi = {IDNum: {} for IDNum in IDli}
    for IDNum in IDli:
        fromGroup = False
        for group, groupAttributes in groups.items():
            criteriaList = groupAttributes["criteria"]
            criteria = [criterion(IDNum) for criterion in criteriaList]
            if all(criteria):
                deid_num = groupAttributes["deidNum"]
                fromGroup = True
                break
        if fromGroup:
            pass
        else:
            deid_num = numbers.pop(0)
        deid_id = f"{irbNumber}_{suffix}_{deid_num}"
        mapDi[IDNum] = {IDName: IDNum,
                        "deid_num": deid_num,
                        f"deid_{columnSuffix}_id": deid_id}
    newMap = pd.DataFrame.from_dict(mapDi, orient="index")
    newMap.index = range(1, len(newMap) + 1)
    return newMap


def makeSetComplement(set1, cardinalityOfNewSet):
    """
    Creates a complement to a set, based on the specified size of the complement. Elements of the first set are assumed to be integers from 1 and above, and cardinalities are non-zero positive integers.

    TODO: Implement empty set handling
    """
    set1Min = 1
    if len(set1) == 0:
        raise ValueError("Set should not be empty.")
    else:
        set1Max = max(set1)
    s1Contiguous = set(range(set1Min, set1Max + 1))
    setDifference = s1Contiguous.difference(set1)
    cardinalityOfSetDifference = len(setDifference)
    cardinalityOfContiguousSubset = cardinalityOfNewSet - cardinalityOfSetDifference
    if cardinalityOfContiguousSubset > 0:
        setDifferenceSubset = setDifference
        contiguousSubset = set(range(set1Max + 1, set1Max + cardinalityOfContiguousSubset + 1))
    elif cardinalityOfContiguousSubset == 0:
        setDifferenceSubset = setDifference
        contiguousSubset = set()
    elif cardinalityOfContiguousSubset < 0:
        setDifferenceSubset = set(list(setDifference)[:cardinalityOfNewSet])
        contiguousSubset = set()
    newSet = setDifferenceSubset.union(contiguousSubset)
    return newSet


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


def patient_key_from_person_id(person_id: int, map_: dict = {}) -> Tuple[int, Literal[0, 1]]:
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
        results = pd.read_sql(query, con=conStr)
        person_id = results["person_id"][0]
        patient_key = results["patient_key"][0]
        source = 1
    return patient_key, source


def personIDs2patientKeys(personIDList: List[int]) -> pd.DataFrame:
    """

    """
    list2str = ",".join([str(num) for num in personIDList])
    query = f"""use DWS_OMOP_PROD
    SELECT
        xref.PERSON_MAPPING.person_id as person_id,
        xref.PERSON_MAPPING.patient_key as patient_key
    FROM
        xref.PERSON_MAPPING
    WHERE
        xref.PERSON_MAPPING.person_id IN ({list2str})"""
    results = pd.read_sql(query, con=conStr)
    return results


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
        oldValue, _, newValue, *_ = row.values
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
        int(float(string))
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


def str2intOr0(string):
    """
    Converts a string to its numeric value, or 0, if it has no numeric value.
    """
    if string.isnumeric():
        return int(string)
    else:
        return 0


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


def ditchFloat(value):
    """
    Gets rid of float types if value is string, integer, or float.
    """
    if isinstance(value, str):
        value = str(value)
        if value.isnumeric():
            standardValue = int(value)
        elif isNumber(value):
            standardValue = int(float(value))
        else:
            raise ValueError(f"""Unexpected data type "{type(value)}" for value "{value}". Expect only string, float, or integers.""")
    elif isinstance(value, int) or isinstance(value, np.integer) or isinstance(value, float):
        standardValue = int(value)
    else:
        raise ValueError(f"""Unexpected data type "{type(value)}" for value "{value}". Expect only string, float, or integers.""")
    return standardValue


def makeChunks(array_range, chunkSize):
    """
    Inspired by GeekForGeeks.com (https://www.geeksforgeeks.org/break-list-chunks-size-n-python/)

    Only makes chunks of one dimensional arrays (e.g., lists, Pandas Series), but not dataframes.

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


def tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False,
         length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""
    # prefix components:
    space = '    '
    branch = '│   '
    # pointers:
    tee = '├── '
    last = '└── '

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