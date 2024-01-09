"""
Get all variables/columns of tables/files in the project.
"""

import os
from collections import OrderedDict
from pathlib import Path
# Third-party packages
import pandas as pd


def getProjectColumns(listOfPortionDirs: list,
                      ROOT_DIRECTORY,
                      rootDirectory,
                      logger):
    """
    """
    functionName = __name__.split(".")[-1]
    logger.info(f"""Begin running "{functionName}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Function arguments:

    # Arguments
    ``: "{""}"
    """)

    # Get columns
    columns = {}
    for portionPath in listOfPortionDirs:
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        dirRelativePath = portionPath.absolute().relative_to(rootDirectory)
        logger.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logger.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = [lambda x: x.is_file(), lambda x: x.suffix == ".csv", lambda x: x.name != ".DS_Store"]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logger.info(f"""  Reading "{file.absolute().relative_to(rootDirectory)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns

    # Get all columns by file
    logger.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    columnsOrdered = OrderedDict(sorted(columns.items()))
    for key, value in columnsOrdered.items():
        if it > -1:
            logger.info(key)
            logger.info("")
            for el in sorted(value):
                logger.info(f"  {el}")
                allColumns.add(el)
            logger.info("")
        it += 1

    # Get all columns by portion
    # TODO
    pass

    # Print the set of all columns
    logger.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logger.info(f"  {el}")

    # End script
    logger.info(f"""Finished running "{functionName}".""")
