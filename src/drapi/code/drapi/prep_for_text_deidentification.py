"""
Functions to convert files to the format required by DeepDe-ID.
"""

import logging
from pathlib import Path
from typing_extensions import (List,
                               Union)

import pandas as pd

from drapi.code.drapi.drapi import readDataFile

def prep_for_text_deidentification(filepath: Path,
                                   output_directory: Path,
                                   logger: logging.Logger,
                                   log_file_name: bool = True,
                                   rename_columns: bool = False,
                                   columns_to_keep: Union[None, List[Union[int, str]]] = None) -> None:
    """
    """
    if log_file_name:
        logger.info(f"""Working on file "{filepath}".""")

    # Read file
    readerObject = readDataFile(fname=filepath,
                                engine="pyarrow")

    # Pre-process
    df = pd.DataFrame(readerObject)

    # Pre-process: Columns to keep
    if columns_to_keep:
        # Pre-process: Columns to keep: Assertions
        len_columns_to_keep = len(columns_to_keep)
        if len_columns_to_keep == 2:
            pass
        else:
            message = f"""The number of columns to keep must be precisely 2, got instead "{len_columns_to_keep:,}"."""
            logger.critical(message)
            raise Exception(message)

        # Pre-process: Columns to keep: Choose columns
        if all([isinstance(el, int) for el in columns_to_keep]):
            df = df.iloc[:, columns_to_keep]
        elif all([isinstance(el, str) for el in columns_to_keep]):
            df = df.loc[:, columns_to_keep]
        else:
            message = "We expect the values in `columns_to_keep` to be either all integers or all strings."
            logger.critical(message)
            raise Exception(message)

    # Rename columns
    if rename_columns:
        columns = df.columns
        column_1 = columns[0]
        column_2 = columns[1]

        # Rename columns: Column 1
        df = df.rename(columns={column_1: "De-identified Linkage"})

        # Rename columns: Column 2
        df = df.rename(columns={column_2: "note_text"})

    # Save as TSV
    file_stem = filepath.stem
    export_path = output_directory.joinpath(f"{file_stem}.TSV")
    df.to_csv(path_or_buf=export_path,
              index=False,
              sep="\t")
