"""
Get all variables/columns of tables/files in the project.
"""

import logging
import os
import sys
from pathlib import Path
# Third-party packages
import numpy as np
import pandas as pd
# Local packages
from hermanCode.hermanCode import getTimestamp, make_dir_path

# Arguments
LOG_LEVEL = "DEBUG"
PORTIONS_OUTPUT_DIR_PATH_MAC = {"Notes": Path("/Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Shukla/IRB202001660 DatReq02/Intermediate Results/Notes Portion/data/output/free_text"),
                                "OMOP": Path("/Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Shukla/IRB202001660 DatReq02/Intermediate Results/OMOP Portion/data/output/2023-03-09 10-57-42")}
PORTIONS_OUTPUT_DIR_PATH_WINDOWS = {"Notes": Path(""),
                                    "OMOP": Path("")}

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.absolute().parent.parent
IRBDir = projectDir.parent
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    intermediateDataDir = dataDir.joinpath("intermediate")
    outputDataDir = dataDir.joinpath("output")
    if intermediateDataDir:
        runIntermediateDataDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

# Variables: Path construction: OS-specific
isAccessible = np.all([path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_MAC.values()]) or np.all([path.exists() for path in PORTIONS_OUTPUT_DIR_PATH_WINDOWS.values()])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_MAC
    elif operatingSystem == "win32":
        portionsOutputDirPath = PORTIONS_OUTPUT_DIR_PATH_WINDOWS
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    # portionsOutputDirPath = None
    print("Not implement")
    sys.exit()

# Directory creation: General
make_dir_path(runIntermediateDataDir)
make_dir_path(runOutputDir)
make_dir_path(runLogsDir)

if __name__ == "__main__":
    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(LOG_LEVEL)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)

    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler, streamHandler],
                        level=LOG_LEVEL)

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `projectDir`: "{projectDir}".""")

    # Script

    def theThing(variable, funcs):
        """
        Applies one variable to multiple functions
        """
        return

    # Get columns
    columns = {}
    for portionName, portionPath in portionsOutputDirPath.items():
        content_paths = [Path(dirObj) for dirObj in os.scandir(portionPath)]
        content_names = "\n  ".join(sorted([path.name for path in content_paths]))
        dirRelativePath = portionPath.relative_to(IRBDir)
        logging.info(f"""Reading files from the directory "{dirRelativePath}". Below are its contents:""")
        for fpath in sorted(content_paths):
            logging.info(f"""  {fpath.name}""")
        for file in content_paths:
            conditions = [lambda x: x.is_file(), lambda x: x.suffix == ".csv", lambda x: x.name != ".DS_Store"]
            conditionResults = [func(file) for func in conditions]
            if all(conditionResults):
                logging.debug(f"""  Reading "{file.relative_to(IRBDir)}".""")
                df = pd.read_csv(file, dtype=str, nrows=10)
                columns[file.name] = df.columns

    # Get all columns by file
    logging.info("""Printing columns by file.""")
    allColumns = set()
    it = 0
    for key, value in columns.items():
        if it > 0:
            logging.info(key)
            logging.info("")
            for el in sorted(value):
                logging.info(f"  {el}")
                allColumns.add(el)
            logging.info("")
        it += 1

    # Get all columns by portion
    # TODO
    pass

    # Print the set of all columns
    logging.info("""Printing the set of all columns.""")
    for el in sorted(list(allColumns)):
        logging.info(f"  {el}")

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
