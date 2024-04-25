"""
An example of how to use the BO/SQL features of DRAPI-Lemur
"""

import logging
# Third-party packages
import pandas as pd
# First-party packages
from drapi.code.drapi.getData.getData import getData

getData(sqlFilePath="Query.SQL",
        connectionString="mssql+pymssql://USERNAME:PASSWORD@SERVER/DATABASE",
        filterVariableChunkSize=10000,
        filterVariableColumnName="Column Name",
        filterVariableData=pd.Series(),
        filterVariableFilePath=None,
        filterVariablePythonDataType="int",
        filterVariableSqlQueryTemplatePlaceholder="Placeholder Text in SQL Query File",
        logger=logging.getLogger(),
        outputFileName="Query Result Name",
        runOutputDir="My Directory",
        queryChunkSize=10000)
