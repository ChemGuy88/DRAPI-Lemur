"""
Utility functions used with images data requests.
"""

__all__ = ["getPatientNumber",
           "getSessionNumber",
           "getPatientAndSessionNumbers"]

import re


def getPatientNumber(string):
    """
    Returns the patient number from an image data release folder name.
    """
    pattern = r"^Patient_(?P<patientNumber>\d+)_IRB201802747$"
    obj = re.match(pattern, string)
    if obj:
        groupdict = obj.groupdict()
        patientNumber = groupdict["patientNumber"]
        if len(patientNumber) > 0:
            patientNumber = int(patientNumber)
        else:
            raise Exception("""String is of an unexpected format: "{string}".""")
    else:
        raise Exception("String was of an unexpected format")
    return patientNumber


def getSessionNumber(string):
    """
    Returns the session number from an image data release folder name.
    """
    pattern = r"^Session_(?P<patientNumber>\d+)_IRB201802747[_]{0,1}(?P<sessionNumber>\d*)$"
    obj = re.match(pattern, string)
    if obj:
        groupdict = obj.groupdict()
        sessionNumber = groupdict["sessionNumber"]
        if len(sessionNumber) > 0:
            sessionNumber = int(sessionNumber)
        elif len(sessionNumber) == 0:
            sessionNumber = 0
        else:
            raise Exception("""String is of an unexpected format: "{string}".""")
    else:
        raise Exception(f"""String was of an unexpected format: "{string}".""")
    return sessionNumber


def getPatientAndSessionNumbers(string):
    """
    Returns the patient and session number from an image data release folder name as a 2-tuple.
    """
    pattern = r"^(?:Session|Patient)_(?P<patientNumber>\d+)_IRB201802747[_]{0,1}(?P<sessionNumber>\d*)$"
    obj = re.match(pattern, string)
    if obj:
        groupdict = obj.groupdict()
        patientNumber = groupdict["patientNumber"]
        if len(patientNumber) > 0:
            patientNumber = int(patientNumber)
        else:
            raise Exception("""String is of an unexpected format: "{string}".""")
        sessionNumber = groupdict["sessionNumber"]
        if len(sessionNumber) > 0:
            sessionNumber = int(sessionNumber)
        elif len(sessionNumber) == 0:
            sessionNumber = 0
        else:
            raise Exception("""String is of an unexpected format: "{string}".""")
    else:
        raise Exception(f"""String was of an unexpected format: "{string}".""")
    return patientNumber, sessionNumber
