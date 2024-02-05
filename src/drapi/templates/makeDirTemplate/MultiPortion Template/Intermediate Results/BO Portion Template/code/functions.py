"""
"""

import re
from logging import Logger
from pathlib import Path
# Third-party packages
import pandas as pd
from sqlalchemy import create_engine
# Local packages
from drapi.code.drapi.drapi import (makeChunks,
                                    replace_sql_query)


def getData(queryName: str, querySubName: str, sqlFilePath: Path, cohortData: pd.DataFrame, conStr: str, runOutputDir, queryChunkSize: int, logger: Logger) -> pd.DataFrame:
    """
    """
    connection1 = create_engine(conStr).connect().execution_options(stream_results=True)
    connection2 = create_engine(conStr).connect().execution_options(stream_results=True)

    # Read query file
    with open(sqlFilePath, "r") as file:
        query0 = file.read()

    # Fill out query template
    logger.info("""  Filling out query template.""")

    query = query0[:]

    # Save query to log
    logger.log(9, query)

    # Execute query
    logger.info("""  ..  Executing query.""")

    logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}".""")
    queryGenerator0 = pd.read_sql(sql=query, con=connection1, chunksize=queryChunkSize)
    chunks2 = [1 for _ in queryGenerator0]
    numChunks2 = sum(chunks2)
    logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}" - Done.""")

    logger.info("""  ..  Creating query generator.""")
    queryGenerator1 = pd.read_sql(sql=query, con=connection2, chunksize=queryChunkSize)
    logger.info("""  ..  Creating query generator - Done.""")

    padlen2 = len(str(numChunks2))
    logger.info("""  ..  Iterating over query generator.""")
    for it2, queryChunk in enumerate(queryGenerator1, start=1):
        itstring2 = str(it2).zfill(padlen2)
        logger.info(f"""  ..  ..  Executing query chunk {itstring2} of {numChunks2}.""")
        result = queryChunk
        logger.info("""  ..  ..  Finished query chunk.""")

        logger.info("  ..  ..  Saving chunk.")
        if len(querySubName) > 0:
            querySubNamePart = f" - {querySubName}"
        else:
            querySubNamePart = querySubName
        fpath = runOutputDir.joinpath(f"{queryName}{querySubNamePart} - {itstring2} of {numChunks2}.CSV")
        result.to_csv(fpath, index=False)
        logger.info("  ..  ..  Saving chunk - done.")

    connection1.close()
    connection2.close()


def getData2(queryName: str, querySubName: str, sqlFilePath: Path, cohortData: pd.DataFrame, conStr: str, runOutputDir, queryChunkSize: int, logger: Logger) -> pd.DataFrame:
    """
    """
    filterChunkSize = 20000
    connection1 = create_engine(conStr).connect().execution_options(stream_results=True)
    connection2 = create_engine(conStr).connect().execution_options(stream_results=True)

    # Read query file
    with open(sqlFilePath, "r") as file:
        query0 = file.read()

    # Fill out query template
    logger.info("""  Filling out query template.""")

    IDSeries1 = cohortData["Patient Key"]  # TODO
    templatePlaceholder1 = "{PYTHON_VARIABLE: PATIENT_KEY}"  # TODO
    variableDataType1 = "int"  # TODO
    if variableDataType1 == "int":
        IDValues1 = IDSeries1.drop_duplicates().dropna().astype("int64").sort_values().values
    elif variableDataType1 == "varchar":
        IDValues1 = IDSeries1.drop_duplicates().dropna().sort_values().values

    IDsChunk0 = makeChunks(IDValues1, filterChunkSize)
    IDsChunk1 = makeChunks(IDValues1, filterChunkSize)
    numChunks1 = sum([1 for _ in IDsChunk0])
    padlen1 = len(str(numChunks1))
    for it1, IDsChunk in enumerate(IDsChunk1, start=1):
        itstring1 = str(it1).zfill(padlen1)
        logger.info(f"""    Working on filter chunk {itstring1} of {numChunks1} with `filterChunkSize` "{filterChunkSize:,}".""")

        # Fill query template: lists to strings
        if variableDataType1 == "int":
            IDListAsString1 = ",".join([f"{el}" for el in IDsChunk])
        elif variableDataType1 == "varchar":
            IDListAsString1 = ",".join([f"'{el}'" for el in IDsChunk])

        query = replace_sql_query(query=query0,
                                  old="""(( ADMIT_EVENT_Derived.NUM_GRAM_WGHT )/1000)/((( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)*(( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)) as "Admit BMI",""",
                                  new="""(( ADMIT_EVENT_Derived.NUM_GRAM_WGHT )/1000)/NULLIF(((( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)*(( ADMIT_EVENT_Derived.NUM_CENTMTR_HGHT )/100)), 0) as "Admit BMI",""")
        query = replace_sql_query(query=query,
                                  old=",(cast(wt.last_wt_oz as decimal(10,2))*0.0283495)/((cast(ht.last_ht_in as decimal(10,2))*0.0254)*(cast(ht.last_ht_in as decimal(10,2)))*0.0254) as bmi_manual_calc",
                                  new=",(cast(wt.last_wt_oz as decimal(10,2))*0.0283495)/NULLIF(((cast(ht.last_ht_in as decimal(10,2))*0.0254)*(cast(ht.last_ht_in as decimal(10,2)))*0.0254), 0) as bmi_manual_calc")

        query = replace_sql_query(query=query,
                                  old=templatePlaceholder1,
                                  new=IDListAsString1)

        # Save query to log
        logger.log(9, query)

        # Execute query
        logger.info("""  ..  Executing query.""")

        logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}".""")
        queryGenerator0 = pd.read_sql(sql=query, con=connection1, chunksize=queryChunkSize)
        chunks2 = [1 for _ in queryGenerator0]
        numChunks2 = sum(chunks2)
        logger.info(f"""  ..  Counting the number of query result chunks that are expected with `queryChunkSize` "{queryChunkSize:,}" - Done.""")

        logger.info("""  ..  Creating query generator.""")
        queryGenerator1 = pd.read_sql(sql=query, con=connection2, chunksize=queryChunkSize)
        logger.info("""  ..  Creating query generator - Done.""")

        padlen2 = len(str(numChunks2))
        logger.info("""  ..  Iterating over query generator.""")
        for it2, queryChunk in enumerate(queryGenerator1, start=1):
            itstring2 = str(it2).zfill(padlen2)
            logger.info(f"""  ..  ..  Executing query chunk {itstring2} of {numChunks2}.""")
            result = queryChunk
            logger.info("""  ..  ..  Finished query chunk.""")

            logger.info("  ..  ..  Saving chunk.")
            if len(querySubName) > 0:
                querySubNamePart = f" - {querySubName}"
            else:
                querySubNamePart = querySubName
            fpath = runOutputDir.joinpath(f"{queryName}{querySubNamePart} - {itstring1} of {numChunks1} - {itstring2} of {numChunks2}.CSV")
            result.to_csv(fpath, index=False)
            logger.info("  ..  ..  Saving chunk - done.")

    connection1.close()
    connection2.close()


def checkFileConditions(sqlFilePath: Path, cohortData: pd.DataFrame, stepNumberCondition: str, logger: Logger, conStr: str, runOutputDir: Path, getDataFunction: object, queryChunkSize: int):
    """
    """
    logger.info(f"""  Working on file "{sqlFilePath}".""")
    pattern = r"^(?P<universe>.+?) - (?P<queryName>[^-]+)( - )?(?P<querySubName>[^-]*).SQL$"
    matchObj = re.match(pattern, sqlFilePath.name)
    if matchObj:
        groupdict = matchObj.groupdict()
        queryName = groupdict["queryName"]
        querySubName = groupdict["querySubName"]
        condition1 = sqlFilePath.suffix.lower() == ".sql"
    else:
        condition1 = False

    if condition1:
        logger.info("  Processing file.")
        getDataFunction(queryName=queryName,
                        querySubName=querySubName,
                        sqlFilePath=sqlFilePath,
                        cohortData=cohortData,
                        conStr=conStr,
                        runOutputDir=runOutputDir,
                        queryChunkSize=queryChunkSize,
                        logger=logger)
    else:
        logger.info("  This file has not met the conditions for processing.")
