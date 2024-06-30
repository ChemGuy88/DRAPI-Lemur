#!/usr/bin/env bash

# Remove data and log files based on completed `nohup` logs
# NOTE - ASUMPTIONS
# Runs from different programs do not have the same name or timestamp.
# Dotfiles are not included in glob expansion.
# Data and log directories have a fixed depth.
# NOTE - TODO
# Sort the contents of `all_files_to_check` by the parent directory, and display like in `tree`.

# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash" || exit 1

# Formatting
GRN=$'\e[0;32m'
RED=$'\e[0;31m'
NC=$'\e[0m'

usage0() {
    cat <<USAGE
This script moves "data" and "log" files to a ".TRASH" folder if their corresponding \`nohup\` logs are not found in the "logs (nohup)" directory.

"$(basename "$0")" -t [t|T[rue]]|[f|F[alse]]

    -t \`test_mode\`, a boolean argument {T[RUE], F[ALSE]}. Case in-sensitive.
USAGE
}
usage() {
    usage0 1>&2
    exit 1
}

while getopts ":t:" opt; do
    case "${opt}" in
        t) test_mode=${OPTARG};;
        *) usage;;
    esac
done
shift $((OPTIND -1))

# >>> Argument confirmation >>>
# `test_mode`
shopt -s nocasematch &&
if [[ "$test_mode" =~ (t|true) ||  "$test_mode" =~ (f|false) ]]; then
    if [[ "$test_mode" =~ (t|true) ]]; then
        test_mode_="true"
    elif [[ "$test_mode" =~ (f|false) ]]; then
        test_mode_="false"
    else
        echo "This should not happen"
        exit 1
    fi
else
    invalid_arguments=1
fi &&
shopt -u nocasematch 

echo "The value of the argument 'test_mode' is '$test_mode'"

if [[ "$invalid_arguments" == 1 ]]; then
    echo "${RED}You provided invalid arguments.${NC}"
    usage
fi
# <<< Argument confirmation <<<

# set constants
current_working_directory="$(pwd)"
echo "\`current_working_directory\`: \"$current_working_directory\""

# Assert there is a valid `nohup` logs directory
nohup_logs_directory="$current_working_directory/logs (nohup)"
if [[ -d "$nohup_logs_directory" ]]; then
    :
else
    echo "The directory \"logs (nohup)\" was not found in your current working directory."
    exit 1
fi

# Collect completed `nohup` logs
completed_jobs_array=()
for file_path in "$nohup_logs_directory"/*;
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
shopt -u dotglob  # Make sure we do not include dotfiles in our glob expansion.
shopt -s nullglob  # Make glob return nulls instead of its literal self if it matches no patterns.
list_of_paths_logs=("$dir_path_logs"/*/*)
list_of_paths_data_intermediate=("$dir_path_data_intermediate"/*/*)
list_of_paths_data_output=("$dir_path_data_output"/*/*)
shopt -u nullglob
all_files_to_check=()
all_files_to_check+=("${list_of_paths_logs[@]}")
all_files_to_check+=("${list_of_paths_data_intermediate[@]}")
all_files_to_check+=("${list_of_paths_data_output[@]}")

files_to_remove=()
echo "
The complete collection of data directories and log files for all runs are below. ${RED}RED${NC} items will be deleted. ${GRN}Green${NC} items will be not be deleted."
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

trash_folder_path="$current_working_directory/.TRASH"

# User confirmation
read -r -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

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
    if [[ "$test_mode_" == "true" ]]; then
        echo "mv \"$file_path\" \"$to_dir\""
    else
        # mv "$file_path" "$to_dir"
        :
    fi
    echo ""
done
