"""
Stuff for OMOP
"""

import os
import sys
import yaml
from pathlib import Path


def editConfig(inputPath: Path, outputPath: Path, timestamp):
    """
    Edits a YAML config file so that the output paths end with a timestamp
    """
    with open(inputPath) as file:
        configFile = yaml.safe_load(file)
    identified_file_location = Path(configFile["data_output"]["identified_file_location"]).joinpath(timestamp)
    deidentified_file_location = Path(configFile["data_output"]["deidentified_file_location"]).joinpath(timestamp)
    mapping_location = Path(configFile["data_output"]["mapping_location"]).joinpath(timestamp)

    sep = os.sep

    configFile["data_output"]["identified_file_location"] = identified_file_location.__str__() + sep
    configFile["data_output"]["deidentified_file_location"] = deidentified_file_location.__str__() + sep
    configFile["data_output"]["mapping_location"] = mapping_location.__str__() + sep

    with open(outputPath, "w") as file:
        yaml.dump(configFile, file)


def interpretPath(pathAsString: str) -> str:
    """
    Makes sure path separators are appropriate for the current operating system.
    """
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        newPathAsString = pathAsString.replace("\\", "/")
    elif operatingSystem == "win32":
        newPathAsString = pathAsString
    else:
        raise Exception("Unsupported operating system")
    return newPathAsString
