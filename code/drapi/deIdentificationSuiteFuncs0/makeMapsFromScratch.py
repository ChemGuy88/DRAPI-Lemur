"""
Makes de-identification maps from scratch.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Needs to combine similar IDs, like different providers IDs.
"""

import logging
# Third-party packages
import pandas as pd
from pandas.errors import EmptyDataError
# Local packages
from drapi.drapi import makeMap


def main(SETS_PATH, VARIABLE_SUFFIXES, IRB_NUMBER, rootDirectory, runOutputDir, thisFilePath):
    """
    """
    # Get set of values
    # Imported from "getIDValues.py"

    # Map values
    for file in SETS_PATH.iterdir():
        variableName = file.stem
        logging.info(f"""  Working on variable "{variableName}" located at "{file.absolute().relative_to(rootDirectory)}".""")
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
            logging.info(f"""    The length of the ID array was reduced from {len0:,} to {len1:,} when removing duplicates.""")
        elif df.shape[1] == 0:
            pass
        # Map contents
        deIdIDSuffix = VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]
        map_ = makeMap(IDset=values, IDName=variableName, startFrom=1, irbNumber=IRB_NUMBER, suffix=deIdIDSuffix, columnSuffix=variableName)
        # Save map
        mapPath = runOutputDir.joinpath(f"{variableName} map.csv")
        map_.to_csv(mapPath, index=False)
        logging.info(f"""    De-identification map saved to "{mapPath.absolute().relative_to(rootDirectory)}".""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
