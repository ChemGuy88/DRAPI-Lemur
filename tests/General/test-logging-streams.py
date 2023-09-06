"""
If I import a function with a logger in it, will it still send messages to the main script's stream and file handlers?

So far I've discovered that having just one file and stream handler at the top level (root, this file) is enough. Adding another handler in the function's module will cause duplicate logging messages.
"""

import logging
import os
from datetime import datetime as dt
from drapi.drapi import replace_sql_query, makeDirPath
from pathlib import Path

loglevel = "DEBUG"

this_file_path = Path(__file__)
base_dir = this_file_path.absolute().parent
timestamp = dt.now().strftime("%Y-%m-%d %H-%M-%S")
logpath = os.path.join(base_dir, "logs", this_file_path.stem, f"log {timestamp}.log")
makeDirPath(Path(logpath).parent)

# Define handlers
fileHandler = logging.FileHandler(logpath)
fileHandler.setLevel(loglevel)
streamHandler = logging.StreamHandler()
streamHandler.setLevel(loglevel)

# Define basicConfig
logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                    handlers=[fileHandler, streamHandler],
                    level=loglevel)

logging.debug(f"fileHandler level: {fileHandler.level}\nstreamHandler level: {streamHandler.level}")

query = """SELECT
    generic_Column -- this is a column name
FROM
-- table_A_XXXXX  -- table A
table_B_XXXXX -- table B"""

logging.debug("This is a debug message.")
logging.info('This is an info message.')
logging.error("This is an error message.")
logging.warning("This is a warning!")
logging.critical("Oh noes!")

# Logging messages from the function call below will be handled both by the handler in the function's module and also by the handler in this main script.
nq = replace_sql_query(query, "XXXXX", "12345", "DEBUG")

logging.info(f"""Finished running "{__file__}".""")
