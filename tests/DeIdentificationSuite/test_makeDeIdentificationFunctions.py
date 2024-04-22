"""
This test module checks to see if we can dynamically define de-identification functions.
"""

import json
# Third-party imports
import pandas as pd
# Local imports
from drapi.code.drapi.constants.phiVariables import (VARIABLE_SUFFIXES_BO,
                                                     VARIABLE_SUFFIXES_I2B2,
                                                     VARIABLE_SUFFIXES_CLINICAL_TEXT,
                                                     VARIABLE_SUFFIXES_OMOP)
from drapi.code.drapi.deIdentificationFunctions import functionFromSettings

IRB_NUMBER = "PROTOCOL123456789"

DE_IDENTIFICATION_TEST_VALUES = [-1,
                                 0,
                                 1,
                                 pd.NA]


LIST_OF_VARIABLE_SUFFIX_PORTIONS = [VARIABLE_SUFFIXES_BO,
                                    VARIABLE_SUFFIXES_CLINICAL_TEXT,
                                    VARIABLE_SUFFIXES_I2B2,
                                    VARIABLE_SUFFIXES_OMOP]
VARIABLE_SUFFIXES = {}
for di in LIST_OF_VARIABLE_SUFFIX_PORTIONS:
    VARIABLE_SUFFIXES.update(di)


string = """{"Encounter # (CSN)": [1, "random"],
             "Encounter Key": [1, "random"],
             "Linkage Note ID": [1, "random"],
             "MRN (Jax)": [1, "random"],
             "MRN (UF)": [1, "random"],
             "Note ID": [1, "random"],
             "Note Key": [1, "random"],
             "Order ID": [1, "random"],
             "Order Key": [1, "random"],
             "Patient Key": [1, "random"],
             "Provider Key": [1, "random"],
             "person_id": [1, "random"],
             "provider_id": [1, "random"],
             "visit_occurrence_id": [1, "random"]}"""
dictionaryOfMappingArguments = json.loads(string)
dictionaryOfMappingArguments = dict(dictionaryOfMappingArguments)  # For type hinting

mappingArguments = [{variableName: tu} for variableName, tu in dictionaryOfMappingArguments.items()]
DE_IDENTIFICATION_FUNCTIONS = {}
mappingSettings = {}
for di in mappingArguments:
    variableName = list(di.keys())[0]
    encryptionType, encryptionSecret0 = list(di.values())[0]
    encryptionSecret, variableFunction = functionFromSettings(ENCRYPTION_TYPE=encryptionType,
                                                              ENCRYPTION_SECRET=encryptionSecret0,
                                                              suffix=VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"],
                                                              IRB_NUMBER=IRB_NUMBER)
    DE_IDENTIFICATION_FUNCTIONS[variableName] = variableFunction
    mappingSettings[variableName] = {"Encryption Type": encryptionType,
                                     "Encryption Secret (Input)": encryptionSecret0,
                                     "Encryption Secret (Final)": encryptionSecret}
    print(f"""`variableName`: "{variableName}".""")
    print(f"""  `deIdIDSuffix`: {VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"]}.""")
    print(f"""  `encryptionSecret`: "{encryptionSecret}".""")
    print(f"""  `variableFunction`: "{variableFunction}".""")
    for value in DE_IDENTIFICATION_TEST_VALUES:
        print(f"""  `variableFunction({value})`: "{variableFunction(value)}".""")
    print()

print()
for variableName, variableFunction in DE_IDENTIFICATION_FUNCTIONS.items():
    encryptionSecret = mappingSettings[variableName]["Encryption Secret (Final)"]
    print(f"""`variableName`: "{variableName}".""")
    print(f"""  `encryptionSecret`: "{encryptionSecret}".""")
    print(f"""  `variableFunction`: "{variableFunction}".""")
    for value in DE_IDENTIFICATION_TEST_VALUES:
        print(f"""  `variableFunction({value})`: "{variableFunction(value)}".""")
    print()

