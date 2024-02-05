"""
Utility functions commonly used in IDR data request projects.
"""

import datetime as dt
import logging
import os
import re
from array import array
from collections.abc import Collection
from datetime import datetime
from datetime import date
from datetime import time
from dateutil.parser import parse
from itertools import islice
from logging import Logger
from pathlib import Path
from typing import Callable, List, Tuple, Union
from typing_extensions import Literal
import sys
# Third-party packages
import numpy as np
import pandas as pd
import sqlalchemy as sa
import sqlite3
from pandas.io.parsers.readers import TextFileReader
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


def makeDirPath(directory_path: str) -> None:
    """
    Check if all directories exists in a path. If not, create them
    """
    path_obj = Path(directory_path)
    paths = list(path_obj.parents)[::-1] + [path_obj]
    for dir in paths:
        if not os.path.exists(dir):
            os.mkdir(dir)


def getTimestamp():
    return dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def getPercentDifference(x, y):
    """
    Calculates a percentage if the denominator is not 0, else it returns `"N/A"`.
    """
    if y != 0:
        return f"{x / y: 0.2%}"
    else:
        return "N/A"


def flatExtend(iterable: Collection) -> list:
    """
    Creates a list from an iterable.
    """
    outputList = []
    for el in iterable:
        outputList.extend(el)
    return outputList


def readDataFile(fname: Path, *args, **kwargs) -> TextFileReader:
    """
    Opens a file based on the file extension of its file name `fname` using a Pandas built-in to return a DataFrame object. Below is the list of Pandas built-ins, whose odcumentation you can search to find out what keyword arguments (`kwargs`) to use.
      - `pd.read_csv`
      - `pd.read_json`
      - `pd.read_xml`
      - `pd.read_excel`
      - `pd.read_hdf`
      - `pd.read_sql`
    """
    suffix = fname.suffix.lower()
    if suffix.endswith(('.csv',)):
        TextFileReaderObject = pd.read_csv(fname, *args, **kwargs)
    elif suffix.endswith(('.tsv',)):
        kwargs["delimiter"] = "\t"
        TextFileReaderObject = pd.read_csv(fname, *args, **kwargs)
    elif suffix.endswith(('.json',)):
        TextFileReaderObject = pd.read_json(fname, *args, **kwargs)
    elif suffix.endswith(('.xml',)):
        TextFileReaderObject = pd.read_xml(fname, *args, **kwargs)
    elif suffix.endswith(('.xls', 'xlsx',)):
        TextFileReaderObject = pd.read_excel(fname, *args, **kwargs)
    elif suffix.endswith(('.hdf',)):
        TextFileReaderObject = pd.read_hdf(fname, *args, **kwargs)
    elif suffix.endswith(('.sql',)):
        TextFileReaderObject = pd.read_sql(fname, *args, **kwargs)
    else:
        raise ValueError(f"""Unsupported filetype for file "{fname}".""")
    return TextFileReaderObject


def successiveParents(pathObj: Path, numLevels: int) -> Tuple[Path, int]:
    """
    Successively get the parents of the Path object submitted.
    """
    while numLevels > 0:
        pathObj = pathObj.parent
        numLevels -= 1
    return pathObj, numLevels


def fileContainsColumn(pathObj: Path, listOfColumns: list) -> bool:
    """
    Determines if the file defined by `pathObj` has any of the columns contained in `listOfColumns`.
    """
    condition = False
    df = pd.read_csv(pathObj, nrows=10)
    columns = df.columns
    for columnName in listOfColumns:
        if columnName in columns:
            condition = True
            break
        else:
            continue
    return condition


def getCommonDirectoryParent(primaryPath: Path, secondaryPath: Path) -> Path:
    """
    """
    commonPrefix = os.path.commonprefix([primaryPath, secondaryPath])
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        if commonPrefix == "/":
            pathResult = primaryPath
        else:
            pathResult = primaryPath.absolute().relative_to(secondaryPath)
    elif operatingSystem == "win32":
        if commonPrefix == "":
            pathResult = primaryPath
        else:
            pathResult = primaryPath.absolute().relative_to(secondaryPath)
    return pathResult


def getFilesToRelease(filesToRelease: List[Path], fileCriteria: List[Callable]):
    """
    Applies the functions in the iterable `fileCriteria` to each Path object in `filesToRelease`.
    """
    filesToRelease = []
    for file in filesToRelease:
        criteria = []
        for criteriaFunc in fileCriteria:
            criteria.append(criteriaFunc(file))
        criteriaMet = all(criteria)
        if criteriaMet:
            filesToRelease.append(file)
        else:
            pass


def getLastIDNum(df, columnName="deid_num"):
    """
    Gets the last ID number in a de-identification map.
    """
    numbers = df[columnName].astype(int)
    return max(numbers)


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
        if "invalid literal for int() with base 10:" in msg:  # This must be an old Python exception message
            return False
        elif "could not convert string to float:" in msg:  # I think this is the new exception message
            return False
        else:
            raise Exception(error)


def fileName2variableName(pathObj):
    """
    """
    pattern = r"^(?P<variableName>.+) map"
    string = pathObj.stem
    obj = re.match(pattern, string)
    if obj:
        groupDict = obj.groupdict()
        variableName = groupDict["variableName"]
    else:
        raise Exception("This file path objected was of an unexpected format.")
    return variableName


def mapGroupCriteria4unknownValue(value):
    """
    Checks if `value` is a number. If so, it checks if it's less than 0. If it's not a number, return `True`.

    This is used in making de-identification maps, where negative ID values are usually used to represent unknown or null values.
    """
    if isNumber(value):
        return float(value) < 0
    else:
        return False


def makeMap(IDset: set,
            IDName: str,
            startFrom: Union[int, list],
            irbNumber: str,
            suffix: str,
            columnSuffix: str,
            logger: Logger,
            groups: dict = {0: {"criteria": [mapGroupCriteria4unknownValue],
                                "deidNum": 0}},
            deIdentificationMapStyle: Literal["classic", "lemur"] = "lemur") -> pd.DataFrame:
    """
    Makes an IDR de-identification map.

    INPUT
        `IDset`, a set of IDs
        `IDName`, the name of the ID
        `startFrom`, the integer number to start from
        `groups`, ID values to group or map in a many-to-one fashion. E.g., invalid IDs (negative numbers) are usually all mapped to the same de-identified number, like "0".
        `deIdentificationMapStyle`, a string, one of {"classic, "lemur"}. The formats are as follow:
            | Format Style  | de-Identififed ID Column Header   |
            | ------------- | -------------------------------   |
            | "clasic"      | `f"deid_{columnSuffix}_id"`       |
            | "lemur"       | `f"de-Identified {IDName}"`       |

    OUTPUT
        `map_`, a Pandas DataFrame with the following format:
        | `IDName` | deid_num   | de-Identififed ID Column Header |
        | -------- | --------   | ------------------------ |
        | IDset[0] | numbers[0] | ... |
        | ...      | ...        | ... |
    """
    # QA: `irbNumber` must not be NoneType
    if isinstance(irbNumber, type(None)):
        raise Exception("""`irbNumber` cannot be of type "None".""")

    # Assign header formats: de-Identififed ID Column Header
    if deIdentificationMapStyle == "classic":
        deIdentificationSerialNumberHeader = "deid_num"
    elif deIdentificationMapStyle == "lemur":
        deIdentificationSerialNumberHeader = "De-identification Serial Number"

    # Assign header formats: de-Identififed ID Column Header
    if deIdentificationMapStyle == "classic":
        deIdentifiedIDColumnHeader = f"deid_{columnSuffix}_id"
    elif deIdentificationMapStyle == "lemur":
        deIdentifiedIDColumnHeader = f"De-identified {IDName}"

    if len(IDset) == 0:
        return pd.DataFrame(columns=[IDName,
                                     deIdentificationSerialNumberHeader,
                                     deIdentifiedIDColumnHeader])
    else:
        pass
    if isinstance(startFrom, int):
        startFrom = startFrom
        numbers = list(range(startFrom, startFrom + len(IDset)))
    elif isinstance(startFrom, list):
        numbers = startFrom[:]
        startFrom = numbers[0]
    numbers.extend([None])
    logger.info("    Sorting `IDset`.")
    IDli = sortIntegersAndStrings(list(IDset))
    logger.info("    Sorting `IDset` - done.")
    logger.info("    Creating `mapDi`.")
    mapDi = {IDNum: {} for IDNum in IDli}
    logger.info("    Creating `mapDi` - done.")
    lenIDli = len(IDli)
    if lenIDli > 100000:
        itChunk = 1000
    else:
        itChunk = max(round(lenIDli / 50), 1)
    for it, IDNum in enumerate(IDli, start=1):
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
                        deIdentificationSerialNumberHeader: deid_num,
                        deIdentifiedIDColumnHeader: deid_id}
        if it % itChunk == 0:
            logger.info(f"  ..  Working on item {it:,} of {len(IDli):,} ({it/lenIDli:.2%} done).")
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


def epicID2patientKey(epicIDlist: List[str]) -> pd.DataFrame:
    """
    Executes a SQL query to map EPIC Patient IDs to Patient Keys.
    """
    IDsAsString = ",".join([f"'{el}'" for el in epicIDlist])
    query = f"""USE DWS_PROD
    SELECT
        dbo.ALL_PATIENTS.PATNT_KEY AS 'Patient Key',
        dbo.ALL_PATIENTS.PATNT_ID AS 'EPIC Patient ID'
    FROM
        dbo.ALL_PATIENTS
    WHERE
        (
        dbo.ALL_PATIENTS.PATNT_ID  IN  ( {IDsAsString}  )
        AND
        ( dbo.ALL_PATIENTS.TEST_IND='N'  )
        )"""
    results = pd.read_sql(query, con=conStr)
    return results


def map2di(map_: pd.DataFrame, fromColumnIndex: int = 0, toColumnIndex: int = 2) -> dict:
    """
    `fromColumnIndex` is the variable to assign as the key to the dictionary.
    `toColumnIndex` is the variable to assign as the value pair in the dictionary.
    Assumes the following structure to "map_":
    column 1      | column 2       | column 3      | ... | column k
        x_(1,1)   |     x_(1,2)    |    x_(1,3)    | ... |   x_(1,k)
        .         |     .          |     .         | ... |   .
        .         |     .          |     .         | ... |   .
        .         |     .          |     .         | ... |   .
        x_(n,1)   |     x_(n,2)    |    x_(n,3)    | ... |   x_(n,k)
    Where the columns are from 1, 2, 3, ..., i, ..., k-1, k, and the rows are from 1, 2, 3, ..., j, ..., n-1, n.
    """
    di = {}
    errors = []
    for _, row in map_.iterrows():
        oldValue = row.values[fromColumnIndex]
        newValue = row.values[toColumnIndex]
        if oldValue in di.keys() and di[oldValue] != newValue:
            errors.append({oldValue: newValue})
        di[oldValue] = newValue
    if len(errors) > 0:
        raise Exception(f"This map is not one to one. At least one ID is duplicated with multiple de-identified IDs: {errors}")
    else:
        return di


def float2str(value: float, navalue="") -> str:
    """
    Converts values to string-type. If a value is NaN it is replaced with a value that can be converted to a string, default empty string, "".
    """
    assert isinstance(navalue, str), """"navalue" is not a string type."""
    if pd.isna(value):
        newValue = str(navalue)
    else:
        newValue = str(int(value))
    return newValue


def numericOrString2integerOrString(value) -> Union[str, int]:
    """
    Determines if a value is numeric or string. If numeric, convert to an integer, else return as string.

    Used by `makeMapsFromOthers.py`
    """
    if isNumber(value):
        return int(float(value))
    else:
        return str(value)


def sortIntegersAndStrings(li: list) -> list:
    """
    Sorts a list of integers and strings by sorted them separately and then concatenating the results.
    """
    series = pd.Series(li)
    maskIntegers = series.apply(lambda el: isinstance(el, int))
    maskStrings = series.apply(lambda el: isinstance(el, str))
    li2 = sorted(series[maskIntegers].to_list()) + sorted(series[maskStrings].to_list())
    return li2


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


def deconstructStudyID(string):
    """
    Deconstructs a de-identified study ID into its component parts, assuming the following format: STUDY-TYPESTUDY-NUMBER_SERIAL-NUMBER
    Where "STUDY_TYPE" is the study type, e.g., "CED", "IRB", or "WIRB"
          "STUDY-NUMBER" is the study serial number, usually a 9-digit number where the first four numbers is a four-digit year.
          "SERIAL-NUMBER" is the de-identified study-specific serial number of a patient or other subject.
    For example: "IRB202300123_222"
    """
    pattern = r"(?P<studyType>\w+)(?P<studyNumber>\d{9})_(?P<PHI_type>\w+)_(?P<deIdentificationNumber>\d+)"
    regexObj = re.search(pattern, string)
    if regexObj:
        di = regexObj.groupdict()
        return di
    else:
        raise Exception("String is of an unexpected format. See function docstring for expected format.")


def studyID2tuple(string):
    """
    Extracts the numeric portion of a string.

    Assumes the following format: STUDY-TYPESTUDY-NUMBER_SERIAL-NUMBER
    Where "STUDY_TYPE" is the study type, e.g., "CED", "IRB", or "WIRB"
          "STUDY-NUMBER" is the study serial number, usually a 9-digit number where the first four numbers is a four-digit year.
          "SERIAL-NUMBER" is the de-identified study-specific serial number of a patient or other subject.
    For example: "IRB202300123_222"

    This is intended for use when sorting columns by the numeric value of the string, and not the text value.
    """
    di = deconstructStudyID(string)
    studyType = di["studyType"]
    studyNumber = int(di["studyNumber"])
    PHI_type = di["PHI_type"]
    deIdentificationNumber = int(di["deIdentificationNumber"])
    tu = studyType, studyNumber, PHI_type, deIdentificationNumber
    return tu


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


def isDatetime(string):
    """
    Checks if a string contains a datetime format.
    """
    try:
        _ = parse(string, fuzzy=False)
        return True
    except ValueError:
        return False


def ditchFloat(value):
    """
    Gets rid of float types if value is string, integer, float, or datetime
    """
    if isinstance(value, str):
        value = str(value)
        if value.isnumeric():
            standardValue = int(value)
        elif isNumber(value):
            standardValue = int(float(value))
        elif isDatetime(value):
            standardValue = parse(value, fuzzy=False)
        else:
            raise ValueError(f"""Unexpected format in string value "{value}". We expected a string with a number, numeric, or datetime format.""")
    elif isinstance(value, int) or isinstance(value, np.integer) or isinstance(value, float):
        standardValue = int(value)
    else:
        raise ValueError(f"""Unexpected data type "{type(value)}" for value "{value}". Expect only string, float, or integers.""")
    return standardValue


def handleDatetimeForJson(obj):
    """
    JSON serializer for objects not serializable by default json code

    h/t to https://stackoverflow.com/a/22238613/5478086
    """
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def makeChunks(array_range: array, chunkSize: int) -> tuple:
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
