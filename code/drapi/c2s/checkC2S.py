"""
Check the C2S status of MRNs. This checks C2S enrollment and death information.
"""

import argparse
import sys
# Third-party packages
import pandas as pd
from pathlib import Path
# Local packages
from c2s import checkStatus, doCheck


def checkStatusWrapper(fpath: str, columnName: str, statusType: str, location: str, verbosity):
    """
    """
    fpath
    data = pd.read_csv(fpath)

    MRNsAsList = data[columnName].to_list()

    result = checkStatus(statusType=statusType,
                         location=location,
                         listOfMRNs=MRNsAsList)

    checkResultPass, failedRows = doCheck(result, statusType)

    if checkResultPass:
        print("Passed.")
    elif not checkResultPass:
        print("Not passed. Below are the failed cases:")
        print(failedRows)

    if verbosity < 10:
        print(result.set_index(columnName).sort_index().to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--verbosity", help="""Increase output verbosity. See "logging" module's log level for valid values.""", type=int, default=10)

    parser.add_argument("fpath", help="The path to the file that contains the MRNs.", type=str)

    parser.add_argument("columnName", help="The name of the column that contains the MRNs.", type=str)

    parser.add_argument("statusType", help="The type of status check.", choices=["C2S", "death"], type=str)

    parser.add_argument("location", help="The MRN location type.", choices=["gnv", "jax"], type=str)

    args = parser.parse_args()

    fpathAsString = args.fpath
    columnName = args.columnName
    statusType = args.statusType
    location = args.location

    verbosity = args.verbosity

    fpath = Path(fpathAsString)

    checkStatusWrapper(fpath, columnName, statusType, location, verbosity)

    if not len(sys.argv) > 1:
        parser.print_usage()
