# README

# Important considerations

The IDs in your data have a typo. The contain the ID suffix "PAT" for all ID types. This is an inconsequential typo and does not affect the quality of your data.

# Data contents

The ZIP file "2024-03-08 19-17-24.ZIP" contains the data for release:
  - Notes metadata
  - Notes text
  - OMOP-formatted electronic health records

# De-identified IDs

The de-identified ID values have the following format

[IRB_NUMBER]_[SUFFIX]_[ID_NUMBER]

where
 
  - [IRB_NUMBER] is the IRB protocol and number. In this case, it's "IRB202300703"
  - [SUFFIX] is an indication of the type of ID, one of
    - "ACCT" for account numbers.
    - "ENC" for encounter.
    - "LINK" for note linkage IDs. This is the ID that links the note text to its metadata.
    - "LOC" for location.
    - "NRAS" for 
    - "NOTE" for notes, a type of clinical text.
    - "ORD" for orders, a type of clinical text.
    - "PAT" for patients.
    - "PROV" for providers.
    - "STN" for clinical stations.
  - [ID_NUMBER] is an integer representing a real, unrevealed ID number.