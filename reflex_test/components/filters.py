import json
import reflex as rx
import pandas as pd
import datetime as dt

from typing import List, Dict, Any

from .react_components import MultiSelect, AgGrid, DateRange, TagInput, DatePicker
from ..core.statefulness import Stateful, state, state_var, handler


class Dropdown(Stateful):
    
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


class Filters(Stateful):
    
    def __init__(self, name, filter_objs, table):
        self.name = name
        self.table = table
        self.filter_objs = filter_objs
    
    @state
    # really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
    def query_args(self) -> Dict[str, List[str]]:
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
        res = res[self.display_columns].values.tolist() #if using glide grid
        # res = res[self.display_columns].to_dict(orient='records') #if using ag grid
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
            rx.icon(tag='play'),
            "Update Data",
            on_click=self.update_query_args,
            variant="outline",
            color="green",
        )
        return rx.vstack(
            self.table_element,
            button,
        )

    @property
    def column_defs(self) -> List[Dict[str, Any]]:
        res = []
        for col in self.display_columns:
            # res0 = {'title': col} #for glide
            # res0 = {'field': col, 'headerName': col} #for ag grid
            res0 = {'name': col, 'sort':True} #for base rx.data_table
            if col in 'CASE_SUMY_X':
                res0['width'] = 800
            res.append(res0)
        return res
    
    # @property
    # def grid_element(self):
    #     # glide grid
    #     return rx.data_editor.create(
    #         columns=self.column_defs,
    #         data=self.display_data,
    #         # on_cell_clicked=self.click_cell,
    #         get_cell_for_selection=True,
    #         row_height=50,
    #         allowWrapping=True,
    #     )
        
    @property
    def table_element(self):
        return rx.data_table(
            columns=self.column_defs,
            data=self.display_data,
            # resizable=True,
        )
    
    # @property
    # def ag_grid_element(self):
    #     grid = AgGrid.create(
    #         columnDefs=self.column_defs,
    #         rowData=self.display_data,
    #     )
    #     return rx.box(grid, class_name='style-reset')


class Embeddings(Stateful):
    
    @state_var(cached=True)
    def embeddings(self) -> pd.DataFrame:
        calculate_embeddings = NotImplemented
        res = self.data
        res['embed_x','embed_y'] = calculate_embeddings(res['CASE_SUMY_X'])
        return self.data

