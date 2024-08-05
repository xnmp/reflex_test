import reflex as rx
import pandas as pd

from typing import List, Dict, Any

from .multi_select import MultiSelect
from ..core.statefulness import Stateful, state, state_var, handler


class Dropdown(Stateful):

    @state
    def selected_option(self):
        return self.options[0]['value']
    
    @handler
    def handle_change(self, values):
        print("Dropdown Values:", values, type(values), self.name, type(self))
        self.selected_option = [self.name + '-' + el['value'] for el in values]
        
    def __init__(self, name, options):
        self.name = name
        self.options = options
    
    @property
    def element(self):
        return MultiSelect.create(
            options=self.options,
            is_multi=True,
            on_change=self.handle_change,
            placeholder="Select an option..."
        )


class Filters(Stateful):
    
    @state
    # really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
    def filter_dict(self): 
        return {}
    
    @state_var
    def df(self) -> pd.DataFrame:
        if self.filter_dict:
            return pd.DataFrame(self.filter_dict.values(), index=self.filter_dict.keys(), columns=['col1'])
        return pd.DataFrame()
    
    @state_var(cached=True)
    def df2(self) -> pd.DataFrame:
        res = self.df
        res['gogo'] = 1
        return res
    
    def __init__(self, name, filter_objs):
        self.name = name
        self.filter_objs = filter_objs
    
    @handler
    async def update_filters(self):
        states = {filter_obj.name: await self.get_state(filter_obj.State) for filter_obj in self.filter_objs}
        self.filter_dict = {k: v.selected_option[0] for k, v in states.items()}
    
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


options_dict ={
    'flavor': [
        {"value": "chocolate", "label": "Chocolate"},
        {"value": "strawberry", "label": "Strawberry"},
        {"value": "vanilla", "label": "Vanilla"}
    ],
    'color': [
        {"value": "green", "label": "Green"},
        {"value": "red", "label": "Red"},
        {"value": "blue", "label": "Blue"}
    ]
}

dropdowns = {name: Dropdown(name, options=options) for name, options in options_dict.items()}

filters = Filters('filters', filter_objs=dropdowns.values())

