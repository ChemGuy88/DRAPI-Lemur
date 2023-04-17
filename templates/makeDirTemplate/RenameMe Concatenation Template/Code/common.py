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
PROJECT_ROOT_DIRECTORY = Path(__file__).absolute().parent.parent  # TODO
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

NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath(r"free_text")

OMOP_PORTION_DIR_MAC = PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = PROJECT_ROOT_DIRECTORY.joinpath(r"Intermediate Results\OMOP Portion\data\output\...")  # TODO

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/...")  # TODO

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
