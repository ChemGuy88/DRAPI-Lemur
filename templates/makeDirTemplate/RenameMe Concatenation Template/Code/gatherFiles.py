"""
Gather files in a central location for the honest broker to review

Define input files paths
Define input directory paths
Define destination directory path

create compression archive in destination directory path
for directory path in input directory paths
    move all contents to compression archive
for file in input file paths
    move file to compression archive
"""

from pathlib import Path

# Arguments

PROJECT_ROOT_DIRECTORY = Path("").absolute().parent

INPUT_FILE_PATHS = []

INPUT_DIRECTORY_PATHS = [Path("data/output/deleteColumns/2023-03-31 12-00-40"),
                         PROJECT_ROOT_DIRECTORY.joinpath("Intermediate Results/De-identified Notes/2023-03-30")]

OUTPUT_DIRECTORY_PATH = Path("")

# List all input files
inputFilePaths = [Path(string) for string in INPUT_FILE_PATHS]
inputDirectoryPaths = [Path(string) for string in INPUT_DIRECTORY_PATHS]

# TODO Create compression archive

# TODO Add all input files to compression archive

# TODO Move compression archive to destination directory

print("This is not implemented. Move files manually. See script arguments for what files need to be moved.")
