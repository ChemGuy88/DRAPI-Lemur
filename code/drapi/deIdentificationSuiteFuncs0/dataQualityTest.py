"""
Iterates over the files that would be processed in the pipeline and runs quality tests on them. Currently the quality tests are

  1. Check for delimmeter issues. This is done by reading the whole file with `pd.read_csv`. Usually if there's an unexpected presence or absence of a delimmeter this will raise an error.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
"""


import logging
# Third-party packages
import pandas as pd
from pandas.errors import ParserError


def main(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS, CHUNK_SIZE, thisFilePath, ROOT_DIRECTORY, rootDirectory, runOutputDir):
    """
    """
    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Data quality check
    logging.info("""Getting the set of values for each variable to de-identify.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Read file
                logging.info("""    This file has met all conditions for testing.""")
                # Test 1: Make sure all lines have the same number of delimiters
                logging.info("""  ..  Test 1: Make sure all lines have the same number of delimiters.""")
                try:
                    numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                    _ = numChunks
                    logging.info("""  ..    There are no apparent problems reading this file.""")
                except ParserError as err:
                    msg = err.args[0]
                    logging.info(f"""  ..    This file raised an error: "{msg}".""")
                # Test 2: ...
                pass
            else:
                logging.info("""    This file does not need to be tested.""")

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logging.info(f"""Finished collecting the set of ID values to de-identify. The set files are located in "{runOutputDir.relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
