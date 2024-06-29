# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash"

# Replace text: "<NULL-BYTE>" with b"\x00"
timestamp_2="$(getTimestamp)"
replace_text.py \
    --list_of_file_paths "../../Data Request 03 - 2024-04-15/Concatenated Results - v03/data/test.TSV" \
    --old_text "<NULL-BYTE>" \
    --new_text_bytes "\x00" \
    --as_bytes "true" \
    --TIMESTAMP "$timestamp_2"\
