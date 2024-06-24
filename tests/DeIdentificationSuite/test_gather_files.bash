# Tests for `gather_files`

# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash"

# Test 1
timestamp="$(getTimestamp)"
destination_folder="data/output/$timestamp"
nohup python "src/scripts/resultsConcatenation/gather_files.py" \
             --destination_folder "$destination_folder" \
             --list_of_directories "data/tests/gatherFiles/Portion 1" \
             "data/tests/gatherFiles/Portion 2" \
             "data/tests/gatherFiles/Portion 3" \
             --list_of_loose_files "data/tests/gatherFiles/example loose file 1.text" \
             --list_of_directories_new_names "A" "B" "C" \
             --create_merged_folder True \
             --create_compressed_archive True \
             --overwrite_if_exists_archive False \
             --overwrite_if_exists_file False \
             --overwrite_if_exists_folder False \
             --delete_folder_after_archiving False \
      &> "logs (nohup)/$timestamp.out" & echo "$timestamp"
sleep 2

# Test 2
timestamp="$(getTimestamp)"
destination_folder="data/output/$timestamp"
mkdir -p "$destination_folder" && 
nohup python "tests/DeIdentificationSuite/test_gather_files.py" \
             --destination_folder "$destination_folder" \
             --list_of_directories "data/tests/gatherFiles/Portion 1" \
             "data/tests/gatherFiles/Portion 2" \
             "data/tests/gatherFiles/Portion 3" \
             --list_of_loose_files "data/tests/gatherFiles/example loose file 1.text" \
             --list_of_directories_new_names "A" "B" "C" \
             --create_merged_folder True \
             --create_compressed_archive True \
             --overwrite_if_exists_archive False \
             --overwrite_if_exists_file False \
             --overwrite_if_exists_folder False \
             --delete_folder_after_archiving False \
      &> "logs (nohup)/$timestamp.out" & echo "$timestamp"
sleep 2

# Test 3
timestamp="$(getTimestamp)"
destination_folder="data/output/$timestamp"
mkdir -p "$destination_folder" && 
nohup python "tests/DeIdentificationSuite/test_gather_files.py" \
             --destination_folder "$destination_folder" \
             --list_of_directories "data/tests/gatherFiles/Portion 1" \
             "data/tests/gatherFiles/Portion 2" \
             "data/tests/gatherFiles/Portion 3" \
             --list_of_loose_files "data/tests/gatherFiles/example loose file 1.text" \
             --list_of_directories_new_names "A" "B" "C" \
             --create_merged_folder True \
             --create_compressed_archive True \
             --overwrite_if_exists_archive False \
             --overwrite_if_exists_file False \
             --overwrite_if_exists_folder True \
             --delete_folder_after_archiving False \
      &> "logs (nohup)/$timestamp.out" & echo "$timestamp"
sleep 2
