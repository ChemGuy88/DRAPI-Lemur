"""
Run a function in parallel but wait until they're all completed.
"""

import asyncio
import logging
from itertools import repeat

logFormat = logging.Formatter("[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s")

logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logFormat)

logger.addHandler(consoleHandler)

fileHander = logging.FileHandler('test.log')
fileHander.setLevel(logging.DEBUG)
fileHander.setFormatter(logFormat)

logger.addHandler(fileHander)

logger.setLevel(logging.INFO)


def function(x, y):
    """
    """
    logger.info(f"""Executing function with (x, y) = ({x}, {y}).""")
    logger.debug(f"""x + y = {x+y}.""")
    logger.info(f"""Executing function with (x, y) = ({x}, {y}) - Done.""")


if __name__ == "__main__":
    logger.debug("This is a debug message.")
    logger.info("This is an info message")
    xli = [1, 2, 3]
    y = 10

    loop = asyncio.get_event_loop()
    looper = asyncio.gather(*[function(x, y) for x, y in zip(xli, repeat(y))])
    results = loop.run_until_complete(looper)

    logger.info("All done!")
