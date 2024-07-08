"""
Functions to convert files to the format required by DeepDe-ID.
"""

import logging
from pathlib import Path
from typing_extensions import (Dict,
                               List,
                               Union)

import pandas as pd

from drapi.code.drapi.drapi import readDataFile

def prep_for_text_deidentification(filepath: Path,
                                   output_directory: Path,
                                   logger: logging.Logger,
                                   log_file_name: bool = True,
                                   rename_columns: Union[Dict[Union[int, str], Union[int,str]],
                                                         List[Union[int, str]],
                                                         None] = None,
                                   columns_to_keep: Union[None, List[Union[int, str]]] = None) -> None:
    """
    """
    # Verbose block
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
        # Assertions: The number of columns to rename should be the same as the number of columns, if list-like, else it should be a dictionary-like.
        if isinstance(rename_columns, list):
            len_rename_columns = len(rename_columns)
            message = f"""If you wish to rename the columns, then `rename_columns` should have the same number of columns as your table."""
            if len_rename_columns == len(df.columns):
                pass
            else:
                logger.critical(message)
                raise Exception(message)
        elif isinstance(rename_columns, dict):
            pass
        else:
            raise Exception(f"""We expect `rename_columns` to be a list or dictionary. We got "{type(rename_columns)}" instead.""")
        
        # Use `rename_columns`
        if isinstance(rename_columns, list):
            for old_column, new_column in zip(df.columns, rename_columns):
                df = df.rename(columns={old_column: new_column})
        elif isinstance(rename_columns, dict):
            df = df.rename(columns=rename_columns)
        else:
            raise Exception(f"""We expect `rename_columns` to be a list or dictionary. We got "{type(rename_columns)}" instead.""")

    # Save as TSV
    file_stem = filepath.stem
    export_path = output_directory.joinpath(f"{file_stem}.TSV")
    df.to_csv(path_or_buf=export_path,
              index=False,
              sep="\t")
