"""
Parsers used by argparse.
"""

def parse_string_to_boolean(string_: str) -> bool:
    """
    """
    if string_.lower() == "true":
        return True
    elif string_.lower() == "false":
        return False
    else:
        raise Exception("String must be one of {true, false}, case insensitive.")
