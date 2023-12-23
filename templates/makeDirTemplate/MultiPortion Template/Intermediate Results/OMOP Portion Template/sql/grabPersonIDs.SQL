USE DWS_OMOP_PROD
SELECT
	[person_id] AS 'person_id'
	,[person_source_value] AS 'Patient Key'
FROM
	[DWS_OMOP_PROD].[dbo].[PERSON]
WHERE
	person_source_value IN (XXXXX)