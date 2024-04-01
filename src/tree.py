"""
Utility program to visualize the structure of a directory and its contents in the form of a tree. Compare this to the Linux built-in `tree`.
"""

USAGE_INSTRUCTIONS = """Usage instructions

To use this program, just enter in the command line:

`python tree.py directory_path`

where `directory_path` is the path of the directory you want the tree of. If you are in the directory you want the tree for, then you just do

`python tree.py .`

Note the above example assumes "tree.py" is in the same directory that you are operating on. If the program is in another directory, you must type its path as below

`python path/to/tree.py directory_path`
"""

# NOTE The function `tree` is copied from, and is also available in the `drapi` module.

import argparse
import sys
# Package imports
from drapi.code.drapi.drapi import tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("dir_path",
                        help="The path of the directory for which to get the tree.",
                        type=str)

    parser.add_argument("--level",
                        help="The level.",
                        default=-1,
                        type=int)

    parser.add_argument("--limit_to_directories",
                        help="Limit to directories.",
                        default=False,
                        type=bool)

    parser.add_argument("--length_limit",
                        help="The length limit.",
                        default=1000,
                        type=int)

    if not len(sys.argv) > 1:
        parser.print_usage()
        print(USAGE_INSTRUCTIONS)
        sys.exit(0)
    else:
        args = parser.parse_args()

    dir_path = args.dir_path
    level = args.level
    limit_to_directories = args.limit_to_directories
    length_limit = args.length_limit

    tree(dir_path=dir_path,
         level=level,
         limit_to_directories=limit_to_directories,
         length_limit=length_limit)

