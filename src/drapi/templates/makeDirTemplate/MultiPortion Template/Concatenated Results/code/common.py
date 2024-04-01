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

import re
from pathlib import Path
# Local packages
from drapi.code.drapi.constants.constants import DATA_TYPES_DICT
from drapi.code.drapi.constants.phiVariables import (LIST_OF_PHI_VARIABLES_BO,
                                          LIST_OF_PHI_VARIABLES_I2B2,
                                          LIST_OF_PHI_VARIABLES_NOTES,
                                          LIST_OF_PHI_VARIABLES_OMOP,
                                          VARIABLE_NAME_TO_FILE_NAME_DICT,
                                          VARIABLE_SUFFIXES_BO,
                                          VARIABLE_SUFFIXES_I2B2,
                                          VARIABLE_SUFFIXES_NOTES,
                                          VARIABLE_SUFFIXES_OMOP)
from drapi.code.drapi.drapi import flatExtend

# Project parameters: Meta-variables
STUDY_TYPE = "Limited Data Set (LDS)"  # Pick from "Non-Human", "Limited Data Set (LDS)", "Identified"
IRB_NUMBER = "IRB202300703"  # TODO
DATA_REQUEST_ROOT_DIRECTORY_DEPTH = 3  # TODO  # NOTE To prevent unexpected results, like moving, writing, or deleting the wrong files, set this to folder that is the immediate parent of concatenated result and the intermediate results folder.


# Project parameters: Aliases: Definitions  # TODO
# NOTE: Some variable names are not standardized. This section is used by the de-identification process when looking for the de-identification map. This way several variables can be de-identified with the same map. If you have variables with a custom, non-BO name, you should alias them, if necessary using the following format:
# VAR_ALIASES_CUSTOM_VARS = {"Custom Variable 1": "BO Equivalent 1",
#                            "Custom Variable 2": "BO Equivalent 2"}
VAR_ALIASES_NOTES_ENCOUNTERS = {"EncounterCSN": "Encounter # (CSN)",
                                "EncounterKey": "Encounter Key"}
VAR_ALIASES_NOTES_NOTES = {"NoteID": "Note ID",
                           "NoteKey": "Note Key",
                           "LinkageNoteID": "Linkage Note ID"}
VAR_ALIASES_NOTES_PATIENTS = {"MRN_GNV": "MRN (UF)",
                              "MRN_JAX": "MRN (Jax)",
                              "PatientKey": "Patient Key"}
VAR_ALIASES_NOTES_PROVIDERS = {"AuthoringProviderKey": "Provider Key",
                               "AuthorizingProviderKey": "Provider Key",
                               "CosignProviderKey": "Provider Key",
                               "OrderingProviderKey": "Provider Key",
                               "ProviderKey": "Provider Key"}
VAR_ALIASES_SDOH_ENCOUNTERS = {"NOTE_ENCNTR_KEY": "Linkage Note ID",
                               "NOTE_KEY": "Note Key"}
LIST_OF_ALIAS_DICTS = [VAR_ALIASES_NOTES_ENCOUNTERS,
                       VAR_ALIASES_NOTES_NOTES,
                       VAR_ALIASES_NOTES_PATIENTS,
                       VAR_ALIASES_NOTES_PROVIDERS,
                       VAR_ALIASES_SDOH_ENCOUNTERS]
VARIABLE_ALIASES = {}
for di in LIST_OF_ALIAS_DICTS:
    VARIABLE_ALIASES.update(di)

# Project parameters: Aliases: Data types  # TODO
# NOTE Add each variable in `VARIABLE_ALIASES` to `ALIAS_DATA_TYPES`.
ALIAS_DATA_TYPES_MANUAL = {}  # TODO
ALIAS_DATA_TYPES_AUTOMATIC = {}
for alias, variableName in VARIABLE_ALIASES.items():
    if alias not in DATA_TYPES_DICT.keys():
        ALIAS_DATA_TYPES_AUTOMATIC[alias] = DATA_TYPES_DICT[variableName]
    else:
        pass
ALIAS_DATA_TYPES = ALIAS_DATA_TYPES_MANUAL.copy()
ALIAS_DATA_TYPES.update(ALIAS_DATA_TYPES_AUTOMATIC)
DATA_TYPES_DICT.update(ALIAS_DATA_TYPES)

# Project parameters: Aliases: Alias-to-File-name conversion  # TODO
VARIABLES_TO_OVER_WRITE_MANUALLY = {}  # TODO
VARIABLES_TO_ADD_FROM_ALIASES = {variableName: variableName for variableName in VARIABLE_ALIASES.keys()}
VARIABLES_TO_OVER_WRITE_LIST = [VARIABLES_TO_ADD_FROM_ALIASES,
                                VARIABLES_TO_OVER_WRITE_MANUALLY]  # NOTE The manual list must go last, to over-write the automatic additions.
VARIABLES_TO_ADD_DICT = {}
for di in VARIABLES_TO_OVER_WRITE_LIST:
    VARIABLES_TO_ADD_DICT.update(di)
VARIABLE_NAME_TO_FILE_NAME_DICT.update(VARIABLES_TO_ADD_DICT)
FILE_NAME_TO_VARIABLE_NAME_DICT = {fileName: varName for varName, fileName in VARIABLE_NAME_TO_FILE_NAME_DICT.items()}

# QA: Make sure all aliases have data types.
li = []
for alias in VARIABLE_ALIASES.keys():
    if alias in DATA_TYPES_DICT.keys():
        pass
    else:
        li.append(alias)
if len(li) > 0:
    string = "\n".join(sorted(li))
    msg = f"""The following variable aliases have no data type assigned:\n{string}"""
    raise Exception(msg)

# Add aliases to list of variables to de-identify by adding the keys from `VARIABLE_ALIASES` and `ALIAS_DATA_TYPES` to `COLUMNS_TO_DE_IDENTIFY`.
LIST_OF_PHI_VARIABLES_FROM_ALIASES = [variableName for variableName in VARIABLE_ALIASES.keys()] + [variableName for variableName in ALIAS_DATA_TYPES.keys()]
LIST_OF_PHI_VARIABLES_FROM_ALIASES = list(set(LIST_OF_PHI_VARIABLES_FROM_ALIASES))

# Project parameters: Columns to de-identify
if STUDY_TYPE.lower() == "Non-Human":
    LIST_OF_PHI_VARIABLES_TO_KEEP = []
else:
    LIST_OF_PHI_VARIABLES_TO_KEEP = []
COLUMNS_TO_DE_IDENTIFY = flatExtend([LIST_OF_PHI_VARIABLES_BO,
                                     LIST_OF_PHI_VARIABLES_I2B2,
                                     LIST_OF_PHI_VARIABLES_NOTES,
                                     LIST_OF_PHI_VARIABLES_OMOP,
                                     LIST_OF_PHI_VARIABLES_FROM_ALIASES])
COLUMNS_TO_DE_IDENTIFY = [variableName for variableName in COLUMNS_TO_DE_IDENTIFY if variableName not in LIST_OF_PHI_VARIABLES_TO_KEEP]

# Project parameters: Variable suffixes
VARIABLE_SUFFIXES_LIST = [VARIABLE_SUFFIXES_BO,
                          VARIABLE_SUFFIXES_I2B2,
                          VARIABLE_SUFFIXES_NOTES,
                          VARIABLE_SUFFIXES_OMOP]
VARIABLE_SUFFIXES = dict()
for variableSuffixDict in VARIABLE_SUFFIXES_LIST:
    VARIABLE_SUFFIXES.update(variableSuffixDict)

# Project parameters: Portion directories
MODIFIED_OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/...")  # TODO
MODIFIED_OMOP_PORTION_DIR_WIN = Path(r"data\output\convertColumns\...")  # TODO

NOTES_ROOT_DIRECTORY = Path(r"..\Notes\original_note_pull\data\Output")  # TODO
NOTES_PORTION_DIR_MAC = NOTES_ROOT_DIRECTORY.joinpath("free_text")
NOTES_PORTION_DIR_WIN = NOTES_ROOT_DIRECTORY.joinpath("free_text")

OMOP_PORTION_DIR_MAC = Path(r"..\OMOP_Structured_Data\data\output\identified")  # TODO
OMOP_PORTION_DIR_WIN = Path(r"..\OMOP_Structured_Data\data\output\identified")  # TODO

OMOP_PORTION_2_DIR_MAC = Path(r"..\Intermediate Results\OMOP Portion\data\output\identified\2024-01-23 13-54-26")  # TODO
OMOP_PORTION_2_DIR_WIN = Path(r"..\Intermediate Results\OMOP Portion\data\output\identified\2024-01-23 13-54-26")  # TODO

# Project parameters: File criteria
NOTES_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv",
                               lambda pathObj: True if re.search(pattern=r"metadata_\d+.csv",
                                                         string=pathObj.name) else False]
OMOP_PORTION_FILE_CRITERIA = [lambda pathObj: pathObj.suffix.lower() == ".csv"]


# Project parameters: Maps
OLD_MAPS_DIR_PATH = {"EncounterCSN": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_encounter.csv")],
                     "LinkageNoteID": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note_link.csv")],
                     "NoteKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_note.csv")],
                     "OrderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_order.csv")],
                     "PatientKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_patient.csv")],
                     "ProviderKey": [NOTES_ROOT_DIRECTORY.joinpath("mapping/map_provider.csv")]}

# Quality assurance
if __name__ == "__main__":
    ALL_VARS = [MODIFIED_OMOP_PORTION_DIR_MAC,
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
