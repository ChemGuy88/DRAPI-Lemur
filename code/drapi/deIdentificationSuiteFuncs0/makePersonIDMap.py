"""
Convert OMOP person IDs to IDR patient keys.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

from pathlib import Path
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from drapi.drapi import getTimestamp, makeDirPath, personIDs2patientKeys


def makePersonIDMap(COLUMNS_TO_CONVERT,
                    SETS_PATH,
                    listOfPortionDirs,
                    LIST_OF_PORTION_CONDITIONS,
                    CHUNK_SIZE,
                    pipelineOutputDir: Path,
                    ROOT_DIRECTORY: str,
                    rootDirectory,
                    logger) -> Path:
    """
    """
    functionName = __name__.split(".")[-1]
    runOutputDir = pipelineOutputDir.joinpath(functionName, getTimestamp())
    runIntermediateDataDir = pipelineOutputDir.joinpath(functionName, getTimestamp(), "temp")
    makeDirPath(runOutputDir)
    makeDirPath(runIntermediateDataDir)
    logger.info(f"""Begin running "{functionName}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Function arguments:

    # Arguments
    ``: "{""}"
    """)

    # Get set of values
    if SETS_PATH:
        logger.info(f"""Using the set of values previously collected from "{SETS_PATH}".""")
    else:
        logger.info("""Getting the set of values for each variable to convert.""")
        columnSetsVarsDi = {columnName: {"fpath": runIntermediateDataDir.joinpath(f"{columnName}.txt"),
                                         "fileMode": "w"} for columnName in COLUMNS_TO_CONVERT}
        for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
            # Act on directory
            logger.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
            for file in directory.iterdir():
                logger.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logger.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logger.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_CONVERT:
                                logger.info("""  ..  ..  Column must be converted. Collecting values.""")
                                valuesSet = sorted(list(set(dfChunk[columnName].dropna().values)))
                                columnSetFpath = columnSetsVarsDi[columnName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[columnName]["fileMode"]
                                with open(columnSetFpath, columnSetFileMode) as file:
                                    for value in valuesSet:
                                        file.write(str(value))
                                        file.write("\n")
                                columnSetsVarsDi[columnName]["fileMode"] = "a"
                                logger.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(rootDirectory)}" in the project directory.""")
                else:
                    logger.info("""    This file does not need to be processed.""")

    # Map values
    if SETS_PATH:
        setsPathDir = SETS_PATH
    else:
        setsPathDir = runIntermediateDataDir
    for file in setsPathDir.iterdir():
        columnName = file.stem
        logger.info(f"""  Working on variable "{columnName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Read file
        try:
            df = pd.read_table(file, header=None)
        except EmptyDataError as err:
            _ = err
            df = pd.DataFrame()
        # Assert
        if df.shape[1] == 1:
            # Try to convert to integer-type
            try:
                df.iloc[:, 0] = df.iloc[:, 0].astype(int)
            except ValueError as err:
                _ = err
            # Check length differences
            len0 = len(df)
            values = set(df.iloc[:, 0].values)
            len1 = len(values)
            logger.info(f"""    The length of the ID array was reduced from {len0:,} to {len1:,} when removing duplicates.""")
        elif df.shape[1] == 0:
            pass
        # Map contents
        map_ = personIDs2patientKeys(list(values))
        # Save map
        mapPath = runOutputDir.joinpath(f"{columnName} map.csv")
        map_.to_csv(mapPath, index=False)
        logger.info(f"""    PersonID-to-PatientKey map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{functionName}".""")

    return mapPath
