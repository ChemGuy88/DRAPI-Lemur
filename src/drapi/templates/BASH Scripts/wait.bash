#!/usr/bin/env bash

# Run a script that waits for commands to complete before moving on to the next command. This is useful when running `uploadData` because we are, apparently, allowed to run one SQL process per user.

# Setup
# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash" || exit 1

# Upload data sets to server
# Upload clinital text and their metadata to server: Portion 1
:  # Nohup job 1

echo "Waiting on job 1"
wait
echo "Waiting on job 1 - done."

# Upload clinital text and their metadata to server: Portion 2
:  # Nohup job 2
