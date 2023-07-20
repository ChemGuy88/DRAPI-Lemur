-- select distinct
-- 	NOTE_ENCNTR_KEY as LinkageNoteID,
-- 	dbo.fn_CleanInv(note_encntr_text) as note_text
-- from dws_prod.dbo.NOTE_ENCOUNTER_TEXT
-- where NOTE_ENCNTR_KEY in (XXXXX)
SELECT DISTINCT
	DWS_PROD.dbo.NOTE_ENCOUNTER_TEXT.NOTE_ENCNTR_KEY as LinkageNoteID,
	DWS_PROD.dbo.NOTE_ENCOUNTER_TEXT.NOTE_ENCNTR_TEXT as note_text
FROM
    dws_prod.dbo.NOTE_ENCOUNTER_TEXT
WHERE NOTE_ENCNTR_KEY in (XXXXX)
