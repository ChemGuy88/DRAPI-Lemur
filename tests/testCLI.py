"""
Test command-line argument parsing with Python's `argparse` module.
"""

import argparse
# Third-party packages
pass
# First-party packages
from drapi.code.drapi.cli_parsers import parse_string_to_boolean

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--boolean",
                        default=False,
                        type=parse_string_to_boolean)

    argNamespace = parser.parse_args()

    # Parsed arguments: Main: Multiple query option
    boolean = argNamespace.boolean

    print(boolean)
