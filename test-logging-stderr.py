"""
This redirects, but does not duplicate, stdout and stderr to a log file using the logging package.
"""

import logging
import os
import sys
from datetime import datetime as dt
from hermanCode.hermanCode import make_dir_path, StreamToLogger
from pathlib import Path

# Set and make log path
timestamp = dt.now().strftime("%Y-%m-%d %H-%M-%S")
base_dir = Path(__file__).absolute().parent
logpath = os.path.join(base_dir, "logs", f"log {timestamp}.log")
make_dir_path(Path(logpath).parent)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    filename=logpath,
                    filemode='a')
log = logging.getLogger('foobar')
sys.stdout = StreamToLogger(log, logging.INFO)
sys.stderr = StreamToLogger(log, logging.ERROR)
print('Test to standard out')
raise Exception('Test to standard error')
