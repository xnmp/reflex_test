import reflex as rx
import pandas as pd

from typing import List, Dict, Any

from .multi_select import MultiSelect
from ..core.statefulness import Stateful, state, handler


class Dropdown(Stateful):

    @state
    def selected_option(self):
        return self.options[0]['value']
    
    @handler
    def handle_change(self, values):
        print("Dropdown Values:", values, type(values), self.name, type(self))
        self.selected_option = [self.name + '-' + el['value'] for el in values]
        
        # can't do this...
        # Filters.filters[self.name] = [el['value'] for el in values]
        # print("===\n", Filters.update_filters(self.name, self.selected_option))
        
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


class Filters(Stateful):
    
    @state
    def filters(self): 
        return {}
    
    @state
    def df(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    # really want to be able to add @rx.cached_var here but can't
    @handler
    async def update_filters(self):
        states = {name: await self.get_state(dropdown.State) for name, dropdown in dropdowns.items()}
        self.filters = {k: v.selected_option[0] for k, v in states.items()}
        self.df = pd.DataFrame(self.filters.values(), index=self.filters.keys(), columns=['col1'])
    
    @property
    def element(self):
        data_table = rx.data_table(
            data=self.df,
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


filters = Filters('filters')


def dropdown_elements():

    table = rx.data_table(
        data=Filters.df,
        pagination=True,
        search=True,
        sort=True,
    )
    
    return rx.vstack(
        dropdowns['flavor'].element,
        dropdowns['color'].element,
        rx.text(f"Selected: {dropdowns['flavor'].selected_option}"),
        rx.text(f"Selected: {dropdowns['color'].selected_option}"),#, on_click=[component_df.update_df, component_df.handle_change2]),
        rx.text(f"Selected: {Filters.filters}", on_click=[Filters.update_filters]),
        table,
        rx.select(
            ["apple", "grape", "pear"],
            default_value="apple",
            name="select",
        ),
    )
