import sqlite3
import os
import pandas as pd
import numpy as np

from functools import lru_cache


class SQLTable:
    
    def __init__(self, df_or_path=None, 
                 text_col='CASE_SUMY_X', 
                 id_col='CASE_REFN_I', 
                 sets_of_filter_cols=[],
                 table_name='complaint', 
                 ):
        if isinstance(df_or_path, str):
            self.path = df_or_path
        else:
            self.path = "file::memory:?cache=shared"
            # self.create(df, table_name, text_col, sets_of_filter_cols)
        self.text_col = text_col
        self.id_col = id_col
        self.sets_of_filter_cols = sets_of_filter_cols
        self.table_name = table_name
    
    
    @property
    def default_path(self):
        return 'data/test.db'
    
    
    @property
    def memory_path(self):
        return 'file::memory:?cache=shared'
    
    
    @staticmethod
    def convert_type(t0):
        if t0 == np.dtype('O'):
            return 'TEXT'
        if t0 == np.dtype('int64'):
            return 'INTEGER'
        if t0 == np.dtype('float64'):
            return 'REAL'
        return 'TEXT'
    
    
    def get_conn(self):
        if self.path == self.memory_path:
            return self.get_conn_memory()
        return sqlite3.connect(self.path)
    
    
    @lru_cache()
    def get_conn_memory(self):
        return sqlite3.connect(self.memory_path)
    
    
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

        print(create_sql)
        
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


    def get_sql(self, filters=None, match_strs=None, limit=None, select='all', group_bys=None, distinct=True, order_by=None, by_relevance=False):

        if isinstance(match_strs, str):
            match_strs = [match_strs]
        if isinstance(group_bys, str):
            group_bys = [group_bys]

        if filters is None:
            filters = []
        
        if match_strs is not None and len(match_strs) > 0:
            # match_str_all = ' AND '.join([f'({ss})' for ss in match_strs])
            match_str_all = ' '.join(match_strs).strip()
            if match_str_all.startswith('AND '):
                match_str_all = match_str_all[4:]
            if match_str_all.startswith('OR '):
                match_str_all = match_str_all[3:]
            # match_subquery = f"SELECT rowid FROM {self.table_name}_index WHERE {self.table_name}_index MATCH '{match_str_all}';"
            match_filter_str = f"{self.table_name}_index MATCH '{match_str_all}'"
            filters = [match_filter_str] + filters
        
        # if sample is not None:
        #     filters.append(f'id IN (select id FROM {self.table_name} ORDER BY RANDOM() LIMIT {limit})')
        
        search_sql = f"""SELECT"""
        if distinct:
            search_sql += " DISTINCT"

        if select == 'all':
            select_str = 't.*'
        else:
            select_str = ', '.join([f't.{sel}' if sel == self.index_col else sel for sel in select])
        search_sql += f' {select_str} FROM {self.table_name} t'

        if match_strs is not None and len(match_strs) > 0:
            search_sql += f' JOIN {self.table_name}_index ft on ft.rowid = t.id'
        if len(filters) > 0:
            search_sql += ' WHERE ' + ' AND '.join(filters)

        if group_bys is not None:
            search_sql += ' GROUP BY ' + ', '.join(group_bys)
        
        orders = []
        if order_by is not None:
            if not isinstance(order_by, list):
                order_by = [order_by]
            orders += order_by
        if by_relevance and match_strs is not None and len(match_strs) > 0:
            orders += f"BM25({self.table_name}_index)"
        if len(orders) > 0:
            search_sql += f" ORDER BY {','.join(orders)}"

        if limit is not None:
            search_sql += f' LIMIT {limit}'
        
        return search_sql
    
    
    def query(self, *args, **kwargs):
        sql = self.get_sql(*args, **kwargs)
        return pd.read_sql(sql, self.get_conn())
