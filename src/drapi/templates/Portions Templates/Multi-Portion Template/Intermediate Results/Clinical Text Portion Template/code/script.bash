# Expand ID column for Clinical Text - Order Result Comment
nohup expandColumns.py --PATHS order_result_comment_*.tsv \
                 --COLUMN_TO_SPLIT "id" \
                 --NAME_OF_NEW_COLUMNS "Order Key" "LINE" \
                 --LOCATION_OF_NEW_COLUMNS 0 1 \
                 --SPLITTING_PATTERN '([0-9]+)_([0-9]+)' \
                 &>"logs (nohup)/$(getTimestamp).out"& getTimestamp
