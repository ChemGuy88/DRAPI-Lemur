"""
Aliases for variables.
"""

VAR_ALIASES_CLINICAL_TEXT_ENCOUNTERS = {"EncounterCSN": "Encounter # (CSN)",
                                        "EncounterKey": "Encounter Key"}
VAR_ALIASES_CLINICAL_TEXT_NOTES = {"NoteID": "Note ID",
                                   "NoteKey": "Note Key",
                                   "LinkageNoteID": "Linkage Note ID"}
VAR_ALIASES_CLINICAL_TEXT_ORDERS = {"OrderID": "Order ID",
                                    "OrderKey": "Order Key"}
VAR_ALIASES_CLINICAL_TEXT_PATIENTS = {"MRN_GNV": "MRN (UF)",
                                      "MRN_JAX": "MRN (Jax)",
                                      "PatientKey": "Patient Key"}
VAR_ALIASES_CLINICAL_TEXT_PROVIDERS = {"AuthoringProviderKey": "Provider Key",
                                       "AuthorizingProviderKey": "Provider Key",
                                       "CosignProviderKey": "Provider Key",
                                       "OrderingProviderKey": "Provider Key",
                                       "ProviderKey": "Provider Key"}
VAR_ALIASES_SDOH_ENCOUNTERS = {"NOTE_ENCNTR_KEY": "Linkage Note ID",
                               "NOTE_KEY": "Note Key"}
LIST_OF_ALIAS_DICTS = [VAR_ALIASES_CLINICAL_TEXT_ENCOUNTERS,
                       VAR_ALIASES_CLINICAL_TEXT_NOTES,
                       VAR_ALIASES_CLINICAL_TEXT_ORDERS,
                       VAR_ALIASES_CLINICAL_TEXT_PATIENTS,
                       VAR_ALIASES_CLINICAL_TEXT_PROVIDERS,
                       VAR_ALIASES_SDOH_ENCOUNTERS]
VARIABLE_ALIASES = {}
for di in LIST_OF_ALIAS_DICTS:
    VARIABLE_ALIASES.update(di)

