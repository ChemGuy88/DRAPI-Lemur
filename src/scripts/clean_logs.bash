#!/usr/bin/env bash

# Remove data and log files based on completed `nohup` logs
# NOTE - ASUMPTIONS
# Runs from different programs do not have the same name or timestamp.
# Dotfiles are not included in glob expansion.
# Data and log directories have a fixed depth.
# NOTE - DEVELOPMENT
# You can remove commented code after initial commit.

# Formatting
GRN=$'\e[0;32m'
RED=$'\e[0;31m'
NC=$'\e[0m'

# set constants
current_working_directory="$(pwd)"
echo "\`current_working_directory\`: \"$current_working_directory\""

# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash" || exit 1

# Collect completed `nohup` logs
completed_jobs_array=()
for file_path in "$current_working_directory/logs (nohup)"/*;
do
    file_name="$(basename -- "$file_path")"
    run_name="${file_name%.*}"
    completed_jobs_array+=("$run_name")
done

# Display completed run names
echo "The completed jobs are below:"
for completed_job in "${completed_jobs_array[@]}";
do
    echo " - \"$completed_job\""
done

# Display run names to remove
dir_path_logs="$current_working_directory/logs"
dir_path_data_intermediate="$current_working_directory/data/intermediate"
dir_path_data_output="$current_working_directory/data/output"
# dir_path_array=("$dir_path_logs" \
#                 "$dir_path_data_intermediate" \
#                 "$dir_path_data_output")
shopt -u dotglob  # Make sure we do not include dotfiles in our glob expansion.
list_of_paths_logs=("$dir_path_logs"/*/*)
list_of_paths_data_intermediate=("$dir_path_data_intermediate"/*/*)
list_of_paths_data_output=("$dir_path_data_output"/*/*)
all_files_to_check=()
all_files_to_check+=("${list_of_paths_logs[@]}")
all_files_to_check+=("${list_of_paths_data_intermediate[@]}")
all_files_to_check+=("${list_of_paths_data_output[@]}")

files_to_remove=()
echo "
The complete collection of data directories and log files for all runs are below:"
for file_path in "${all_files_to_check[@]}";
do
    file_name="$(basename -- "$file_path")"
    run_name="${file_name%.*}"
    if [[ ${completed_jobs_array[*]} =~ $run_name ]];
    then
        # Keep file
        echo " - ${GRN}$run_name${NC}"
    else
        # Remove file
        echo " - ${RED}$run_name${NC}"
        files_to_remove+=("$file_path")
    fi
done

# # Recreate directory structure in trash folder: build paths
# echo "
# Recreate directory structure in trash folder: build paths"
# trash_folder_paths_array=()
trash_folder_path="$current_working_directory/.TRASH"
# for dir_path in "${dir_path_array[@]}";
# do
#     echo "  \`dir_path\`: \"$dir_path\""
#     dir_relative_path="$(realpath -s --relative-to="$trash_folder_path" "$dir_path")"
#     tree_limb="${dir_relative_path##}"
#     echo "    \`dir_relative_path\`: \"$dir_relative_path\""
#     tree_limb="${dir_relative_path/"../"/}"  # HACK
#     echo "    \`tree_limb\`: \"$tree_limb\""
#     trash_sub_dir="$trash_folder_path/$tree_limb"
#     echo "    \`trash_sub_dir\`: \"$trash_sub_dir\""
#     trash_folder_paths_array+=("$trash_sub_dir")
#     echo ""
# done

# # Recreate directory structure in trash folder: make directories
# echo "
# Recreating directory structure in trash folder: make directories."
# for dir_path in "${trash_folder_paths_array[@]}";
# do
#     echo "  Working on \`dir_path\`: \"$(realpath --relative-to="$current_working_directory" "$dir_path")\""
#     if [ -d "$dir_path" ];
#     then
#         echo "    Directory exists."
#     else
#         echo "    Creating directory."
#         mkdir -p "$dir_path"
#     fi
# done

# User confirmation
read -pr "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

# Trash files and folders
echo "
The following files and folders will be trashed:"
for file_path in "${files_to_remove[@]}";
do
    echo "  \"$file_path\""
    dir_relative_path="$(realpath -s --relative-to="$trash_folder_path" "$file_path")"
    tree_limb="${dir_relative_path##}"
    echo "    \`dir_relative_path\`: \"$dir_relative_path\""
    tree_limb="${dir_relative_path/"../"/}"  # NOTE HACK
    echo "    \`tree_limb\`: \"$tree_limb\""
    to_path="$trash_folder_path/$tree_limb"
    to_dir="$(dirname -- "$to_path")"
    mkdir -p "$to_dir"
    echo "    \`to_path\`: \"$to_path\""
    # mv "$file_path" "$to_dir"
    echo ""
done
