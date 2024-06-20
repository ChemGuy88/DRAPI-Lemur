# Test script.

# Originally from "SHANDS/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Xu/IRB202202722/Data Request 03 - 2024-04-15/Concatenated Results - v03"

# shellcheck shell=bash

timestamp=$(getTimestamp)
nohup python "/data/herman/Documents/Git Repositories/DRAPI-Lemur/src/drapi/templates/scripts/uploadData_functionless.py" \
      &> "logs (nohup)/$timestamp.out" & echo "$timestamp"
