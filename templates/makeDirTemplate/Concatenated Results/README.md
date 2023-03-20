# README file for IRB202001660

# Request Date: 3/10/2023

# PI: 
 - Virk, Sarah S.

# Request Type:
 - Line-level

# Final Applied Inclusion Criteria:
 - Patients with chronic kidney disease (CKD) as identified by diagnostic codes
   - ICD9: 580 to 589
   - ICD10
     - N00 to N08
     - N10 to N16
     - N17 to N19

# Final Applied Exclusion Criteria:
 - None

# Data Elements for Release:
 - Clinical notes (all notes available as of date of data request)
   - Clinical notes
   - Order narratives
   - Order impression
   - Order result comments
 - OMOP Variables. All variables available as of date of data request. See IRB data elements attachment

# Steps to Generate Data Release:
 - Run Notes Portion
 - Run OMOP Portion
 - For each of the following, modify the script arguments as necessary (located in top of file) and then run the script:
   - Run "makePersonIDMap.py"
   - Run "convertColumns.py"
   - Run "makeMaps.py"
   - Run "deIdentify.py"
   - 
   - Run "gatherFiles.py"
 - Submit the output from "gatherFiles.py" to the honest broker for release

# Release to:
 - 

# 3/10/2023 Release Files:
 - Cohort File: Virk/IRB202300505/data/file_name.csv

# Other Notes:

## Files to use as of 3/15/2023

| Description                      | Path                                                                | Script that uses it        |
| -------------------------------- | ------------------------------------------------------------------- | -------------------------- |
| person ID map                    | "data/output/makePersonIDMap/2023-03-14 12-53-37/person_id map.csv" | convertColumns.py          |
| converted OMOP files             | "data/output/convertColumns/2023-03-14 13-04-07"                    | makeMaps.py, deIdentify.py |
| ID Sets (map intermediate files) | "data/intermediate/makeMaps/2023-03-14 14-06-55"                    | makeMaps.py                |
| De-identification maps           | "data/output/makeMaps/2023-03-14 14-06-55"                          | deIdentify.py              |
| Final results                    | "data/output/deIdentify/2023-03-14 14-17-10"                        | Honest broker              |

____________________________________________________________
