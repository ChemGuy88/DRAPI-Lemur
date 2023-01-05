"""
Useful definitions used throughout IDR

See the Notes portion for current IDR mapping standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Intermediate Results/Notes Portion/Data/Output/mapping
See Noah's data request for my attempt at using these standards: /Volumes/FILES/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Bian/IRB202202436/Concatenated Results/Code/makeMap.py
"""

__all__ = ["DeIdIDName2DeIdIDSuffix",
           "IDName2DeIdIDName",
           "mapDtypes"]

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
