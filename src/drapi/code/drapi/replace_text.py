"""
"""

from pathlib import Path
from typing_extensions import Union


def preview_file(file_path: Path,
                 num_characters: int = 100):
    """
    """
    with open(file_path, "rb") as file:
        text = file.read(num_characters)
    print(text)


def replace_text(file_path_in: Path,
                 old_text: Union[bytes, str],
                 new_text: Union[bytes, str],
                 file_path_out: Path = None):
    """
    """
    # Read
    with open(file_path_in, "rb") as file:
        file_text = file.read()

    # Replace
    file_text_new_0 = file_text.replace(old_text, new_text)

    # Decode
    if isinstance(file_text, bytes):
        file_text_new_1 = file_text_new_0.decode()
    else:
        file_text_new_1 = file_text_new_0

    # Choose file path to write to.
    if file_path_out:
        file_path_out_ = file_path_out
    else:
        file_path_out_ = file_path_in

    # Write
    with open(file_path_out_, "w") as file:
        file.write(file_text_new_1)


def replace_text_wrapper(file_path_in: Path,
                         output_dir: Path,
                         old_text: Union[bytes, str],
                         new_text: Union[bytes, str]):
    """
    Wrapper for parallel processing.
    """
    file_path_in_name = file_path_in.name
    file_path_out = output_dir.joinpath(file_path_in_name)
    replace_text(file_path_in=file_path_in,
                 old_text=old_text,
                 new_text=new_text,
                 file_path_out=file_path_out)
