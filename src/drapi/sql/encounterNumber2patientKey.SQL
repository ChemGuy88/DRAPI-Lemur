SELECT
  dbo.ALL_PATIENTS.PATNT_KEY,
  PATNT_ENCNTR_KEY_XREF1.ENCNTR_CSN_ID
FROM
  dbo.ALL_PATIENTS RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS  ALL_PT_SNAPSHOTS_ENCOUNTER ON (ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY)
   RIGHT OUTER JOIN dbo.PATIENT_ENCOUNTER_DTL ON (ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_SNAPSHT_KEY=dbo.PATIENT_ENCOUNTER_DTL.DSCHRG_PATNT_SNAPSHT_KEY  AND  dbo.PATIENT_ENCOUNTER_DTL.TEST_IND='N'
)
   LEFT OUTER JOIN dbo.PATNT_ENCNTR_KEY_XREF  PATNT_ENCNTR_KEY_XREF1 ON (dbo.PATIENT_ENCOUNTER_DTL.PATNT_ENCNTR_KEY=PATNT_ENCNTR_KEY_XREF1.PATNT_ENCNTR_KEY  AND  dbo.PATIENT_ENCOUNTER_DTL.TEST_IND='N'
)
  
WHERE
  (
   PATNT_ENCNTR_KEY_XREF1.ENCNTR_CSN_ID  IN  ( 0123456789, 1234567890  )
   AND
   ( dbo.ALL_PATIENTS.TEST_IND='N'  )
  )
/* User Running = @Variable('BOUSER') ; Document = @Variable('DOCNAME'); Query = @Variable('DPNAME') (@Variable('DPTYPE')) */