import json
# Local imports
from drapi.code.drapi.constants.phiVariables import (VARIABLE_SUFFIXES_BO,
                                                     VARIABLE_SUFFIXES_I2B2,
                                                     VARIABLE_SUFFIXES_NOTES,
                                                     VARIABLE_SUFFIXES_OMOP)
from drapi.code.drapi.deIdentificationFunctions import functionFromSettings

IRB_NUMBER = "PROTOCOL-123456789"
VARIABLE_SUFFIXES = {}
LIST_OF_VARIABLE_SUFFIX_PORTIONS = [VARIABLE_SUFFIXES_BO, VARIABLE_SUFFIXES_I2B2, VARIABLE_SUFFIXES_NOTES, VARIABLE_SUFFIXES_OMOP]
for di in LIST_OF_VARIABLE_SUFFIX_PORTIONS:
    VARIABLE_SUFFIXES.update(di)


string = """{'Encounter # (CSN)': [1, 'random'],
             'Encounter Key': [1, 'random'],
             'Linkage Note ID': [1, 'random'],
             'MRN (Jax)': [1, 'random'],
             'MRN (UF)': [1, 'random'],
             'Note ID': [1, 'random'],
             'Note Key': [1, 'random'],
             'Patient Key': [1, 'random'],
             'Provider Key': [1, 'random']}"""
string = string.replace("'", '"')

DICTIONARY_OF_MAPPING_ARGUMENTS = json.loads(string)

mappingArguments = [{variableName: tu} for variableName, tu in DICTIONARY_OF_MAPPING_ARGUMENTS.items()]

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
    print(VARIABLE_SUFFIXES[variableName]["deIdIDSuffix"])
    print(encryptionSecret)
    print(variableFunction)
    print(DE_IDENTIFICATION_FUNCTIONS[variableName](1))
    print()

print()
for variableName, func in DE_IDENTIFICATION_FUNCTIONS.items():
    print(f"""  {variableName}: {func(1)}""")
    print(func)
    print()


def func0(cookie): return print(cookie)
