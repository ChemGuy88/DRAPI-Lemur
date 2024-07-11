"""
Module that contains the outer (wrapper) function for getting data using SQL queries.
"""

import re
from logging import Logger
from pathlib import Path
from typing_extensions import Union
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages
from drapi.code.drapi.classes import SecretString
from drapi.code.drapi.drapi import (makeChunks,
                                    readDataFile,
                                    replace_sql_query)
from drapi.code.drapi.getData.getData_inner import getData_inner


def getData_outer(connectionString1: SecretString,
                  filterVariableColumnName: str,
                  filterVariableChunkSize: int,
                  filterVariableData: Union[pd.DataFrame, pd.Series],
                  filterVariableFilePath: Union[Path, str],
                  filterVariablePythonDataType: str,
                  filterVariableSqlQueryTemplatePlaceholder: str,
                  outputName: str,
                  queryChunkSize: int,
                  sqlFilePath: Union[Path, str],
                  logger: Logger,
                  downloadData: bool,
                  connectionString2: SecretString,
                  newSQLTable_Database: str,
                  newSQLTable_Name: str,
                  newSQLTable_Schema: str,
                  runOutputDir: Path) -> pd.DataFrame:
    """
    Executes a SQL query with a filter.
    """
    # >>> Determine filter variable data sourcing type: Direct or indirect sourcing >>> NOTE This block is a little rough around the edges. TODO Needs testing.
    # Note -> Direct sourcing
    # Note -> Direct sourcing: Case 1: `filterVariableData` is defined and is a Series
    # Note -> Direct sourcing: Case 2: `filterVariableData` is defined and is a DataFrame and is of width 1
    # Note -> Direct sourcing: Case 3: `filterVariableData` is defined and is a DataFrame and `filterVariableColumnName` is defined
    # Note -> Indirect sourcing
    # Note -> Indirect sourcing: Case 1: `filterVariableFilePath` and `filterVariableColumnName` are defined

    # Determine filter variable data sourcing type: Direct or indirect sourcing: Direct sourcing
    sourcing = None
    if isinstance(filterVariableData, type(None)):
        sourcing = "direct - False"
        sourcingCase = None
    elif isinstance(filterVariableData, (pd.DataFrame)):
        # If-block 1
        if filterVariableData.shape[1] == 1:
            sourcing = "direct"
            sourcingCase = 2
        else:
            sourcingCase = None
        # If-block 2
        if isinstance(filterVariableColumnName,  (str, int)):
            sourcing = "direct"
            sourcingCase = 3
        else:
            sourcing = "direct - False"
            sourcingCase = None
    elif isinstance(filterVariableData, (pd.Series)):
        sourcing = "direct"
        sourcingCase = 1
    else:
        message = f"""The variable `filterVariableData` is of an unexpected data type: "{filterVariableData}"."""
        logger.critical(message)
        raise Exception(message)

    # Determine filter variable data sourcing type: Direct or indirect sourcing: Indirect sourcing
    if sourcing == "direct":
        pass
    else:
        if isinstance(filterVariableFilePath, type(None)) or isinstance(filterVariableColumnName, type(None)):
            sourcing = "indirect - False"
            sourcingCase = None
        elif isinstance(filterVariableFilePath, (Path, str)) and isinstance(filterVariableColumnName, (str, int)):
            sourcing = "indirect"
            sourcingCase = 1
        else:
            message = f"""One of the following variables is of an unexpected data type: `filterVariableData` -> "{type(filterVariableData)}"; `filterVariableColumnName` -> "{type(filterVariableColumnName)}"."""
            logger.critical(message)
            raise Exception(message)
    # <<< Determine filter variable data sourcing type: Direct or indirect sourcing <<<

    # >>> Select filter variable data >>>
    if sourcing == "direct":
        if sourcingCase == 1:
            filterVariableDataSeries = filterVariableData
        elif sourcingCase == 2:
            filterVariableDataSeries = filterVariableData.iloc[:,0]
        elif sourcingCase == 3:
            filterVariableDataSeries = filterVariableData[filterVariableColumnName]
        else:
            message = "An unexpected error occurred when determining the direct sourcing case for the filter variable data. Check the values for `filterVariableData` and `filterVariableColumnName`."
            logger.critical(message)
            raise Exception(message)
    elif sourcing == "indirect":
            dataFrame = readDataFile(fname=Path(filterVariableFilePath))
            filterVariableDataSeries = dataFrame[filterVariableColumnName]
            del dataFrame
    else:
        message = f"""An unexpected error occurred when determinig the filter variable data sourcing type. Check the values for `filterVariableColumnName`, `filterVariableData`, and `filterVariableColumnName`.\nDebugging values:\n`sourcing`: "{sourcing}"\n`sourcingCase`: "{sourcingCase}" """
        logger.critical(message)
        raise Exception(message)
    # <<< Select filter variable data <<<
        
    # Read query file
    with open(sqlFilePath, "r") as file:
        query0 = file.read()

    # Fill out query template
    logger.info("""  Filling out query template.""")

    if filterVariablePythonDataType == "int":
        filterVariableValues = filterVariableDataSeries.drop_duplicates().dropna().astype("int64").sort_values().to_list()
    elif filterVariablePythonDataType == "str":
        filterVariableValues = filterVariableDataSeries.drop_duplicates().dropna().sort_values().to_list()
    else:
        raise Exception(f"""Unexpected value for ``: {type(filterVariablePythonDataType)}.""")

    chunkGenerator1 = makeChunks(filterVariableValues, filterVariableChunkSize)
    chunkGenerator2 = makeChunks(filterVariableValues, filterVariableChunkSize)
    numChunks1 = sum([1 for _ in chunkGenerator1])
    padlen1 = len(str(numChunks1))
    for it1, dfChunk in enumerate(chunkGenerator2, start=1):
        itstring1 = str(it1).zfill(padlen1)
        logger.info(f"""    Working on filter chunk {it1:,} of {numChunks1:,} with `filterVariableChunkSize` "{filterVariableChunkSize:,}".""")

        # Fill query template: lists to strings
        if filterVariablePythonDataType == "int":
            filterVariableValuesAsString = ",".join([f"{el}" for el in dfChunk])
        elif filterVariablePythonDataType == "str":
            filterVariableValuesAsString = ",".join([f"'{el}'" for el in dfChunk])

        # Fill query template: Patch queries that might raise divide-by-zero errors
        query = replace_sql_query(query=query0,
                                  old="""(( ADMIT_EVENT_Derived.NUM_GRAM_WGHT )/1000)/((( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)*(( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)) as "Admit BMI",""",
                                  new="""(( ADMIT_EVENT_Derived.NUM_GRAM_WGHT )/1000)/NULLIF(((( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)*(( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)), 0) as "Admit BMI",""",
                                  logger=logger)
        query = re.sub(pattern=r"""\(\s*cast\(\s*wt.last_wt_oz\s+[asAS]{2}\s+decimal\(10,\s*2\s*\)\s*\)\s*\*\s*0.0283495\s*\)\s*/\s*\(\s*\(cast\s*\(ht.last_ht_in\s+[asAS]{2}\s+decimal\(10,\s*2\s*\)\s*\)\s*\*\s*0.0254\s*\)\s*\*\s*\(cast\(\s*ht.last_ht_in\s+[asAS]{2}\s+decimal\(10,\s*2\)\s*\)\s*\)\s*\*\s*0.0254\s*\)""",
                       repl="(cast(wt.last_wt_oz as decimal(10,2))*0.0283495)/NULLIF(((cast(ht.last_ht_in as decimal(10,2))*0.0254)*(cast(ht.last_ht_in as decimal(10,2)))*0.0254), 0)",
                       string=query)

        # Fill query template: filter
        query = replace_sql_query(query=query,
                                  old=filterVariableSqlQueryTemplatePlaceholder,
                                  new=filterVariableValuesAsString,
                                  logger=logger)

        # Fill query template: Non-download option: New table name, database, and schema
        if downloadData:
            pass
        else:
            query = query.replace("PYTHON_VARIABLE__newSQLTable_Database",
                                newSQLTable_Database)
            query = str(query)  # For type hinting
            query = query.replace("PYTHON_VARIABLE__newSQLTable_Name",
                                newSQLTable_Name)
            query = str(query)  # For type hinting
            query = query.replace("PYTHON_VARIABLE__newSQLTable_Schema",
                                newSQLTable_Schema)
            query = str(query)  # For type hinting

        getData_inner(connectionString1=connectionString1,
                      logger=logger,
                      outputName=outputName,
                      queryChunkSize=queryChunkSize,
                      runOutputDir=runOutputDir,
                      sqlQuery=query,
                      downloadData=downloadData,
                      connectionString2=connectionString2,
                      newSQLTable_Name=newSQLTable_Name,
                      newSQLTable_Schema=newSQLTable_Schema,
                      itstring1=itstring1,
                      numChunks1=numChunks1,
                      sqlFilePath=None)
