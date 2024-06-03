"""
Test command-line argument parsing with Python's `argparse` module.
"""

import argparse
# Third-party packages
pass
# First-party packages
pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--DOWNLOAD_DATA",
                        required=True,
                        type=lambda value: True if value.lower() == "true" else False if value.lower() == "false" else None)

    argNamespace = parser.parse_args()

    # Parsed arguments: Main: Multiple query option
    DOWNLOAD_DATA = argNamespace.DOWNLOAD_DATA

    if isinstance(DOWNLOAD_DATA, type(None)):
        parser.error("--DOWNLOAD_DATA must be one of {{True, False}}.")

    print(DOWNLOAD_DATA)
