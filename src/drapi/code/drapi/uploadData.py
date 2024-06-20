"""
Uploads a pandas-compatible file to a SQL server
"""

import logging
import re
from pathlib import Path
from typing_extensions import (List,
                               Union)
# Third-party packages
import pandas as pd
import sqlalchemy as sa
# Local packages
from drapi.code.drapi.classes import SecretString
from drapi.code.drapi.drapi import readDataFile

def lazy_hack_1_function(string_: str):
    """
    """
    if isinstance(string_, str):
        pass
    else:
        return string_
    new_string = re.sub(pattern="\x00",
                    repl="<NULL-BYTE>",
                    string=string_)
    return new_string


def uploadData(list_of_paths: List[Union[Path, str]],
               schema_name: str,
               table_name: str,
               connection_string: SecretString,
               lazy_hack_1: List[Union[int, str]],
               logger: logging.Logger):
    """
    Uploads a pandas-compatible file to a SQL server
    """
    logger.info("Dropping table if it exists.")
    query_prep_table = f"""\
    DROP TABLE IF EXISTS [{schema_name}].[{table_name}]
    \
    """
    with sa.engine.create_engine(url=connection_string).connect() as connection:
        with connection.begin():
            _ = connection.execute(sa.text(query_prep_table))
    logger.info("Dropping table if it exists - done.")

    num_files = len(list_of_paths)
    for it, fpath in enumerate(list_of_paths, start=1):
        logger.info(f"""  Working on file {it:,} of {num_files:,}.""")
        df = readDataFile(fname=fpath,
                          engine="pyarrow")
        df = pd.DataFrame(df)  # For type hinting
        if lazy_hack_1:
            column_name = "note_text"
            series = df[column_name]
            df[column_name] = series.apply(lazy_hack_1_function)
        df.to_sql(name=table_name,
                con=connection_string,
                schema=schema_name,
                if_exists="append",
                index=False)
        logger.info(f"""  Working on file {it:,} of {num_files:,} - done.""")
