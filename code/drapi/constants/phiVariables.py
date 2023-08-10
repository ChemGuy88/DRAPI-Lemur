"""
Useful definitions used throughout the IDR.
"""

__all__ = ["LIST_OF_PHI_VARIABLES_BO",
           "LIST_OF_PHI_VARIABLES_NOTES",
           "LIST_OF_PHI_VARIABLES_OMOP"]

LIST_OF_PHI_VARIABLES_NOTES = ["AuthoringProviderKey",
                               "AuthorizingProviderKey",
                               "CosignProviderKey",
                               "EncounterCSN",
                               "EncounterKey",
                               "LinkageNoteID",
                               "MRN_GNV",
                               "MRN_JAX",
                               "NoteID",
                               "NoteKey",
                               "OrderID",
                               "OrderKey",
                               "OrderingProviderKey",
                               "PatientKey",
                               "Patient Key",
                               "ProviderKey"]

LIST_OF_PHI_VARIABLES_BO = ['Accct Number - Enter DateTime Comb',
                            'Acct Number - Exit DateTime Comb',
                            'At Station',
                            'EPIC Patient ID',
                            'Encounter #',
                            'Encounter # (CSN)',
                            'Encounter # (Primary CSN)',
                            'Encounter Key (Primary CSN)',
                            'Enterprise ID',
                            'From Station',
                            'Location of Svc',
                            'Location of Svc ID',
                            'MRN (Jax)',
                            'MRN (UF)',
                            'Patient Encounter Key',
                            'Patient Key',
                            'Patnt Key',
                            'To Station']

LIST_OF_PHI_VARIABLES_OMOP = ['csn',
                              'location_id',
                              'patient_key',
                              'preceding_visit_occurrence_id',
                              'provider_id',
                              'visit_occurrence_id']

VARIABLE_SUFFIXES_BO = {"Accct Number - Enter DateTime Comb": {"columnSuffix": "account",
                                                               "deIdIDSuffix": "ACCT"},
                        "Acct Number - Exit DateTime Comb": {"columnSuffix": "account",
                                                             "deIdIDSuffix": "ACCT"},
                        "At Station": {"columnSuffix": "station",
                                       "deIdIDSuffix": "STN"},
                        "EPIC Patient ID": {"columnSuffix": "patient",
                                            "deIdIDSuffix": "PAT"},
                        "Encounter #": {"columnSuffix": "encounter",
                                        "deIdIDSuffix": "ENC"},
                        "Encounter # (CSN)": {"columnSuffix": "encounter",
                                              "deIdIDSuffix": "ENC"},
                        "Encounter # (Primary CSN)": {"columnSuffix": "encounter",
                                                      "deIdIDSuffix": "ENC"},
                        "Encounter Key (Primary CSN)": {"columnSuffix": "encounter",
                                                        "deIdIDSuffix": "ENC"},
                        "Enterprise ID": {"columnSuffix": "patient",
                                          "deIdIDSuffix": "PAT"},
                        "From Station": {"columnSuffix": "station",
                                         "deIdIDSuffix": "STN"},
                        "Location of Svc": {"columnSuffix": "location",
                                            "deIdIDSuffix": "LOC"},
                        "Location of Svc ID": {"columnSuffix": "location",
                                               "deIdIDSuffix": "LOC"},
                        "MRN (Jax)": {"columnSuffix": "patient",
                                      "deIdIDSuffix": "PAT"},
                        "MRN (UF)": {"columnSuffix": "patient",
                                     "deIdIDSuffix": "PAT"},
                        "Patient Encounter Key": {"columnSuffix": "encounter",
                                                  "deIdIDSuffix": "ENC"},
                        "Patient Key": {"columnSuffix": "patient",
                                        "deIdIDSuffix": "PAT"},
                        "Patnt Key": {"columnSuffix": "patient",
                                      "deIdIDSuffix": "PAT"},
                        "To Station": {"columnSuffix": "station",
                                       "deIdIDSuffix": "STN"}}

VARIABLE_SUFFIXES_NOTES = {"AuthoringProviderKey": {"columnSuffix": "provider",
                                                    "deIdIDSuffix": "PROV"},
                           "AuthorizingProviderKey": {"columnSuffix": "provider",
                                                      "deIdIDSuffix": "PROV"},
                           "CosignProviderKey": {"columnSuffix": "provider",
                                                 "deIdIDSuffix": "PROV"},
                           "EncounterCSN": {"columnSuffix": "encounter",
                                            "deIdIDSuffix": "ENC"},
                           "EncounterKey": {"columnSuffix": "encounter",
                                            "deIdIDSuffix": "ENC"},
                           "LinkageNoteID": {"columnSuffix": "link_note",
                                             "deIdIDSuffix": "LINK_NOTE"},
                           "MRN_GNV": {"columnSuffix": "patient",
                                       "deIdIDSuffix": "PAT"},
                           "MRN_JAX": {"columnSuffix": "patient",
                                       "deIdIDSuffix": "PAT"},
                           "NoteID": {"columnSuffix": "note",
                                      "deIdIDSuffix": "NOTE"},
                           "NoteKey": {"columnSuffix": "note",
                                       "deIdIDSuffix": "NOTE"},
                           "OrderID": {"columnSuffix": "order",
                                       "deIdIDSuffix": "ORD"},
                           "OrderKey": {"columnSuffix": "order",
                                        "deIdIDSuffix": "ORD"},
                           "OrderingProviderKey": {"columnSuffix": "order",
                                                   "deIdIDSuffix": "ORD"},
                           "PatientKey": {"columnSuffix": "patient",
                                          "deIdIDSuffix": "PAT"},
                           "ProviderKey": {"columnSuffix": "provider",
                                           "deIdIDSuffix": "PROV"}}

VARIABLE_SUFFIXES_OMOP = {"csn": {"columnSuffix": "encounter",
                                  "deIdIDSuffix": "ENC"},
                          "location_id": {"columnSuffix": "location",
                                          "deIdIDSuffix": "LOC"},
                          "patient_key": {"columnSuffix": "patient",
                                          "deIdIDSuffix": "PAT"},
                          "person_id": {"columnSuffix": "patient",
                                        "deIdIDSuffix": "PAT"},
                          "preceding_visit_occurrence_id": {"columnSuffix": "encounter",
                                                            "deIdIDSuffix": "ENC"},
                          "provider_id": {"columnSuffix": "provider",
                                          "deIdIDSuffix": "PROV"},
                          "visit_occurrence_id": {"columnSuffix": "encounter",
                                                  "deIdIDSuffix": "ENC"}}

# QA
for key in VARIABLE_SUFFIXES_BO.keys():
    checkBO = key not in list(VARIABLE_SUFFIXES_NOTES.keys()) + list(VARIABLE_SUFFIXES_OMOP.keys())
for key in VARIABLE_SUFFIXES_NOTES.keys():
    checkNotes = key not in list(VARIABLE_SUFFIXES_BO.keys()) + list(VARIABLE_SUFFIXES_OMOP.keys())
for key in VARIABLE_SUFFIXES_OMOP.keys():
    checkOMOP = key not in list(VARIABLE_SUFFIXES_BO.keys()) + list(VARIABLE_SUFFIXES_NOTES.keys())

assert all([checkBO, checkNotes, checkOMOP]), "Some variables are present in more than one variable suffix dictionary. This may lead to unintended consequences."