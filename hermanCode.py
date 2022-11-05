"""
Herman's utility functions commonly used in his projects
"""

import logging
import os
import re
import sys
from pathlib import Path


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    h/t to https://stackoverflow.com/a/39215961/5478086
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


class LoggerWriter:
    """
    h/t to https://stackoverflow.com/a/31688396/5478086
    """

    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        self.level(sys.stderr)


def make_dir_path(directory_path):
    """
    Check if all directories exists in a path. If not, create them
    """
    path_obj = Path(directory_path)
    paths = list(path_obj.parents)[::-1] + [path_obj]
    for dir in paths:
        if not os.path.exists(dir):
            os.mkdir(dir)


def replace_sql_query(query, old, new):
    """
    Replaces text in a SQL query only if it's not commented out. I.e., this function applies string.replace() only if the string doesn't begin with "--".
    """
    pattern = r"^\w*--"
    li = query.split("\n")
    result = []
    logging.debug("Starting")
    for line in li:
        logging.debug(f"""  Working on "{line}".""")
        obj = re.search(pattern, line)
        if obj:
            logging.debug("    Passing")
            nline = line
        else:
            nline = line.replace(old, new)
            logging.debug(f"""    Transforming "{line}" --> "{nline}".""")
        logging.debug("  Appending...")
        result.append(nline)
    logging.debug("Finished")
    return "\n".join(result)
