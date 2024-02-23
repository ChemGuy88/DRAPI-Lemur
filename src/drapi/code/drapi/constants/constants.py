"""
Useful definitions used throughout IDR

See the Notes portion for current IDR mapping standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Intermediate Results/Notes Portion/Data/Output/mapping
See Noah's data request for my attempt at using these standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Concatenated Results/Code/makeMap.py
"""
from drapi.code.drapi.constants.phiVariables import LIST_OF_PHI_VARIABLES

__all__ = ["DeIdIDName2DeIdIDSuffix",
           "IDName2DeIdIDName",
           "mapDtypes",
           "DATA_TYPES_DICT"]

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

# Define data types. NOTE that all the `String` variables contain numbers with leading zeros that get converted to integers in the current process. Either we convert these variables to `string` or we change the process.
DATA_TYPES_BO = {"Acct Number - Enter DateTime Comb": "String",
                 "Acct Number - Exit DateTime Comb": "String",
                 "At Station": "String",
                 "Authoring Provider Key": "Numeric",
                 "Authorizing Provider Key": "Numeric",
                 "Chemotherapy Rx Hosp Code Desc": "String",
                 "Cosign Provider Key": "Numeric",
                 "Diagnosis County": "String",
                 "EPIC Patient ID": "String",
                 "Encounter #": "Numeric",
                 "Encounter # (CSN)": "Numeric",
                 "Encounter # (Primary CSN)": "Numeric",
                 "Encounter Key": "Numeric",
                 "Encounter Key (Primary CSN)": "Numeric",
                 "EncounterCSN": "Numeric",
                 "Enterprise ID": "String",
                 "From Station": "String",
                 "F/u Physicians": "String",
                 "Linkage Note ID": "Numeric",
                 "Location of Svc": "String",
                 "Location of Svc ID": "String",
                 "Managing Physician": "String",
                 "Medical Record Number": "Numeric",
                 "MRN (Jax)": "Numeric",
                 "MRN (UF)": "Numeric",
                 "Note ID": "Numeric",
                 "Note Key": "Numeric",
                 "NRAS": "String",
                 "Order ID": "Numeric",
                 "Ordering Provider Key": "Numeric",
                 "Order Key": "Numeric",
                 "Provider Key": "Numeric",
                 "Patient Encounter Key": "Numeric",
                 "Patient Key": "Numeric",
                 "PatientKey": "Numeric",
                 "Patnt Key": "Numeric",
                 "Prim  surgeon Code": "String",
                 "Radiation Hosp Code Desc": "String",
                 "Source Sys": "String",
                 "Surgery Rx Hosp Code Desc": "String",
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

DATA_TYPES_OMOP = {"care_site_id": "Numeric",
                   "csn": "Numeric",
                   "city": "String",
                   "county": "String",
                   "location_id": "Numeric",
                   "observation_period_id": "Numeric",
                   "patient_key": "Numeric",
                   "person_id": "Numeric",
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

# Convert DRAPI data types to SQL data types
DRAPI_TO_SQL_DATA_TYPES_MAP = {"Datetime": "TEXT",
                               "Numeric": "INTEGER",
                               "String": "TEXT"}
DATA_TYPES_DICT_SQL = {name: DRAPI_TO_SQL_DATA_TYPES_MAP[drapiDataType] for name, drapiDataType in DATA_TYPES_DICT.items()}

# QA: Make sure all PHI variables have their data type defined
# assert all([varName in DATA_TYPES_DICT.keys() for varName in LIST_OF_PHI_VARIABLES])
listOfMissingVariables = []
for varName in LIST_OF_PHI_VARIABLES:
    if varName not in DATA_TYPES_DICT.keys():
        listOfMissingVariables.append(varName)
if len(listOfMissingVariables) > 0:
    text = "\n".join([f'"{varName}"' for varName in listOfMissingVariables])
    raise Exception(f"Not all PHI variables have their data type defined: {text}")
