"""
Herman's utility functions commonly used in his projects
"""

import os
import sys
from pathlib import Path


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
