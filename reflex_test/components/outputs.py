from ..core.statefulness import Stateful, state, state_var, handler

import pandas as pd
import plotly.express as px
import reflex as rx
import plotly

from typing import List, Dict, Any


class DisplayTable(Stateful):
    
    def __init__(self, name, filter_objs, table):
        self.name = name
        self.table = table
        self.filter_objs = filter_objs
    
    @state
    def query_args(self) -> Dict[str, List[str]]:
        # note: really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
        return {}
    
    @state_var(cached=True)
    def data(self) -> pd.DataFrame:
        print("SQL:", self.table.get_sql(**self.query_args, limit=10))
        return self.table.query(**self.query_args, limit=10)#, select=[''])
    
    @state_var(cached=True)
    def display_data(self) -> List[List[Any]]:
        res = self.data
        if len(res) > 5:
            res = res.sample(5)
        for col in self.display_columns:
            res[col] = res[col].astype(str)
        res = res[self.display_columns].values.tolist()
        return res
    
    @property
    def display_columns(self):
        return ['CASE_RECV_S', 'CASE_SUMY_X', 'State', 'case_sumy_length']
    
    @handler
    async def update_query_args(self):
        states = [await self.get_state(filter_obj.State) for filter_obj in self.filter_objs]
        res = {}
        for state in states:
            for k, v in state.query_args.items():
                res[k] = res.get(k, []) + v
        self.query_args = res
    
    @property
    def element(self):
        button = rx.button(
            rx.icon(tag='play'), "Update Data",
            on_click=self.update_query_args,
            variant="outline", color="green",
        )
        return rx.vstack(
            self.table_element,
            button,
        )

    @property
    def column_defs(self) -> List[Dict[str, Any]]:
        res = []
        for col in self.display_columns:
            res0 = {'name': col, 'sort':True} #for base rx.data_table
            if col in 'CASE_SUMY_X':
                res0['width'] = 800
            res.append(res0)
        return res
    
    @property
    def table_element(self):
        _element = rx.data_table(
            columns=self.column_defs,
            data=self.display_data,
            # resizable=True,
        )
        return rx.box(_element, max_height="50vh", overflow='auto')


class Embeddings(Stateful):
    
    @state_var(cached=True)
    def embeddings(self) -> pd.DataFrame:
        calculate_embeddings = NotImplemented
        res = self.data
        res['embed_x','embed_y'] = calculate_embeddings(res['CASE_SUMY_X'])
        return self.data


class Constellation(Stateful):
    
    def __init__(self, name):
        self.name = name
        # self.text_col = text_col
    
    @state
    def fig(self) -> plotly.graph_objects.Figure:
        df = px.data.gapminder().query("country=='Canada'")
        fig =px.line(
            df,
            x="year",
            y="lifeExp",
            title="Life expectancy in Canada",
        )
        fig.update_layout(height=500)
        return fig
    
    @property
    def element(self):
        return rx.plotly(data=self.fig, height='35vh')


class WordFreqBar(Stateful):
    
    @state
    def words(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    @property
    def element(self):
        data = {
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Values': [20, 14, 23, 25, 22]
        }
        df = pd.DataFrame(data)

        # Create the bar chart using Plotly Express
        fig = px.bar(
            df, 
            x='Category', 
            y='Values', 
            title='Sample Bar Chart',
            labels={'Values': 'Count'},
            color='Category',
            color_continuous_scale=px.colors.sequential.Viridis,
            
        )
        
        return rx.plotly(data=fig, height='35vh')