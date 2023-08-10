"""
Get all variables/columns of tables/files in the project.
"""

import logging
import os
from collections import OrderedDict
from pathlib import Path
# Third-party packages
import pandas as pd


def main(portionsOutputDirPath, rootDirectory, thisFilePath, projectDir):
    """
    """

    # Get columns
    columns = {}
    for portionName, portionPath in portionsOutputDirPath.items():
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        dirRelativePath = portionPath.absolute().relative_to(rootDirectory)
        logging.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logging.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = [lambda x: x.is_file(), lambda x: x.suffix == ".csv", lambda x: x.name != ".DS_Store"]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logging.debug(f"""  Reading "{file.absolute().relative_to(rootDirectory)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns

    # Get all columns by file
    logging.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    columnsOrdered = OrderedDict(sorted(columns.items()))
    for key, value in columnsOrdered.items():
        if it > -1:
            logging.info(key)
            logging.info("")
            for el in sorted(value):
                logging.info(f"  {el}")
                allColumns.add(el)
            logging.info("")
        it += 1

    # Get all columns by portion
    # TODO
    pass

    # Print the set of all columns
    logging.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logging.info(f"  {el}")

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
