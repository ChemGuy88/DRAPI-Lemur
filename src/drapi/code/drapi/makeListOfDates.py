from typing import (Literal,
                    Union)
# Third-party packages
import pandas as pd
from pandas._libs.tslibs import BaseOffset


def makeListOfDates(start: str,
                    end: str,
                    period: Union[Literal["D", "h", "M", "Q", "s", "Y"],
                                  BaseOffset],
                    periodValue: Union[int, float],
                    dateFormat: str= "%Y-%m-%d"):
    """
    Makes a list of dates of the form `'date1' and 'date2', 'date2' and 'date3'`.)
    """
    listOfDates = []
    timeStamp_0 = pd.to_datetime(start)
    timeStamp_n = pd.to_datetime(end)
    period_0 = timeStamp_0.to_period(period)
    period_1 = period_0 + periodValue
    timeStamp_1 = period_1.to_timestamp()
    while timeStamp_1.toordinal() < timeStamp_n.toordinal():
        date_0 = timeStamp_0.strftime(dateFormat)
        date_1 = timeStamp_1.strftime(dateFormat)
        string = f"""'{date_0}' and '{date_1}'"""
        listOfDates.append(string)
        timeStamp_0 = timeStamp_1
        period_0 = timeStamp_0.to_period(period)
        period_1 = period_0 + periodValue
        timeStamp_0 = period_0.to_timestamp()
        timeStamp_1 = period_1.to_timestamp()
    timeStamp_1 = timeStamp_n
    date_0 = timeStamp_0.strftime(dateFormat)
    date_1 = timeStamp_1.strftime(dateFormat)
    string = f"""'{date_0}' and '{date_1}'"""
    listOfDates.append(string)
    return listOfDates

