"""
Utility functions for the notes pipelines.
"""

import re
from typing import Union


def isNotesChunk(string: str, cohortName: str) -> Union[bool, None]:
    """
    Checks if a filename is the intermediate chunked version of the final table and returns the corresponding boolean. If the file name does not match the notes pipeline filename format, it returns `None`.
    """
    pattern = rf"^(?P<cohortName>{cohortName})_(?P<noteType>note|order_impression|order|order_narrative|order_result_comment)_metadata_?(?P<chunkNum>\d+)?.csv$"
    matchObj = re.match(pattern, string)
    if matchObj:
        groupdict = matchObj.groupdict()
        chunkNum = groupdict["chunkNum"]
        if chunkNum:
            isChunk = True
        else:
            isChunk = False
    else:
        isChunk = None
    return isChunk
