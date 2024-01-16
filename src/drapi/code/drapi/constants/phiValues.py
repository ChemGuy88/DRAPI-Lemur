"""
Defining standards for variables that can contain PHI. For example, some labs have text which may contain PHI, so all of these labs are removed from data sets. Another example are Zip Codes in the OMOP "observation" table.
"""

PHI_VALUES_DICT_BO = {"Lab ID": [43,
                                 1234,
                                 1235,
                                 1243,
                                 1244,
                                 1245,
                                 1248,
                                 1249,
                                 1250,
                                 1258,
                                 2188,
                                 2904,
                                 3749,
                                 5097,
                                 5098,
                                 5319,
                                 5321,
                                 5613,
                                 6542,
                                 6565,
                                 6880,
                                 6881,
                                 6891,
                                 7276,
                                 7524,
                                 7527,
                                 7530,
                                 7533,
                                 8416,
                                 10161,
                                 10211,
                                 10221,
                                 10352,
                                 10353,
                                 10354,
                                 10369,
                                 10410,
                                 10500,
                                 10683,
                                 10684,
                                 11262,
                                 11849,
                                 21031,
                                 21032,
                                 123493,
                                 123494,
                                 123496,
                                 123535,
                                 210005,
                                 1230600,
                                 1231094,
                                 1232278,
                                 1232743,
                                 1232856,
                                 1234529,
                                 1234909,
                                 1235011,
                                 1236593,
                                 1555065,
                                 1810871,
                                 1810872,
                                 1810929,
                                 1810930,
                                 1810933,
                                 1810937,
                                 1811351,
                                 2102197,
                                 2102198,
                                 12300029,
                                 12300030,
                                 12300031,
                                 12300035,
                                 12300037,
                                 12300038,
                                 12300039,
                                 12300040,
                                 12300071,
                                 12300104,
                                 12308101,
                                 12308106,
                                 12380003,
                                 12380004,
                                 12380005,
                                 12380006,
                                 12380008,
                                 12380009,
                                 12380010,
                                 12380011,
                                 12380012,
                                 12380014,
                                 12390050,
                                 12391022,
                                 21034003,
                                 123069101,
                                 123150009,
                                 123199471,
                                 210209338,
                                 210211111,
                                 210312002,
                                 210312102,
                                 210312103,
                                 210312105,
                                 210840002,
                                 210840003,
                                 210840201,
                                 1230900700,
                                 1230916170,
                                 1230916173,
                                 1231400005,
                                 1231400007,
                                 1231400009,
                                 1231400010,
                                 1231400011,
                                 1231400014,
                                 1231400016,
                                 1231400017,
                                 1231400020,
                                 1231400025,
                                 1231400031,
                                 1231400032,
                                 1231400033,
                                 1231400036,
                                 1231400045,
                                 1231400048,
                                 1231400049,
                                 1231400061,
                                 1231510356,
                                 1235000719,
                                 1235000958,
                                 1235000960,
                                 2102111114,
                                 2102111116,
                                 2103122033,
                                 2103125098,
                                 2108401011,
                                 2108401012,
                                 2108401013,
                                 2108401014,
                                 12314000666,
                                 12345655545,
                                 123031010240,
                                 123091615325,
                                 1230916123456]}

PHI_VALUES_DICT_OMOP = {"measurement_source_value": ["11546-9",
                                                     "11778-8",
                                                     "11779-6",
                                                     "13169-8",
                                                     "14869-2",
                                                     "14895-7",
                                                     "15419-5",
                                                     "15420-3",
                                                     "15421-1",
                                                     "19139-5",
                                                     "19146-0",
                                                     "19765-7",
                                                     "19767-3",
                                                     "19769-9",
                                                     "21026-0",
                                                     "21112-8",
                                                     "22638-1",
                                                     "2335-8",
                                                     "25700-6",
                                                     "32144-8",
                                                     "33882-2",
                                                     "34970-4",
                                                     "41394-8",
                                                     "42127-1",
                                                     "45374-6",
                                                     "46608-6",
                                                     "49049-0",
                                                     "49088-8",
                                                     "49296-7",
                                                     "51784-7",
                                                     "55107-7",
                                                     "55752-0",
                                                     "58445-8",
                                                     "60431-4",
                                                     "60432-2",
                                                     "61099-8",
                                                     "61100-4",
                                                     "69426-5",
                                                     "72170-4",
                                                     "72486-4",
                                                     "75218-8",
                                                     "75653-6",
                                                     "8251-1",
                                                     "8268-5",
                                                     "8269-3",
                                                     "8665-2"],
                        "observation_source_value": ["Zipcode"]}

PHI_VALUES_DICT_ALL = {}
PHI_VALUES_DICT_ALL.update(PHI_VALUES_DICT_BO)
PHI_VALUES_DICT_ALL.update(PHI_VALUES_DICT_OMOP)