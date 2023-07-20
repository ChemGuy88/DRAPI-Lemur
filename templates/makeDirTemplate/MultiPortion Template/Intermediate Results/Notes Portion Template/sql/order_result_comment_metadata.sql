SELECT distinct
	notes.ORDR_PROC_KEY as OrderKey, 
	notes.LINE as Line,
	ox.ORDR_PROC_ID as OrderID,
	op.ORDR_PLACE_DT as OrderPlacedDatetime,
	op.ORDR_RESULT_DT as OrderResultDatetime,
	ps.PATNT_KEY as PatientKey,
	pat1.IDENT_ID_INT as MRN_GNV,
	pat2.IDENT_ID_INT as MRN_JAX,	
	'order_result_comment: ' + ot.STNDRD_LABEL as NoteType,
	ped.ENCNTR_EFF_DATE as EncounterDate,
	ped.PATNT_ENCNTR_KEY as EncounterKey,
	x.ENCNTR_CSN_ID as EncounterCSN,
	prov1.PROVIDR_KEY as OrderingProviderKey,
	prov1.PROVIDR_TYPE as OrderingProviderType,
	prov1.SPCLTY_DESC as OrderingProviderSpecialty,
	prov2.PROVIDR_KEY as AuthorizingProviderKey,
	prov2.PROVIDR_TYPE as AuthorizingProviderType,
	prov2.SPCLTY_DESC as AuthorizingProviderSpecialty		
FROM 
	--order text. It is indexed by order key, which is an IDR concept.
	dws_prod.dbo.ORDER_RESULT_COMMENT AS notes
	--order ID. This is Epic concept. It can be used to link to other order information.
	LEFT OUTER JOIN dws_prod.dbo.ORDR_PROC_KEY_XREF ox on notes.ORDR_PROC_KEY = ox.ORDR_PROC_KEY
	--information about the order
	LEFT OUTER JOIN dws_prod.dbo.ORDER_PROCEDURE_DTL op ON (op.ORDR_PROC_KEY=NOTES.ORDR_PROC_KEY)
	--patient key	
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_SNAPSHOTS ps on op.PATNT_SNAPSHT_KEY = ps.PATNT_SNAPSHT_KEY
	--MRN_GNV
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_IDENTITIES pat1 on ps.PATNT_KEY=pat1.PATNT_KEY and pat1.IDENT_ID_TYPE=101 and pat1.LOOKUP_IND='Y'
	--MRN_JAX
	LEFT OUTER JOIN dws_prod.dbo.ALL_PATIENT_IDENTITIES pat2 on ps.PATNT_KEY=pat2.PATNT_KEY and pat2.IDENT_ID_TYPE=110 and pat2.LOOKUP_IND='Y'	
	--encounter date, encounter key (this is used to get CSN)
	LEFT OUTER JOIN dws_prod.dbo.PATIENT_ENCOUNTER_DTL ped on op.PATNT_ENCNTR_KEY = ped.PATNT_ENCNTR_KEY
	--encounter CSN
	LEFT OUTER JOIN dws_prod.dbo.PATNT_ENCNTR_KEY_XREF x on ped.PATNT_ENCNTR_KEY = x.PATNT_ENCNTR_KEY
	--order type
	LEFT OUTER JOIN dws_prod.dbo.ALL_ORDER_TYPES ot on (ot.ORDR_TYPE_CD_KEY=op.ORDR_TYPE_CD_KEY)	
	--ordering provider
	LEFT OUTER JOIN dws_prod.dbo.ALL_PROVIDERS prov1 ON (op.ORDR_PROVIDR_KEY=prov1.PROVIDR_KEY) 
	--autorizing provider
	LEFT OUTER JOIN dws_prod.dbo.ALL_PROVIDERS prov2 ON (op.AUTH_PROVIDR_KEY=prov2.PROVIDR_KEY)	
WHERE (ps.TEST_IND = 'N' or ps.TEST_IND is null)
and ps.PATNT_KEY in ( XXXXX ) --all Patient Keys
--and x.ENCNTR_CSN_ID in ( XXXXX ) --all CSNs
--and ped.PATNT_ENCNTR_KEY in (XXXXX) -- all Patient Encounter Keys
and ped.TEST_IND='N'
and ped.ENCNTR_EFF_DATE >= '{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_START}'
and ped.ENCNTR_EFF_DATE <= '{PYTHON_VARIABLE: SQL_ENCOUNTER_EFFECTIVE_DATE_END}'
and (ped.TEST_IND='N' or ped.TEST_IND is null)
