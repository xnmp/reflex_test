import reflex as rx

from typing import List, Dict, Any


class Creatable(rx.Component):
    library = "react-select"
    tag = "CreatableSelect"
    is_default = True
    options: rx.Var[List[Dict[str, Any]]]
    on_change: rx.EventHandler#[lambda color: [color]]
    is_multi: rx.Var[bool] = False
    value: rx.Var[dict]
    placeholder: rx.Var[str]
#     # is_disabled: rx.Var[bool] = False
#     # is_clearable: rx.Var[bool] = True
#     # is_searchable: rx.Var[bool] = True



creatable = Creatable.create

options = [
    {"value": "ocean", "label": "Ocean", "color": "#00B8D9", "isFixed": True},
    {"value": "blue", "label": "Blue", "color": "#0052CC", "isDisabled": True},
    {"value": "purple", "label": "Purple", "color": "#5243AA"},
]

def dropdowns():
    """The main view."""
    return rx.vstack(
        creatable(options=options, is_multi=True, on_change=State1.handle_change),
        rx.text(f"Selected: {State1.selected_option}")
    )


# class CombinedFilters(rx.State):
#     values: dict = {}


class State1(rx.State):
    selected_option: dict = {}
    def handle_change(self, *values):
        self.selected_option = values


class State2(rx.State):
    selected_option: dict = {}
    def handle_change(self, *values):
        self.selected_option = values


def dropdowns2():
    options_flavour = [
        {"value": "chocolate", "label": "Chocolate"},
        {"value": "strawberry", "label": "Strawberry"},
        {"value": "vanilla", "label": "Vanilla"}
    ]

    options_color = [
        {"value": "green", "label": "Green"},
        {"value": "red", "label": "Red"},
        {"value": "blue", "label": "Blue"}
    ]
    
    return rx.vstack(
        creatable(
            options=options_flavour,
            value=State1.selected_option,
            on_change=State1.handle_change,
            placeholder="Select a flavor..."
        ),
        # creatable(
        #     options=options_color,
        #     value=State2.selected_option,
        #     on_change=State2.handle_change,
        #     placeholder="Select a flavor..."
        # ),
        rx.text(f"Selected: {State1.selected_option}")
    )
