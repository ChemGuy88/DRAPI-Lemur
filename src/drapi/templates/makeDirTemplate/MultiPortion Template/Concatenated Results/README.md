# README file for IRB000000000

# Request Date: MM/DD/YYYY

# PI: 
 - ...

# Request Type:
 - Line-level

# Final Applied Inclusion Criteria:
 - ...

# Final Applied Exclusion Criteria:
 - None

# Data Elements for Release:
 - 

# Steps to Generate Data Release:
 - Run ... Portion. See its corresponding README for details.
 - Run ... Portion. See its corresponding README for details.
 - For each of the following, modify the script arguments as necessary (located in top of file), and the project arguments (located in "common.py") and then run the script:
   - "makePersonIDMap.py"
   - "convertColumns.py"
   - "getIDValues.py"
   - "makeMapsFromOthers.py"
   - "concatenateMaps.py"
   - "deIdentify.py"
   - "deleteColumns.py"
   - "gatherFiles.py"
 - Submit the output from "gatherFiles.py" to the honest broker for release

# Release to:
 - ...

# Release Files:
 - ...

# Other Notes:

## Files to use for release dated MM/DD/YYYY

File paths are relative to the common parent directory, whose absolute path is "..."

| File(s) Description                  | File(s) path or directory                                                             | Process that uses the file(s) |
| ------------------------------------ | ------------------------------------------------------------------------------------- | ----------------------------- |
| Original OMOP data set               | "IRB000000000/Intermediate Results/OMOP Portion/data/output/..."                      | makePersonIDMaps.py           |
| OMOP Person ID map                   | "IRB000000000/Concatenated Results/data/output/makePersonIDMap/.../person_id map.csv" | convertColumns.py             |
| Original OMOP data set               | "IRB000000000/Intermediate Results/OMOP Portion/data/output/..."                      | convertColumns.py             |
| Modified OMOP files                  | "IRB000000000/Concatenated Results/data/output/convertColumns/..."                    | getIDValues.py                |
| Notes metadata data set              | "IRB000000000/Intermediate Results/Notes Portion/data/output/free_text"               | getIDValues.py                |
| Notes portion de-identification maps | "IRB000000000/Intermediate Results/Notes Portion/data/output/mapping"                 | makeMapsFromOthers.py         |
| ID Sets (map intermediate files)     | "IRB000000000/Concatenated Results/data/output/getIDValues/..."                       | makeMapsFromOthers.py         |
| Notes portion de-identification maps | "IRB000000000/Intermediate Results/Notes Portion/data/output/mapping"                 | concatenateMaps.py            |
| De-identification maps               | "IRB000000000/Concatenated Results/data/output/makeMapsFromOthers/..."                | concatenateMaps.py            |
| De-identification maps               | "IRB000000000/Concatenated Results/data/output/makeMapsFromOthers/..."                | deIdentify.py                 |
| Modified OMOP files                  | "IRB000000000/Concatenated Results/data/output/convertColumns/..."                    | deIdentify.py                 |
| Notes metadata data set              | "IRB000000000/Intermediate Results/Notes Portion/data/output/free_text"               | deIdentify.py                 |
| De-identified data set               | "IRB000000000/Concatenated Results/data/output/deIdentify/..."                        | deleteColumns.py              |
| Reduced de-identified data set       | "IRB000000000/Concatenated Results/data/output/deleteColumns/..."                     | gatherFiles.py                |
| De-identified notes data set         | "IRB000000000/Intermediate Results/De-identified Notes/..."                           | gatherFiles.py                |
| Final results                        |                                                                                       | Honest broker                 |

____________________________________________________________
