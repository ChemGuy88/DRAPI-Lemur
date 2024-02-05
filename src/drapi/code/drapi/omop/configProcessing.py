"""
Utility functions for processing the OMOP Data Pull configuration file.
"""

import os
import sys
from pathlib import Path
# Third-party packages
import yaml
# Custom packages
from drapi.drapi import successiveParents


def interpretPath(pathAsString: str) -> str:
    """
    Makes sure path separators are appropriate for the current operating system.
    """
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        newPathAsString = pathAsString.replace("\\", "/")
    elif operatingSystem == "win32":
        newPathAsString = pathAsString.replace("/", "\\")
    else:
        raise Exception("Unsupported operating system")
    return newPathAsString


def editConfig(inputPath: Path, outputPath: Path, timestamp: str) -> None:
    """
    Edits a YAML config file so that the output paths have a timestamp according to the following formats:
    Category 1 Directory: "parent1/parenti/parentn-1/parentn" --> "parent1/parenti/parentn-1/parentn/<timestamp>/"
    Category 2 Directory: "parent1/parenti/parentn-1/parentn" --> "parent1/parenti/parentn-1/<timestamp>/parentn/"

    Category 1 directories:
      - mapping_location
    Category 2 directories:
      - deidentified_file_location
      - identified_file_location
    """
    with open(inputPath) as file:
        configFile = yaml.safe_load(file)

    # Get paths as strings
    identified_file_location_str = configFile["data_output"]["identified_file_location"]
    deidentified_file_location_str = configFile["data_output"]["deidentified_file_location"]
    mapping_location_str = configFile["data_output"]["mapping_location"]

    # Make sure path separators are OS-appropriate
    identified_file_location_str2 = interpretPath(identified_file_location_str)
    deidentified_file_location_str2 = interpretPath(deidentified_file_location_str)
    mapping_location_str2 = interpretPath(mapping_location_str)

    # Add timestamp to path as subfolder
    pathDict = {"identified_file_location": identified_file_location_str2,
                "deidentified_file_location": deidentified_file_location_str2,
                "mapping_location": mapping_location_str2}
    CATEGORY_1 = ["mapping_location"]
    CATEGORY_2 = ["identified_file_location", "deidentified_file_location"]
    sep = os.sep
    for pathName, pathStr in pathDict.items():
        pathObj = Path(pathStr).absolute()
        if pathName in CATEGORY_1:
            newPath = pathObj.joinpath(timestamp)
        elif pathName in CATEGORY_2:
            pathDirName = pathObj.name
            pathParent, _ = successiveParents(pathObj, 1)
            newPath = pathParent.joinpath(timestamp).joinpath(pathDirName)
        else:
            raise Exception(f"""Unexpected value: "{pathName}".""")
        configFile["data_output"][pathName] = str(newPath) + sep

    with open(outputPath, "w") as file:
        yaml.dump(configFile, file)
