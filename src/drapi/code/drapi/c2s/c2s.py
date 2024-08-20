"""
Consent 2 Share
"""

from string import Template
import logging
# https://stackoverflow.com/questions/35217048/how-can-i-pass-variable-into-a-sql-file-while-running-through-python


def C2Share_query(
    sqlpath,
    facility,
    MRNs,
    logger: logging.Logger
):
    with open(sqlpath, 'r') as sqlfile:
        sql = sqlfile.read()
        C2ShareAndDeathQuery = Template(sql).substitute(
            facility=facility,
            MRNs=MRNs

    )  
    logger.info(C2ShareAndDeathQuery)
    return C2ShareAndDeathQuery
