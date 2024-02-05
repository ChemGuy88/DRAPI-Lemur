"""
Copy files to a single destination directory. Optionally this directory can be added to a compressed archive.
"""

import logging
import os
import shutil
import zipfile
from pathlib import Path
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)

# Arguments
LIST_OF_DIRECTORIES = []
LIST_OF_FILES = []
DESTINATION_FOLDER = fr"..\Concatenated Results\disclosure\{getTimestamp()}"

OVERWRITE_IF_EXISTS_FOLDER = False
OVERWRITE_IF_EXISTS_FILE = False

CREATE_COMPRESSED_ARCHIVE = True
DELETE_FOLDER_AFTER_ARCHIVING = True

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = PROJECT_DIR_DEPTH + 1
IDR_DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 4

ROOT_DIRECTORY = "IRB_DIRECTORY"  # TODO One of the following:
                                                 # ["IDR_DATA_REQUEST_DIRECTORY",    # noqa
                                                 #  "IRB_DIRECTORY",                 # noqa
                                                 #  "DATA_REQUEST_DIRECTORY",        # noqa
                                                 #  "PROJECT_OR_PORTION_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Arguments: SQL connection settings
SERVER = "DWSRSRCH01.shands.ufl.edu"
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = None
PWD = os.environ["HFA_UFADPWD"]

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_DIR_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    outputDataDir = dataDir.joinpath("output")
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

if ROOT_DIRECTORY == "PROJECT_OR_PORTION_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir
else:
    raise Exception("An unexpected error occurred.")

# Variables: Path construction: Project-specific
pass

# Variables: SQL Parameters
if UID:
    uid = UID[:]
else:
    uid = fr"{USERDOMAIN}\{USERNAME}"
conStr = f"mssql+pymssql://{uid}:{PWD}@{SERVER}/{DATABASE}"

# Variables: Other
pass

# Directory creation: General
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

if __name__ == "__main__":
    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:


    # Arguments
    `LIST_OF_DIRECTORIES`: "{LIST_OF_DIRECTORIES}"
    `LIST_OF_FILES`: "{LIST_OF_FILES}"
    `DESTINATION_FOLDER`: "{DESTINATION_FOLDER}"
    `OVERWRITE_IF_EXISTS_FOLDER`: "{OVERWRITE_IF_EXISTS_FOLDER}"
    `OVERWRITE_IF_EXISTS_FILE`: "{OVERWRITE_IF_EXISTS_FILE}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}" ----------> "{projectDir}"
    `IRB_DIR_DEPTH`: "{IRB_DIR_DEPTH}" --------------> "{IRBDir}"
    `IDR_DATA_REQUEST_DIR_DEPTH`: "{IDR_DATA_REQUEST_DIR_DEPTH}" -> "{IDRDataRequestDir}"

    `LOG_LEVEL` = "{LOG_LEVEL}"

    # Arguments: SQL connection settings
    `SERVER` = "{SERVER}"
    `DATABASE` = "{DATABASE}"
    `USERDOMAIN` = "{USERDOMAIN}"
    `USERNAME` = "{USERNAME}"
    `UID` = "{UID}"
    `PWD` = censored
    """)

    # Define the destination path
    destinationFolder = Path(DESTINATION_FOLDER)

    # Copy files and directories
    if destinationFolder.exists():
        logger.warning(f"""WARNING: The destination folder already exists: "{destinationFolder.absolute().relative_to(rootDirectory)}".""")
        if OVERWRITE_IF_EXISTS_FOLDER:
            logger.info("""  Removing folder contents to make room for new files.""")
            for fpath in destinationFolder.iterdir():
                logger.info(f"""    Removing "{fpath.absolute().relative_to(rootDirectory)}".""")
                os.remove(fpath)
                logger.info(f"""    Removing "{fpath.absolute().relative_to(rootDirectory)}" - done.""")
        else:
            msg = "  The destination folder exists and no option was passed to over-write it."
            logger.fatal(msg)
            raise Exception(msg)
    else:
        logger.info(f"""Making destination folder: "{destinationFolder.absolute().relative_to(rootDirectory)}".""")
        makeDirPath(destinationFolder)

    logger.info("""Working on list of files.""")
    for fpathString in LIST_OF_FILES:
        fpath = Path(fpathString)
        logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
        dest = destinationFolder.joinpath(fpath.name)
        logger.info(f"""    Saving to "{dest.absolute().relative_to(rootDirectory)}".""")
        shutil.copyfile(fpath, dest)
    logger.info("""Working on list of files - done.""")

    logger.info("""Working on list of directories.""")
    for directoryString in LIST_OF_DIRECTORIES:
        directory = Path(directoryString)
        for fpath in directory.iterdir():
            logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
            dest = destinationFolder.joinpath(fpath.name)
            logger.info(f"""    The destination path is "{dest.absolute().relative_to(rootDirectory)}".""")
            if dest.exists():
                msg = f"""    WARNING: This file already exists: "{dest}"."""
                logger.warning(msg)
                if OVERWRITE_IF_EXISTS_FILE:
                    continueOperation = True
                else:
                    continueOperation = False
            else:
                continueOperation = True
            if continueOperation:
                logger.info("""    Saving to destination path.""")
                shutil.copyfile(fpath, dest)
            else:
                logger.info("""    The file was not saved to the destination path. File over-write is set to `False`.""")
    logger.info("""Working on list of directories - done.""")

    # Create compressed archive
    if CREATE_COMPRESSED_ARCHIVE:
        archivePath = destinationFolder.with_suffix(".ZIP")
        logger.info(f"""Creating compressed archive: "{archivePath.absolute().relative_to(rootDirectory)}"".""")
        if archivePath.exists():
            logger.info("""The archive folder already exists and will be removed before writing.""")
            os.remove(archivePath)
        else:
            pass

        with zipfile.ZipFile(file=archivePath,
                             mode="a",
                             compression=zipfile.ZIP_DEFLATED) as zipObj:
            logger.info("Adding files to archive.")
            for fpath in destinationFolder.iterdir():
                logger.info(f"""  Working on file "{fpath.absolute().relative_to(rootDirectory)}".""")
                newPath = fpath.name
                zipObj.write(filename=fpath, arcname=newPath)
        logger.info("Creating compressed archive - done.")

        if DELETE_FOLDER_AFTER_ARCHIVING:
            logger.info("""Removing intermediate folder.""")
            shutil.rmtree(destinationFolder)
            logger.info("""Removing intermediate folder - done.""")
        else:
            pass

    # End script
    logger.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
