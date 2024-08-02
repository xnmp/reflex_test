import reflex as rx

from typing import List, Dict, Any

from .components.multi_select import MultiSelect
from .core.statefulness import StateMeta, Stateful, state, state_change


class Dropdown(Stateful):

    @state
    def selected_option(self):
        return 'tg'
    
    @state_change
    def handle_change(self, values):
        print("Values:", values, type(values))
        self.selected_option = [el['value'] for el in values]
        
    def __init__(self, options):
        self.options = options
        print("State:", self._state)
    
    @property
    def element(self):
        return MultiSelect.create(
            options=self.options,
            is_multi=True,
            on_change=self.handle_change,
            placeholder="Select an option..."
        )


def dropdowns():

    options_flavour = [
        {"value": "chocolate", "label": "Chocolate"},
        {"value": "strawberry", "label": "Strawberry"},
        {"value": "vanilla", "label": "Vanilla"}
    ]
    flavour_dropdown = Dropdown(options_flavour)

    options_color = [
        {"value": "green", "label": "Green"},
        {"value": "red", "label": "Red"},
        {"value": "blue", "label": "Blue"}
    ]
    color_dropdown = Dropdown(options_color)
    
    return rx.vstack(
        flavour_dropdown.element,
        color_dropdown.element,
        rx.text(f"Selected: {flavour_dropdown.selected_option}"),
        rx.text(f"Selected: {color_dropdown.selected_option}"),
        rx.select(
            ["apple", "grape", "pear"],
            default_value="apple",
            name="select",
        ),
    )
