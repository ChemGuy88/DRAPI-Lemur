"""
A collection of classes
"""

class SecretString(str):
    """A `str` obj with a special `__repr__` that doesn't reveal the value."""

    def __init__(self, object=""):
        str.__init__(self)

    def __repr__(self):
        return "CENSORED"

    def __str__(self):
        return "CENSORED"
