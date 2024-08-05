import reflex as rx
import pandas as pd

from typing import List, Dict, Any

from .react_components import MultiSelect
from ..core.statefulness import Stateful, state, state_var, handler


class Dropdown(Stateful):

    @state
    def selected(self) -> List[str]:
        return []
    
    @state_var(cached=True)
    def sql_string(self):
        if len(self.selected) > 1:
            in_str = ','.join([f"'{el}'" for el in self.selected])
            return f"{self.column_name} in ({in_str})"
        elif len(self.selected) == 1:
            return f"{self.column_name} = '{self.selected[0]}'"
        return None
    
    @handler
    def handle_change(self, values):
        print("Dropdown Values:", values, type(values), self.name, type(self))
        self.selected = [el['value'] for el in values]
        
    def __init__(self, name, options, column_name=None, is_multi=True):
        self.name = name
        self.column_name = column_name or name
        self.options = options
        self.is_multi = is_multi
    
    @property
    def element(self):
        return MultiSelect.create(
            options=self.options,
            is_multi=self.is_multi,
            on_change=self.handle_change,
            placeholder=f"Select {self.name}"
        )


class Filters(Stateful):
    
    @state
    # really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
    def filter_strs(self): 
        return set()
    
    @state_var(cached=True)
    def df(self) -> pd.DataFrame:
        if self.filter_strs:
            return self.table.query(self.filter_strs)
        return pd.DataFrame()
    
    @state_var(cached=True)
    def df2(self) -> pd.DataFrame:
        if len(self.df) < 100:
            return self.df
        return self.df.sample(100)
    
    def __init__(self, name, filter_objs, table):
        self.name = name
        self.table = table
        self.filter_objs = filter_objs
    
    @handler
    async def update_filters(self):
        states = {filter_obj.name: await self.get_state(filter_obj.State) for filter_obj in self.filter_objs}
        self.filter_strs = {v.sql_string for k, v in states.items() if v.sql_string}
    
    @property
    def element(self):
        data_table = rx.data_table(
            data=self.df2,
            pagination=True,
            search=True,
            sort=True,
        )
        button = rx.button(
            rx.icon(tag='play'),
            "Update Data",
            on_click=self.update_filters,
            variant="outline",
            color="green",
        )
        return rx.vstack(
            data_table,
            button,
        )

