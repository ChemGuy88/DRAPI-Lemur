"""
Originally from "/Volumes/SHARE/DSS/IDR Data Requests/ACTIVE RDRs/Guo/IRB202201080/code/DataPullProject" but since modified.
"""

import pandas as pd
import numpy as np

# import identified cohort file used for rapid data service


def deidentify_shift(cohort_file, data_release):
    person_id_mapping = cohort_file[['person_id']].drop_duplicates()
    person_id_mapping.reset_index(drop=True, inplace=True)
    occurrence_id_mapping = cohort_file[['visit_occurrence_id']].drop_duplicates()
    occurrence_id_mapping.reset_index(drop=True, inplace=True)
    location_id_mapping = cohort_file[['location_id']].drop_duplicates()
    location_id_mapping.reset_index(drop=True, inplace=True)
    # create a deidentified id for each patient key and keep only needed columns
    person_id_mapping['deid_num'] = person_id_mapping.index + 1
    person_id_mapping['Deidentified_ID'] = person_id_mapping.apply(lambda row: 'Pat_{}'.format(row['deid_num']), axis=1)
    person_id_mapping = person_id_mapping[['person_id', 'Deidentified_ID']]
    # create random number for date shifting between +/- 30
    if ('deidentified' in data_release):
        person_id_mapping['Shift_Num'] = np.random.randint(-30, 30, size=len(person_id_mapping))
        person_id_mapping['Shift_Num'] = pd.to_timedelta(person_id_mapping['Shift_Num'], 'd')
    # create a deidentified id for each occurrence_id and keep only needed columns
    occurrence_id_mapping['deid_num'] = occurrence_id_mapping.index + 1
    occurrence_id_mapping['Deidentified_occurrence_id'] = occurrence_id_mapping.apply(lambda row: 'occurrence_id_{}'.format(row['deid_num']), axis=1)
    occurrence_id_mapping = occurrence_id_mapping[['visit_occurrence_id', 'Deidentified_occurrence_id']]

    location_id_mapping['deid_num'] = location_id_mapping.index + 1
    location_id_mapping['Deidentified_location_id'] = location_id_mapping.apply(lambda row: 'location_id_{}'.format(row['deid_num']), axis=1)
    location_id_mapping = location_id_mapping[['location_id', 'Deidentified_location_id']]
    # output mapping files
    return person_id_mapping, occurrence_id_mapping, location_id_mapping


def shift_person_occurrence(current_file, mapping_file_location, data_release):
    mapping_file = pd.read_csv(mapping_file_location)
    id_mapping = mapping_file[['person_id', 'Deidentified_ID']].drop_duplicates()
    occurrence_mapping = mapping_file[['visit_occurrence_id', 'Deidentified_occurrence_id']].drop_duplicates()
    location_mapping = mapping_file[['location_id', 'Deidentified_location_id']]

    dfs = pd.DataFrame()
    for chunk in pd.read_csv(current_file, chunksize=50000):
        deid1 = pd.DataFrame()
        try:
            deid1 = pd.merge(id_mapping, chunk, on=['person_id'])
            deid1.drop(['person_id'], axis=1, inplace=True)
        except Exception as err:
            _ = err
            deid1 = pd.merge(location_mapping, chunk, on=['location_id'])
            deid1.drop(['location_id'], axis=1, inplace=True)
        try:
            deid1 = pd.merge(occurrence_mapping, deid1, on=['visit_occurrence_id'])
            deid1.drop(['visit_occurrence_id'], axis=1, inplace=True)
        except Exception as err:
            _ = err
            pass
        if (data_release[0] == 'deidentified'):
            date_mapping = mapping_file[['person_id', 'Shift_Num']]
            date_cols = [col for col in deid1.columns if 'date' in col]
            for i in range(len(date_cols)):
                current_column = date_cols[i]
                deid1.loc[:, current_column] = pd.to_datetime(deid1[current_column], errors='ignore')
                date_mapping.loc[:, 'Shift_Num'] = pd.to_timedelta(date_mapping['Shift_Num'])
                deid1.loc[:, current_column] = pd.to_datetime(deid1[current_column], errors='ignore') + pd.to_timedelta(date_mapping['Shift_Num'], 'd')
        dfs = dfs.append(deid1, ignore_index=False)
    return dfs


r'''
#import merged demographics file and merge again with the mapping file to a new file deidentified demographics file
print('de-identify demographics')
demographics=pd.read_csv(r'..\data_sample\demographics_fake.csv')
demo_deid=pd.merge(person_id_mapping,demographics, on='person_id')
demo_deid=pd.merge(occurrence_id_mapping,demo_deid, on='encounter_occurrence_id')
demo_deid2=demo_deid[['Deidentified_ID', 'Deidentified_occurrence_id', 'current_age', 'sex', 'race',
                'ethnicity','language']]
demo_deid2.to_csv(r'..\data_sample\de-identified\demographics_fake.csv',index=False,header=True)

#de-identify labs
print('de-identify labs')
labs=pd.read_csv(r'..\data_sample\labs_fake.csv')
labs_deid=pd.merge(person_id_mapping,labs, on='person_id')
labs_deid=pd.merge(occurrence_id_mapping,labs_deid, on='encounter_occurrence_id')
labs_deid['specimen_taken_datetime'] = pd.to_datetime(labs_deid['specimen_taken_datetime'])
labs_deid['specimen_taken_datetime_shifted'] = pd.to_datetime(labs_deid['specimen_taken_datetime']) + labs_deid['Shift_Num']
labs_deid['inferred_specimen_datetime'] = pd.to_datetime(labs_deid['inferred_specimen_datetime'])
labs_deid['inferred_specimen_datetime'] = pd.to_datetime(labs_deid['inferred_specimen_datetime']) + labs_deid['Shift_Num']
labs_deid2=labs_deid[['Deidentified_ID','Deidentified_occurrence_id','hospital','age_at_encounter','lab_order_description','lab_name','lab_result',
lab_result_numeric','lab_unit','LOINC_code','specimen_taken_datetime_shifted']]
labs_deid2.to_csv(r'..\data_sample\de-identified\labs_fake.csv',index=False,header=True)

print('END')
'''
