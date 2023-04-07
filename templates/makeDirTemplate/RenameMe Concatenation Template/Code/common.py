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

NOTES_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/free_text")
NOTES_PORTION_DIR_WIN = Path(r"Z:\IDR Data Requests\ACTIVE RDRs\Bian\IRB202300242\Intermediate Results\Notes Portion\data\output\free_text")

OMOP_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/OMOP Portion/data/output/2023-03-20 12-29-02")
OMOP_PORTION_DIR_WIN = Path(r"Z:\IDR Data Requests\ACTIVE RDRs\Bian\IRB202300242\Intermediate Results\OMOP Portion\data\output\2023-03-20 12-29-02")

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/2023-03-24 17-20-15")
MODIFIED_OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/2023-03-24 17-20-15")

OLD_MAPS_DIR_PATH = {"EncounterCSN": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_encounter.csv")],
                     "LinkageNoteID": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_note_link.csv")],
                     "NoteKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_note.csv")],
                     "OrderKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_order.csv")],
                     "PatientKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_patient.csv")],
                     "ProviderKey": [PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/Notes Portion/data/output/2023-03-28/mapping/map_provider.csv")]}
