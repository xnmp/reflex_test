import reflex as rx
import pandas as pd

from typing import List, Dict, Any

from .components.multi_select import MultiSelect
from .core.statefulness import StateMeta, Stateful, state, state_change


class Dropdown(rx.ComponentState):
    
    selected_option: List[str] = ['tg']
    
    def handle_change(self, values):
        print("Values:", values, type(values))
        self.selected_option = [el['value'] for el in values]
    
    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        return MultiSelect.create(
            options=props.pop('options'),
            is_multi=True,
            on_change=cls.handle_change,
            placeholder="Select an option..."
        )


options_flavour = [
        {"value": "chocolate", "label": "Chocolate"},
        {"value": "strawberry", "label": "Strawberry"},
        {"value": "vanilla", "label": "Vanilla"}
    ]
flavour_dropdown = Dropdown.create(options=options_flavour)

options_color = [
    {"value": "green", "label": "Green"},
    {"value": "red", "label": "Red"},
    {"value": "blue", "label": "Blue"}
]
color_dropdown = Dropdown.create(options=options_color)




def dropdowns():

    # table = rx.data_table(
    #     data=component_df.df,
    #     pagination=True,
    #     search=True,
    #     sort=True,
    # )
    
    return rx.vstack(
        flavour_dropdown,
        color_dropdown,
        rx.text(f"Selected: {flavour_dropdown.State.selected_option}"),
        rx.text(f"Selected: {color_dropdown.State.selected_option}"),#, on_click=[component_df.update_df, component_df.handle_change2]),
        # table,
        rx.select(
            ["apple", "grape", "pear"],
            default_value="apple",
            name="select",
        ),
    )
