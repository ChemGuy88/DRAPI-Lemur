"""
De-identify files

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Assign portion name to each path (per OS) so that portion files are stored in their respective folders, this prevents file from being overwritten in the unlikely, but possible, case files from different portions have the same name.
# TODO Investigate if a symlink can be made for files that are copied without alteration, to save space and time on larger projects.
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getTimestamp, makeDirPath, successiveParents
from common import DATA_REQUEST_ROOT_DIRECTORY_DEPTH, BO_PORTION_DIR_MAC, BO_PORTION_DIR_WIN, NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, BO_PORTION_FILE_CRITERIA, NOTES_PORTION_FILE_CRITERIA, OMOP_PORTION_FILE_CRITERIA, ZIP_CODE_PORTION_FILE_CRITERIA, ZIP_CODE_PORTION_DIR_MAC, ZIP_CODE_PORTION_DIR_WIN

# Arguments: File location definition: By portions
# These are imported from the `common` module.
pass

# Arguments: File location definition: By concatenation
CONCATENATED_PORTIONS_DIR_MAC = Path("data/output/deIdentify/...")
CONCATENATED_PORTIONS_DIR_WIN = Path("data/output/deIdentify/...")

# Arguments: File location definition: OS-specific
# There are two typical workflows. Deleting columns in the beginning of the workflow, or towards the end, after it's been de-identified (i.e., "concatenated")
if True:
    MAC_PATHS = [BO_PORTION_DIR_MAC, NOTES_PORTION_DIR_MAC, OMOP_PORTION_DIR_MAC, ZIP_CODE_PORTION_DIR_MAC]
    WIN_PATHS = [BO_PORTION_DIR_WIN, NOTES_PORTION_DIR_WIN, OMOP_PORTION_DIR_WIN, ZIP_CODE_PORTION_DIR_WIN]
elif True:
    MAC_PATHS = [CONCATENATED_PORTIONS_DIR_MAC]
    WIN_PATHS = [CONCATENATED_PORTIONS_DIR_WIN]

# Arguments: Definition of criteria for file release
# NOTE (Developer's Note) The files to release and the file criteiria both act as criteria to release. The argument structure here is not very clear and it will take some time to create a generalizeable template. However, it seems that `LIST_OF_PORTION_CONDITIONS` is the only output of this arguments section, i.e., the only require input for the script. Also note that each portion has its own criteria, but they are not used in the template.
BO_FILES_TO_RELEASE = ["..."]  # TODO
COHORT_NAME = ""  # TODO
NOTES_METADATA_FILES_TO_RELEASE = ["provider_metadata.csv",
                                   f"{COHORT_NAME}_note_metadata.csv",
                                   f"{COHORT_NAME}_order_impression_metadata.csv",
                                   f"{COHORT_NAME}_order_metadata.csv",
                                   f"{COHORT_NAME}_order_narrative_metadata.csv",
                                   f"{COHORT_NAME}_order_result_comment_metadata.csv"]
OMOP_FILES_TO_RELEASE = ["condition_occurrence.csv",
                         "death.csv",
                         "device_exposure.csv",
                         "drug_exposure.csv",
                         "location.csv",
                         "measurement_laboratories.csv",
                         "measurement.csv",
                         "observation_period.csv",
                         "observation.csv",
                         "person.csv",
                         "procedure_occurrence.csv",
                         "visit_occurrence.csv"]
ZIP_CODE_FILES_TO_RELEASE = ["zipcodes.csv"]

FILES_TO_RELEASE = BO_FILES_TO_RELEASE + NOTES_METADATA_FILES_TO_RELEASE + OMOP_FILES_TO_RELEASE + ZIP_CODE_FILES_TO_RELEASE

_ = BO_PORTION_FILE_CRITERIA
_ = NOTES_PORTION_FILE_CRITERIA
_ = OMOP_PORTION_FILE_CRITERIA
_ = ZIP_CODE_PORTION_FILE_CRITERIA

CONCATENATED_PORTIONS_FILE_CRITERIA = [lambda pathObj: pathObj.name in FILES_TO_RELEASE,
                                       lambda pathObj: pathObj.suffix.lower() == ".csv",
                                       lambda pathObj: pathObj.is_file()]

LIST_OF_PORTION_CONDITIONS = [CONCATENATED_PORTIONS_FILE_CRITERIA]

# Arguments: Columns to delete
# TODO Columns to delete. The list variable deletes column matches in any file. The dictionary variable delete the columns that are in the file named in the dictionary key. Below are typical values for a limited data release.
COLUMNS_TO_DELETE = ["person_source_value",
                     # The columns below are non-informative because they only uniquely identify the row in the table
                     "condition_occurrence_id",
                     "device_exposure_id",
                     "drug_exposure_id",
                     "location_source_value",
                     "measurement_id",
                     "observation_id",
                     "procedure_occurrence_id",
                     "visit_detail_id"]
COLUMNS_TO_DELETE_DICT = {"condition_occurrence": [],
                          "death": [],
                          "device_exposure": [],
                          "drug_exposure": ["sig"],
                          "encounters": [],
                          "location": ["address_1",
                                       "address_2"],
                          "measurement": [],
                          "measurement_laboratories": [],
                          "observation": [],
                          "observation_period": [],
                          "person": [],
                          "procedure_occurrence": [],
                          "visit_occurrence": []}

# Arguments: General

CHUNK_SIZE = 50000

# Arguments: Meta-variables
CONCATENATED_RESULTS_DIRECTORY_DEPTH = DATA_REQUEST_ROOT_DIRECTORY_DEPTH - 1
PROJECT_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH  # The concatenation suite of scripts is considered to be the "project".
IRB_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH + 2
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "DATA_REQUEST_DIRECTORY"  # TODO One of the following:
                                           # ["IDR_DATA_REQUEST_DIRECTORY",      # noqa
                                           #  "IRB_DIRECTORY",                   # noqa
                                           #  "DATA_REQUEST_DIRECTORY",          # noqa
                                           #  "CONCATENATED_RESULTS_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
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

if ROOT_DIRECTORY == "CONCATENATED_RESULTS_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    print("Not implemented. Check settings in your script.")
    sys.exit()

# Directory creation: General
makeDirPath(runIntermediateDataDir)
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

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
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # De-identify columns
    logging.info("""Deleting columns not authorized for release.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            logging.info(f"""  Conditions: "{conditions}".""")
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logging.info("""    File has met all conditions for processing.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    # Work on chunk
                    logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        logging.info(f"""  ..    Working on column "{columnName}".""")
                        if file.stem in COLUMNS_TO_DELETE_DICT.keys():
                            listOfColumns = COLUMNS_TO_DELETE + COLUMNS_TO_DELETE_DICT[file.stem]
                        else:
                            listOfColumns = COLUMNS_TO_DELETE
                        if columnName in listOfColumns:
                            logging.info("""  ..  ..  Column must be deleted. Deleting column.""")
                            dfChunk = dfChunk.drop(columns=columnName)
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logging.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logging.info("""    This file does not need to be processed.""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
