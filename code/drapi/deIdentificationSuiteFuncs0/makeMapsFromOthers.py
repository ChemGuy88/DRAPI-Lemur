"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# NOTE Expects integer IDs, so no string IDs like Epic Patient IDs.
"""

import json
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import makeDirPath, getTimestamp, makeMap, makeSetComplement, ditchFloat, handleDatetimeForJson


def makeMapsFromOthers(SETS_PATH,
                       OLD_MAPS_DIR_PATH,
                       IRB_NUMBER,
                       VARIABLE_SUFFIXES,
                       DATA_TYPES,
                       ROOT_DIRECTORY,
                       rootDirectory,
                       pipelineOutputDir,
                       logger):
    """
    """
    functionName = __name__.split(".")[-1]
    runOutputDir = pipelineOutputDir.joinpath(functionName, getTimestamp())
    runIntermediateDataDir = pipelineOutputDir.joinpath(functionName, getTimestamp(), "temp")
    makeDirPath(runOutputDir)
    logger.info(f"""Begin running "{functionName}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Function arguments:

    # Arguments
    ``: "{""}"
    """)

    # Get set of values
    # NOTE The code that used to be in this section was moved to "getIDValues.py"
    getIDValuesOutput = SETS_PATH
    logger.info(f"""Using the set of new values in the directory "{getIDValuesOutput.absolute().relative_to(rootDirectory)}".""")

    # Assertions
    collectedVariables = sorted([fname.stem for fname in getIDValuesOutput.iterdir()])
    for variableName in collectedVariables:
        assert variableName in DATA_TYPES.keys(), f"""The variable "{variableName}" was not in the `DATA_TYPES` dictionary."""
        assert variableName in VARIABLE_SUFFIXES.keys(), f"""The variable "{variableName}" was not in the `VARIABLE_SUFFIXES` dictionary."""

    # Concatenate all old maps
    oldMaps = {}
    logger.info("""Concatenating all similar pre-existing maps.""")
    for variableName in collectedVariables:
        logger.info(f"""  Working on variable "{variableName}".""")
        if variableName in OLD_MAPS_DIR_PATH.keys():
            logger.info("""    Variable has pre-existing map(s).""")
            listOfMapPaths = OLD_MAPS_DIR_PATH[variableName]
            dfConcat = pd.DataFrame()
            for mapPath in listOfMapPaths:
                logger.info(f"""  ..  Reading pre-existing map from "{mapPath}".""")
                df = pd.DataFrame(pd.read_csv(mapPath))
                dfConcat = pd.concat([dfConcat, df])
            oldMaps[variableName] = dfConcat
        elif variableName not in OLD_MAPS_DIR_PATH.keys():
            logger.info("""    Variable has no pre-existing map.""")
            oldMaps[variableName] = pd.DataFrame()

    # Get the set difference between all old maps and the set of un-mapped values
    valuesToMap = {}
    setsToMapDataDir = runIntermediateDataDir.joinpath("valuesToMap")
    makeDirPath(setsToMapDataDir)
    logger.info("""Getting the set difference between all old maps and the set of un-mapped values.""")
    for variableName in collectedVariables:
        logger.info(f"""  Working on variable "{variableName}".""")
        variableDataType = DATA_TYPES[variableName]

        # Get old set of IDs
        logger.info("""    Getting the old set of IDs.""")
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldIDSet = set(oldMap[variableName].values)
            oldIDSet = set([ditchFloat(el) for el in oldIDSet])  # NOTE: Hack. Convert values to type int or string
        elif len(oldMap) == 0:
            oldIDSet = set()
        logger.info(f"""    The size of this set is {len(oldIDSet):,}.""")

        # Get new set of IDs
        newSetPath = getIDValuesOutput.joinpath(f"{variableName}.txt")
        logger.info(f"""    Getting the new set of IDs from "{newSetPath.absolute().relative_to(rootDirectory)}".""")
        newIDSet = set()
        with open(newSetPath, "r") as file:
            text = file.read()
            lines = text.split("\n")[:-1]
        for line in lines:
            newIDSet.add(line)
        if variableDataType.lower() == "numeric":
            newIDSet = set([ditchFloat(el) for el in newIDSet])  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logger.error(msg)
            raise ValueError(msg)
        logger.info(f"""    The size of this set is {len(newIDSet):,}.""")

        # Set difference
        IDSetDiff = newIDSet.difference(oldIDSet)
        valuesToMap[variableName] = IDSetDiff

        # Save new subset to `setsToMapDataDir`
        fpath = setsToMapDataDir.joinpath(f"{variableName}.JSON")
        with open(fpath, "w") as file:
            if variableDataType.lower() == "numeric":
                li = [ditchFloat(IDNumber) for IDNumber in IDSetDiff]  # NOTE: Hack. Convert values to type int or string
            elif variableDataType.lower() == "string":
                li = list(IDSetDiff)
            else:
                msg = "The table column is expected to have a data type associated with it."
                logger.error(msg)
                raise Exception(msg)
            file.write(json.dumps(li, default=handleDatetimeForJson))
        if len(IDSetDiff) == 0:
            series = pd.Series(dtype=int)
        else:
            if variableDataType.lower() == "numeric":
                series = pd.Series(sorted(list(IDSetDiff)))
            elif variableDataType.lower() == "string":
                series = pd.Series(sorted([str(el) for el in IDSetDiff]))  # NOTE TODO I don't know why this variable exists, if it was ever used, or what it's for.
            else:
                msg = "The table column is expected to have a data type associated with it."
                logger.error(msg)
                raise Exception(msg)

    # Get numbers for new map
    logger.info("""Getting numbers for new map.""")
    newNumbersDict = {}
    for variableName in collectedVariables:
        oldMap = oldMaps[variableName]
        if len(oldMap) > 0:
            oldNumbersSet = set(oldMap["deid_num"].values)
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
    logger.info("""Mapping un-mapped values.""")
    for file in setsToMapDataDir.iterdir():
        variableName = file.stem
        variableDataType = DATA_TYPES[variableName]
        logger.info(f"""  Working on un-mapped values for variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
        # Map contents
        values = valuesToMap[variableName]
        if variableDataType.lower() == "numeric":
            values = set(int(float(value)) for value in values)  # NOTE: Hack. Convert values to type int or string
        elif variableDataType.lower() == "string":
            pass
        else:
            msg = "The table column is expected to have a data type associated with it."
            logger.error(msg)
            raise Exception(msg)
        numbers = sorted(list(newNumbersDict[variableName]))
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=numbers, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName, deIdentificationMapStyle="lemur")
        # Save map
        mapPath = runOutputDir.joinpath(f"{variableName} map.csv")
        map_.to_csv(mapPath, index=False)
        logger.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{functionName}".""")

    return runOutputDir
