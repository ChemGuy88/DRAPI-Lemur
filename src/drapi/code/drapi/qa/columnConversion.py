"""
Quality Assurance functions to make sure columns were properly converted or de-identified.
"""

import logging
# Third-party packages
import pandas as pd
# First-party packages
pass

# Functions

def spotCheckColumns(listOfFiles1: list,
                     listofFiles2: list,
                     connectionString: str,
                     logger: logging.Logger,
                     moduloChunks: int,
                     chunkSize: int = 50_000,
                     messageModuloChunks: int = 50,
                     messageModuloFiles: int = 100,
                     columnsToCheck1: dict[int: str] = {0: "visit_occurrence_id",
                                                        1: "person_id",
                                                        2: "provider_id"},
                     columnsToCheck2: dict[int: str] = {0: "Encounter # (CSN)",
                                                        1: "Patient Key",
                                                        2: "Provider Key"}) -> None:
    """
    This function "spot checks" pairs of files to see if the passed variables have been properly converted from the OMOP data model to the UF Health data model.

    In `columnsToCheck1` and `columnsToCheck2` the keys of the dictionary have the following meaning:
    - 0: Encounter ID Variable Name
    - 1: Patient ID Variable Name
    - 2: Provider ID Variable Name

    The code is only meant to check these three ID types, because under the hood these integer values are mapped to SQL queries. So, for example, you could not pass `{0: "Note Key"}` to the function, because it would use the SQL query that maps encounter IDs.

    NOTE This has only been tested and verified on 3-on-3 checks. That is, checking if all three informative OMOP ID variables have been mapped to their three UF Health equivalents. The code should be able to also do spot checks for less number of variables, like just `person_id` to `Patient Key`, but it has not been tested.
    """
    with open("../Concatenated Results/sql/BO Variable Spot Check - Encounter # (CSN).sql", "r") as file:
        query0_0 = file.read()
    with open("../Concatenated Results/sql/BO Variable Spot Check - Patient Key.sql", "r") as file:
        query1_0 = file.read()
    with open("../Concatenated Results/sql/BO Variable Spot Check - Provider Key.sql", "r") as file:
        query2_0 = file.read()

    for file1, file2 in zip(listOfFiles1, listofFiles2):
        try:
            logger.info(f"""  Working on file pair:
        `file1`: "{file1}"
        `file2`: "{file2}".""")
            df2_0 = pd.read_csv(file2, nrows=2)
            df2_0columns = df2_0.columns
            columnChecks2 = df2_0columns.isin(columnsToCheck2.values())
            logger.debug(f"""  Group 2 table:\n{df2_0.to_string()}""")
            logger.debug(f"""  Group 2 columns:\n{df2_0.columns}""")
            logger.debug(f"""  Group 2 columns check:\n{columnChecks2}""")
            spot2df = df2_0.loc[0, columnChecks2]
            spot2df = pd.DataFrame(spot2df)  # For type hinting
            logger.info(f"  A row has been selected for a spot check:\n{spot2df.T.to_string()}")
            # Convert group 2 spot to group 1 values
            spot2dict = spot2df.to_dict()[0]
            logger.info(spot2dict)
            query0_1 = query0_0[:]
            query1_1 = query1_0[:]
            query2_1 = query2_0[:]
            spot1dict = {}
            if 0 in columnsToCheck2.keys():
                encounterIDVariableName = columnsToCheck2[0]
                if df2_0columns.isin([encounterIDVariableName]).sum() > 0:
                    queryEncounterIDValue = spot2dict[encounterIDVariableName]
                    query0_1 = query0_1.replace("{PYTHON_VARIABLE: Encounter # (CSN)}", str(queryEncounterIDValue))
                    result0 = pd.read_sql(sql=query0_1, con=connectionString)
                    if result0.shape != (1,2):
                        logger.warning(f"""  ..  The encounter ID mapping is not one-to-one:\n{result0.to_string()}.""")
                        spot1EncounterID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1EncounterID = result0["visit_occurrence_id"][0]
                    spot1dict["visit_occurrence_id"] = [spot1EncounterID]
            if 1 in columnsToCheck2.keys():
                patientIDVariableName = columnsToCheck2[1]
                if df2_0columns.isin([patientIDVariableName]).sum() > 0:
                    queryPatientIDValue = spot2dict[patientIDVariableName]
                    query1_1 = query1_1.replace("{PYTHON_VARIABLE: Patient Key}", str(queryPatientIDValue))
                    result1 = pd.read_sql(sql=query1_1, con=connectionString)
                    if result1.shape != (1,2):
                        logger.warning(f"""  ..  The patient ID mapping is not one-to-one:\n{result1.to_string()}.""")
                        spot1PatientID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1PatientID = result1["person_id"][0]
                    spot1dict["person_id"] = [spot1PatientID]
            if 1 in columnsToCheck2.keys():
                providerIDVariableName = columnsToCheck2[2]
                if df2_0columns.isin([providerIDVariableName]).sum() > 0:
                    queryProviderIDValue = spot2dict[providerIDVariableName]
                    query2_1 = query2_1.replace("{PYTHON_VARIABLE: Provider Key}", str(queryProviderIDValue))
                    result2 = pd.read_sql(sql=query2_1, con=connectionString)
                    if result2.shape != (1,2):
                        logger.warning(f"""  ..  The provider ID mapping is not one-to-one:\n{result2.to_string()}.""")
                        spot1ProviderID = None  # NOTE This is a dummy value assigned to the variable to allow the code to continue running, but at the same time to indicate that an unexpected or undesired result has occurred.
                    else:
                        spot1ProviderID = result2["provider_id"][0]
                    spot1dict["provider_id"] = [spot1ProviderID]
            spot1Targetdf = pd.DataFrame.from_dict(data=spot1dict, orient="columns")
            logger.info(f"""The values that we are looking for in the group 1 set of files is below:\n{spot1Targetdf}""" )
            # Chunk
            chunkGenerator1 = pd.read_csv(file1, chunksize=chunkSize, low_memory=False)
            chunkGenerator2 = pd.read_csv(file1, chunksize=chunkSize, low_memory=False)
            logger.info("    Counting the number of chunks in the file.")
            it1Total = sum([1 for _ in chunkGenerator1])
            logger.info(f"    Counting the number of chunks in the file - done. There are {it1Total:,} chunks.")
            if it1Total < messageModuloChunks:
                moduloChunks = it1Total
            else:
                moduloChunks = round(it1Total / messageModuloChunks)
            if it1Total / moduloChunks < 100:
                moduloChunks = 1
            else:
                pass
            for it1, df1Chunk in enumerate(chunkGenerator2, start=1):
                if it1 % moduloChunks == 0:
                    allowLogging = True
                else:
                    allowLogging = False
                if allowLogging:
                    logger.info(f"""  ..  Working on chunk {it1:,} of {it1Total:,}.""")
                df1Chunk = pd.DataFrame(df1Chunk)  # For type hinting
                columnChecks1 = df1Chunk.columns.isin(columnsToCheck1.values())
                df1 = df1Chunk.loc[:, columnChecks1]
                df1 = pd.DataFrame(df1)  # For type hinting
                mask = df1.isin(spot1Targetdf.values.flatten()).all(axis=1)
                rowLocation = mask.index[mask][0]
                if mask.sum() > 0:
                    spot1Hitdf = df1[mask]
                    logger.info(f"""    Found spot located at index value (row number) "{rowLocation}":\n{spot1Hitdf.to_string()}.""")
                    break
        except Exception as error:
            logger.fatal(error)