"""
Makes symbolic links
"""

import os
from pathlib import Path

LIST_OF_DIRECTORIES = ["Concatenated Results\data\output\makeMapsFromOthers\2023-11-07 12-05-06"]
LIST_OF_FILES = ["Concatenated Results\data\output\makeMapsFromScratch\2023-12-20 15-42-03\Patient Encounter Key map.csv"]
DESTINATION_FOLDER = "Concatenated Results\data\All Maps (SymLinks)"

destinationFolder = Path(DESTINATION_FOLDER)

for fpathString in LIST_OF_FILES:
    fpath = Path(fpathString)
    # SymLink to destination
    dest = destinationFolder.joinpath(fpath.name)
    os.symlink(fpath, dest)

for directoryString in LIST_OF_DIRECTORIES:
    directory = Path(directoryString)
    for fpath in directory.iterdir():
        # SymLink to DESTINATION
        dest = destinationFolder.joinpath(fpath.name)
        os.symlink(fpath, dest)

