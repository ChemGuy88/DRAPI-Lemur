-- SERVER: EDW.shands.ufl
SELECT
    *
FROM
    (
        SELECT
            DISTINCT A.ENCOUNTER_NUM AS 'i2b2 Encounter Number',
            A.ENCOUNTER_IDE AS 'Encounter # (CSN)'
        FROM
            [DWS_I2B2].[dbo].ENCOUNTER_MAPPING AS A
    ) AS A
WHERE
    A.[i2b2 Encounter Number] IN ({ PYTHON_VARIABLE: i2b2_Encounter_Number })
