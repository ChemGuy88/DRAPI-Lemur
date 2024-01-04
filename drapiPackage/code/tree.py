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
from itertools import islice
from pathlib import Path


def tree(dir_path: Path,
         level: int = -1,
         limit_to_directories: bool = False,
         length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""
    # prefix components:
    space = '    '
    branch = '│   '
    # pointers:
    tee = '├── '
    last = '└── '

    dir_path = Path(dir_path)  # accept string coerceable to Path
    files = 0
    directories = 0

    def inner(dir_path: Path, prefix: str = '', level=-1):
        nonlocal files, directories
        if not level:
            return  # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix + extension, level=level - 1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1
    print(dir_path.name)
    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        print(line)
    if next(iterator, None):
        print(f'... length_limit, {length_limit}, reached, counted:')
    print(f'\n{directories} directories' + (f', {files} files' if files else ''))

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

