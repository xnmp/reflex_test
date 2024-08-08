import reflex as rx
import pandas as pd
import datetime as dt

from typing import List, Dict, Any

from .react_components import MultiSelect, AgGrid, DateRange, TagInput, DatePicker
from ..core.statefulness import Stateful, state, state_var, handler


class DropdownComponent(Stateful):
    
    def __init__(self, name, options, column_name=None, is_multi=True):
        self.name = name
        self.column_name = column_name or name
        self.options = options
        self.is_multi = is_multi
    
    @state
    def selected(self) -> List[str]:
        return []
    
    @state_var(cached=True)
    def query_args(self) -> Dict[str, List[str]]:
        if len(self.selected) > 1:
            in_str = ','.join([f"'{el}'" for el in self.selected])
            return {'filters': [f"{self.column_name} in ({in_str})"]}
        elif len(self.selected) == 1:
            return {'filters': [f"{self.column_name} = '{self.selected[0]}'"]}
        return {}
    
    @handler
    def handle_change(self, values):
        print("Dropdown Values:", values, type(values), self.name, type(self))
        self.selected = [el['value'] for el in values]
    
    @property
    def element(self):
        return MultiSelect.create(
            options=self.options,
            is_multi=self.is_multi,
            on_change=self.handle_change,
            placeholder=f"Select {self.name}"
        )


class TagInputComponent(Stateful):
    
    def __init__(self, name, and_or='AND'):
        self.name = name
        self.and_or = and_or

    @state
    def selected_tags(self) -> List[str]:
        return []
    
    @state_var(cached=True)
    def query_args(self) -> Dict[str, List[str]]:
        return {'match_strs': [f"{self.and_or} {val}" for val in self.selected_tags]}
    
    @handler
    def handle_change(self, values):
        print("TagInput Values:", values)
        self.selected_tags = values#[el['value'] for el in values]
    
    @property
    def element(self):
        return TagInput.create(
            onChange=self.handle_change,
            value=self.selected_tags,
            inputProps={'placeholder': f'Add {self.and_or} keywords'},
        )


class DateRangeComponent(Stateful):
    
    def __init__(self, name, column_name=None):
        self.name = name
        self.column_name = column_name or name
    
    @state
    def selected_dates(self) -> List[Dict[str, Any]]:
        return [{}]
    
    @state_var(cached=True)
    def query_args(self) -> Dict[str, List[str]]:
        return {'filters': [f"{self.column_name} between '{self.selected_dates[0]['start_date']}' and '{self.selected_dates[0]['end_date']}'"]}

    @handler
    def handle_change(self, values):
        self.selected_dates = values

    @property
    def element(self):
        return rx.box(
            DateRange.create(
                onChange=self.handle_change,
                ranges=self.selected_dates,
            ),
            class_name='style-reset'
        )


class DatePickerComponent(Stateful):
    
    def __init__(self, name, column_name=None, gt_or_lt='>='):
        self.name = name
        self.column_name = column_name or name
        self.gt_or_lt = gt_or_lt

    @state
    def selected_date(self) -> str:
        return ''
    
    @state_var(cached=True)
    def query_args(self) -> Dict[str, List[str]]:
        if self.selected_date:
            return {'filters': [f"{self.column_name} {self.gt_or_lt} '{self.selected_date}'"]}
        return {}
    
    @handler
    def handle_change(self, value):
        if value:
            self.selected_date = str((pd.to_datetime(value) + dt.timedelta(hours=12)).date())
        else:
            self.selected_date = ''
        print("DatePicker Value:", self.selected_date)
    
    @property
    def element(self):
        return DatePicker.create(
            onChange=self.handle_change,
        )
