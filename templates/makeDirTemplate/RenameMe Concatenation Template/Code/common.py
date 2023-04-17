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

# Argument meta variables
PROJECT_ROOT_DIRECTORY = Path(__file__).absolute().parent.parent
NOTES_ROOT_DIRECTORY = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results",
                                                       "Notes Portion",
                                                       "data",
                                                       "output")

# Project arguments
COLUMNS_TO_DE_IDENTIFY = ["AuthoringProviderKey",
                          "AuthorizingProviderKey",
                          "CosignProviderKey",
                          "EncounterCSN",
                          "EncounterKey",
                          "LinkageNoteID",
                          "MRN_GNV",
                          "MRN_JAX",
                          "NoteID",  # ?
                          "NoteKey",  # ?
                          "OrderID",  # ?
                          "OrderKey",  # ?
                          "OrderingProviderKey",
                          "PatientKey",
                          "Patient Key",
                          "ProviderKey",
                          "csn",
                          "location_id",
                          "patient_key",
                          "preceding_visit_occurrence_id",
                          "provider_id",
                          "visit_occurrence_id"]

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
                                "deIdIDSuffix": "NOTE"},  # ?
                     "NoteKey": {"columnSuffix": "note",
                                 "deIdIDSuffix": "NOTE"},  # ?
                     "OrderID": {"columnSuffix": "order",
                                 "deIdIDSuffix": "ORD"},  # ?
                     "OrderKey": {"columnSuffix": "order",
                                  "deIdIDSuffix": "ORD"},  # ?
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

NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath(r"free_text")

OMOP_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = PROJECT_ROOT_DIRECTORY.joinpath(r"Intermediate Results\OMOP Portion\data\output\...")  # TODO

# File criteria
MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/...")  # TODO

# Maps
OLD_MAPS_DIR_PATH = {"EncounterCSN": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_encounter.csv")],
                     "LinkageNoteID": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note_link.csv")],
                     "NoteKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note.csv")],
                     "OrderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_order.csv")],
                     "PatientKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_patient.csv")],
                     "ProviderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_provider.csv")]}

# Quality assurance
if __name__ == "__main__":
    ALL_VARS = [PROJECT_ROOT_DIRECTORY,
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
