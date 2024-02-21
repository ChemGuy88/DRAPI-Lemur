"""
Create a working directory from a template. The general structure of the directory to be made is as follows:

New Directory
├── code
├── data
│   ├── input
│   └── output
├── logs
├── sql
├── .env
├── .gitignore
└── README.md

where "New Directory" is the name of the directory to be created
"""

import argparse
import json
import os
import sys
import shutil
from pathlib import Path
# Local imports
from drapi.templates.makeDirTemplate import PATH as makeDirTemplatePath


def win2nixPath(string: str) -> str:
    """
    Converts a Windows-like path to a Linux-like path by changing the path separators.
    """
    platform = sys.platform
    platformSeparator = os.sep
    if platform == "darwin":
        newString = platformSeparator.join(string.split("\\"))
    elif platform == "linux":
        newString = platformSeparator.join(string.split("\\"))
    elif platform == "win32":
        newString = string
    else:
        raise Exception(f"""Unsupported operating system: "{platform}".""")
    return newString


ROOT_PATH = makeDirTemplatePath.__str__()
# NOTE `optionsDict` expects `"path"` values to be in Windows format because it's later used by `win2nixPath`
optionsDict = {"BO": {"number": 2,
                      "path": r"\MultiPortion Template\Intermediate Results\BO Portion Template"},
               "De-identification Suite": {"number": 1,
                                           "path": r"\MultiPortion Template\Concatenated Results"},
               "General Script": {"number": 3,
                                  "path": r"\Intermediate Results\General Script Template"},
               "i2b2": {"number": 4,
                        "path": r"\MultiPortion Template\Intermediate Results\i2b2 Portion Template"},
               "Multi-Portion Template": {"number": 0,
                                          "path": r"\MultiPortion Template"},
               "Notes": {"number": 5,
                         "path": r"\MultiPortion Template\Intermediate Results\Notes Portion Template"},
               "OMOP": {"number": 6,
                        "path": r"\MultiPortion Template\Intermediate Results\OMOP Portion Template"}}

optionsDict2 = {values["number"]: {"name": name,
                                   "path": ROOT_PATH + win2nixPath(values["path"])} for name, values in optionsDict.items()}

optionsNumbers = {name: value for name, values in optionsDict.items() for key, value in values.items() if key == "number"}


def copyTemplateDirectory(templateChoice: int,
                          destinationPath: str) -> None:
    """
    Given a template selection `templateChoice`, copies the corresponding template directory to the destination path, `destinationPath`.
    """

    templateDirPath = Path(optionsDict2[templateChoice]["path"])

    shutil.copytree(src=templateDirPath,
                    dst=destinationPath)

    # Prepare template for use
    for fpath in Path(destinationPath).glob("./**/*.*"):
        # Remove placeholder files
        if fpath.name.lower() == ".deleteme":
            os.remove(fpath)
        # Modify ".gitignore"
        if fpath.name.lower() == ".gitignore":
            with open(fpath, "r") as file:
                text = file.read()
                text = text.replace("!**/launchIPython.bat\n", "")
                text = text.replace("!.env", ".env")
                text = text.replace("!data/input/\n", "")
                text = text.replace("!data/output/\n", "")
            with open(fpath, "w") as file:
                file.write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("templateChoice", help=f"""The template you wish to copy. Each template has a numerical option: {json.dumps(optionsNumbers)}""", choices=sorted(list(optionsDict2.keys())), type=int)

    parser.add_argument("destinationPath", help="The directory path for `templateChoice`.", type=str)

    args = parser.parse_args()

    templateChoice = args.templateChoice
    destinationPath = args.destinationPath

    copyTemplateDirectory(templateChoice=templateChoice,
                          destinationPath=destinationPath)
