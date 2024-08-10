from ..core.statefulness import Stateful, state, state_var, handler
from ..utils.clustering import add_cluster_names

import pandas as pd
import reflex as rx

from typing import List, Dict, Any
from django.utils.functional import cached_property


class CoreState(Stateful):
    
    def __init__(self, name, filter_objs, table):
        self.name = name
        self.table = table
        self.filter_objs = filter_objs
    
    @state
    def query_args(self) -> Dict[str, List[str]]:
        # note: really want to be able to add @rx.cached_var here but can't - can't use await self.get_state within @rx.cached_var
        return {}
    
    @state_var(cached=True)
    def _data(self) -> pd.DataFrame:
        print("SQL:", self.table.get_sql(**self.query_args, limit=300))
        return self.table.query(**self.query_args, limit=300)#, select=[''])
    
    @state_var(cached=True)
    def display_data(self) -> List[List[Any]]:
        # return [[]]
        res = self._data
        if len(res) > 10:
            res = res.sample(10)
        for col in self.display_columns:
            res[col] = res[col].astype(str)
        res = res[self.display_columns].values.tolist()
        return res
    
    @handler
    async def update(self):
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
            on_click=self.update_all,
            variant="outline", color="green",
        )
        return button
    
    
    @property
    def display_columns(self):
        return ['CASE_RECV_S', 'CASE_SUMY_X', 'State', 'case_sumy_length']

