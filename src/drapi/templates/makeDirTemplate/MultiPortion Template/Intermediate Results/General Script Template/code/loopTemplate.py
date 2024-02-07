from typing import Collection

MESSAGE_MODULO_CHUNKS = 100
MIN_NUMBER_OF_MESSAGES = 100

PLACEHOLDER1 = 1  # An integer
PLACEHOLDER2 = []  # An iterable


def func1(chunk1) -> Collection:
    """
    Dummy function that represents a process. `chunks` is a function of `chunk1`
    """
    result = []
    return result


def getNumChunks(result) -> int:
    """
    Dummy function that represents a counting process.
    """
    numChunks = 1
    return numChunks


def getChunks(result) -> Collection:
    """
    A dummy function that represents a chunking process.
    """
    chunks = []
    return chunks


numChunks1 = PLACEHOLDER1
# >>> Calculate logging requency for loop layer 1
if numChunks1 < MESSAGE_MODULO_CHUNKS:
    moduloChunks1 = numChunks1
else:
    moduloChunks1 = round(numChunks1 / MESSAGE_MODULO_CHUNKS)
if numChunks1 / moduloChunks1 < MIN_NUMBER_OF_MESSAGES:
    moduloChunks1 = 1
else:
    pass
# <<< <<< <<< <<<
chunks = PLACEHOLDER2
for it1, chunk1 in enumerate(chunks, start=1):
    # >>> Set chunk verbosity for loop layer 1
    if it1 % moduloChunks1 == 0:
        allowLogging = True
    else:
        allowLogging = False
    # <<< <<< <<< <<<
    result1 = func1(chunk1)
    numChunks2 = getNumChunks(result1)
    chunks2 = getChunks(result1)
    # >>> Calculate logging requency for loop layer 2
    if numChunks2 < MESSAGE_MODULO_CHUNKS:
        moduloChunks2 = numChunks2
    else:
        moduloChunks2 = round(numChunks2 / MESSAGE_MODULO_CHUNKS)
    if numChunks2 / moduloChunks2 < MIN_NUMBER_OF_MESSAGES:
        moduloChunks2 = 1
    else:
        pass
    # <<< <<< <<< <<<
    for it2, chunk2 in enumerate(chunks2, start=1):
        # >>> Set chunk verbosity for loop layer 1
        if it2 % moduloChunks2 == 0:
            allowLogging = True
        else:
            allowLogging = False
        # <<< <<< <<< <<<
