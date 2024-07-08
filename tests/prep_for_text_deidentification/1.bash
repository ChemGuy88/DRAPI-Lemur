# Test

# Formatting
GRN=$'\e[0;32m'
NC=$'\e[0m'

# shellcheck shell=bash
# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash"

# Preview input data
file_path_1="data/tests/prep_for_text_deidentification/1_1.CSV"
file_path_2="data/tests/prep_for_text_deidentification/1_2.TSV"
cat "$file_path_1"
cat "$file_path_2"

# Test 1.1
echo "
${GRN}Test 1.1${NC}
"
timestamp_2="$(getTimestamp)"
prep_for_text_deidentification.py \
    --list_of_file_paths "$file_path_1" \
                         "$file_path_2" \
    --rename_columns '["New Column 1",
                       "Not Enough Columns"]' \
    --TIMESTAMP "$timestamp_2" &&
new_file_path_1="data/output/prep_for_text_deidentification/$timestamp_2/1_1.TSV" &&
new_file_path_2="data/output/prep_for_text_deidentification/$timestamp_2/1_2.TSV" &&
cat "$new_file_path_1" &&
cat "$new_file_path_2"

# Test 1.2
echo "
${GRN}Test 1.2${NC}
"
timestamp_2="$(getTimestamp)"
prep_for_text_deidentification.py \
    --list_of_file_paths "$file_path_1" \
                         "$file_path_2" \
    --rename_columns '["New Column 1",
                       "New Column 2",
                       "New Column 3",
                       "Too Many Columns"]' \
    --TIMESTAMP "$timestamp_2" &&
new_file_path_1="data/output/prep_for_text_deidentification/$timestamp_2/1_1.TSV" &&
new_file_path_2="data/output/prep_for_text_deidentification/$timestamp_2/1_2.TSV" &&
cat "$new_file_path_1" &&
cat "$new_file_path_2"

# Test 2
echo "
${GRN}Test 2${NC}
"
timestamp_2="$(getTimestamp)"
prep_for_text_deidentification.py \
    --list_of_file_paths "$file_path_1" \
                         "$file_path_2" \
    --rename_columns '["New Column 1",
                       "New Column 2",
                       "New Column 3"]' \
    --TIMESTAMP "$timestamp_2" &&
new_file_path_1="data/output/prep_for_text_deidentification/$timestamp_2/1_1.TSV" &&
new_file_path_2="data/output/prep_for_text_deidentification/$timestamp_2/1_2.TSV" &&
cat "$new_file_path_1" &&
cat "$new_file_path_2" &&

# Test 3
echo "
${GRN}Test 3${NC}
"
timestamp_2="$(getTimestamp)"
prep_for_text_deidentification.py \
    --list_of_file_paths "$file_path_1" \
                         "$file_path_2" \
    --rename_columns '{"Column 2": "New Column 2",
                       "B": "New Column B",
                       "This column doesn'\''t exist": "asdf"}' \
    --TIMESTAMP "$timestamp_2" &&
new_file_path_1="data/output/prep_for_text_deidentification/$timestamp_2/1_1.TSV" &&
new_file_path_2="data/output/prep_for_text_deidentification/$timestamp_2/1_2.TSV" &&
cat "$new_file_path_1" &&
cat "$new_file_path_2"
