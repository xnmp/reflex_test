import pandas as pd

def load_data():
    df = pd.read_parquet('data/dummy_data_cleaned_sample_1000.parquet')
    df = df[['CASE_RECV_S', 'pdct_catg_x', 'pdct_sub_catg_x', 'CAUS_CATG_X',
                'CAUS_SUB_CATG_X', 'CASE_SUMY_X', 'State', 'case_sumy_length', 'case_sumy_x_cleaned']]
    df = df.reset_index(drop=True)
    df.index += 1
    return df


select_cols = [
    'CASE_RECV_S', 'CASE_SUMY_X', 'State', 'case_sumy_length'
]


cat_cols = [
    'pdct_catg_x', 'pdct_sub_catg_x', 'CAUS_CATG_X', 'CAUS_SUB_CATG_X'#, 'State',
]

date_col = 'CASE_RECV_S'

text_cols = [
    'CASE_SUMY_X', 'case_sumy_x_cleaned'
]

num_cols = ['case_sumy_length']

