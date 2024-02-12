"""
Compare two cohort (group) files.
"""

import logging
from typing_extensions import (Literal,
                               Union)
# Third-party packages
import pandas as pd


def mappingAnalysis(x0: Union[pd.DataFrame, pd.Series], m0: pd.DataFrame, logger: logging.Logger, mappingMethod: Literal["inner", "outer"] = "inner") -> None:
    """
    # x0: The vector of input values
    # m0: The matrix of mapping values, an n_m by 2 matrix
    # x1: The vector of output values
    """
    assert len(x0.shape) == 1 or x0.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."
    assert len(m0.shape) == 2, "The mapping table should be of two dimensions."
    assert m0.shape[1] == 2, "The mapping table should be of two columns."
    if isinstance(x0, pd.DataFrame):
        pass
    elif isinstance(x0, pd.Series):
        x0 = pd.DataFrame(x0)
    else:
        raise Exception(f"""`x0` is of an unexpected type: "{type(x0)}".""")
    fromColumn = x0.columns.to_list()[0]
    toColumn = m0.columns.to_list()[1]

    mappingMethodsList = ["inner", "outer"]
    x1 = {}
    for mappingMethod in mappingMethodsList:
        x1[mappingMethod] = x0.set_index(fromColumn).join(other=m0.set_index(fromColumn),
                                                          how=mappingMethod,
                                                          lsuffix="_L",
                                                          rsuffix="_R")

    lenx0 = len(x0)
    lenx0unique = len(x0.drop_duplicates())
    lenm0 = len(m0)
    lenm0_1 = len(m0[fromColumn])
    lenm0_2 = len(m0[toColumn])
    lenm0_1unique = len(m0[fromColumn].drop_duplicates())
    lenm0_2unique = len(m0[toColumn].drop_duplicates())
    lenx1 = {}
    lenx1unique = {}
    for mappingMethod in mappingMethodsList:
        lenx1[mappingMethod] = len(x1[mappingMethod])
        lenx1unique[mappingMethod] = len(x1[mappingMethod].drop_duplicates())

    logger.info(f"""The size of the input group is {lenx0:,}.""")
    logger.info(f"""The size of the input group (unique values) is {lenx0unique:,}.""")
    logger.info(f"""The size of the entire map is {lenm0:,}.""")
    logger.info(f"""The size of the map's left side is {lenm0_1:,}.""")
    logger.info(f"""The size of the map's right side is {lenm0_2:,}.""")
    logger.info(f"""The size of the map's left side (unique values) is {lenm0_1unique:,}.""")
    logger.info(f"""The size of the map's right side (unique values) is {lenm0_2unique:,}.""")
    for mappingMethod in mappingMethodsList:
        logger.info(f"""  Mapping values using method "{mappingMethod}".""")
        logger.info(f"""    The size of the output group is {lenx1[mappingMethod]:,}.""")
        logger.info(f"""    The size of the output group (unique values) is {lenx1unique[mappingMethod]:,}.""")


def compareGroups(group1: Union[pd.DataFrame, pd.Series], group2: Union[pd.DataFrame, pd.Series], logger: logging.Logger) -> None:
    """
    """
    assert len(group1.shape) == 1 or group1.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."
    assert len(group2.shape) == 1 or group2.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."
    if isinstance(group1, pd.DataFrame):
        group1series = group1.iloc[:, 0]
    else:
        group1series = group1
    if isinstance(group2, pd.DataFrame):
        group2series = group2.iloc[:, 0]
    else:
        group2series = group2

    c1l = len(group1series)
    c2l = len(group2series)

    c1inc2 = group1series.isin(group2series)
    c2inc1 = group2series.isin(group1series)

    c1inc2count = c1inc2.sum()
    c2inc1count = c2inc1.sum()

    c1inc2percent = c1inc2count / c1l
    c2inc1percent = c2inc1count / c2l

    intersection = set(group1series.to_list()).intersection(set(group2series.to_list()))
    intersectionl = len(intersection)

    logger.info("""The following results are of the set of groups 1 and 2. I.e., we are only counting the unique values.""")
    logger.info(f"""Group 1 size: {c1l:,}.""")
    logger.info(f"""Group 2 size: {c2l:,}.""")
    logger.info(f"""Size of intersection of groups 1 and 2: {intersectionl:,}.""")
    logger.info(f"""Percent of group 1 in group 2: {c1inc2percent:.2%}.""")
    logger.info(f"""Percent of group 2 in group 1: {c2inc1percent:.2%}.""")


def determineMapType(x0: Union[pd.DataFrame, pd.Series], x1: Union[pd.DataFrame, pd.Series]):
    """
    """
    assert len(x0.shape) == 1 or x0.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."
    assert len(x1.shape) == 1 or x1.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."

    x0duplicated = x0.duplicated().sum() > 0
    x1duplicated = x1.duplicated().sum() > 0

    if x0duplicated and x1duplicated:
        mapType = "m:m"
    elif x0duplicated:
        mapType = "m:1"
    elif x1duplicated:
        mapType = "1:m"
    elif (not x0duplicated) & (not x1duplicated):
        mapType = "1:1"
    else:
        raise Exception("Unexpected error.")

    return mapType


def _determineMapType_MapValues(x0: Union[pd.DataFrame, pd.Series],
                                m0: pd.DataFrame) -> pd.DataFrame:
    """
    """
    assert len(x0.shape) == 1 or x0.shape[1] == 1, "The input vector should be of one dimension or two dimensions with one column."
    assert len(m0.shape) == 2, "The mapping table should be of two dimensions."
    assert m0.shape[1] == 2, "The mapping table should be of two columns."
    if isinstance(x0, pd.DataFrame):
        pass
    elif isinstance(x0, pd.Series):
        x0 = pd.DataFrame(x0)
    else:
        raise Exception(f"""`x0` is of an unexpected type: "{type(x0)}".""")
    fromColumn = x0.columns.to_list()[0]
    toColumn = m0.columns.to_list()[1]
    _ = toColumn

    # Map values
    x0 = pd.DataFrame(x0)  # To allow use of `set_index`
    x1 = x0.set_index(fromColumn).join(other=m0.set_index(fromColumn),
                                       how="inner",
                                       lsuffix="_L",
                                       rsuffix="_R")
    return x1


def determineMapTypeFromMap(x0: Union[pd.DataFrame, pd.Series],
                            m0: pd.DataFrame,
                            logger: Union[logging.Logger, None] = None,
                            x1: Union[pd.DataFrame, pd.Series, None] = None) -> Literal["1:1", "m:1", "1:m"]:
    """
    """
    if x1:
        x1 = x1
    elif isinstance(x1, type(None)):
        x1 = _determineMapType_MapValues(x0=x0,
                                         m0=m0)

    # Count duplicates
    mapType = determineMapType(x0=x0, x1=x1)

    return mapType
