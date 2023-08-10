"""
Convert person ID column to patient key

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
# Third-party packages
import pandas as pd
# Local packages
from drapi.idealist.idealist import idealistMap2dict


def main(COLUMNS_TO_CONVERT_DI, PERSON_ID_MAP_PATH, listOfPortionDirs, LIST_OF_PORTION_CONDITIONS, CHUNK_SIZE, thisFilePath, ROOT_DIRECTORY, rootDirectory, runOutputDir):
    """
    """

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Load person ID map
    personIDMap = pd.read_csv(PERSON_ID_MAP_PATH)
    personIDMapDi = idealistMap2dict(personIDMap, "person_id", "patient_key")

    # Convert columns
    logging.info("""Getting the set of values for each variable to convert.""")
    # Create file parameters dictionary

    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logging.info("""    File has met all conditions for processing.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        logging.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in COLUMNS_TO_CONVERT_DI.keys():
                            logging.info("""  ..  ..  Column must be converted. Converting values.""")
                            dfChunk[columnName] = dfChunk[columnName].apply(lambda IDNum: personIDMapDi[IDNum])
                            dfChunk = dfChunk.rename(columns={columnName: COLUMNS_TO_CONVERT_DI[columnName]})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logging.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logging.info("""    This file does not need to be processed.""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
