# Journal

This is a lab journal with notes about the IDR

## i2b2 Portion Template

For IRB202100946 I created two auxilairy scripts for de-identifying i2b2 data sets
- i2b2MakeMap, which really just concatenates files
- i2b2GetIDs, which is not needed if you use the output of the `get_IDs` function in the i2b2 portion.

## IDR Virtual Environments

Commonly used Python packages
    - IPython
    - pandas
    - pymssql
    - SQLAlchemy

## SQL Surprises

The following are interesting or useful SQL tidbits.

### Average numberof note per patients

```SQL
-- COUNT THE NUMBER OF NOTE ENCOUNTER KEYS PER PATIENT. THE NOTE ENCOUNTER KEY IDENTIFIES THE UNIQUE TEXT

SELECT DISTINCT
	APS.PATNT_KEY AS 'Patient Key',
	COUNT (NEI.NOTE_ENCNTR_KEY) AS 'COUNT NOTE_ENCNTR_KEY (AKA "Linkage Note ID")'
INTO
	#Counts
FROM 
	DWS_PROD.dbo.ALL_PATIENT_SNAPSHOTS AS APS
	LEFT OUTER JOIN DWS_PROD.dbo.NOTE_INFORMATION AS NI ON APS.PATNT_SNAPSHT_KEY = NI.PATNT_SNAPSHT_KEY
	LEFT OUTER JOIN DWS_PROD.dbo.NOTE_ENCOUNTER_INFORMATION AS NEI ON NEI.NOTE_KEY = NI.NOTE_KEY
WHERE
	(APS.TEST_IND = 'N' or APS.TEST_IND IS NULL)
GROUP BY
	APS.PATNT_KEY

-- VIEW COUNTS

SELECT
	*
FROM
	#Counts
ORDER BY
	[COUNT NOTE_ENCNTR_KEY (AKA "Linkage Note ID")] DESC

-- GET THE AVERAGE NUMBER OF NOTE ENCOUNTER KEYS PER PATIENT, FOR VALID PATIENT KEYS

SELECT
	AVG(CAST([COUNT NOTE_ENCNTR_KEY (AKA "Linkage Note ID")] AS INT)) AS 'AVERAGE `NOTE_ENCNTR_KEY` PER Patient Key'
FROM
	#Counts
WHERE
	#Counts.[Patient Key] > 0
```

### Note types

There are four clinical note types.
    1. Notes
    2. Order Impressions
    3. Order Narratives
    4. Order Result Comments

These four note types themselves are categorized into two types
    1. Notes
    2. Orders

The identifier for the note texts corresponds to these types

| Note Type | Note Identifier |
| --------- | --------------- |
| Notes     | Linkage Note ID |
| Orders    | Order Key       |

A detailed list of note and order types can be found by using the following query.

```SQL
USE DWS_PROD
SELECT DISTINCT
	NOTE_TYPE_KEY,
	NOTE_TYPE,
	NOTE_TYPE_DESC
FROM
	dws_prod.dbo.ALL_NOTE_TYPES nt
ORDER BY
	NOTE_TYPE

SELECT DISTINCT
	ORDR_TYPE_CD_KEY,
	ORDR_TYPE_CD,
	ORDR_TYPE_CD_DESC
FROM
	dws_prod.dbo.ALL_ORDER_TYPES
ORDER BY
	ORDR_TYPE_CD
```

### How to search schemas, tables, and columns.

```SQL
-- SELECT CLARITY COLUMNS, TABLES, AND SCHEMAS THAT MENTION A KEYWORD

SELECT s.name AS 'Schema Name'
      ,t.name AS 'Table Name'
      ,c.name AS 'Column Name'
FROM
	CLARITYSQLPROD.CLARITY.sys.tables t
	JOIN CLARITYSQLPROD.CLARITY.sys.schemas s ON t.schema_id = s.schema_id
	JOIN CLARITYSQLPROD.CLARITY.sys.columns c ON t.object_id = c.object_id
WHERE
	s.name LIKE '%KEYWORD%'
	OR
	t.name LIKE '%KEYWORD%'
ORDER BY
	s.name,
	t.name,
	c.name
```

### ID Type Codes

```SQL
USE DWS_PROD
SELECT
	DISTINCT(IDENT_ID_TYPE),
	IDENT_ID_TYPE_DESC
FROM
	[DWS_PROD].[dbo].[ALL_PATIENT_IDENTITIES]
ORDER BY
	IDENT_ID_TYPE
```

```
IDENT_ID_TYPE	IDENT_ID_TYPE_DESC
-1000	NERVE PATIENT ID
0	ENTERPRISE ID NUMBER
14	MODEL SYSTEM MRN
99	EXTERNAL PATHOLOGY MR
101	UFP MRN
102	AGH MRN
103	CORP ID
104	LIVE OAK MRN
105	LAKESHORE MRN
106	REHAB MRN
107	STARKE MRN
108	VISTA MRN
109	IDX PAT ID
110	JACKSONVILLE MRN
111	UNIVERSITY OF FLORIDA ID
112	SIEMENS REHAB MRN
113	SIEMENS VISTA MRN
114	SIEMENS UF MRN
115	SIEMENS AGH MRN
116	SIEMENS LSH MRN
117	SIEMENS LOAK MRN
118	SIEMENS STK MRN
120	UFJP MRN
150	SELECT HOSPITAL MRN
151	ELLKAY INTERFACED CLIENT SITE MRN
170	ELLKAY CARE EVOLVE (UFHPL) INTERFACED CLIENT SITE MRN
181	HALIFAX MRN
200	CF CORP ID
201	LEESBURG MRN
202	VILLAGES MRN
203	LB MR
204	VL MR
205	UFPTI MRN
31001	XVIVO ORGAN
```
