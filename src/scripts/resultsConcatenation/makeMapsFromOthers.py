"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects integer IDs, so no string IDs like Epic Patient IDs.
"""

import argparse
import logging
import os
import pprint
import json
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
from sqlalchemy import URL
# Local packages
from drapi import __version__ as drapiVersion
from drapi.code.drapi.drapi import (choosePathToLog,
                                    ditchFloat,
                                    getTimestamp,
                                    handleDatetimeForJson,
                                    makeDirPath,
                                    makeMap,
                                    makeSetComplement,
                                    successiveParents)
from drapi.code.drapi.constants.phiVariables import (FILE_NAME_TO_VARIABLE_NAME_DICT,
                                                     VARIABLE_NAME_TO_FILE_NAME_DICT)


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("--SETS_PATH",
                        required=True,
                        type=Path,
                        help="The path to the directory that contains the variable set of values for which to create maps.")
    
    # Arguments: Common to the de-identification suite
    parser.add_argument("--IRB_NUMBER")
    parser.add_argument("--CUSTOM_ALIASES",
                        help="""A JSON-formatted string of the form {`ALIAS`: `VARIABLE_NAME`}, where `VARIABLE_NAME` is the BO version of a variable name, and `ALIAS` is an alias of the variable name. An example is {"EncounterCSN": "Encounter # (CSN)"}.""",
                        type=json.loads)

    # Arguments: 
    parser.add_argument("--DEFAULT_ALIASES",
                        help="""Indicates whether to include the default IDR aliases for variables.""",
                        action="store_true")

    # Arguments: Other
    parser.add_argument("--PANDAS_ENGINE",
                        help="""The pandas engine to use when reading data files.""",
                        default="pyarrow",
                        choices=["c",
                                 "none",
                                 "python",
                                 "pyarrow"])

    # Arguments: Meta-parameters
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=int,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    # Arguments: SQL connection settings
    parser.add_argument("--SERVER",
                        default="DWSRSRCH01.shands.ufl.edu",
                        type=str,
                        choices=["Acuo03.shands.ufl.edu",
                                 "EDW.shands.ufl.edu",
                                 "DWSRSRCH01.shands.ufl.edu",
                                 "IDR01.shands.ufl.edu",
                                 "RDW.shands.ufl.edu"],
                        help="")
    parser.add_argument("--DATABASE",
                        default="DWS_PROD",
                        type=str,
                        choices=["DWS_NOTES",
                                 "DWS_OMOP_PROD",
                                 "DWS_OMOP",
                                 "DWS_PROD"],  # TODO Add the i2b2 databases... or all the other databases?
                        help="")
    parser.add_argument("--USER_DOMAIN",
                        default="UFAD",
                        type=str,
                        choices=["UFAD"],
                        help="")
    parser.add_argument("--USERNAME",
                        default=os.environ["USER"],
                        type=str,
                        help="")
    parser.add_argument("--USER_ID",
                        default=None,
                        help="")
    parser.add_argument("--USER_PWD",
                        default=None,
                        help="")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    pass

    # Parsed arguments: Meta-parameters
    LOG_LEVEL = argNamespace.LOG_LEVEL

    # Parsed arguments: SQL connection settings
    SERVER = argNamespace.SERVER
    DATABASE = argNamespace.DATABASE
    USER_DOMAIN = argNamespace.USER_DOMAIN
    USERNAME = argNamespace.USERNAME
    USER_ID = argNamespace.USER_ID
    USER_PWD = argNamespace.USER_PWD
    # <<< `Argparse` arguments <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    pass
    # <<< Argument checks <<<

    # Variables: Path construction: General
    runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    currentWorkingDir = Path(os.getcwd()).absolute()
    projectDir = currentWorkingDir
    dataDir = projectDir.joinpath("data")
    if dataDir:
        inputDataDir = dataDir.joinpath("input")
        intermediateDataDir = dataDir.joinpath("intermediate")
        outputDataDir = dataDir.joinpath("output")
        if intermediateDataDir:
            runIntermediateDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
        if outputDataDir:
            runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
    logsDir = projectDir.joinpath("logs")
    if logsDir:
        runLogsDir = logsDir.joinpath(thisFileStem)
    sqlDir = projectDir.joinpath("sql")

    # Variables: Path construction: Project-specific
    pass

    # Variables: SQL Parameters
    if USER_ID:
        userID = USER_ID[:]
    else:
        userID = fr"{USER_DOMAIN}\{USERNAME}"
    if USER_PWD:
        userPwd = USER_PWD
    else:
        userPwd = os.environ["HFA_UFADPWD"]
    connectionString = URL.create(drivername="mssql+pymssql",
                                  username=userID,
                                  password=userPwd,
                                  host=SERVER,
                                  database=DATABASE)

    # Variables: Other
    pass

    # Directory creation: General
    makeDirPath(runIntermediateDir)
    makeDirPath(runOutputDir)
    makeDirPath(runLogsDir)

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

    logger.info(f"""Begin running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
    logger.info(f"""DRAPI-Lemur version is "{drapiVersion}".""")
    logger.info(f"""All other paths will be reported in debugging relative to the current working directory: "{choosePathToLog(path=projectDir, rootPath=projectDir)}".""")

    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)  # TODO Remove secrets from list to print, e.g., passwords.
    logger.info(f"""Script arguments:\n{argListString}""")

    # >>> Begin script body >>>

    # Get set of values
    # NOTE The code that used to be in this section was moved to "getIDValues.py"
    logging.info(f"""Using the set of new values in the directory "{getIDValuesOutput.absolute().relative_to(rootDirectory)}".""")

    # QA: Make sure all data variables are present in the script parameters.
    collectedVariables = [FILE_NAME_TO_VARIABLE_NAME_DICT[fname.stem] for fname in getIDValuesOutput.iterdir()]
    missingDataTypes = []
    missingVariableSuffixes = []
    for variableName in collectedVariables:
        if variableName not in DATA_TYPES_DICT.keys():
            missingDataTypes.append(variableName)
        if variableName not in VARIABLE_SUFFIXES.keys():
            missingVariableSuffixes.append(variableName)
    if len(missingDataTypes) > 0:
        text = "\n".join(missingDataTypes)
        raise Exception(f"""Not all variables have a data type assigned to them:\n{text}""")
    if len(missingVariableSuffixes) > 0:
        text = "\n".join(missingVariableSuffixes)
        raise Exception(f"Not all variables have a de-identification suffix assigned to them:\n{text}")

    # Create reverse-look-up alias map
    variableAliasesReverse = {}
    for variableAlias, variableMainName in VARIABLE_ALIASES.items():
        if variableMainName in variableAliasesReverse.keys():
            variableAliasesReverse[variableMainName].append(variableAlias)
        else:
            variableAliasesReverse[variableMainName] = [variableAlias]

    # Concatenate all old maps
    oldMaps = {}
    logging.info("""Concatenating all similar pre-existing maps.""")
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        # Get maps explicitely or implicietly referring to this variable name.
        condition1 = variableName in OLD_MAPS_DIR_PATH.keys()
        if condition1:
            variableLookupName = variableName
            logging.info("""    Variable has pre-existing map(s).""")
            listOfMapPaths = OLD_MAPS_DIR_PATH[variableLookupName]
            dfConcat = pd.DataFrame()
            for mapPath in listOfMapPaths:
                logging.info(f"""  ..  Reading pre-existing map from "{mapPath.absolute().relative_to(rootDirectory)}".""")
                df = pd.DataFrame(pd.read_csv(mapPath))
                dfConcat = pd.concat([dfConcat, df])
            oldMaps[variableName] = dfConcat
        if variableName in variableAliasesReverse.keys():
            for variableAlias in variableAliasesReverse[variableName]:
                condition2 = variableAlias in OLD_MAPS_DIR_PATH.keys()
                if condition2:
                    variableLookupName = variableAlias
                    logging.info("""    Variable has pre-existing aliased map(s).""")
                    listOfMapPaths = OLD_MAPS_DIR_PATH[variableLookupName]
                    dfConcat = pd.DataFrame()
                    for mapPath in listOfMapPaths:
                        logging.info(f"""  ..  Reading pre-existing map from "{mapPath}".""")
                        df = pd.DataFrame(pd.read_csv(mapPath))
                        dftemp = makeMap(IDset=set(), IDName=variableName, startFrom=0, irbNumber=IRB_NUMBER, suffix="", columnSuffix=variableName, deIdentificationMapStyle="lemur", logger=logging.getLogger())
                        df.columns = dftemp.columns
                        dfConcat = pd.concat([dfConcat, df])
                    if condition1:
                        df = oldMaps[variableName]
                        dfConcat = pd.concat([dfConcat, df])
                        oldMaps[variableName] = dfConcat
                    else:
                        oldMaps[variableName] = dfConcat
        else:
            condition2 = False
        if not (condition1 or condition2):
            logging.info("""    Variable has no pre-existing map.""")
            oldMaps[variableName] = pd.DataFrame()

    # Get the set difference between all old maps and the set of un-mapped values
    valuesToMap = {}
    setsToMapDataDir = runIntermediateDataDir.joinpath("valuesToMap")
    makeDirPath(setsToMapDataDir)
    logging.info("""Getting the set difference between all old maps and the set of un-mapped values.""")
    for variableName in collectedVariables:
        logging.info(f"""  Working on variable "{variableName}".""")
        variableDataType = DATA_TYPES_DICT[variableName]

        # Get old set of IDs
        logging.info("""    Getting the old set of IDs.""")
        oldMap = oldMaps[variableName]
        oldMap = pd.DataFrame(oldMap)
        if len(oldMap) > 0:
            if variableDataType.lower() == "numeric":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.unique()
                oldIDSet = set([ditchFloat(el) for el in oldIDSet])  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.astype(str)
                oldIDSet = oldIDSet.unique()
            elif variableDataType.lower() == "numeric_or_string":
                oldIDSet = oldMap[variableName]
                oldIDSet = pd.Series(oldIDSet)
                oldIDSet = oldIDSet.astype(str)
                oldIDSet = oldIDSet.unique()
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)
        elif len(oldMap) == 0:
            oldIDSet = set()
        logging.info(f"""    The size of this set is {len(oldIDSet):,}.""")

        # Get new set of IDs
        newSetPath = getIDValuesOutput.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]}.txt")
        logging.info(f"""    Getting the new set of IDs from "{newSetPath.absolute().relative_to(rootDirectory)}".""")
        try:
            setSeries = pd.read_table(newSetPath, header=None)[0]
            newIDSet = set(setSeries.to_list())
        except EmptyDataError as err:
            _ = err
            newIDSet = set()
        if variableDataType.lower() == "numeric":
            newIDSet = set([ditchFloat(el) for el in newIDSet])  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            newIDSet = set([str(el) for el in newIDSet])
        elif variableDataType.lower() == "numeric_or_string":
            newIDSet = set([str(el) for el in newIDSet])
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise Exception(msg)
        logging.info(f"""    The size of this set is     {len(newIDSet):,}.""")

        # Set difference
        IDSetDiff = newIDSet.difference(oldIDSet)
        logging.info(f"""    The set difference size is  {len(IDSetDiff):,}.""")
        valuesToMap[variableName] = IDSetDiff

        # Save new subset to `setsToMapDataDir`
        fpath = setsToMapDataDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]}.JSON")
        with open(fpath, "w") as file:
            if variableDataType.lower() == "numeric":
                li = [ditchFloat(IDNumber) for IDNumber in IDSetDiff]  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                li = list(IDSetDiff)
            elif variableDataType.lower() == "numeric_or_string":
                li = list(IDSetDiff)
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)
            file.write(json.dumps(li, default=handleDatetimeForJson))
        if len(IDSetDiff) == 0:
            series = pd.Series(dtype=int)
        else:
            if variableDataType.lower() == "numeric":
                series = pd.Series(sorted(list(IDSetDiff)))
            elif variableDataType.lower() == "string":
                series = pd.Series(sorted([str(el) for el in IDSetDiff]))
            elif variableDataType.lower() == "numeric_or_string":
                series = pd.Series(sorted([str(el) for el in IDSetDiff]))
            else:
                msg = "The table column is expected to have a data type associated with it."
                logging.error(msg)
                raise Exception(msg)

    # Get numbers for new map
    logging.info("""Getting numbers for new map.""")
    newNumbersDict = {}
    for variableName in collectedVariables:
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldNumbersSet = set(oldMap.iloc[:, 1].values)
        elif len(oldMap) == 0:
            oldNumbersSet = set()
        # Get quantity of numbers needed for map
        quantityOfNumbersUnmapped = len(valuesToMap[variableName])
        # Get new numbers
        lenOlderNumbersSet = len(oldNumbersSet)
        if lenOlderNumbersSet == 0:
            newNumbers = list(range(1, quantityOfNumbersUnmapped + 1))
        else:
            newNumbersSet = makeSetComplement(oldNumbersSet, quantityOfNumbersUnmapped)
            newNumbers = sorted(list(newNumbersSet))
        newNumbersDict[variableName] = newNumbers

    # Map un-mapped values
    logging.info("""Mapping un-mapped values.""")
    for file in setsToMapDataDir.iterdir():
        variableName = FILE_NAME_TO_VARIABLE_NAME_DICT[file.stem]
        variableDataType = DATA_TYPES_DICT[variableName]
        logging.info(f"""  Working on un-mapped values for variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Map contents
        values = valuesToMap[variableName]
        if variableDataType.lower() == "numeric":
            values = set(int(float(value)) for value in values)  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        elif variableDataType.lower() == "numeric_or_string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logging.error(msg)
            raise Exception(msg)
        numbers = sorted(list(newNumbersDict[variableName]))
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values,
                       IDName=variableName,
                       startFrom=numbers,
                       irbNumber=IRB_NUMBER,
                       suffix=deIdIDSuffix,
                       columnSuffix=variableName,
                       deIdentificationMapStyle="lemur",
                       logger=logging.getLogger())
        # Save map
        mapPath = runOutputDir.joinpath(f"{VARIABLE_NAME_TO_FILE_NAME_DICT[variableName]} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # <<< End script body <<<
    logger.info(f"""Finished running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
