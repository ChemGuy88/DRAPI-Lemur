"""
Module that contains the inner function for getting data using SQL queries.
"""

from logging import Logger
from pathlib import Path
from typing_extensions import Union
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages
from drapi.code.drapi.classes import SecretString


def getData_inner(connectionString1: str,
                  logger: Logger,
                  queryChunkSize: int,
                  runOutputDir: Path,
                  sqlQuery: Union[None, str],
                  downloadData: bool,
                  connectionString2: SecretString = None,
                  newSQLTable_Name: str = None,
                  newSQLTable_Schema: str = None,
                  outputName: str = None,
                  itstring1: str = None,
                  numChunks1: int = None,
                  sqlFilePath: Union[None, Path, str] = None) -> pd.DataFrame:
    """
    Executes a SQL query.
    """
    connection1 = create_engine(connectionString1).connect().execution_options(stream_results=True)
    connection2 = create_engine(connectionString1).connect().execution_options(stream_results=True)

    # >>> Determine query source: File or string >>>
    # Case 1 (file): `sqlFilePath` is defined
    # Case 2 (string): `sqlQuery` is defined

    if isinstance(sqlFilePath, type(None)):
        case1 = False
    elif isinstance(sqlFilePath, (Path, str)):
        case1 = True
    else:
        message = f"""The variable `sqlFilePath` is of an unexpected type: "{type(sqlFilePath)}"."""
        logger.fatal(message)
        raise Exception(message)

    if isinstance(sqlQuery, type(None)):
        case2 = False
    elif isinstance(sqlQuery, str):
        case2 = True
    else:
        message = f"""The variable `sqlQuery` is of an unexpected type: "{type(sqlQuery)}"."""
        logger.fatal(message)
        raise Exception(message)
    # <<< Determine query source: File or string <<<

    # >>> Define `query` >>>
    if case1 and case2:
        message = f"""There is an ambiguous argument input. Only one of `sqlFilePath` or `sqlQuery` may be passed, but not both."""
        logger.fatal(message)
        raise Exception(message)
    elif case1:
        with open(sqlFilePath, "r") as file:
            query = file.read()
    elif case2:
        query = sqlQuery
    else:
        message = f"""An unexpected error occurred."""
        logger.fatal(message)
        raise Exception(message)
    # <<< Define `query` <<<
    
    # >>> Argumnet check: `outputName` >>>
    if downloadData:
        if isinstance(outputName, type(None)):
            message = """When `downloadData` is set to `True`, you must pass a value to `outputName`."""
            logger.critical(message)
            raise Exception(message)
    else:
        pass

    # <<< Argumnet check: `outputName` <<<

    # Save query to log
    logger.debug(query)

    # Execute query
    logger.info("""  ..  Executing query.""")

    if downloadData:
        logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}".""")
        queryGenerator0 = pd.read_sql(sql=query, con=connection1, chunksize=queryChunkSize)
        chunks2 = [1 for _ in queryGenerator0]
        numChunks2 = sum(chunks2)
        padlen2 = len(str(numChunks2))
        logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}" - Done. there are {numChunks2:,} chunks.""")
    else:
        pass

    logger.info("""  ..  Creating query generator.""")
    queryGenerator1 = pd.read_sql(sql=query, con=connection2, chunksize=queryChunkSize)
    logger.info("""  ..  Creating query generator - Done.""")

    logger.info("""  ..  Iterating over query generator.""")
    for it2, queryChunk in enumerate(queryGenerator1, start=1):
        if downloadData:
            logger.info(f"""  ..  ..  Executing query chunk {it2:,} of {numChunks2:,}.""")
            result = queryChunk
            result = pd.DataFrame(result)  # For type hinting
            logger.info("""  ..  ..  Finished query chunk.""")
            logger.info("  ..  ..  Saving chunk.")
            itstring2 = str(it2).zfill(padlen2)
            if itstring1 and numChunks1:
                fpath = runOutputDir.joinpath(f"{outputName} - {itstring1} of {numChunks1} - {itstring2} of {numChunks2}.CSV")
            else:
                fpath = runOutputDir.joinpath(f"{outputName} - {itstring2} of {numChunks2}.CSV")
            result.to_csv(fpath, index=False)
            logger.info("  ..  ..  Saving chunk - done.")
        else:
            logger.info(f"""  ..  ..  Executing query chunk {it2:,}.""")
            result = queryChunk
            result = pd.DataFrame(result)  # For type hinting
            result.to_sql(name=newSQLTable_Name,
                          schema=newSQLTable_Schema,
                          con=connectionString2,
                          if_exists="append",
                          index=False)
            logger.info("""  ..  ..  Finished query chunk.""")

    connection1.close()
    connection2.close()
