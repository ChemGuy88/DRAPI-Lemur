"""
De-identify files

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Assign portion name to each path (per OS) so that portion files are stored in their respective folders, this prevents file from being overwritten in the unlikely, but possible, case files from different portions have the same name.
"""

# Third-party packages
import pandas as pd
# Local packages
from drapi.constants.constants import DATA_TYPES
from drapi.drapi import getTimestamp, makeDirPath, fileName2variableName, map2di, makeMap


def deIdentify(MAPS_DIR_PATH,
               listOfPortionDirs,
               LIST_OF_PORTION_CONDITIONS,
               IRB_NUMBER,
               COLUMNS_TO_DE_IDENTIFY,
               VARIABLE_ALIASES,
               VARIABLE_SUFFIXES,
               CHUNK_SIZE,
               pipelineOutputDir,
               logger,
               ROOT_DIRECTORY,
               rootDirectory):
    """
    """
    functionName = __name__.split(".")[-1]
    runOutputDir = pipelineOutputDir.joinpath(functionName, getTimestamp())
    makeDirPath(runOutputDir)
    logger.info(f"""Begin running "{functionName}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Function arguments:

    # Arguments
    ``: "{""}"
    """)

    # Load de-identification maps for each variable that needs to be de-identified
    logger.info("""Loading de-identification maps for each variable that needs to be de-identified.""")
    mapsDi = {}
    mapsColumnNames = {}
    variablesCollected = [fileName2variableName(fname) for fname in MAPS_DIR_PATH.iterdir()]
    for varName in variablesCollected:
        if varName in VARIABLE_ALIASES.keys():
            map_ = makeMap(IDset=set(), IDName=varName, startFrom=1, irbNumber=IRB_NUMBER, suffix=VARIABLE_SUFFIXES[varName]["deIdIDSuffix"], columnSuffix=varName, deIdentifiedIDColumnHeaderFormatStyle="lemur")
            mapsColumnNames[varName] = map_.columns[-1]
        else:
            varPath = MAPS_DIR_PATH.joinpath(f"{varName} map.csv")
            map_ = pd.read_csv(varPath)
            mapDi = map2di(map_)
            mapsDi[varName] = mapDi
            mapsColumnNames[varName] = map_.columns[-1]

    # De-identify columns
    logger.info("""De-identifying files.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logger.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logger.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logger.info("""    File has met all conditions for processing.""")
                logger.info("""  ..  Reading file to count the number of chunks.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                logger.info(f"""  ..  This file has {numChunks} chunks.""")
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    # Work on chunk
                    logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        logger.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in COLUMNS_TO_DE_IDENTIFY:  # Keep this reference to `COLUMNS_TO_DE_IDENTIFY` as a way to make sure that all variables were collected during `getIDValues` and the `makeMap` scripts.
                            variableDataType = DATA_TYPES[columnName]
                            logger.info(f"""  ..  ..  Column must be de-identified. De-identifying values. Values are being treated as the following data type: "{variableDataType}".""")
                            if columnName in VARIABLE_ALIASES.keys():
                                mapsDiLookUpName = VARIABLE_ALIASES[columnName]
                            else:
                                mapsDiLookUpName = columnName
                            # Look up values in de-identification maps according to data type. NOTE We are relying on pandas assigning the correct data type to the look-up values in the de-identification map.
                            if variableDataType.lower() == "numeric":
                                dfChunk[columnName] = dfChunk[columnName].apply(lambda IDNum: mapsDi[mapsDiLookUpName][IDNum] if not pd.isna(IDNum) else IDNum)
                            elif variableDataType.lower() == "string":
                                dfChunk[columnName] = dfChunk[columnName].apply(lambda IDvalue: mapsDi[mapsDiLookUpName][str(IDvalue)] if not pd.isna(IDvalue) else IDvalue)
                            else:
                                msg = "The table column is expected to have a data type associated with it."
                                logger.error(msg)
                                raise ValueError(msg)
                            dfChunk = dfChunk.rename(columns={columnName: mapsColumnNames[columnName]})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logger.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logger.info("""    This file does not need to be processed.""")

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{functionName}".""")
