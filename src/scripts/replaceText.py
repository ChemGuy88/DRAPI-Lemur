"""
Replaces text using byte strings.

This is useful for converting CRLF to LF. You can do so like this:

```bash
python replaceText.py -f FILEPATH -bo $'\\r\\n' -bn $'\\n'
```
"""

import argparse
import pprint
from pathlib import Path


def previewFile(fpath: Path,
                numCharacters: int=100):
    """
    """
    with open(fpath, "rb") as file:
        text = file.read(numCharacters)
    print(text)


def convertNewlines(fpath: Path,
                    oldLineEnding: bytes,
                    newLineEnding: bytes):
    """
    """
    with open(fpath, "rb") as file:
        text = file.read()
        newText = text.replace(oldLineEnding, newLineEnding)
    with open(fpath, "wb") as file:
        file.write(newText)


if __name__ == "__main__":
    # >>> `Argparse` arguments >>>
    parser = argparse.ArgumentParser()

    # Arguments: Main
    parser.add_argument("-d",
                        "--LIST_OF_DIRECTORIES",
                        nargs="*",
                        type=Path,
                        help="List of directories whose contents are to be edited.")
    parser.add_argument("-f",
                        "--LIST_OF_FILES",
                        nargs="*",
                        type=Path,
                        help="List of files to edit.")
    HINT = """HINT, to pass an escaped character like "\\n" in a BASH-like shell, use `$'\\n'`. Note the single quotes."""
    parser.add_argument("-bo",
                        "--BYTES_OLD",
                        type=lambda string: bytes(string, encoding="utf-8"),
                        help=f"""The bytes to replace. {HINT}""")
    parser.add_argument("-bn",
                        "--BYTES_NEW",
                        type=lambda string: bytes(string, encoding="utf-8"),
                        help=f"The bytes to replace with. {HINT}")


    parser.add_argument("-p",
                        "--PREVIEW_FILE",
                        type=Path,
                        help="The path to a file to preview in bytes.")
    parser.add_argument("-nc",
                        "--PREVIEW_FILE_NUM_CHARS",
                        type=int,
                        help="The number of bytes to preview from a file.")

    argNamespace = parser.parse_args()

    # Parsed arguments: Main
    LIST_OF_DIRECTORIES = argNamespace.LIST_OF_DIRECTORIES
    LIST_OF_FILES = argNamespace.LIST_OF_FILES
    OLD_LINE_ENDING = argNamespace.OLD_LINE_ENDING
    NEW_LINE_ENDING = argNamespace.NEW_LINE_ENDING

    PREVIEW_FILE = argNamespace.PREVIEW_FILE
    PREVIEW_FILE_NUM_CHARS = argNamespace.PREVIEW_FILE_NUM_CHARS
    # <<< `Argparse` arguments <<<

    # >>> Custom argument parsing >>>
    if LIST_OF_FILES or LIST_OF_DIRECTORIES:
        pass
    elif PREVIEW_FILE:
        pass
    else:
        parser.error("Although `LIST_OF_FILES`, `LIST_OF_DIRECTORIES`, and `PREVIEW_FILE` are marked as optional in the help text, you must actually provide arguments for at least one of them.")
    # <<< Custom argument parsing <<<

    # >>> Module variables >>>        
    thisFilePath = Path(__file__)
    thisFileStem = thisFilePath.stem
    # <<< Module variables <<<

    # >>> Logging block >>>
    print(f"""Running "{thisFileStem}".""")
    argList = argNamespace._get_args() + argNamespace._get_kwargs()
    argListString = pprint.pformat(argList)
    print(f"""Script arguments:\n{argListString}""")
    # <<< Logging block <<<

    # >>> Begin module body >>>
    if LIST_OF_FILES:
        listOfFiles1 = sorted([Path(path) for path in LIST_OF_FILES])
        for fpath in LIST_OF_FILES:
            fpath = Path(fpath)  # For type hinting
            convertNewlines(fpath=fpath,
                            oldLineEnding=OLD_LINE_ENDING,
                            newLineEnding=NEW_LINE_ENDING)
    elif LIST_OF_DIRECTORIES:
        for dpath in LIST_OF_DIRECTORIES:
            dpath = Path(dpath)  # For type hinting
            listOfFiles2 = sorted(list(dpath.iterdir()))
            for fpath in listOfFiles2:
                convertNewlines(fpath=fpath,
                                oldLineEnding=OLD_LINE_ENDING,
                                newLineEnding=NEW_LINE_ENDING)
    elif PREVIEW_FILE:
        previewFile(fpath=PREVIEW_FILE,
                    numCharacters=PREVIEW_FILE_NUM_CHARS)

    print(f"""Finished running "{thisFileStem}".""")