"""
Iterates over the files that would be processed in the pipeline and runs quality tests on them. Currently the quality tests are

  1. Check for delimmeter issues. This is done by reading the whole file with `pd.read_csv`. Usually if there's an unexpected presence or absence of a delimmeter this will raise an error.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
"""


# Third-party packages
import pandas as pd
from pandas.errors import ParserError
# Local packages
from drapi.drapi import getTimestamp, makeDirPath


def dataQualityTest(listOfPortionDirs,
                    LIST_OF_PORTION_CONDITIONS,
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
    `listOfPortionDirs`: "{listOfPortionDirs}"
    `LIST_OF_PORTION_CONDITIONS`: "{LIST_OF_PORTION_CONDITIONS}"
    `CHUNK_SIZE`: "{CHUNK_SIZE}"
    `pipelineOutputDir`: "{pipelineOutputDir}"
    `logger`: "{logger}"
    `ROOT_DIRECTORY`: "{ROOT_DIRECTORY}"
    `rootDirectory`: "{rootDirectory}"
    """)

    # Data quality check
    logger.info("""Getting the set of values for each variable to de-identify.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logger.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logger.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Read file
                logger.info("""    This file has met all conditions for testing.""")
                # Test 1: Make sure all lines have the same number of delimiters
                logger.info("""  ..  Test 1: Make sure all lines have the same number of delimiters.""")
                try:
                    for it, _ in enumerate(pd.read_csv(file, chunksize=CHUNK_SIZE), start=1):
                        logger.info(f"""  ..    Working on chunk {it}...""")
                    logger.info("""  ..    There are no apparent problems reading this file.""")
                except ParserError as err:
                    msg = err.args[0]
                    logger.info(f"""  ..    This file raised an error: "{msg}".""")
                # Test 2: ...
                pass
            else:
                logger.info("""    This file does not need to be tested.""")

    # Return path to sets fo ID values
    # TODO If this is implemented as a function, instead of a stand-alone script, return `runOutputDir` to define `setsPathDir` in the "makeMap" scripts.
    logger.info(f"""Finished performing the battery of tests. Results, if any, will be located the run output directory: "{runOutputDir.relative_to(rootDirectory)}".""")

    # End script
    logger.info(f"""Finished running "{functionName}".""")
