SELECT distinct
	notes.NOTE_KEY as NoteKey, 
	nx.NOTE_ID as NoteID,
	b.NOTE_ENCNTR_KEY as LinkageNoteID,
	b.CNTCT_NUM as ContactNumber,
	b.CNTCT_DATE as ContactDate,
	ni.NOTE_CREATE_DT as CreatedDatetime,
	ni.NOTE_SRVC_DT as ServiceDatetime,
	ps.PATNT_KEY as PatientKey,
	pat1.IDENT_ID_INT as MRN_GNV,
	pat2.IDENT_ID_INT as MRN_JAX,	
	nt.NOTE_TYPE_DESC as NoteType,
	nt2.NOTE_TYPE_DESC as InpatientNoteType,
	ped.ENCNTR_EFF_DATE as EncounterDate,
	ped.PATNT_ENCNTR_KEY as EncounterKey,
	x.ENCNTR_CSN_ID as EncounterCSN,
	prov1.PROVIDR_KEY as AuthoringProviderKey,
	prov1.PROVIDR_TYPE as AuthoringProviderType,
	prov1.SPCLTY_DESC as AuthoringProviderSpecialty,
	prov2.PROVIDR_KEY as CosignProviderKey,
	prov2.PROVIDR_TYPE as CosignProviderType,
	prov2.SPCLTY_DESC as CosignProviderSpecialty
FROM 
	--note text. It is indexed by note key, which is an IDR concept.
	dws_prod.dbo.NOTE_ENCOUNTER_TEXT notes
	--note ID. This is Epic concept.
	LEFT OUTER JOIN dws_prod.dbo.NOTE_KEY_XREF nx ON nx.NOTE_KEY = notes.NOTE_KEY
	--note key, contact number (a.k.a. note version), note_encntr_key (a.k.a., linkage note ID) 
	LEFT OUTER JOIN dws_prod.dbo.NOTE_ENCOUNTER_INFORMATION b ON notes.NOTE_ENCNTR_KEY=b.NOTE_ENCNTR_KEY
	--dates
	LEFT OUTER JOIN dws_prod.dbo.NOTE_INFORMATION ni ON notes.NOTE_KEY = ni.NOTE_KEY
	--patient key
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_SNAPSHOTS ps ON ni.PATNT_SNAPSHT_KEY = ps.PATNT_SNAPSHT_KEY
	--MRN_GNV
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_IDENTITIES pat1 on ps.PATNT_KEY=pat1.PATNT_KEY and pat1.IDENT_ID_TYPE=101 and pat1.LOOKUP_IND='Y'
	--MRN_JAX
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_IDENTITIES pat2 on ps.PATNT_KEY=pat2.PATNT_KEY and pat2.IDENT_ID_TYPE=110 and pat2.LOOKUP_IND='Y'	
	--note type
	LEFT OUTER JOIN dws_prod.dbo.ALL_NOTE_TYPES nt ON ni.NOTE_TYPE_KEY = nt.NOTE_TYPE_KEY	
	--inpatient note type
	LEFT OUTER JOIN dws_prod.dbo.ALL_NOTE_TYPES nt2 ON nt2.NOTE_TYPE_KEY=ni.INPATNT_NOTE_TYPE_KEY
	--encounter date, encounter key (this is used to get CSN)
	LEFT OUTER JOIN dws_prod.dbo.PATIENT_ENCOUNTER_DTL ped ON ni.PATNT_ENCNTR_KEY = ped.PATNT_ENCNTR_KEY
	--encounter CSN
	LEFT OUTER JOIN dws_prod.dbo.PATNT_ENCNTR_KEY_XREF x ON ped.PATNT_ENCNTR_KEY = x.PATNT_ENCNTR_KEY 
	--authoring provider
	LEFT OUTER JOIN dws_prod.dbo.ALL_PROVIDERS prov1 ON (b.AUTHR_PROVIDR_KEY=prov1.PROVIDR_KEY)
	--cosign
	LEFT OUTER JOIN dws_prod.dbo.ALL_USERS usr ON (b.COSIGN_USER_KEY=usr.USER_KEY)
	LEFT OUTER JOIN dws_prod.dbo.ALL_PROVIDERS prov2 ON (usr.PROVIDR_KEY=prov2.PROVIDR_KEY)
WHERE (ps.TEST_IND = 'N' or ps.TEST_IND is null)
and ps.PATNT_KEY in ( XXXXX ) --all Patient Keys
--and x.ENCNTR_CSN_ID in ( XXXXX ) --all CSNs
--and ped.PATNT_ENCNTR_KEY in ( XXXXX ) -- all Patient Encounter Keys
and (ped.TEST_IND='N' or ped.TEST_IND is null)
and ped.ENCNTR_EFF_DATE >= '{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_START}'
and ped.ENCNTR_EFF_DATE <= '{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_END}'
-- and (
--  nt.NOTE_TYPE_DESC in ( 'H&P', 'Progress Note', 'Progress Notes' )  --e.g., nt.NOTE_TYPE_DESC in ( 'H&P', 'Progress Note', 'Progress Notes' )
--  or nt2.NOTE_TYPE_DESC in ( 'H&P', 'Progress Note', 'Progress Notes' )  --e.g., or nt2.NOTE_TYPE_DESC in ( 'H&P', 'Progress Note', 'Progress Notes' )
--)