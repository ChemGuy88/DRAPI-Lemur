"""
"""

# Local packages
from drapi.code.drapi.deIdentificationFunctions import (deIdentificationFunction,
                                                        encryptValue1,
                                                        encryptValue2,
                                                        encryptValue3)

x1 = deIdentificationFunction(encryptionFunction=lambda value: encryptValue1(value=value,
                                                                             offset=1),
                              irbNumber="IRB012345678",
                              suffix="X",
                              value='123456789')
x2 = deIdentificationFunction(encryptionFunction=lambda value: encryptValue2(value=value,
                                                                             secretKey='password'),
                              irbNumber="IRB012345678",
                              suffix="X",
                              value='123456789')
x3 = deIdentificationFunction(encryptionFunction=lambda value: encryptValue3(value=value,
                                                                             secretKey=111111111),
                              irbNumber="IRB012345678",
                              suffix="X",
                              value=123456789)

print(x1)
print(x2)
print(x3)
