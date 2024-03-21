SELECT
    A.PATID AS "OneFlorida Patient ID",
    A.PATNT_KEY AS "Patient Key",
    B.IDENT_ID AS "MRN (UF)",
    C.IDENT_ID AS "MRN (Jax)",
    D.IDENT_ID AS "MRN (Pathology)"
FROM
    [DWS_PCORNET].[pcnv5].[PATIENT_MAPPING] AS A
    LEFT OUTER JOIN [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] AS B ON a.patnt_key = b.patnt_key
    AND b.ident_id_type = 101
    AND b.LOOKUP_IND = 'Y'
    LEFT OUTER JOIN [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] AS C ON a.patnt_key = c.patnt_key
    AND c.ident_id_type = 110
    AND c.LOOKUP_IND = 'Y'
    LEFT OUTER JOIN [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] AS D ON a.patnt_key = d.patnt_key
    AND d.ident_id_type = 99
    AND d.LOOKUP_IND = 'Y'
WHERE
    { PYTHON_VARIABLE: IDTypeSQL } IN ({ PYTHON_VARIABLE: IDTypeValues })