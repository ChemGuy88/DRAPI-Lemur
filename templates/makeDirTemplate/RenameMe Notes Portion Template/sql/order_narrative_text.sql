select distinct
	cast(ordr_proc_key as varchar(50)) as OrderKey, 
	dbo.fn_CleanInv(ordr_narrative) as note_text
from dws_prod.dbo.ORDER_NARRATIVE
where ordr_proc_key in (XXXXX)
