# This is a (BA)SH script with examples on how to use DRAPI scripts.
# For most examples please note the use of a positional argument with value `True`.

# Load shell functions
# shellcheck source="/home/herman/.hermanCode/functions.bash"
source "/home/herman/.hermanCode/functions.bash"

# Start list of examples
# Create template directories
makeDirTemplate 0 "Path to Where you Want the Template Directory Create"

# Map OneFlorida IDs to IDR Patient IDs
mapOF2IDR.py True --MAP_1_PATH "Path to OneFlorida-to-De-identified-OneFlorida IDs/filename.CSV" \
                  -FIRST_TIME True \
                  -PATIENT_KEYS_FILE_PATH "Path to File with IDR Patient IDs/filename.CSV" \
                  -MAP_1_COLUMN_NAME_FROM "Column Name from <MAP_1_PATH> that you are converting FROM"

# If you have previously downloaded the OneFlorida-to-IDR map, you can specify its path using `OLD_RUN_PATH`
mapOF2IDR.py True --MAP_1_PATH "Path to OneFlorida-to-De-identified-OneFlorida IDs/filename.CSV" \
                  -FIRST_TIME True \
                  -PATIENT_KEYS_FILE_PATH "Path to File with IDR Patient IDs/filename.CSV" \
                  -MAP_1_COLUMN_NAME_FROM "Column Name from <MAP_1_PATH> that you are converting FROM" \
                  -OLD_RUN_PATH "../../Intermediate Results/SQL Portion/data/output/mapOF2IDR/2024-03-20 14-51-32/Map 2"

# De-identify using an additive function
nohup python "code/convertColumnsHash.py" TRUE\
                                          --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [1, \"random\"],\
                                                                              \"Patient Key\": [1, \"random\"],\
                                                                              \"Provider Key\": [1, \"random\"],\
                                                                              \"Encounter Key\": [1, \"random\"],\
                                                                              \"Note Key\": [1, \"random\"],\
                                                                              \"Note ID\": [1, \"random\"],\
                                                                              \"Linkage Note ID\": [1, \"random\"],\
                                                                              \"MRN (UF)\": [1, \"random\"],\
                                                                              \"MRN (Jax)\": [1, \"random\"]}"\
                                                                              &> "logs (nohup)/$(timeStamp).out" & timeStamp


# Replace text in files. In this example, CRLF to LF
replaceText.py -f FILEPATH -bo $'\\r\\n' -bn $'\\n'

# More examples to come!