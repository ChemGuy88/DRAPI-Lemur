"""
Useful definitions used throughout IDR

See the Notes portion for current IDR mapping standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Intermediate Results/Notes Portion/Data/Output/mapping
See Noah's data request for my attempt at using these standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Concatenated Results/Code/makeMap.py
"""

__all__ = ["DeIdIDName2DeIdIDSuffix",
           "IDName2DeIdIDName",
           "mapDtypes",
           "DATA_TYPES"]

IDName2DeIdIDNameRoot = {"ENCNTR_CSN_ID": "enc",
                         "IDENT_ID_INT": "pat",
                         "ORDR_PROC_ID": "order",
                         "PATNT_KEY": "pat"}
IDName2DeIdIDName = {IDName: f"deid_{DeIdIDNameRoot}_id" for IDName, DeIdIDNameRoot in IDName2DeIdIDNameRoot.items()}
DeIdIDName2DeIdIDSuffix = {"pat": "PAT",
                           "enc": "ENC",
                           "note": "NOTE",
                           "link_note": "LINK_NOTE",
                           "order": "ORDER",
                           "provider": "PROV"}
mapDtypes = {0: int,
             1: int,
             2: str}

DATA_TYPES_BO = {"Accct Number - Enter DateTime Comb": "String",
                 "Acct Number - Exit DateTime Comb": "String",
                 "At Station": "String",
                 "Authoring Provider Key": "Numeric",
                 "Authorizing Provider Key": "Numeric",
                 "Cosign Provider Key": "Numeric",
                 "EPIC Patient ID": "String",
                 "Encounter #": "Numeric",
                 "Encounter # (CSN)": "Numeric",
                 "Encounter # (Primary CSN)": "Numeric",
                 "Encounter Key": "Numeric",
                 "Encounter Key (Primary CSN)": "Numeric",
                 "EncounterCSN": "Numeric",
                 "Enterprise ID": "String",
                 "From Station": "String",
                 "Linkage Note ID": "Numeric",
                 "Location of Svc": "String",
                 "Location of Svc ID": "Numeric_Or_String",
                 "MRN (Jax)": "Numeric",
                 "MRN (UF)": "Numeric",
                 "Note ID": "Numeric",
                 "Note Key": "Numeric",
                 "Order ID": "Numeric",
                 "Ordering Provider Key": "Numeric",
                 "Order Key": "Numeric",
                 "Provider Key": "Numeric",
                 "Patient Encounter Key": "Numeric",
                 "Patient Key": "Numeric",
                 "PatientKey": "Numeric",
                 "Patnt Key": "Numeric",
                 "To Station": "String"}

# Note that notes data are from the same source as BO data. These variable names are actually aliases and are here for convenience.
DATA_TYPES_I2B2 = {"LOCATION_CD": "Numeric"}
DATA_TYPES_NOTES = {"AuthoringProviderKey": "Numeric",
                    "AuthorizingProviderKey": "Numeric",
                    "ContactDate": "Datetime",
                    "CosignProviderKey": "Numeric",
                    "CreatedDatetime": "Datetime",
                    "EncounterCSN": "Numeric",
                    "EncounterDate": "Datetime",
                    "EncounterKey": "Numeric",
                    "LinkageNoteID": "Numeric",
                    "MRN_GNV": "Numeric",
                    "MRN_JAX": "Numeric",
                    "NoteID": "Numeric",
                    "NoteKey": "Numeric",
                    "OrderID": "Numeric",
                    "OrderKey": "Numeric",
                    "OrderPlacedDatetime": "Datetime",
                    "OrderResultDatetime": "Datetime",
                    "OrderingProviderKey": "Numeric",
                    "PatientKey": "Numeric",
                    "ProviderKey": "Numeric",
                    "ServiceDatetime": "Datetime"}

DATA_TYPES_OMOP = {"location_id": "Numeric",
                   "preceding_visit_occurrence_id": "Numeric",
                   "provider_id": "Numeric",
                   "visit_occurrence_id": "Numeric"}

DATA_TYPES_DICT = DATA_TYPES_BO.copy()
DATA_TYPES_DICT.update(DATA_TYPES_I2B2)
DATA_TYPES_DICT.update(DATA_TYPES_NOTES)
DATA_TYPES_DICT.update(DATA_TYPES_OMOP)

DATA_TYPES_BY_PORTION = {"BO": DATA_TYPES_BO,
                         "Notes": DATA_TYPES_NOTES,
                         "OMOP": DATA_TYPES_OMOP}

