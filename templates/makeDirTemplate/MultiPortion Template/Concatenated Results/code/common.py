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
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_BO, LIST_OF_PHI_VARIABLES_NOTES, LIST_OF_PHI_VARIABLES_OMOP, VARIABLE_SUFFIXES_BO, VARIABLE_SUFFIXES_NOTES, VARIABLE_SUFFIXES_OMOP
from drapi.drapi import successiveParents

# Argument meta variables
IRB_NUMBER = None  # TODO
DATA_REQUEST_ROOT_DIRECTORY_DEPTH = 3  # TODO  # NOTE To prevent unexpected results, like moving, writing, or deleting the wrong files, set this to folder that is the immediate parent of concatenated result and the intermediate results folder.

dataRequestRootDirectory, _ = successiveParents(Path(__file__).absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
NOTES_ROOT_DIRECTORY = dataRequestRootDirectory.joinpath("Intermediate Results",
                                                         "Notes Portion",
                                                         "data",
                                                         "output")
# Project arguments
COLUMNS_TO_DE_IDENTIFY = LIST_OF_PHI_VARIABLES_BO + LIST_OF_PHI_VARIABLES_NOTES + LIST_OF_PHI_VARIABLES_OMOP

# `VARIABLE_ALIASES` NOTE: Some variable names are not standardized. This argument is used by the de-identification process when looking for the de-identification map. This way several variables can be de-identified with the same map.
# TODO Add or remove from this dictionary as necessary.
# VAR_ALIASES_BO_ENCOUNTERS = {"Encounter # (CSN)": "Encounter #",         # True only for EPIC accounts, post-Siemens
#                              "Encounter # (Primary CSN)": "Encounter #"}  # True only for EPIC accounts, post-Siemens
VAR_ALIASES_NOTES_ENCOUNTERS = {"EncounterCSN": "Encounter #",
                                "EncounterKey": "Patient Encounter Key"}
VAR_ALIASES_NOTES_PATIENTS = {"MRN_GNV": "MRN (UF)",
                              "PatientKey": "Patient Key"}
VAR_ALIASES_NOTES_PROVIDERS = {"AuthoringProviderKey": "ProviderKey",
                               "AuthorizingProviderKey": "ProviderKey",
                               "CosignProviderKey": "ProviderKey",
                               "OrderingProviderKey": "ProviderKey"}
LIST_OF_ALIAS_DICTS = [VAR_ALIASES_NOTES_ENCOUNTERS,
                       VAR_ALIASES_NOTES_PATIENTS,
                       VAR_ALIASES_NOTES_PROVIDERS]
VARIABLE_ALIASES = {}
for di in LIST_OF_ALIAS_DICTS:
    VARIABLE_ALIASES.update(di)

VARIABLE_SUFFIXES_LIST = [VARIABLE_SUFFIXES_BO, VARIABLE_SUFFIXES_NOTES, VARIABLE_SUFFIXES_OMOP]
VARIABLE_SUFFIXES = dict()
for variableSuffixDict in VARIABLE_SUFFIXES_LIST:
    VARIABLE_SUFFIXES.update(variableSuffixDict)

# Portion directories
BO_PORTION_DIR_MAC = dataRequestRootDirectory.joinpath("Intermediate Results/BO Portion/data/output/getData/...")  # TODO
BO_PORTION_DIR_WIN = dataRequestRootDirectory.joinpath(r"Intermediate Results\BO Portion\data\output\getData\...")  # TODO

NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath(r"free_text")

OMOP_PORTION_DIR_MAC = dataRequestRootDirectory.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = dataRequestRootDirectory.joinpath(r"Intermediate Results\OMOP Portion\data\output\...")  # TODO

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path(r"data\output\convertColumns\...")  # TODO

ZIP_CODE_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
ZIP_CODE_PORTION_DIR_WIN = Path(r"data\output\convertColumns\...")  # TODO

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
    ALL_VARS = [dataRequestRootDirectory,
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
