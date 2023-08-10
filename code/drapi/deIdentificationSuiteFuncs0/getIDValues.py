"""
Get the set of ID values for all variables to de-identify.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
# Third-party packages
import pandas as pd
# Local packages


def main(SETS_PATH, COLUMNS_TO_DE_IDENTIFY, VARIABLE_ALIASES, listOfPortionDirs, LIST_OF_PORTION_CONDITIONS, CHUNK_SIZE, thisFilePath, ROOT_DIRECTORY, rootDirectory, runOutputDir):
    """
    """

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Get set of values
    if SETS_PATH:
        logging.info(f"""Using the set of values previously collected from "{SETS_PATH}".""")
    else:
        logging.info("""Getting the set of values for each variable to de-identify.""")
        mapNames = [columnName for columnName in COLUMNS_TO_DE_IDENTIFY if columnName not in VARIABLE_ALIASES.keys()]
        columnSetsVarsDi = {columnName: {"fpath": runOutputDir.joinpath(f"{columnName}.txt"),
                                         "fileMode": "w"} for columnName in mapNames}
        for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
            # Act on directory
            logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
            for file in directory.iterdir():
                logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
                conditions = [condition(file) for condition in fileConditions]
                if all(conditions):
                    # Read file
                    logging.info("""    File has met all conditions for processing.""")
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                    for it, dfChunk in enumerate(dfChunks, start=1):
                        logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                        for columnName in dfChunk.columns:
                            logging.info(f"""  ..    Working on column "{columnName}".""")
                            if columnName in COLUMNS_TO_DE_IDENTIFY:
                                logging.info("""  ..  ..  Column must be de-identified. Collecting values.""")
                                valuesSet = sorted(list(set(dfChunk[columnName].dropna().values)))
                                if columnName in VARIABLE_ALIASES.keys():
                                    mapLookUpName = VARIABLE_ALIASES[columnName]
                                else:
                                    mapLookUpName = columnName
                                columnSetFpath = columnSetsVarsDi[mapLookUpName]["fpath"]
                                columnSetFileMode = columnSetsVarsDi[mapLookUpName]["fileMode"]
                                with open(columnSetFpath, columnSetFileMode) as file:
                                    for value in valuesSet:
                                        file.write(str(value))
                                        file.write("\n")
                                columnSetsVarsDi[mapLookUpName]["fileMode"] = "a"
                                logging.info(f"""  ..  ..  Values saved to "{columnSetFpath.absolute().relative_to(rootDirectory)}" in the project directory.""")
                else:
                    logging.info("""    This file does not need to be processed.""")

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logging.info(f"""Finished collecting the set of ID values to de-identify. The set files are located in "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
