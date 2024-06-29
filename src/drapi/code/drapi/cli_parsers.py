"""
Parsers used by argparse.
"""

import ast


def parse_string_to_boolean(string_: str) -> bool:
    """
    """
    if string_.lower() == "true":
        return True
    elif string_.lower() == "false":
        return False
    else:
        raise Exception("String must be one of {true, false}, case insensitive.")


def parse_string_to_bytes(string_: str) -> bytes:
    """
    Expects `string_` to be a Python string literal representation of a byte like `"\\\\x00"` or `"a"`.
    """
    # lazy hack 1
    if string_ == "'":
        string_1 = f'b"{string_}"'
    elif string_ == '"':
        string_1 = f"b'{string_}'"
    else:
        string_1 = f"""b'{string_}'"""
    bytes_array = ast.literal_eval(string_1)
    return bytes_array
