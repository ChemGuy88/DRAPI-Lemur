import pandas as pd
from drapi.code.drapi.drapi import getMapType

# Non-duplicate cases
m1 = pd.DataFrame({"A": ['a', 'b'],
                   "B": [1, 2]})
m2 = pd.DataFrame({"A": ['a', 'a'],
                   "B": [1, 2]})
m3 = pd.DataFrame({"A": ['a', 'b'],
                   "B": [1, 1]})
m4 = pd.DataFrame({"A": ['a', 'b', 'a'],
                   "B": [1, 1, 2]})

# Duplicate cases
m5 = pd.DataFrame({"A": ['a', 'b', 'a', 'b'],
                   "B": [1, 2, 1, 2]})
m6 = pd.DataFrame({"A": ['a', 'a', 'a', 'a'],
                   "B": [1, 2, 1, 2]})
m7 = pd.DataFrame({"A": ['a', 'b', 'a', 'b'],
                   "B": [1, 1, 1, 1]})
m8 = pd.DataFrame({"A": ['a', 'b', 'a', 'a', 'b', 'a'],
                   "B": [1, 1, 2, 1, 1, 2]})

caseList = [m1,  # "1:1"
            m2,  # "1:m"
            m3,  # "m:1"
            m4,  # "m:m"
            m5,  # "1:1"
            m6,  # "1:m"
            m7,  # "m:1"
            m8]  # "m:m"
caseCheck = ["1:1",
             "1:m",
             "m:1",
             "m:m",
             "1:1",
             "1:m",
             "m:1",
             "m:m"]

resultsDict = {}
for it, testCase in enumerate(caseList, start=1):
    resultsDict[it] = getMapType(testCase)

resultsDf = pd.DataFrame.from_dict(data=resultsDict, orient="index", columns=["Map Type"])
resultsDf["Check"] = resultsDf["Map Type"] == caseCheck
print(resultsDf)
