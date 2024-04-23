source "/home/herman/.hermanCode/functions.bash"

# De-identify using an additive function: Clinical Text
nohup python "code/convertColumnsHash.py" FALSE \
                                          "../../Notes Portion/data/output/freeText/$DATE_TIME_TIMESTAMP/free_text"/FlaDia_*/!(deid*) \
                                          --PORTION_NAME="Clinical Text" \
                                          --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [1, \"random\"],\
                                                                              \"Encounter Key\": [1, \"random\"],\
                                                                              \"Linkage Note ID\": [1, \"random\"],\
                                                                              \"MRN (Jax)\": [1, \"random\"], \
                                                                              \"MRN (UF)\": [1, \"random\"],\
                                                                              \"Note ID\": [1, \"random\"],\
                                                                              \"Note Key\": [1, \"random\"],\
                                                                              \"Order ID\": [1, \"random\"],\
                                                                              \"Order Key\": [1, \"random\"],\
                                                                              \"Patient Key\": [1, \"random\"],\
                                                                              \"Provider Key\": [1, \"random\"]}" \
                                          --BY="file"\
                                          &> "logs (nohup)/$(timeStamp).out" & timeStamp

# De-identify using an additive function, with previous secrets: Clinical Text Metadata
nohup python "code/convertColumnsHash.py" FALSE \
                                          "../../Notes Portion/data/output/freeText/$DATE_TIME_TIMESTAMP/free_text"/FlaDia_*[0-9].csv \
                                          --PORTION_NAME="Clinical Text Metadata" \
                                          --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [1, $SECRET_1],\
                                                                              \"Encounter Key\": [1, $SECRET_1],\
                                                                              \"Linkage Note ID\": [1, $SECRET_1],\
                                                                              \"MRN (Jax)\": [1, $SECRET_1], \
                                                                              \"MRN (UF)\": [1, $SECRET_1],\
                                                                              \"Note ID\": [1, $SECRET_1],\
                                                                              \"Note Key\": [1, $SECRET_1],\
                                                                              \"Order ID\": [1, $SECRET_1],\
                                                                              \"Order Key\": [1, $SECRET_1],\
                                                                              \"Patient Key\": [1, $SECRET_1],\
                                                                              \"Provider Key\": [1, $SECRET_1]}" \
                                          --BY="file"\
                                          &> "logs (nohup)/$(timeStamp).out" & timeStamp

# De-identify using an additive function: OMOP
nohup python "code/convertColumnsHash.py" FALSE \
                                          "../../OMOP Portion/data/output/$DATE_TIME_TIMESTAMP/identified"/* \
                                          --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"visit_occurrence_id\": [1, \"random\"],\
                                                                              \"person_id\": [1, \"random\"],\
                                                                              \"provider_id\": [1, \"random\"]}" \
                                          --PORTION_NAME="OMOP" \
                                          --BY="file"\
                                          &> "logs (nohup)/$(timeStamp).out" & timeStamp

# QA: De-identification
# QA: De-identification: Combine and test the de-identification maps from `convertColumnsHash.py` - Clinical Text Portion
nohup python code/qaDeIdentification.py -m 1 \
                                        -c "$PATH_TO_DEIDENTIFIED_CLINICAL_TEXT_PORTION"\
                                        &> "logs (nohup)/$(timeStamp).out" & timeStamp

# QA: De-identification: Combine and test the de-identification maps from `convertColumnsHash.py` - Clinical Text Metadata Portion
nohup python code/qaDeIdentification.py -m 1 \
                                        -c "$PATH_TO_DEIDENTIFIED_CLINICAL_TEXT_METADATA_PORTION"\
                                        &> "logs (nohup)/$(timeStamp).out" & timeStamp

# QA: De-identification: Combine and test the de-identification maps from `convertColumnsHash.py` - OMOP Portion
nohup python code/qaDeIdentification.py -m 1 \
                                        -c "$PATH_TO_DEIDENTIFIED_OMOP_PORTION"\
                                        &> "logs (nohup)/$(timeStamp).out" & timeStamp

# QA: De-identification: Combine combined maps and test them.
nohup python code/qaDeIdentification.py -m 2 \
                                        -c "$PATH_TO_COMBINED_MAPS_CLINICAL_TEXT_PORTION"/* \
                                        "$PATH_TO_COMBINED_MAPS_CLINICAL_TEXT_PORTION"/* \
                                        "$PATH_TO_COMBINED_MAPS_CLINICAL_TEXT_METADATA_PORTION"/* \
                                        --DEFAULT_ALIASES\
                                        &> "logs (nohup)/$(timeStamp).out" & timeStamp

# Delete columns
python code/deleteColumns.py&> "logs (nohup)/$(timeStamp).out" & timeStamp

# Symlink Portions
# Symlink Portions: Clinical Text
ls "$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT" | xargs -I {} ln -s "$(pwd)/$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT/{}" "disclosure/Portion Symlinks/Clinical Text/$(basename {})"
# Symlink Portions: Clinical Text Metadata
ls "$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT" | xargs -I {} ln -s "$(pwd)/$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT/{}" "disclosure/Portion Symlinks/Clinical Text Metadata/$(basename {})"
# Symlink Portions: OMOP
ls "$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT" | xargs -I {} ln -s "$(pwd)/$RELATIVE_PATH_TO_DEIDENTIFIED_CLINICAL_TEXT/{}" "disclosure/Portion Symlinks/OMOP/$(basename {})"

# Gather files
nohup python code/gatherFiles.py\
      &> "logs (nohup)/$(timeStamp).out" & timeStamp

# Create OMOP-EPIC map for encounters, patients, and providers


