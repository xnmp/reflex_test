import json
import reflex as rx
import pandas as pd

from typing import List, Dict, Any

from .react_components import MultiSelect, AgGrid, DateRange, TagInput
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


class TagInputComponent(Stateful):

    @state
    def selected(self) -> List[str]:
        return ['Hello']
    
    @handler
    def handle_change(self, values):
        print("TagInput Values:", values)
        self.selected = values#[el['value'] for el in values]
    
    @property
    def element(self):
        return TagInput.create(
            onChange=self.handle_change,
            value=self.selected,
        )


class DateRangeComponent(Stateful):

    @handler
    def handle_change(self, drange):
        return

    @property
    def element(self):
        return rx.box(
            DateRange.create(
                onChange=self.handle_change,
                ranges=[{}],
            ),
            class_name='style-reset'
        )


class Filters(Stateful):
    
    def __init__(self, name, filter_objs, table):
        self.name = name
        self.table = table
        self.filter_objs = filter_objs
    
    @state
    # really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
    def filter_strs(self): 
        return set()
    
    @state_var(cached=True)
    def data(self) -> pd.DataFrame:
        if self.filter_strs:
            return self.table.query(self.filter_strs, limit=5)#, select=[''])
        return self.table.query(limit=5)
    
    @state_var(cached=True)
    def display_data(self) -> List[List[Any]]:
        res = self.data
        if len(res) > 5:
            res = res.sample(5)
        # import textwrap
        # res['CASE_SUMY_X'] = res['CASE_SUMY_X'].apply(lambda x: '\n'.join(textwrap.wrap(x, width=70)))
        for col in self.display_columns:
            res[col] = res[col].astype(str)
        res = res[self.display_columns].values.tolist() #if using glide grid
        # res = res[self.display_columns].to_dict(orient='records') #if using ag grid
        return res
    
    @property
    def display_columns(self):
        return ['CASE_RECV_S', 'CASE_SUMY_X', 'State', 'case_sumy_length']
    
    @handler
    async def update_filters(self):
        states = {filter_obj.name: await self.get_state(filter_obj.State) for filter_obj in self.filter_objs}
        self.filter_strs = {v.sql_string for k, v in states.items() if v.sql_string}
    
    @property
    def element(self):
        button = rx.button(
            rx.icon(tag='play'),
            "Update Data",
            on_click=self.update_filters,
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
    
    @property
    def grid_element(self):
        return rx.data_editor.create(
            columns=self.column_defs,
            data=self.display_data,
            # on_cell_clicked=self.click_cell,
            get_cell_for_selection=True,
            row_height=50,
            allowWrapping=True,
        )
        
    @property
    def table_element(self):
        return rx.data_table(
            columns=self.column_defs,
            data=self.display_data,
            # resizable=True,
        )
    
    @property
    def ag_grid_element(self):
        grid = AgGrid.create(
            columnDefs=self.column_defs,
            rowData=self.display_data,
        )
        return rx.box(grid, class_name='style-reset')


class Embeddings(Stateful):
    
    @state_var(cached=True)
    def embeddings(self) -> pd.DataFrame:
        calculate_embeddings = NotImplemented
        res = self.data
        res['embed_x','embed_y'] = calculate_embeddings(res['CASE_SUMY_X'])
        return self.data

