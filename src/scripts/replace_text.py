"""
Replaces text using byte strings.

This is useful for converting CRLF to LF. You can do so like this:

```bash
python replaceText.py -f FILEPATH -bo $'\\r\\n' -bn $'\\n'
```
"""

import argparse
import logging
import multiprocessing as pp
import os
import pprint
import shutil
from functools import partial
from pathlib import Path
from typing import List
# Third-party packages
pass
# First-party packages
from drapi.code.drapi.cli_parsers import (parse_string_to_boolean,
                                          parse_string_to_bytes)
from drapi.code.drapi.drapi import (choosePathToLog,
                                    getTimestamp,
                                    loggingChoiceParser,
                                    makeDirPath)
from drapi.code.drapi.replace_text import replace_text_wrapper
from drapi import loggingChoices
from drapi import __version__ as drapiVersion


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments
    parser.add_argument("--list_of_file_paths",
                        type=Path,
                        required=True,
                        nargs="+",
                        help="The list of file paths to convert.")

    # Arguments: group 1
    parser_group_old_text = parser.add_mutually_exclusive_group(required=True)
    parser_group_old_text.add_argument("--old_text",
                        type=str,
                        help="The text to replace.")
    parser_group_old_text.add_argument("--old_text_bytes",
                        type=parse_string_to_bytes,
                        help="""The text to replace, as Python literal bytes, e.g. `"\\x00"` for `b"\\x00"` or `"Column 1\\tColumn2" for `b"Column 1\\tColumn2".""")

    # Arguments: group 2
    parser_group_new_text = parser.add_mutually_exclusive_group(required=True)
    parser_group_new_text.add_argument("--new_text",
                        type=str,
                        help="The text with which to replace.")
    parser_group_new_text.add_argument("--new_text_bytes",
                        type=parse_string_to_bytes,
                        help="""The text with which to replace, as Python literal bytes, e.g. `"\\x00"` for `b"\\x00"` or `"Column 1\\tColumn2" for `b"Column 1\\tColumn2".""")
    
    # Arguments: Meta-parameters
    parser.add_argument("--TIMESTAMP",
                        type=str)
    parser.add_argument("--LOG_LEVEL",
                        default=10,
                        type=loggingChoiceParser,
                        choices=loggingChoices,
                        help="""Increase output verbosity. See "logging" module's log level for valid values.""")

    argNamespace = parser.parse_args()

    # Parsed arguments
    list_of_file_paths: List[Path] = argNamespace.list_of_file_paths

    old_text: str = argNamespace.old_text
    new_text: str = argNamespace.new_text
    old_text_bytes: bytes = argNamespace.old_text_bytes
    new_text_bytes: bytes = argNamespace.new_text_bytes

    # Parsed arguments: Meta-parameters
    TIMESTAMP: str = argNamespace.TIMESTAMP
    LOG_LEVEL: str = argNamespace.LOG_LEVEL
    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    # >>> Custom argument parsing: Parsing 1 >>>
    if True:
        if any([old_text_bytes, new_text_bytes]):
            as_bytes = True
        else:
            as_bytes = False

        if old_text:
            if as_bytes:
                old_text_ = old_text.encode()
            else:
                old_text = old_text
        elif old_text_bytes:
            old_text_ = old_text_bytes
        else:
            raise Exception
        
        if new_text:
            if as_bytes:
                new_text_ = new_text.encode()
            else:
                new_text_ = new_text
        elif new_text_bytes:
            new_text_ = new_text_bytes
        else:
            raise Exception
    # <<< Custom argument parsing: Parsing 1 <<<

    # >>> Custom argument parsing: Parsing 2 >>>
    # <<< Custom argument parsing: Parsing 2 <<<
    # <<< Custom argument parsing <<<

    # >>> Argument checks >>>
    # NOTE TODO Look into handling this natively with `argparse` by using `subcommands`. See "https://stackoverflow.com/questions/30457162/argparse-with-different-modes"
    # >>> Argument checks: Check 1 >>>
    pass
    # <<< Argument checks: Check 1 <<<
    # >>> Argument checks: Check 2 >>>
    pass
    # <<< Argument checks: Check 2 <<<
    # <<< Argument checks <<<

    # Variables: Path construction: General
    if TIMESTAMP:
        runTimestamp = TIMESTAMP
    else:
        runTimestamp = getTimestamp()
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    currentWorkingDir = Path(os.getcwd()).absolute()
    projectDir = currentWorkingDir
    dataDir = projectDir.joinpath("data")
    if dataDir:
        inputDataDir = dataDir.joinpath("input")
        intermediateDataDir = dataDir.joinpath("intermediate")
        outputDataDir = dataDir.joinpath("output")
        if intermediateDataDir:
            runIntermediateDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
        if outputDataDir:
            runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
    logsDir = projectDir.joinpath("logs")
    if logsDir:
        runLogsDir = logsDir.joinpath(thisFileStem)
    sqlDir = projectDir.joinpath("sql")

    # Variables: Path construction: Project-specific
    pass

    # Variables: Other
    pass

    # Directory creation: General
    makeDirPath(runIntermediateDir)
    makeDirPath(runOutputDir)
    makeDirPath(runLogsDir)

    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    logFormat = logging.Formatter("""[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s""")

    logger = logging.getLogger(__name__)

    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(9)
    fileHandler.setFormatter(logFormat)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)
    streamHandler.setFormatter(logFormat)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    logger.setLevel(9)

    logger.info(f"""Begin running "{choosePathToLog(path=thisFilePath, rootPath=projectDir)}".""")
    logger.info(f"""DRAPI-Lemur version is "{drapiVersion}".""")
    logger.info(f"""All other paths will be reported in debugging relative to the current working directory: "{choosePathToLog(path=projectDir, rootPath=projectDir)}".""")

    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)  # TODO Remove secrets from list to print, e.g., passwords.
    logger.info(f"""Script arguments:\n{argListString}""")

    # >>> Begin script body >>>

    # Parallel implementation
    with pp.Pool() as pool:
        # NOTE TODO For developer: should not pass implicitely-valued None-types to the function. I should handle this better, maybe by using `eval`. See https://www.geeksforgeeks.org/execute-string-code-python/
        results = pool.map(partial(replace_text_wrapper,
                                old_text=old_text_,
                                new_text=new_text_,
                                output_dir=runOutputDir),
                        list_of_file_paths)

    # <<< End script body <<<

    # Output location summary
    logger.info(f"""Script output is located in the following directory: "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")

    # Remove intermediate files, unless running in `DEBUG` mode.
    if logger.getEffectiveLevel() > 10:
        logger.info("Removing intermediate files.")
        shutil.rmtree(runIntermediateDir)
        logger.info("Removing intermediate files - done.")

    # Script end confirmation
    logger.info(f"""Finished running "{choosePathToLog(path=runOutputDir, rootPath=projectDir)}".""")
