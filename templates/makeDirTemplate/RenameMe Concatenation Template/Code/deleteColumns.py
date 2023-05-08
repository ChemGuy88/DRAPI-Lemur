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
from hermanCode.hermanCode import getTimestamp, make_dir_path

# Arguments
LOG_LEVEL = "DEBUG"

BO_FILES_TO_RELEASE = ["Bian_IRB202202436.csv"]
NOTES_METADATA_FILES_TO_RELEASE = ["provider_metadata.csv",
                                   "subjects_note_metadata.csv",
                                   "subjects_order_impression_metadata.csv",
                                   "subjects_order_metadata.csv",
                                   "subjects_order_narrative_metadata.csv",
                                   "subjects_order_result_comment_metadata.csv"]
OMOP_FILES_TO_RELEASE = ["condition_occurrence.csv",
                         "death.csv",
                         "device_exposure.csv",
                         "drug_exposure.csv",
                         "measurement.csv",
                         "measurement_laboratories.csv",
                         "person.csv",
                         "procedure_occurrence.csv"]
ZIP_CODE_FILES_TO_RELEASE = ["zipcodes.csv"]
FILES_TO_RELEASE = BO_FILES_TO_RELEASE + NOTES_METADATA_FILES_TO_RELEASE + OMOP_FILES_TO_RELEASE + ZIP_CODE_FILES_TO_RELEASE

CONCATENATED_PORTIONS_DIR_MAC = Path("data/output/deIdentify/...")
CONCATENATED_PORTIONS_DIR_WIN = Path("data/output/deIdentify/...")

MAC_PATHS = [CONCATENATED_PORTIONS_DIR_MAC]
WIN_PATHS = [CONCATENATED_PORTIONS_DIR_WIN]

CONCATENATED_PORTIONS_FILE_CRITERIA = [lambda pathObj: pathObj.name in FILES_TO_RELEASE]

LIST_OF_PORTION_CONDITIONS = [CONCATENATED_PORTIONS_FILE_CRITERIA]

COLUMNS_TO_DELETE = ["address_1",
                     "address_2",
                     "condition_occurrence_id",
                     "device_exposure_id",
                     "drug_exposure_id",
                     "location_source_value",
                     "measurement_id",
                     "observation_id",
                     "person_source_value",
                     "procedure_occurrence_id",
                     "visit_detail_id"]
COLUMNS_TO_DELETE_DICT = {"Bian_IRB202202436": ["Accession #",
                                                "Medical Record Number",
                                                "Managing Physician",
                                                "Prim  surgeon Code",
                                                "F/u Physicians"],
                          "condition_occurrence": [None],
                          "death": ["cause_concept_id",
                                    "cause_source_concept_id",
                                    "cause_source_value"],
                          "device_exposure": [None],
                          "drug_exposure": ["sig"],
                          # Why were the below variables for "measurement" not released before? They seem useful.
                          "measurement": ["measurement_concept_id",         # Totally populated
                                          "measurement_source_concept_id",  # Totally populated
                                          "measurement_time",               # Totally populated
                                          "measurement_type_concept_id",    # Totally populated
                                          "operator_concept_id",            # Totally un-populated (all nans)
                                          "unit_concept_id",                # Populated
                                          "value_as_concept_id"],           # Totally un-populated (all nans)
                          "measurement_laboratories": ["measurement_concept_id",
                                                       "measurement_datetime",
                                                       "measurement_id",
                                                       "measurement_source_concept_id",
                                                       "measurement_time",
                                                       "measurement_type_concept_id",
                                                       "operator_concept_id",
                                                       "unit_concept_id",
                                                       "value_as_concept_id"],
                          "person": [None]}

CHUNK_SIZE = 50000

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir = thisFilePath.absolute().parent.parent
IRBDir = projectDir.parent  # Uncommon. TODO: Adjust directory depth/level as necessary
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
    notesPortionDir = None
    omopPortionDir = None

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
    logging.info(f"""All other paths will be reported in debugging relative to `IRBDir`: "{IRBDir}".""")

    # De-identify columns
    logging.info("""Deleting columns not authorized for release.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.absolute().relative_to(IRBDir)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(IRBDir)}".""")
            conditions = [condition(file) for condition in fileConditions]
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
                    logging.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(IRBDir)}".""")
            else:
                logging.info("""    This file does not need to be processed.""")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(IRBDir)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(IRBDir)}".""")
