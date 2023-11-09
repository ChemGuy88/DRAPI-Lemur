import pandas as pd
import os
import pymssql

base_dir = r'Z:\SHARE\DSS\IDR Data Requests\ACTIVE RDRs\Guo_Yi\IRB202100946\Intermediate Results\i2b2 Portion'  # type the path to the base_dir.
data_dir = os.path.join(base_dir, 'data')
i2b2_dir = os.path.join(data_dir, 'i2b2')
map_dir = os.path.join(data_dir, 'mapping')
disclosure_dir = os.path.join(base_dir, 'disclosure')

host = 'EDW.shands.ufl.edu'
database_prod = 'DWS_PROD'
host_i2b2 = 'idr01.shands.ufl.edu'
database_i2b2_GNV = 'I2B2LTDDATA'
database_i2b2_JAX = 'I2B2LTDDATAJAX'

cohort = 'ADSGM'  # Replace with the name of the cohort. E.g., cohort = 'subjects'
irb = 'IRB202100946'  # Replace with the IRB number. This is used in deidentification step. E.g., irb = 'IRB200001234'

# database methods for trusted connection (AD Windows authentication)


def db_connect(host, database):
    db_conn = pymssql.connect(
        host=host,
        database=database
    )
    return db_conn


def db_close(db_conn):
    db_conn.close()


def db_query(query, db_connection):
    return pd.read_sql(query, db_connection)


def db_execute_read_query(query, host, database):
    db_conn = db_connect(host, database)
    result_df = db_query(query, db_conn)
    db_close(db_conn)
    return result_df


# methods
def get_IDs():
    '''
    Get i2b2 patient IDs from patient keys.
    Assumption: patient keys are in 'Patient Key' column in cohort.csv file. The cohort.csv file is in 'data' directory.
    '''

    query = '''
	select distinct
	  a.PATIENT_IDE as 'EPIC_ID',
	  a.PATIENT_NUM as 'I2B2_PATIENT_NUM',
	  b.PATNT_KEY as 'PatientKey',
	  c.IDENT_ID as 'MRN_UF',
	  d.IDENT_ID as 'MRN_JAX'
	from dws_I2B2.dbo.PATIENT_MAPPING a
	LEFT OUTER JOIN dws_prod.dbo.all_patient_identities b ON a.patient_ide = b.patnt_id
	LEFT OUTER JOIN dws_prod.dbo.all_patient_identities c ON a.patient_ide = c.patnt_id and c.IDENT_ID_TYPE=101 and c.LOOKUP_IND='Y'
	LEFT OUTER JOIN dws_prod.dbo.all_patient_identities d ON a.patient_ide = d.patnt_id and d.IDENT_ID_TYPE=110 and d.LOOKUP_IND='Y'
	where a.patient_ide in (XXXXX )
	--where  b.PATNT_KEY in (XXXXX)
	'''
    m = 'w'
    h = True
    for chunk in pd.read_csv(os.path.join(data_dir, 'cohort.csv'), chunksize=3000):
        chunk = chunk[['EPIC Patient ID']]
        chunk = chunk.drop_duplicates()
        id = chunk['EPIC Patient ID'].tolist()
        ids = "','".join(str(x) for x in id)
        ids = "'" + ids + "'"
        query1 = query.replace('XXXXX', ids)
        result = db_execute_read_query(query1, host, database_prod)
        result = result.drop_duplicates()
        result.to_csv(os.path.join(data_dir, 'Cohort_IDs.csv'), index=False, mode=m, header=h)
        m = 'a'
        h = False


def i2b2_dump_main(source, table, cohort_dir, i2b2_dir, cohort):
    '''
    source: 'GNV' or 'JAX'. Indicates which i2b2 instance to use as the source of data.
    table: 'patient_dimension', 'visit_dimension', or observation_fact'. Indicates which table to dump.
    cohort_dir: Specifies directory where cohort file is saved.
    i2b2_dir: directory where i2b2 data will be saved.
    cohort: The name of the cohort. E.g., 'subjects'.
    '''
    h = True  # header of the output file
    m = 'w'  # mode of the output file
    counter = 0  # used only for tracking/time estimation purposes.
    # cohort should be saved in Cohort_IDs.csv file. It should contain i2b2 patient IDs in 'I2B2_PATIENT_NUM' column.
    for ids in pd.read_csv(os.path.join(cohort_dir, 'Cohort_IDs.csv'), chunksize=100):
        counter = counter + 1
        print(counter)
        ids = ids[['I2B2_PATIENT_NUM']].drop_duplicates().dropna()
        ids = ids['I2B2_PATIENT_NUM'].unique().tolist()
        ids = "','".join(str(x) for x in ids)
        ids = "'" + ids + "'"

        if (source == 'GNV'):
            database = 'I2B2LTDDATA'
        elif (source == 'JAX'):
            database = 'I2B2LTDDATAJAX'

        if (table == 'patient_dimension'):
            query = '''
            select  PATIENT_NUM,VITAL_STATUS_CD,BIRTH_DATE,DEATH_DATE,SEX_CD,AGE_IN_YEARS_NUM,LANGUAGE_CD,RACE_CD,MARITAL_STATUS_CD,RELIGION_CD,ZIP_CD,STATECITYZIP_PATH,INCOME_CD,ETHNIC_CD,PAYER_CD,SMOKING_STATUS_CD,COUNTY_CD,SSN_VITAL_STATUS_CD,MYCHART_CD,CANCER_IND
            from database.dbo.PATIENT_DIMENSION
            where PATIENT_NUM in ( XXXXX )
            '''
        elif (table == 'visit_dimension'):
            query = '''
            select
            PATIENT_NUM,ENCOUNTER_NUM,ACTIVE_STATUS_CD,START_DATE,END_DATE,INOUT_CD,LOCATION_CD,LOCATION_PATH,LENGTH_OF_STAY
            from database.dbo.VISIT_DIMENSION
            where PATIENT_NUM in ( XXXXX )
            '''
        elif (table == 'observation_fact'):
            query = '''
            select  PATIENT_NUM,ENCOUNTER_NUM,CONCEPT_CD,START_DATE,MODIFIER_CD,VALTYPE_CD,TVAL_CHAR,NVAL_NUM,VALUEFLAG_CD,QUANTITY_NUM,UNITS_CD,END_DATE,LOCATION_CD
            from database.dbo.OBSERVATION_FACT
            where PATIENT_NUM in ( XXXXX )
            '''
        query = query.replace('XXXXX', ids)
        query = query.replace('database', database)
        if (source == 'GNV'):
            result = db_execute_read_query(query, host_i2b2, database_i2b2_GNV)
        elif (source == 'JAX'):
            result = db_execute_read_query(query, host_i2b2, database_i2b2_JAX)
        result = result.drop_duplicates()
        file = cohort + '_' + table + '_' + source + '.csv'
        result.to_csv(os.path.join(i2b2_dir, file), mode=m, header=h, index=False)
        h = False
        m = 'a'
    print("i2b2 dump {} {} completed".format(table, source))
    return


def generate_patient_map(map_dir, cohort_dir):
    pat = pd.read_csv(os.path.join(cohort_dir, 'Cohort_IDs.csv'))
    pat_map = pat[['PatientKey']].drop_duplicates()
    pat_map = pat_map.reset_index()
    pat_map['deid_num'] = pat_map.index + 1
    pat_map['deid_pat_ID'] = pat_map.apply(lambda row: str(irb) + '_PAT_' + str(int(row['deid_num'])), axis=1)
    pat = pd.merge(pat, pat_map, how='left', on='PatientKey')
    pat.to_csv(os.path.join(map_dir, 'map_patient.csv'), index=False)
    return


def generate_encounter_map_i2b2(map_dir, i2b2_dir):
    # GNV
    in_file = cohort + '_visit_dimension_GNV.csv'
    df = pd.read_csv(os.path.join(i2b2_dir, in_file))
    df = df[['ENCOUNTER_NUM']].drop_duplicates()
    df1 = pd.DataFrame()
    in_file = cohort + '_observation_fact_GNV.csv'
    for chunk in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        chunk = chunk[['ENCOUNTER_NUM']].drop_duplicates()
        df1 = pd.concat([df1, chunk])
        df1 = df1.drop_duplicates()
    df = pd.concat([df, df1])
    df = df.drop_duplicates()
    df = df.reset_index()
    df['deid_num'] = df.index + 1
    df['deid_enc_ID'] = df.apply(lambda row: str(irb) + '_ENC_' + str(int(row['deid_num'])), axis=1)
    df['source'] = 'GNV'
    size = df.shape[0]
    # JAX
    in_file = cohort + '_visit_dimension_JAX.csv'
    df2 = pd.read_csv(os.path.join(i2b2_dir, in_file))
    df2 = df2[['ENCOUNTER_NUM']].drop_duplicates()
    df1 = pd.DataFrame()
    in_file = cohort + '_observation_fact_JAX.csv'
    for chunk in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        chunk = chunk[['ENCOUNTER_NUM']].drop_duplicates()
        df1 = pd.concat([df1, chunk])
        df1 = df1.drop_duplicates()
    df2 = pd.concat([df2, df1])
    df2 = df2.drop_duplicates()
    df2 = df2.reset_index()
    df2['deid_num'] = df2.index + 1 + size
    df2['deid_enc_ID'] = df2.apply(lambda row: str(irb) + '_ENC_' + str(int(row['deid_num'])), axis=1)
    df2['source'] = 'JAX'
    # concatenate GNV and JAX
    df = pd.concat([df, df2])
    df.to_csv(os.path.join(map_dir, 'map_encounter.csv'), index=False)
    return


def generate_mappings():
    generate_patient_map(map_dir, data_dir)
    generate_encounter_map_i2b2(map_dir, i2b2_dir)
    return


def lds_i2b2(map_dir, i2b2_dir, disclosure_dir_i2b2):
    lds_i2b2_patient_dim(map_dir, i2b2_dir, disclosure_dir_i2b2)
    lds_i2b2_visit_dim(map_dir, i2b2_dir, disclosure_dir_i2b2)
    lds_i2b2_observation_fact(map_dir, i2b2_dir, disclosure_dir_i2b2)
    return


def lds_i2b2_patient_dim(map_dir, i2b2_dir, disclosure_dir_i2b2):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), index=False)
    # GNV
    in_file = cohort + '_patient_dimension_GNV.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = df[['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), header=False, index=False, mode='a')
    print("deidentified GNV patient dimension")
    # JAX
    in_file = cohort + '_patient_dimension_JAX.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = df[['deid_pat_ID', 'VITAL_STATUS_CD', 'BIRTH_DATE', 'DEATH_DATE', 'SEX_CD', 'AGE_IN_YEARS_NUM', 'LANGUAGE_CD', 'RACE_CD', 'MARITAL_STATUS_CD', 'RELIGION_CD', 'ZIP_CD', 'STATECITYZIP_PATH', 'INCOME_CD', 'ETHNIC_CD', 'PAYER_CD', 'SMOKING_STATUS_CD', 'COUNTY_CD', 'SSN_VITAL_STATUS_CD', 'MYCHART_CD', 'CANCER_IND']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'patient_dimension.csv'), header=False, index=False, mode='a')
    print("deidentified JAX patient dimension")
    return


def lds_i2b2_visit_dim(map_dir, i2b2_dir, disclosure_dir_i2b2):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    map_enc = pd.read_csv(os.path.join(map_dir, 'map_encounter.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), index=False)
    # GNV
    in_file = cohort + '_visit_dimension_GNV.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), header=False, index=False, mode='a')
    print("deidentified GNV visit dimension")
    # JAX
    in_file = cohort + '_visit_dimension_JAX.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'ACTIVE_STATUS_CD', 'START_DATE', 'END_DATE', 'INOUT_CD', 'LOCATION_CD', 'LOCATION_PATH', 'LENGTH_OF_STAY']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'visit_dimension.csv'), header=False, index=False, mode='a')
    print("deidentified JAX visit dimension")
    return


def lds_i2b2_observation_fact(map_dir, i2b2_dir, disclosure_dir_i2b2):
    map_pat = pd.read_csv(os.path.join(map_dir, 'map_patient.csv'))
    map_enc = pd.read_csv(os.path.join(map_dir, 'map_encounter.csv'))
    df = pd.DataFrame(columns=['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD'])
    df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), index=False)
    # GNV
    in_file = cohort + '_observation_fact_GNV.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = df[df['PATIENT_NUM'] != 'PATIENT_NUM']
        df['PATIENT_NUM'] = df['PATIENT_NUM'].astype(int)
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), header=False, index=False, mode='a')
    print("deidentified GNV observation fact")
    # JAX
    in_file = cohort + '_observation_fact_JAX.csv'
    for df in pd.read_csv(os.path.join(i2b2_dir, in_file), chunksize=10000):
        df = df.drop_duplicates()
        df = df[df['PATIENT_NUM'] != 'PATIENT_NUM']
        df['PATIENT_NUM'] = df['PATIENT_NUM'].astype(int)
        df = pd.merge(df, map_pat, how='left', left_on='PATIENT_NUM', right_on='I2B2_PATIENT_NUM')
        df = pd.merge(df, map_enc, how='left', on='ENCOUNTER_NUM')
        df = df[['deid_pat_ID', 'deid_enc_ID', 'CONCEPT_CD', 'START_DATE', 'MODIFIER_CD', 'VALTYPE_CD', 'TVAL_CHAR', 'NVAL_NUM', 'VALUEFLAG_CD', 'QUANTITY_NUM', 'UNITS_CD', 'END_DATE', 'LOCATION_CD']]
        df.to_csv(os.path.join(disclosure_dir_i2b2, 'observation_fact.csv'), header=False, index=False, mode='a')
    print("deidentified JAX observation fact")
    return


def limited_data_set():
    lds_i2b2(map_dir, i2b2_dir, disclosure_dir)
    return


## MAIN ##
if __name__ == '__main__':
    print('START')
    # generate i2b2 patient IDs
    get_IDs()

    # i2b2 dump
    if (not os.path.exists(i2b2_dir)):  # i2b2 dump will be saved in 'i2b2' subdirectory of 'data' folder.
        os.makedirs(i2b2_dir)
    i2b2_dump_main('GNV', 'patient_dimension', data_dir, i2b2_dir, cohort)  # Pull data from patient_dimension in GNV i2b2 instance.
    i2b2_dump_main('JAX', 'patient_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('GNV', 'visit_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('JAX', 'visit_dimension', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('GNV', 'observation_fact', data_dir, i2b2_dir, cohort)
    i2b2_dump_main('JAX', 'observation_fact', data_dir, i2b2_dir, cohort)

    # prepare limited data set for disclosure
    if (not os.path.exists(map_dir)):  # mappings for patient IDs and encounter IDs will be saved in 'mapping' subdirectory of 'data' folder.
        os.makedirs(map_dir)
    generate_mappings()
    if (not os.path.exists(disclosure_dir)):  # limited data set of i2b2 dump will be saved in 'disclosure' directory.
        os.makedirs(disclosure_dir)
    limited_data_set()
    print('END')
