"""
SQL helper functions
"""


def labelMRNColumns(query):
    """
    NOTE Not implemented

    Replace text in a query for each of the MRN columsn thusly:

    `Table__1308.IDENT_ID_INT` --> `Table__1308.IDENT_ID_INT as MRN_UF`
    `Table__1311.IDENT_ID_int` --> `Table__1311.IDENT_ID_int as MRN_Vista`
    `Table__1312.IDENT_ID_int` --> `Table__1312.IDENT_ID_int as MRN_Rehab`
    `Table__1117.IDENT_ID_INT` --> `Table__1117.IDENT_ID_INT as MRN_Jax`
    `Table__2699.IDENT_ID_INT` --> `Table__2699.IDENT_ID_INT as MRN_CFH_Lessburg`
    `Table__2700.IDENT_ID_INT` --> `Table__2700.IDENT_ID_INT AS MRN_CFH_Villages`

    Outline

    for each instance of the above strings, if it's not behind a comment marker (e.g., `--`), replace it with its corresponding string pair. If it's the last column make sure to no add a comma
    """
    # TODO
    return
