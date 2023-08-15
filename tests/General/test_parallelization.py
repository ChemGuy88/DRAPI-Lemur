"""
Test parallelization with logging.
"""

import logging
from itertools import repeat
from multiprocessing import Pool

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

    with Pool(4) as pool:
        pool.starmap(function, zip(xli, repeat(y)))
