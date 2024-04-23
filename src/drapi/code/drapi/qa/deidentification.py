"""
QA: Make sure values were correctly converted.

# TODO Handle headers for aliased variables. Currently when tables are concatenated for the same variable but with different aliases, each alias is stored in a separate column. This can be done under `combineMaps`.
"""

import logging
from pathlib import Path
from typing_extensions import (Dict,
                               List,
                               Tuple,
                               Union)
# Third-party packages
import pandas as pd
from pandas.api.types import (is_numeric_dtype,
                              is_object_dtype)
# First-party packages
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getMapType)
from drapi.code.drapi.constants.constants import DE_IDENTIFICATION_PREFIXES


# Functions
def iterateOverFiles(listOfFiles: List[Union[str, Path]],
                     SCRIPT_TEST_MODE: bool,
                     logger: logging.Logger,
                     directoryName: Union[str, None] = None) -> pd.DataFrame:
    """
    """  # TODO Parallelize
    di = {}
    it1Total = len(listOfFiles)
    for it1, fpath in enumerate(listOfFiles, start=1):
        logger.info(f"""  Working on file {it1:,} of {it1Total:,}: "{fpath.name}".""")
        if SCRIPT_TEST_MODE:
            pass
        else:
            df = pd.read_csv(fpath, low_memory=False)
            result = getMapType(df=df)
            di[it1] = {"Directory": directoryName,
                       "File Name": fpath.name,
                       "Result": result}
    dfresult = pd.DataFrame.from_dict(data=di, orient="index")
    return dfresult


def qaListOfFilesAndDirectories(LIST_OF_FILES: List[Union[str, Path]],
                                LIST_OF_DIRECTORIES: List[Union[str, Path]],
                                SCRIPT_TEST_MODE: bool,
                                logger: logging.Logger):
    """
    """
    # Sort input alphabetically for easier debugging.
    if LIST_OF_FILES:
        listOfFiles1 = sorted([Path(fpath) for fpath in LIST_OF_FILES])
    else:
        listOfFiles1 = []
    if LIST_OF_DIRECTORIES:
        listOfDirectories = sorted([Path(dpath) for dpath in LIST_OF_DIRECTORIES])
    else:
        listOfDirectories = []

    # Work on files first
    dfresult1 = iterateOverFiles(listOfFiles=listOfFiles1,
                                 SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                 directoryName=None)

    # Work on directories
    resultsli = []
    for dpath in listOfDirectories:
        logger.info(f"""  Working on directory "{dpath.name}".""")
        listOfFiles2 = sorted(list(dpath.iterdir()))
        dfresult2 = iterateOverFiles(listOfFiles=listOfFiles2,
                                     SCRIPT_TEST_MODE=SCRIPT_TEST_MODE,
                                     directoryName=dpath.name)
        resultsli.append(dfresult2)

    dfresult = pd.concat([dfresult1] + resultsli, axis=0)
    return dfresult


def standardizeMapHeaders(dataFrame: pd.DataFrame,
                          variableAliases: Dict[str, str],
                          logger: logging.Logger) -> pd.DataFrame:
    """
    """
    TABLE_WIDTH = 2  # We assume the intermediate and final maps have only two columns.
    df = dataFrame
    columns = df.columns
    columnHeader1, columnHeader2 = columns
    if columnHeader1 in variableAliases.keys():
        identifiedVariableNameIndex = 0
        standardVariableName = variableAliases[columnHeader1]
    elif columnHeader2 in variableAliases.keys():
        identifiedVariableNameIndex = 1
        standardVariableName = variableAliases[columnHeader2]
    elif columnHeader1 in variableAliases.values():
        standardVariableName = columnHeader1
        identifiedVariableNameIndex = 0
    elif columnHeader2 in variableAliases.values():
        identifiedVariableNameIndex = 1
        standardVariableName = columnHeader2
    else:
        logger.warning(f"""Assuming variable is not aliased. Map columns were\n{columns}\nVariable aliases were\n{variableAliases}""")
        if any([columnHeader1.lower().startswith(prefix.lower()) for prefix in DE_IDENTIFICATION_PREFIXES.values()]):
            standardVariableName = columnHeader2
            identifiedVariableNameIndex = 1
        elif any([columnHeader2.lower().startswith(prefix.lower()) for prefix in DE_IDENTIFICATION_PREFIXES.values()]):
            standardVariableName = columnHeader1
            identifiedVariableNameIndex = 0
        else:
            raise Exception("This should not happen.")
    identifiedVariableName = columns[identifiedVariableNameIndex]
    # Standardize variable names: Deduce de-identified variable name location
    li = list(range(TABLE_WIDTH))
    li.pop(identifiedVariableNameIndex)
    deidentifiedVariableNameIndex = li[0]
    # Standardize variable names: Determine if de-identified variable contains standard or aliased name
    deidentifiedVariableName = columns[deidentifiedVariableNameIndex]
    deidentifiedVariableName = str(deidentifiedVariableName)
    deidentifiedVariableNameIsStandardized = standardVariableName in deidentifiedVariableName
    if deidentifiedVariableNameIsStandardized:
        newDeidentifiedVariableName = deidentifiedVariableName[:]
    else:
        # Determine which non-standard name is being used
        nameInAlias = False
        variableAliasesList = sorted(list(variableAliases.keys()),
                                     key=lambda string: len(string),
                                     reverse=True)
        for variableAlias in variableAliasesList:
            if variableAlias in deidentifiedVariableName:
                nameInAlias = variableAlias[:]
                break
            else:
                pass
        if not nameInAlias:
            if standardVariableName in deidentifiedVariableName:
                nameInAlias = standardVariableName
            else:
                raise Exception(f"""We were not able to deduce the identified version of the de-identified variable name.""")
        else:
            pass
        newDeidentifiedVariableName = deidentifiedVariableName.replace(nameInAlias,
                                                                       standardVariableName)
    # Standardize variable names: Rename variables
    df = df.rename(columns={identifiedVariableName: standardVariableName,
                            deidentifiedVariableName: newDeidentifiedVariableName})
    # Standardize order
    df = df[[standardVariableName, newDeidentifiedVariableName]]
    return df


def conformDataTypes(dataFrame: pd.DataFrame,
                     dataTypesDict: Dict[str, str],
                     logger=logging.Logger) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Converts dataframe datatypes according to what the IDR typically uses.
    """
    _ = logger
    df = dataFrame
    feedback = {}
    for it, variableName in enumerate(df.columns.to_list(), start=1):
        logger.info(f"""  Working on variable "{variableName}".""")
        if variableName in dataTypesDict.keys():
            # Lookup variable Python data type
            variableDataType0 = dataTypesDict[variableName]
            if variableDataType0.lower() == "numeric":
                variableDataType = "Int64"
            elif variableDataType0.lower() == "numeric_or_string":
                variableDataType = str
            elif variableDataType0.lower() == "string":
                variableDataType = str
            else:
                raise Exception("This should not happen")
            # Standardize Python data type # TODO We don't need this if the input data is clean, i.e., all values are of the same data type, e.g., there are no headers in the rows.
            if False:
                if variableDataType == str:
                    df[variableName] = df[variableName].astype(variableDataType)
                elif variableDataType == "Int64":
                    if is_numeric_dtype(df[variableName]):
                        df[variableName] = df[variableName].astype(variableDataType)
                    elif is_object_dtype(df[variableName]):
                        df[variableName] = df[variableName].astype(float).astype(variableDataType)
                    else:
                        raise Exception(f"""Encountered unexpected Pandas data type: "{df[variableName].dtypes}".""")
                else:
                    raise Exception(f"""Encountered unexpected data type: "{variableDataType}".""")
            elif True:
                dt1 = df[variableName].dtype
                logger.info(f"""    Converting data type from "{dt1}" to "{variableDataType}".""")
                df[variableName] = df[variableName].astype(variableDataType)
            result = True
        else:
            result = False
        feedback[it] = {"Column": variableName,
                        "Converted": result}
    feebackdf = pd.DataFrame.from_dict(data=feedback,
                                       orient="index")
    return df, feebackdf


def combineMaps(listOfDirectories: List[str],
                mode: int,
                variableAliases: Dict[str, str],
                dataTypesDict: Dict[str, str],
                runIntermediateDir: Path,
                runOutputDir: Path,
                rootPath: Path,
                rootDirectory: Path,
                logger: logging.Logger) -> List[Path]:
    """
    for `mode` = 1, assumes `listOfDirectories` is a tree with depth of 3, e.g. the "Maps by Portion" folder with the following structure:
    - Maps by Portion
        - Portion 1
            - Variable 1
                - CSV File 1
                - CSV File 2
                - etc.
            - Variable 2
                - CSV File 1
                - CSV File 2
                - etc.
            - etc.
        - Portion 2
            - Variable 1
                - CSV File 1
                - CSV File 2
                - etc.
            - Variable 2
                - CSV File 1
                - CSV File 2
                - etc.
            - etc.
        - etc.
    For `mode` = 2, assumes `listOfDirectories` is a tree with depth of 2.
    """
    listOfDirectories1 = sorted(list(listOfDirectories))
    dictOfVariables = {}
    it1 = 1
    for dpathString in listOfDirectories1:
        dpath = Path(dpathString)
        listOfVariables = sorted(list(dpath.iterdir()))
        for fpath1 in listOfVariables:
            variableDirName = fpath1.name
            if mode == 1:
                listOfFiles = sorted([fpath for fpath in fpath1.iterdir() if not fpath.name.startswith(".")])
                diNew = {it: {"Variable Name": variableDirName,
                              "File Path": fpath} for it, fpath in enumerate(listOfFiles, start=it1)}
            elif mode == 2:
                listOfFiles = [fpath1]
                diNew = {it: {"Variable Name": fpath.stem,
                              "File Path": fpath} for it, fpath in enumerate(listOfFiles, start=it1)}
            it1 += len(listOfFiles)
            dictOfVariables.update(diNew)

    dfAllPaths = pd.DataFrame.from_dict(data=dictOfVariables, orient="index")
    dfAllPaths.index.name = "Index"
    dfAllPaths = dfAllPaths.sort_values(by=["Variable Name", "File Path"])
    savePathAllPaths = runOutputDir.joinpath("Paths for All Maps.CSV")
    dfAllPaths.to_csv(path_or_buf=savePathAllPaths)

    # Combine maps by variable name
    listOfVariableNames = dfAllPaths["Variable Name"].drop_duplicates()
    it2Total = len(listOfVariableNames)
    savePathDir = runOutputDir.joinpath("Combined Maps", "By Variable")
    savePathDir.mkdir(parents=True)
    listOfPathsForCombinedMaps = []
    header = True
    for it2, variableName in enumerate(listOfVariableNames, start=1):
        logger.info(f"""  Working on variable {it2:,} of {it2Total:,}: "{variableName}".""")
        mask = dfAllPaths["Variable Name"] == variableName
        listOfPaths = dfAllPaths["File Path"][mask].to_list()
        it3Total = len(listOfPaths)
        listOfDataFramesPath = runIntermediateDir.joinpath(variableName)
        for it3, fpath in enumerate(listOfPaths, start=1):
            logger.info(f"""    Working on file {it3:,} of {it3Total:,}: "{choosePathToLog(path=fpath, rootPath=rootPath)}".""")
            df = pd.read_csv(filepath_or_buffer=fpath,
                             engine="pyarrow")
            # Standardize variable names
            df = standardizeMapHeaders(dataFrame=df,
                                       variableAliases=variableAliases,
                                       logger=logger)

            # TODO Remove this line, and fix upstream
            df = df.dropna(how="any")

            # Standardize Python data type
            df, _ = conformDataTypes(dataFrame=df,
                                     dataTypesDict=dataTypesDict,
                                     logger=logger)

            # Write results
            df.to_csv(path_or_buf=listOfDataFramesPath,
                      index=False,
                      mode="a",
                      header=header)
            header = False

        # Read file
        dfAllUnique = pd.read_csv(filepath_or_buffer=listOfDataFramesPath,
                                  low_memory=False)
        # Standardize Python data type
        df, _ = conformDataTypes(dataFrame=dfAllUnique,
                                 dataTypesDict=dataTypesDict,
                                 logger=logger)
        # Drop duplicates
        dfAllUnique = dfAllUnique.drop_duplicates()
        # Save results
        savePath = savePathDir.joinpath(f"{variableName}.CSV")
        logger.info(f"""    Saving combined maps to "{choosePathToLog(path=savePath, rootPath=rootDirectory)}".""")
        dfAllUnique.to_csv(path_or_buf=savePath,
                           index=False)
        listOfPathsForCombinedMaps.append(savePath)

    return listOfPathsForCombinedMaps
