"""
Stuff for OMOP
"""

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

    configFile["data_output"]["identified_file_location"] = identified_file_location.__str__() + "/"
    configFile["data_output"]["deidentified_file_location"] = deidentified_file_location.__str__() + "/"
    configFile["data_output"]["mapping_location"] = mapping_location.__str__() + "/"

    with open(outputPath, "w") as file:
        yaml.dump(configFile, file)
