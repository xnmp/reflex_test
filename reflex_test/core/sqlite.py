import sqlite3
import os
import pandas as pd
import numpy as np

from functools import lru_cache


def load_data():
    df = pd.read_parquet('data/dummy_data_cleaned_sample_1000.parquet')
    df = df[['CASE_RECV_S', 'pdct_catg_x', 'pdct_sub_catg_x', 'CAUS_CATG_X',
                'CAUS_SUB_CATG_X', 'CASE_SUMY_X', 'State', 'case_sumy_length', 'case_sumy_x_cleaned']]
    df = df.reset_index(drop=True)
    df.index += 1
    return df


class SQLTable:
    
    def __init__(self, df_or_path=None, text_col='CASE_SUMY_X', id_col='CASE_REFN_I', 
                 sets_of_filter_cols=[],
                 table_name='main_table', path=None):
        if isinstance(df_or_path, str):
            self.path = df_or_path
        else:
            self.path = "file::memory:?cache=shared"
            df = df_or_path
            # self.create(df, table_name, text_col, sets_of_filter_cols)
    
    @property
    def default_path(self):
        return 'data/test.db'
    
    @staticmethod
    def convert_type(t0):
        if t0 == np.dtype('O'):
            return 'TEXT'
        if t0 == np.dtype('int64'):
            return 'INTEGER'
        if t0 == np.dtype('float64'):
            return 'REAL'
        return 'TEXT'
    
    
    @lru_cache()
    def get_conn(self, path=None):
        path = self.path if path is None else path
        return sqlite3.connect(path)
    
    
    def execute(self, sql):
        conn = self.get_conn()
        conn.cursor().execute(sql)
        conn.commit()
    
    
    def create_base_table(self, df, table_name):
        
        # assert df.index.min() == 1 #since we join id to rowid later, it must start at 1
        
        create_rows = [f'{col} {self.convert_type(t0)},'  for col, t0 in df.dtypes.items()]
        create_rows_str = '\n'.join(create_rows).strip(',')    
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {create_rows_str}
        )
        """
        
        self.execute(create_sql)
    
    
    def insert_df(self, df, table_name, create=True):
        df.to_sql(table_name, self.get_conn(), if_exists='append', index=True, index_label='id')
    
    
    def create_index(self, table_name, text_col):
        create_sql = f'CREATE VIRTUAL TABLE IF NOT EXISTS "{table_name}_index" USING fts5({text_col});'
        self.execute(create_sql)
    
    
    def insert_into_index(self, table_name, text_col):
        insert_sql = f"INSERT INTO {table_name}_index SELECT {text_col} from {table_name};"
        self.execute(insert_sql)
    
    
    def create_filter_index(self, table_name, index_cols):
        index_name = '_'.join(index_cols) + '_index'
        index_sql = f"CREATE INDEX {index_name} on {table_name} ({','.join(index_cols)});"
        self.execute(index_sql)

    
    def create(self, df, table_name, text_col, sets_of_filter_cols):
        self.create_base_table(df, table_name)
        self.insert_df(df, table_name)
        self.create_index(table_name, text_col)
        self.insert_into_index(table_name, text_col)
        if sets_of_filter_cols:
            for filter_cols in sets_of_filter_cols:
                self.create_filter_index(table_name, filter_cols)
    

    def save(self, path, if_exists='replace'):
        if if_exists == 'replace' and os.path.exists(path):
            os.remove(path)
        db_disk = sqlite3.connect(path)
        self.get_conn().backup(db_disk)
        self.get_conn().close()
        self.path = path

