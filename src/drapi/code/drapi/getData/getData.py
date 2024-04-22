"""
Script template to download data using SQL queries.
"""

import logging
from pathlib import Path
from typing import Union
# Third-party packages
import pandas as pd
# First-party packages
from drapi.code.drapi.getData.getData_inner import getData_inner
from drapi.code.drapi.getData.getData_outer import getData_outer

# Functions


def getData(sqlFilePath: Union[Path, str],
            connectionString: str,
            filterVariablePythonDataType: str,
            filterVariableSqlQueryTemplatePlaceholder: str,
            logger: logging.Logger,
            outputFileName: str,
            runOutputDir: Union[Path, str],
            filterVariableChunkSize: int = 1000,
            filterVariableColumnName: str = None,
            filterVariableData: Union[pd.DataFrame, pd.Series] = None,
            filterVariableFilePath: Union[Path, str] = None,
            queryChunkSize: int = 10000):
    """
    Efficiently download data based on a SQL query. Can filter query by one variable.
    """
    # >>> Determine if we're filtering >>>
    # Case 1: We have both `filterVariableFilePath` and `filterVariableColumnName` defined
    # Case 2: We have `filterVariableData` defined.
    # Case 3: Neither case 1 nor case 2
    # Determine if we're filtering: Determine filter type
    # Determine if we're filtering: Determine filter type: Case 1
    if isinstance(filterVariableFilePath, (str, Path)) and isinstance(filterVariableColumnName, (str, int)):
        useFilteringCase1 = True
    else:
        useFilteringCase1 = False
    # Determine if we're filtering: Determine filter type: Case 2
    if isinstance(filterVariableData, (pd.Series, pd.DataFrame)):
        useFilteringCase2 = True
    else:
        useFilteringCase2 = False
    # Determine if we're filtering: Determine filter type: Ambiguous case: case 1 and 2
    if useFilteringCase1 and useFilteringCase2:
        message = "Ambiguous argument input. If you want to filter your query by a variable, you must either (1) pass the variable as a Pandas Series or DataFrame or (2) pass the (2.a) path to the file that contains the data and the (2.b.) column name of the variable."
        logger.critical(message)
        raise Exception(message)
    # Determine if we're filtering: Make decision
    if useFilteringCase1:
        useFiltering = True
    elif useFilteringCase2:
        useFiltering = True
    elif (not useFilteringCase1) and (not useFilteringCase2):
        useFiltering = False
    else:
        message = "An unexpected error occurred."
        logger.critical(message)
        raise Exception(message)
    # <<< Determine if we're filtering <<<

    # Choose core function
    if not useFiltering:
        getData_inner(conStr=connectionString,
                      logger=logger,
                      outputName=outputFileName,
                      queryChunkSize=queryChunkSize,
                      runOutputDir=runOutputDir,
                      sqlQuery=None,
                      itstring1=None,
                      numChunks1=None,
                      sqlFilePath=sqlFilePath)
    elif useFiltering:
        getData_outer(conStr=connectionString,
                      filterVariableColumnName=filterVariableColumnName,
                      filterVariableChunkSize=filterVariableChunkSize,
                      filterVariableData=filterVariableData,
                      filterVariableFilePath=filterVariableFilePath,
                      filterVariablePythonDataType=filterVariablePythonDataType,
                      filterVariableSqlQueryTemplatePlaceholder=filterVariableSqlQueryTemplatePlaceholder,
                      logger=logger,
                      outputName=outputFileName,
                      queryChunkSize=queryChunkSize,
                      runOutputDir=runOutputDir,
                      sqlFilePath=sqlFilePath)
    else:
        message = "An unexpected error occurred."
        logger.critical(message)
        raise Exception(message)
    return
