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
import shutil
from pathlib import Path
# Local imports
from drapi.templates.makeDirTemplate import PATH as makeDirTemplatePath

ROOT_PATH = makeDirTemplatePath.__str__()
optionsDict = {"BO": {"number": 2,
                      "path": ROOT_PATH + r"\MultiPortion Template\Intermediate Results\BO Portion Template"},
               "De-identification Suite": {"number": 1,
                                           "path": ROOT_PATH + r"\MultiPortion Template\Concatenated Results"},
               "General Script": {"number": 3,
                                  "path": ROOT_PATH + r"\Intermediate Results\General Script Template"},
               "i2b2": {"number": 4,
                        "path": ROOT_PATH + r"\MultiPortion Template\Intermediate Results\i2b2 Portion Template"},
               "Multi-Portion Template": {"number": 0,
                                          "path": ROOT_PATH + r"\MultiPortion Template"},
               "Notes": {"number": 5,
                         "path": ROOT_PATH + r"\MultiPortion Template\Intermediate Results\Notes Portion Template"},
               "OMOP": {"number": 6,
                        "path": ROOT_PATH + r"\MultiPortion Template\Intermediate Results\OMOP Portion Template"}}

optionsDict2 = {values["number"]: {"name": name,
                                   "path": values["path"]} for name, values in optionsDict.items()}

optionsNumbers = {name: value for name, values in optionsDict.items() for key, value in values.items() if key == "number"}


def copyTemplateDirectory(templateChoice: int,
                          destinationPath: str) -> None:
    """
    Given a template selection `templateChoice`, copies the corresponding template directory to the destination path, `destinationPath`.
    """

    templateDirPath = Path(optionsDict2[templateChoice]["path"])

    shutil.copytree(src=templateDirPath,
                    dst=destinationPath)

    # Remove placeholder files
    for fpath in Path(destinationPath).glob("./**/*.*"):
        if fpath.name.lower() == ".deleteme":
            os.remove(fpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("templateChoice", help=f"""The template you wish to copy. Each template has a numerical option: {json.dumps(optionsNumbers)}""", choices=sorted(list(optionsDict2.keys())), type=int)

    parser.add_argument("destinationPath", help="", type=str)

    args = parser.parse_args()

    templateChoice = args.templateChoice
    destinationPath = args.destinationPath

    copyTemplateDirectory(templateChoice=templateChoice,
                          destinationPath=destinationPath)
