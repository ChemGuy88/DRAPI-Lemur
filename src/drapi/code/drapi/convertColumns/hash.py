"""
These functions convert columns by using conversion functions.
"""

import logging
import pprint
import sys
from pathlib import Path
from time import sleep
from typing import (Callable,
                    List,
                    Literal,
                    Union)
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (choosePathToLog,
                                    makeDirPath,
                                    makeMap,
                                    readDataFile)


def convertColumnsHash_byDir(listOfPortionDirs: list,
                             listOfPortionNames: List[str],
                             LIST_OF_PORTION_CONDITIONS: list,
                             columnsToConvert: list,
                             mapsColumnNames: dict,
                             logger: logging.Logger,
                             deIdentificationFunctions: dict,
                             VARIABLE_ALIASES: dict,
                             CHUNKSIZE: int,
                             runOutputDir: Path,
                             rootDirectory: Path,
                             MESSAGE_MODULO_CHUNKS: int,
                             SCRIPT_TEST_MODE: bool = False,):
    """
    """
    # Assert all portions have file criteria accounted for
    if len(listOfPortionDirs) == len(LIST_OF_PORTION_CONDITIONS):
        pass
    else:
        raise Exception("The number of portions does not equal the number of portion conditions.")

    # De-identify columns
    logger.info("""De-identifying files.""")
    allowLogging = False
    # Set file options: Map file
    for portionName, directory, fileConditions in zip(listOfPortionNames, listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        directory = Path(directory)  # For type hinting
        # Act on directory
        logger.info(f"""Working on directory "{choosePathToLog(directory, rootDirectory)}".""")
        listOfFiles = sorted(list(directory.iterdir()))
        for file in listOfFiles:
            logger.info(f"""  Working on file "{choosePathToLog(file, rootDirectory)}".""")
            fileOptions = {columnName: {"header": True,
                                        "mode": "w"} for columnName in columnsToConvert}
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options: Data file
                exportPath = runOutputDir.joinpath("Portions", portionName, f"{file.stem}.CSV")
                makeDirPath(exportPath.parent)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logger.info("""    File has met all conditions for processing.""")
                logger.info("""  ..  Reading file to count the number of chunks.""")
                # >>> TEST BLOCK >>>  # TODO Remove
                if SCRIPT_TEST_MODE:
                    it1Total = 100
                else:
                    it1Total = sum([1 for _ in readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)])
                # <<< TEST BLOCK <<<
                logger.info(f"""  ..  This file has {it1Total:,} chunks.""")
                # Calculate logging requency
                if it1Total < MESSAGE_MODULO_CHUNKS:
                    moduloChunks = it1Total
                else:
                    moduloChunks = round(it1Total / MESSAGE_MODULO_CHUNKS)
                if it1Total / moduloChunks < 100:
                    moduloChunks = 1
                else:
                    pass
                dfChunks = readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)
                filePreview = readDataFile(file, nrows=2)
                filePreview = pd.DataFrame(filePreview)
                for it1, dfChunk0 in enumerate(dfChunks, start=1):
                    # >>> TEST BLOCK >>>  # TODO Remove
                    if SCRIPT_TEST_MODE:
                        if it1 > 1:
                            logger.info("""  ..  `SCRIPT_TEST_MODE` engaged. BREAKING.""")
                            break
                    # <<< TEST BLOCK <<<
                    dfChunk = pd.DataFrame(dfChunk0)
                    # Work on chunk
                    if it1 % moduloChunks == 0:
                        allowLogging = True
                    else:
                        allowLogging = False
                    if allowLogging:
                        logger.info(f"""  ..  Working on chunk {it1:,} of {it1Total:,}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        if columnName in VARIABLE_ALIASES.keys():
                            columnNameAlias = VARIABLE_ALIASES[columnName]
                            hasAlias = True
                        else:
                            columnNameAlias = columnName
                            hasAlias = False
                        # Logging block
                        if allowLogging:
                            if hasAlias:
                                logger.info(f"""  ..    Working on column "{columnName}" aliased as "{columnNameAlias}".""")
                            else:
                                logger.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in columnsToConvert or columnNameAlias in columnsToConvert:
                            if allowLogging:
                                logger.info("""  ..  ..  Column must be converted. Converting column...""")
                            # De-identify column: create de-identified values
                            newColumnName = mapsColumnNames[columnName]
                            newColumn = dfChunk[columnName].apply(deIdentificationFunctions[columnNameAlias])
                            newColumn = pd.Series(newColumn)  # For type hinting
                            newColumnWithOldName = newColumn
                            newColumnWithNewName = newColumn.rename(newColumnName)  # We can change `newColumnName` with the aliased version
                            # QA: Column/Variable Map: Variables
                            mapSavePath = runOutputDir.joinpath("Metadata", "Maps by Portion", portionName, f"{columnNameAlias}", f"{file.stem}.CSV")
                            makeDirPath(mapSavePath.parent)
                            mapHeader = fileOptions[columnNameAlias]["header"]
                            mapMode = fileOptions[columnNameAlias]["mode"]
                            # QA: Column/Variable Map: Save mapped column
                            chunkColumnMap = pd.concat([dfChunk[columnName], newColumnWithNewName], axis=1).drop_duplicates()
                            logger.info(f"""  ..  ..  Saving QA table to "{choosePathToLog(mapSavePath.absolute(), rootPath=rootDirectory)}".""")
                            logger.info(f"""  ..  ..  Saving QA table to `mapHeader` set to "{mapHeader}".""")
                            logger.info(f"""  ..  ..  Saving QA table to `mapMode` set to "{mapMode}".""")
                            chunkColumnMap.to_csv(mapSavePath, index=False, header=mapHeader, mode=mapMode)
                            fileOptions[columnNameAlias]["header"] = False
                            fileOptions[columnNameAlias]["mode"] = "a"
                            # De-identify column: Replace old values
                            dfChunk[columnName] = newColumnWithOldName
                            dfChunk = dfChunk.rename(columns={columnName: newColumnName})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileHeaders = False
                    fileMode = "a"
                    if allowLogging:
                        logger.info(f"""  ..  Chunk saved to "{choosePathToLog(exportPath, rootDirectory)}".""")
                # End file lopp
                pass
            else:
                logger.info("""    This file does not need to be processed.""")


def convertColumnsHash_byFile(file: Union[Path, str],
                              portionName: str,
                              columnsToConvert: list,
                              mapsColumnNames: dict,
                              deIdentificationFunctions: dict,
                              VARIABLE_ALIASES: dict,
                              CHUNKSIZE: int,
                              runOutputDir: Path,
                              rootDirectory: Path,
                              logger: logging.Logger,
                              MESSAGE_MODULO_CHUNKS: int,
                              SCRIPT_TEST_MODE: bool = False,):
    """
    """
    # Set file options: Data file
    file = Path(file)
    fileOptions = {columnName: {"header": True,
                                "mode": "w"} for columnName in columnsToConvert}
    exportPath = runOutputDir.joinpath("Portions", portionName, f"{file.stem}.CSV")
    makeDirPath(exportPath.parent)
    fileMode = "w"
    fileHeaders = True
    # Read file
    logger.info("""  ..  Reading file to count the number of chunks.""")
    # >>> TEST BLOCK >>>
    if SCRIPT_TEST_MODE:
        it1Total = 100
    else:
        it1Total = sum([1 for _ in readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)])
    # <<< TEST BLOCK <<<
    logger.info(f"""  ..  This file has {it1Total:,} chunks.""")
    # Calculate logging requency
    if it1Total < MESSAGE_MODULO_CHUNKS:
        moduloChunks = it1Total
    else:
        moduloChunks = round(it1Total / MESSAGE_MODULO_CHUNKS)
    if it1Total / moduloChunks < 100:
        moduloChunks = 1
    else:
        pass
    dfChunks = readDataFile(file, chunksize=CHUNKSIZE, low_memory=False)
    filePreview = readDataFile(file, nrows=2)
    filePreview = pd.DataFrame(filePreview)
    for it1, dfChunk0 in enumerate(dfChunks, start=1):
        # >>> TEST BLOCK >>>  # TODO Remove
        if SCRIPT_TEST_MODE:
            if it1 > 1:
                logger.info("""  ..  `SCRIPT_TEST_MODE` engaged. BREAKING.""")
                break
        # <<< TEST BLOCK <<<
        dfChunk = pd.DataFrame(dfChunk0)
        # Work on chunk
        if it1 % moduloChunks == 0:
            allowLogging = True
        else:
            allowLogging = False
        if allowLogging:
            logger.info(f"""  ..  Working on chunk {it1:,} of {it1Total:,}.""")
        for columnName in dfChunk.columns:
            # Work on column
            if columnName in VARIABLE_ALIASES.keys():
                columnNameAlias = VARIABLE_ALIASES[columnName]
                hasAlias = True
            else:
                columnNameAlias = columnName
                hasAlias = False
            # Logging block
            if allowLogging:
                if hasAlias:
                    logger.info(f"""  ..    Working on column "{columnName}" aliased as "{columnNameAlias}".""")
                else:
                    logger.info(f"""  ..    Working on column "{columnName}".""")
            if columnName in columnsToConvert or columnNameAlias in columnsToConvert:
                if allowLogging:
                    logger.info("""  ..  ..  Column must be converted. Converting column...""")
                # De-identify column: create de-identified values
                newColumnName = mapsColumnNames[columnName]
                newColumn = dfChunk[columnName].apply(deIdentificationFunctions[columnNameAlias])
                newColumn = pd.Series(newColumn)  # For type hinting
                newColumnWithOldName = newColumn
                newColumnWithNewName = newColumn.rename(newColumnName)  # We can change `newColumnName` with the aliased version
                # QA: Column/Variable Map: Variables
                mapSavePath = runOutputDir.joinpath("Metadata", "Maps by Portion", portionName, f"{columnNameAlias}", f"{file.stem}.CSV")
                makeDirPath(mapSavePath.parent)
                mapHeader = fileOptions[columnNameAlias]["header"]
                mapMode = fileOptions[columnNameAlias]["mode"]
                # QA: Column/Variable Map: Save mapped column
                chunkColumnMap = pd.concat([dfChunk[columnName], newColumnWithNewName], axis=1).drop_duplicates()
                logger.info(f"""  ..  ..  Saving QA table to "{choosePathToLog(mapSavePath.absolute(), rootPath=rootDirectory)}".""")
                logger.info(f"""  ..  ..  Saving QA table to `mapHeader` set to "{mapHeader}".""")
                logger.info(f"""  ..  ..  Saving QA table to `mapMode` set to "{mapMode}".""")
                chunkColumnMap.to_csv(mapSavePath, index=False, header=mapHeader, mode=mapMode)
                fileOptions[columnNameAlias]["header"] = False
                fileOptions[columnNameAlias]["mode"] = "a"
                # De-identify column: Replace old values
                dfChunk[columnName] = newColumnWithOldName
                dfChunk = dfChunk.rename(columns={columnName: newColumnName})
        # Save chunk
        dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
        fileHeaders = False
        fileMode = "a"
        if allowLogging:
            logger.info(f"""  ..  Chunk saved to "{choosePathToLog(exportPath, rootDirectory)}".""")
    # End file lopp
    pass


def convertColumnsHash(by: Literal["dir", "file"],
                       # Arguments used in preparation of case functions
                       IRB_NUMBER: str,
                       VARIABLE_SUFFIXES: dict,
                       # Arguments used in preparation AND passed to other functions: Common to both cases
                       VARIABLE_ALIASES: dict,
                       deIdentificationFunctions: dict,
                       logger: logging.Logger,
                       # Arguments passed to other functions: Common to both cases
                       rootDirectory: Path,
                       runOutputDir: Path,
                       CHUNKSIZE: int,
                       MESSAGE_MODULO_CHUNKS: int,
                       SCRIPT_TEST_MODE: bool,
                       # Arguments passed to other functions: "dir" case
                       listOfPortionDirs: list[Union[Path, str]] = None,
                       listOfPortionNames: list[str] = None,
                       LIST_OF_PORTION_CONDITIONS: list[Callable] = None,
                       # Arguments passed to other functions: "file" case
                       fpath: Path = None,
                       portionName: str = None
                       ) -> None:
    """
    """
    argsAsString = pprint.pformat(locals())
    logger.info(f"""`locals()`:\n{argsAsString}""")

    # Collect columns to convert
    columnsToConvert = sorted(list(deIdentificationFunctions.keys()))

    # Load de-identification maps for each variable that needs to be de-identified
    logger.info("""Loading de-identification maps for each variable that needs to be de-identified.""")
    mapsColumnNames = {}
    variablesCollected = [fname for fname in deIdentificationFunctions.keys()]
    for varName in variablesCollected:
        logger.info(f"""  Creating de-identified variable name for "{varName}".""")
        mapsColumnNames[varName] = f"De-identified {varName}"
    # Add aliases to `mapsColumnNames`
    for varName in VARIABLE_ALIASES.keys():
        varAlias = VARIABLE_ALIASES[varName]
        map_ = makeMap(IDset=set(),
                       IDName=varName,
                       startFrom=1,
                       irbNumber=IRB_NUMBER,
                       suffix=VARIABLE_SUFFIXES[varAlias]["deIdIDSuffix"],
                       columnSuffix=varName,
                       deIdentificationMapStyle="lemur",
                       logger=logging.getLogger())
        mapsColumnNames[varName] = map_.columns[-1]

    # QA: Test de-identification functions
    logger.info("""QA: Testing de-identification functions.""")
    for variableName, func in deIdentificationFunctions.items():
        logger.info(f"""  {variableName}: {func(1)}.""")

    # Run conversion
    if by == "dir":
        # Not implemented! TODO
        raise Exception("Sorry, this is not yet implemented! =(")
        convertColumnsHash_byDir(listOfPortionDirs=listOfPortionDirs,
                                 listOfPortionNames=listOfPortionNames,
                                 LIST_OF_PORTION_CONDITIONS=LIST_OF_PORTION_CONDITIONS,
                                 columnsToConvert=columnsToConvert,
                                 mapsColumnNames=mapsColumnNames,
                                 logger=logger,
                                 deIdentificationFunctions=deIdentificationFunctions,
                                 VARIABLE_ALIASES=VARIABLE_ALIASES,
                                 CHUNKSIZE=CHUNKSIZE,
                                 runOutputDir=runOutputDir,
                                 rootDirectory=rootDirectory,
                                 MESSAGE_MODULO_CHUNKS=MESSAGE_MODULO_CHUNKS,
                                 SCRIPT_TEST_MODE=SCRIPT_TEST_MODE)
    elif by in ["file", "file-dir"]:
        logger.info(f"""Working on file "{fpath}".""")
        convertColumnsHash_byFile(file=fpath,
                                  portionName=portionName,
                                  columnsToConvert=columnsToConvert,
                                  mapsColumnNames=mapsColumnNames,
                                  deIdentificationFunctions=deIdentificationFunctions,
                                  VARIABLE_ALIASES=VARIABLE_ALIASES,
                                  CHUNKSIZE=CHUNKSIZE,
                                  runOutputDir=runOutputDir,
                                  rootDirectory=rootDirectory,
                                  logger=logger,
                                  MESSAGE_MODULO_CHUNKS=MESSAGE_MODULO_CHUNKS,
                                  SCRIPT_TEST_MODE=SCRIPT_TEST_MODE)
        logger.info(f"""Working on file "{fpath}" - done.""")
    else:
        raise Exception(f"""`by` must be one of {{"dir", "file"}}, but instead got "{by}".""")
