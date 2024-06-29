"""
Testing parsing command-line string representation of bytes.

1. The user types bytes using string literal notation in the command line
2. Arguments go through argparse and a custom parser to convert the strings into bytes.
"""

import argparse
import ast
from typing_extensions import Dict

from drapi.code.drapi.cli_parsers import parse_string_to_bytes

# Script arguments
COMMAND_LINE_INPUT = """--arg_string \\x00\
                        --arg_bytes \\x00\
                        """
VALUES_TO_COMPARE = {1: {"name": "null byte",
                         "value": b"\x00"},
                     2: {"name": "escaped null byte",
                         "value": "\\x00"}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--arg_string",
                        type=str)
    parser.add_argument("--arg_bytes",
                        type=parse_string_to_bytes)

    argNamespace = parser.parse_args(COMMAND_LINE_INPUT.split())

    arg_string: str = argNamespace.arg_string
    arg_bytes: bytes = argNamespace.arg_bytes

    feedback_message = f"""\
`arg_string` type:  {type(arg_string)}
`arg_string` value: {arg_string}
`arg_bytes` type:   {type(arg_bytes)}
`arg_bytes` value:  {arg_bytes}\
"""
    print(feedback_message)

    for it, di in VALUES_TO_COMPARE.items():
        di: Dict[str, str] = di
        value_to_compare_name = di["name"]
        value_to_compare = di["value"]
        comparison_message = f"""\
    Is equal to {value_to_compare_name} ({repr(value_to_compare)})?
        `arg_string`: {arg_string == value_to_compare}
        `arg_bytes`:  {arg_bytes == value_to_compare}\
"""
        print(comparison_message)

    print("""Printing "utf-8" characters from 0 to 128.""")
    for integer in range(128):
        bytes_array = bytes([integer])
        bytes_array_repr = repr(bytes_array)
        bytes_array_decoded = bytes_array.decode(encoding="utf-8")
        bytes_array_decoded_repr = repr(bytes_array_decoded)
        bytes_array_escaped = ast.literal_eval(f"r{bytes_array_decoded_repr}")
        bytes_array_escaped_repr = repr(bytes_array_escaped)
        bytes_from_string = parse_string_to_bytes(string_=bytes_array_escaped)
        bytes_from_string_repr = repr(bytes_from_string)
        print(f"Working on integer {integer}:")
        print(f"  Bytes array:\t\t\t{bytes_array_repr}")
        print(f"  Bytes array decoded:\t\t{bytes_array_decoded}")
        print(f"  Bytes array escaped:\t\t {bytes_array_escaped_repr}")
        print(f"  String parsed as bytes:\t{bytes_from_string_repr}")
        if integer == 0:
            special_case_1_result = bytes_array_escaped == "\\x00"
            special_case_2_result = bytes_from_string == b"\x00"
            message_1 = f"""    Special case. Testing if the null byte was correctly escaped. Result: {special_case_1_result}."""
            message_2 = f"""    Special case. Testing if the null byte was correctly escaped and reconstructed. Result: {special_case_2_result}."""
            print(message_1)
            print(message_2)
        print()
