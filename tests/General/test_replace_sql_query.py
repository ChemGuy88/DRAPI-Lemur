"""
Test `replace_sql_query`
"""

import logging

from drapi.code.drapi.drapi import replace_sql_query

q1 = """\
-- This is sample query 1
SELECT
    A.*
FROM
    -- This is a comment
    [SERVER].[DATABASE].[SCHEMA].[TABLE] AS A
"""

q2 = """\
-- This is sample query 2
SELECT
    A.COLUMN_1,
    -- A.COLUMN_2,  -- We like to comment-out things.
    A.COLUMN_3,
FROM
    [SERVER].[DATABASE].[SCHEMA].[TABLE] AS A
"""

q2 = """\
-- This is sample query 2
SELECT
    A.COLUMN_1,
    -- A.COLUMN_2,  -- We like to comment-out things.
    A.COLUMN_3,
FROM
    [SERVER].[DATABASE].[SCHEMA].[TABLE] AS A
WHERE
    A.COLUMN_1 in (XXXXX)  -- Filter by column 1
    -- A.COLUMN_2 in (XXXXX)  -- Filter by column 2
"""

q12 = replace_sql_query(query=q1,
                        old="",
                        new="",
                        logger=logging.Logger())
