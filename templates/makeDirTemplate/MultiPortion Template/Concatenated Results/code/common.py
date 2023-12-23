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
from drapi.constants.constants import DATA_TYPES_DICT
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_BO
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_I2B2
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_NOTES
from drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES_OMOP
from drapi.constants.phiVariables import VARIABLE_SUFFIXES_BO
from drapi.constants.phiVariables import VARIABLE_SUFFIXES_I2B2
from drapi.constants.phiVariables import VARIABLE_SUFFIXES_NOTES
from drapi.constants.phiVariables import VARIABLE_SUFFIXES_OMOP
from drapi.drapi import successiveParents

# Argument meta variables
STUDY_TYPE = "Limited Data Set (LDS)"  # Pick from "Non-Human", "Limited Data Set (LDS)", "Identified"
IRB_NUMBER = None  # TODO
DATA_REQUEST_ROOT_DIRECTORY_DEPTH = 3  # TODO  # NOTE To prevent unexpected results, like moving, writing, or deleting the wrong files, set this to folder that is the immediate parent of concatenated result and the intermediate results folder.

dataRequestRootDirectory, _ = successiveParents(Path(__file__).absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
NOTES_ROOT_DIRECTORY = dataRequestRootDirectory.joinpath("Intermediate Results",
                                                         "Notes Portion",
                                                         "data",
                                                         "output",
                                                         "freeText",
                                                         "...")

# Project arguments
# TODO: Update or remove `ALIAS_DATA_TYPES` as necessary.
ALIAS_DATA_TYPES = {}
DATA_TYPES_DICT.update(ALIAS_DATA_TYPES)
# Add the keys from `ALIAS_DATA_TYPES` to `COLUMNS_TO_DE_IDENTIFY`
LIST_OF_PHI_VARIABLES_FROM_ALIASES = [variableName for variableName in ALIAS_DATA_TYPES.keys()]
if STUDY_TYPE.lower() == "Non-Human":
    LIST_OF_PHI_VARIABLES_TO_KEEP = []
else:
    LIST_OF_PHI_VARIABLES_TO_KEEP = ["city",
                                    "county",
                                    "observation_period_id"]
COLUMNS_TO_DE_IDENTIFY = LIST_OF_PHI_VARIABLES_BO + \
                         LIST_OF_PHI_VARIABLES_I2B2 + \
                         LIST_OF_PHI_VARIABLES_NOTES + \
                         LIST_OF_PHI_VARIABLES_OMOP + \
                         LIST_OF_PHI_VARIABLES_FROM_ALIASES
COLUMNS_TO_DE_IDENTIFY = [variableName for variableName in COLUMNS_TO_DE_IDENTIFY if variableName not in LIST_OF_PHI_VARIABLES_TO_KEEP]

# `VARIABLE_ALIASES` NOTE: Some variable names are not standardized. This argument is used by the de-identification process when looking for the de-identification map. This way several variables can be de-identified with the same map.
# TODO Add or remove from these dictionaries as necessary.
# NOTE That if you have variables with a custom, non-BO name, you should alias them, if necessary using the following format:
# VAR_ALIASES_CUSTOM_VARS = {"Custom Variable 1": "BO Equivalent 1",
#                            "Custom Variable 2": "BO Equivalent 2"}
if False:
    VAR_ALIASES_BO_ENCOUNTERS = {"Encounter # (CSN)": "Encounter #",         # True only for EPIC accounts, post-Siemens
                                "Encounter # (Primary CSN)": "Encounter #"}  # True only for EPIC accounts, post-Siemens
VAR_ALIASES_NOTES_ENCOUNTERS = {"EncounterCSN": "Encounter # (CSN)"}
VAR_ALIASES_NOTES_PATIENTS = {"MRN_GNV": "MRN (UF)",
                              "MRN_JAX": "MRN (Jax)",
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

VARIABLE_SUFFIXES_LIST = [VARIABLE_SUFFIXES_BO,
                          VARIABLE_SUFFIXES_I2B2,
                          VARIABLE_SUFFIXES_NOTES,
                          VARIABLE_SUFFIXES_OMOP]
VARIABLE_SUFFIXES = dict()
for variableSuffixDict in VARIABLE_SUFFIXES_LIST:
    VARIABLE_SUFFIXES.update(variableSuffixDict)

# Portion directories
BO_PORTION_DIR_MAC = dataRequestRootDirectory.joinpath("Intermediate Results/BO Portion/data/output/getData/...")  # TODO
BO_PORTION_DIR_WIN = dataRequestRootDirectory.joinpath(r"Intermediate Results\BO Portion\data\output\getData\...")  # TODO
I2B2_PORTION_DIR_MAC = dataRequestRootDirectory.joinpath("Concatenated Results\data\output\i2b2ConvertIDs\...")  # TODO
I2B2_PORTION_DIR_WIN = dataRequestRootDirectory.joinpath(r"Concatenated Results\data\output\i2b2ConvertIDs\...")  # TODO

MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path(r"data\output\convertColumns\...")  # TODO

OMOP_PORTION_DIR_MAC = dataRequestRootDirectory.joinpath("Intermediate Results/OMOP Portion/data/output/...")  # TODO
OMOP_PORTION_DIR_WIN = dataRequestRootDirectory.joinpath(r"Intermediate Results\OMOP Portion\data\output\...")  # TODO

NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath(r"free_text")

# File criteria
BO_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
I2B2_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]


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
                BO_PORTION_DIR_MAC,
                BO_PORTION_DIR_WIN,
                I2B2_PORTION_DIR_MAC,
                I2B2_PORTION_DIR_WIN,
                MODIFIED_OMOP_PORTION_DIR_MAC,
                MODIFIED_OMOP_PORTION_DIR_WIN,
                NOTES_ROOT_DIRECTORY,
                NOTES_PORTION_DIR_MAC,
                NOTES_PORTION_DIR_WIN,
                OMOP_PORTION_DIR_MAC,
                OMOP_PORTION_DIR_WIN]

    for li in OLD_MAPS_DIR_PATH.values():
        ALL_VARS.extend(li)

    for path in ALL_VARS:
        print(path.exists())
