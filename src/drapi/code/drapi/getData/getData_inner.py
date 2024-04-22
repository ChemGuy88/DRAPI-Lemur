"""
"""

from logging import Logger
from pathlib import Path
from typing_extensions import Union
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages


def getData_inner(conStr: str,
                  logger: Logger,
                  outputName: str,
                  queryChunkSize: int,
                  runOutputDir: Path,
                  sqlQuery: Union[None, str],
                  itstring1: str = None,
                  numChunks1: int = None,
                  sqlFilePath: Union[None, Path, str] = None) -> pd.DataFrame:
    """
    Executes a SQL query.
    """
    connection1 = create_engine(conStr).connect().execution_options(stream_results=True)
    connection2 = create_engine(conStr).connect().execution_options(stream_results=True)

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

    # Save query to log
    logger.log(9, query)

    # Execute query
    logger.info("""  ..  Executing query.""")

    logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}".""")
    queryGenerator0 = pd.read_sql(sql=query, con=connection1, chunksize=queryChunkSize)
    chunks2 = [1 for _ in queryGenerator0]
    numChunks2 = sum(chunks2)
    logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}" - Done. there are {numChunks2:,} chunks.""")

    logger.info("""  ..  Creating query generator.""")
    queryGenerator1 = pd.read_sql(sql=query, con=connection2, chunksize=queryChunkSize)
    logger.info("""  ..  Creating query generator - Done.""")

    padlen2 = len(str(numChunks2))
    logger.info("""  ..  Iterating over query generator.""")
    for it2, queryChunk in enumerate(queryGenerator1, start=1):
        itstring2 = str(it2).zfill(padlen2)
        logger.info(f"""  ..  ..  Executing query chunk {it2:,} of {numChunks2}.""")
        result = queryChunk
        logger.info("""  ..  ..  Finished query chunk.""")

        logger.info("  ..  ..  Saving chunk.")
        if itstring1 and numChunks1:
            fpath = runOutputDir.joinpath(f"{outputName} - {itstring1} of {numChunks1} - {itstring2} of {numChunks2}.CSV")
        else:
            fpath = runOutputDir.joinpath(f"{outputName} - {itstring2} of {numChunks2}.CSV")
        result.to_csv(fpath, index=False)
        logger.info("  ..  ..  Saving chunk - done.")

    connection1.close()
    connection2.close()
