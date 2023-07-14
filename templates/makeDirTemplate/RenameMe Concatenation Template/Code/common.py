"""
Variable constants common to this project
"""

__all__ = ["COLUMNS_TO_DE_IDENTIFY",
           "MODIFIED_OMOP_PORTION_DIR_MAC",
           "MODIFIED_OMOP_PORTION_DIR_WIN",
           "NOTES_PORTION_DIR_MAC",
           "NOTES_PORTION_DIR_WIN",
           "OLD_MAPS_DIR_PATH",
           "OMOP_PORTION_DIR_MAC",
           "OMOP_PORTION_DIR_WIN"]

from pathlib import Path
# Local packages
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_BO, LIST_OF_PHI_VARIABLES_NOTES, LIST_OF_PHI_VARIABLES_OMOP
from drapi.drapi import successiveParents

# Argument meta variables
IRB_NUMBER = None  # TODO  # TODO
PROJECT_ROOT_DIRECTORY_DEPTH = 3  # TODO

projectRootDirectory, _ = successiveParents(Path(__file__).absolute(), PROJECT_ROOT_DIRECTORY_DEPTH)
NOTES_ROOT_DIRECTORY = projectRootDirectory.joinpath("Intermediate Results",
                                                     "Notes Portion",
                                                     "data",
                                                     "output")
# Project arguments
COLUMNS_TO_DE_IDENTIFY = LIST_OF_PHI_VARIABLES_BO + LIST_OF_PHI_VARIABLES_NOTES + LIST_OF_PHI_VARIABLES_OMOP

# `VARIABLE_ALIASES` NOTE: Some variable names are not standardized. This argument is used by the de-identification process when looking for the de-identification map. This way several variables can be de-identified with the same map.
VARIABLE_ALIASES = {"csn": "EncounterCSN",
                    "Patient Key": "PatientKey",
                    "patient_key": "PatientKey"}

VARIABLE_SUFFIXES = {"AuthoringProviderKey": {"columnSuffix": "provider",
                                              "deIdIDSuffix": "PROV"},
                     "AuthorizingProviderKey": {"columnSuffix": "provider",
                                                "deIdIDSuffix": "PROV"},
                     "CosignProviderKey": {"columnSuffix": "provider",
                                           "deIdIDSuffix": "PROV"},
                     "EncounterCSN": {"columnSuffix": "encounter",
                                      "deIdIDSuffix": "ENC"},
                     "EncounterKey": {"columnSuffix": "encounter",
                                      "deIdIDSuffix": "ENC"},
                     "LinkageNoteID": {"columnSuffix": "link_note",
                                       "deIdIDSuffix": "LINK_NOTE"},
                     "MRN_GNV": {"columnSuffix": "patient",
                                 "deIdIDSuffix": "PAT"},
                     "MRN_JAX": {"columnSuffix": "patient",
                                 "deIdIDSuffix": "PAT"},
                     "NoteID": {"columnSuffix": "note",
                                "deIdIDSuffix": "NOTE"},
                     "NoteKey": {"columnSuffix": "note",
                                 "deIdIDSuffix": "NOTE"},
                     "OrderID": {"columnSuffix": "order",
                                 "deIdIDSuffix": "ORD"},
                     "OrderKey": {"columnSuffix": "order",
                                  "deIdIDSuffix": "ORD"},
                     "OrderingProviderKey": {"columnSuffix": "order",
                                             "deIdIDSuffix": "ORD"},
                     "PatientKey": {"columnSuffix": "patient",
                                    "deIdIDSuffix": "PAT"},
                     "Patient Key": {"columnSuffix": "patient",
                                     "deIdIDSuffix": "PAT"},
                     "ProviderKey": {"columnSuffix": "provider",
                                     "deIdIDSuffix": "PROV"},
                     "csn": {"columnSuffix": "encounter",
                             "deIdIDSuffix": "ENC"},
                     "location_id": {"columnSuffix": "location",
                                     "deIdIDSuffix": "LOC"},
                     "patient_key": {"columnSuffix": "patient",
                                     "deIdIDSuffix": "PAT"},
                     "person_id": {"columnSuffix": "patient",
                                   "deIdIDSuffix": "PAT"},
                     "preceding_visit_occurrence_id": {"columnSuffix": "encounter",
                                                       "deIdIDSuffix": "ENC"},
                     "provider_id": {"columnSuffix": "provider",
                                     "deIdIDSuffix": "PROV"},
                     "visit_occurrence_id": {"columnSuffix": "encounter",
                                             "deIdIDSuffix": "ENC"}}

# Portion directories
BO_PORTION_DIR = projectRootDirectory.joinpath("Intermediate Results/BO Portion/data/output/getData/2023-06-28 14-16-28")
NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath(r"free_text")

OMOP_PORTION_DIR_MAC = projectRootDirectory.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = projectRootDirectory.joinpath(r"Intermediate Results\OMOP Portion\data\output\...")  # TODO

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/...")  # TODO

# File criteria
NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
BO_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
ZIP_CODE_PORTION_FILE_CRITERIA = [None]  # TODO

# Maps
OLD_MAPS_DIR_PATH = {"EncounterCSN": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_encounter.csv")],
                     "LinkageNoteID": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note_link.csv")],
                     "NoteKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note.csv")],
                     "OrderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_order.csv")],
                     "PatientKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_patient.csv")],
                     "ProviderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_provider.csv")]}

# Quality assurance
if __name__ == "__main__":
    ALL_VARS = [projectRootDirectory,
                NOTES_ROOT_DIRECTORY,
                NOTES_PORTION_DIR_MAC,
                NOTES_PORTION_DIR_WIN,
                OMOP_PORTION_DIR_MAC,
                OMOP_PORTION_DIR_WIN,
                MODIFIED_OMOP_PORTION_DIR_MAC,
                MODIFIED_OMOP_PORTION_DIR_WIN]

    for li in OLD_MAPS_DIR_PATH.values():
        ALL_VARS.extend(li)

    for path in ALL_VARS:
        print(path.exists())
