import numpy as np
import pandas as pd
import dash
import datetime as dt
from pytictoc import TicToc
from icecream import ic
from dash.dependencies import Output, Input
from django.utils.functional import cached_property, classproperty
from dash.exceptions import PreventUpdate
from frozendict import frozendict

from components.filters_components import FilterDict
from core.db_data import SQLData, ChromaData, LanceData
from components.sumy_table import DashTable
from components.misc import NoMatchModal
from core.dash_object_abc import PandasData, Callback, InputArgsMixin
from utils.helpers import session_property, group_means


class FilteredData(InputArgsMixin, SQLData):
    
    cols = DashTable.display_columns + ['case_sumy_x_cleaned', 'IS_CASE_SUMY_HIDDEN']

    def get_input_args(self, filter_data: FilterDict, *args, **kwargs):
        return (self.deps['filters'].to_input_args(filter_data),)

    def update_data(self, query_data, *args, cols=None, **kwargs):

        cols = cols or self.cols
        
        # TODO: the below is prob redundant
        # if len(query_data['filters']) == 0 and len(query_data['match_strs']) == 0:
        #     print("FilteredData: Using default data")
        #     from instantiate import df
        #     return df
        
        df = self.table.search(select=cols, order_by='orderid', **query_data, **kwargs)

        return df


class SampleFilteredData(FilteredData, LanceData):
    
    def __init__(self, name, vectordb=None, table=None):
        super().__init__(name)
        self.vectordb = vectordb
        self.table = table
    
    def update(self, *args, **kwargs):
        self.input_args = self.get_input_args(*args, **kwargs)
        return PandasData.update(self, *args, **kwargs)


    def get_input_args(self, filter_data, sample_size, by_relevance, user):
        return (self.deps['filters'].to_input_args(filter_data), sample_size, user is None)


    @InputArgsMixin.memoize
    def update_data(self, filter_data, sample_size, by_relevance, user):
        print("Updating SampleFilteredData...")
        query_data = self.to_sql_strings(filter_data)
        res = FilteredData.update_data(self, query_data, cols=self.cols, limit=sample_size, by_relevance=by_relevance)
        if user is None:
            mask = res['IS_CASE_SUMY_HIDDEN'] == 1
            res.loc[mask, 'CASE_SUMY_X'] = '***HIDDEN***'
            res.loc[mask, 'case_sumy_x_cleaned'] = ''
        res = res.drop(columns=['IS_CASE_SUMY_HIDDEN'])
        return res
    
    
    @Callback(
        inputs = lambda x:[
            x.deps['login_modal'].input(),
            # x.deps['similarity'].input('n_clicks', suffix='submit'),
            x.deps['filters'].input(),
            x.deps['sample_size_slider'].input(),
            x.deps['relevance_switch'].input(),
            x.deps['rstr'].input('data', suffix='current_user'),
        ],
        # states = lambda x: [
        #     x.deps['similarity'].state('value'),
        #     x.deps['similarity'].state('value', suffix='ref'),
        #     x.deps['similarity'].state('value', suffix='slider'),
        # ]
    )
    def callback_update(self, is_not_logged_in, *args):
        if is_not_logged_in:
            from inspect import signature
            n_args = len(signature(self.get_input_args).parameters) - 1
            self.input_args = [None] * n_args
            return dash.no_update
        return self.update(*args)


class EmbeddingData(InputArgsMixin, PandasData):
    # sequence is callback_update -> update -> update_data -> calculate
    max_fit_points = 5000

    def get_input_args(self, df, stop_words):
        base_data_args = self.deps['base_data'].input_args #includes sample size
        if base_data_args is None:
            base_data_args = []
        if stop_words is None:
            stop_words = []

        return tuple(list(base_data_args) + [tuple(stop_words)])

    # @lru_cache
    @InputArgsMixin.memoize
    def update_data(self, df, stop_words, *args, **kwargs):

        # if len(df) < NoMatchModal.min_size:
        #     raise PreventUpdate()
        
        if stop_words is not None:
            from utils.helpers import _remove_stopwords
            try:
                df = df.assign(**{self.text_col: df[self.text_col].apply(lambda x: _remove_stopwords(x, stop_words))})
            except:
                a = 1

        df = self.calculate(df)
        # ic(df.head())
        return df
    
    def calculate(self, df, lower_limit=10):

        if not df.empty:
            embeddings = self.embedder.fit_transform(df[self.text_col].iloc[:self.max_fit_points])
        else:
            embeddings = np.array([])
        if len(df) > self.max_fit_points:
            embeddings2 = self.embedder.transform(df[self.text_col].iloc[self.max_fit_points:])
            embeddings = np.concatenate([embeddings, embeddings2])

        if len(df) <= lower_limit:
            df['cluster'] = 1
        else:
            df['cluster'] = self.clusterer.fit_predict(embeddings)
    
        res = self.add_cluster_names(df)
        return res
    
    
    @Callback(inputs=['base_data', 'stop_word_box', lambda x: x.deps['cluster_options'].algorithm_input, Input('top_tables', 'is_open')],
              prevent_initial_call=True)
    def callback_update(self, df, stop_words, algorithm_control, is_open, *args, **kwargs):
        if algorithm_control != 'kmeans' or not is_open or df is None:
            self.input_args = self.get_input_args(df, stop_words)
            return dash.no_update
        # TODO: shouldn't need this because it'll just be defined as part of StateData or PandasData itself
        print(f"{self.__class__.__name__}: Callback Update")
        tt = TicToc()
        tt.tic()
        res = self.update(df, stop_words, *args, **kwargs)
        tt.toc(f' * Finished Update for {self.__class__.__name__}')
        # ic("Embeddings", self.data)
        return res

    # below is all copied from data_store.embeddingData
    def __init__(self, name, text_col, **pipe_args):
        super().__init__(name)
        self.text_col = text_col

    @session_property
    def embedder(self):
        from utils.transforms import base_text_embedder
        return base_text_embedder()
    
    @cached_property
    def clusterer(self):
        from sklearn.cluster import KMeans
        return KMeans(10, n_init='auto')
    
    def get_cluster_names(self, df, top_n=5, cluster_col='cluster', tfidf=None, text_col=None):
        
        tfidf = tfidf or self.embedder[0]
        text_col = text_col or self.text_col

        tfidfs0 = tfidf.transform(df[text_col])
        top_tfidfs = group_means(tfidfs0, 
                                 df[cluster_col], 
                                 feature_names=tfidf.get_feature_names_out(), 
                                 top_n=top_n)
        top_tfidfs = top_tfidfs.set_index(['group','word'])['value']
        res = top_tfidfs.reset_index().groupby('group')['word'].agg(list)
        return res.apply('_'.join).reset_index().set_axis([cluster_col, f'{cluster_col}_name'], axis='columns')
    
    def add_cluster_names(self, df, *args, **kwargs):
        # need to preserve the order of df, otherwise when the text visualizer takes the first 5000 they'll all be the same cluster
        # can merge like the below but it is slower
        # df = df.reset_index().merge(self.get_cluster_names(df)).sort_values('index').drop(columns='index')
        cluster_names = self.get_cluster_names(df, *args, **kwargs)
        cluster_names = {rec['cluster']: rec['cluster_name'] for rec in cluster_names.to_records()}
        df['cluster_name'] = df['cluster'].apply(cluster_names.get)
        return df


class TSNEEmbeddingData(EmbeddingData):

    cluster_args = {'eps': 2}

    def get_input_args(self, df, stop_words, *args):
        return super().get_input_args(df, stop_words)
    
    @Callback(inputs=['base_data','stop_word_box', lambda x: x.deps['cluster_options'].algorithm_input, Input('top_tables', 'is_open')])
    def callback_update(self, *args, **kwargs):
        print(f"{self.__class__.__name__}: Callback Update")
        tt = TicToc()
        tt.tic()
        res = self.update(*args, **kwargs)
        tt.toc(f' * Finished Update for {self.__class__.__name__}')
        return res
    
    @classproperty
    def default_input_args(cls):
        return (frozendict(), 500, False, '', '', None, tuple())

    def calculate(self, df):
        import os
        import joblib
        self.embedder = self.fitted_embedder(df.iloc[:self.max_fit_points])
        df[['embed_x','embed_y']] = self.embedder.transform(df[self.text_col])
        df = self.add_clusters(df)
        df = self.add_cluster_names(df)
        
        if self.input_args == self.default_input_args:
            # print("Loading saved models and embeddings")
            embedder_path = 'data/saved_embedder_500.pkl'
            clusterer_path = 'data/saved_clusterer_500.pkl'
            embeddings_path = 'data/saved_embeddings_500.parquet'

            if os.path.exists(embedder_path) and os.path.exists(clusterer_path) and os.path.exists(embeddings_path):
                self.embedder = joblib.load(embedder_path)
                self.clusterer = joblib.load(clusterer_path)
                return pd.read_parquet(embeddings_path)
            else:
                joblib.dump(self.embedder, embedder_path)
                joblib.dump(self.clusterer, clusterer_path)
                df.to_parquet(embeddings_path)

        return df
    
    def add_clusters(self, df, lower_limit=10):
        embeddings = df[['embed_x','embed_y']]
        if len(df) <= lower_limit:
            df['cluster'] = 1
            return df
        df.loc[:self.max_fit_points - 1, 'cluster'] = self.clusterer.fit_predict(embeddings.iloc[:self.max_fit_points])
        if len(df) > self.max_fit_points:
            from utils.transforms import dbscan_predict
            df.loc[self.max_fit_points:, 'cluster'] = dbscan_predict(self.clusterer, embeddings.iloc[self.max_fit_points:])
        return df
    
    def update(self, df, stop_words, algorithm_control, is_open):
        # TODO: move this check to callback_update
        if algorithm_control != 'tsne' or not is_open:
            self.input_args = self.get_input_args(df, stop_words)
            return dash.no_update
        return super().update(df, stop_words)

    @session_property
    def embedder(self):
        from utils.transforms import text_embedder
        return text_embedder()
    
    @InputArgsMixin.memoize
    def fitted_embedder(self, df, *args, **kwargs):
        # self.memoized['fitted_embedder'] only contains fitted embedders
        # so if self.input args isn't in the keys, then the current embedder hasn't been fitted
        # test to see whether this is working: go 500 -> 750 -> back to 500 -> trend selected -> 750
        res = self.embedder_copy()
        # tt = TicToc()
        # tt.tic()
        # print(f"Fitting embedder for {len(df)} points...")
        res.fit(df[self.text_col])
        # tt.toc(' * Done Fitting')
        return res
    
    def embedder_copy(self):
        from copy import deepcopy
        orig = self.embedder
        res = deepcopy(orig)
        if hasattr(orig[-1], 'embedding_'):
            for key, value in orig[-1].embedding_.__dict__.items():
                setattr(res[-1].embedding_, key, value)
        return res
    
    @cached_property
    def clusterer(self):
        # doesn't have to be session specific since it's stateless
        try: 
            from daal4py.sklearn.cluster import DBSCAN
            
        except ImportError:
            from sklearn.cluster import DBSCAN
        
        return DBSCAN(**self.cluster_args)

class TrendlineData(SQLData):
    
    # time aggregated filtered data
    # time aggregated full data (DATE_COUNTS_TOTAL) - just another instance with no deps, and which only gets run once
    # also very slow

    def update_data(self, query_data, active_tab):

        ic("Trendlinedata", query_data, active_tab)

        if active_tab != 'trend_tabs':
            return dash.no_update
        
        # need a groupby here:
        # aggregation in pandas is actually almost as fast
        select_cols = ['CASE_RECV_S', 'COUNT(DISTINCT CASE_REFN_I)']
        df = self.table.search(select=select_cols, group_bys=['CASE_RECV_S'], **query_data)
        df['CASE_RECV_S'] = df['CASE_RECV_S'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))
        ic(df.head())
        return df


class SelectedData(PandasData):

    def update_data(self, embeddings, selected_range, selected_cluster, active_tab):

        # print('---------Updating selected data')

        # if active_tab == 'cluster_view' and ctx.triggered_id == self.deps['embeddings'].id:
        #     # if the active tab is cluster view, then the callback will trigger again when the embeddings updates the selected cluster
        #     # so cancel one of the triggers
        #     return dash.no_update
        
        # print("Embedding Size for selected data:", len(embeddings))
        res = self.deps['selected_cluster'].filter(embeddings, selected_cluster)

        # from icecream import ic
        # ic("selected_range", res.head())
        
        if not selected_range:
            return res
        
        xmin, xmax = selected_range['x']
        ymin, ymax = selected_range['y']

        def get_range(df):
            return df[
                (df['embed_x'] >= xmin) & (df['embed_x'] <= xmax)
                & (df['embed_y'] >= ymin) & (df['embed_y'] <= ymax)
            ]

        res = get_range(res)

        # print('Selection Size:', len(res))

        return res
    
    @Callback(inputs=['embeddings', 'constellation','selected_cluster'], states=['active_tab'])
    def callback_update(self, *args, **kwargs):
        return super().update(*args, **kwargs)
