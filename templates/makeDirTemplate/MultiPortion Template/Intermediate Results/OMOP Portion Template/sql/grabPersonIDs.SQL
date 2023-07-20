-- Copied from "/Volumes/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Guo/IRB202201080/sql/grab_person_ids.sql"
use DWS_OMOP_PROD

SELECT 
	xref.PERSON_MAPPING.person_id as person_id,
	xref.PERSON_MAPPING.patient_key as patient_key
FROM
	xref.PERSON_MAPPING
WHERE
    xref.PERSON_MAPPING.patient_key IN (XXXXX)