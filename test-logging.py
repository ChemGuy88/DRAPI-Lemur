"""
Test logging module

This version works at printing logs to the console and a file. However, I also want to capture exceptions or tracebacks in the log file.
"""

import os
import logging
from datetime import datetime as dt
from hermanCode import make_dir_path
from pathlib import Path


def main(loglevel):
    this_file_path = Path(__file__)
    base_dir = this_file_path.absolute().parent

    timestamp = dt.now().strftime("%Y-%m-%d %H-%M-%S")
    logpath = os.path.join(base_dir, "logs", f"log {timestamp}.log")
    make_dir_path(Path(logpath).parent)

    # Define handlers
    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(loglevel)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(loglevel)

    # Define basicConfig
    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler, streamHandler],
                        level=loglevel)

    logging.debug(f"Running '{this_file_path}'.")
    logging.debug(f"`base_dir`: '{this_file_path}'.")
    logging.debug(f"Creating fileHandler with path at '{logpath}'.")

    logging.debug("This is a debug message.")
    logging.info('This is an info message.')
    logging.error("This is an error message.")
    logging.warning("This is a warning!")
    logging.critical("Oh noes!")

    logging.info("Prepare for division by zero...")
    x = 1 / 0  # noqa
    logging.debug("If you can see this you handled the division by zero error.")


if __name__ == "__main__":
    userLogLevel = "DEBUG"
    loglevel = getattr(logging, userLogLevel)
    main(loglevel)
