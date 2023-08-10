"""
Log messages with log level values above 10 to the stream handler, and messages wtih log level values above 0 to the file handler.

h/t https://stackoverflow.com/questions/58965871/logger-that-logs-to-console-and-file-at-different-levels
"""

import logging

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

if __name__ == "__main__":
    logger.debug("This is a debug message.")
    logger.info("This is an info message")
