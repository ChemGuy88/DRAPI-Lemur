#!/bin/bash

# This is a summary of the steps done to fulfill the data request.
# De-identify using encryption function: Clinical Text - Notes
nohup "convertColumnsHash.py" "Intermediate Results/Clinical Text De-identification/data/output/Unzipped Files/"note_* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="Clinical Text - Notes" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Linkage Note ID\": [3, \"random\"]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --CUSTOM_ALIASES="{\"id\": \"Linkage Note ID\"}" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: Clinical Text - Orders
nohup "convertColumnsHash.py" "Intermediate Results/Clinical Text De-identification/data/output/Unzipped Files/"order_!(result*) \
                              "Intermediate Results/Notes Portion/data/output/expandColumns/YYYY-MM-DD hh-mm-ss/"order_result_comment_*.tsv \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="Clinical Text - Orders" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Order Key\": [3, \"random\"]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --CUSTOM_ALIASES="{\"id\": \"Order Key\"}" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: Clinical Text Metadata
nohup "convertColumnsHash.py" "Intermediate Results/Notes Portion/data/output/freeText/YYYY-MM-DD hh-mm-ss/free_text/"FlaDia_*[0-9].csv \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="Clinical Text Metadata" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [3, \"random\"],\
                                                                  \"Encounter Key\": [3, \"random\"],\
                                                                  \"Linkage Note ID\": [3, $SECRET_VALUE_3],\
                                                                  \"MRN (Jax)\": [3, \"random\"], \
                                                                  \"MRN (UF)\": [3, \"random\"],\
                                                                  \"Note ID\": [3, \"random\"],\
                                                                  \"Note Key\": [3, \"random\"],\
                                                                  \"Order ID\": [3, \"random\"],\
                                                                  \"Order Key\": [3, $SECRET_VALUE_9],\
                                                                  \"Patient Key\": [3, \"random\"],\
                                                                  \"Provider Key\": [3, \"random\"]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: OMOP
nohup "convertColumnsHash.py" "Intermediate Results/OMOP Portion/data/output/YYYY-MM-DD hh-mm-ss/identified/"* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="OMOP" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"person_id\": [3, \"random\"],\
                                                                  \"provider_id\": [3, \"random\"],\
                                                                  \"visit_occurrence_id\": [3, \"random\"]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: Smoking - At Encounter
nohup "convertColumnsHash.py" "Intermediate Results/BO Portion/data/output/script/YYYY-MM-DD hh-mm-ss/Smoking - At Encounter"* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="GAD Labs, Smoking History, and Zip Codes" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [3, $SECRET_VALUE_1],\
                                                                  \"Encounter Key\": [3, $SECRET_VALUE_2],\
                                                                  \"Linkage Note ID\": [3, $SECRET_VALUE_3],\
                                                                  \"MRN (Jax)\": [3, $SECRET_VALUE_4], \
                                                                  \"MRN (UF)\": [3, $SECRET_VALUE_5],\
                                                                  \"Note ID\": [3, $SECRET_VALUE_6],\
                                                                  \"Note Key\": [3, $SECRET_VALUE_7],\
                                                                  \"Order ID\": [3, $SECRET_VALUE_8],\
                                                                  \"Order Key\": [3, $SECRET_VALUE_9],\
                                                                  \"Patient Key\": [3, $SECRET_VALUE_10],\
                                                                  \"Provider Key\": [3, $SECRET_VALUE_11]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: Smoking - Social Hx Detail
nohup "convertColumnsHash.py" "Intermediate Results/BO Portion/data/output/script/YYYY-MM-DD hh-mm-ss/Smoking - Social Hx Detail"* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="GAD Labs, Smoking History, and Zip Codes" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [3, $SECRET_VALUE_1],\
                                                                  \"Encounter Key\": [3, $SECRET_VALUE_2],\
                                                                  \"Linkage Note ID\": [3, $SECRET_VALUE_3],\
                                                                  \"MRN (Jax)\": [3, $SECRET_VALUE_4], \
                                                                  \"MRN (UF)\": [3, $SECRET_VALUE_5],\
                                                                  \"Note ID\": [3, $SECRET_VALUE_6],\
                                                                  \"Note Key\": [3, $SECRET_VALUE_7],\
                                                                  \"Order ID\": [3, $SECRET_VALUE_8],\
                                                                  \"Order Key\": [3, $SECRET_VALUE_9],\
                                                                  \"Patient Key\": [3, $SECRET_VALUE_10],\
                                                                  \"Provider Key\": [3, $SECRET_VALUE_11]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: Zip Codes
nohup "convertColumnsHash.py" "Intermediate Results/BO Portion/data/output/script/YYYY-MM-DD hh-mm-ss/Zip Codes"* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="GAD Labs, Smoking History, and Zip Codes" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [3, $SECRET_VALUE_1],\
                                                                  \"Encounter Key\": [3, $SECRET_VALUE_2],\
                                                                  \"Linkage Note ID\": [3, $SECRET_VALUE_3],\
                                                                  \"MRN (Jax)\": [3, $SECRET_VALUE_4], \
                                                                  \"MRN (UF)\": [3, $SECRET_VALUE_5],\
                                                                  \"Note ID\": [3, $SECRET_VALUE_6],\
                                                                  \"Note Key\": [3, $SECRET_VALUE_7],\
                                                                  \"Order ID\": [3, $SECRET_VALUE_8],\
                                                                  \"Order Key\": [3, $SECRET_VALUE_9],\
                                                                  \"Patient Key\": [3, $SECRET_VALUE_10],\
                                                                  \"Provider Key\": [3, $SECRET_VALUE_11]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# De-identify using encryption function: GAD Labs
nohup "convertColumnsHash.py" "Intermediate Results/BO Portion/data/output/script/YYYY-MM-DD hh-mm-ss"/* \
                              --IRB_NUMBER="IRB123456789" \
                              --PORTION_NAME="GAD Labs, Smoking History, and Zip Codes" \
                              --DICTIONARY_OF_MAPPING_ARGUMENTS="{\"Encounter # (CSN)\": [3, $SECRET_VALUE_1],\
                                                                  \"Encounter Key\": [3, $SECRET_VALUE_2],\
                                                                  \"Linkage Note ID\": [3, $SECRET_VALUE_3],\
                                                                  \"MRN (Jax)\": [3, $SECRET_VALUE_4], \
                                                                  \"MRN (UF)\": [3, $SECRET_VALUE_5],\
                                                                  \"Note ID\": [3, $SECRET_VALUE_6],\
                                                                  \"Note Key\": [3, $SECRET_VALUE_7],\
                                                                  \"Order ID\": [3, $SECRET_VALUE_8],\
                                                                  \"Order Key\": [3, $SECRET_VALUE_9],\
                                                                  \"Patient Key\": [3, $SECRET_VALUE_10],\
                                                                  \"Provider Key\": [3, $SECRET_VALUE_11]}" \
                              --BY="file"\
                              --SCRIPT_TEST_MODE="False" \
                              --USE_DEFAULT_ALIASES="True"\
                              &> "logs (nohup)/$(getTimestamp).out" & getTimestamp


# Delete OMOP columns
nohup python code/deleteColumns.py&> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# Make IDR to OMOP ID maps: Find all metadata directories
find "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/convertColumnsHash" -type d -name "Maps by Portion"
# Make IDR to OMOP ID maps: Combine de-identification maps
nohup qaDeidentification.py -m 1 \
                            -c "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Metadata/Maps by Portion"/* \
                            --DEFAULT_ALIASES \
                            --PANDAS_ENGINE "pyarrow" \
                            &> "logs (nohup)/$(getTimestamp).out" & getTimestamp

# Make IDR to OMOP ID maps: Join IDR and OMOP maps: Encounters
nohup map_deid2deid.py --LEFT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/Encounter # (CSN).CSV" \
                       --RIGHT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/visit_occurrence_id.CSV" \
                       --LEFT_VARIABLE_NAME "Encounter # (CSN)" \
                       --RIGHT_VARIABLE_NAME "visit_occurrence_id" \
                       --SQL_FILE_PATH "sql/OMOP to UFH Map - Encounters.SQL" \
                       --SQL_FILE_PLACEHOLDER "{PYTHON_VARIABLE: Encounter # (CSN)}" \
                       --OUTPUT_FILE_NAME "OMOP to UFH Map - Encounters" \
                       --STANDARDIZE_COLUMN_NAMES \
                       --DROP_NA_HOW "any" \
                       --FIRST_TIME\
                       &> "logs (nohup)/$(getTimestamp).out" & getTimestamp
                    #    --LEFT_VARIABLE_NAME_ALIAS "EncounterCSN" \

# Make IDR to OMOP ID maps: Join IDR and OMOP maps: Patients
nohup map_deid2deid.py --LEFT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/Patient Key.CSV" \
                       --RIGHT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/person_id.CSV" \
                       --LEFT_VARIABLE_NAME "Patient Key" \
                       --RIGHT_VARIABLE_NAME "person_id" \
                       --SQL_FILE_PATH "sql/OMOP to UFH Map - Patients.SQL" \
                       --SQL_FILE_PLACEHOLDER "{PYTHON_VARIABLE: Patient Key}" \
                       --OUTPUT_FILE_NAME "OMOP to UFH Map - Patients" \
                       --STANDARDIZE_COLUMN_NAMES \
                       --DROP_NA_HOW "any" \
                       --FIRST_TIME\
                       &> "logs (nohup)/$(getTimestamp).out" & getTimestamp
                    #    --LEFT_VARIABLE_NAME_ALIAS "Patient Key" \

# Make IDR to OMOP ID maps: Join IDR and OMOP maps: Providers
nohup map_deid2deid.py --LEFT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/Provider Key.CSV" \
                       --RIGHT_DEIDENTIFICATION_MAP_PATH "../../Data Request X - YYYY-MM-DD/Concatenated Results/data/output/qaDeidentification/YYYY-MM-DD hh-mm-ss/Combined Maps/By Variable/provider_id.CSV" \
                       --LEFT_VARIABLE_NAME "Provider Key" \
                       --RIGHT_VARIABLE_NAME "provider_id" \
                       --SQL_FILE_PATH "sql/OMOP to UFH Map - Providers.SQL" \
                       --SQL_FILE_PLACEHOLDER "{PYTHON_VARIABLE: Provider Key}" \
                       --OUTPUT_FILE_NAME "OMOP to UFH Map - Providers" \
                       --STANDARDIZE_COLUMN_NAMES \
                       --DROP_NA_HOW "any" \
                       --FIRST_TIME\
                       &> "logs (nohup)/$(getTimestamp).out" & getTimestamp
                    #    --LEFT_VARIABLE_NAME_ALIAS "AuthoringProviderKey" \

# Symlink results: Clinical Text, Clinical Text Metadata, OMOP
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/Clinical Text - Notes"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$(pwd)/data/Data for Release - Symlinks/Clinical Text/$(basename "{}")"'
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/Clinical Text - Orders"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$(pwd)/data/Data for Release - Symlinks/Clinical Text/$(basename "{}")"'
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/Clinical Text Metadata"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$(pwd)/data/Data for Release - Symlinks/Clinical Text Metadata/$(basename "{}")"'
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/OMOP"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$(pwd)/data/Data for Release - Symlinks/OMOP/$(basename "{}")"'

# Symlink results: GAD Labs, Smoking History, and Zip Codes: Smoking History - At Encounter
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/GAD Labs, Smoking History, and Zip Codes"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "data/Data for Release - Symlinks/Data/GAD Labs, Smoking History, and Zip Codes/$(basename "{}")"'
# Symlink results: GAD Labs, Smoking History, and Zip Codes: Smoking History - Social Hx Detail
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/GAD Labs, Smoking History, and Zip Codes"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "data/Data for Release - Symlinks/Data/GAD Labs, Smoking History, and Zip Codes/$(basename "{}")"'
# Symlink results: GAD Labs, Smoking History, and Zip Codes: Zip Codes
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/GAD Labs, Smoking History, and Zip Codes"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "data/Data for Release - Symlinks/Data/GAD Labs, Smoking History, and Zip Codes/$(basename "{}")"'
# Symlink results: GAD Labs, Smoking History, and Zip Codes: GAD Labs
ls "data/output/convertColumnsHash/YYYY-MM-DD hh-mm-ss/Portions/GAD Labs, Smoking History, and Zip Codes"/* | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "data/Data for Release - Symlinks/Data/GAD Labs, Smoking History, and Zip Codes/$(basename "{}")"'

# Symlink results: OMOP to UF Health maps
ln -sv "Data Request X - YYYY-MM-DDIRB123456789/Data Request X - YYYY-MM-DD/Concatenated Results/data/output/map_deid2deid/YYYY-MM-DD hh-mm-ss/Encounter # (CSN) to visit_occurrence_id.CSV" "data/Data for Release - Symlinks/Metadata/Encounter # (CSN) to visit_occurrence_id.CSV"
ln -sv "Data Request X - YYYY-MM-DDIRB123456789/Data Request X - YYYY-MM-DD/Concatenated Results/data/output/map_deid2deid/YYYY-MM-DD hh-mm-ss/Patient Key to person_id.CSV" "Data Request X - YYYY-MM-DDIRB123456789/Data Request X - YYYY-MM-DD/Concatenated Results/data/Data for Release - Symlinks/Metadata/Patient Key to person_id.CSV"
ln -sv "Data Request X - YYYY-MM-DDIRB123456789/Data Request X - YYYY-MM-DD/Concatenated Results/data/output/map_deid2deid/YYYY-MM-DD hh-mm-ss/Provider Key to provider_id.CSV" "Data Request X - YYYY-MM-DDIRB123456789/Data Request X - YYYY-MM-DD/Concatenated Results/data/Data for Release - Symlinks/Metadata/Provider Key to provider_id.CSV"

# Gather files
nohup python code/gatherFiles.py&> "logs (nohup)/$(getTimestamp).out" & getTimestamp
