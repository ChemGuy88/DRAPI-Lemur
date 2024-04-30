"""
"""

import pandas as pd
from drapi.code.drapi.expandColumn import expandColumn

DATA_DICT = {'id': {0: '123456789_1',
                    1: '123456789_2',
                    2: '123456789_2',
                    3: '123456789_3',
                    4: '123456789_1'},
             'note_text': {0: 'Specimen has been received and initial testing has been performed. However, additional testing is required to verify initial results. Final result to follow. ----------------------------------------- Performing Lab:[**LOCATION_INSTITUTE**] Performing Lab Address:[**LOCATION_STREET**], [**LOCATION_CITY**], NC, [**LOCATION_ZIP**] Performing Lab Phone:8005554344',
                           1: 'Acinetobacter baumannii Greater than 100,000 colony forming units per mL',
                           2: 'Reference Range Follicular Phase  1.9-12.5 Mid-Cycle Peak    8.7-76.3 Luteal Phase      0.5-16.9 Postmenopausal    10.0-54.7',
                           3: 'For patients >49 years of age, the reference limit for Creatinine is approximately 13% higher for people identified as African-American.',
                           4: 'Critical result(s) called to and read back by DR [**NAME**] IN ER @ 0312/TF'}}

df = pd.DataFrame.from_dict(DATA_DICT)

newTable = expandColumn(tableOrPath=df,
                        columnToSplit="id",
                        nameOfNewColumns=["id", "version"],
                        locationOfNewColumns=[0, 1],
                        splittingPattern=r"([0-9]+)_([0-9]+)",
                        logger=None)
