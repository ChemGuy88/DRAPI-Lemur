"""
__init__ file for "drapi" package
"""

import logging
from pathlib import Path
from os.path import dirname
PATH = Path(dirname(__file__)).absolute()

__version__ = "1.0.47"

# Logging choices
loggingChoices_Numeric_Min = min(logging.getLevelNamesMapping().values())
loggingChoices_Numeric_Max = max(logging.getLevelNamesMapping().values())
loggingChoices_Numeric = list(range(loggingChoices_Numeric_Min, loggingChoices_Numeric_Max + 1))
loggingChoices_String = list(logging.getLevelNamesMapping().keys())
loggingChoices = loggingChoices_Numeric + loggingChoices_String
