"""
"""

import logging
import re
from pathlib import Path
from typing import List
from typing_extensions import (Union,
                               Tuple)
# Third-party packages
import pandas as pd
# First-party packages
from drapi.code.drapi.drapi import readDataFile


def expandColumn(tableOrPath: Union[pd.DataFrame, Path, str],
                 columnToSplit: Union[int, str],
                 nameOfNewColumns: List[Union[int, str]],
                 locationOfNewColumns: List[int],
                 splittingPattern: str,
                 logger: logging.Logger) -> pd.DataFrame:
    """
    """
    _ = logger

    if isinstance(tableOrPath, (str)):
        fpath = Path(tableOrPath)
        table = readDataFile(fname=fpath)
        table = pd.DataFrame(table)  # For type hinting
    elif isinstance(tableOrPath, Path):
        table = readDataFile(fname=tableOrPath)
        table = pd.DataFrame(table)  # For type hinting
    else:
        table = tableOrPath

    def splittingFunction(string_: str) -> Tuple[str]:
        """
        """
        reObj = re.search(splittingPattern, string_)
        if reObj:
            return reObj.groups()
        else:
            return None

    series0 = table[columnToSplit].apply(splittingFunction)

    table = table.drop(columns=columnToSplit)
    for it, (columnName, location) in enumerate(zip(nameOfNewColumns, locationOfNewColumns)):
        series = series0.apply(lambda tu: tu[it])
        table.insert(loc=location,
                     column=columnName,
                     value=series)

    return table


def expandColumnWrapper(runOutputPath: Path,
                        tableOrPath: Union[pd.DataFrame, Path, str],
                        columnToSplit: Union[int, str],
                        nameOfNewColumns: List[Union[int, str]],
                        locationOfNewColumns: List[int],
                        splittingPattern: str,
                        logger: logging.Logger,
                        separator: str = ",") -> None:
    """
    """
    newTable = expandColumn(tableOrPath=tableOrPath,
                            columnToSplit=columnToSplit,
                            nameOfNewColumns=nameOfNewColumns,
                            locationOfNewColumns=locationOfNewColumns,
                            splittingPattern=splittingPattern,
                            logger=logger)
    newTable.to_csv(runOutputPath,
                    index=False,
                    sep=separator)
