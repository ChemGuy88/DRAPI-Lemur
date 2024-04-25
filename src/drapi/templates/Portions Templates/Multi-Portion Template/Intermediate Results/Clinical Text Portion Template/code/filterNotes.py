"""
Searches and selects notes by the list of note types contained in `NOTE_TYPES_TO_FILTER_BY` and outputs the corresponding metadata and notes text.

Note we distinguish between the following three concepts
    - Note Class (two values)
    - Note Category (four values)
    - Note Type (More than 100 values for each class.)
See the NOTE comment tags in the code for details.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)

# Arguments
FREE_TEXT_DIR_PATH = Path(r"data\output\freeText\...\free_text")  # TODO
COHORT_NAME = ""  # TODO
NOTE_TYPES_TO_FILTER_BY = ["order_impression: IMAGING",
                           "order_narative: IMAGING"]  # TODO
DE_IDENTIFICATION_MAP_PATH_FOR_NOTES = r"data\output\freeText\...\mapping\map_note_link.csv"  # TODO
DE_IDENTIFICATION_MAP_PATH_FOR_ORDERS = r"data\output\freeText\...\mapping\map_order.csv"  # TODO
USE_DE_IDENTIFIED_NOTE_VERSION = True  # TODO
CHUNKSIZE = 10000


# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2
DATA_REQUEST_DIR_DEPTH = PROJECT_DIR_DEPTH + 2
IRB_DIR_DEPTH = DATA_REQUEST_DIR_DEPTH + 0
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

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
IRBDir, _ = successiveParents(thisFilePath, IRB_DIR_DEPTH)
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
noteDeIdentificationMaps = {"Notes": DE_IDENTIFICATION_MAP_PATH_FOR_NOTES,
                            "Orders": DE_IDENTIFICATION_MAP_PATH_FOR_ORDERS}

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
    `FREE_TEXT_DIR_PATH`: "{FREE_TEXT_DIR_PATH}"
    `COHORT_NAME`: "{COHORT_NAME}"
    `NOTE_TYPES_TO_FILTER_BY`: "{NOTE_TYPES_TO_FILTER_BY}"
    `DE_IDENTIFICATION_MAP_PATH_FOR_NOTES`: "{DE_IDENTIFICATION_MAP_PATH_FOR_NOTES}"
    `DE_IDENTIFICATION_MAP_PATH_FOR_ORDERS`: "{DE_IDENTIFICATION_MAP_PATH_FOR_ORDERS}"
    `USE_DE_IDENTIFIED_NOTE_VERSION`: "{USE_DE_IDENTIFIED_NOTE_VERSION}"
    `CHUNKSIZE`: "{CHUNKSIZE}"

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

    # Search by note types
    logger.info("Searching by note types.")
    LIST_OF_NOTE_TARGET_FILES_AND_DIRS = ["_note"]
    LIST_OF_ORDER_TARGET_FILES_AND_DIRS = ["_order_impression",
                                           "_order",
                                           "_order_narrative",
                                           "_order_result_comment"]
    LIST_OF_TARGET_FILES_AND_FOLDERS = LIST_OF_NOTE_TARGET_FILES_AND_DIRS + LIST_OF_ORDER_TARGET_FILES_AND_DIRS
    resultsdi = {}
    for fpath in FREE_TEXT_DIR_PATH.iterdir():
        logger.info(f"""  Working on directory item "{fpath.absolute().relative_to(rootDirectory)}".""")
        if fpath.suffix.lower() == ".csv" and any([fname in fpath.stem for fname in LIST_OF_TARGET_FILES_AND_FOLDERS]):
            logger.info("""    This item has met the criteria for processing.""")
            numChunks = 0
            logger.info("""    Counting the number of chunks in the file.""")
            for dfchunk in pd.read_csv(fpath, chunksize=CHUNKSIZE):
                numChunks += 1
            logger.info("""    Counting the number of chunks in the file - done.""")
            fileResults = pd.DataFrame()
            for it, dfchunk in enumerate(pd.read_csv(fpath, chunksize=CHUNKSIZE), start=1):
                logger.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                mask = dfchunk["NoteType"].isin(NOTE_TYPES_TO_FILTER_BY)
                subset = dfchunk[mask]
                fileResults = pd.concat([fileResults, subset])
            resultsdi[fpath.stem] = fileResults.drop_duplicates()
        else:
            logger.info("""    This item has NOT met the criteria for processing.""")

    # Save search results
    logger.info("Saving search results to the drive.")
    for noteCategory, df in resultsdi.items():
        rsavepath = runOutputDir.joinpath("Selected Notes Metadata",
                                          f"{noteCategory}.CSV")
        makeDirPath(rsavepath.parent)
        df.to_csv(rsavepath, index=False)
    logger.info("Saving search results to the drive - done.")

    # Concatenate results by note class
    logger.info("Concatenating results by note class.")
    results = {"Notes": None,
               "Orders": None}
    # NOTE: Here we introduce the "Note Category" concept, which is one of four values: "Note", "Order Impression", "Order Narrative" or "Order Result Comment".
    for noteCategory, df in resultsdi.items():
        if any([name in noteCategory for name in LIST_OF_NOTE_TARGET_FILES_AND_DIRS]):
            results["Notes"] = pd.concat([results["Notes"], df["LinkageNoteID"]])
        elif any([name in noteCategory for name in LIST_OF_ORDER_TARGET_FILES_AND_DIRS]):
            results["Orders"] = pd.concat([results["Orders"], df["OrderKey"]])
        else:
            raise Exception("Something unexpected happened.")
    # NOTE: Here we introduce the "Note Class" concept, which is one of two values: "Note" or "Order".
    for noteClass, series in results.items():
        series = pd.Series(series)
        results[noteClass] = series.drop_duplicates().sort_values()
    logger.info("Concatenating results by note class - done.")

    # For each note class, filter by its corresponding note identifier, i.e., `LinkageNoteID` or `OrderKey`
    for noteClass, noteIdentifierValues in results.items():
        logger.info(f"""  Working on note class "{noteClass}".""")
        # Get note class identifier map
        if noteClass == "Notes":
            NOTE_IDENTIFIER_TYPE = "LinkageNoteID"
            NOTE_IDENTIFIER_TYPE_DE_IDENTIFIED = "deid_link_note_id"
        elif noteClass == "Orders":
            NOTE_IDENTIFIER_TYPE = "OrderKey"
            NOTE_IDENTIFIER_TYPE_DE_IDENTIFIED = "deid_order_id"
        noteIdentifierValues = pd.DataFrame(noteIdentifierValues)
        noteIdentifierValues = noteIdentifierValues.set_index(NOTE_IDENTIFIER_TYPE).sort_index()
        mapPath = noteDeIdentificationMaps[noteClass]
        noteIdentifierMap = pd.read_csv(mapPath)
        noteIdentifierMap = noteIdentifierMap.set_index(NOTE_IDENTIFIER_TYPE)
        selectedNoteIdentiferMap = noteIdentifierValues.join(noteIdentifierMap, how="inner")
        selectedNoteIdentiferMap = selectedNoteIdentiferMap.reset_index()
        selectedNoteIdentiferMap = selectedNoteIdentiferMap.set_index(NOTE_IDENTIFIER_TYPE_DE_IDENTIFIED)

        # Join map on note text files.
        DICT_OF_TARGET_FILES_AND_FOLDERS = {"Notes": LIST_OF_NOTE_TARGET_FILES_AND_DIRS,
                                            "Orders": LIST_OF_ORDER_TARGET_FILES_AND_DIRS}
        if USE_DE_IDENTIFIED_NOTE_VERSION:
            noteDeIdentificationPrefix = "deid"
        else:
            noteDeIdentificationPrefix = ""
        for fpath in FREE_TEXT_DIR_PATH.glob("**/*"):
            logger.info(f"""    Working on directory item "{fpath.absolute().relative_to(rootDirectory)}".""")
            listOfClassTargetFilesAndFolders = DICT_OF_TARGET_FILES_AND_FOLDERS[noteClass]
            if fpath.suffix.lower() == ".tsv" and any([fname in fpath.stem for fname in listOfClassTargetFilesAndFolders]) and "deid_" in fpath.stem:
                logger.info("""  ..  This item has met the criteria for processing.""")
                # Determine note identifier
                if any([f"{noteDeIdentificationPrefix}{nameRoot}" in fpath.stem for nameRoot in LIST_OF_NOTE_TARGET_FILES_AND_DIRS]):
                    noteIdentifierDeIdentifiedColumnName = "deid_link_note_id"
                elif any([f"{noteDeIdentificationPrefix}{nameRoot}" in fpath.stem for nameRoot in LIST_OF_ORDER_TARGET_FILES_AND_DIRS]):
                    noteIdentifierDeIdentifiedColumnName = "deid_order_id"
                else:
                    raise Exception("Something went wrong.")
                # Count number of chunks
                logger.info("""  ..  Counting the number of chunks in the file.""")
                numChunks = 0
                for dfchunk in pd.read_csv(fpath, chunksize=CHUNKSIZE, delimiter="\t"):
                    numChunks += 1
                # Iterate over chunks
                logger.info("""  ..  Counting the number of chunks in the file - done.""")
                header = True
                mode = "w"
                for it, dfchunk in enumerate(pd.read_csv(fpath, chunksize=CHUNKSIZE, delimiter="\t"), start=1):
                    logger.info(f"""  ..    Working on chunk {it} of {numChunks}.""")
                    # Filter by selected note or order identifiers.
                    dfchunk = dfchunk.set_index(noteIdentifierDeIdentifiedColumnName)
                    selectedText = selectedNoteIdentiferMap.join(dfchunk, how="inner")
                    selectedText = selectedText["note_text"]
                    # Define `savepath` based on `fpath`
                    savepath = runOutputDir.joinpath("Selected Notes",
                                                     "{fpath.stem}.TSV")
                    makeDirPath(savepath.parent)
                    # Save to file
                    selectedText = selectedText.reset_index()
                    selectedText.to_csv(savepath, index=False, header=header, mode=mode, sep="\t")
                    header = False
                    mode = "a"
                logger.info(f"""  ..  Chunks saved to "{savepath.absolute().relative_to(rootDirectory)}".""")
            else:
                logger.info("""  ..  This item has NOT met the criteria for processing.""")

    # End script
    logger.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
