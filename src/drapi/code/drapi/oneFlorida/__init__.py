"""
The OneFlorida workflow.
"""

ID_TYPE_LIST = ["MRN (Jax)",
                "MRN (Pathology)",
                "MRN (UF)",
                "OneFlorida Patient ID",
                "Patient Key"]
ID_TYPE_DICT = {"oneflorida patient id": "A.PATID",
                "patient key": "A.PATNT_KEY",
                "mrn (uf)": "B.IDENT_ID",
                "mrn (jax)": "C.IDENT_ID",
                "mrn (pathology)": "D.IDENT_ID"}
