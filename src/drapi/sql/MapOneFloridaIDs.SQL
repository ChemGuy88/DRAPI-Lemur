	SELECT 
		a.PATID as "OneFlorida Patient ID",
		a.PATNT_KEY as "Patient Key",
		b.IDENT_ID as "MRN (UF)",
		c.IDENT_ID as "MRN (Jax)",
		d.IDENT_ID as "MRN (Pathology)"
	FROM [DWS_PCORNET].[pcnv5].[PATIENT_MAPPING] a
	left outer join [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] b on a.patnt_key = b.patnt_key and b.ident_id_type=101 and b.LOOKUP_IND = 'Y'
	left outer join [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] c on a.patnt_key = c.patnt_key and c.ident_id_type=110 and c.LOOKUP_IND = 'Y'
	left outer join [DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES] d on a.patnt_key = d.patnt_key and d.ident_id_type=99 and d.LOOKUP_IND = 'Y'
	where {PYTHON_VARIABLE: IDTypeSQL} in ( {PYTHON_VARIABLE: IDTypeValues}  )  -- Give the list of OneFlorida patient IDs