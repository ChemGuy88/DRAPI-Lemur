"""
Gather files in a central location for the honest broker to review

Define input files paths
Define input directory paths
Define destination directory path

for directory path in input directory paths
    move all contents to destination directory path
for file in input file paths
    move file to destination directory path
"""

from pathlib import Path

INPUT_FILE_PATHS = ["IRB202001660 DatReq02/Intermediate Results/Notes Portion/data/output/free_text/patients_note/deid_note_1.tsv",
                    "IRB202001660 DatReq02/Intermediate Results/Notes Portion/data/output/free_text/patients_order_impression/deid_order_impression_1.tsv",
                    "IRB202001660 DatReq02/Intermediate Results/Notes Portion/data/output/free_text/patients_order_narrative/deid_order_narrative_1.tsv",
                    "IRB202001660 DatReq02/Intermediate Results/Notes Portion/data/output/free_text/patients_order_result_comment/deid_order_result_comment_1.tsv"]

INPUT_DIRECTORY_PATHS = ["IRB202001660 DatReq02/Concatenated Results/data/output/deIdentify/2023-03-14 14-17-10"]

OUTPUT_DIRECTORY_PATH = Path("")

inputFilePaths = [Path(string) for string in INPUT_FILE_PATHS]
inputDirectoryPaths = [Path(string) for string in INPUT_DIRECTORY_PATHS]

print("This is not implemented. Move files manually. See script for what files need to be moved.")
