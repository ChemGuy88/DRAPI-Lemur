select distinct
	cast(ordr_proc_key as varchar(50)) as OrderKey, 
	LINE as LINE,
	dbo.fn_CleanInv(ordr_result_comment) as note_text
from dws_prod.dbo.ORDER_RESULT_COMMENT
where ordr_proc_key in (XXXXX)
