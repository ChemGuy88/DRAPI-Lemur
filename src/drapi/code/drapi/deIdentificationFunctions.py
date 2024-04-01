"""
Functions used in the mapping or de-identification of values, namely "convertColumnsHash.py" in the "Concatenated Results" template/module.
"""

import random
import string
from typing_extensions import (Callable,
                               Collection,
                               Tuple,
                               Union)
# Third-party packages
import numpy as np
import pandas as pd


def encryptValue1(value: Union[float, int, str],
                  secret: Union[int, Collection[int]]):
    """
    Additive encryption.
    Example:
    ```
    encryptValue1(value='123456789', secret=1)
    # 123456790
    ```
    """
    intsAndFloats = (int,
                     np.integer,
                     float,
                     np.floating)
    if isinstance(value, str):
        newValue = float(value) + secret
    elif isinstance(secret, intsAndFloats):
        newValue = value + secret
    else:
        newValue = value + secret
    return newValue


def encryptValue2(value: Union[str, int],
                  secret: str):
    r"""
    Encrypt with character-wise XOR operation of both operands, with the second operand rotating over the set of character-wise values in `secretkey`.
    Example:
    ```
    encryptValue1(value='123456789', secret='password')
    # 'AS@GBYE\I'
    ```
    """
    if isinstance(value, (int, str)):
        valueInOrd = []
        for el in str(value):
            valueInOrd.append(ord(el))
        resultList = []
        for it, integer in enumerate(valueInOrd):
            result = integer ^ ord(secret[it % len(secret)])
            resultList.append(result)
        newValue = "".join([chr(el) for el in resultList])
    else:
        raise Exception("`value` must be of type `int` or `str`.")
    return newValue


def encryptValue3(value: Union[int],
                  secret: int):
    """
    Encrypt with whole-value XOR operation. Requires both operands to be integers.
    Example:
    ```
    encryptValue1(value=123456789, secret=111111111)
    # 1326016938
    ```
    """
    if isinstance(value, (int,)):
        newValue = value ^ secret
    else:
        raise Exception(f"""`value` must be of type `int`. Received type "{type(value)}".""")
    return newValue


def deIdentificationFunction(encryptionFunction,
                             irbNumber,
                             suffix,
                             value):
    """
    """
    if pd.isna(value):
        deIdentifiedValue = ""
    else:
        newValue = encryptionFunction(value)
        deIdentifiedValue = f"{irbNumber}_{suffix}_{newValue}"
    return deIdentifiedValue


def functionFromSettings(ENCRYPTION_TYPE: int,
                         ENCRYPTION_SECRET: Union[int, str],
                         IRB_NUMBER: str) -> Tuple[Union[int, str], Callable]:
    """
    """
    ENCRYPTION_TYPE = int(ENCRYPTION_TYPE)
    ENCRYPTION_SECRET = str(ENCRYPTION_SECRET)
    # Set Parameter: Encryption function: Core
    if ENCRYPTION_TYPE == 1:
        encryptionFunction = encryptValue1
    elif ENCRYPTION_TYPE == 2:
        encryptionFunction = encryptValue2
    elif ENCRYPTION_TYPE == 3:
        encryptionFunction = encryptValue3
    else:
        raise Exception(f"""Argument `ENCRYPTION_TYPE` must be one of {{1, 2, 3}}, instead got "{ENCRYPTION_TYPE}".""")
    # Set Parameter: Encryption secret
    if ENCRYPTION_SECRET.lower() == "random":
        if ENCRYPTION_TYPE in [1, 3]:
            # Integer
            encryptionSecret = np.random.randint(1000000, 10000000)
        elif ENCRYPTION_TYPE in [2]:
            # Alphanumeric
            encryptionSecret = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + string.whitespace) for _ in range(15))
        else:
            raise Exception(f"""Argument `ENCRYPTION_TYPE` must be one of {{1, 2, 3}}, instead got "{ENCRYPTION_TYPE}".""")
    elif ENCRYPTION_SECRET.isnumeric():
        encryptionSecret = int(ENCRYPTION_SECRET)
    else:
        encryptionSecret = ENCRYPTION_SECRET

    # Set parameter: Encryption function: Wrapper
    def variableFunction(value, suffix: str, secret):
        """
        This is a wrapper function for `deIdentificationFunction`
        """
        if pd.isna(value):
            value = value
        elif isinstance(value, float):
            value = int(value)
        else:
            value = value
        deIdentifiedValue = deIdentificationFunction(value=value,
                                                     suffix=suffix,
                                                     encryptionFunction=lambda value1: encryptionFunction(value=value1,
                                                                                                          secret=secret),
                                                     irbNumber=IRB_NUMBER)
        return deIdentifiedValue
    return (encryptionSecret, variableFunction)
