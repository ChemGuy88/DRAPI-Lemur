"""
"""

import datetime
import sys
import time
from datetime import datetime as dt
from typing import Union
# Third-party libraries
import pandas as pd
# Local libraries
from hermanCode.hermanCode import getTimestamp


def checkTime(nowTime: Union[datetime.datetime, datetime.time], min: str = "07:00:00", max: str = "23:00:00"):
    """
    """
    # Convert string date-times to pandas datetime object.
    if min:
        min = pd.to_datetime(min)
    if max:
        max = pd.to_datetime(max)

    print(f"`nowTime`: {nowTime}")
    print(f"`min`: {min}")
    print(f"`max`: {max}")

    # Return results
    if min and max:
        print(f"`min` < `nowTime` < `max`: {min < nowTime < max}")
        return min < nowTime < max
    elif min:
        print(f"`min` < `nowTime`: {min < nowTime}")
        return min < nowTime
    elif max:
        print(f"`min` < `nowTime` < `max`: {nowTime < max}")
        return nowTime < max


def delay(nowTime: Union[datetime.datetime, datetime.time], targetTime: Union[str, datetime.datetime, datetime.time]):
    """
    """
    if isinstance(targetTime, str):
        targetTime = pd.to_datetime(targetTime)
    difference = targetTime - nowTime
    time.sleep(difference.seconds)


def workerSimple():
    """
    """
    nowTime = dt.now()
    if nowTime.hour < 23 or nowTime.hour > 7:
        pass  # Do something
    else:
        sys.exit()


def workerBetter():
    """
    """
    timeStamp = getTimestamp()

    print(f"[{timeStamp}] Starting worker")

    nowTime = dt.now()
    minTime = "11:45"
    maxTime = "11:47"
    while not checkTime(nowTime, minTime, maxTime):

        print(f"[{timeStamp}] Delaying...")

        delay(nowTime, maxTime)
    pass  # Do something

    print(f"[{timeStamp}] I'm working!")


# Test
workerBetter()
