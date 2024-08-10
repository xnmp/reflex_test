import reflex as rx
import pandas as pd
import plotly.express as px
import plotly
from django.utils.functional import cached_property

from ..core.statefulness import Stateful, state, handler, state_var
from ..utils.clustering import add_cluster_names
from ..utils.constellation import make_constellation


class Constellation(Stateful):
    
    lower_limit = 10
    
    def __init__(self, name):
        self.name = name
        # self.text_col = text_col
    
    @state
    def _embeddings(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    
    @state_var(cached=True)
    def fig(self) -> plotly.graph_objects.Figure:
        df = self._embeddings[:]
        if len(df) == 0:
            return self.default_fig
        
        df['CASE_SUMY_X_hover'] = df['CASE_SUMY_X'].fillna('').str.wrap(65).apply(lambda x: x.replace('\n', '<br>'))
        print(df.head())
        res = make_constellation(df, hover_cols=['cluster_name','CASE_SUMY_X_hover'], tfidf=self.embedder[0], color_col='cluster', text_col='case_sumy_x_cleaned')
        return res
    
    @handler
    async def update(self) -> pd.DataFrame:
        
        df = await self.get_source('data')
        df[['embed_x','embed_y']] = self.embedder.fit_transform(df['CASE_SUMY_X'])
        
        if len(df) <= self.lower_limit:
            df['cluster'] = 1
            self._embeddings = df
            return
        
        df['cluster'] = self.clusterer.fit_predict(df[['embed_x','embed_y']])
        
        # df.loc[:self.max_fit_points - 1, 'cluster'] = self.clusterer.fit_predict(df[['embed_x','embed_y']].iloc[:self.max_fit_points])
        # if len(df) > self.max_fit_points:
        #     from utils.transforms import dbscan_predict
        #     df.loc[self.max_fit_points:, 'cluster'] = dbscan_predict(self.clusterer, df[['embed_x','embed_y']].iloc[self.max_fit_points:])
        
        df = add_cluster_names(df, tfidf=self.embedder[0], text_col='CASE_SUMY_X')
        self._embeddings= df
    
    @cached_property
    def embedder(self):
        from ..utils.transforms import default_embedder
        return default_embedder()
    
    @cached_property
    def clusterer(self):
        from daal4py.sklearn.cluster import DBSCAN
        return DBSCAN(eps=2)

    @property
    def default_fig(self):
        # TODO: use placeholder instead of default_fig
        return px.line(
            px.data.gapminder().query("country=='Canada'"),
            x="year",
            y="lifeExp",
            title="Life expectancy in Canada",
        )
    
    @property
    def element(self):
        return rx.plotly(data=self.fig, height='40vh', width='55%')

