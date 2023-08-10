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


def main(INPUT_FILE_PATHS, INPUT_DIRECTORY_PATHS):
    """
    """
    # List all input files
    inputFilePaths = [Path(string) for string in INPUT_FILE_PATHS]
    inputDirectoryPaths = [Path(string) for string in INPUT_DIRECTORY_PATHS]

    # TODO Create compression archive

    # TODO Add all input files to compression archive
    _ = inputFilePaths
    _ = inputDirectoryPaths

    # TODO Move compression archive to destination directory

    print("This is not implemented. Move files manually. See script arguments for what files need to be moved.")
