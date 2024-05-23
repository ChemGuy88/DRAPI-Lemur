# This is a (BA)SH script with examples on how to use DRAPI scripts.
# For most examples please note the use of a positional argument with value `True`.

# Load shell functions
# shellcheck source="/home/herman/.hermanCode/functions.bash"
source "/home/herman/.hermanCode/functions.bash"

# Start list of examples
# Create template directories
makeDirTemplate 0 "Path to Where you Want the Template Directory Create"

# Map OneFlorida IDs to IDR Patient IDs
mapOF2IDR_id2id.py --FILE_PATH "../../../Data Request 06 - 2024-05-17/Intermediate Results/General Portion/data/input/mpa_id_mapping_add.csv" \
                   --FILE_HEADER "UFH_ID" \
                   --FROM "OneFlorida Patient ID" \
                   --TO_VARIABLES "MRN (UF)" "MRN (Jax)" \
                   --ID_TYPE "OneFlorida Patient ID" \
                   --FIRST_TIME\
                   &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# Join OneFlorida de-identification map to OF-to-IDR map
join.py --LEFT_TABLE "../../../Data Request 06 - 2024-05-17/Intermediate Results/General Portion/data/input/mpa_id_mapping_add.csv" \
        --RIGHT_TABLE "../../../Data Request 06 - 2024-05-17/Intermediate Results/General Portion/data/output/mapOF2IDR_id2id/2024-05-23 16-28-53/OneFlorida to UF Health Patient ID Map - Final.CSV" \
        --LEFT_TABLE_INDEX "UFH_ID" \
        --RIGHT_TABLE_INDEX "OneFlorida Patient ID" \
        --HOW "outer" \
        --COLUMNS_TO_DROP "UFH_ID" \
        --FILE_EXTENSION "CSV" \
        &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using an additive function

# Replace text in files. In this example, CRLF to LF
replaceText.py -f FILEPATH -bo $'\\r\\n' -bn $'\\n'

# More examples to come!
