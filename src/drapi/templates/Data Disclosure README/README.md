# README

This README provides a summary of the data released (disclosed) to you.

# Data Privacy

The main objective of the IDR is to provide patient data while respecting patient privacy. Although we do our best to de-identify data sets to the specifications of the IRB, it's possible that some personal identifiable information (PII) may leak through the de-identification process. If you detect any such information, please inform the IDR analyst who released this data to you so they can identify and correct the problem and prevent future mistakes.

# Data contents

The entirety of your data request, that is, your data set(s), are contained in the ZIP file "asdf", and are organized into the following portions:
  - Clinical text
  - Clinical text metadata
  - OMOP-formatted electronic health records
  - Other line-level (custom) data elements

# Data Quality

It's typical for IDR analysts to perform quality checks on data before its release. If your data request had any data quality issues they will be listed below with a description, and their approximate effect on your analysis (**impact**) based on our recommended course of action for you (**mitigation**).

### `ISSUE TITLE`

|                 |      |
| --------------- | ---- |
| **Impact**      | asdf |
| **Description** | asdf |
| **Mitigation**  | asdf |

# De-identified IDs

## Column names

For the sake of data quality, that is, to more easily identify errors in the data management, and de-identification processes, your data preserved the ID variable (column) name in the de-identified variable (column) name by simply appending the original name to the prefix `De-identified `. For example, the patient ID variable `Patient Key` would have been converted to `De-identified Patient Key`.

## ID formats

De-identified IDs have the format

`<PROTOCOL_NUMBER>_<SUFFIX>_<ID_NUMBER>`

where
 
  - `<PROTOCOL_NUMBER>` is the IRB protocol abbreviation and number. In this case, it's "asdf"
  - `<SUFFIX>` is an indication of the type of ID, one of
    - "ACCT" for account numbers.
    - "ENC" for encounter.
    - "LINK" for note linkage IDs. This is the ID that links a note's text to its metadata.
    - "LOC" for location.
    - "NRAS".
    - "NOTE" for notes, a type of clinical text.
    - "ORD" for orders, a type of clinical text.
    - "PAT" for patients.
    - "PROV" for providers.
    - "STN" for clinical stations.
  - `<ID_NUMBER>` is an integer representing a real, unrevealed ID. The way this value is generated is a secret, so as to preserve patient privacy.

For example, a patient's real ID may be `123456789` but it was de-identified to `IRB202001234_157073610`.

## ID numbers and placeholder values

ID numbers are non-negative integers. However, the 0-valued ID numbers have a special meaning. It is sometimes the case that there may exist negative values in the raw electronic health records. These negative values are purposely put in during the data collection process to indicate that the value is unknown, e.g., a nurse may put in `-999` to indicate that the race of a patient is unknown. The IDR usually maps these non-positive numeric values to a label of the form `<PROTOCOL_NUMBER>_<SUFFIX>_0`.

Your analysis of the data may be more accurate if you identify other such placeholder values, like `?` or `UNKNOWN`.

