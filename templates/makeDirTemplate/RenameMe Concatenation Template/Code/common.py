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
PROJECT_ROOT_DIRECTORY = Path("").absolute().parent

# Project arguments
COLUMNS_TO_DE_IDENTIFY = ["AuthoringProviderKey",
                          "AuthorizingProviderKey",
                          "CosignProviderKey",
                          "EncounterCSN",
                          "EncounterKey",
                          "MRN_GNV",
                          "MRN_JAX",
                          "NoteID",  # ?
                          "NoteKey",  # ?
                          "OrderID",  # ?
                          "OrderKey",  # ?
                          "PatientKey",
                          "ProviderKey",
                          "location_id",
                          "preceding_visit_occurrence_id",
                          "provider_id",
                          "visit_occurrence_id"]

NOTES_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../free_text")  # TODO
NOTES_PORTION_DIR_WIN = Path(r"Z:\IDR Data Requests\ACTIVE RDRs\...\...\Intermediate Results\Notes Portion\data\output\free_text")  # TODO

OMOP_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = Path(r"Z:\IDR Data Requests\ACTIVE RDRs\...\...\Intermediate Results\OMOP Portion\data\output\...")  # TODO

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/...")  # TODO

OLD_MAPS_DIR_PATH = {"EncounterCSN": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_encounter.csv")],  # TODO
                     "LinkageNoteID": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_note_link.csv")],  # TODO
                     "NoteKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_note.csv")],  # TODO
                     "OrderKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_order.csv")],  # TODO
                     "PatientKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_patient.csv")],  # TODO
                     "ProviderKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/.../mapping/map_provider.csv")]}  # TODO
